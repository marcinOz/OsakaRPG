import Phaser from 'phaser';
import { PAL } from '@/config';
import { txt } from '@/ui/Text';

export function screenShake(scene: Phaser.Scene, intensity = 0.015, ms = 200): void {
  scene.cameras.main.shake(ms, intensity);
}

export function flash(scene: Phaser.Scene, color = 0xffffff, ms = 150): void {
  scene.cameras.main.flash(ms, (color >> 16) & 0xff, (color >> 8) & 0xff, color & 0xff);
}

export function damageNumber(
  scene: Phaser.Scene,
  x: number,
  y: number,
  text: string,
  color: number = PAL.white,
  crit = false
): void {
  const displayColor = crit ? PAL.yellow : color;
  const t = txt(scene, x, y - 10, text, {
    color: displayColor,
    big: crit,
    origin: [0.5, 0.5],
  });
  t.setDepth(2000);

  scene.tweens.add({
    targets: t,
    y: y - 26,
    scaleX: crit ? 1.4 : 1.1,
    scaleY: crit ? 1.4 : 1.1,
    alpha: 0,
    ease: 'Back.easeOut',
    duration: 700,
    onComplete: () => t.destroy(),
  });
}

export function fadeTransition(
  scene: Phaser.Scene,
  targetScene: string,
  data?: any,
  ms = 350
): void {
  scene.cameras.main.fadeOut(ms, 0, 3, 11);
  scene.cameras.main.once(Phaser.Cameras.Scene2D.Events.FADE_OUT_COMPLETE, () => {
    scene.scene.start(targetScene, data);
  });
}

export function glowPulse(
  scene: Phaser.Scene,
  target: Phaser.GameObjects.GameObject,
  _color = PAL.cyan
): Phaser.Tweens.Tween {
  return scene.tweens.add({
    targets: target,
    alpha: { from: 0.6, to: 1.0 },
    yoyo: true,
    repeat: -1,
    duration: 600,
    ease: 'Sine.easeInOut',
  });
}

export function scanSweep(
  scene: Phaser.Scene,
  x: number,
  y: number,
  w: number,
  h: number,
  color = PAL.cyanHi
): Phaser.GameObjects.Graphics {
  const g = scene.add.graphics().setDepth(500);
  g.fillStyle(color, 0.85);
  g.fillRect(x, y, w, 2);

  scene.tweens.add({
    targets: g,
    y: y + h - 2,
    yoyo: true,
    repeat: -1,
    duration: 1200,
    ease: 'Linear',
  });

  return g;
}
