import type {
  BattleAdvantage,
  BattleParams,
  BattleRewardConfig,
  EnemyParam,
  EnemySpec,
  GameData,
  HeroId,
  HeroParam,
  HeroSpec,
  StatusEffectDef,
} from '@/types';
import { HEROES } from '@/content/heroes';
import { ENEMIES } from '@/content/enemies';
import { Combatant } from './Combatant';
import { makeHeroCombatant, makeEnemyCombatant } from './BattleEngine';
import { toBattleHeroes, newGame, partyEffects } from './GameState';

export interface ResolvedBattleConfig {
  state: GameData;
  bg: string;
  music: string;
  victoryMusic: string;
  battleTitle?: string;
  heroes: Combatant[];
  enemies: Combatant[];
  advantage: BattleAdvantage;
  canFlee: boolean;
  fleeSuccessChance: number;
  allowDefeat: boolean;
  defeatScene: string;
  returnScene: string;
  returnSceneData: Record<string, any>;
  partyEffects: StatusEffectDef[];
  enemyEffects: StatusEffectDef[];
  rewards: Required<BattleRewardConfig>;
}

/**
 * Calculates visual size for an enemy sprite.
 */
export function getEnemySpriteSize(combatant: Combatant | string | undefined): number {
  if (!combatant) return 96;
  if (typeof combatant === 'string') {
    if (combatant.includes('panJanusz') || combatant.includes('kredyt') || combatant.includes('audyt')) {
      return 144;
    }
    if (combatant.includes('bolKregoslupa') || combatant.includes('slacki')) {
      return 96;
    }
    return 128;
  }
  if (combatant.spriteSize) {
    return combatant.spriteSize;
  }
  const spr = combatant.sprite ?? '';
  if (combatant.boss || spr.includes('panJanusz') || spr.includes('kredyt') || spr.includes('audyt')) {
    return 144;
  }
  if (spr.includes('bolKregoslupa') || spr.includes('slacki')) {
    return 96;
  }
  return 128;
}

/**
 * Builds hero combatants from flexible specifications, falling back to state.party.
 */
export function buildHeroCombatants(heroes: HeroParam[] | undefined, state: GameData): Combatant[] {
  if (!heroes || heroes.length === 0) {
    return toBattleHeroes(state);
  }

  return heroes.map((param) => {
    // If it is already a Combatant object
    if (typeof param === 'object' && 'uid' in param && 'side' in param) {
      return param as Combatant;
    }

    // If it is a string HeroId
    if (typeof param === 'string') {
      const hid = param as HeroId;
      const def = HEROES[hid];
      const member = state.roster[hid] ?? { level: 1, xp: 0, hp: def.base.hp, mp: def.base.mp };
      return makeHeroCombatant(def, member.level, member.hp, member.mp);
    }

    // If it is a HeroSpec object
    const spec = param as HeroSpec;
    const def = HEROES[spec.id];
    const member = state.roster[spec.id] ?? { level: 1, xp: 0, hp: def.base.hp, mp: def.base.mp };
    const level = spec.level ?? member.level;
    const combatant = makeHeroCombatant(def, level, member.hp, member.mp);

    if (spec.stats) {
      combatant.max = { ...combatant.max, ...spec.stats };
    }
    if (spec.hp !== undefined) {
      if (spec.hp > combatant.max.hp) {
        combatant.max.hp = spec.hp;
      }
      combatant.hp = spec.hp;
      combatant.alive = spec.hp > 0;
    }
    if (spec.mp !== undefined) {
      if (spec.mp > combatant.max.mp) {
        combatant.max.mp = spec.mp;
      }
      combatant.mp = spec.mp;
    }
    if (spec.skills) {
      combatant.skills = [...spec.skills];
    }
    if (spec.atb !== undefined) {
      combatant.atb = Math.max(0, Math.min(100, spec.atb));
    }
    return combatant;
  });
}

/**
 * Builds enemy combatants from flexible specifications (string ID or EnemySpec).
 */
export function buildEnemyCombatants(enemies: EnemyParam[]): Combatant[] {
  if (!enemies || enemies.length === 0) {
    return [makeEnemyCombatant(ENEMIES.bolKregoslupa, 0)];
  }

  return enemies.map((param, idx) => {
    if (typeof param === 'string') {
      const def = (ENEMIES as Record<string, any>)[param] ?? ENEMIES.bolKregoslupa;
      return makeEnemyCombatant(def, idx);
    }

    const spec = param as EnemySpec;
    const baseDef = (ENEMIES as Record<string, any>)[spec.id] ?? ENEMIES.bolKregoslupa;

    const mergedDef = {
      ...baseDef,
      id: spec.id,
      name: spec.name ?? baseDef.name,
      level: spec.level ?? baseDef.level,
      stats: {
        ...baseDef.stats,
        ...(spec.stats ?? {}),
      },
      sprite: spec.sprite ?? baseDef.sprite,
      boss: spec.boss !== undefined ? spec.boss : baseDef.boss,
    };

    const combatant = makeEnemyCombatant(mergedDef, idx);
    if (spec.hp !== undefined) {
      combatant.hp = Math.min(spec.hp, combatant.max.hp);
    }
    if (spec.mp !== undefined) {
      combatant.mp = Math.min(spec.mp, combatant.max.mp);
    }
    if (spec.atb !== undefined) {
      combatant.atb = Math.max(0, Math.min(100, spec.atb));
    }
    if (spec.spriteSize !== undefined) {
      combatant.spriteSize = spec.spriteSize;
    }

    return combatant;
  });
}

/**
 * Applies initial ATB gauges to heroes and enemies based on advantage preset and manual overrides.
 */
export function applyStartingAtb(
  heroes: Combatant[],
  enemies: Combatant[],
  opts: {
    advantage: BattleAdvantage;
    heroAtbStart?: number | number[] | ((idx: number) => number);
    enemyAtbStart?: number | number[] | ((idx: number) => number);
  }
): void {
  // 1. Semantic Presets
  if (opts.advantage === 'preemptive') {
    heroes.forEach((h) => (h.atb = 100));
    enemies.forEach((e) => (e.atb = 0));
  } else if (opts.advantage === 'ambush') {
    heroes.forEach((h) => (h.atb = 0));
    enemies.forEach((e) => (e.atb = 100));
  } else {
    // Normal preset: party leader / first hero starts full (100) for immediate command menu, others at 70, enemies at 70
    heroes.forEach((h, idx) => {
      h.atb = idx === 0 ? 100 : 70;
    });
    enemies.forEach((e) => {
      e.atb = 70;
    });
  }

  // 2. Explicit Hero ATB Overrides (if specified)
  if (opts.heroAtbStart !== undefined) {
    heroes.forEach((h, idx) => {
      if (typeof opts.heroAtbStart === 'number') {
        h.atb = opts.heroAtbStart;
      } else if (Array.isArray(opts.heroAtbStart)) {
        h.atb = opts.heroAtbStart[idx] ?? h.atb;
      } else if (typeof opts.heroAtbStart === 'function') {
        h.atb = opts.heroAtbStart(idx);
      }
    });
  }

  // 3. Explicit Enemy ATB Overrides (if specified)
  if (opts.enemyAtbStart !== undefined) {
    enemies.forEach((e, idx) => {
      if (typeof opts.enemyAtbStart === 'number') {
        e.atb = opts.enemyAtbStart;
      } else if (Array.isArray(opts.enemyAtbStart)) {
        e.atb = opts.enemyAtbStart[idx] ?? e.atb;
      } else if (typeof opts.enemyAtbStart === 'function') {
        e.atb = opts.enemyAtbStart(idx);
      }
    });
  }
}

/**
 * Normalizes any BattleParams into a complete, validated ResolvedBattleConfig.
 */
export function resolveBattleConfig(params: BattleParams): ResolvedBattleConfig {
  const state = params.state ?? newGame('danny');
  const advantage: BattleAdvantage = params.advantage ?? 'normal';

  const heroes = buildHeroCombatants(params.heroes, state);
  const enemies = buildEnemyCombatants(params.enemies);

  applyStartingAtb(heroes, enemies, {
    advantage,
    heroAtbStart: params.heroAtbStart,
    enemyAtbStart: params.enemyAtbStart,
  });

  const resolvedPartyEffects: StatusEffectDef[] = [
    ...(params.partyEffects ?? (params.state ? partyEffects(params.state) : [])),
  ];

  const resolvedEnemyEffects: StatusEffectDef[] = [
    ...(params.enemyEffects ?? []),
  ];

  const rewards: Required<BattleRewardConfig> = {
    xpMultiplier: params.rewards?.xpMultiplier ?? 1.0,
    bonusXp: params.rewards?.bonusXp ?? 0,
    bonusItems: params.rewards?.bonusItems ? [...params.rewards.bonusItems] : [],
    grantProgression: params.rewards?.grantProgression ?? true,
  };

  return {
    state,
    bg: params.bg ?? 'battle_apartment_bg',
    music: params.music ?? 'ch01_battle',
    victoryMusic: params.victoryMusic ?? 'victory',
    battleTitle: params.battleTitle,
    heroes,
    enemies,
    advantage,
    canFlee: params.canFlee ?? false,
    fleeSuccessChance: params.fleeSuccessChance ?? 0.75,
    allowDefeat: params.allowDefeat ?? false,
    defeatScene: params.defeatScene ?? 'Title',
    returnScene: params.returnScene ?? 'World',
    returnSceneData: params.returnSceneData ?? {},
    partyEffects: resolvedPartyEffects,
    enemyEffects: resolvedEnemyEffects,
    rewards,
  };
}
