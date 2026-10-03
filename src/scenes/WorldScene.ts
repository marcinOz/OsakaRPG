import Phaser from 'phaser';
import { GAME_W, GAME_H, PAL, TILE } from '@/config';
import { HeroId } from '@/types';
import { GameData, newGame, walkSpeedMultiplier, hasFlag, setFlag, removeWorldStatus, addToParty } from '@/systems/GameState';
import { CH01 } from '@/content/chapters/ch01';
import { CH02 } from '@/content/chapters/ch02';
import { CH03 } from '@/content/chapters/ch03';
import { DialogueBox } from '@/ui/DialogueBox';
import { DialogueRunner } from '@/systems/Dialogue';
import { Input } from '@/ui/Input';
import { Audio } from '@/audio/ChipAudio';
import { applyCrtToCamera } from '@/fx/CrtPipeline';
import { txt } from '@/ui/Text';
import { drawPanel } from '@/ui/Panel';
import { setTimeOfDay } from '@/fx/Palette';

interface TrailPoint {
  x: number;
  y: number;
  dir: string;
}

export class WorldScene extends Phaser.Scene {
  private state!: GameData;
  private inputHandler!: Input;
  private dialogueBox!: DialogueBox;
  private playerSprite!: Phaser.GameObjects.Sprite;
  private followerSprites: Map<string, Phaser.GameObjects.Sprite> = new Map();
  private trail: TrailPoint[] = [];

  private mapContainer!: Phaser.GameObjects.Container;
  private npcContainer!: Phaser.GameObjects.Container;
  private hudContainer!: Phaser.GameObjects.Container;
  private hudText!: Phaser.GameObjects.BitmapText | Phaser.GameObjects.Text;
  private isBusy = false;
  private currentMap = 'apartment';

  private mapW = 18;
  private mapH = 12;
  private solids: boolean[][] = [];

  // QTE state
  private qteContainer: Phaser.GameObjects.Container | null = null;
  private qteMarkerX = 0;
  private qteMarkerSpeed = 160;

  constructor() {
    super('World');
  }

  init(data: { leader?: HeroId; loadSave?: GameData; returnFromBattle?: boolean; battleResult?: 'victory' | 'defeat' }): void {
    if (data.loadSave) {
      this.state = data.loadSave;
    } else if (data.leader) {
      this.state = newGame(data.leader);
    } else if (!this.state) {
      this.state = newGame('danny');
    }

    if (data.returnFromBattle) {
      this.isBusy = false;
      // Handle post-battle storyline
      if (this.currentMap === 'garage' && hasFlag(this.state, 'fought_sasiad') && !hasFlag(this.state, 'danny_alior_joined')) {
        this.time.delayedCall(300, () => this.afterSasiadBoss());
      } else if (this.currentMap === 'pub' && hasFlag(this.state, 'fought_hipsters') && !hasFlag(this.state, 'barti_joined')) {
        this.time.delayedCall(300, () => this.afterPubBattle());
      }
    }
  }

  create(): void {
    applyCrtToCamera(this);
    this.cameras.main.setBackgroundColor(PAL.void);

    this.mapContainer = this.add.container(0, 0);
    this.npcContainer = this.add.container(0, 0).setDepth(120);
    this.hudContainer = this.add.container(0, 0).setDepth(900).setScrollFactor(0);

    this.buildMap(this.currentMap);
    this.updateAtmosphere();

    // Player sprite
    const px = this.state.x * TILE + 8;
    const py = this.state.y * TILE + 8;
    this.playerSprite = this.add.sprite(px, py, `${this.state.leader}_walk`, 0).setDepth(150);
    this.playerSprite.play(`anim_${this.state.leader}_walk_down`);
    this.playerSprite.stop();

    this.cameras.main.startFollow(this.playerSprite, true, 0.1, 0.1);
    this.cameras.main.setBounds(0, 0, this.mapW * TILE, this.mapH * TILE);

    // Followers
    this.syncFollowerSprites();

    // HUD Top Bar
    const hg = this.add.graphics();
    drawPanel(hg, 4, 4, GAME_W - 8, 16, { fill: PAL.navy, border: PAL.steel, glow: false });
    this.hudContainer.add(hg);

    this.hudText = txt(this, 10, 8, '', { color: PAL.cyan });
    this.hudContainer.add(this.hudText);
    this.updateHud();

    this.dialogueBox = new DialogueBox(this, 1000);
    this.inputHandler = new Input(this);

    // Initial wake-up sequence
    if (this.currentMap === 'apartment' && !hasFlag(this.state, 'ch1_woke_up')) {
      this.time.delayedCall(400, () => this.runWakeUpSequence());
    }
  }

  private updateAtmosphere(): void {
    if (this.currentMap === 'apartment' || this.currentMap === 'city') {
      setTimeOfDay(this, 'morning');
      Audio.playSong('ch01_explore', { fadeMs: 500 });
    } else if (this.currentMap === 'garage') {
      setTimeOfDay(this, 'day');
      Audio.playSong('ch02_garage', { fadeMs: 500 });
    } else if (this.currentMap === 'pub') {
      setTimeOfDay(this, 'dusk');
      Audio.playSong('ch03_pub', { fadeMs: 500 });
    }
  }

  private updateHud(): void {
    const leaderName = this.state.leader.toUpperCase();
    const partyCount = this.state.party.length;
    let loc = 'MIESZKANIE';
    if (this.currentMap === 'city') loc = 'PORANNE MIASTO';
    else if (this.currentMap === 'garage') loc = 'GARAŻ (UFC HQ)';
    else if (this.currentMap === 'pub') loc = 'PUB CZARNY KRĄŻEK';

    const hasHangover = this.state.worldStatuses.includes('kacGigant');
    const statusTag = hasHangover ? ' [DEBUFF: KAC GIGANT]' : ' [STATUS: OK]';
    (this.hudText as any).setText(`LIDER: ${leaderName} | EKIPA: ${partyCount}/6 | R${this.state.chapter}: ${loc}${statusTag}`);
  }

  private syncFollowerSprites(): void {
    const followers = this.state.party.slice(1);
    for (const [hid, spr] of this.followerSprites.entries()) {
      if (!followers.includes(hid as HeroId)) {
        spr.destroy();
        this.followerSprites.delete(hid);
      }
    }

    followers.forEach((hid) => {
      if (!this.followerSprites.has(hid)) {
        const fspr = this.add.sprite(this.playerSprite.x, this.playerSprite.y, `${hid}_walk`, 0).setDepth(140);
        fspr.play(`anim_${hid}_walk_down`);
        fspr.stop();
        this.followerSprites.set(hid, fspr);
      }
    });
  }

  private buildMap(mapName: string): void {
    this.mapContainer.removeAll(true);
    this.npcContainer.removeAll(true);
    this.solids = [];
    for (let y = 0; y < this.mapH; y++) {
      this.solids[y] = [];
      for (let x = 0; x < this.mapW; x++) {
        this.solids[y][x] = false;
      }
    }

    if (mapName === 'apartment') {
      this.buildApartmentMap();
    } else if (mapName === 'city') {
      this.buildCityMap();
    } else if (mapName === 'garage') {
      this.buildGarageMap();
    } else if (mapName === 'pub') {
      this.buildPubMap();
    }
  }

  private buildApartmentMap(): void {
    for (let y = 0; y < this.mapH; y++) {
      for (let x = 0; x < this.mapW; x++) {
        let tileIdx = 0;
        let isSolid = false;
        if (y === 0) { tileIdx = 2; isSolid = true; }
        else if (y === 1) { tileIdx = 1; isSolid = true; }
        else if (y === this.mapH - 1 || x === 0 || x === this.mapW - 1) { tileIdx = 1; isSolid = true; }
        if (x === 3 && y === 2) { tileIdx = 3; isSolid = true; }
        if (x === 3 && y === 3) { tileIdx = 4; isSolid = true; }
        if (x === 8 && y === 2) { tileIdx = 6; isSolid = true; }
        if (x === 9 && y === 2) { tileIdx = 6; isSolid = true; }
        if (x === 6 && y === 5 || x === 7 && y === 5) { tileIdx = 5; }
        if (x === 10 && y === this.mapH - 1) { tileIdx = 7; isSolid = false; }

        this.solids[y][x] = isSolid;
        const spr = this.add.image(x * TILE + 8, y * TILE + 8, 'tiles_apartment');
        spr.setCrop(tileIdx * 16, 0, 16, 16);
        this.mapContainer.add(spr);
      }
    }
  }

  private buildCityMap(): void {
    for (let y = 0; y < this.mapH; y++) {
      for (let x = 0; x < this.mapW; x++) {
        let tileIdx = 1;
        let isSolid = false;
        if (y < 3) { tileIdx = (x % 2 === 0) ? 2 : 3; isSolid = true; }
        else if (y >= 8) { tileIdx = 0; }
        if (x === 4 && y === 3) { tileIdx = 5; isSolid = true; }
        if (x === 10 && y === 4) { tileIdx = 6; isSolid = true; }
        if (x === 17 && y === 5) { tileIdx = 7; isSolid = false; }

        this.solids[y][x] = isSolid;
        const spr = this.add.image(x * TILE + 8, y * TILE + 8, 'tiles_city');
        spr.setCrop(tileIdx * 16, 0, 16, 16);
        this.mapContainer.add(spr);
      }
    }
  }

  private buildGarageMap(): void {
    for (let y = 0; y < this.mapH; y++) {
      for (let x = 0; x < this.mapW; x++) {
        let tileIdx = 0; // concrete
        let isSolid = false;
        if (y === 0) { tileIdx = 2; isSolid = true; }
        else if (y === 1) { tileIdx = 1; isSolid = true; }
        else if (y === this.mapH - 1 || x === 0 || x === this.mapW - 1) { tileIdx = 1; isSolid = true; }

        // Props
        if (x === 3 && y === 2) { tileIdx = 3; isSolid = true; } // tires
        if (x === 4 && y === 2) { tileIdx = 4; isSolid = true; } // weights
        if (x === 8 && y === 2) { tileIdx = 6; isSolid = true; } // projector UFC
        if (x === 14 && y === 2) { tileIdx = 5; isSolid = true; } // beer fridge
        if (x === 17 && y === 6) { tileIdx = 7; isSolid = false; } // exit to pub!

        this.solids[y][x] = isSolid;
        const spr = this.add.image(x * TILE + 8, y * TILE + 8, 'tiles_garage');
        spr.setCrop(tileIdx * 16, 0, 16, 16);
        this.mapContainer.add(spr);
      }
    }

    // Spawn Danny & Alior NPCs if they haven't joined yet
    if (!this.state.party.includes('danny')) {
      const dNpc = this.add.sprite(5 * TILE + 8, 4 * TILE + 8, 'danny_walk', 0);
      this.npcContainer.add(dNpc);
    }
    if (!this.state.party.includes('alior')) {
      const aNpc = this.add.sprite(8 * TILE + 8, 4 * TILE + 8, 'alior_walk', 0);
      this.npcContainer.add(aNpc);
    }
  }

  private buildPubMap(): void {
    for (let y = 0; y < this.mapH; y++) {
      for (let x = 0; x < this.mapW; x++) {
        let tileIdx = 0; // dark wood floor
        let isSolid = false;
        if (y === 0) { tileIdx = 2; isSolid = true; }
        else if (y === 1) { tileIdx = 1; isSolid = true; }
        else if (y === this.mapH - 1 || x === 0 || x === this.mapW - 1) { tileIdx = 1; isSolid = true; }

        // Bar counter & DJ setup
        if (y === 3 && x >= 4 && x <= 12) {
          tileIdx = (x === 8) ? 4 : (x === 10 ? 6 : 3);
          isSolid = true;
        }
        if (x === 14 && y === 2) { tileIdx = 5; isSolid = true; } // vinyl rack
        if (x === 17 && y === 6) { tileIdx = 7; isSolid = false; } // exit to campfire

        this.solids[y][x] = isSolid;
        const spr = this.add.image(x * TILE + 8, y * TILE + 8, 'tiles_pub');
        spr.setCrop(tileIdx * 16, 0, 16, 16);
        this.mapContainer.add(spr);
      }
    }

    // Spawn Barti NPC behind DJ decks if not joined yet
    if (!this.state.party.includes('barti')) {
      const bNpc = this.add.sprite(10 * TILE + 8, 2 * TILE + 8, 'barti_walk', 0);
      this.npcContainer.add(bNpc);
    }
  }

  private async runWakeUpSequence(): Promise<void> {
    this.isBusy = true;
    setFlag(this.state, 'ch1_woke_up', true);
    Audio.sfx('notification');

    const runner = new DialogueRunner(CH01.wake, this.state.leader);
    await this.dialogueBox.play(runner.allResolved());
    await this.showPhonePopup();

    const hangRunner = new DialogueRunner(CH01.hangover, this.state.leader);
    await this.dialogueBox.play(hangRunner.allResolved());
    this.isBusy = false;
  }

  private async showPhonePopup(): Promise<void> {
    const pop = this.add.container(GAME_W / 2, GAME_H / 2).setDepth(850).setScrollFactor(0);
    const pg = this.add.graphics();
    drawPanel(pg, -110, -70, 220, 140, { fill: PAL.panel, border: PAL.cyanHi });
    pop.add(pg);

    pop.add(txt(this, -90, -62, 'WHATSAPP: EKIPA 36+ [REUNION NIGHT]', { color: PAL.yellow }));

    CH01.groupChat.forEach((msg, i) => {
      const isLeader = msg.from === this.state.leader;
      const color = isLeader ? PAL.cyan : PAL.white;
      pop.add(txt(this, -100, -42 + i * 16, `${msg.from.toUpperCase()}: ${msg.text}`, { color, maxWidth: 200 }));
    });

    pop.add(txt(this, 0, 56, '[NACIŚNIJ ENTER / Z]', { color: PAL.silver, align: 'center', origin: [0.5, 0.5] }));
    Audio.sfx('notification');

    await new Promise<void>((resolve) => {
      const checkInput = () => {
        if (this.inputHandler.okOrTap()) {
          Audio.sfx('confirm');
          pop.destroy();
          resolve();
        } else {
          this.time.delayedCall(50, checkInput);
        }
      };
      this.time.delayedCall(200, checkInput);
    });
  }

  override update(_time: number, delta: number): void {
    if (this.qteContainer) {
      this.updateQte(delta);
      return;
    }

    if (this.dialogueBox.active) {
      this.dialogueBox.update(this.inputHandler, delta);
      return;
    }

    if (this.isBusy) return;

    // Movement
    const axis = this.inputHandler.axis();
    if (axis.x !== 0 || axis.y !== 0) {
      const speedMult = walkSpeedMultiplier(this.state);
      const speed = 70 * speedMult * (delta / 1000);

      const targetX = this.playerSprite.x + axis.x * speed;
      const targetY = this.playerSprite.y + axis.y * speed;

      const tileX = Math.floor(targetX / TILE);
      const tileY = Math.floor(targetY / TILE);

      if (this.isWalkable(tileX, tileY)) {
        this.playerSprite.x = targetX;
        this.playerSprite.y = targetY;
        this.state.x = tileX;
        this.state.y = tileY;

        // Record breadcrumb trail for followers
        const dir = axis.x > 0 ? 'right' : axis.x < 0 ? 'left' : axis.y > 0 ? 'down' : 'up';
        this.trail.push({ x: targetX, y: targetY, dir });
        if (this.trail.length > 80) this.trail.shift();

        this.updateFollowers();
      }

      const dir = axis.x > 0 ? 'right' : axis.x < 0 ? 'left' : axis.y > 0 ? 'down' : 'up';
      this.playerSprite.play(`anim_${this.state.leader}_walk_${dir}`, true);

      this.checkTriggers(tileX, tileY);
    } else {
      this.playerSprite.stop();
      this.followerSprites.forEach((spr) => spr.stop());
    }
  }

  private updateFollowers(): void {
    const followers = this.state.party.slice(1);
    followers.forEach((hid, idx) => {
      const spr = this.followerSprites.get(hid);
      if (!spr) return;
      const historyIndex = Math.max(0, this.trail.length - 1 - (idx + 1) * 12);
      const pt = this.trail[historyIndex];
      if (pt) {
        spr.setPosition(pt.x, pt.y);
        spr.play(`anim_${hid}_walk_${pt.dir}`, true);
      }
    });
  }

  private isWalkable(x: number, y: number): boolean {
    if (x < 0 || x >= this.mapW || y < 0 || y >= this.mapH) return false;
    return !this.solids[y]?.[x];
  }

  private checkTriggers(x: number, y: number): void {
    if (this.currentMap === 'apartment') {
      if (x === 4 && y === 4 && !hasFlag(this.state, 'ch1_fought_spine')) {
        setFlag(this.state, 'ch1_fought_spine', true);
        this.startSpineEncounter();
        return;
      }
      if ((x === 8 || x === 9) && y === 3 && !hasFlag(this.state, 'ch1_fought_slack')) {
        setFlag(this.state, 'ch1_fought_slack', true);
        this.startSlackEncounter();
        return;
      }
      if (x === 10 && y >= this.mapH - 1) {
        this.transitionToMap('city', 5, 4);
        return;
      }
    } else if (this.currentMap === 'city') {
      if (x === 4 && y === 4 && !hasFlag(this.state, 'bought_coffee')) {
        setFlag(this.state, 'bought_coffee', true);
        this.buyCoffee();
        return;
      }
      if (x >= 16 && y === 5) {
        // Enter Chapter 2 Garage!
        this.transitionToMap('garage', 2, 5);
        return;
      }
    } else if (this.currentMap === 'garage') {
      // Meet Danny & Alior in garage
      if ((x === 5 || x === 6) && (y === 4 || y === 5) && !hasFlag(this.state, 'garage_wrestled')) {
        this.triggerGarageEncounter();
        return;
      }
      // Exit garage to Pub
      if (x >= 16 && y === 6 && hasFlag(this.state, 'danny_alior_joined')) {
        this.transitionToMap('pub', 2, 5);
        return;
      }
    } else if (this.currentMap === 'pub') {
      // Approach Barti at DJ desk
      if ((x === 9 || x === 10) && (y === 4 || y === 5) && !hasFlag(this.state, 'pub_cleared')) {
        this.triggerPubEncounter();
        return;
      }
      // Exit pub to Campfire
      if (x >= 16 && y === 6 && hasFlag(this.state, 'barti_joined')) {
        this.cameras.main.fadeOut(500, 0, 3, 11);
        this.cameras.main.once(Phaser.Cameras.Scene2D.Events.FADE_OUT_COMPLETE, () => {
          this.scene.start('Campfire');
        });
        return;
      }
    }
  }

  private async startSpineEncounter(): Promise<void> {
    this.isBusy = true;
    const runner = new DialogueRunner(CH01.backPainAmbush, this.state.leader);
    await this.dialogueBox.play(runner.allResolved());

    this.cameras.main.flash(300, 255, 255, 255);
    Audio.sfx('encounter');
    this.time.delayedCall(400, () => {
      this.scene.start('Battle', {
        state: this.state,
        enemies: ['bolKregoslupa'],
        bg: 'battle_apartment_bg',
        returnScene: 'World',
      });
    });
  }

  private async startSlackEncounter(): Promise<void> {
    this.isBusy = true;
    const runner = new DialogueRunner(CH01.laptop, this.state.leader);
    await this.dialogueBox.play(runner.allResolved());

    this.cameras.main.flash(300, 255, 255, 255);
    Audio.sfx('encounter');
    this.time.delayedCall(400, () => {
      this.scene.start('Battle', {
        state: this.state,
        enemies: ['slacki'],
        bg: 'battle_apartment_bg',
        returnScene: 'World',
      });
    });
  }

  private async buyCoffee(): Promise<void> {
    this.isBusy = true;
    removeWorldStatus(this.state, 'kacGigant');
    this.updateHud();

    const runner = new DialogueRunner(CH01.city.kioskBuy, this.state.leader);
    await this.dialogueBox.play(runner.allResolved());
    this.isBusy = false;
  }

  // Chapter 2: Garage & Wrestling QTE
  private async triggerGarageEncounter(): Promise<void> {
    this.isBusy = true;
    this.state.chapter = 2;
    this.updateHud();

    const runner = new DialogueRunner(CH02.enter, this.state.leader);
    await this.dialogueBox.play(runner.allResolved());

    const wRunner = new DialogueRunner(CH02.wrestlingPrompt, this.state.leader);
    await this.dialogueBox.play(wRunner.allResolved());

    // Launch Wrestling QTE Bar
    this.startWrestlingQte();
  }

  private startWrestlingQte(): void {
    this.qteContainer = this.add.container(GAME_W / 2, GAME_H / 2).setDepth(850).setScrollFactor(0);
    const qg = this.add.graphics();
    drawPanel(qg, -80, -25, 160, 50, { fill: PAL.panel, border: PAL.cyanHi });
    // Bar frame
    qg.fillStyle(PAL.ink, 1);
    qg.fillRect(-60, -5, 120, 12);
    // Green sweet spot (-15..15)
    qg.fillStyle(PAL.green, 1);
    qg.fillRect(-15, -5, 30, 12);

    this.qteContainer.add(qg);
    this.qteContainer.add(txt(this, 0, -18, 'POWAL DANNY\'EGO! [Z / ENTER]', { color: PAL.yellow, origin: [0.5, 0.5] }));

    this.qteMarkerX = -55;
    this.qteMarkerSpeed = 160;
  }

  private updateQte(delta: number): void {
    if (!this.qteContainer) return;

    this.qteMarkerX += this.qteMarkerSpeed * (delta / 1000);
    if (this.qteMarkerX > 55) {
      this.qteMarkerX = 55;
      this.qteMarkerSpeed = -Math.abs(this.qteMarkerSpeed);
    } else if (this.qteMarkerX < -55) {
      this.qteMarkerX = -55;
      this.qteMarkerSpeed = Math.abs(this.qteMarkerSpeed);
    }

    // Redraw marker
    const g = this.qteContainer.getAt(0) as Phaser.GameObjects.Graphics;
    g.clear();
    drawPanel(g, -80, -25, 160, 50, { fill: PAL.panel, border: PAL.cyanHi });
    g.fillStyle(PAL.ink, 1);
    g.fillRect(-60, -5, 120, 12);
    g.fillStyle(PAL.green, 1);
    g.fillRect(-15, -5, 30, 12);
    // Marker line
    g.fillStyle(PAL.white, 1);
    g.fillRect(this.qteMarkerX - 2, -7, 4, 16);

    if (this.inputHandler.okOrTap()) {
      const isSuccess = Math.abs(this.qteMarkerX) <= 18;
      this.qteContainer.destroy();
      this.qteContainer = null;
      setFlag(this.state, 'garage_wrestled', true);

      if (isSuccess) {
        Audio.sfx('crit');
      } else {
        Audio.sfx('hit');
      }
      this.afterWrestling();
    }
  }

  private async afterWrestling(): Promise<void> {
    const wWin = new DialogueRunner(CH02.wrestlingWin, this.state.leader);
    await this.dialogueBox.play(wWin.allResolved());

    // Neighbour bangs on the door!
    Audio.sfx('hit');
    this.cameras.main.shake(200, 0.015);
    const nInter = new DialogueRunner(CH02.neighbourInterruption, this.state.leader);
    await this.dialogueBox.play(nInter.allResolved());

    // Boss fight against Sąsiad Szkodnik!
    setFlag(this.state, 'fought_sasiad', true);
    this.cameras.main.flash(300, 255, 255, 255);
    Audio.sfx('encounter');
    this.time.delayedCall(400, () => {
      this.scene.start('Battle', {
        state: this.state,
        enemies: ['sasiadSzkodnik'],
        bg: 'battle_garage_bg',
        returnScene: 'World',
      });
    });
  }

  private async afterSasiadBoss(): Promise<void> {
    this.isBusy = true;
    setFlag(this.state, 'danny_alior_joined', true);
    addToParty(this.state, 'danny');
    addToParty(this.state, 'alior');
    this.syncFollowerSprites();
    this.updateHud();

    const runner = new DialogueRunner(CH02.afterBoss, this.state.leader);
    await this.dialogueBox.play(runner.allResolved());
    this.isBusy = false;
  }

  // Chapter 3: Pub "Czarny Krążek"
  private async triggerPubEncounter(): Promise<void> {
    this.isBusy = true;
    this.state.chapter = 3;
    setFlag(this.state, 'pub_cleared', true);
    this.updateHud();

    const pEnter = new DialogueRunner(CH03.enter, this.state.leader);
    await this.dialogueBox.play(pEnter.allResolved());

    const pFight = new DialogueRunner(CH03.beforeFight, this.state.leader);
    await this.dialogueBox.play(pFight.allResolved());

    // Battle against Auto-Tune Hipster & Drogie Piwo!
    setFlag(this.state, 'fought_hipsters', true);
    this.cameras.main.flash(300, 255, 255, 255);
    Audio.sfx('encounter');
    this.time.delayedCall(400, () => {
      this.scene.start('Battle', {
        state: this.state,
        enemies: ['autoTuneHipster', 'drogiePiwo'],
        bg: 'battle_pub_bg',
        returnScene: 'World',
      });
    });
  }

  private async afterPubBattle(): Promise<void> {
    this.isBusy = true;
    setFlag(this.state, 'barti_joined', true);
    addToParty(this.state, 'barti');
    this.syncFollowerSprites();
    this.updateHud();

    const runner = new DialogueRunner(CH03.afterFight, this.state.leader);
    await this.dialogueBox.play(runner.allResolved());
    this.isBusy = false;
  }

  private transitionToMap(mapName: string, targetX: number, targetY: number): void {
    this.isBusy = true;
    this.cameras.main.fadeOut(250, 0, 3, 11);
    this.cameras.main.once(Phaser.Cameras.Scene2D.Events.FADE_OUT_COMPLETE, () => {
      this.currentMap = mapName;
      this.buildMap(mapName);
      this.updateAtmosphere();
      this.playerSprite.setPosition(targetX * TILE + 8, targetY * TILE + 8);
      this.state.x = targetX;
      this.state.y = targetY;
      this.trail = [];
      this.syncFollowerSprites();
      this.updateHud();
      this.cameras.main.fadeIn(250, 0, 3, 11);
      this.isBusy = false;
    });
  }
}
