// @ts-nocheck
import { describe, it, expect } from 'vitest';
import fs from 'node:fs';
import path from 'node:path';
import { newGame } from '@/systems/GameState';
import manifest from '../public/assets/manifest.json';

describe('HD Overworld Maps & Assets (Phase 1 & 2)', () => {
  const mapsDir = path.resolve(__dirname, '../public/assets/maps');
  const tilesDir = path.resolve(__dirname, '../public/assets/tiles');

  const readPngDimensions = (filePath: string) => {
    const buffer = fs.readFileSync(filePath);
    // PNG header check
    expect(buffer.subarray(0, 8).toString('hex')).toBe('89504e470d0a1a0a');
    // IHDR chunk: width at 16..20, height at 20..24
    const width = buffer.readUInt32BE(16);
    const height = buffer.readUInt32BE(20);
    return { width, height };
  };

  it('generates all 8 HD overworld maps with exact resolutions', () => {
    const expectedMaps = [
      { file: 'apartment_bg.png', width: 1024, height: 576 },
      { file: 'zabka_bg.png', width: 1024, height: 576 },
      { file: 'garage_bg.png', width: 1024, height: 576 },
      { file: 'pub_bg.png', width: 1024, height: 576 },
      { file: 'city_bg.png', width: 1280, height: 576 },
      { file: 'alley_bg.png', width: 1280, height: 576 },
      { file: 'marina_bg.png', width: 1280, height: 576 },
      { file: 'forest_bg.png', width: 1280, height: 576 },
    ];

    for (const map of expectedMaps) {
      const fullPath = path.join(mapsDir, map.file);
      expect(fs.existsSync(fullPath), `${map.file} should exist`).toBe(true);
      expect(readPngDimensions(fullPath)).toEqual({ width: map.width, height: map.height });
    }
  });

  it('provides updated tilesets matching the art standards for all 8 locations', () => {
    const expectedTiles = [
      'apartment.png',
      'city.png',
      'zabka.png',
      'garage.png',
      'pub.png',
      'alley.png',
      'marina.png',
      'forest.png',
    ];

    for (const tile of expectedTiles) {
      const fullPath = path.join(tilesDir, tile);
      expect(fs.existsSync(fullPath), `${tile} tileset should exist`).toBe(true);
    }
  });

  it('includes all 8 HD map keys in manifest.json', () => {
    const images = (manifest as any).images;
    expect(images['map_apartment_bg']).toBe('assets/maps/apartment_bg.png');
    expect(images['map_city_bg']).toBe('assets/maps/city_bg.png');
    expect(images['map_zabka_bg']).toBe('assets/maps/zabka_bg.png');
    expect(images['map_garage_bg']).toBe('assets/maps/garage_bg.png');
    expect(images['map_pub_bg']).toBe('assets/maps/pub_bg.png');
    expect(images['map_alley_bg']).toBe('assets/maps/alley_bg.png');
    expect(images['map_marina_bg']).toBe('assets/maps/marina_bg.png');
    expect(images['map_forest_bg']).toBe('assets/maps/forest_bg.png');
  });

  it('includes all 8 tileset keys in manifest.json', () => {
    const images = (manifest as any).images;
    expect(images['tiles_apartment']).toBe('assets/tiles/apartment.png');
    expect(images['tiles_city']).toBe('assets/tiles/city.png');
    expect(images['tiles_zabka']).toBe('assets/tiles/zabka.png');
    expect(images['tiles_garage']).toBe('assets/tiles/garage.png');
    expect(images['tiles_pub']).toBe('assets/tiles/pub.png');
    expect(images['tiles_alley']).toBe('assets/tiles/alley.png');
    expect(images['tiles_marina']).toBe('assets/tiles/marina.png');
    expect(images['tiles_forest']).toBe('assets/tiles/forest.png');
  });

  it('preserves initial spawn coordinates in apartment', () => {
    const state = newGame('danny');
    expect(state.mapId).toBe('apartment');
    expect(state.x).toBe(4);
    expect(state.y).toBe(5);
  });
});
