import Phaser from 'phaser';
import { PAL, hex } from '@/config';
import type { Btn } from './Input';

export interface VirtualPadState {
  up: boolean;
  down: boolean;
  left: boolean;
  right: boolean;
  a: boolean;
  b: boolean;
  m: boolean;
}

export type VirtualPadBtn = keyof VirtualPadState;

interface HitBox {
  minX: number;
  minY: number;
  maxX: number;
  maxY: number;
}

interface ButtonVisuals {
  unpressedG: Phaser.GameObjects.Graphics;
  pressedG: Phaser.GameObjects.Graphics;
  labelText: Phaser.GameObjects.Text;
  subText?: Phaser.GameObjects.Text;
  baseY: number;
  baseSubY?: number;
  normalColorHex: string;
}

interface ButtonConfig {
  key: VirtualPadBtn;
  x: number;
  y: number;
  w: number;
  h: number;
  label: string;
  sublabel?: string;
  accent: number;
  labelSize: string;
  labelOffsetY: number;
  subOffsetY?: number;
}

const HEX_YELLOW = hex(PAL.yellow);
const HEX_CYAN = hex(PAL.cyan);
const HEX_WHITE = hex(PAL.white);
const HEX_SLATE = hex(PAL.slate);

/**
 * Auto-detect touch capability on the device.
 */
export function isTouchDevice(scene?: Phaser.Scene): boolean {
  try {
    if (typeof navigator !== 'undefined') {
      if (navigator.maxTouchPoints > 0 || ((navigator as any).msMaxTouchPoints ?? 0) > 0) {
        return true;
      }
    }
  } catch {
    // Ignore restricted navigator
  }
  try {
    if (scene?.sys?.game?.device?.input?.touch) {
      return true;
    }
  } catch {
    // Ignore
  }
  return false;
}

/**
 * Draws retro 16-bit arcade button with bevels, drop shadows/glow, and chamfered corners.
 */
function drawRetroButton(
  g: Phaser.GameObjects.Graphics,
  cx: number,
  cy: number,
  w: number,
  h: number,
  isPressed: boolean,
  accentColor: number = PAL.cyan
): void {
  const left = Math.round(cx - w / 2);
  const top = Math.round(cy - h / 2);

  // Outer shadow or halo
  if (isPressed) {
    g.fillStyle(PAL.yellow, 0.25);
    g.fillRect(left - 2, top - 2, w + 4, h + 4);
    g.fillStyle(PAL.yellow, 0.45);
    g.fillRect(left - 1, top - 1, w + 2, h + 2);
  } else {
    g.fillStyle(PAL.void, 0.4);
    g.fillRect(left + 2, top + 2, w, h);
  }

  // Button background body
  const bodyFill = isPressed ? PAL.steel : PAL.panel;
  const bodyAlpha = isPressed ? 0.95 : 0.82;
  g.fillStyle(bodyFill, bodyAlpha);
  g.fillRect(left + 1, top + 1, w - 2, h - 2);

  // Top highlight line (tactile bevel)
  const hiColor = isPressed ? PAL.cyanHi : PAL.panelHi;
  g.fillStyle(hiColor, isPressed ? 0.8 : 0.6);
  g.fillRect(left + 2, top + 2, w - 4, 1);

  // Pixel border with chamfered / cut corners
  const borderColor = isPressed ? PAL.yellow : accentColor;
  g.fillStyle(borderColor, 0.95);
  // Top and bottom horizontal borders
  g.fillRect(left + 2, top, w - 4, 1);
  g.fillRect(left + 2, top + h - 1, w - 4, 1);
  // Left and right vertical borders
  g.fillRect(left, top + 2, 1, h - 4);
  g.fillRect(left + w - 1, top + 2, 1, h - 4);
  // Chamfered corner inner pixels
  g.fillRect(left + 1, top + 1, 1, 1);
  g.fillRect(left + w - 2, top + 1, 1, 1);
  g.fillRect(left + 1, top + h - 2, 1, 1);
  g.fillRect(left + w - 2, top + h - 2, 1, 1);
}

/**
 * Draws the central pivot plate unifying the 4-way D-Pad arms.
 */
function drawDPadHub(g: Phaser.GameObjects.Graphics, cx: number, cy: number, size: number): void {
  const left = Math.round(cx - size / 2);
  const top = Math.round(cy - size / 2);
  g.fillStyle(PAL.ink, 0.65);
  g.fillRect(left, top, size, size);
  g.fillStyle(PAL.steel, 0.45);
  g.fillRect(left + 1, top + 1, size - 2, size - 2);
  g.fillStyle(PAL.slate, 0.85);
  g.fillRect(cx - 5, cy - 5, 10, 10);
  g.fillStyle(PAL.panel, 0.95);
  g.fillRect(cx - 2, cy - 2, 4, 4);
}

/**
 * On-screen virtual touch controls container for mobile and tablet players.
 * Renders an arcade-style retro controller:
 * - Left: 4-way D-Pad (Up, Down, Left, Right)
 * - Right: Action buttons [A] (OK / Interact), [B] (Cancel / Back), [M] (Menu / Phone)
 * Zero memory allocations during update frames.
 */
export class VirtualPad extends Phaser.GameObjects.Container {
  readonly padState: VirtualPadState = {
    up: false,
    down: false,
    left: false,
    right: false,
    a: false,
    b: false,
    m: false,
  };

  readonly justPressed: VirtualPadState = {
    up: false,
    down: false,
    left: false,
    right: false,
    a: false,
    b: false,
    m: false,
  };

  private readonly hitBoxes: HitBox[] = [];
  private readonly zones: Phaser.GameObjects.Zone[] = [];
  private readonly buttonElements: Partial<Record<VirtualPadBtn, ButtonVisuals>> = {};

  private readonly dpadCenterX = 105;
  private readonly dpadCenterY = 475;
  private isPointerInDPadState = false;

  private pointerMoveHandler?: (p: Phaser.Input.Pointer) => void;
  private pointerUpHandler?: () => void;

  constructor(scene: Phaser.Scene, depth = 990) {
    super(scene, 0, 0);
    this.setDepth(depth);
    this.setScrollFactor(0);
    scene.add.existing(this as any);

    // Ensure multi-touch pointers exist
    if (scene.input?.addPointer) {
      const count = (scene.input as any).totalPointers ?? (scene.input as any).pointersTotal ?? 1;
      if (count < 3) {
        scene.input.addPointer(3 - count);
      }
    }

    this.createControls();

    // Auto-detect touch capability
    const touchAvailable = isTouchDevice(scene);
    this.setVisible(touchAvailable);

    // Global pointer listeners for smooth sliding and safety release
    if (scene.input?.on) {
      this.pointerMoveHandler = (p: Phaser.Input.Pointer) => this.handlePointerMove(p);
      this.pointerUpHandler = () => this.checkAllPointersUp();

      scene.input.on('pointermove', this.pointerMoveHandler);
      scene.input.on('pointerup', this.pointerUpHandler);
    }
  }

  private createControls(): void {
    const scene = this.scene;

    // D-Pad decorative center hub
    const hubG = scene.add.graphics();
    drawDPadHub(hubG, this.dpadCenterX, this.dpadCenterY, 44);
    this.add(hubG);

    // D-Pad cluster bounding area for quick touch filtering
    this.hitBoxes.push({
      minX: this.dpadCenterX - 85,
      minY: this.dpadCenterY - 85,
      maxX: this.dpadCenterX + 85,
      maxY: this.dpadCenterY + 85,
    });

    const configs: ButtonConfig[] = [
      // Left side: 4-Way D-Pad
      {
        key: 'up',
        x: this.dpadCenterX,
        y: this.dpadCenterY - 47,
        w: 44,
        h: 44,
        label: '▲',
        accent: PAL.steel,
        labelSize: '20px',
        labelOffsetY: 0,
      },
      {
        key: 'down',
        x: this.dpadCenterX,
        y: this.dpadCenterY + 47,
        w: 44,
        h: 44,
        label: '▼',
        accent: PAL.steel,
        labelSize: '20px',
        labelOffsetY: 0,
      },
      {
        key: 'left',
        x: this.dpadCenterX - 47,
        y: this.dpadCenterY,
        w: 44,
        h: 44,
        label: '◀',
        accent: PAL.steel,
        labelSize: '20px',
        labelOffsetY: 0,
      },
      {
        key: 'right',
        x: this.dpadCenterX + 47,
        y: this.dpadCenterY,
        w: 44,
        h: 44,
        label: '▶',
        accent: PAL.steel,
        labelSize: '20px',
        labelOffsetY: 0,
      },

      // Right side: Action buttons [A], [B], [M]
      {
        key: 'a',
        x: 945,
        y: 455,
        w: 52,
        h: 52,
        label: 'A',
        sublabel: 'OK',
        accent: PAL.yellow,
        labelSize: '20px',
        labelOffsetY: -5,
        subOffsetY: 16,
      },
      {
        key: 'b',
        x: 865,
        y: 495,
        w: 48,
        h: 48,
        label: 'B',
        sublabel: 'BACK',
        accent: PAL.cyan,
        labelSize: '18px',
        labelOffsetY: -5,
        subOffsetY: 15,
      },
      {
        key: 'm',
        x: 945,
        y: 365,
        w: 48,
        h: 36,
        label: 'M',
        sublabel: 'MENU',
        accent: PAL.cyan,
        labelSize: '16px',
        labelOffsetY: -4,
        subOffsetY: 11,
      },
    ];

    for (let i = 0; i < configs.length; i++) {
      this.buildButton(configs[i]);
    }
  }

  private buildButton(cfg: ButtonConfig): void {
    const scene = this.scene;

    // 1. Unpressed state graphics
    const unpressedG = scene.add.graphics();
    drawRetroButton(unpressedG, cfg.x, cfg.y, cfg.w, cfg.h, false, cfg.accent);
    this.add(unpressedG);

    // 2. Pressed state graphics (initially hidden)
    const pressedG = scene.add.graphics();
    drawRetroButton(pressedG, cfg.x, cfg.y, cfg.w, cfg.h, true, cfg.accent);
    pressedG.setVisible(false);
    this.add(pressedG);

    // 3. Label text
    const normalColorHex = cfg.accent === PAL.yellow ? HEX_YELLOW : cfg.key === 'a' ? HEX_YELLOW : HEX_CYAN;
    const baseY = cfg.y + cfg.labelOffsetY;
    const labelText = scene.add.text(cfg.x, baseY, cfg.label, {
      fontFamily: 'monospace, "Courier New", sans-serif',
      fontSize: cfg.labelSize,
      fontStyle: 'bold',
      color: normalColorHex,
      align: 'center',
    }).setOrigin(0.5, 0.5);
    this.add(labelText);

    // 4. Sublabel text (if any)
    let subText: Phaser.GameObjects.Text | undefined;
    let baseSubY: number | undefined;
    if (cfg.sublabel && cfg.subOffsetY !== undefined) {
      baseSubY = cfg.y + cfg.subOffsetY;
      subText = scene.add.text(cfg.x, baseSubY, cfg.sublabel, {
        fontFamily: 'monospace, "Courier New", sans-serif',
        fontSize: '8px',
        fontStyle: 'bold',
        color: HEX_SLATE,
        align: 'center',
      }).setOrigin(0.5, 0.5);
      this.add(subText);
    }

    // 5. Interactive touch zone with generous padding
    const zoneW = cfg.w + 12;
    const zoneH = cfg.h + 12;
    const zone = scene.add.zone(cfg.x, cfg.y, zoneW, zoneH);
    zone.setOrigin(0.5, 0.5);
    zone.setScrollFactor(0);
    zone.setInteractive({ useHandCursor: true });
    this.add(zone);
    this.zones.push(zone);

    zone.on('pointerdown', () => this.handleButtonDown(cfg.key));
    zone.on('pointerup', () => this.handleButtonUp(cfg.key));
    zone.on('pointerout', () => this.handleButtonUp(cfg.key));
    zone.on('pointerover', (p: Phaser.Input.Pointer) => {
      if (p.isDown) this.handleButtonDown(cfg.key);
    });

    // 6. Hitbox registration
    this.hitBoxes.push({
      minX: cfg.x - zoneW / 2,
      minY: cfg.y - zoneH / 2,
      maxX: cfg.x + zoneW / 2,
      maxY: cfg.y + zoneH / 2,
    });

    this.buttonElements[cfg.key] = {
      unpressedG,
      pressedG,
      labelText,
      subText,
      baseY,
      baseSubY,
      normalColorHex,
    };
  }

  private handleButtonDown(key: VirtualPadBtn): void {
    if (!this.padState[key]) {
      this.padState[key] = true;
      this.justPressed[key] = true;
      this.updateButtonVisual(key, true);
    }
  }

  private handleButtonUp(key: VirtualPadBtn): void {
    if (this.padState[key]) {
      this.padState[key] = false;
      this.updateButtonVisual(key, false);
    }
  }

  private updateButtonVisual(key: VirtualPadBtn, isDown: boolean): void {
    const btn = this.buttonElements[key];
    if (!btn) return;
    btn.unpressedG.setVisible(!isDown);
    btn.pressedG.setVisible(isDown);
    btn.labelText.setColor(isDown ? HEX_WHITE : btn.normalColorHex);
    btn.labelText.setY(isDown ? btn.baseY + 1 : btn.baseY);
    if (btn.subText && btn.baseSubY !== undefined) {
      btn.subText.setColor(isDown ? HEX_YELLOW : HEX_SLATE);
      btn.subText.setY(isDown ? btn.baseSubY + 1 : btn.baseSubY);
    }
  }

  /**
   * Handle thumb dragging smoothly across the 4-way D-Pad.
   */
  private handlePointerMove(p: Phaser.Input.Pointer): void {
    if (!this.visible || !p.isDown) return;
    const dx = p.x - this.dpadCenterX;
    const dy = p.y - this.dpadCenterY;
    const distSq = dx * dx + dy * dy;

    if (distSq <= 80 * 80) {
      const deadzone = 14;
      const isLeft = dx < -deadzone;
      const isRight = dx > deadzone;
      const isUp = dy < -deadzone;
      const isDown = dy > deadzone;

      this.isPointerInDPadState = true;
      this.setDPadState(isUp, isDown, isLeft, isRight);
    } else if (this.isPointerInDPadState) {
      this.setDPadState(false, false, false, false);
      this.isPointerInDPadState = false;
    }
  }

  private setDPadState(up: boolean, down: boolean, left: boolean, right: boolean): void {
    if (this.padState.up !== up) {
      this.padState.up = up;
      if (up) this.justPressed.up = true;
      this.updateButtonVisual('up', up);
    }
    if (this.padState.down !== down) {
      this.padState.down = down;
      if (down) this.justPressed.down = true;
      this.updateButtonVisual('down', down);
    }
    if (this.padState.left !== left) {
      this.padState.left = left;
      if (left) this.justPressed.left = true;
      this.updateButtonVisual('left', left);
    }
    if (this.padState.right !== right) {
      this.padState.right = right;
      if (right) this.justPressed.right = true;
      this.updateButtonVisual('right', right);
    }
  }

  private checkAllPointersUp(): void {
    const manager = this.scene.input?.manager;
    if (!manager) return;
    for (let i = 0; i < manager.pointers.length; i++) {
      if (manager.pointers[i].isDown) {
        return;
      }
    }
    this.releaseAll();
  }

  /**
   * Release all buttons and reset edge-triggered states.
   */
  releaseAll(): void {
    this.setDPadState(false, false, false, false);
    this.handleButtonUp('a');
    this.handleButtonUp('b');
    this.handleButtonUp('m');
    this.justPressed.up = false;
    this.justPressed.down = false;
    this.justPressed.left = false;
    this.justPressed.right = false;
    this.justPressed.a = false;
    this.justPressed.b = false;
    this.justPressed.m = false;
    this.isPointerInDPadState = false;
  }

  /**
   * Toggles visibility of the virtual pad.
   */
  toggle(): boolean {
    this.setVisible(!this.visible);
    return this.visible;
  }

  override setVisible(v: boolean): this {
    super.setVisible(v);
    for (let i = 0; i < this.zones.length; i++) {
      const input = this.zones[i].input;
      if (input) {
        input.enabled = v;
      }
    }
    if (!v) {
      this.releaseAll();
    }
    return this;
  }

  /**
   * Checks whether a screen point touches any part of the VirtualPad controls.
   * Used by Input to prevent spurious gameplay pointer taps when tapping pad buttons.
   */
  containsPoint(px: number, py: number): boolean {
    if (!this.visible) return false;
    for (let i = 0; i < this.hitBoxes.length; i++) {
      const box = this.hitBoxes[i];
      if (px >= box.minX && px <= box.maxX && py >= box.minY && py <= box.maxY) {
        return true;
      }
    }
    return false;
  }

  /**
   * Returns whether a specific virtual button is currently held down.
   */
  isDown(btn: VirtualPadBtn): boolean {
    return this.padState[btn];
  }

  /**
   * Consumes and resets the edge-triggered just-pressed flag for a virtual button.
   */
  consumeJustPressed(btn: VirtualPadBtn): boolean {
    const val = this.justPressed[btn];
    this.justPressed[btn] = false;
    return val;
  }

  /**
   * Maps an Input `Btn` to its VirtualPad counterpart and checks held state.
   */
  isBtnDown(btn: Btn): boolean {
    switch (btn) {
      case 'up': return this.padState.up;
      case 'down': return this.padState.down;
      case 'left': return this.padState.left;
      case 'right': return this.padState.right;
      case 'ok': return this.padState.a;
      case 'cancel': return this.padState.b;
      case 'menu': return this.padState.m;
      default: return false;
    }
  }

  /**
   * Maps an Input `Btn` to its VirtualPad counterpart and consumes edge-triggered press.
   */
  consumeBtnJustPressed(btn: Btn): boolean {
    switch (btn) {
      case 'up': {
        const v = this.justPressed.up;
        this.justPressed.up = false;
        return v;
      }
      case 'down': {
        const v = this.justPressed.down;
        this.justPressed.down = false;
        return v;
      }
      case 'left': {
        const v = this.justPressed.left;
        this.justPressed.left = false;
        return v;
      }
      case 'right': {
        const v = this.justPressed.right;
        this.justPressed.right = false;
        return v;
      }
      case 'ok': {
        const v = this.justPressed.a;
        this.justPressed.a = false;
        return v;
      }
      case 'cancel': {
        const v = this.justPressed.b;
        this.justPressed.b = false;
        return v;
      }
      case 'menu': {
        const v = this.justPressed.m;
        this.justPressed.m = false;
        return v;
      }
      default: return false;
    }
  }

  override destroy(fromScene?: boolean): void {
    if (this.pointerMoveHandler && this.scene?.input) {
      this.scene.input.off('pointermove', this.pointerMoveHandler);
    }
    if (this.pointerUpHandler && this.scene?.input) {
      this.scene.input.off('pointerup', this.pointerUpHandler);
    }
    super.destroy(fromScene);
  }
}
