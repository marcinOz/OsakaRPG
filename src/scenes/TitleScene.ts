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

  // Dev Panel State & Objects
  private isDevPanelOpen = false;
  private devPanelContainer!: Phaser.GameObjects.Container;
  private selectedHeroIdx = 0;
  private selectedChapterIdx = 0;
  private heroCardGraphics!: Phaser.GameObjects.Graphics;
  private chapterCardGraphics!: Phaser.GameObjects.Graphics;
  private leaderInfoText!: TextObj;
  private chapterTextRows: { title: TextObj; details: TextObj }[] = [];
  private isTransitioning = false;

  constructor() {
    super('Title');
  }

  create(): void {
    applyCrtToCamera(this);
    Audio.unlock();
    Audio.playSong('title', { fadeMs: 600 });

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
    txt(this, 12, 4, 'THE PACK: RETRO ENGINE v2.0 [HD PIXEL-PERFECT EDITION]', {
      color: PAL.cyan,
      big: false,
    });
    // Window control buttons ▢ ▢ ✕
    txt(this, GAME_W - 48, 4, '― ▢ ✕', { color: PAL.silver });

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
      { label: 'PANEL DEWELOPERSKI (DEV)' },
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

    // 3. Header Bar
    const headerTitle = txt(
      this,
      GAME_W / 2,
      py + 16,
      '★ PANEL DEWELOPERSKI: WYBÓR ROZDZIAŁU & BOHATERA ★',
      {
        color: PAL.yellow,
        big: true,
        align: 'center',
        origin: [0.5, 0.5],
      }
    );
    this.devPanelContainer.add(headerTitle);

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

    // 4. Hero Selector Strip at Top
    const heroStripY = py + 38;
    const heroLabel = txt(this, px + 24, heroStripY, '1. WYBIERZ BOHATERA (LIDERA DRUŻYNY):', {
      color: PAL.silver,
      big: false,
    });
    this.devPanelContainer.add(heroLabel);

    this.heroCardGraphics = this.add.graphics();
    this.devPanelContainer.add(this.heroCardGraphics);

    const heroCardW = 138;
    const heroCardH = 72;
    const heroStartX = px + 24;
    const heroCardsY = heroStripY + 20;

    ALL_HERO_IDS.forEach((hid, idx) => {
      const cardX = heroStartX + idx * (heroCardW + 9);
      const def = HEROES[hid];

      // Portrait
      const portSpr = this.add
        .image(cardX + 38, heroCardsY + 36, `portrait_${hid}_64`)
        .setDisplaySize(56, 56)
        .setOrigin(0.5, 0.5);
      this.devPanelContainer.add(portSpr);

      // Hero name & class
      const nameTxt = txt(this, cardX + 72, heroCardsY + 18, def.name, {
        color: def.color,
        big: true,
      });
      const classTxt = txt(this, cardX + 72, heroCardsY + 40, def.className, {
        color: PAL.silver,
        big: false,
      });
      this.devPanelContainer.add([nameTxt, classTxt]);

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
      this.devPanelContainer.add(heroZone);
    });

    // Leader info subtitle
    this.leaderInfoText = txt(this, px + 24, heroCardsY + heroCardH + 8, '', {
      color: PAL.cyan,
      big: false,
    });
    this.devPanelContainer.add(this.leaderInfoText);

    // 5. Chapter Grid (2 Columns x 5 Rows)
    const chapterSectionY = heroCardsY + heroCardH + 34;
    const chapterLabel = txt(
      this,
      px + 24,
      chapterSectionY,
      '2. WYBIERZ ROZDZIAŁ DO TESTOWANIA (WARP):',
      {
        color: PAL.silver,
        big: false,
      }
    );
    this.devPanelContainer.add(chapterLabel);

    this.chapterCardGraphics = this.add.graphics();
    this.devPanelContainer.add(this.chapterCardGraphics);

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
      this.devPanelContainer.add([titleTxt, detailsTxt]);
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
      this.devPanelContainer.add(chZone);
    });

    // 6. Bottom Navigation Controls Hint
    const bottomHint = txt(
      this,
      px + 24,
      py + ph - 22,
      '[← / →]: ZMIEŃ BOHATERA   [↑ / ↓]: ZMIEŃ ROZDZIAŁ   [Z / ENTER / KLIK]: TESTUJ   [ESC / X]: POWRÓT',
      {
        color: PAL.grey,
        big: false,
      }
    );
    this.devPanelContainer.add(bottomHint);

    this.updateDevPanelVisuals();
  }

  private openDevPanel(): void {
    this.isDevPanelOpen = true;
    this.isTransitioning = false;
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

    // Redraw Hero Cards
    this.heroCardGraphics.clear();
    const heroCardW = 138;
    const heroCardH = 72;
    const heroStartX = px + 24;
    const heroCardsY = py + 38 + 20;

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
    const activeHero = HEROES[ALL_HERO_IDS[this.selectedHeroIdx]];
    if (this.leaderInfoText) {
      (this.leaderInfoText as any).setText(
        `AKTYWNY LIDER: ${activeHero.fullName} (${activeHero.className}) • BONUS: ${activeHero.leaderBonus.label}`
      );
      if (this.leaderInfoText instanceof Phaser.GameObjects.BitmapText) {
        this.leaderInfoText.setTint(activeHero.color);
      } else {
        this.leaderInfoText.setColor('#' + activeHero.color.toString(16).padStart(6, '0'));
      }
    }

    // Redraw Chapter Cards
    this.chapterCardGraphics.clear();
    const colW = 428;
    const rowH = 46;
    const col1X = px + 24;
    const col2X = px + pw - colW - 24;
    const rowStartY = heroCardsY + heroCardH + 34 + 20;

    CHAPTER_DEV_REGISTRY.forEach((chDef, idx) => {
      const isCol2 = idx >= 5;
      const rowIdx = idx % 5;
      const cx = isCol2 ? col2X : col1X;
      const cy = rowStartY + rowIdx * (rowH + 6);
      const isSelected = idx === this.selectedChapterIdx;

      this.chapterCardGraphics.fillStyle(isSelected ? PAL.navy : PAL.panel, 0.95);
      this.chapterCardGraphics.fillRect(cx, cy, colW, rowH);

      if (isSelected) {
        this.chapterCardGraphics.lineStyle(2, PAL.yellow, 1);
        this.chapterCardGraphics.strokeRect(cx, cy, colW, rowH);
      } else {
        this.chapterCardGraphics.lineStyle(1, PAL.steel, 0.7);
        this.chapterCardGraphics.strokeRect(cx, cy, colW, rowH);
      }

      const rowTexts = this.chapterTextRows[idx];
      if (rowTexts) {
        const prefix = isSelected ? '► ' : '  ';
        (rowTexts.title as any).setText(`${prefix}${chDef.title}: ${chDef.subtitle}`);
        (rowTexts.details as any).setText(
          `   Lokacja: ${chDef.location}  •  Tryb: [${chDef.targetScene}]  •  Poziom: Lv.${chDef.recommendedLevel}`
        );

        const titleColor = isSelected ? PAL.yellow : PAL.white;
        if (rowTexts.title instanceof Phaser.GameObjects.BitmapText) {
          rowTexts.title.setTint(titleColor);
        } else {
          rowTexts.title.setColor('#' + titleColor.toString(16).padStart(6, '0'));
        }
      }
    });
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

  update(): void {
    // If Dev Panel is active, handle Dev Panel navigation
    if (this.isDevPanelOpen) {
      if (this.isTransitioning) return;

      if (this.inputHandler.pressed('cancel')) {
        this.closeDevPanel();
        return;
      }

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
      // Open Dev Panel modal!
      this.openDevPanel();
    } else if (pick === 2) {
      // Load slot 0
      const save = Saves.load(0);
      if (save) {
        this.cameras.main.fadeOut(300, 0, 3, 11);
        this.cameras.main.once(Phaser.Cameras.Scene2D.Events.FADE_OUT_COMPLETE, () => {
          this.scene.start('World', { loadSave: save });
        });
      }
    } else if (pick === 3) {
      // Toggle CRT
      const newState = !isCrtEnabled();
      setCrtEnabled(this, newState);
      this.menu.setItems([
        { label: 'NOWA GRA' },
        { label: 'PANEL DEWELOPERSKI (DEV)' },
        {
          label: Saves.list()[0].exists ? `KONTYNUUJ` : 'KONTYNUUJ',
          disabled: !Saves.list()[0].exists,
        },
        { label: `FILTR CRT: ${newState ? 'WŁĄCZONY' : 'WYŁĄCZONY'}` },
      ]);
    }
  }
}
