import Phaser from 'phaser';

export type Btn = 'up' | 'down' | 'left' | 'right' | 'ok' | 'cancel' | 'menu' | 'n1' | 'n2' | 'n3';

/**
 * Unified input: arrows/WASD move, Z/Enter/Space confirm, X/Esc/Backspace cancel, M/Tab menu, 1-3 quick choices.
 * Pointer taps emit 'ok'. Provides edge-triggered `pressed()` and level `held()`.
 */
export class Input {
  private keys: Record<Btn, Phaser.Input.Keyboard.Key[]>;
  private tapped = false;
  private tapPos: { x: number; y: number } | null = null;

  constructor(scene: Phaser.Scene) {
    const kb = scene.input.keyboard!;
    const K = Phaser.Input.Keyboard.KeyCodes;
    const add = (...codes: number[]) => codes.map((c) => kb.addKey(c, true, false));
    this.keys = {
      up: add(K.UP, K.W),
      down: add(K.DOWN, K.S),
      left: add(K.LEFT, K.A),
      right: add(K.RIGHT, K.D),
      ok: add(K.Z, K.ENTER, K.SPACE),
      cancel: add(K.X, K.ESC, K.BACKSPACE),
      menu: add(K.M, K.TAB),
      n1: add(K.ONE),
      n2: add(K.TWO),
      n3: add(K.THREE),
    };
    scene.input.on('pointerdown', (p: Phaser.Input.Pointer) => {
      this.tapped = true;
      this.tapPos = { x: p.x, y: p.y };
    });
  }

  pressed(b: Btn): boolean {
    return this.keys[b].some((k) => Phaser.Input.Keyboard.JustDown(k));
  }

  held(b: Btn): boolean {
    return this.keys[b].some((k) => k.isDown);
  }

  /** consume a pointer tap (returns position) */
  tap(): { x: number; y: number } | null {
    if (!this.tapped) return null;
    this.tapped = false;
    return this.tapPos;
  }

  okOrTap(): boolean {
    const k = this.pressed('ok');
    const t = this.tap();
    return k || !!t;
  }

  axis(): { x: number; y: number } {
    const x = (this.held('right') ? 1 : 0) - (this.held('left') ? 1 : 0);
    const y = (this.held('down') ? 1 : 0) - (this.held('up') ? 1 : 0);
    return { x, y };
  }
}
