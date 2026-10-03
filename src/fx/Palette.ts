import Phaser from 'phaser';
import { GAME_W, GAME_H, PAL } from '@/config';

export type TimeOfDay = 'morning' | 'day' | 'dusk' | 'night' | 'blueFire';

export function setTimeOfDay(scene: Phaser.Scene, tod: TimeOfDay): Phaser.GameObjects.Rectangle | null {
  const existing = scene.children.getByName('tod_overlay');
  if (existing) existing.destroy();

  let color: number = PAL.navy;
  let alpha = 0;

  switch (tod) {
    case 'morning':
      color = 0xffe8c0;
      alpha = 0.08;
      break;
    case 'day':
      alpha = 0;
      break;
    case 'dusk':
      color = 0xff6b4a;
      alpha = 0.15;
      break;
    case 'night':
      color = PAL.navy;
      alpha = 0.35;
      break;
    case 'blueFire':
      color = PAL.blueFire;
      alpha = 0.28;
      break;
  }

  if (alpha > 0) {
    const rect = scene.add
      .rectangle(0, 0, GAME_W, GAME_H, color, alpha)
      .setOrigin(0, 0)
      .setDepth(999)
      .setScrollFactor(0)
      .setName('tod_overlay');
    return rect;
  }
  return null;
}
