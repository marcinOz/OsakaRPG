import Phaser from 'phaser';
import { GAME_W, GAME_H, PAL, TILE } from '@/config';
import { HeroId } from '@/types';
import { GameData, newGame, walkSpeedMultiplier, hasFlag, setFlag, removeWorldStatus } from '@/systems/GameState';
import { CH01 } from '@/content/chapters/ch01';
import { DialogueBox } from '@/ui/DialogueBox';
import { DialogueRunner } from '@/systems/Dialogue';
import { Input } from '@/ui/Input';
import { Audio } from '@/audio/ChipAudio';
import { applyCrtToCamera } from '@/fx/CrtPipeline';
import { txt } from '@/ui/Text';
import { drawPanel } from '@/ui/Panel';
import { setTimeOfDay } from '@/fx/Palette';

export class WorldScene extends Phaser.Scene {
  private state!: GameData;
  private inputHandler!: Input;
  private dialogueBox!: DialogueBox;
  private playerSprite!: Phaser.GameObjects.Sprite;
  private mapContainer!: Phaser.GameObjects.Container;
  private hudContainer!: Phaser.GameObjects.Container;
  private hudText!: Phaser.GameObjects.BitmapText | Phaser.GameObjects.Text;
  private isBusy = false;
  private currentMap = 'apartment';

  // Tile grid: 10 rows x 15 cols = 240x160 centered
  private mapW = 18;
  private mapH = 12;
  private solids: boolean[][] = [];

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
      // Returned from battle
      this.isBusy = false;
    }
  }

  create(): void {
    applyCrtToCamera(this);
    this.cameras.main.setBackgroundColor(PAL.void);

    Audio.playSong('ch01_explore', { fadeMs: 500 });
    setTimeOfDay(this, 'morning');

    this.mapContainer = this.add.container(0, 0);
    this.hudContainer = this.add.container(0, 0).setDepth(900).setScrollFactor(0);

    this.buildMap(this.currentMap);

    // Player sprite
    const px = this.state.x * TILE + 8;
    const py = this.state.y * TILE + 8;
    this.playerSprite = this.add.sprite(px, py, `${this.state.leader}_walk`, 0).setDepth(100);
    this.playerSprite.play(`anim_${this.state.leader}_walk_down`);
    this.playerSprite.stop();

    this.cameras.main.startFollow(this.playerSprite, true, 0.1, 0.1);
    this.cameras.main.setBounds(0, 0, this.mapW * TILE, this.mapH * TILE);

    // HUD Top Bar
    const hg = this.add.graphics();
    drawPanel(hg, 4, 4, GAME_W - 8, 16, { fill: PAL.navy, border: PAL.steel, glow: false });
    this.hudContainer.add(hg);

    this.hudText = txt(this, 10, 8, '', { color: PAL.cyan });
    this.hudContainer.add(this.hudText);
    this.updateHud();

    this.dialogueBox = new DialogueBox(this, 1000);
    this.inputHandler = new Input(this);

    // Start Chapter 1 wake up sequence if new game
    if (!hasFlag(this.state, 'ch1_woke_up')) {
      this.time.delayedCall(400, () => this.runWakeUpSequence());
    }
  }

  private updateHud(): void {
    const leaderName = this.state.leader.toUpperCase();
    const hasHangover = this.state.worldStatuses.includes('kacGigant');
    const statusTag = hasHangover ? ' [DEBUFF: KAC GIGANT (-20% SPD)]' : ' [STATUS: OK]';
    const loc = this.currentMap === 'apartment' ? 'MIESZKANIE' : 'PORANNE MIASTO';
    (this.hudText as any).setText(`LIDER: ${leaderName} | ROZDZIAŁ 1: ${loc}${statusTag}`);
  }

  private buildMap(mapName: string): void {
    this.mapContainer.removeAll(true);
    this.solids = [];
    for (let y = 0; y < this.mapH; y++) {
      this.solids[y] = [];
      for (let x = 0; x < this.mapW; x++) {
        this.solids[y][x] = false;
      }
    }

    if (mapName === 'apartment') {
      // 18x12 room
      for (let y = 0; y < this.mapH; y++) {
        for (let x = 0; x < this.mapW; x++) {
          let tileIdx = 0; // wood floor
          let isSolid = false;

          // Outer walls
          if (y === 0) {
            tileIdx = 2; // wall top
            isSolid = true;
          } else if (y === 1) {
            tileIdx = 1; // wall
            isSolid = true;
          } else if (y === this.mapH - 1 || x === 0 || x === this.mapW - 1) {
            tileIdx = 1;
            isSolid = true;
          }

          // Furniture
          if (x === 3 && y === 2) { tileIdx = 3; isSolid = true; } // bed head
          if (x === 3 && y === 3) { tileIdx = 4; isSolid = true; } // bed body
          if (x === 8 && y === 2) { tileIdx = 6; isSolid = true; } // desk PC
          if (x === 9 && y === 2) { tileIdx = 6; isSolid = true; }
          if (x === 6 && y === 5) { tileIdx = 5; } // rug (walkable)
          if (x === 7 && y === 5) { tileIdx = 5; }
          if (x === 10 && y === this.mapH - 1) {
            tileIdx = 7; // door to city!
            isSolid = false;
          }

          this.solids[y][x] = isSolid;
          const spr = this.add.image(x * TILE + 8, y * TILE + 8, 'tiles_apartment');
          spr.setCrop(tileIdx * 16, 0, 16, 16);
          this.mapContainer.add(spr);
        }
      }
    } else {
      // City street (blokowisko)
      for (let y = 0; y < this.mapH; y++) {
        for (let x = 0; x < this.mapW; x++) {
          let tileIdx = 1; // sidewalk
          let isSolid = false;

          if (y < 3) {
            tileIdx = (x % 2 === 0) ? 2 : 3; // building wall & windows
            isSolid = true;
          } else if (y >= 8) {
            tileIdx = 0; // asphalt road
          }

          // Żabka kiosk at x=4, y=3
          if (x === 4 && y === 3) { tileIdx = 5; isSolid = true; }
          // Bench at x=10, y=4
          if (x === 10 && y === 4) { tileIdx = 6; isSolid = true; }
          // Garage door at right exit: x=17, y=5
          if (x === 17 && y === 5) { tileIdx = 7; isSolid = false; }

          this.solids[y][x] = isSolid;
          const spr = this.add.image(x * TILE + 8, y * TILE + 8, 'tiles_city');
          spr.setCrop(tileIdx * 16, 0, 16, 16);
          this.mapContainer.add(spr);
        }
      }
    }
  }

  private async runWakeUpSequence(): Promise<void> {
    this.isBusy = true;
    setFlag(this.state, 'ch1_woke_up', true);

    // Audio notification
    Audio.sfx('notification');

    const runner = new DialogueRunner(CH01.wake, this.state.leader);
    await this.dialogueBox.play(runner.allResolved());

    // Show phone notification popup: "EKIPA 36+ [REUNION NIGHT]"
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

    const title = txt(this, -90, -62, 'WHATSAPP: EKIPA 36+ [REUNION NIGHT]', { color: PAL.yellow });
    pop.add(title);

    // Chat messages
    CH01.groupChat.forEach((msg, i) => {
      const isLeader = msg.from === this.state.leader;
      const color = isLeader ? PAL.cyan : PAL.white;
      const mt = txt(this, -100, -42 + i * 16, `${msg.from.toUpperCase()}: ${msg.text}`, {
        color,
        maxWidth: 200,
      });
      pop.add(mt);
    });

    const prompt = txt(this, 0, 56, '[NACIŚNIJ ENTER / Z]', { color: PAL.silver, align: 'center', origin: [0.5, 0.5] });
    pop.add(prompt);

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

      let targetX = this.playerSprite.x + axis.x * speed;
      let targetY = this.playerSprite.y + axis.y * speed;

      const tileX = Math.floor(targetX / TILE);
      const tileY = Math.floor(targetY / TILE);

      // Check collision
      if (this.isWalkable(tileX, tileY)) {
        this.playerSprite.x = targetX;
        this.playerSprite.y = targetY;
        this.state.x = tileX;
        this.state.y = tileY;
      }

      // Anim
      const dir = axis.x > 0 ? 'right' : axis.x < 0 ? 'left' : axis.y > 0 ? 'down' : 'up';
      this.playerSprite.play(`anim_${this.state.leader}_walk_${dir}`, true);

      // Check triggers
      this.checkTriggers(tileX, tileY);
    } else {
      this.playerSprite.stop();
    }
  }

  private isWalkable(x: number, y: number): boolean {
    if (x < 0 || x >= this.mapW || y < 0 || y >= this.mapH) return false;
    return !this.solids[y]?.[x];
  }

  private checkTriggers(x: number, y: number): void {
    if (this.currentMap === 'apartment') {
      // Bed wake-up fight with back pain (first time stepping near bed)
      if (x === 4 && y === 4 && !hasFlag(this.state, 'ch1_fought_spine')) {
        setFlag(this.state, 'ch1_fought_spine', true);
        this.startSpineEncounter();
        return;
      }

      // Desk PC slack check
      if ((x === 8 || x === 9) && y === 3 && !hasFlag(this.state, 'ch1_fought_slack')) {
        setFlag(this.state, 'ch1_fought_slack', true);
        this.startSlackEncounter();
        return;
      }

      // Door to City
      if (x === 10 && y >= this.mapH - 1) {
        this.transitionToMap('city', 5, 4);
        return;
      }
    } else if (this.currentMap === 'city') {
      // Kiosk coffee purchase
      if (x === 4 && y === 4 && !hasFlag(this.state, 'bought_coffee')) {
        setFlag(this.state, 'bought_coffee', true);
        this.buyCoffee();
        return;
      }

      // Reaching Danny's Garage exit
      if (x >= 16 && y === 5) {
        this.reachGarage();
        return;
      }
    }
  }

  private async startSpineEncounter(): Promise<void> {
    this.isBusy = true;
    const runner = new DialogueRunner(CH01.backPainAmbush, this.state.leader);
    await this.dialogueBox.play(runner.allResolved());

    // Launch BattleScene!
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
    // Cures hangover!
    removeWorldStatus(this.state, 'kacGigant');
    this.updateHud();

    const runner = new DialogueRunner(CH01.city.kioskBuy, this.state.leader);
    await this.dialogueBox.play(runner.allResolved());
    this.isBusy = false;
  }

  private async reachGarage(): Promise<void> {
    this.isBusy = true;
    const runner = new DialogueRunner(CH01.city.garage, this.state.leader);
    await this.dialogueBox.play(runner.allResolved());

    // Wrap up Chapter 1 vertical slice -> show tease card or transition to Campfire!
    await this.dialogueBox.play([
      {
        name: 'SYSTEM',
        text: 'ROZDZIAŁ 1 UKOŃCZONY!\nEkipa zebrała się w komplecie.\nPrzechodzimy do Rozdziału 7: Ognisko!',
        color: PAL.cyan,
      },
    ]);

    this.cameras.main.fadeOut(500, 0, 3, 11);
    this.cameras.main.once(Phaser.Cameras.Scene2D.Events.FADE_OUT_COMPLETE, () => {
      this.scene.start('Campfire');
    });
  }

  private transitionToMap(mapName: string, targetX: number, targetY: number): void {
    this.isBusy = true;
    this.cameras.main.fadeOut(250, 0, 3, 11);
    this.cameras.main.once(Phaser.Cameras.Scene2D.Events.FADE_OUT_COMPLETE, () => {
      this.currentMap = mapName;
      this.buildMap(mapName);
      this.playerSprite.setPosition(targetX * TILE + 8, targetY * TILE + 8);
      this.state.x = targetX;
      this.state.y = targetY;
      this.updateHud();
      this.cameras.main.fadeIn(250, 0, 3, 11);
      this.isBusy = false;
    });
  }
}
