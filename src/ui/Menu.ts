import Phaser from 'phaser';
import { PAL } from '@/config';
import { drawPanel } from './Panel';
import { txt, TextObj } from './Text';
import type { Input } from './Input';
import { Audio } from '@/audio/ChipAudio';

export interface MenuItem {
  label: string;
  disabled?: boolean;
  hint?: string;
}

/** Vertical cursor menu in a panel. `update()` returns selected index, -2 on cancel, -1 otherwise. */
export class Menu {
  readonly root: Phaser.GameObjects.Container;
  private g: Phaser.GameObjects.Graphics;
  private texts: TextObj[] = [];
  private cursor: Phaser.GameObjects.Triangle;
  idx = 0;
  rowH = 18;

  constructor(
    private scene: Phaser.Scene,
    public x: number,
    public y: number,
    public w: number,
    private items: MenuItem[],
    depth = 900,
    private onHover?: (item: MenuItem, index: number) => void
  ) {
    this.root = scene.add.container(0, 0).setDepth(depth).setScrollFactor(0);
    this.g = scene.add.graphics();
    this.cursor = scene.add.triangle(0, 0, 0, 0, 6, 4, 0, 8, PAL.yellow).setOrigin(0, 0);
    this.root.add([this.g, this.cursor]);
    this.setItems(items);
    scene.tweens.add({ targets: this.cursor, x: '+=2', yoyo: true, repeat: -1, duration: 250 });
  }

  get h(): number {
    return this.items.length * this.rowH + 12;
  }

  get selectedItem(): MenuItem | undefined {
    return this.items[this.idx];
  }

  setItems(items: MenuItem[]): void {
    this.items = items;
    this.texts.forEach((t) => t.destroy());
    this.g.clear();
    drawPanel(this.g, this.x, this.y, this.w, this.h);
    this.texts = items.map((it, i) => {
      const t = txt(this.scene, this.x + 16, this.y + 6 + i * this.rowH, it.label, { color: it.disabled ? PAL.grey : PAL.white, big: true });
      this.root.add(t);
      return t;
    });
    this.idx = Math.min(this.idx, Math.max(0, items.length - 1));
    this.place();
  }

  setVisible(v: boolean): this {
    this.root.setVisible(v);
    if (v) this.place();
    return this;
  }

  destroy(): void {
    this.root.destroy();
  }

  update(input: Input): number {
    if (!this.root.visible || !this.items.length) return -1;
    if (input.pressed('up')) { this.idx = (this.idx + this.items.length - 1) % this.items.length; Audio.sfx('cursor'); this.place(); }
    if (input.pressed('down')) { this.idx = (this.idx + 1) % this.items.length; Audio.sfx('cursor'); this.place(); }
    if (input.pressed('cancel')) { Audio.sfx('cancel'); return -2; }
    if (input.pressed('ok')) {
      if (this.items[this.idx].disabled) { Audio.sfx('miss'); return -1; }
      Audio.sfx('confirm');
      return this.idx;
    }
    const tap = input.tap();
    if (tap && tap.x >= this.x && tap.x <= this.x + this.w && tap.y >= this.y && tap.y <= this.y + this.h) {
      const clickedIdx = Math.floor((tap.y - (this.y + 6)) / this.rowH);
      if (clickedIdx >= 0 && clickedIdx < this.items.length) {
        if (clickedIdx === this.idx) {
          if (this.items[this.idx].disabled) { Audio.sfx('miss'); return -1; }
          Audio.sfx('confirm');
          return this.idx;
        } else {
          this.idx = clickedIdx;
          Audio.sfx('cursor');
          this.place();
        }
      }
    }
    return -1;
  }

  private place(): void {
    this.cursor.setPosition(this.x + 6, this.y + 7 + this.idx * this.rowH);
    this.texts.forEach((t, i) => {
      const it = this.items[i];
      const c = it.disabled ? PAL.grey : i === this.idx ? PAL.yellow : PAL.white;
      if (t instanceof Phaser.GameObjects.BitmapText) t.setTint(c);
      else t.setColor('#' + c.toString(16).padStart(6, '0'));
    });
    if (this.onHover && this.items[this.idx]) {
      this.onHover(this.items[this.idx], this.idx);
    }
  }
}
