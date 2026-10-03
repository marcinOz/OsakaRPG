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

    // Dim overlay
    const overlay = this.add.graphics().setDepth(200);
    overlay.fillStyle(0x00030b, 0.88);
    overlay.fillRect(0, 0, GAME_W, GAME_H);

    // Photo frame container (Polaroid style)
    const pg = this.add.graphics().setDepth(210);
    drawPanel(pg, 48, 28, GAME_W - 96, GAME_H - 56, { fill: PAL.navy, border: PAL.yellow, glow: true });

    txt(this, GAME_W / 2, 52, '★ FRIEND PACK ANALYZER v1.0 – PAMIĄTKOWE ZDJĘCIE ★', {
      color: PAL.yellow,
      origin: [0.5, 0.5],
    });
    txt(this, GAME_W / 2, 74, 'LEGENDA LEŚNEGO OGNISKA • 2026 REUNION • WILCZY LAS', {
      color: PAL.cyanHi,
      origin: [0.5, 0.5],
    });

    // 6 Hero Portraits in individual framed cards (using high-res 96x96 portraits)
    const heroInfo: Record<string, { name: string; tag: string }> = {
      danny: { name: 'DANNY', tag: 'SIŁACZ' },
      alior: { name: 'ALIOR', tag: 'MAG TECH' },
      lisu: { name: 'LISU', tag: 'SZPIEG' },
      barti: { name: 'BARTI', tag: 'BARD' },
      oziem: { name: 'OZIEM', tag: 'PALADYN' },
      luki: { name: 'ŁUKI', tag: 'RATOWNIK' },
    };

    const heroes = ['danny', 'alior', 'lisu', 'barti', 'oziem', 'luki'];
    const startPx = GAME_W / 2 - 350;
    heroes.forEach((hid, i) => {
      const px = startPx + i * 140;
      const py = 180;

      // Card frame
      const frameG = this.add.graphics().setDepth(215);
      frameG.fillStyle(PAL.panel, 1);
      frameG.lineStyle(2, PAL.steel, 1);
      frameG.fillRoundedRect(px - 52, py - 52, 104, 134, 4);
      frameG.strokeRoundedRect(px - 52, py - 52, 104, 134, 4);

      this.add.image(px, py, `portrait_${hid}_96`).setDisplaySize(92, 92).setDepth(220);
      txt(this, px, py + 56, heroInfo[hid].name, { color: PAL.yellow, origin: [0.5, 0.5] });
      txt(this, px, py + 70, heroInfo[hid].tag, { color: PAL.cyan, origin: [0.5, 0.5] });
    });

    // Stats summary box
    const sg = this.add.graphics().setDepth(215);
    drawPanel(sg, 80, 320, GAME_W - 160, 110, { fill: PAL.panel, border: PAL.steel });

    txt(this, GAME_W / 2, 342, `LIDER: ${this.state.leader.toUpperCase()}   |   ROSTER: 6/6 ZWERBOWANYCH   |   KLIMAT: 100%   |   WSPOMNIENIA: ZAPISANE`, {
      color: PAL.green,
      origin: [0.5, 0.5],
    });
    txt(this, GAME_W / 2, 370, 'POKONANE WYZWANIA: BÓL KRĘGOSŁUPA, SLACKI, SĄSIAD SZKODNIK, HIPSTERZY, KARK, PAN JANUSZ', {
      color: PAL.cyanHi,
      origin: [0.5, 0.5],
    });
    txt(this, GAME_W / 2, 398, 'STATUS DOROSŁOŚCI: PRZEŁAMANA   |   PRZYJAŹŃ: LEGENDARNA   |   FPS: 60 (BEZ LAGÓW)', {
      color: PAL.yellow,
      origin: [0.5, 0.5],
    });

    txt(this, GAME_W / 2, 470, '[ NACIŚNIJ SPACJA / ENTER / Z – POWRÓT DO MENU GŁÓWNEGO ]', {
      color: PAL.fireHi,
      origin: [0.5, 0.5],
    });
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
