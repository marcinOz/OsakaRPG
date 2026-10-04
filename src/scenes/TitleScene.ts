import Phaser from 'phaser';
import { GAME_W, GAME_H, PAL } from '@/config';
import { txt, TextObj } from '@/ui/Text';
import { Input } from '@/ui/Input';
import { Menu } from '@/ui/Menu';
import { Audio } from '@/audio/ChipAudio';
import { addWeather } from '@/fx/Weather';
import { isCrtEnabled, setCrtEnabled, applyCrtToCamera } from '@/fx/CrtPipeline';
import { Saves } from '@/systems/Save';
import { HEROES } from '@/content/heroes';
import { ENEMIES } from '@/content/enemies';
import { drawPanel } from '@/ui/Panel';
import {
  ALL_HERO_IDS,
  CHAPTER_DEV_REGISTRY,
  createDevChapterState,
} from '@/systems/DevState';
import { startBattle } from '@/content/encounters';

export class TitleScene extends Phaser.Scene {
  private inputHandler!: Input;
  private menu!: Menu;

  // Audio Splash Gate
  private isAudioGateActive = false;
  private audioSplashPrompt: TextObj | null = null;
  private audioSplashTween: Phaser.Tweens.Tween | null = null;
  private splashUnlockHandler: (() => void) | null = null;
  private gateDismissedFrame = -1;
  private devPanelToggledFrame = -1;

  // Dev Panel State & Objects
  private isDevPanelOpen = false;
  private activeDevTab: 'chapters' | 'villains' = 'chapters';
  private devPanelContainer!: Phaser.GameObjects.Container;
  private selectedHeroIdx = 0;
  private selectedChapterIdx = 0;
  private selectedVillainIdx = 0;

  // Tabs & Views
  private tabChaptersBg!: Phaser.GameObjects.Graphics;
  private tabVillainsBg!: Phaser.GameObjects.Graphics;
  private tabChaptersText!: TextObj;
  private tabVillainsText!: TextObj;

  private chapterViewContainer!: Phaser.GameObjects.Container;
  private villainsViewContainer!: Phaser.GameObjects.Container;

  private heroCardGraphics!: Phaser.GameObjects.Graphics;
  private chapterCardGraphics!: Phaser.GameObjects.Graphics;
  private leaderInfoText!: TextObj;
  private chapterTextRows: { title: TextObj; details: TextObj }[] = [];

  private villainsCardGraphics!: Phaser.GameObjects.Graphics;
  private villainsSubtitleText!: TextObj;
  private villainCardsList: { id: string; x: number; y: number; w: number; h: number }[] = [];

  private isTransitioning = false;

  constructor() {
    super('Title');
  }

  create(): void {
    applyCrtToCamera(this);
    const audioUnlocked = Audio.isUnlocked();
    if (audioUnlocked) {
      Audio.playSong('title', { fadeMs: 600 });
    }

    // Background
    this.add.image(GAME_W / 2, GAME_H / 2, 'title_bg').setDisplaySize(GAME_W, GAME_H);

    // Weather particles: wandering fireflies
    addWeather(this, 'fireflies');

    // Retro monitor top bar
    const bar = this.add.graphics();
    bar.fillStyle(PAL.panel, 0.95);
    bar.fillRect(0, 0, GAME_W, 20);
    bar.fillStyle(PAL.steel, 1);
    bar.fillRect(0, 19, GAME_W, 1);
    bar.setDepth(1050);

    const topBarTitle = txt(this, 12, 4, 'THE PACK: RETRO ENGINE v2.0 [HD PIXEL-PERFECT EDITION]', {
      color: PAL.cyan,
      big: false,
    });
    topBarTitle.setDepth(1051);

    // Window control buttons ▢ ▢ ✕
    const winBtns = txt(this, GAME_W - 48, 4, '― ▢ ✕', { color: PAL.silver });
    winBtns.setDepth(1051);

    // Secret shortcut: Clicking retro top bar title toggles Dev Panel
    const topBarZone = this.add
      .zone(0, 0, 480, 20)
      .setOrigin(0, 0)
      .setDepth(1052)
      .setInteractive({ useHandCursor: true });
    topBarZone.on('pointerdown', (pointer: Phaser.Input.Pointer) => {
      pointer.event.stopPropagation();
      if (this.isTransitioning) return;
      if (this.isAudioGateActive) {
        this.dismissAudioSplashGate();
      }
      this.toggleDevPanel();
    });

    // Secret shortcut: pressing 'D' or '~' / '`' toggles Dev Panel
    this.input.keyboard?.on('keydown', (e: KeyboardEvent) => {
      if (this.isTransitioning) return;
      const key = e.key.toLowerCase();
      if (key === 'd' || key === '~' || key === '`' || e.code === 'Backquote') {
        if (this.isAudioGateActive) {
          this.dismissAudioSplashGate();
        }
        this.toggleDevPanel();
      }
    });

    // Main Logo
    txt(this, GAME_W / 2, 120, 'THE PACK', {
      color: PAL.yellow,
      big: true,
      align: 'center',
      origin: [0.5, 0.5],
    });

    txt(this, GAME_W / 2, 155, 'LEGEND OF THE FOREST FIREPLACE', {
      color: PAL.cyanHi,
      big: true,
      align: 'center',
      origin: [0.5, 0.5],
    });

    txt(this, GAME_W / 2, 185, 'Ekipa 36+ • Kronika Przyjaźni i Ognia', {
      color: PAL.silver,
      big: false,
      align: 'center',
      origin: [0.5, 0.5],
    });

    // Check existing save
    const saveList = Saves.list();
    const hasSave = saveList[0].exists;

    const crtState = isCrtEnabled();
    const menuItems = [
      { label: 'NOWA GRA' },
      { label: hasSave ? `KONTYNUUJ (${saveList[0].leader})` : 'KONTYNUUJ', disabled: !hasSave },
      { label: `FILTR CRT: ${crtState ? 'WŁĄCZONY' : 'WYŁĄCZONY'}` },
    ];

    const menuW = 340;
    const menuX = (GAME_W - menuW) / 2;
    const menuY = 260;
    this.menu = new Menu(this, menuX, menuY, menuW, menuItems);

    // Footer credits
    txt(this, GAME_W / 2, GAME_H - 24, '© 2026 THE PACK CREW • [STRZAŁKI / Z: WYBIERZ]', {
      color: PAL.grey,
      align: 'center',
      origin: [0.5, 0.5],
    });

    this.inputHandler = new Input(this);

    // Create Dev Panel Modal Container
    this.createDevPanel();

    // Audio Splash Gate: If not unlocked, display retro pulsing prompt and await user gesture
    if (!audioUnlocked) {
      this.showAudioSplashGate();
    }
  }

  private showAudioSplashGate(): void {
    this.isAudioGateActive = true;
    this.menu.setVisible(false);
    this.menu.root.setAlpha(0);

    // Retro pulsing prompt in the center
    this.audioSplashPrompt = txt(
      this,
      GAME_W / 2,
      290,
      '► NACIŚNIJ DOWOLNY KLAWISZ LUB KLIKNIJ ◄',
      {
        color: PAL.yellow,
        big: true,
        align: 'center',
        origin: [0.5, 0.5],
      }
    );
    this.audioSplashPrompt.setDepth(950);

    this.audioSplashTween = this.tweens.add({
      targets: this.audioSplashPrompt,
      alpha: { from: 1, to: 0.2 },
      duration: 650,
      yoyo: true,
      repeat: -1,
      ease: 'Sine.easeInOut',
    });

    this.splashUnlockHandler = () => {
      this.dismissAudioSplashGate();
    };

    this.input.keyboard?.once('keydown', this.splashUnlockHandler);
    this.input.once('pointerdown', this.splashUnlockHandler);
  }

  private dismissAudioSplashGate(): void {
    if (!this.isAudioGateActive) return;
    this.isAudioGateActive = false;
    this.gateDismissedFrame = this.game?.loop?.frame ?? -1;

    if (this.splashUnlockHandler) {
      this.input.keyboard?.off('keydown', this.splashUnlockHandler);
      this.input.off('pointerdown', this.splashUnlockHandler);
      this.splashUnlockHandler = null;
    }

    // Unlock Audio and start title music
    Audio.unlock();
    Audio.playSong('title', { fadeMs: 600 });
    Audio.sfx('confirm');

    // Fade out splash prompt
    if (this.audioSplashTween) {
      this.audioSplashTween.stop();
      this.audioSplashTween = null;
    }
    if (this.audioSplashPrompt) {
      const promptToFade = this.audioSplashPrompt;
      this.audioSplashPrompt = null;
      this.tweens.add({
        targets: promptToFade,
        alpha: 0,
        duration: 200,
        onComplete: () => {
          promptToFade.destroy();
        },
      });
    }

    // Smoothly fade in main menu
    this.menu.setVisible(true);
    this.menu.root.setAlpha(0);
    this.tweens.add({
      targets: this.menu.root,
      alpha: 1,
      duration: 400,
      ease: 'Sine.easeOut',
    });
  }

  private createDevPanel(): void {
    const pw = 920;
    const ph = 520;
    const px = (GAME_W - pw) / 2;
    const py = 28;

    this.devPanelContainer = this.add.container(0, 0).setDepth(1000).setVisible(false);

    // 1. Semi-transparent black backdrop (blocks clicks to main menu)
    const backdrop = this.add.rectangle(0, 0, GAME_W, GAME_H, 0x000000, 0.78).setOrigin(0, 0);
    backdrop.setInteractive(); // consume pointer clicks
    this.devPanelContainer.add(backdrop);

    // 2. Main Panel Window
    const winGraphics = this.add.graphics();
    drawPanel(winGraphics, px, py, pw, ph);
    this.devPanelContainer.add(winGraphics);

    // 3. Tab Switcher Header (Chapters / Heroes VS Dev Villains)
    this.tabChaptersBg = this.add.graphics();
    this.tabVillainsBg = this.add.graphics();
    this.devPanelContainer.add([this.tabChaptersBg, this.tabVillainsBg]);

    const tab1W = 270;
    const tab2W = 330;
    const tabH = 26;
    const tab1X = px + 24;
    const tab2X = px + 304;
    const tabY = py + 12;

    this.tabChaptersText = txt(this, tab1X + 16, tabY + 5, '1. ROZDZIAŁY & BOHATEROWIE', {
      color: PAL.yellow,
      big: true,
    });
    this.tabVillainsText = txt(this, tab2X + 16, tabY + 5, '2. ⚡ DEV VILLAINS (11 WROGÓW)', {
      color: PAL.silver,
      big: true,
    });
    this.devPanelContainer.add([this.tabChaptersText, this.tabVillainsText]);

    // Tab Click Zones
    const tab1Zone = this.add
      .zone(tab1X, tabY, tab1W, tabH)
      .setOrigin(0, 0)
      .setInteractive({ useHandCursor: true });
    tab1Zone.on('pointerdown', () => {
      if (this.isTransitioning) return;
      this.switchDevTab('chapters');
    });

    const tab2Zone = this.add
      .zone(tab2X, tabY, tab2W, tabH)
      .setOrigin(0, 0)
      .setInteractive({ useHandCursor: true });
    tab2Zone.on('pointerdown', () => {
      if (this.isTransitioning) return;
      this.switchDevTab('villains');
    });
    this.devPanelContainer.add([tab1Zone, tab2Zone]);

    // Close Button in header
    const closeBtn = txt(this, px + pw - 120, py + 16, '[✕ POWRÓT]', {
      color: PAL.red,
      big: true,
      origin: [0, 0.5],
    });
    this.devPanelContainer.add(closeBtn);

    const closeZone = this.add
      .zone(px + pw - 125, py + 5, 110, 24)
      .setOrigin(0, 0)
      .setInteractive({ useHandCursor: true });
    closeZone.on('pointerdown', () => this.closeDevPanel());
    this.devPanelContainer.add(closeZone);

    // =========================================================================
    // SUB-VIEW A: CHAPTERS & HEROES
    // =========================================================================
    this.chapterViewContainer = this.add.container(0, 0);
    this.devPanelContainer.add(this.chapterViewContainer);

    // 4. Hero Selector Strip at Top
    const heroStripY = py + 42;
    const heroLabel = txt(this, px + 24, heroStripY, 'WYBIERZ BOHATERA (LIDERA DRUŻYNY):', {
      color: PAL.silver,
      big: false,
    });
    this.chapterViewContainer.add(heroLabel);

    this.heroCardGraphics = this.add.graphics();
    this.chapterViewContainer.add(this.heroCardGraphics);

    const heroCardW = 138;
    const heroCardH = 72;
    const heroStartX = px + 24;
    const heroCardsY = heroStripY + 18;

    ALL_HERO_IDS.forEach((hid, idx) => {
      const cardX = heroStartX + idx * (heroCardW + 9);
      const def = HEROES[hid];

      // Portrait
      const portSpr = this.add
        .image(cardX + 38, heroCardsY + 36, `portrait_${hid}_64`)
        .setDisplaySize(56, 56)
        .setOrigin(0.5, 0.5);
      this.chapterViewContainer.add(portSpr);

      // Hero name & class
      const nameTxt = txt(this, cardX + 72, heroCardsY + 18, def.name, {
        color: def.color,
        big: true,
      });
      const classTxt = txt(this, cardX + 72, heroCardsY + 40, def.className, {
        color: PAL.silver,
        big: false,
      });
      this.chapterViewContainer.add([nameTxt, classTxt]);

      // Interactive Click Zone
      const heroZone = this.add
        .zone(cardX, heroCardsY, heroCardW, heroCardH)
        .setOrigin(0, 0)
        .setInteractive({ useHandCursor: true });
      heroZone.on('pointerdown', () => {
        if (this.isTransitioning) return;
        this.selectedHeroIdx = idx;
        Audio.sfx('cursor');
        this.updateDevPanelVisuals();
      });
      this.chapterViewContainer.add(heroZone);
    });

    // Leader info subtitle
    this.leaderInfoText = txt(this, px + 24, heroCardsY + heroCardH + 8, '', {
      color: PAL.cyan,
      big: false,
    });
    this.chapterViewContainer.add(this.leaderInfoText);

    // 5. Chapter Grid (2 Columns x 5 Rows)
    const chapterSectionY = heroCardsY + heroCardH + 34;
    const chapterLabel = txt(
      this,
      px + 24,
      chapterSectionY,
      'WYBIERZ ROZDZIAŁ DO TESTOWANIA (WARP):',
      {
        color: PAL.silver,
        big: false,
      }
    );
    this.chapterViewContainer.add(chapterLabel);

    this.chapterCardGraphics = this.add.graphics();
    this.chapterViewContainer.add(this.chapterCardGraphics);

    const colW = 428;
    const rowH = 46;
    const col1X = px + 24;
    const col2X = px + pw - colW - 24;
    const rowStartY = chapterSectionY + 20;

    CHAPTER_DEV_REGISTRY.forEach((_chDef, idx) => {
      const isCol2 = idx >= 5;
      const rowIdx = idx % 5;
      const cx = isCol2 ? col2X : col1X;
      const cy = rowStartY + rowIdx * (rowH + 6);

      const titleTxt = txt(this, cx + 12, cy + 6, '', {
        color: PAL.white,
        big: true,
      });
      const detailsTxt = txt(this, cx + 12, cy + 26, '', {
        color: PAL.silver,
        big: false,
      });
      this.chapterViewContainer.add([titleTxt, detailsTxt]);
      this.chapterTextRows.push({ title: titleTxt, details: detailsTxt });

      // Interactive Click Zone
      const chZone = this.add
        .zone(cx, cy, colW, rowH)
        .setOrigin(0, 0)
        .setInteractive({ useHandCursor: true });
      chZone.on('pointerdown', () => {
        if (this.isTransitioning) return;
        this.selectedChapterIdx = idx;
        this.warpToSelectedChapter();
      });
      chZone.on('pointerover', () => {
        if (this.isTransitioning) return;
        if (this.selectedChapterIdx !== idx) {
          this.selectedChapterIdx = idx;
          Audio.sfx('cursor');
          this.updateDevPanelVisuals();
        }
      });
      this.chapterViewContainer.add(chZone);
    });

    const bottomHint = txt(
      this,
      px + 24,
      py + ph - 22,
      '[TAB]: PRZEŁĄCZ ZAKŁADKĘ   [← / →]: BOHATER   [↑ / ↓]: ROZDZIAŁ   [Z / ENTER]: TESTUJ   [ESC]: POWRÓT',
      {
        color: PAL.grey,
        big: false,
      }
    );
    this.chapterViewContainer.add(bottomHint);

    // =========================================================================
    // SUB-VIEW B: DEV VILLAINS (11 ENEMIES & BOSSES SHOWCASE)
    // =========================================================================
    this.villainsViewContainer = this.add.container(0, 0).setVisible(false);
    this.devPanelContainer.add(this.villainsViewContainer);

    this.villainsSubtitleText = txt(this, px + 24, py + 42, '', {
      color: PAL.yellow,
      big: false,
    });
    this.villainsViewContainer.add(this.villainsSubtitleText);

    this.villainsCardGraphics = this.add.graphics();
    this.villainsViewContainer.add(this.villainsCardGraphics);

    // 11 Enemies in 4 columns x 3 rows grid
    const VILLAIN_KEYS = [
      'bolKregoslupa', 'slacki', 'sasiadSzkodnik', 'autoTuneHipster',
      'drogiePiwo', 'straznik', 'kark', 'rwaKulszowa',
      'panJanusz', 'kredyt', 'audyt'
    ];

    const vCardW = 208;
    const vCardH = 114;
    const vGapX = 13;
    const vGapY = 8;
    const vGridStartY = py + 66;

    VILLAIN_KEYS.forEach((eid, idx) => {
      const col = idx % 4;
      const row = Math.floor(idx / 4);
      const cx = px + 24 + col * (vCardW + vGapX);
      const cy = vGridStartY + row * (vCardH + vGapY);

      this.villainCardsList.push({ id: eid, x: cx, y: cy, w: vCardW, h: vCardH });

      const def = ENEMIES[eid];

      // Animated Sprite
      const spr = this.add.sprite(cx + 38, cy + 54, `enemy_${eid}`, 0);
      spr.setDisplaySize(60, 60);
      if (this.anims.exists(`anim_enemy_${eid}`)) {
        spr.play(`anim_enemy_${eid}`);
      }
      this.villainsViewContainer.add(spr);

      // Enemy Name
      const nameTxt = txt(this, cx + 72, cy + 8, def?.name ?? eid, {
        color: def?.boss ? PAL.yellow : PAL.white,
        big: true,
      });

      // Type / Boss badge
      const isBoss = !!def?.boss;
      const tierTxt = txt(
        this,
        cx + 72,
        cy + 28,
        isBoss ? `★ BOSS Lv.${def.level}` : `WRÓG Lv.${def.level}`,
        { color: isBoss ? PAL.red : PAL.silver, big: false }
      );

      // Stats line
      const statsTxt = txt(
        this,
        cx + 72,
        cy + 46,
        `HP:${def.stats.hp} ATK:${def.stats.atk} DEF:${def.stats.def}`,
        { color: PAL.cyan, big: false }
      );

      // Fight Button Graphic & Text
      const btnBg = this.add.graphics();
      btnBg.fillStyle(PAL.navy, 0.95);
      btnBg.fillRoundedRect(cx + 72, cy + 68, 126, 32, 4);
      btnBg.lineStyle(1, isBoss ? PAL.red : PAL.green, 0.9);
      btnBg.strokeRoundedRect(cx + 72, cy + 68, 126, 32, 4);

      const btnTxt = txt(this, cx + 80, cy + 76, isBoss ? '⚔ WALKAZ BOSSEM' : '⚔ TESTUJ WALKĘ', {
        color: isBoss ? PAL.red : PAL.green,
        big: false,
      });

      this.villainsViewContainer.add([nameTxt, tierTxt, statsTxt, btnBg, btnTxt]);

      // Interactive Click Zone
      const vZone = this.add
        .zone(cx, cy, vCardW, vCardH)
        .setOrigin(0, 0)
        .setInteractive({ useHandCursor: true });

      vZone.on('pointerdown', () => {
        if (this.isTransitioning) return;
        this.selectedVillainIdx = idx;
        this.launchVillainBattle(eid);
      });

      vZone.on('pointerover', () => {
        if (this.isTransitioning) return;
        if (this.selectedVillainIdx !== idx) {
          this.selectedVillainIdx = idx;
          Audio.sfx('cursor');
          this.updateDevPanelVisuals();
        }
      });

      this.villainsViewContainer.add(vZone);
    });

    const villainsHint = txt(
      this,
      px + 24,
      py + ph - 22,
      '[TAB]: PRZEŁĄCZ ZAKŁADKĘ   [STRZAŁKI]: WYBIERZ WROGA   [Z / ENTER / KLIK]: TESTUJ WALKĘ   [ESC]: POWRÓT',
      {
        color: PAL.grey,
        big: false,
      }
    );
    this.villainsViewContainer.add(villainsHint);

    this.updateDevPanelVisuals();
  }

  private switchDevTab(tab: 'chapters' | 'villains'): void {
    if (this.activeDevTab === tab) return;
    this.activeDevTab = tab;
    Audio.sfx('cursor');

    if (tab === 'chapters') {
      this.chapterViewContainer.setVisible(true);
      this.villainsViewContainer.setVisible(false);
    } else {
      this.chapterViewContainer.setVisible(false);
      this.villainsViewContainer.setVisible(true);
    }
    this.updateDevPanelVisuals();
  }

  private toggleDevPanel(): void {
    if (this.isDevPanelOpen) {
      this.closeDevPanel();
    } else {
      this.openDevPanel();
    }
  }

  private openDevPanel(): void {
    this.isDevPanelOpen = true;
    this.isTransitioning = false;
    this.devPanelToggledFrame = this.game?.loop?.frame ?? -1;
    this.devPanelContainer.setVisible(true);
    this.updateDevPanelVisuals();
    Audio.sfx('confirm');
  }

  private closeDevPanel(): void {
    this.isDevPanelOpen = false;
    this.devPanelContainer.setVisible(false);
    Audio.sfx('cancel');
  }

  private updateDevPanelVisuals(): void {
    const pw = 920;
    const px = (GAME_W - pw) / 2;
    const py = 28;

    // Update Tab Headers Styling
    const tab1W = 270;
    const tab2W = 330;
    const tabH = 26;
    const tab1X = px + 24;
    const tab2X = px + 304;
    const tabY = py + 12;

    this.tabChaptersBg.clear();
    this.tabVillainsBg.clear();

    const isChap = this.activeDevTab === 'chapters';

    // Tab 1 (Chapters)
    this.tabChaptersBg.fillStyle(isChap ? PAL.steel : PAL.panel, 0.95);
    this.tabChaptersBg.fillRoundedRect(tab1X, tabY, tab1W, tabH, 4);
    this.tabChaptersBg.lineStyle(isChap ? 2 : 1, isChap ? PAL.yellow : PAL.steel, 0.9);
    this.tabChaptersBg.strokeRoundedRect(tab1X, tabY, tab1W, tabH, 4);

    // Tab 2 (Villains)
    this.tabVillainsBg.fillStyle(!isChap ? PAL.steel : PAL.panel, 0.95);
    this.tabVillainsBg.fillRoundedRect(tab2X, tabY, tab2W, tabH, 4);
    this.tabVillainsBg.lineStyle(!isChap ? 2 : 1, !isChap ? PAL.yellow : PAL.steel, 0.9);
    this.tabVillainsBg.strokeRoundedRect(tab2X, tabY, tab2W, tabH, 4);

    const setTint = (txtObj: TextObj, col: number) => {
      if (txtObj instanceof Phaser.GameObjects.BitmapText) {
        txtObj.setTint(col);
      } else {
        (txtObj as any).setColor?.('#' + col.toString(16).padStart(6, '0'));
      }
    };

    setTint(this.tabChaptersText, isChap ? PAL.yellow : PAL.silver);
    setTint(this.tabVillainsText, !isChap ? PAL.yellow : PAL.silver);

    const activeHero = HEROES[ALL_HERO_IDS[this.selectedHeroIdx]];

    if (isChap) {
      // Redraw Hero Cards
      this.heroCardGraphics.clear();
      const heroCardW = 138;
      const heroCardH = 72;
      const heroStartX = px + 24;
      const heroCardsY = py + 42 + 18;

      ALL_HERO_IDS.forEach((_hid, idx) => {
        const cardX = heroStartX + idx * (heroCardW + 9);
        const isSelected = idx === this.selectedHeroIdx;

        this.heroCardGraphics.fillStyle(PAL.panel, 0.95);
        this.heroCardGraphics.fillRect(cardX, heroCardsY, heroCardW, heroCardH);

        if (isSelected) {
          this.heroCardGraphics.lineStyle(2, PAL.yellow, 1);
          this.heroCardGraphics.strokeRect(cardX, heroCardsY, heroCardW, heroCardH);
        } else {
          this.heroCardGraphics.lineStyle(1, PAL.steel, 0.6);
          this.heroCardGraphics.strokeRect(cardX, heroCardsY, heroCardW, heroCardH);
        }
      });

      // Update Leader Info text
      if (this.leaderInfoText) {
        (this.leaderInfoText as any).setText(
          `AKTYWNY LIDER: ${activeHero.fullName} (${activeHero.className}) • BONUS: ${activeHero.leaderBonus.label}`
        );
        setTint(this.leaderInfoText, activeHero.color);
      }

      // Redraw Chapter Cards
      this.chapterCardGraphics.clear();
      const colW = 428;
      const rowH = 46;
      const col1X = px + 24;
      const col2X = px + pw - colW - 24;
      const chapterSectionY = heroCardsY + heroCardH + 34;
      const rowStartY = chapterSectionY + 20;

      CHAPTER_DEV_REGISTRY.forEach((chDef, idx) => {
        const isCol2 = idx >= 5;
        const rowIdx = idx % 5;
        const cx = isCol2 ? col2X : col1X;
        const cy = rowStartY + rowIdx * (rowH + 6);
        const isSelected = idx === this.selectedChapterIdx;

        this.chapterCardGraphics.fillStyle(PAL.panel, 0.95);
        this.chapterCardGraphics.fillRect(cx, cy, colW, rowH);

        if (isSelected) {
          this.chapterCardGraphics.lineStyle(2, PAL.cyan, 1);
          this.chapterCardGraphics.strokeRect(cx, cy, colW, rowH);
        } else {
          this.chapterCardGraphics.lineStyle(1, PAL.steel, 0.5);
          this.chapterCardGraphics.strokeRect(cx, cy, colW, rowH);
        }

        const rowTexts = this.chapterTextRows[idx];
        if (rowTexts) {
          const prefix = isSelected ? '► ' : '  ';
          (rowTexts.title as any).setText(`${prefix}${chDef.title}: ${chDef.subtitle}`);
          (rowTexts.details as any).setText(
            `   Lokacja: ${chDef.location}  •  Tryb: [${chDef.targetScene}]  •  Poziom: Lv.${chDef.recommendedLevel}`
          );
          setTint(rowTexts.title, isSelected ? PAL.yellow : PAL.white);
        }
      });
    } else {
      // Villains View Visuals
      if (this.villainsSubtitleText) {
        (this.villainsSubtitleText as any).setText(
          `★ TESTUJ NOWY PIXEL ART WROGÓW W WALCE • AKTYWNY BOHATER DO TESTÓW: ${activeHero.fullName} (${activeHero.className})`
        );
      }

      this.villainsCardGraphics.clear();
      this.villainCardsList.forEach((c, idx) => {
        const isSelected = idx === this.selectedVillainIdx;
        this.villainsCardGraphics.fillStyle(PAL.panel, 0.95);
        this.villainsCardGraphics.fillRoundedRect(c.x, c.y, c.w, c.h, 4);

        if (isSelected) {
          this.villainsCardGraphics.lineStyle(2, PAL.yellow, 1);
          this.villainsCardGraphics.strokeRoundedRect(c.x, c.y, c.w, c.h, 4);
        } else {
          this.villainsCardGraphics.lineStyle(1, PAL.steel, 0.6);
          this.villainsCardGraphics.strokeRoundedRect(c.x, c.y, c.w, c.h, 4);
        }
      });
    }
  }

  private warpToSelectedChapter(): void {
    if (this.isTransitioning) return;
    this.isTransitioning = true;

    const heroId = ALL_HERO_IDS[this.selectedHeroIdx];
    const chDef = CHAPTER_DEV_REGISTRY[this.selectedChapterIdx];
    const { state, targetScene, battleEncounterId, startAtJanusz } = createDevChapterState(
      heroId,
      chDef.id
    );

    Audio.sfx('confirm');
    this.cameras.main.fadeOut(300, 0, 3, 11);
    this.cameras.main.once(Phaser.Cameras.Scene2D.Events.FADE_OUT_COMPLETE, () => {
      if (targetScene === 'World') {
        this.scene.start('World', { state, leader: heroId });
      } else if (targetScene === 'Campfire') {
        this.scene.start('Campfire', { state, startAtJanusz });
      } else if (targetScene === 'Battle') {
        startBattle(this, battleEncounterId ?? 'finalBossRift', { state });
      } else if (targetScene === 'Outro') {
        this.scene.start('Outro', { state });
      }
    });
  }

  private launchVillainBattle(eid: string): void {
    if (this.isTransitioning) return;
    this.isTransitioning = true;
    Audio.sfx('confirm');

    const heroId = ALL_HERO_IDS[this.selectedHeroIdx] ?? 'danny';
    const enemyDef = ENEMIES[eid];
    const isBoss = !!enemyDef?.boss;

    // Scale hero to enemy level for balanced test combat
    const enemyLevel = enemyDef?.level ?? 1;
    const scaledChapter = Math.min(10, Math.max(1, enemyLevel));
    const { state } = createDevChapterState(heroId, scaledChapter);

    const bgMap: Record<string, string> = {
      bolKregoslupa: 'battle_apartment_bg',
      slacki: 'battle_apartment_bg',
      sasiadSzkodnik: 'battle_garage_bg',
      autoTuneHipster: 'battle_pub_bg',
      drogiePiwo: 'battle_pub_bg',
      straznik: 'battle_alley_bg',
      kark: 'battle_alley_bg',
      panJanusz: 'battle_rift_bg',
      kredyt: 'battle_rift_bg',
      audyt: 'battle_rift_bg',
      rwaKulszowa: 'battle_rift_bg',
    };

    const bg = bgMap[eid] ?? 'battle_apartment_bg';
    const music = isBoss ? 'ch09_finalboss' : 'ch01_battle';

    this.cameras.main.fadeOut(300, 0, 3, 11);
    this.cameras.main.once(Phaser.Cameras.Scene2D.Events.FADE_OUT_COMPLETE, () => {
      startBattle(this, {
        state,
        heroes: [heroId],
        enemies: [eid],
        bg,
        music,
        battleTitle: `TEST DEV: ${enemyDef?.name ?? eid}`,
        returnScene: 'Title',
      });
    });
  }

  update(): void {
    // If audio splash gate is active, don't process main menu
    if (this.isAudioGateActive) return;
    if (this.game?.loop?.frame === this.gateDismissedFrame) return;

    // If Dev Panel is active, handle Dev Panel navigation
    if (this.isDevPanelOpen) {
      if (this.isTransitioning) return;
      if (this.game?.loop?.frame === this.devPanelToggledFrame) return;

      if (this.inputHandler.pressed('cancel')) {
        this.closeDevPanel();
        return;
      }

      // TAB key toggles between tabs
      if (this.inputHandler.pressed('menu')) {
        this.switchDevTab(this.activeDevTab === 'chapters' ? 'villains' : 'chapters');
        return;
      }

      if (this.activeDevTab === 'chapters') {
        if (this.inputHandler.pressed('left')) {
          this.selectedHeroIdx =
            (this.selectedHeroIdx + ALL_HERO_IDS.length - 1) % ALL_HERO_IDS.length;
          Audio.sfx('cursor');
          this.updateDevPanelVisuals();
        } else if (this.inputHandler.pressed('right')) {
          this.selectedHeroIdx = (this.selectedHeroIdx + 1) % ALL_HERO_IDS.length;
          Audio.sfx('cursor');
          this.updateDevPanelVisuals();
        }

        if (this.inputHandler.pressed('up')) {
          this.selectedChapterIdx =
            (this.selectedChapterIdx + CHAPTER_DEV_REGISTRY.length - 1) %
            CHAPTER_DEV_REGISTRY.length;
          Audio.sfx('cursor');
          this.updateDevPanelVisuals();
        } else if (this.inputHandler.pressed('down')) {
          this.selectedChapterIdx = (this.selectedChapterIdx + 1) % CHAPTER_DEV_REGISTRY.length;
          Audio.sfx('cursor');
          this.updateDevPanelVisuals();
        }

        if (this.inputHandler.pressed('ok')) {
          this.warpToSelectedChapter();
        }
      } else {
        // Villains tab navigation
        const totalVillains = this.villainCardsList.length;
        if (this.inputHandler.pressed('left')) {
          this.selectedVillainIdx = (this.selectedVillainIdx + totalVillains - 1) % totalVillains;
          Audio.sfx('cursor');
          this.updateDevPanelVisuals();
        } else if (this.inputHandler.pressed('right')) {
          this.selectedVillainIdx = (this.selectedVillainIdx + 1) % totalVillains;
          Audio.sfx('cursor');
          this.updateDevPanelVisuals();
        }

        if (this.inputHandler.pressed('up')) {
          this.selectedVillainIdx = (this.selectedVillainIdx + totalVillains - 4) % totalVillains;
          Audio.sfx('cursor');
          this.updateDevPanelVisuals();
        } else if (this.inputHandler.pressed('down')) {
          this.selectedVillainIdx = (this.selectedVillainIdx + 4) % totalVillains;
          Audio.sfx('cursor');
          this.updateDevPanelVisuals();
        }

        if (this.inputHandler.pressed('ok')) {
          const card = this.villainCardsList[this.selectedVillainIdx];
          if (card) {
            this.launchVillainBattle(card.id);
          }
        }
      }
      return;
    }

    // Normal Title Menu Update
    const pick = this.menu.update(this.inputHandler);
    if (pick === 0) {
      // NOWA GRA -> Analyzer
      this.cameras.main.fadeOut(300, 0, 3, 11);
      this.cameras.main.once(Phaser.Cameras.Scene2D.Events.FADE_OUT_COMPLETE, () => {
        this.scene.start('Analyzer');
      });
    } else if (pick === 1) {
      // KONTYNUUJ (Load slot 0)
      const save = Saves.load(0);
      if (save) {
        this.cameras.main.fadeOut(300, 0, 3, 11);
        this.cameras.main.once(Phaser.Cameras.Scene2D.Events.FADE_OUT_COMPLETE, () => {
          this.scene.start('World', { loadSave: save });
        });
      }
    } else if (pick === 2) {
      // Toggle CRT
      const newState = !isCrtEnabled();
      setCrtEnabled(this, newState);
      const curSaveList = Saves.list();
      const curHasSave = curSaveList[0].exists;
      this.menu.setItems([
        { label: 'NOWA GRA' },
        {
          label: curHasSave ? `KONTYNUUJ (${curSaveList[0].leader})` : 'KONTYNUUJ',
          disabled: !curHasSave,
        },
        { label: `FILTR CRT: ${newState ? 'WŁĄCZONY' : 'WYŁĄCZONY'}` },
      ]);
    }
  }
}
