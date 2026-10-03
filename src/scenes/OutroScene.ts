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
    const startX = GAME_W / 2 - 100;
    heroes.forEach((hid, i) => {
      const x = startX + i * 40;
      const y = 205;
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
    overlay.fillStyle(0x00030b, 0.85);
    overlay.fillRect(0, 0, GAME_W, GAME_H);

    // Photo frame container
    const pg = this.add.graphics().setDepth(210);
    drawPanel(pg, 40, 20, GAME_W - 80, GAME_H - 40, { fill: PAL.navy, border: PAL.yellow });

    txt(this, GAME_W / 2 - 120, 28, '★ FRIEND PACK ANALYZER v1.0 ★', { color: PAL.yellow, big: true });
    txt(this, GAME_W / 2 - 110, 48, 'KRONIKA PRZYJAŹNI – LEGENDA LEŚNEGO OGNISKA', { color: PAL.cyanHi });

    // 6 Hero Portraits row in the commemorative frame
    const heroes = ['danny', 'alior', 'lisu', 'barti', 'oziem', 'luki'];
    heroes.forEach((hid, i) => {
      const px = 72 + i * 56;
      const py = 95;
      this.add.image(px, py, `portrait_${hid}_64`).setDisplaySize(48, 48).setDepth(220);
      txt(this, px - 18, py + 28, hid.toUpperCase(), { color: PAL.white });
    });

    // Stats summary
    txt(this, 60, 150, `LIDER: ${this.state.leader.toUpperCase()}    CZAS: 2026 REUNION    STATUS: WOLNA EKIPA`, { color: PAL.green });
    txt(this, 60, 166, 'POKONANE WYZWANIA: BÓL PLECÓW, SLACKI, SĄSIAD, HIPSTERZY, KARK, PAN JANUSZ', { color: PAL.cyan });
    txt(this, 60, 182, 'DOROSŁOŚĆ: POKONANA    KLIMAT: 100%    FPS: 60 (BEZ LAGÓW)', { color: PAL.yellow });

    txt(this, GAME_W / 2 - 70, 215, '[ NACIŚNIJ SPACJA / Z ]', { color: PAL.fireHi });
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
