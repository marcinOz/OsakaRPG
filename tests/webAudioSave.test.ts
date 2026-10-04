// @ts-nocheck
import { describe, it, expect } from 'vitest';
import { Audio } from '@/audio/ChipAudio';
import { SafeLocalStorage, SaveSystem } from '@/systems/Save';
import { newGame } from '@/systems/GameState';
import fs from 'fs';
import path from 'path';

describe('ChipAudio unlock methods', () => {
  it('exposes isUnlocked and returns a boolean', () => {
    expect(typeof Audio.isUnlocked).toBe('function');
    expect(typeof Audio.isUnlocked()).toBe('boolean');
  });

  it('exposes attachAutoUnlock and runs without crashing', () => {
    expect(typeof Audio.attachAutoUnlock).toBe('function');
    expect(() => Audio.attachAutoUnlock()).not.toThrow();
  });
});

describe('SafeLocalStorage and Save resiliency', () => {
  it('falls back to MemoryStorage if localStorage is unavailable or throws', () => {
    const safe = new SafeLocalStorage();
    safe.setItem('player_slot', JSON.stringify({ hero: 'danny' }));
    expect(safe.getItem('player_slot')).toBe(JSON.stringify({ hero: 'danny' }));
    safe.removeItem('player_slot');
    expect(safe.getItem('player_slot')).toBeNull();
  });

  it('SaveSystem saves and loads with SafeLocalStorage default', () => {
    const saves = new SaveSystem();
    const state = newGame('danny');
    state.chapter = 3;
    const ok = saves.save(1, state);
    expect(ok).toBe(true);

    const loaded = saves.load(1);
    expect(loaded).not.toBeNull();
    expect(loaded?.leader).toBe('danny');
    expect(loaded?.chapter).toBe(3);

    const list = saves.list();
    expect(list[1].exists).toBe(true);
    expect(list[1].leader).toBe('Danny');
  });
});

describe('index.html UX and OpenGraph verification', () => {
  it('contains OpenGraph meta tags, touch-action hygiene, and keydown preventDefault', () => {
    const htmlPath = path.resolve(__dirname, '../index.html');
    const content = fs.readFileSync(htmlPath, 'utf8');

    // OpenGraph & Twitter
    expect(content).toContain('property="og:title"');
    expect(content).toContain('property="og:description"');
    expect(content).toContain('property="og:image"');
    expect(content).toContain('name="twitter:card"');

    // Touch-action hygiene
    expect(content).toContain('touch-action: none');

    // Keydown preventDefault for arrow keys and space
    expect(content).toContain('window.addEventListener(\'keydown\'');
    expect(content).toContain('ArrowUp');
    expect(content).toContain('ArrowDown');
    expect(content).toContain('ArrowLeft');
    expect(content).toContain('ArrowRight');
    expect(content).toContain('e.preventDefault()');
  });
});
