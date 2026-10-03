import type { HeroId, StatusEffectDef } from '@/types';
import { HEROES } from '@/content/heroes';
import { WORLD_STATUSES } from '@/content/statuses';
import { Combatant } from './Combatant';
import { heroStatsAtLevel, levelForXp } from './Stats';
import { makeHeroCombatant, BattleEngine } from './BattleEngine';

export interface HeroState {
  level: number;
  xp: number;
  hp: number;
  mp: number;
}

export interface GameData {
  version: number;
  leader: HeroId;
  party: HeroId[];
  roster: Record<HeroId, HeroState>;
  inventory: Record<string, number>;
  chapter: number;
  mapId: string;
  x: number;
  y: number;
  facing: 'down' | 'up' | 'left' | 'right';
  flags: Record<string, boolean | number | string>;
  worldStatuses: string[];
  playtime: number;
  timestamp: number;
}

export function newGame(leader: HeroId): GameData {
  const roster = {} as Record<HeroId, HeroState>;
  for (const [id, def] of Object.entries(HEROES)) {
    const stats = heroStatsAtLevel(def, 1);
    roster[id as HeroId] = {
      level: 1,
      xp: 0,
      hp: stats.hp,
      mp: stats.mp,
    };
  }

  return {
    version: 1,
    leader,
    party: [leader],
    roster,
    inventory: { kawa: 1, piwo: 1 },
    chapter: 1,
    mapId: 'apartment',
    x: 4,
    y: 5,
    facing: 'down',
    flags: {},
    worldStatuses: ['kacGigant'], // Starts with Chapter 1 hangover
    playtime: 0,
    timestamp: Date.now(),
  };
}

export function addToParty(state: GameData, heroId: HeroId): boolean {
  if (state.party.includes(heroId)) return false;
  state.party.push(heroId);
  return true;
}

export function grantXp(
  state: GameData,
  totalXp: number
): { heroId: HeroId; oldLevel: number; newLevel: number }[] {
  const levelUps: { heroId: HeroId; oldLevel: number; newLevel: number }[] = [];
  for (const hid of state.party) {
    const member = state.roster[hid];
    if (!member) continue;
    const oldLevel = member.level;
    member.xp += totalXp;
    const newLevel = levelForXp(member.xp);
    if (newLevel > oldLevel) {
      member.level = newLevel;
      const def = HEROES[hid];
      const newStats = heroStatsAtLevel(def, newLevel);
      member.hp = newStats.hp; // Full restore on level up
      member.mp = newStats.mp;
      levelUps.push({ heroId: hid, oldLevel, newLevel });
    }
  }
  return levelUps;
}

export function hasFlag(state: GameData, key: string): boolean {
  return !!state.flags[key];
}

export function setFlag(state: GameData, key: string, val: boolean | number | string = true): void {
  state.flags[key] = val;
}

export function applyWorldStatus(state: GameData, id: string): void {
  if (!state.worldStatuses.includes(id)) {
    state.worldStatuses.push(id);
  }
}

export function removeWorldStatus(state: GameData, id: string): void {
  state.worldStatuses = state.worldStatuses.filter((s) => s !== id);
}

export function walkSpeedMultiplier(state: GameData): number {
  let mult = 1.0;
  for (const sid of state.worldStatuses) {
    const ws = WORLD_STATUSES[sid];
    if (!ws) continue;
    for (const eff of ws.effects) {
      if (eff.kind === 'walkSpeed') mult *= eff.value;
    }
  }
  return mult;
}

export function partyEffects(state: GameData): StatusEffectDef[] {
  const effects: StatusEffectDef[] = [];
  // Leader bonus
  const leaderDef = HEROES[state.leader];
  if (leaderDef?.leaderBonus?.effect) {
    effects.push(leaderDef.leaderBonus.effect);
  }
  // Combat effects from active world statuses
  for (const sid of state.worldStatuses) {
    const ws = WORLD_STATUSES[sid];
    if (!ws) continue;
    for (const eff of ws.effects) {
      if (eff.kind !== 'walkSpeed') {
        effects.push(eff);
      }
    }
  }
  return effects;
}

export function toBattleHeroes(state: GameData): Combatant[] {
  return state.party.map((hid) => {
    const def = HEROES[hid];
    const member = state.roster[hid];
    return makeHeroCombatant(def, member.level, member.hp, member.mp);
  });
}

export function applyBattleResult(state: GameData, engine: BattleEngine): void {
  for (const combatant of engine.heroes) {
    const hid = combatant.defId as HeroId;
    const member = state.roster[hid];
    if (member) {
      member.hp = Math.max(1, combatant.hp); // At least 1 HP survives after victory
      member.mp = combatant.mp;
    }
  }
}
