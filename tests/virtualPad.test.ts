import { describe, it, expect, vi } from 'vitest';

vi.mock('phaser', () => {
  class MockContainer {
    x = 0;
    y = 0;
    depth = 0;
    scrollFactor = 0;
    visible = true;
    children: any[] = [];
    constructor(public scene: any, x = 0, y = 0) {
      this.x = x;
      this.y = y;
    }
    setDepth(d: number) {
      this.depth = d;
      return this;
    }
    setScrollFactor(s: number) {
      this.scrollFactor = s;
      return this;
    }
    setVisible(v: boolean) {
      this.visible = v;
      return this;
    }
    add(child: any) {
      this.children.push(child);
      return this;
    }
    destroy() {}
  }

  class MockGraphics {
    visible = true;
    fillStyle() { return this; }
    fillRect() { return this; }
    clear() { return this; }
    setVisible(v: boolean) { this.visible = v; return this; }
  }

  class MockText {
    text = '';
    color = '';
    y = 0;
    origin = [0, 0];
    constructor(public x: number, y: number, text: string) {
      this.y = y;
      this.text = text;
    }
    setOrigin(x: number, y: number) { this.origin = [x, y]; return this; }
    setColor(c: string) { this.color = c; return this; }
    setY(y: number) { this.y = y; return this; }
  }

  class MockZone {
    input = { enabled: true };
    handlers: Record<string, Function[]> = {};
    constructor(public x: number, public y: number, public w: number, public h: number) {}
    setOrigin() { return this; }
    setScrollFactor() { return this; }
    setInteractive() { return this; }
    on(event: string, fn: Function) {
      if (!this.handlers[event]) this.handlers[event] = [];
      this.handlers[event].push(fn);
      return this;
    }
    emit(event: string, ...args: any[]) {
      this.handlers[event]?.forEach((fn) => fn(...args));
    }
  }

  return {
    default: {
      GameObjects: {
        Container: MockContainer,
        Graphics: MockGraphics,
        Text: MockText,
        Zone: MockZone,
      },
      Input: {
        Keyboard: {
          KeyCodes: {
            UP: 38, DOWN: 40, LEFT: 37, RIGHT: 39,
            W: 87, S: 83, A: 65, D: 68,
            Z: 90, ENTER: 13, SPACE: 32,
            X: 88, ESC: 27, BACKSPACE: 8,
            M: 77, TAB: 9,
            ONE: 49, TWO: 50, THREE: 51,
          },
          JustDown: (k: any) => k?.justDown ?? false,
        },
      },
    },
  };
});

import Phaser from 'phaser';
import { VirtualPad } from '@/ui/VirtualPad';
import { Input } from '@/ui/Input';

function createMockScene(isTouch = true) {
  const listeners: Record<string, Function[]> = {};
  return {
    sys: {
      game: {
        device: {
          input: {
            touch: isTouch,
          },
        },
        loop: {
          frame: 1,
        },
      },
    },
    game: {
      loop: {
        frame: 1,
      },
    },
    input: {
      keyboard: {
        addKey: () => ({ isDown: false, justDown: false }),
      },
      addPointer: vi.fn(),
      totalPointers: 1,
      on: (event: string, fn: Function) => {
        if (!listeners[event]) listeners[event] = [];
        listeners[event].push(fn);
      },
      emit: (event: string, ...args: any[]) => {
        listeners[event]?.forEach((fn) => fn(...args));
      },
    },
    add: {
      existing: vi.fn(),
      graphics: () => new (Phaser.GameObjects.Graphics as any)(),
      text: (x: number, y: number, s: string) => new (Phaser.GameObjects.Text as any)(x, y, s),
      zone: (x: number, y: number, w: number, h: number) => new (Phaser.GameObjects.Zone as any)(x, y, w, h),
    },
  } as any;
}

describe('VirtualPad & Input Integration', () => {
  it('detects touch availability and sets initial visibility', () => {
    const touchScene = createMockScene(true);
    const padTouch = new VirtualPad(touchScene);
    expect(padTouch.visible).toBe(true);

    const desktopScene = createMockScene(false);
    const padDesktop = new VirtualPad(desktopScene);
    expect(padDesktop.visible).toBe(false);
  });

  it('supports toggle() and setVisible() methods', () => {
    const scene = createMockScene(false);
    const pad = new VirtualPad(scene);
    expect(pad.visible).toBe(false);

    const toggled = pad.toggle();
    expect(toggled).toBe(true);
    expect(pad.visible).toBe(true);

    pad.setVisible(false);
    expect(pad.visible).toBe(false);
  });

  it('filters screen taps when tapping on VirtualPad controls', () => {
    const scene = createMockScene(true);
    const pad = new VirtualPad(scene);
    const input = new Input(scene, pad);

    // Virtual pad D-Pad center is around (105, 475)
    expect(pad.containsPoint(105, 475)).toBe(true);
    // Button A is at (945, 455)
    expect(pad.containsPoint(945, 455)).toBe(true);
    // Button B is at (865, 495)
    expect(pad.containsPoint(865, 495)).toBe(true);
    // Button M is at (945, 365)
    expect(pad.containsPoint(945, 365)).toBe(true);

    // Center of screen (512, 288) should NOT be on virtual pad
    expect(pad.containsPoint(512, 288)).toBe(false);

    // Tapping on D-Pad shouldn't register as world tap
    scene.input.emit('pointerdown', { x: 105, y: 475 });
    expect(input.tap()).toBeNull();

    // Tapping on game canvas (512, 288) registers as world tap
    scene.input.emit('pointerdown', { x: 512, y: 288 });
    const tap = input.tap();
    expect(tap).not.toBeNull();
    expect(tap?.x).toBe(512);
    expect(tap?.y).toBe(288);
  });

  it('updates directional axis when virtual pad D-Pad is pressed', () => {
    const scene = createMockScene(true);
    const pad = new VirtualPad(scene);
    const input = new Input(scene, pad);

    expect(input.axis()).toEqual({ x: 0, y: 0 });

    // Simulate holding right
    (pad.padState as any).right = true;
    expect(input.held('right')).toBe(true);
    expect(input.axis()).toEqual({ x: 1, y: 0 });

    // Simulate holding up and right (diagonal)
    (pad.padState as any).up = true;
    expect(input.held('up')).toBe(true);
    expect(input.axis()).toEqual({ x: 1, y: -1 });

    // Release
    pad.releaseAll();
    expect(input.axis()).toEqual({ x: 0, y: 0 });
  });

  it('propagates action button presses to Input.pressed() and okOrTap()', () => {
    const scene = createMockScene(true);
    const pad = new VirtualPad(scene);
    const input = new Input(scene, pad);

    // Press [A] (OK / Interact)
    (pad.padState as any).a = true;
    (pad.justPressed as any).a = true;

    expect(input.held('ok')).toBe(true);
    expect(input.pressed('ok')).toBe(true);
    expect(input.okOrTap()).toBe(true);

    // Second check in next frame: edge-triggered press is consumed
    scene.game.loop.frame = 2;
    expect(input.pressed('ok')).toBe(false);
    // But held is still true
    expect(input.held('ok')).toBe(true);

    // Release [A]
    pad.releaseAll();
    expect(input.held('ok')).toBe(false);
  });

  it('maps B to cancel and M to menu across frames', () => {
    const scene = createMockScene(true);
    const pad = new VirtualPad(scene);
    const input = new Input(scene, pad);

    // Frame 1: Button B -> cancel
    scene.game.loop.frame = 10;
    (pad.padState as any).b = true;
    (pad.justPressed as any).b = true;
    expect(input.held('cancel')).toBe(true);
    expect(input.pressed('cancel')).toBe(true);

    // Frame 2: Button M -> menu
    scene.game.loop.frame = 11;
    (pad.padState as any).m = true;
    (pad.justPressed as any).m = true;
    expect(input.held('menu')).toBe(true);
    expect(input.pressed('menu')).toBe(true);

    pad.releaseAll();
    expect(input.held('cancel')).toBe(false);
    expect(input.held('menu')).toBe(false);
  });
});
