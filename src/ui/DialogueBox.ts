import Phaser from 'phaser';
import { GAME_W, GAME_H, PAL } from '@/config';
import { drawPanel } from './Panel';
import { txt, TextObj } from './Text';
import type { Input } from './Input';
import { Audio } from '@/audio/ChipAudio';

export interface BoxLine {
  name: string;            // speaker display name ('' for narration)
  text: string;
  portrait?: string;       // texture key (e.g. portrait_danny_64)
  color?: number;          // name tag color
  pitch?: number;          // blip pitch
}

const BOX_H = 110;
const PAD = 10;

/**
 * Bottom-screen dialogue window in the Analyzer panel style.
 * Usage: `await box.play(lines)`; `await box.choose(['A','B'])`. Must call `update(input)` each frame.
 */
export class DialogueBox {
  private root: Phaser.GameObjects.Container;
  private g: Phaser.GameObjects.Graphics;
  private portrait: Phaser.GameObjects.Image;
  private nameT: TextObj;
  private bodyT: TextObj;
  private arrow: Phaser.GameObjects.Triangle;
  private choiceTexts: TextObj[] = [];
  private queue: BoxLine[] = [];
  private full = '';
  private shown = 0;
  private acc = 0;
  private resolveLines: (() => void) | null = null;
  private resolveChoice: ((i: number) => void) | null = null;
  private choiceIdx = 0;
  private current: BoxLine | null = null;
  cps = 45; // characters per second

  constructor(private scene: Phaser.Scene, depth = 1000) {
    const y = GAME_H - BOX_H - 10;
    this.root = scene.add.container(0, 0).setDepth(depth).setScrollFactor(0);
    this.g = scene.add.graphics();
    this.portrait = scene.add.image(12 + PAD + 44, y + BOX_H / 2, '__DEFAULT').setVisible(false);
    this.nameT = txt(scene, 0, y + PAD, '', { color: PAL.yellow, big: true });
    this.bodyT = txt(scene, 0, y + PAD + 18, '', { color: PAL.white, maxWidth: GAME_W - 200 });
    this.arrow = scene.add.triangle(GAME_W - 28, y + BOX_H - 16, 0, 0, 8, 0, 4, 6, PAL.cyan).setOrigin(0, 0);
    this.root.add([this.g, this.portrait, this.nameT, this.bodyT, this.arrow]);
    this.root.setVisible(false);
    scene.tweens.add({ targets: this.arrow, y: '+=3', yoyo: true, repeat: -1, duration: 300 });
  }

  get active(): boolean {
    return this.root.visible;
  }

  play(lines: BoxLine[]): Promise<void> {
    this.queue = [...lines];
    this.root.setVisible(true);
    this.nextLine();
    return new Promise((res) => (this.resolveLines = res));
  }

  /** Shows the choice list in the box (optionally under a prompt line). */
  choose(options: string[], prompt?: BoxLine): Promise<number> {
    this.root.setVisible(true);
    this.layout(prompt ?? { name: '', text: '' });
    this.full = prompt?.text ?? '';
    this.shown = this.full.length;
    this.setBody(this.full);
    this.arrow.setVisible(false);
    const y0 = GAME_H - BOX_H - 10 + PAD + (prompt?.text ? 36 : 14);
    const x0 = this.textX();
    this.choiceTexts.forEach((t) => t.destroy());
    this.choiceTexts = options.map((o, i) => {
      const t = txt(this.scene, x0 + 10, y0 + i * 16, `[${i + 1}] ${o}`, { color: PAL.cyan, big: true });
      this.root.add(t);
      return t;
    });
    this.choiceIdx = 0;
    this.refreshChoices();
    return new Promise((res) => (this.resolveChoice = res));
  }

  update(input: Input, dt: number): void {
    if (!this.root.visible) return;
    if (this.resolveChoice) {
      if (input.pressed('up')) { this.choiceIdx = (this.choiceIdx + this.choiceTexts.length - 1) % this.choiceTexts.length; Audio.sfx('cursor'); this.refreshChoices(); }
      if (input.pressed('down')) { this.choiceIdx = (this.choiceIdx + 1) % this.choiceTexts.length; Audio.sfx('cursor'); this.refreshChoices(); }
      const nums: ('n1' | 'n2' | 'n3')[] = ['n1', 'n2', 'n3'];
      let pick = -1;
      nums.forEach((n, i) => { if (i < this.choiceTexts.length && input.pressed(n)) pick = i; });
      if (input.pressed('ok')) pick = this.choiceIdx;
      if (pick >= 0) {
        Audio.sfx('confirm');
        const r = this.resolveChoice;
        this.resolveChoice = null;
        this.choiceTexts.forEach((t) => t.destroy());
        this.choiceTexts = [];
        this.hide();
        r(pick);
      }
      return;
    }
    if (this.shown < this.full.length) {
      this.acc += dt / 1000 * this.cps;
      const before = this.shown;
      this.shown = Math.min(this.full.length, this.shown + Math.floor(this.acc));
      this.acc -= Math.floor(this.acc);
      if (this.shown !== before) {
        this.setBody(this.full.slice(0, this.shown));
        if (this.full[this.shown - 1] !== ' ' && this.shown % 2 === 0) Audio.sfx('blip', { pitch: this.current?.pitch ?? 1 });
      }
      this.arrow.setVisible(false);
      if (input.okOrTap()) { this.shown = this.full.length; this.setBody(this.full); }
    } else {
      this.arrow.setVisible(true);
      if (input.okOrTap()) { Audio.sfx('cursor'); this.nextLine(); }
    }
  }

  hide(): void {
    this.root.setVisible(false);
  }

  private nextLine(): void {
    const l = this.queue.shift();
    if (!l) {
      this.hide();
      const r = this.resolveLines;
      this.resolveLines = null;
      r?.();
      return;
    }
    this.current = l;
    this.layout(l);
    this.full = l.text;
    this.shown = 0;
    this.acc = 0;
    this.setBody('');
  }

  private textX(): number {
    return this.portrait.visible ? 12 + PAD + 88 + 14 : 12 + PAD + 8;
  }

  private layout(l: BoxLine): void {
    const y = GAME_H - BOX_H - 10;
    this.g.clear();
    drawPanel(this.g, 12, y, GAME_W - 24, BOX_H);
    const hasP = !!l.portrait && this.scene.textures.exists(l.portrait);
    this.portrait.setVisible(hasP);
    if (hasP) {
      this.portrait.setTexture(l.portrait!).setDisplaySize(88, 88);
      drawPanel(this.g, 12 + PAD, y + Math.round((BOX_H - 90) / 2), 90, 90, { fill: PAL.panel, border: PAL.cyan, glow: false });
      this.root.bringToTop(this.portrait);
    }
    const x = this.textX();
    this.nameT.setPosition(x, y + PAD);
    (this.nameT as any).setText(l.name ? l.name.toUpperCase() + ':' : '');
    if ('setTint' in this.nameT && this.nameT instanceof Phaser.GameObjects.BitmapText) this.nameT.setTint(l.color ?? PAL.yellow);
    this.bodyT.setPosition(x, y + PAD + (l.name ? 20 : 6));
    const mw = GAME_W - 24 - (x - 12) - PAD - 20;
    if (this.bodyT instanceof Phaser.GameObjects.BitmapText) this.bodyT.setMaxWidth(mw);
    else this.bodyT.setWordWrapWidth(mw, true);
  }

  private setBody(s: string): void {
    (this.bodyT as any).setText(s);
  }

  private refreshChoices(): void {
    this.choiceTexts.forEach((t, i) => {
      const sel = i === this.choiceIdx;
      if (t instanceof Phaser.GameObjects.BitmapText) t.setTint(sel ? PAL.yellow : PAL.cyan);
      else t.setColor(sel ? '#e8d84a' : '#9ecbd4');
      const raw = (t as any).text as string;
      const clean = raw.replace(/^▶ /, '');
      (t as any).setText(sel ? '▶ ' + clean : clean);
    });
  }
}
