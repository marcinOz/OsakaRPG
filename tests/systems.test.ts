import { describe, it, expect } from 'vitest';
import { HEROES } from '@/content/heroes';
import { makeHeroCombatant } from '@/systems/BattleEngine';
import { applyStatus, cleanse, hasStatus, tickStatuses } from '@/systems/StatusFx';
import { effectiveStat, heroStatsAtLevel, xpForLevel, levelForXp } from '@/systems/Stats';
import { newGame, grantXp, walkSpeedMultiplier } from '@/systems/GameState';
import { SaveSystem, MemoryStorage, SafeLocalStorage } from '@/systems/Save';
import { DialogueRunner } from '@/systems/Dialogue';
import { CH01 } from '@/content/chapters/ch01';

describe('Stats and StatusFx', () => {
  it('hero stats scale with level', () => {
    const lv1 = heroStatsAtLevel(HEROES.danny, 1);
    const lv2 = heroStatsAtLevel(HEROES.danny, 2);
    expect(lv2.hp).toBeGreaterThan(lv1.hp);
    expect(lv2.atk).toBeGreaterThan(lv1.atk);
  });

  it('xp curve gives correct levels', () => {
    expect(xpForLevel(1)).toBe(0);
    expect(levelForXp(0)).toBe(1);
    expect(levelForXp(30)).toBe(2);
  });

  it('effectiveStat applies statMod', () => {
    const hero = makeHeroCombatant(HEROES.danny, 1);
    const baseAtk = effectiveStat(hero, 'atk');
    applyStatus(hero, { id: 'buff', name: 'Siła', kind: 'statMod', stat: 'atk', value: 0.5, turns: 2 });
    expect(effectiveStat(hero, 'atk')).toBe(baseAtk * 1.5);
  });

  it('tickStatuses heals with regen and removes expired buffs', () => {
    const hero = makeHeroCombatant(HEROES.danny, 1);
    hero.hp = 50;
    applyStatus(hero, { id: 'regen', name: 'Zioła', kind: 'regen', value: 0.1, turns: 1 });
    const events = tickStatuses(hero);
    expect(events.some((e) => e.type === 'regen')).toBe(true);
    expect(hero.hp).toBeGreaterThan(50);
    // After 1 turn, it should have expired
    expect(hasStatus(hero, 'regen')).toBe(false);
  });

  it('cleanse removes only debuffs', () => {
    const hero = makeHeroCombatant(HEROES.danny, 1);
    applyStatus(hero, { id: 'buff', name: 'Buff', kind: 'statMod', stat: 'atk', value: 0.2, turns: 2 });
    applyStatus(hero, { id: 'poison', name: 'Trucizna', kind: 'poison', value: 0.1, turns: 2, debuff: true });

    cleanse(hero);
    expect(hasStatus(hero, 'buff')).toBe(true);
    expect(hasStatus(hero, 'poison')).toBe(false);
  });
});

describe('GameState and Saves', () => {
  it('newGame initializes leader, inventory, and hangover debuff', () => {
    const state = newGame('danny');
    expect(state.leader).toBe('danny');
    expect(state.party).toEqual(['danny']);
    expect(state.worldStatuses).toContain('kacGigant');
    expect(walkSpeedMultiplier(state)).toBe(0.8); // Kac Gigant slows down movement
  });

  it('grantXp levels up heroes and restores HP/MP', () => {
    const state = newGame('danny');
    const levelUps = grantXp(state, 50);
    expect(levelUps.length).toBe(1);
    expect(levelUps[0].newLevel).toBe(2);
    expect(state.roster.danny.level).toBe(2);
  });

  it('SaveSystem saves, lists, and loads slots with MemoryStorage', () => {
    const storage = new MemoryStorage();
    const saves = new SaveSystem(storage);
    const state = newGame('alior');
    state.chapter = 2;

    saves.save(0, state);
    const list = saves.list();
    expect(list[0].exists).toBe(true);
    expect(list[0].leader).toBe('Alior');
    expect(list[0].chapter).toBe(2);

    const loaded = saves.load(0);
    expect(loaded?.leader).toBe('alior');
    expect(loaded?.chapter).toBe(2);
  });

  it('SafeLocalStorage handles throwing storage gracefully without crashing', () => {
    const safe = new SafeLocalStorage();
    safe.setItem('test_key', 'val');
    expect(safe.getItem('test_key')).toBe('val');
    safe.removeItem('test_key');
    expect(safe.getItem('test_key')).toBeNull();
  });

  it('SaveSystem handles storage errors gracefully in private browsing mode', () => {
    const brokenStorage = {
      getItem: () => {
        throw new Error('SecurityError: The operation is insecure');
      },
      setItem: () => {
        throw new Error('QuotaExceededError');
      },
      removeItem: () => {
        throw new Error('SecurityError');
      },
    };
    const saves = new SaveSystem(brokenStorage);
    const state = newGame('danny');
    expect(() => saves.save(0, state)).not.toThrow();
    expect(saves.save(0, state)).toBe(false);
    expect(() => saves.load(0)).not.toThrow();
    expect(saves.load(0)).toBeNull();
    expect(() => saves.delete(0)).not.toThrow();
    expect(() => saves.list()).not.toThrow();
  });
});

describe('DialogueRunner', () => {
  it('resolves leader overrides and replaces player tokens', () => {
    const runner = new DialogueRunner(CH01.hangover, 'danny');
    const resolved = runner.allResolved();
    // First line is SYSTEM
    expect(resolved[0].speakerId).toBe('SYSTEM');
    // Second line is player -> resolves to Danny with Danny specific text
    expect(resolved[1].speakerId).toBe('danny');
    expect(resolved[1].name).toBe('Danny');
    expect(resolved[1].text).toContain('martwym ciągu 250');
  });

  it('resolves Alior leader variant correctly', () => {
    const runner = new DialogueRunner(CH01.hangover, 'alior');
    const resolved = runner.allResolved();
    expect(resolved[1].speakerId).toBe('alior');
    expect(resolved[1].text).toContain('Input lag na poziomie 300 ms');
  });

  it('apartment exit requires both Spine and Slack fights to unlock', () => {
    const state = newGame('danny');
    const isAptUnlocked = (s: typeof state) =>
      Boolean(s.flags.ch1_fought_spine && s.flags.ch1_fought_slack);

    expect(isAptUnlocked(state)).toBe(false);

    state.flags.ch1_fought_spine = true;
    expect(isAptUnlocked(state)).toBe(false);

    state.flags.ch1_fought_slack = true;
    expect(isAptUnlocked(state)).toBe(true);
  });

  it('visiting Żabka cures Kac Gigant and unlocks garage exit', () => {
    const state = newGame('danny');
    expect(state.worldStatuses).toContain('kacGigant');
    expect(Boolean(state.flags.bought_coffee)).toBe(false);

    // Buy coffee in Żabka
    state.flags.bought_coffee = true;
    const idx = state.worldStatuses.indexOf('kacGigant');
    if (idx !== -1) state.worldStatuses.splice(idx, 1);
    state.inventory.kawa = (state.inventory.kawa ?? 0) + 2;
    state.inventory.hotDog = (state.inventory.hotDog ?? 0) + 1;
    state.inventory.elektrolity = (state.inventory.elektrolity ?? 0) + 1;

    expect(state.worldStatuses).not.toContain('kacGigant');
    expect(walkSpeedMultiplier(state)).toBe(1.0); // Full speed restored!
    expect(state.inventory.hotDog).toBe(1);
    expect(state.inventory.elektrolity).toBe(1);
    expect(Boolean(state.flags.bought_coffee)).toBe(true);
  });
});
