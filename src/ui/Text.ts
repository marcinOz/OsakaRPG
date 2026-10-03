import Phaser from 'phaser';
import { PAL, hex } from '@/config';

export type TextObj = Phaser.GameObjects.BitmapText | Phaser.GameObjects.Text;

export interface TextOpts {
  color?: number;
  big?: boolean;
  maxWidth?: number;
  align?: 'left' | 'center' | 'right';
  origin?: [number, number];
}

/** Draws pixel text using bitmap font 'pixel' / 'pixel_big' if loaded, else a crisp canvas fallback. */
export function txt(scene: Phaser.Scene, x: number, y: number, s: string, o: TextOpts = {}): TextObj {
  const key = o.big ? 'pixel_big' : 'pixel';
  const color = o.color ?? PAL.white;
  let t: TextObj;
  if (scene.cache.bitmapFont.exists(key)) {
    const bt = scene.add.bitmapText(x, y, key, s);
    bt.setTint(color);
    if (o.maxWidth) bt.setMaxWidth(o.maxWidth);
    if (o.align === 'center') bt.align = 1;
    if (o.align === 'right') bt.align = 2;
    t = bt;
  } else {
    const tt = scene.add.text(x, y, s, {
      fontFamily: 'monospace',
      fontSize: o.big ? '14px' : '8px',
      color: hex(color),
      wordWrap: o.maxWidth ? { width: o.maxWidth, useAdvancedWrap: true } : undefined,
      align: o.align ?? 'left',
      resolution: 1,
    });
    t = tt;
  }
  if (o.origin) t.setOrigin(o.origin[0], o.origin[1]);
  return t;
}

export function setTxtColor(t: TextObj, color: number): void {
  if (t instanceof Phaser.GameObjects.BitmapText) t.setTint(color);
  else t.setColor(hex(color));
}
