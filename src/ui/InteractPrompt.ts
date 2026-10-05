import Phaser from 'phaser';
import { PAL } from '@/config';
import { txt } from './Text';
import { drawPanel } from './Panel';
import { isTouchDevice } from './VirtualPad';

export class InteractPrompt {
  private container: Phaser.GameObjects.Container;
  private background: Phaser.GameObjects.Graphics;
  private labelText: Phaser.GameObjects.BitmapText | Phaser.GameObjects.Text;
  private keycapText: Phaser.GameObjects.BitmapText | Phaser.GameObjects.Text;
  private isVisible = false;
  private floatTween: Phaser.Tweens.Tween | null = null;
  private currentTarget = '';

  constructor(private scene: Phaser.Scene) {
    this.container = scene.add.container(0, 0).setDepth(850).setAlpha(0);

    this.background = scene.add.graphics();
    this.container.add(this.background);

    const isTouch = isTouchDevice(scene);
    this.keycapText = txt(scene, 0, 0, isTouch ? '[A]' : '[Z]', {
      color: PAL.yellow,
      fontSize: '14px',
      fontStyle: 'bold',
      fontFamily: 'monospace, sans-serif',
      resolution: 2,
      origin: [0, 0.5],
    });
    this.container.add(this.keycapText);

    this.labelText = txt(scene, 0, 0, '', {
      color: PAL.cyanHi,
      fontSize: '14px',
      fontStyle: 'bold',
      fontFamily: 'monospace, sans-serif',
      resolution: 2,
      origin: [0, 0.5],
    });
    this.container.add(this.labelText);

    this.floatTween = scene.tweens.add({
      targets: this.container,
      y: '-=4',
      duration: 650,
      yoyo: true,
      repeat: -1,
      ease: 'Sine.easeInOut',
    });
  }

  show(targetKey: string, worldX: number, worldY: number, actionLabel: string, isAlert = false): void {
    if (this.isVisible && this.currentTarget === targetKey) {
      return;
    }

    this.currentTarget = targetKey;
    this.isVisible = true;

    // Position container above target
    this.container.setPosition(worldX, worldY - 32);

    // Update text
    const isTouch = isTouchDevice(this.scene);
    (this.keycapText as any).setText(isTouch ? '[A]' : '[Z]');
    (this.labelText as any).setText(actionLabel);

    // Layout
    const padX = 8;
    const keyW = (this.keycapText as any).width ?? (isTouch ? 28 : 30);
    const labelW = (this.labelText as any).width ?? (actionLabel.length * 8.5);
    const totalW = padX * 3 + keyW + labelW;
    const h = 28;

    this.background.clear();
    drawPanel(this.background, -totalW / 2, -h / 2, totalW, h, {
      fill: PAL.void,
      border: isAlert ? PAL.fireHi : PAL.cyan,
      glow: true,
    });

    // Little triangular arrow pointing down
    this.background.fillStyle(PAL.void, 1);
    this.background.fillTriangle(-5, h / 2 - 1, 5, h / 2 - 1, 0, h / 2 + 5);
    this.background.lineStyle(1, isAlert ? PAL.fireHi : PAL.cyan, 1);
    this.background.lineBetween(-5, h / 2 - 1, 0, h / 2 + 5);
    this.background.lineBetween(5, h / 2 - 1, 0, h / 2 + 5);

    this.keycapText.setPosition(-totalW / 2 + padX, 0);
    this.labelText.setPosition(-totalW / 2 + padX + keyW + 4, 0);

    this.scene.tweens.killTweensOf(this.container);
    this.container.setScale(0.8);
    this.scene.tweens.add({
      targets: this.container,
      alpha: 1,
      scale: 1,
      duration: 120,
      ease: 'Back.easeOut',
    });
  }

  hide(): void {
    if (!this.isVisible) return;
    this.isVisible = false;
    this.currentTarget = '';
    this.scene.tweens.killTweensOf(this.container);
    this.scene.tweens.add({
      targets: this.container,
      alpha: 0,
      scale: 0.8,
      duration: 100,
      ease: 'Quad.easeIn',
    });
  }

  destroy(): void {
    this.floatTween?.stop();
    this.container.destroy();
  }
}
