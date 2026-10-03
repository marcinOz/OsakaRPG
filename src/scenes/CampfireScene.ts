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

export class CampfireScene extends Phaser.Scene {
  private inputHandler!: Input;
  private dialogueBox!: DialogueBox;
  private weatherHandle!: WeatherHandle;
  private fireSprite!: Phaser.GameObjects.Sprite;
  private woodAdded = 0;
  private isBusy = false;

  constructor() {
    super('Campfire');
  }

  create(): void {
    applyCrtToCamera(this);
    Audio.playSong('camp', { fadeMs: 600 });
    setTimeOfDay(this, 'night');

    // Background
    this.add.image(GAME_W / 2, GAME_H / 2, 'campfire_bg').setDisplaySize(GAME_W, GAME_H);

    // Weather: floating rising embers from fire pit
    this.weatherHandle = addWeather(this, 'embers', { x: GAME_W / 2, y: 175 });

    // Animated central campfire
    this.fireSprite = this.add.sprite(GAME_W / 2, 175, 'fire', 0).setDepth(200);
    this.fireSprite.play('anim_fire');

    // 6 Seated Friends around the fire
    this.setupSeatedFriends();

    // Top: [PARTY STATS] HUD Panel (§5 spec)
    this.createPartyStatsHud();

    // Action buttons bar at bottom
    this.createActionBar();

    this.dialogueBox = new DialogueBox(this, 1000);
    this.inputHandler = new Input(this);

    // Play intro campfire dialogue
    this.time.delayedCall(500, () => this.playCampfireIntro());
  }

  private createPartyStatsHud(): void {
    const hg = this.add.graphics().setDepth(500);
    drawPanel(hg, 4, 3, GAME_W - 8, 30, { fill: PAL.navy, border: PAL.steel });

    txt(this, 8, 5, '[PARTY STATS]', { color: PAL.yellow });

    // Row 1
    txt(this, 8, 14, 'DANNY [HP: 100/100]  |  ALIOR [MP: 85/85]  |  LISU [SPD: MAX]', { color: PAL.cyan });
    // Row 2
    txt(this, 8, 22, 'BARTI [BUFF: BASS]   |  OZIEM [FIRE: ON]   |  ŁUKI [RESCUE: READY]', { color: PAL.cyanHi });
  }

  private setupSeatedFriends(): void {
    // Left side heroes (facing right toward fire)
    const leftHeroes = ['danny', 'alior', 'lisu'];
    const leftPositions = [
      { x: GAME_W / 2 - 65, y: 175 },
      { x: GAME_W / 2 - 40, y: 185 },
      { x: GAME_W / 2 - 85, y: 168 },
    ];

    leftHeroes.forEach((hid, i) => {
      const pos = leftPositions[i];
      const spr = this.add.sprite(pos.x, pos.y, `${hid}_sit`, 0).setDepth(150);
      spr.play(`anim_${hid}_sit`);
      spr.setFlipX(true); // Face fire
    });

    // Right side heroes (facing left toward fire)
    const rightHeroes = ['barti', 'oziem', 'luki'];
    const rightPositions = [
      { x: GAME_W / 2 + 40, y: 185 },
      { x: GAME_W / 2 + 65, y: 175 },
      { x: GAME_W / 2 + 85, y: 168 },
    ];

    rightHeroes.forEach((hid, i) => {
      const pos = rightPositions[i];
      const spr = this.add.sprite(pos.x, pos.y, `${hid}_sit`, 0).setDepth(150);
      spr.play(`anim_${hid}_sit`);
    });
  }

  private createActionBar(): void {
    const bg = this.add.graphics().setDepth(400);
    drawPanel(bg, 4, GAME_H - 18, GAME_W - 8, 15, { fill: PAL.panel, border: PAL.steel });

    txt(this, 16, GAME_H - 15, '[1] Dodaj drewna       [2] Puść O.S.T.R. z głośnika       [3] Wznieś toast', {
      color: PAL.cyanHi,
    });
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

    // Blue fire plot twist! (Chapter 8 teaser)
    setTimeOfDay(this, 'blueFire');
    this.fireSprite.setTint(PAL.blueFire);
    Audio.sfx('frameTrap');

    await this.dialogueBox.play([
      { name: 'SYSTEM', text: 'Nagle płomienie zaczynają migotać... na upiorny błękit!', color: PAL.blueFire },
      { name: '???', text: 'Co tu się dzieje?! Nielegalne obozowisko! Hałas po 22:00!', color: PAL.red },
      { name: 'OZIEM', text: 'Kurwa... tylko nie on.', portrait: 'portrait_oziem_64', color: PAL.teal },
      { name: 'SYSTEM', text: 'CIĄG DALSZY NASTĄPI!\nRozdział 8: Strażnik Leśny i Klątwa Dorosłości\nRozdział 9: Ostateczna Batalia o Wolność', color: PAL.cyanHi },
    ]);

    // Return to Title screen
    this.cameras.main.fadeOut(600, 0, 3, 11);
    this.cameras.main.once(Phaser.Cameras.Scene2D.Events.FADE_OUT_COMPLETE, () => {
      this.scene.start('Title');
    });
  }
}
