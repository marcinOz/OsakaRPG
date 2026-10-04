import { describe, it, expect } from 'vitest';
import { resolveBattleConfig, getEnemySpriteSize } from '@/systems/EncounterFactory';
import { ENCOUNTERS } from '@/content/encounters';
import { newGame } from '@/systems/GameState';
import { ENEMIES } from '@/content/enemies';

describe('EncounterFactory & BattleParams', () => {
  it('normalizes battle config with sensible defaults when state is omitted', () => {
    const config = resolveBattleConfig({
      enemies: ['bolKregoslupa'],
    });

    expect(config.state).toBeDefined();
    expect(config.state.leader).toBe('danny');
    expect(config.bg).toBe('battle_apartment_bg');
    expect(config.music).toBe('ch01_battle');
    expect(config.victoryMusic).toBe('victory');
    expect(config.advantage).toBe('normal');
    expect(config.canFlee).toBe(false);
    expect(config.allowDefeat).toBe(false);
    expect(config.returnScene).toBe('World');
    expect(config.heroes.length).toBe(config.state.party.length);
    expect(config.enemies.length).toBe(1);
    expect(config.enemies[0].defId).toBe('bolKregoslupa');
  });

  it('correctly sets initial ATB for normal, preemptive, and ambush advantages', () => {
    const state = newGame('danny');
    state.party = ['danny', 'alior'];

    // 1. Normal: first hero ready (100), second at 70, enemies at 25
    const normalConfig = resolveBattleConfig({
      state,
      enemies: ['bolKregoslupa', 'slacki'],
      advantage: 'normal',
    });
    expect(normalConfig.heroes[0].atb).toBe(100);
    expect(normalConfig.heroes[1].atb).toBe(70);
    expect(normalConfig.enemies[0].atb).toBe(70);
    expect(normalConfig.enemies[1].atb).toBe(70);

    // 2. Preemptive Strike: all heroes ready (100), enemies flatfooted (0)
    const preemptiveConfig = resolveBattleConfig({
      state,
      enemies: ['bolKregoslupa'],
      advantage: 'preemptive',
    });
    expect(preemptiveConfig.heroes[0].atb).toBe(100);
    expect(preemptiveConfig.heroes[1].atb).toBe(100);
    expect(preemptiveConfig.enemies[0].atb).toBe(0);

    // 3. Ambush: enemies ready (100), heroes caught off guard (0)
    const ambushConfig = resolveBattleConfig({
      state,
      enemies: ['bolKregoslupa'],
      advantage: 'ambush',
    });
    expect(ambushConfig.heroes[0].atb).toBe(0);
    expect(ambushConfig.heroes[1].atb).toBe(0);
    expect(ambushConfig.enemies[0].atb).toBe(100);
  });

  it('supports explicit numeric ATB overrides', () => {
    const config = resolveBattleConfig({
      enemies: ['bolKregoslupa', 'slacki'],
      heroAtbStart: 50,
      enemyAtbStart: [15, 85],
    });
    expect(config.heroes[0].atb).toBe(50);
    expect(config.enemies[0].atb).toBe(15);
    expect(config.enemies[1].atb).toBe(85);
  });

  it('supports flexible hero party overrides (solo duel, custom level/stats)', () => {
    const state = newGame('danny');
    state.party = ['danny', 'alior', 'lisu'];

    // Solo fight with only Lisu
    const soloConfig = resolveBattleConfig({
      state,
      heroes: ['lisu'],
      enemies: ['bolKregoslupa'],
    });
    expect(soloConfig.heroes.length).toBe(1);
    expect(soloConfig.heroes[0].defId).toBe('lisu');

    // Custom HeroSpec with overridden level and skills
    const customConfig = resolveBattleConfig({
      state,
      heroes: [
        {
          id: 'barti',
          level: 10,
          hp: 300,
          skills: ['bassBlast'],
        },
      ],
      enemies: ['bolKregoslupa'],
    });
    expect(customConfig.heroes.length).toBe(1);
    expect(customConfig.heroes[0].defId).toBe('barti');
    expect(customConfig.heroes[0].level).toBe(10);
    expect(customConfig.heroes[0].hp).toBe(300);
    expect(customConfig.heroes[0].skills).toEqual(['bassBlast']);
  });

  it('supports polymorphic enemy specifications with level/stat overrides', () => {
    const config = resolveBattleConfig({
      enemies: [
        'bolKregoslupa',
        {
          id: 'kark',
          name: 'Super Kark',
          level: 15,
          stats: { hp: 999, atk: 50 },
          spriteSize: 180,
          boss: true,
        },
      ],
    });

    expect(config.enemies.length).toBe(2);
    // Standard enemy
    expect(config.enemies[0].defId).toBe('bolKregoslupa');
    expect(config.enemies[0].name).toBe(ENEMIES.bolKregoslupa.name);

    // Overridden enemy
    expect(config.enemies[1].defId).toBe('kark');
    expect(config.enemies[1].name).toBe('Super Kark');
    expect(config.enemies[1].level).toBe(15);
    expect(config.enemies[1].max.hp).toBe(999);
    expect(config.enemies[1].max.atk).toBe(50);
    expect(config.enemies[1].boss).toBe(true);
    expect(getEnemySpriteSize(config.enemies[1])).toBe(180);
  });

  it('calculates dynamic enemy sprite sizes correctly', () => {
    const config = resolveBattleConfig({
      enemies: ['bolKregoslupa', 'panJanusz', 'autoTuneHipster'],
    });

    // Small enemies = 96
    expect(getEnemySpriteSize(config.enemies[0])).toBe(96);
    // Boss / Large enemies = 144
    expect(getEnemySpriteSize(config.enemies[1])).toBe(144);
    // Medium enemies = 128
    expect(getEnemySpriteSize(config.enemies[2])).toBe(128);
  });

  it('configures defeat flow, fleeing, and reward tuning', () => {
    const config = resolveBattleConfig({
      enemies: ['bolKregoslupa'],
      canFlee: true,
      fleeSuccessChance: 0.9,
      allowDefeat: true,
      defeatScene: 'CustomDefeatScene',
      returnScene: 'Campfire',
      returnSceneData: { storyCheckpoint: 'ch3_start' },
      rewards: {
        xpMultiplier: 2.0,
        bonusXp: 100,
        bonusItems: ['kawa'],
        grantProgression: false,
      },
    });

    expect(config.canFlee).toBe(true);
    expect(config.fleeSuccessChance).toBe(0.9);
    expect(config.allowDefeat).toBe(true);
    expect(config.defeatScene).toBe('CustomDefeatScene');
    expect(config.returnScene).toBe('Campfire');
    expect(config.returnSceneData).toEqual({ storyCheckpoint: 'ch3_start' });
    expect(config.rewards.xpMultiplier).toBe(2.0);
    expect(config.rewards.bonusXp).toBe(100);
    expect(config.rewards.bonusItems).toEqual(['kawa']);
    expect(config.rewards.grantProgression).toBe(false);
  });

  it('validates all campaign encounters in ENCOUNTERS registry', () => {
    const registryKeys = Object.keys(ENCOUNTERS);
    expect(registryKeys).toContain('spineAmbush');
    expect(registryKeys).toContain('slackInvasion');
    expect(registryKeys).toContain('sasiadBoss');
    expect(registryKeys).toContain('pubHipsters');
    expect(registryKeys).toContain('karkAmbush');
    expect(registryKeys).toContain('finalBossRift');

    // Verify Final Boss Rift has correct theme, background, and return scene
    const finalBoss = ENCOUNTERS.finalBossRift;
    expect(finalBoss.music).toBe('ch09_finalboss');
    expect(finalBoss.bg).toBe('battle_rift_bg');
    expect(finalBoss.returnScene).toBe('Outro');
    expect(finalBoss.enemies).toEqual(['panJanusz', 'kredyt', 'audyt', 'rwaKulszowa']);

    // Ensure all registry entries can be normalized without errors
    for (const key of registryKeys) {
      const resolved = resolveBattleConfig(ENCOUNTERS[key]);
      expect(resolved.enemies.length).toBeGreaterThan(0);
      expect(resolved.bg).toBeDefined();
      expect(resolved.music).toBeDefined();
    }
  });
});
