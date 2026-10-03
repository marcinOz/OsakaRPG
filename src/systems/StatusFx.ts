import type { StatusEffectDef, StatusInstance, StatusKind } from '@/types';
import type { Combatant } from './Combatant';

export type TickEvent =
  | { type: 'regen'; uid: string; statusId: string; amount: number }
  | { type: 'poison'; uid: string; statusId: string; amount: number }
  | { type: 'expire'; uid: string; statusId: string; name: string }
  | { type: 'ko'; uid: string };

/**
 * Apply (or refresh) a status. Same id never stacks: duration is refreshed to the longer
 * of the two and the value is replaced. Returns the live instance.
 */
export function applyStatus(c: Combatant, def: StatusEffectDef, sourceId?: string): StatusInstance {
  const existing = c.statuses.find((s) => s.id === def.id);
  if (existing) {
    existing.value = def.value;
    existing.kind = def.kind;
    existing.stat = def.stat;
    existing.debuff = def.debuff;
    if (def.turns < 0 || existing.remaining < 0) existing.remaining = -1;
    else existing.remaining = Math.max(existing.remaining, def.turns);
    existing.turns = def.turns;
    if (sourceId !== undefined) existing.sourceId = sourceId;
    return existing;
  }
  const inst: StatusInstance = { ...def, remaining: def.turns, sourceId };
  c.statuses.push(inst);
  return inst;
}

/** Remove by id. Also removes "sub-statuses" with id prefix `${id}_` (e.g. kacGigant_spd). Returns removed. */
export function removeStatus(c: Combatant, id: string): StatusInstance[] {
  const removed = c.statuses.filter((s) => s.id === id || s.id.startsWith(id + '_'));
  if (removed.length) c.statuses = c.statuses.filter((s) => !removed.includes(s));
  return removed;
}

export function hasStatus(c: Combatant, id: string): boolean {
  return c.statuses.some((s) => s.id === id);
}

export function hasKind(c: Combatant, kind: StatusKind): boolean {
  return c.statuses.some((s) => s.kind === kind);
}

/** Sum of `value` over statuses of a kind. */
export function kindSum(c: Combatant, kind: StatusKind): number {
  return c.statuses.reduce((a, s) => (s.kind === kind ? a + s.value : a), 0);
}

/** Removes debuffs only. Returns removed instances. */
export function cleanse(c: Combatant): StatusInstance[] {
  const removed = c.statuses.filter((s) => s.debuff);
  if (removed.length) c.statuses = c.statuses.filter((s) => !s.debuff);
  return removed;
}

/**
 * Turn-start processing: regen / poison, then decrement durations and expire.
 * Statuses with turns -1 never expire. Dead units only lose nothing (no-op).
 */
export function tickStatuses(c: Combatant): TickEvent[] {
  const ev: TickEvent[] = [];
  if (!c.alive) return ev;
  for (const s of c.statuses) {
    if (s.kind === 'regen' && c.hp < c.max.hp) {
      const amount = Math.min(c.max.hp - c.hp, Math.max(1, Math.round(c.max.hp * s.value)));
      c.hp += amount;
      ev.push({ type: 'regen', uid: c.uid, statusId: s.id, amount });
    } else if (s.kind === 'poison') {
      const amount = Math.min(c.hp, Math.max(1, Math.round(c.max.hp * s.value)));
      c.hp -= amount;
      ev.push({ type: 'poison', uid: c.uid, statusId: s.id, amount });
    }
  }
  if (c.hp <= 0) {
    c.hp = 0;
    c.alive = false;
    c.statuses = [];
    ev.push({ type: 'ko', uid: c.uid });
    return ev;
  }
  const keep: StatusInstance[] = [];
  for (const s of c.statuses) {
    if (s.remaining < 0) { keep.push(s); continue; }
    s.remaining -= 1;
    if (s.remaining <= 0) ev.push({ type: 'expire', uid: c.uid, statusId: s.id, name: s.name });
    else keep.push(s);
  }
  c.statuses = keep;
  return ev;
}
