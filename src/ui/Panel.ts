import Phaser from 'phaser';
import { PAL } from '@/config';

export interface PanelOpts {
  fill?: number;
  border?: number;
  glow?: boolean;
  alpha?: number;
  radius?: number;
}

/**
 * Reference-style panel: deep navy fill, 1px cyan rim, soft outer glow, 2px rounded corners.
 * Drawn pixel-exact with Graphics (no anti-aliasing at pixelArt scale).
 */
export function drawPanel(g: Phaser.GameObjects.Graphics, x: number, y: number, w: number, h: number, o: PanelOpts = {}): void {
  const fill = o.fill ?? PAL.navy;
  const border = o.border ?? PAL.cyan;
  const a = o.alpha ?? 0.94;
  x = Math.round(x); y = Math.round(y); w = Math.round(w); h = Math.round(h);
  if (o.glow !== false) {
    g.fillStyle(border, 0.12);
    g.fillRect(x - 2, y + 1, w + 4, h - 2);
    g.fillRect(x + 1, y - 2, w - 2, h + 4);
    g.fillStyle(border, 0.2);
    g.fillRect(x - 1, y, w + 2, h);
    g.fillRect(x, y - 1, w, h + 2);
  }
  // body
  g.fillStyle(fill, a);
  g.fillRect(x + 1, y + 1, w - 2, h - 2);
  // inner subtle gradient top highlight
  g.fillStyle(PAL.panelHi, 0.5 * a);
  g.fillRect(x + 2, y + 2, w - 4, 1);
  // rim with cut corners
  g.fillStyle(border, 1);
  g.fillRect(x + 2, y, w - 4, 1);
  g.fillRect(x + 2, y + h - 1, w - 4, 1);
  g.fillRect(x, y + 2, 1, h - 4);
  g.fillRect(x + w - 1, y + 2, 1, h - 4);
  g.fillRect(x + 1, y + 1, 1, 1);
  g.fillRect(x + w - 2, y + 1, 1, 1);
  g.fillRect(x + 1, y + h - 2, 1, 1);
  g.fillRect(x + w - 2, y + h - 2, 1, 1);
}

export function panel(scene: Phaser.Scene, x: number, y: number, w: number, h: number, o: PanelOpts = {}): Phaser.GameObjects.Graphics {
  const g = scene.add.graphics();
  drawPanel(g, x, y, w, h, o);
  return g;
}

/** Small "chip" label box like "HABIT PATTERN ANALYSIS" in the reference. */
export function chip(g: Phaser.GameObjects.Graphics, x: number, y: number, w: number, h: number): void {
  drawPanel(g, x, y, w, h, { fill: PAL.panel, border: PAL.steel, glow: false });
  g.fillStyle(PAL.cyan, 0.6);
  g.fillRect(x + 2, y, w - 4, 1);
}

/** Simple horizontal gauge (HP/MP/ATB). */
export function gauge(g: Phaser.GameObjects.Graphics, x: number, y: number, w: number, h: number, pct: number, color: number, back = PAL.ink): void {
  pct = Phaser.Math.Clamp(pct, 0, 1);
  g.fillStyle(PAL.void, 1);
  g.fillRect(x - 1, y - 1, w + 2, h + 2);
  g.fillStyle(back, 1);
  g.fillRect(x, y, w, h);
  const fw = Math.round(w * pct);
  if (fw > 0) {
    g.fillStyle(color, 1);
    g.fillRect(x, y, fw, h);
    g.fillStyle(0xffffff, 0.25);
    g.fillRect(x, y, fw, 1);
  }
}
