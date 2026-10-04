// @ts-nocheck
import { describe, it, expect } from 'vitest';
import fs from 'node:fs';
import path from 'node:path';
import manifest from '../public/assets/manifest.json';
import { createDevChapterState } from '@/systems/DevState';

describe('Memorial Photo Assets & Outro Integration', () => {
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

  it('contains pixel-perfect 1024x576 memorial_photo.png background', () => {
    const fullPath = path.join(assetsDir, 'bg/memorial_photo.png');
    expect(fs.existsSync(fullPath), 'memorial_photo.png should exist').toBe(true);
    const dims = readPngDimensions(fullPath);
    expect(dims).toEqual({ width: 1024, height: 576 });
    const stats = fs.statSync(fullPath);
    expect(stats.size).toBeGreaterThan(10000);
  });

  it('includes memorial_photo in public/assets/manifest.json', () => {
    const images = (manifest as any).images;
    expect(images.memorial_photo).toBe('assets/bg/memorial_photo.png');
  });

  it('provides Chapter 10 Outro state for memorial scene', () => {
    const outroConfig = createDevChapterState('oziem', 10);
    expect(outroConfig.targetScene).toBe('Outro');
    expect(outroConfig.state.chapter).toBe(10);
    expect(outroConfig.state.party.length).toBe(6);
  });
});
