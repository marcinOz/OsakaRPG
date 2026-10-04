// @ts-nocheck
import { describe, it, expect } from 'vitest';
import fs from 'node:fs';
import path from 'node:path';
import manifest from '../public/assets/manifest.json';
import { ENEMIES } from '@/content/enemies';

describe('Enemies & Bosses High-Definition Pixel Art Assets', () => {
  const assetsDir = path.resolve(__dirname, '../public/assets/enemies');

  const readPngDimensions = (filePath: string) => {
    const buffer = fs.readFileSync(filePath);
    // Verify PNG magic bytes: 89 50 4E 47 0D 0A 1A 0A
    expect(buffer.subarray(0, 8).toString('hex')).toBe('89504e470d0a1a0a');
    // IHDR chunk: width at 16..20, height at 20..24
    const width = buffer.readUInt32BE(16);
    const height = buffer.readUInt32BE(20);
    return { width, height };
  };

  const expectedEnemySheets = [
    { id: 'bolKregoslupa', file: 'bolKregoslupa.png', width: 192, height: 96, frameSize: 96 },
    { id: 'slacki', file: 'slacki.png', width: 192, height: 96, frameSize: 96 }, // untouched
    { id: 'sasiadSzkodnik', file: 'sasiadSzkodnik.png', width: 256, height: 128, frameSize: 128 },
    { id: 'autoTuneHipster', file: 'autoTuneHipster.png', width: 256, height: 128, frameSize: 128 },
    { id: 'drogiePiwo', file: 'drogiePiwo.png', width: 256, height: 128, frameSize: 128 },
    { id: 'straznik', file: 'straznik.png', width: 256, height: 128, frameSize: 128 },
    { id: 'kark', file: 'kark.png', width: 256, height: 128, frameSize: 128 },
    { id: 'rwaKulszowa', file: 'rwaKulszowa.png', width: 256, height: 128, frameSize: 128 },
    { id: 'panJanusz', file: 'panJanusz.png', width: 288, height: 144, frameSize: 144 },
    { id: 'kredyt', file: 'kredyt.png', width: 288, height: 144, frameSize: 144 },
    { id: 'audyt', file: 'audyt.png', width: 288, height: 144, frameSize: 144 },
  ];

  it('contains valid high-definition spritesheets for all 11 enemies/bosses', () => {
    for (const enemy of expectedEnemySheets) {
      const fullPath = path.join(assetsDir, enemy.file);
      expect(fs.existsSync(fullPath), `${enemy.file} should exist on disk`).toBe(true);

      const dims = readPngDimensions(fullPath);
      expect(dims.width).toBe(enemy.width);
      expect(dims.height).toBe(enemy.height);

      const stats = fs.statSync(fullPath);
      expect(stats.size).toBeGreaterThan(1500);
    }
  });

  it('matches all entries and frame dimensions in public/assets/manifest.json', () => {
    const spritesheets = (manifest as any).spritesheets;
    for (const enemy of expectedEnemySheets) {
      const key = `enemy_${enemy.id}`;
      expect(spritesheets[key], `manifest.json should contain spritesheet ${key}`).toBeDefined();
      expect(spritesheets[key].path).toBe(`assets/enemies/${enemy.file}`);
      expect(spritesheets[key].frameWidth).toBe(enemy.frameSize);
      expect(spritesheets[key].frameHeight).toBe(enemy.frameSize);
    }
  });

  it('verifies all registered ENEMIES in src/content/enemies.ts map to valid sprites', () => {
    for (const [id, def] of Object.entries(ENEMIES)) {
      expect(def.sprite).toBe(`enemy_${id}`);
      const expected = expectedEnemySheets.find((e) => e.id === id);
      expect(expected, `Enemy ${id} must be in the expected registry`).toBeDefined();
    }
  });
});
