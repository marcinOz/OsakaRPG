import Phaser from 'phaser';
import { GAME_W, PAL } from '@/config';
import { HEROES } from '@/content/heroes';
import { HERO_IDS, HeroId } from '@/types';
import { txt } from '@/ui/Text';
import { drawPanel, chip } from '@/ui/Panel';
import { Input } from '@/ui/Input';
import { Audio } from '@/audio/ChipAudio';
import { DialogueBox } from '@/ui/DialogueBox';
import { applyCrtToCamera } from '@/fx/CrtPipeline';

interface CardLayout {
  id: HeroId;
  x: number;
  y: number;
  w: number;
  h: number;
}

export class AnalyzerScene extends Phaser.Scene {
  private inputHandler!: Input;
  private dialogueBox!: DialogueBox;
  private selectedIdx = 0;
  private cardLayouts: CardLayout[] = [];
  private selectorGraphics!: Phaser.GameObjects.Graphics;
  private scanLine!: Phaser.GameObjects.Graphics;
  private isConfirming = false;
  private progressBar!: Phaser.GameObjects.Graphics;
  private progressVal = 0.65;

  constructor() {
    super('Analyzer');
  }

  create(): void {
    applyCrtToCamera(this);
    Audio.playSong('analyzer', { fadeMs: 400 });

    this.cameras.main.setBackgroundColor(PAL.void);

    // 1. Top Window Bar
    this.createHeader();

    // 2. Analytics Title & Top Right Thumbnails
    this.createTopSection();

    // 3. Tab Chips
    this.createTabChips();

    // 4. Hero Cards Grid (3 cols x 2 rows)
    this.createHeroCards();

    // 5. Selection and Scanline
    this.selectorGraphics = this.add.graphics().setDepth(200);
    this.scanLine = this.add.graphics().setDepth(250);

    // 6. Dialogue Box for leader quotes
    this.dialogueBox = new DialogueBox(this, 1000);

    this.inputHandler = new Input(this);
    this.updateSelectionVisuals();
  }

  private createHeader(): void {
    const g = this.add.graphics();
    g.fillStyle(PAL.panel, 1);
    g.fillRect(0, 0, GAME_W, 13);
    g.fillStyle(PAL.steel, 1);
    g.fillRect(0, 13, GAME_W, 1);

    txt(this, 6, 2, 'FRIEND PACK ANALYZER: RETRO GAME ENGINE v1.0', { color: PAL.cyan, big: false });
    txt(this, GAME_W - 32, 2, '― ▢ ✕', { color: PAL.silver });
  }

  private createTopSection(): void {
    // Left: ANALYZING GROUP PHOTOS: THE PACK
    const dot = this.add.circle(10, 22, 2, PAL.cyanHi);
    this.tweens.add({ targets: dot, alpha: 0.2, yoyo: true, repeat: -1, duration: 400 });

    txt(this, 16, 17, 'ANALYZING GROUP PHOTOS: THE PACK', { color: PAL.cyanHi, big: false });

    // Right: Thumbnails
    const thumbX = GAME_W - 130;
    const thumbY = 16;
    const thumbs = [
      { key: 'thumb_group', label: 'GROUP' },
      { key: 'thumb_travel', label: 'TRAVEL' },
      { key: 'thumb_funny', label: 'FUNNY' },
      { key: 'thumb_moments', label: 'MOMENTS' },
    ];

    thumbs.forEach((th, i) => {
      const tx = thumbX + i * 31;
      const ty = thumbY;

      // Thumbnail image
      if (this.textures.exists(th.key)) {
        this.add.image(tx + 12, ty + 12, th.key).setDisplaySize(24, 24);
      }
      // Frame
      const tg = this.add.graphics();
      tg.lineStyle(1, PAL.white, 0.8);
      tg.strokeRect(tx, ty, 25, 25);
      // Small green checkmark
      tg.fillStyle(PAL.green, 1);
      tg.fillRect(tx + 18, ty - 2, 7, 7);
      txt(this, tx + 19, ty - 3, '✓', { color: PAL.ink });

      // Label below
      txt(this, tx + 1, ty + 26, th.label, { color: PAL.silver });
    });
  }

  private createTabChips(): void {
    const g = this.add.graphics();
    const y = 49;
    chip(g, 10, y, 130, 10);
    txt(this, 14, y + 1, 'GOOGLE PHOTOS ANALYTICS REPORT', { color: PAL.cyan });

    chip(g, 144, y, 105, 10);
    txt(this, 148, y + 1, 'CHARACTER ATTRIBUTE EXTRACTION', { color: PAL.silver });

    chip(g, 253, y, 95, 10);
    txt(this, 257, y + 1, 'HABIT PATTERN ANALYSIS', { color: PAL.silver });

    chip(g, 352, y, 85, 10);
    txt(this, 356, y + 1, 'MEMORABILIA DETECTION', { color: PAL.silver });
  }

  private createHeroCards(): void {
    const cardW = 150;
    const cardH = 96;
    const startX = 6;
    const startY = 64;
    const spacingX = 158;
    const spacingY = 101;

    HERO_IDS.forEach((hid, i) => {
      const col = i % 3;
      const row = Math.floor(i / 3);
      const cx = startX + col * spacingX;
      const cy = startY + row * spacingY;
      const def = HEROES[hid];

      this.cardLayouts.push({ id: hid, x: cx, y: cy, w: cardW, h: cardH });

      // Card panel base
      const cg = this.add.graphics();
      drawPanel(cg, cx, cy, cardW, cardH, { fill: PAL.panel, border: PAL.steel, glow: false });

      // Portrait on the left (64x64)
      const pKey = `portrait_${hid}_64`;
      if (this.textures.exists(pKey)) {
        this.add.image(cx + 34, cy + 34, pKey).setDisplaySize(60, 60);
      }
      // Inner portrait border
      cg.lineStyle(1, PAL.cyan, 0.7);
      cg.strokeRect(cx + 4, cy + 4, 60, 60);

      // Name & Class
      const textX = cx + 67;
      txt(this, textX, cy + 4, `${def.fullName} (${def.name})`, { color: PAL.white });
      txt(this, textX, cy + 14, `CLASS: ${def.className}`, { color: PAL.cyan });
      txt(this, textX, cy + 24, `ABILITY: ${def.signature}`, { color: PAL.cyanHi });

      // Detected items header
      txt(this, textX, cy + 34, 'DETECTED ITEMS:', { color: PAL.silver });

      // 3 Item icons
      def.items.forEach((itemKey, itemIdx) => {
        const fullItemKey = `item_${itemKey}`;
        const ix = textX + itemIdx * 25 + 10;
        const iy = cy + 52;
        if (this.textures.exists(fullItemKey)) {
          this.add.image(ix, iy, fullItemKey).setDisplaySize(20, 20);
        }
      });

      // Bottom Status rows
      if (i === 5) {
        // Luki has the "ASSET LIBRARY CREATION IN PROGRESS" bar in the reference!
        txt(this, cx + 8, cy + 70, 'ASSET LIBRARY CREATION IN PROGRESS', { color: PAL.cyan, align: 'center' });
        this.progressBar = this.add.graphics();
        this.renderProgressBar(cx + 8, cy + 81, cardW - 16, 8);
      } else {
        txt(this, cx + 6, cy + 68, '▪ INSIDE JOKES: DETECTED', { color: PAL.silver });
        txt(this, cx + 96, cy + 68, '(LORE GENERATING)', { color: PAL.yellow });

        txt(this, cx + 6, cy + 80, '▪ RECURRING LOCATIONS: FOUND', { color: PAL.silver });
        txt(this, cx + 110, cy + 80, '(LEVEL BUILDING)', { color: PAL.cyan });
      }
    });
  }

  private renderProgressBar(x: number, y: number, w: number, h: number): void {
    this.progressBar.clear();
    this.progressBar.fillStyle(PAL.ink, 1);
    this.progressBar.fillRect(x, y, w, h);
    this.progressBar.fillStyle(PAL.cyan, 1);
    this.progressBar.fillRect(x + 1, y + 1, (w - 2) * this.progressVal, h - 2);
    this.progressBar.lineStyle(1, PAL.cyanHi, 1);
    this.progressBar.strokeRect(x, y, w, h);
  }

  private updateSelectionVisuals(): void {
    this.selectorGraphics.clear();
    this.scanLine.clear();

    const card = this.cardLayouts[this.selectedIdx];
    if (!card) return;

    // Glowing cyan frame on selected card
    this.selectorGraphics.lineStyle(2, PAL.cyanHi, 1);
    this.selectorGraphics.strokeRect(card.x - 1, card.y - 1, card.w + 2, card.h + 2);

    // Glowing corner notches
    this.selectorGraphics.fillStyle(PAL.yellow, 1);
    this.selectorGraphics.fillRect(card.x - 2, card.y - 2, 4, 4);
    this.selectorGraphics.fillRect(card.x + card.w - 2, card.y - 2, 4, 4);
    this.selectorGraphics.fillRect(card.x - 2, card.y + card.h - 2, 4, 4);
    this.selectorGraphics.fillRect(card.x + card.w - 2, card.y + card.h - 2, 4, 4);

    // Scan line animation over portrait
    this.scanLine.fillStyle(PAL.cyanHi, 0.7);
    this.scanLine.fillRect(card.x + 4, card.y + 4, 60, 2);
    this.tweens.killTweensOf(this.scanLine);
    this.scanLine.y = 0;
    this.tweens.add({
      targets: this.scanLine,
      y: 58,
      yoyo: true,
      repeat: -1,
      duration: 900,
      ease: 'Linear',
    });
  }

  override update(time: number, delta: number): void {
    // Animate progress bar slightly
    this.progressVal = 0.6 + Math.sin(time / 800) * 0.15;
    if (this.progressBar) {
      const lukiCard = this.cardLayouts[5];
      if (lukiCard) {
        this.renderProgressBar(lukiCard.x + 8, lukiCard.y + 81, lukiCard.w - 16, 8);
      }
    }

    if (this.dialogueBox.active) {
      this.dialogueBox.update(this.inputHandler, delta);
      return;
    }

    if (this.isConfirming) return;

    // Grid Navigation
    if (this.inputHandler.pressed('left')) {
      if (this.selectedIdx % 3 > 0) {
        this.selectedIdx -= 1;
        Audio.sfx('cursor');
        this.updateSelectionVisuals();
      }
    } else if (this.inputHandler.pressed('right')) {
      if (this.selectedIdx % 3 < 2) {
        this.selectedIdx += 1;
        Audio.sfx('cursor');
        this.updateSelectionVisuals();
      }
    } else if (this.inputHandler.pressed('up')) {
      if (this.selectedIdx >= 3) {
        this.selectedIdx -= 3;
        Audio.sfx('cursor');
        this.updateSelectionVisuals();
      }
    } else if (this.inputHandler.pressed('down')) {
      if (this.selectedIdx < 3) {
        this.selectedIdx += 3;
        Audio.sfx('cursor');
        this.updateSelectionVisuals();
      }
    } else if (this.inputHandler.pressed('ok')) {
      this.confirmLeader();
    }
  }

  private async confirmLeader(): Promise<void> {
    this.isConfirming = true;
    Audio.sfx('confirm');

    const heroId = this.cardLayouts[this.selectedIdx].id;
    const heroDef = HEROES[heroId];

    // Play character leader quote in dialogue box
    await this.dialogueBox.play([
      {
        name: heroDef.name,
        text: heroDef.leaderQuote,
        portrait: `portrait_${heroId}_64`,
        color: heroDef.color,
      },
      {
        name: 'SYSTEM',
        text: `Wybrano Lidera: ${heroDef.name}!\nBonus Pasywny: ${heroDef.leaderBonus.label}`,
        color: PAL.cyan,
      },
    ]);

    // Transition to Chapter 1 World Scene
    this.cameras.main.fadeOut(400, 0, 3, 11);
    this.cameras.main.once(Phaser.Cameras.Scene2D.Events.FADE_OUT_COMPLETE, () => {
      this.scene.start('World', { leader: heroId, chapter: 1 });
    });
  }
}
