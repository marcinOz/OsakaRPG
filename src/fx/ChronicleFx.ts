import Phaser from 'phaser';
import { GAME_W, GAME_H, PAL } from '@/config';
import { flicker } from '@/systems/ChronicleTimeline';

export interface FxHandle {
  update(dtMs: number, t: number): void;
  setAlpha(alpha: number): void;
  destroy(): void;
}

export function ensureChronicleTextures(scene: Phaser.Scene): void {
  const tex = scene.textures;

  if (!tex.exists('p_dot_white')) {
    const g = scene.make.graphics({ x: 0, y: 0 });
    g.fillStyle(0xffffff, 1);
    g.fillRect(0, 0, 2, 2);
    g.generateTexture('p_dot_white', 2, 2);
    g.destroy();
  }

  if (!tex.exists('p_rain_streak')) {
    const g = scene.make.graphics({ x: 0, y: 0 });
    g.fillStyle(PAL.cyan, 0.7);
    g.fillRect(0, 0, 2, 8);
    g.generateTexture('p_rain_streak', 2, 8);
    g.destroy();
  }

  if (!tex.exists('p_ember')) {
    const g = scene.make.graphics({ x: 0, y: 0 });
    g.fillStyle(PAL.fireHi, 1);
    g.fillRect(0, 0, 2, 2);
    g.fillStyle(PAL.fire, 1);
    g.fillRect(0, 1, 2, 1);
    g.generateTexture('p_ember', 2, 2);
    g.destroy();
  }

  if (!tex.exists('p_firefly')) {
    const g = scene.make.graphics({ x: 0, y: 0 });
    g.fillStyle(PAL.yellow, 1);
    g.fillRect(0, 0, 3, 3);
    g.fillStyle(PAL.white, 1);
    g.fillRect(1, 1, 1, 1);
    g.generateTexture('p_firefly', 3, 3);
    g.destroy();
  }

  if (!tex.exists('p_leaf')) {
    const g = scene.make.graphics({ x: 0, y: 0 });
    g.fillStyle(0x7a8a30, 1);
    g.fillRect(0, 0, 4, 3);
    g.fillStyle(0x506020, 1);
    g.fillRect(1, 1, 2, 1);
    g.generateTexture('p_leaf', 4, 3);
    g.destroy();
  }

  if (!tex.exists('p_radial_glow')) {
    const canvas = document.createElement('canvas');
    canvas.width = 64;
    canvas.height = 64;
    const ctx = canvas.getContext('2d');
    if (ctx) {
      const grad = ctx.createRadialGradient(32, 32, 0, 32, 32, 32);
      grad.addColorStop(0, 'rgba(255, 255, 255, 1)');
      grad.addColorStop(0.3, 'rgba(255, 240, 200, 0.6)');
      grad.addColorStop(0.7, 'rgba(255, 200, 100, 0.15)');
      grad.addColorStop(1, 'rgba(255, 200, 100, 0)');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, 64, 64);
      tex.addCanvas('p_radial_glow', canvas);
    }
  }
}

export function spawnParticlePreset(
  scene: Phaser.Scene,
  parent: Phaser.GameObjects.Container,
  preset: string,
  opts: any = {}
): FxHandle {
  ensureChronicleTextures(scene);
  const container = scene.add.container(0, 0);
  parent.add(container);

  let emitter: Phaser.GameObjects.Particles.ParticleEmitter | null = null;

  switch (preset) {
    case 'rain': {
      emitter = scene.add.particles(0, 0, 'p_rain_streak', {
        emitZone: {
          type: 'random',
          source: new Phaser.Geom.Rectangle(0, -20, GAME_W, 20),
        } as any,
        speedY: { min: 450, max: 700 },
        speedX: { min: -40, max: -10 },
        lifespan: 1200,
        frequency: 25,
        alpha: { start: 0.8, end: 0.2 },
        scale: { min: 0.8, max: 1.2 },
      });
      container.add(emitter);
      break;
    }
    case 'embers': {
      const originX = opts.x ?? 512;
      const originY = opts.y ?? 420;
      emitter = scene.add.particles(originX, originY, 'p_ember', {
        speed: { min: 25, max: 80 },
        angle: { min: 250, max: 290 },
        scale: { start: 1.6, end: 0.2 },
        alpha: { start: 1, end: 0 },
        lifespan: { min: 1200, max: 2400 },
        frequency: 80,
        gravityY: -20,
        blendMode: 'ADD',
      });
      container.add(emitter);
      break;
    }
    case 'fireflies': {
      emitter = scene.add.particles(0, 0, 'p_firefly', {
        emitZone: {
          type: 'random',
          source: new Phaser.Geom.Rectangle(0, 60, GAME_W, GAME_H - 120),
        } as any,
        speed: { min: 8, max: 20 },
        lifespan: { min: 3000, max: 5500 },
        scale: { start: 0.6, end: 1.2 },
        alpha: { start: 0, end: 0.9, ease: 'Sine.easeInOut' },
        frequency: 220,
        blendMode: 'ADD',
      });
      container.add(emitter);
      break;
    }
    case 'leaves': {
      emitter = scene.add.particles(0, 0, 'p_leaf', {
        emitZone: {
          type: 'random',
          source: new Phaser.Geom.Rectangle(-40, -10, GAME_W + 40, 10),
        } as any,
        speedY: { min: 30, max: 70 },
        speedX: { min: -50, max: -10 },
        rotate: { start: 0, end: 360 },
        lifespan: 7000,
        frequency: 350,
      });
      container.add(emitter);
      break;
    }
    case 'dust': {
      const shaftRect = opts.zone ?? new Phaser.Geom.Rectangle(200, 100, 400, 300);
      emitter = scene.add.particles(0, 0, 'p_dot_white', {
        emitZone: {
          type: 'random',
          source: shaftRect,
        } as any,
        speed: { min: 2, max: 6 },
        lifespan: { min: 2500, max: 4500 },
        scale: { start: 0.8, end: 1.2 },
        alpha: { start: 0, end: 0.6, ease: 'Sine.easeInOut' },
        frequency: 180,
        blendMode: 'ADD',
      });
      container.add(emitter);
      break;
    }
    case 'debrisSpiral': {
      const centerX = opts.x ?? 512;
      const centerY = opts.y ?? 260;
      emitter = scene.add.particles(centerX, centerY, 'p_dot_white', {
        speed: { min: 30, max: 120 },
        scale: { start: 2.0, end: 0.2 },
        alpha: { start: 0.9, end: 0.0 },
        lifespan: { min: 1000, max: 2000 },
        frequency: 70,
        blendMode: 'ADD',
      });
      container.add(emitter);
      break;
    }
    default:
      break;
  }

  return {
    update(_dt: number, _t: number) {},
    setAlpha(a: number) {
      container.setAlpha(a);
    },
    destroy() {
      container.destroy();
    },
  };
}

export function spawnLightGlow(
  scene: Phaser.Scene,
  parent: Phaser.GameObjects.Container,
  lightDef: any
): FxHandle {
  ensureChronicleTextures(scene);
  const at = lightDef.at ?? [512, 288];
  const glow = lightDef.glow;
  const radius = glow?.radius ?? 64;
  const colorHex = glow?.color ? parseInt(glow.color.replace('#', '0x'), 16) : 0xffb85a;
  const baseAlpha = glow?.alpha ?? 0.35;

  const glowSprite = scene.add.image(at[0], at[1], 'p_radial_glow');
  glowSprite.setDisplaySize(radius * 2, radius * 2);
  glowSprite.setTint(colorHex);
  glowSprite.setBlendMode('ADD');
  glowSprite.setAlpha(baseAlpha);
  parent.add(glowSprite);

  const style = lightDef.style ?? 'steady';
  const seed = lightDef.seed ?? 1;
  const minInt = lightDef.intensity?.[0] ?? 0.7;
  const maxInt = lightDef.intensity?.[1] ?? 1.0;

  return {
    update(_dt: number, _t: number) {
      const now = scene.time.now;
      const f = flicker(style, seed, now);
      const intensity = minInt + (maxInt - minInt) * f;
      glowSprite.setAlpha(baseAlpha * intensity);
    },
    setAlpha(a: number) {
      glowSprite.setAlpha(baseAlpha * a);
    },
    destroy() {
      glowSprite.destroy();
    },
  };
}

export function triggerLightningFlash(
  scene: Phaser.Scene,
  parent: Phaser.GameObjects.Container
): void {
  const flashRect = scene.add.rectangle(0, 0, GAME_W, GAME_H, 0xffffff, 0.85);
  flashRect.setOrigin(0, 0);
  parent.add(flashRect);

  scene.tweens.add({
    targets: flashRect,
    alpha: 0,
    duration: 350,
    ease: 'Quad.easeOut',
    onComplete: () => flashRect.destroy(),
  });
}

export function triggerBassShockwave(
  scene: Phaser.Scene,
  parent: Phaser.GameObjects.Container,
  x = 512,
  y = 360
): void {
  const g = scene.add.graphics();
  parent.add(g);

  let radius = 10;
  let alpha = 0.8;

  const timer = scene.time.addEvent({
    delay: 16,
    repeat: 24,
    callback: () => {
      radius += 8;
      alpha -= 0.032;
      g.clear();
      g.lineStyle(3, PAL.yellow, Math.max(0, alpha));
      g.strokeCircle(x, y, radius);
      if (alpha <= 0) {
        timer.remove();
        g.destroy();
      }
    },
  });
}
