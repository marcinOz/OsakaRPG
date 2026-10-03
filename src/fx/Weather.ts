import Phaser from 'phaser';
import { GAME_W, GAME_H, PAL } from '@/config';

export type WeatherKind = 'rain' | 'fog' | 'fireflies' | 'embers' | 'dust' | 'leaves' | 'smoke';

export interface WeatherHandle {
  destroy(): void;
  setIntensity(level: number): void;
}

function ensureParticleTextures(scene: Phaser.Scene): void {
  const tex = scene.textures;
  if (!tex.exists('p_dot_white')) {
    const g = scene.make.graphics({ x: 0, y: 0 });
    g.fillStyle(0xffffff, 1);
    g.fillRect(0, 0, 2, 2);
    g.generateTexture('p_dot_white', 2, 2);
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
}

export function addWeather(
  scene: Phaser.Scene,
  kind: WeatherKind,
  opts: { x?: number; y?: number; count?: number } = {}
): WeatherHandle {
  ensureParticleTextures(scene);

  const container = scene.add.container(0, 0).setDepth(800).setScrollFactor(0);

  if (kind === 'embers') {
    const originX = opts.x ?? GAME_W / 2;
    const originY = opts.y ?? GAME_H / 2;

    const emitter = scene.add.particles(originX, originY, 'p_ember', {
      speed: { min: 20, max: 60 },
      angle: { min: 250, max: 290 },
      scale: { start: 1.5, end: 0.2 },
      alpha: { start: 1, end: 0 },
      lifespan: { min: 1000, max: 2000 },
      frequency: 100,
      gravityY: -15,
      blendMode: 'ADD',
    });
    container.add(emitter);

    return {
      destroy: () => container.destroy(),
      setIntensity: (lvl) => {
        emitter.frequency = Math.max(20, Math.round(150 / lvl));
      },
    };
  }

  if (kind === 'fireflies') {
    const emitter = scene.add.particles(0, 0, 'p_firefly', {
      emitZone: {
        type: 'random',
        source: new Phaser.Geom.Rectangle(0, 0, GAME_W, GAME_H),
      } as any,
      speed: { min: 5, max: 15 },
      lifespan: { min: 3000, max: 6000 },
      scale: { start: 0.5, end: 1 },
      alpha: {
        start: 0,
        end: 1,
        ease: 'Sine.easeInOut',
      },
      frequency: 300,
      blendMode: 'ADD',
    });
    container.add(emitter);

    return {
      destroy: () => container.destroy(),
      setIntensity: (lvl) => {
        emitter.frequency = Math.max(50, Math.round(400 / lvl));
      },
    };
  }

  // Fog or subtle ambient dust overlay
  const overlay = scene.add.rectangle(0, 0, GAME_W, GAME_H, PAL.cyan, 0.05).setOrigin(0, 0);
  container.add(overlay);

  return {
    destroy: () => container.destroy(),
    setIntensity: (lvl) => {
      overlay.setFillStyle(PAL.cyan, 0.05 * lvl);
    },
  };
}
