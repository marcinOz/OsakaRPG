import Phaser from 'phaser';
import { GAME_W, GAME_H, PAL } from '@/config';
import { HEROES } from '@/content/heroes';
import { HeroId } from '@/types';
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

    // 1. Pixel-Perfect 1024x576 Analyzer Background directly from authentic reference
    this.add.image(0, 0, 'analyzer_bg').setOrigin(0, 0).setDisplaySize(GAME_W, GAME_H);

    // 2. Exact Card Layouts matching reference.jpg (3 cols x 2 rows)
    this.cardLayouts = [
      { id: 'danny', x: 37, y: 173, w: 307, h: 182 },
      { id: 'alior', x: 364, y: 173, w: 307, h: 182 },
      { id: 'lisu',  x: 691, y: 173, w: 307, h: 182 },
      { id: 'barti', x: 37, y: 363, w: 307, h: 182 },
      { id: 'oziem', x: 364, y: 363, w: 307, h: 182 },
      { id: 'luki',  x: 691, y: 363, w: 307, h: 182 },
    ];

    // Interactive pointer hitboxes on cards
    this.cardLayouts.forEach((card, idx) => {
      const zone = this.add.zone(card.x, card.y, card.w, card.h).setOrigin(0, 0).setInteractive({ useHandCursor: true });
      zone.on('pointerdown', () => {
        if (this.isConfirming || this.dialogueBox.active) return;
        if (this.selectedIdx === idx) {
          this.confirmLeader();
        } else {
          this.selectedIdx = idx;
          Audio.sfx('cursor');
          this.updateSelectionVisuals();
        }
      });
      zone.on('pointerover', () => {
        if (this.isConfirming || this.dialogueBox.active) return;
        if (this.selectedIdx !== idx) {
          this.selectedIdx = idx;
          Audio.sfx('cursor');
          this.updateSelectionVisuals();
        }
      });
    });

    // 3. Selection Frame, Notches, and Portrait Scanline
    this.selectorGraphics = this.add.graphics().setDepth(200);
    this.scanLine = this.add.graphics().setDepth(250);

    // 4. Animated Progress Bar on Łuki's card
    this.progressBar = this.add.graphics().setDepth(150);

    // 5. Dialogue Box for character leader confirmation
    this.dialogueBox = new DialogueBox(this, 1000);

    this.inputHandler = new Input(this);
    this.updateSelectionVisuals();
  }

  private renderProgressBar(x: number, y: number, w: number, h: number): void {
    this.progressBar.clear();
    // Inner bar fill
    this.progressBar.fillStyle(0x0c2134, 1);
    this.progressBar.fillRect(x, y, w, h);
    // Animated cyan fill
    this.progressBar.fillStyle(PAL.cyan, 1);
    this.progressBar.fillRect(x + 1, y + 1, Math.round((w - 2) * this.progressVal), h - 2);
    // Highlight top reflection
    this.progressBar.fillStyle(PAL.cyanHi, 0.7);
    this.progressBar.fillRect(x + 1, y + 1, Math.round((w - 2) * this.progressVal), 2);
  }

  private updateSelectionVisuals(): void {
    this.selectorGraphics.clear();
    this.scanLine.clear();

    const card = this.cardLayouts[this.selectedIdx];
    if (!card) return;

    // Outer cyan glow & border
    this.selectorGraphics.lineStyle(2, PAL.cyanHi, 0.95);
    this.selectorGraphics.strokeRect(card.x - 1, card.y - 1, card.w + 2, card.h + 2);

    // Subtle soft outer glow
    this.selectorGraphics.lineStyle(1, PAL.cyan, 0.35);
    this.selectorGraphics.strokeRect(card.x - 3, card.y - 3, card.w + 6, card.h + 6);

    // Yellow corner notches
    this.selectorGraphics.fillStyle(PAL.yellow, 1);
    const notch = 5;
    this.selectorGraphics.fillRect(card.x - 2, card.y - 2, notch, notch);
    this.selectorGraphics.fillRect(card.x + card.w - 3, card.y - 2, notch, notch);
    this.selectorGraphics.fillRect(card.x - 2, card.y + card.h - 3, notch, notch);
    this.selectorGraphics.fillRect(card.x + card.w - 3, card.y + card.h - 3, notch, notch);

    // Scan line animation over portrait area (approx 98x116 from card top-left)
    const px = card.x + 8;
    const py = card.y + 8;
    const pw = 98;
    const ph = 116;

    this.scanLine.fillStyle(PAL.cyanHi, 0.65);
    this.scanLine.fillRect(px, py, pw, 2);
    this.tweens.killTweensOf(this.scanLine);
    this.scanLine.y = 0;
    this.tweens.add({
      targets: this.scanLine,
      y: ph - 4,
      yoyo: true,
      repeat: -1,
      duration: 1000,
      ease: 'Linear',
    });
  }

  override update(time: number, delta: number): void {
    // Animate progress bar slightly on Łuki's card (x=700, y=518, w=290, h=14)
    this.progressVal = 0.65 + Math.sin(time / 800) * 0.12;
    this.renderProgressBar(700, 518, 290, 14);

    if (this.dialogueBox.active) {
      this.dialogueBox.update(this.inputHandler, delta);
      return;
    }

    if (this.isConfirming) return;

    // Grid Navigation (3 cols x 2 rows)
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
        portrait: `portrait_${heroId}_96`,
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
