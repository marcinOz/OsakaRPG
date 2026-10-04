import { describe, it, expect } from 'vitest';
import fs from 'node:fs';
import path from 'node:path';
import { newGame } from '@/systems/GameState';
import manifest from '../public/assets/manifest.json';

describe('Phase 1 HD Overworld Maps & Assets', () => {
  const mapsDir = path.resolve(__dirname, '../public/assets/maps');
  const tilesDir = path.resolve(__dirname, '../public/assets/tiles');

  it('generates all 3 HD overworld maps with exact resolutions', () => {
    const aptPath = path.join(mapsDir, 'apartment_bg.png');
    const cityPath = path.join(mapsDir, 'city_bg.png');
    const zabkaPath = path.join(mapsDir, 'zabka_bg.png');

    expect(fs.existsSync(aptPath)).toBe(true);
    expect(fs.existsSync(cityPath)).toBe(true);
    expect(fs.existsSync(zabkaPath)).toBe(true);

    // Verify PNG header and dimensions
    const readPngDimensions = (filePath: string) => {
      const buffer = fs.readFileSync(filePath);
      // PNG header check
      expect(buffer.subarray(0, 8).toString('hex')).toBe('89504e470d0a1a0a');
      // IHDR chunk: width at 16..20, height at 20..24
      const width = buffer.readUInt32BE(16);
      const height = buffer.readUInt32BE(20);
      return { width, height };
    };

    expect(readPngDimensions(aptPath)).toEqual({ width: 1024, height: 576 });
    expect(readPngDimensions(cityPath)).toEqual({ width: 1280, height: 576 });
    expect(readPngDimensions(zabkaPath)).toEqual({ width: 1024, height: 576 });
  });

  it('provides updated tilesets matching the art standards', () => {
    const aptTiles = path.join(tilesDir, 'apartment.png');
    const cityTiles = path.join(tilesDir, 'city.png');
    const zabkaTiles = path.join(tilesDir, 'zabka.png');

    expect(fs.existsSync(aptTiles)).toBe(true);
    expect(fs.existsSync(cityTiles)).toBe(true);
    expect(fs.existsSync(zabkaTiles)).toBe(true);
  });

  it('includes HD map keys in manifest.json', () => {
    const images = (manifest as any).images;
    expect(images['map_apartment_bg']).toBe('assets/maps/apartment_bg.png');
    expect(images['map_city_bg']).toBe('assets/maps/city_bg.png');
    expect(images['map_zabka_bg']).toBe('assets/maps/zabka_bg.png');
  });

  it('preserves initial spawn coordinates in apartment', () => {
    const state = newGame('danny');
    expect(state.mapId).toBe('apartment');
    expect(state.x).toBe(4);
    expect(state.y).toBe(5);
  });
});
