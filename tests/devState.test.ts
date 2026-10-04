import { describe, it, expect } from 'vitest';
import {
  createDevChapterState,
  CHAPTER_DEV_REGISTRY,
  ALL_HERO_IDS,
} from '@/systems/DevState';

describe('DevState System (Headless)', () => {
  it('has valid definitions for all 10 chapters', () => {
    expect(CHAPTER_DEV_REGISTRY.length).toBe(10);
    for (let i = 1; i <= 10; i++) {
      const def = CHAPTER_DEV_REGISTRY.find((c) => c.id === i);
      expect(def).toBeDefined();
      expect(def?.title).toContain(`Rozdział ${i}`);
      expect(def?.recommendedLevel).toBe(i);
    }
  });

  it('generates valid state for all 6 heroes across all 10 chapters', () => {
    for (const heroId of ALL_HERO_IDS) {
      for (let ch = 1; ch <= 10; ch++) {
        const { state, targetScene } = createDevChapterState(heroId, ch);

        expect(state.leader).toBe(heroId);
        expect(state.party[0]).toBe(heroId);
        expect(state.chapter).toBe(ch);
        expect(targetScene).toBeDefined();

        // Roster stats
        for (const pid of state.party) {
          const heroState = state.roster[pid];
          expect(heroState).toBeDefined();
          expect(heroState.level).toBe(ch);
          expect(heroState.hp).toBeGreaterThan(0);
          expect(heroState.mp).toBeGreaterThan(0);
        }
      }
    }
  });

  it('scales party members progressively according to chapter storyline', () => {
    // Ch 1: Only leader
    const ch1 = createDevChapterState('danny', 1);
    expect(ch1.state.party).toEqual(['danny']);
    expect(ch1.state.worldStatuses).toContain('kacGigant');
    expect(ch1.targetScene).toBe('World');
    expect(ch1.state.mapId).toBe('apartment');

    // Ch 3: Danny + Alior recruited
    const ch3Alior = createDevChapterState('alior', 3);
    // Leader is Alior, Danny is recruited
    expect(ch3Alior.state.party).toEqual(['alior', 'danny']);
    expect(ch3Alior.targetScene).toBe('World');
    expect(ch3Alior.state.mapId).toBe('pub');

    const ch3Barti = createDevChapterState('barti', 3);
    // Barti as leader, Danny and Alior recruited
    expect(ch3Barti.state.party).toEqual(['barti', 'danny', 'alior']);

    // Ch 4: Barti recruited
    const ch4 = createDevChapterState('danny', 4);
    expect(ch4.state.party).toEqual(['danny', 'alior', 'barti']);
    expect(ch4.state.mapId).toBe('alley');

    // Ch 5: Lisu recruited
    const ch5 = createDevChapterState('danny', 5);
    expect(ch5.state.party).toEqual(['danny', 'alior', 'barti', 'lisu']);
    expect(ch5.state.mapId).toBe('marina');

    // Ch 6: Łuki recruited
    const ch6 = createDevChapterState('danny', 6);
    expect(ch6.state.party).toEqual(['danny', 'alior', 'barti', 'lisu', 'luki']);
    expect(ch6.state.mapId).toBe('forest');

    // Ch 7+: All 6 heroes recruited
    const ch7 = createDevChapterState('oziem', 7);
    expect(ch7.state.party.length).toBe(6);
    expect(ch7.targetScene).toBe('Campfire');

    // Ch 8: Campfire with startAtJanusz = true
    const ch8 = createDevChapterState('lisu', 8);
    expect(ch8.targetScene).toBe('Campfire');
    expect(ch8.startAtJanusz).toBe(true);

    // Ch 9: BattleScene launching finalBossRift
    const ch9 = createDevChapterState('danny', 9);
    expect(ch9.targetScene).toBe('Battle');
    expect(ch9.battleEncounterId).toBe('finalBossRift');

    // Ch 10: OutroScene
    const ch10 = createDevChapterState('luki', 10);
    expect(ch10.targetScene).toBe('Outro');
  });

  it('sets required progression flags for later chapters', () => {
    const ch6 = createDevChapterState('danny', 6);
    expect(ch6.state.flags.ch1_woke_up).toBe(true);
    expect(ch6.state.flags.bought_coffee).toBe(true);
    expect(ch6.state.flags.fought_sasiad).toBe(true);
    expect(ch6.state.flags.fought_hipsters).toBe(true);
    expect(ch6.state.flags.fought_kark).toBe(true);
    expect(ch6.state.flags.luki_saved).toBe(true);
  });
});
