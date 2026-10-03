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
    const startX = GAME_W / 2 - 200;
    heroes.forEach((hid, i) => {
      const x = startX + i * 80;
      const y = 485;
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

    // Dim overlay
    const overlay = this.add.graphics().setDepth(200);
    overlay.fillStyle(0x00030b, 0.88);
    overlay.fillRect(0, 0, GAME_W, GAME_H);

    // Photo frame container
    const pg = this.add.graphics().setDepth(210);
    drawPanel(pg, 80, 40, GAME_W - 160, GAME_H - 80, { fill: PAL.navy, border: PAL.yellow });

    txt(this, GAME_W / 2, 60, '★ FRIEND PACK ANALYZER v1.0 ★', { color: PAL.yellow, big: true, origin: [0.5, 0.5] });
    txt(this, GAME_W / 2, 85, 'KRONIKA PRZYJAŹNI – LEGENDA LEŚNEGO OGNISKA', { color: PAL.cyanHi, origin: [0.5, 0.5] });

    // 6 Hero Portraits row in the commemorative frame (using native uncompressed 96x96)
    const heroes = ['danny', 'alior', 'lisu', 'barti', 'oziem', 'luki'];
    const startPx = GAME_W / 2 - 350;
    heroes.forEach((hid, i) => {
      const px = startPx + i * 140;
      const py = 190;
      this.add.image(px, py, `portrait_${hid}_96`).setDisplaySize(88, 88).setDepth(220);
      txt(this, px, py + 56, hid.toUpperCase(), { color: PAL.white, origin: [0.5, 0.5] });
    });

    // Stats summary
    txt(this, GAME_W / 2, 330, `LIDER: ${this.state.leader.toUpperCase()}    CZAS: 2026 REUNION    STATUS: WOLNA EKIPA`, { color: PAL.green, origin: [0.5, 0.5] });
    txt(this, GAME_W / 2, 360, 'POKONANE WYZWANIA: BÓL PLECÓW, SLACKI, SĄSIAD, HIPSTERZY, KARK, PAN JANUSZ', { color: PAL.cyan, origin: [0.5, 0.5] });
    txt(this, GAME_W / 2, 390, 'DOROSŁOŚĆ: POKONANA    KLIMAT: 100%    FPS: 60 (BEZ LAGÓW)', { color: PAL.yellow, origin: [0.5, 0.5] });

    txt(this, GAME_W / 2, 450, '[ NACIŚNIJ SPACJA / Z ]', { color: PAL.fireHi, origin: [0.5, 0.5] });
  }

  override update(_time: number, delta: number): void {
    if (this.dialogueBox.active) {
      this.dialogueBox.update(this.inputHandler, delta);
      return;
    }

    if (this.photoShown && (this.inputHandler.pressed('ok') || this.inputHandler.pressed('cancel'))) {
      Audio.sfx('confirm');
      this.cameras.main.fadeOut(800, 0, 3, 11);
      this.cameras.main.once(Phaser.Cameras.Scene2D.Events.FADE_OUT_COMPLETE, () => {
        this.scene.start('Title');
      });
    }
  }
}
