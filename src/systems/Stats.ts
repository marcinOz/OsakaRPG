import type { HeroDef, StatKey, Stats } from '@/types';
import type { Combatant } from './Combatant';

export const STAT_KEYS: StatKey[] = ['hp', 'mp', 'atk', 'def', 'mag', 'spd', 'lck'];
export const MAX_LEVEL = 50;

/** Base stats + per-level growth (level 1 = base). Values are floored. */
export function heroStatsAtLevel(def: HeroDef, level: number): Stats {
  const lv = Math.max(1, Math.min(MAX_LEVEL, Math.floor(level)));
  const out = {} as Stats;
  for (const k of STAT_KEYS) {
    out[k] = Math.floor(def.base[k] + (def.growth[k] ?? 0) * (lv - 1));
  }
  return out;
}

/** Total XP required to reach `level` (level 1 = 0). L2=30, L3=120, L5=480, L10=2430. */
export function xpForLevel(level: number): number {
  const lv = Math.max(1, Math.floor(level));
  return 30 * (lv - 1) * (lv - 1);
}

/** Level reached with a given total XP. */
export function levelForXp(xp: number): number {
  let lv = 1;
  while (lv < MAX_LEVEL && xp >= xpForLevel(lv + 1)) lv++;
  return lv;
}

/** Sum of statMod values affecting `key` (includes stat 'all'). */
export function statModSum(c: Combatant, key: StatKey): number {
  let sum = 0;
  for (const s of c.statuses) {
    if (s.kind === 'statMod' && (s.stat === key || s.stat === 'all')) sum += s.value;
  }
  return sum;
}

/** Stat after multiplicative statMod statuses. Never below 10% of base, never below 0. */
export function effectiveStat(c: Combatant, key: StatKey): number {
  const base = c.max[key];
  const mult = Math.max(0.1, 1 + statModSum(c, key));
  return base * mult;
}
