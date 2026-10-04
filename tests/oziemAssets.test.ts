// @ts-nocheck
import { describe, it, expect } from 'vitest';
import fs from 'node:fs';
import path from 'node:path';
import manifest from '../public/assets/manifest.json';
import { createDevChapterState } from '@/systems/DevState';

describe('Oziem High-Definition Pixel Art & Assets', () => {
  const assetsDir = path.resolve(__dirname, '../public/assets');

  const readPngDimensions = (filePath: string) => {
    const buffer = fs.readFileSync(filePath);
    // Verify PNG magic bytes: 89 50 4E 47 0D 0A 1A 0A
    expect(buffer.subarray(0, 8).toString('hex')).toBe('89504e470d0a1a0a');
    // IHDR chunk: width at 16..20, height at 20..24
    const width = buffer.readUInt32BE(16);
    const height = buffer.readUInt32BE(20);
    return { width, height };
  };

  it('generates all Oziem spritesheets with precise engine frame dimensions', () => {
    const expectedSprites = [
      { file: 'sprites/oziem_walk.png', width: 128, height: 192 },
      { file: 'sprites/oziem_battle.png', width: 512, height: 80 },
      { file: 'sprites/oziem_sit.png', width: 64, height: 32 },
    ];

    for (const spr of expectedSprites) {
      const fullPath = path.join(assetsDir, spr.file);
      expect(fs.existsSync(fullPath), `${spr.file} should exist`).toBe(true);
      expect(readPngDimensions(fullPath)).toEqual({ width: spr.width, height: spr.height });
      const stats = fs.statSync(fullPath);
      // High-detail assets should have non-trivial file size (> 1KB)
      expect(stats.size).toBeGreaterThan(1000);
    }
  });

  it('generates all multi-resolution portraits, avatar, and hero analyzer card', () => {
    const expectedPortraits = [
      { file: 'portraits/oziem_128.png', width: 128, height: 128 },
      { file: 'portraits/oziem_96.png', width: 96, height: 96 },
      { file: 'portraits/oziem_64.png', width: 64, height: 64 },
      { file: 'ui/avatar_oziem.png', width: 32, height: 32 },
      { file: 'cards/oziem.png', width: 307, height: 182 },
    ];

    for (const p of expectedPortraits) {
      const fullPath = path.join(assetsDir, p.file);
      expect(fs.existsSync(fullPath), `${p.file} should exist`).toBe(true);
      expect(readPngDimensions(fullPath)).toEqual({ width: p.width, height: p.height });
      const stats = fs.statSync(fullPath);
      expect(stats.size).toBeGreaterThan(500);
    }
  });

  it('has valid manifest.json entries for Oziem portraits, cards, and avatar', () => {
    const images = (manifest as any).images;
    expect(images.portrait_oziem_128).toBe('assets/portraits/oziem_128.png');
    expect(images.portrait_oziem_96).toBe('assets/portraits/oziem_96.png');
    expect(images.portrait_oziem_64).toBe('assets/portraits/oziem_64.png');
    expect(images.card_oziem).toBe('assets/cards/oziem.png');
    expect(images.avatar_oziem).toBe('assets/ui/avatar_oziem.png');
  });

  it('verifies Oziem state in DevState for wilderness campfire and battle chapters', () => {
    // Chapter 7: Forest Campfire
    const ch7 = createDevChapterState('oziem', 7);
    expect(ch7.state.leader).toBe('oziem');
    expect(ch7.state.party).toContain('oziem');
    expect(ch7.targetScene).toBe('Campfire');
    expect(ch7.state.flags.oziem_joined).toBe(true);

    // Chapter 9: Wilderness Assault Battle
    const ch9 = createDevChapterState('oziem', 9);
    expect(ch9.state.leader).toBe('oziem');
    expect(ch9.state.party).toContain('oziem');
    expect(ch9.targetScene).toBe('Battle');
  });
});
