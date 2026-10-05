import Phaser from 'phaser';
import { GAME_W, GAME_H, PAL } from '@/config';
import { txt } from '@/ui/Text';
import { drawPanel } from '@/ui/Panel';
import { DialogueBox } from '@/ui/DialogueBox';
import { Input } from '@/ui/Input';
import { Audio } from '@/audio/ChipAudio';
import { addWeather, WeatherHandle } from '@/fx/Weather';
import { applyCrtToCamera } from '@/fx/CrtPipeline';
import { setTimeOfDay } from '@/fx/Palette';
import { flash } from '@/fx/Juice';
import { CH08 } from '@/content/chapters/ch08';
import { CH09 } from '@/content/chapters/ch09';
import { DialogueRunner } from '@/systems/Dialogue';
import { GameData, newGame } from '@/systems/GameState';
import type { HeroId } from '@/types';
import { startBattle } from '@/content/encounters';

export class CampfireScene extends Phaser.Scene {
  private inputHandler!: Input;
  private dialogueBox!: DialogueBox;
  private weatherHandle!: WeatherHandle;
  private fireSprite!: Phaser.GameObjects.Sprite;
  private state!: GameData;
  private woodAdded = 0;
  private isBusy = false;
  private startAtJanusz = false;

  constructor() {
    super('Campfire');
  }

  init(data?: { state?: GameData; startAtJanusz?: boolean }): void {
    this.state = data?.state || newGame('oziem');
    this.startAtJanusz = Boolean(data?.startAtJanusz);
    const allHeroes = ['danny', 'alior', 'lisu', 'barti', 'oziem', 'luki'] as HeroId[];
    for (const h of allHeroes) {
      if (!this.state.party.includes(h)) {
        this.state.party.push(h);
      }
    }
  }

  create(): void {
    applyCrtToCamera(this);
    Audio.playSong('camp', { fadeMs: 600 });
    setTimeOfDay(this, 'night');

    // Background
    this.add.image(GAME_W / 2, GAME_H / 2, 'campfire_bg').setDisplaySize(GAME_W, GAME_H);

    // Weather: floating rising embers from fire pit
    // Weather: floating rising embers from fire pit
    this.weatherHandle = addWeather(this, 'embers', { x: GAME_W / 2, y: 440 });

    // Animated central campfire (64x80) placed at the stone fire pit
    this.fireSprite = this.add.sprite(GAME_W / 2, 465, 'fire', 0).setOrigin(0.5, 0.92).setDepth(450);
    this.fireSprite.play('anim_fire');

    // 6 Seated Friends around the fire
    this.setupSeatedFriends();

    // Top: [PARTY STATS] HUD Panel (§5 spec)
    this.createPartyStatsHud();

    // Action buttons bar at bottom
    this.createActionBar();

    this.dialogueBox = new DialogueBox(this, 1000);
    this.inputHandler = new Input(this);

    // Play intro campfire dialogue or jump to Janusz if started from Chapter 8 Dev Warp
    if (this.startAtJanusz) {
      this.time.delayedCall(500, () => this.triggerJanuszSequence());
    } else {
      this.time.delayedCall(500, () => this.playCampfireIntro());
    }
  }

  private createPartyStatsHud(): void {
    const hg = this.add.graphics().setDepth(500);
    drawPanel(hg, 16, 10, GAME_W - 32, 84, { fill: PAL.navy, border: PAL.steel, glow: true });

    txt(this, GAME_W / 2, 20, '★ PARTY STATS – ROZDZIAŁ 7: OGNISKO W WILCZYM LESIE ★', {
      color: PAL.yellow,
      fontSize: '13px',
      fontStyle: 'bold',
      fontFamily: 'monospace, sans-serif',
      resolution: 2,
      origin: [0.5, 0.5],
    });

    // 6 Heroes organized into a 2 rows x 3 columns grid for mobile readability
    const row1 = [
      'DANNY [HP: 100/100]',
      'ALIOR [MP: 85/85]',
      'LISU [SPD: MAX]',
    ];
    const row2 = [
      'BARTI [BUFF: BASS]',
      'OZIEM [FIRE: ON]',
      'ŁUKI [RESCUE: OK]',
    ];

    const startX = 36;
    const colW = (GAME_W - 72) / 3;

    row1.forEach((s, idx) => {
      txt(this, startX + idx * colW + colW / 2, 38, s, {
        color: PAL.cyan,
        fontSize: '13px',
        fontStyle: 'bold',
        fontFamily: 'monospace, sans-serif',
        resolution: 2,
        origin: [0.5, 0.5],
      });
    });

    row2.forEach((s, idx) => {
      txt(this, startX + idx * colW + colW / 2, 58, s, {
        color: PAL.cyanHi,
        fontSize: '13px',
        fontStyle: 'bold',
        fontFamily: 'monospace, sans-serif',
        resolution: 2,
        origin: [0.5, 0.5],
      });
    });

    txt(this, GAME_W / 2, 78, 'EKIPA: KOMPLET (6/6)   |   OGIEŃ: PŁONIE   |   BUFF: KLIMAT LAT MŁODOŚCI', {
      color: PAL.green,
      fontSize: '13px',
      fontStyle: 'bold',
      fontFamily: 'monospace, sans-serif',
      resolution: 2,
      origin: [0.5, 0.5],
    });
  }

  private setupSeatedFriends(): void {
    // Left side heroes (Danny, Alior, Lisu - facing right toward fire)
    const leftHeroes = [
      { id: 'lisu', x: GAME_W / 2 - 165, y: 425 },
      { id: 'danny', x: GAME_W / 2 - 115, y: 455 },
      { id: 'alior', x: GAME_W / 2 - 65, y: 485 },
    ];

    leftHeroes.forEach((h) => {
      // Ground shadow
      this.add.ellipse(h.x, h.y + 12, 28, 10, 0x000000, 0.45).setDepth(h.y - 1);
      const spr = this.add.sprite(h.x, h.y, `${h.id}_sit`, 0).setDepth(h.y);
      spr.play(`anim_${h.id}_sit`);
      spr.setFlipX(true); // Face fire
    });

    // Right side heroes (Barti, Oziem, Łuki - facing left toward fire)
    const rightHeroes = [
      { id: 'luki', x: GAME_W / 2 + 165, y: 425 },
      { id: 'oziem', x: GAME_W / 2 + 115, y: 455 },
      { id: 'barti', x: GAME_W / 2 + 65, y: 485 },
    ];

    rightHeroes.forEach((h) => {
      // Ground shadow
      this.add.ellipse(h.x, h.y + 12, 28, 10, 0x000000, 0.45).setDepth(h.y - 1);
      const spr = this.add.sprite(h.x, h.y, `${h.id}_sit`, 0).setDepth(h.y);
      spr.play(`anim_${h.id}_sit`);
      spr.setFlipX(false); // Face fire
    });
  }

  private createActionBar(): void {
    const bg = this.add.graphics().setDepth(400);
    drawPanel(bg, 16, GAME_H - 46, GAME_W - 32, 38, { fill: PAL.panel, border: PAL.steel, glow: true });

    this.add.image(GAME_W / 2, GAME_H - 27, 'keys_legend', 2).setDepth(500);
  }

  private async playCampfireIntro(): Promise<void> {
    this.isBusy = true;
    await this.dialogueBox.play([
      { name: 'OZIEM', text: 'Ogień pali się stabilnie. Nalewajcie do kubków, panowie!', portrait: 'portrait_oziem_64', color: PAL.teal },
      { name: 'DANNY', text: 'Kurwa... niczego więcej do szczęścia dzisiaj nie trzeba.', portrait: 'portrait_danny_64', color: PAL.fire },
    ]);

    // Play nostalgia round
    await this.dialogueBox.play([
      { name: 'DANNY', text: 'Pamiętacie, jak 15 lat temu siedzieliśmy na ławce pod blokiem bez grosza w kieszeni?', portrait: 'portrait_danny_64', color: PAL.fire },
      { name: 'ALIOR', text: 'I grało się w Gauntlet i Tekkena do czwartej rano na kineskopowym telewizorze...', portrait: 'portrait_alior_64', color: PAL.green },
      { name: 'BARTI', text: 'Ale bit z taśmy magnetofonowej zawsze wszedł idealnie. Kurwa, to były czasy.', portrait: 'portrait_barti_64', color: PAL.denim },
      { name: 'LISU', text: 'A pamiętacie, jak uciekaliśmy przed dozorcą przez trzy podwórka? Nikt mnie wtedy nie złapał. Do dziś.', portrait: 'portrait_lisu_64', color: PAL.red },
      { name: 'ŁUKI', text: 'A ja pamiętam, jak Barti wpadł do jeziora na obozie. Pierwsza akcja ratunkowa w mojej karierze.', portrait: 'portrait_luki_64', color: PAL.cyan },
      { name: 'BARTI', text: 'Miałem walkmana w kieszeni! Ratowałem kasetę, nie siebie!', portrait: 'portrait_barti_64', color: PAL.denim },
      { name: 'OZIEM', text: 'I wtedy pierwszy raz rozpaliłem ognisko z jednej zapałki. Od tamtej pory już nie przestałem.', portrait: 'portrait_oziem_64', color: PAL.teal },
    ]);

    this.isBusy = false;
  }

  override update(_time: number, delta: number): void {
    if (this.dialogueBox.active) {
      this.dialogueBox.update(this.inputHandler, delta);
      return;
    }

    if (this.isBusy) return;

    if (this.inputHandler.pressed('n1')) {
      this.actionAddWood();
    } else if (this.inputHandler.pressed('n2')) {
      this.actionPlayMusic();
    } else if (this.inputHandler.pressed('n3')) {
      this.actionToast();
    }
  }

  private async actionAddWood(): Promise<void> {
    this.isBusy = true;
    Audio.sfx('confirm');

    if (this.woodAdded === 0) {
      this.woodAdded = 1;
      this.fireSprite.setScale(1.25);
      this.weatherHandle.setIntensity(2);
      await this.dialogueBox.play([
        { name: 'OZIEM', text: 'Brzoza na rozpałkę, buk na długi żar. Patrzcie i uczcie się.', portrait: 'portrait_oziem_64', color: PAL.teal },
        { name: 'SYSTEM', text: 'Ogień buzuje mocniej! Iskry lecą wysoko w nocne niebo.', color: PAL.fireHi },
      ]);
    } else {
      await this.dialogueBox.play([
        { name: 'OZIEM', text: 'Starczy, bo nam hamaki spłoną. Żar jest idealny.', portrait: 'portrait_oziem_64', color: PAL.teal },
      ]);
    }
    this.isBusy = false;
  }

  private async actionPlayMusic(): Promise<void> {
    this.isBusy = true;
    Audio.sfx('confirm');
    Audio.playSong('camp', { fadeMs: 300 });

    await this.dialogueBox.play([
      { name: 'BARTI', text: 'Dobra, cisza. Wjeżdża klasyk. Głośnik na pełną.', portrait: 'portrait_barti_64', color: PAL.denim },
      { name: 'SYSTEM', text: '♪ Z głośnika płynie tłusty bit z winyla Bartiego ♪', color: PAL.yellow },
      { name: 'ALIOR', text: 'Ten flow... 60 klatek na sekundę, mordo.', portrait: 'portrait_alior_64', color: PAL.green },
    ]);
    this.isBusy = false;
  }

  private async actionToast(): Promise<void> {
    this.isBusy = true;
    Audio.sfx('confirm');

    await this.dialogueBox.play([
      { name: 'DANNY', text: 'Panowie, wstajemy. Za ekipę!', portrait: 'portrait_danny_64', color: PAL.fire },
      { name: 'LISU', text: 'Za tych, co zawsze wracają.', portrait: 'portrait_lisu_64', color: PAL.red },
      { name: 'ŁUKI', text: 'Za to, że nikt dziś nie wpadł do rzeki. Jeszcze.', portrait: 'portrait_luki_64', color: PAL.cyan },
      { name: 'BARTI', text: 'Za stare bity i nowe wspomnienia!', portrait: 'portrait_barti_64', color: PAL.denim },
      { name: 'ALIOR', text: 'Za brak patchy, które by to zepsuły.', portrait: 'portrait_alior_64', color: PAL.green },
      { name: 'OZIEM', text: 'Za ogień. I za las, który należy dziś do nas.', portrait: 'portrait_oziem_64', color: PAL.teal },
      { name: 'SYSTEM', text: 'MORALE MAX!\nOtrzymano buff: KLIMAT LAT MŁODOŚCI (+50% wszystkie statystyki)!', color: PAL.yellow },
    ]);

    await this.triggerJanuszSequence();
  }

  private async triggerJanuszSequence(): Promise<void> {
    this.isBusy = true;
    // Blue fire plot twist! (Chapter 8)
    setTimeOfDay(this, 'blueFire');
    this.fireSprite.setTint(PAL.blueFire);
    Audio.sfx('frameTrap');
    Audio.playSong('ch08_industrial', { fadeMs: 500 });
    addWeather(this, 'fog');

    const ch8Runner = new DialogueRunner(CH08.twist, this.state.leader, this.state.party);
    await this.dialogueBox.play(ch8Runner.allResolved());

    // Chapter 9: Dimensional Rift Intro
    const ch9Runner = new DialogueRunner(CH09.intro, this.state.leader, this.state.party);
    await this.dialogueBox.play(ch9Runner.allResolved());

    // Enter Final Boss Battle!
    flash(this, 0xffffff, 400);
    Audio.sfx('encounter');

    this.time.delayedCall(400, () => {
      startBattle(this, 'finalBossRift', {
        state: this.state,
      });
    });
  }
}
