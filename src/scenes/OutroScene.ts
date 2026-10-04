import Phaser from 'phaser';
import { GAME_W, GAME_H, PAL } from '@/config';
import { txt } from '@/ui/Text';
import { drawPanel } from '@/ui/Panel';
import { DialogueBox } from '@/ui/DialogueBox';
import { Input } from '@/ui/Input';
import { Audio } from '@/audio/ChipAudio';
import { applyCrtToCamera } from '@/fx/CrtPipeline';
import { flash } from '@/fx/Juice';
import { CH10 } from '@/content/chapters/ch10';
import { DialogueRunner } from '@/systems/Dialogue';
import type { GameData } from '@/systems/GameState';

export class OutroScene extends Phaser.Scene {
  private inputHandler!: Input;
  private dialogueBox!: DialogueBox;
  private state!: GameData;
  private photoShown = false;
  private isEnding = false;

  constructor() {
    super('Outro');
  }

  init(data: { state: GameData }): void {
    this.state = data.state;
  }

  create(): void {
    applyCrtToCamera(this);
    Audio.playSong('ch10_sunrise', { fadeMs: 800 });

    // Sunrise Background
    this.add.image(GAME_W / 2, GAME_H / 2, 'sunrise_bg').setDisplaySize(GAME_W, GAME_H);

    // 6 friends seated on the pier watching sunrise
    this.setupSeatedFriends();

    this.dialogueBox = new DialogueBox(this, 1000);
    this.inputHandler = new Input(this);

    // Start outro dialogue
    this.time.delayedCall(600, () => this.playOutroSequence());
  }

  private setupSeatedFriends(): void {
    const heroes = ['danny', 'alior', 'lisu', 'barti', 'oziem', 'luki'];
    const startX = GAME_W / 2 - 250;
    heroes.forEach((hid, i) => {
      const x = startX + i * 100;
      const y = 480;
      // Ground shadow on pier
      this.add.ellipse(x, y + 12, 28, 10, 0x000000, 0.45).setDepth(90);
      const spr = this.add.sprite(x, y, `${hid}_sit`, 0).setDepth(100);
      spr.play(`anim_${hid}_sit`);
    });
  }

  private async playOutroSequence(): Promise<void> {
    const runner = new DialogueRunner(CH10.outro, this.state.leader, this.state.party);
    await this.dialogueBox.play(runner.allResolved());

    // Flash & Camera Snapshot
    Audio.sfx('confirm');
    flash(this, 0xffffff, 600);

    this.time.delayedCall(400, () => {
      this.showCommemorativePhoto();
    });
  }

  private showCommemorativePhoto(): void {
    this.photoShown = true;

    // Full-screen Commemorative Photograph
    this.add.image(GAME_W / 2, GAME_H / 2, 'memorial_photo')
      .setDisplaySize(GAME_W, GAME_H)
      .setDepth(205);

    // Retro Polaroid & Golden frame border
    const frameG = this.add.graphics().setDepth(210);
    frameG.lineStyle(2, PAL.yellow, 0.85);
    frameG.strokeRect(8, 8, GAME_W - 16, GAME_H - 16);
    frameG.lineStyle(1, PAL.cyan, 0.5);
    frameG.strokeRect(12, 12, GAME_W - 24, GAME_H - 24);

    // Header panel (top sky band)
    const topG = this.add.graphics().setDepth(210);
    drawPanel(topG, 32, 16, GAME_W - 64, 52, { fill: PAL.navy, border: PAL.yellow, glow: true, alpha: 0.85 });

    txt(this, GAME_W / 2, 32, '★ FRIEND PACK ANALYZER v1.0 – PAMIĄTKOWE ZDJĘCIE ★', {
      color: PAL.yellow,
      origin: [0.5, 0.5],
    }).setDepth(220);

    txt(this, GAME_W / 2, 52, 'LEGENDA LEŚNEGO OGNISKA • 2026 REUNION • WILCZY LAS', {
      color: PAL.cyanHi,
      origin: [0.5, 0.5],
    }).setDepth(220);

    // Stats & summary box (bottom shoreline band)
    const bottomG = this.add.graphics().setDepth(210);
    drawPanel(bottomG, 32, 486, GAME_W - 64, 72, { fill: PAL.navy, border: PAL.steel, glow: true, alpha: 0.88 });

    txt(this, GAME_W / 2, 502, `LIDER: ${this.state.leader.toUpperCase()}   |   ROSTER: 6/6 ZWERBOWANYCH   |   KLIMAT: 100%   |   WSPOMNIENIA: ZAPISANE`, {
      color: PAL.green,
      origin: [0.5, 0.5],
    }).setDepth(220);

    txt(this, GAME_W / 2, 522, 'POKONANE WYZWANIA: BÓL KRĘGOSŁUPA, SLACKI, SĄSIAD SZKODNIK, HIPSTERZY, KARK, PAN JANUSZ', {
      color: PAL.cyanHi,
      origin: [0.5, 0.5],
    }).setDepth(220);

    txt(this, GAME_W / 2, 542, '[ NACIŚNIJ SPACJA / ENTER / Z LUB KLIKNIJ – POWRÓT DO MENU GŁÓWNEGO ]', {
      color: PAL.fireHi,
      origin: [0.5, 0.5],
    }).setDepth(220);

    // Click/tap support for touch & mouse players
    this.input.once('pointerdown', () => {
      this.finishOutro();
    });
  }

  private finishOutro(): void {
    if (this.isEnding) return;
    this.isEnding = true;
    Audio.sfx('confirm');
    this.cameras.main.fadeOut(800, 0, 3, 11);
    this.cameras.main.once(Phaser.Cameras.Scene2D.Events.FADE_OUT_COMPLETE, () => {
      this.scene.start('Title');
    });
  }

  override update(_time: number, delta: number): void {
    if (this.dialogueBox.active) {
      this.dialogueBox.update(this.inputHandler, delta);
      return;
    }

    if (this.photoShown && (this.inputHandler.pressed('ok') || this.inputHandler.pressed('cancel'))) {
      this.finishOutro();
    }
  }
}
