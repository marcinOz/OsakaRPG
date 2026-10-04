import type { EnemyDef, HeroDef, SkillDef, StatusEffectDef } from '@/types';
import { SKILLS } from '@/content/skills';
import { ITEMS } from '@/content/items';
import type { Combatant, Rng } from './Combatant';
import { effectiveStat, heroStatsAtLevel } from './Stats';
import { applyStatus, cleanse, hasKind, hasStatus, kindSum, tickStatuses } from './StatusFx';

export { type Combatant, type Rng } from './Combatant';

export type BattleEvent =
  | { type: 'ready'; uid: string }
  | { type: 'skip'; uid: string; reason: string }
  | { type: 'skill'; actorUid: string; skillId: string; targets: string[]; fx?: string }
  | { type: 'item'; actorUid: string; itemId: string; targets: string[] }
  | { type: 'damage'; uid: string; amount: number; crit: boolean; targetHp: number }
  | { type: 'heal'; uid: string; amount: number; targetHp: number }
  | { type: 'miss'; uid: string }
  | { type: 'immune'; uid: string; reason: string }
  | { type: 'mp'; uid: string; delta: number; currentMp: number }
  | { type: 'status'; uid: string; statusId: string; name: string; applied: boolean }
  | { type: 'ko'; uid: string }
  | { type: 'revive'; uid: string; targetHp: number }
  | { type: 'phase'; say: string }
  | { type: 'log'; text: string }
  | { type: 'victory'; xp: number; items: string[] }
  | { type: 'defeat' };

export interface BattleOptions {
  rng?: Rng;
  partyEffects?: StatusEffectDef[];
}

export function makeHeroCombatant(def: HeroDef, level: number, hp?: number, mp?: number): Combatant {
  const max = heroStatsAtLevel(def, level);
  return {
    uid: `hero_${def.id}`,
    side: 'hero',
    defId: def.id,
    name: def.name,
    level,
    max,
    hp: hp !== undefined ? Math.min(hp, max.hp) : max.hp,
    mp: mp !== undefined ? Math.min(mp, max.mp) : max.mp,
    statuses: [],
    atb: 0,
    skills: [...def.skills],
    alive: (hp ?? max.hp) > 0,
    defending: false,
  };
}

export function makeEnemyCombatant(def: EnemyDef, idx = 0): Combatant {
  return {
    uid: `enemy_${def.id}_${idx}`,
    side: 'enemy',
    defId: def.id,
    name: def.name,
    level: def.level,
    max: { ...def.stats },
    hp: def.stats.hp,
    mp: def.stats.mp,
    statuses: [],
    atb: 0,
    skills: [...def.skills],
    alive: true,
    defending: false,
    sprite: def.sprite,
    boss: def.boss,
    immune: def.immune,
  };
}

export class BattleEngine {
  readonly heroes: Combatant[];
  readonly enemies: Combatant[];
  private readonly rng: Rng;
  private readonly enemyDefs: Map<string, EnemyDef> = new Map();
  private triggeredPhases: Set<string> = new Set();
  waitingHero: Combatant | null = null;
  private isFinished = false;

  constructor(
    heroes: Combatant[],
    enemies: Combatant[],
    defs: EnemyDef[] = [],
    opts: BattleOptions = {}
  ) {
    this.heroes = heroes;
    this.enemies = enemies;
    this.rng = opts.rng ?? (() => Math.random());
    defs.forEach((d) => this.enemyDefs.set(d.id, d));

    // Apply starting party passive bonuses / world statuses
    if (opts.partyEffects) {
      for (const h of this.heroes) {
        if (!h.alive) continue;
        for (const eff of opts.partyEffects) {
          applyStatus(h, eff);
        }
      }
    }
  }

  getCombatant(uid: string): Combatant | undefined {
    return this.heroes.find((c) => c.uid === uid) ?? this.enemies.find((c) => c.uid === uid);
  }

  outcome(): 'ongoing' | 'victory' | 'defeat' {
    if (this.enemies.every((e) => !e.alive)) return 'victory';
    if (this.heroes.every((h) => !h.alive)) return 'defeat';
    return 'ongoing';
  }

  rewards(): { xp: number; items: string[] } {
    let totalXp = 0;
    const items: string[] = [];
    for (const e of this.enemies) {
      const def = this.enemyDefs.get(e.defId);
      if (def) totalXp += def.xp;
    }
    return { xp: totalXp, items };
  }

  tick(dtMs: number): BattleEvent[] {
    const events: BattleEvent[] = [];
    if (this.isFinished) return events;

    const out = this.outcome();
    if (out !== 'ongoing') {
      this.isFinished = true;
      if (out === 'victory') {
        const rew = this.rewards();
        events.push({ type: 'victory', xp: rew.xp, items: rew.items });
        events.push({ type: 'log', text: `ZWYCIĘSTWO! Zdobyto ${rew.xp} XP!` });
      } else {
        events.push({ type: 'defeat' });
        events.push({ type: 'log', text: 'PORAŻKA... Ekipa poległa.' });
      }
      return events;
    }

    // In WAIT mode, if a hero is selecting a command, ATB does not fill
    if (this.waitingHero) return events;

    // Fill ATB gauges
    const all = [...this.heroes, ...this.enemies];
    for (const c of all) {
      if (!c.alive) continue;
      const spd = effectiveStat(c, 'spd');
      // Full gauge at spd 10 in ~1.4s: 100 in 1428ms -> rate = (spd / 10) * (100 / 1428) * dtMs = spd * 0.007 * dtMs
      c.atb = Math.min(100, c.atb + spd * 0.007 * dtMs);

      if (c.atb >= 100) {
        if (c.side === 'hero') {
          // Process turn start status tick
          const wasStunned = hasStatus(c, 'stun');
          if (wasStunned) {
            c.statuses = c.statuses.filter((s) => s.id !== 'stun');
            c.atb = 0;
            events.push({ type: 'skip', uid: c.uid, reason: 'Ogłuszenie' });
            events.push({ type: 'log', text: `${c.name} traci turę przez ogłuszenie!` });
            continue;
          }
          const tickEvs = this.handleTurnStart(c);
          events.push(...tickEvs);
          if (!c.alive) {
            c.atb = 0;
            continue;
          }
          c.defending = false;
          this.waitingHero = c;
          events.push({ type: 'ready', uid: c.uid });
          break; // wait mode halts loop
        } else {
          // Enemy turn
          const wasStunned = hasStatus(c, 'stun');
          if (wasStunned) {
            c.statuses = c.statuses.filter((s) => s.id !== 'stun');
            c.atb = 0;
            events.push({ type: 'skip', uid: c.uid, reason: 'Ogłuszenie' });
            events.push({ type: 'log', text: `${c.name} traci turę przez ogłuszenie!` });
            continue;
          }
          const tickEvs = this.handleTurnStart(c);
          events.push(...tickEvs);
          if (!c.alive) {
            c.atb = 0;
            continue;
          }
          c.defending = false;
          c.atb = 0;
          const enemyEvents = this.executeEnemyTurn(c);
          events.push(...enemyEvents);
          // Check if battle finished after enemy turn
          if (this.outcome() !== 'ongoing') {
            return [...events, ...this.tick(0)];
          }
        }
      }
    }

    return events;
  }

  private handleTurnStart(c: Combatant): BattleEvent[] {
    const events: BattleEvent[] = [];
    const ticks = tickStatuses(c);
    for (const t of ticks) {
      if (t.type === 'regen') {
        events.push({ type: 'heal', uid: c.uid, amount: t.amount, targetHp: c.hp });
        events.push({ type: 'log', text: `${c.name} regeneruje ${t.amount} HP!` });
      } else if (t.type === 'poison') {
        events.push({ type: 'damage', uid: c.uid, amount: t.amount, crit: false, targetHp: c.hp });
        events.push({ type: 'log', text: `${c.name} otrzymuje ${t.amount} obrażeń od statusu!` });
      } else if (t.type === 'expire') {
        events.push({ type: 'status', uid: c.uid, statusId: t.statusId, name: t.name, applied: false });
      } else if (t.type === 'ko') {
        events.push({ type: 'ko', uid: c.uid });
        events.push({ type: 'log', text: `${c.name} upada!` });
      }
    }
    return events;
  }

  validTargets(actorUid: string, skillId: string): Combatant[] {
    const actor = this.getCombatant(actorUid);
    if (!actor) return [];
    const skill = SKILLS[skillId];
    if (!skill) return [];

    const allies = actor.side === 'hero' ? this.heroes : this.enemies;
    const foes = actor.side === 'hero' ? this.enemies : this.heroes;

    switch (skill.target) {
      case 'self':
        return [actor];
      case 'ally':
        return allies.filter((a) => a.alive);
      case 'deadAlly':
        return allies.filter((a) => !a.alive);
      case 'allAllies':
        return allies; // will apply appropriately in execution
      case 'enemy': {
        const liveFoes = foes.filter((f) => f.alive);
        // If an enemy taunt is active, return that taunter if possible
        if (actor.side === 'enemy') {
          const taunter = liveFoes.find((f) => hasKind(f, 'taunt'));
          if (taunter) return [taunter];
        }
        return liveFoes;
      }
      case 'allEnemies':
        return foes.filter((f) => f.alive);
      default:
        return [];
    }
  }

  act(actorUid: string, skillId: string, targetUid?: string): BattleEvent[] {
    const events: BattleEvent[] = [];
    const actor = this.getCombatant(actorUid);
    if (!actor || !actor.alive) return events;

    const skill = SKILLS[skillId];
    if (!skill) return events;

    if (actor.mp < skill.mpCost) {
      events.push({ type: 'log', text: `${actor.name}: Za mało MP!` });
      return events;
    }

    // Deduct MP
    if (skill.mpCost > 0) {
      actor.mp -= skill.mpCost;
      events.push({ type: 'mp', uid: actor.uid, delta: -skill.mpCost, currentMp: actor.mp });
    }

    // Reset ATB and clear waitingHero if this was hero turn
    actor.atb = 0;
    if (actor.side === 'hero') {
      this.waitingHero = null;
    }

    // Resolve target combatants
    let targets: Combatant[] = [];
    const foes = actor.side === 'hero' ? this.enemies : this.heroes;
    const allies = actor.side === 'hero' ? this.heroes : this.enemies;

    if (skill.target === 'self') {
      targets = [actor];
    } else if (skill.target === 'allEnemies') {
      targets = foes.filter((f) => f.alive);
    } else if (skill.target === 'allAllies') {
      targets = skill.revivePct ? allies : allies.filter((a) => a.alive);
    } else if (skill.target === 'deadAlly') {
      const dead = allies.find((a) => a.uid === targetUid && !a.alive) ?? allies.find((a) => !a.alive);
      targets = dead ? [dead] : [];
    } else if (skill.target === 'ally') {
      const t = allies.find((a) => a.uid === targetUid && a.alive) ?? allies.find((a) => a.alive);
      targets = t ? [t] : [];
    } else {
      // Single enemy target
      // Check taunt if an enemy is attacking heroes
      let target: Combatant | undefined;
      if (actor.side === 'enemy') {
        const taunter = foes.find((f) => f.alive && hasKind(f, 'taunt'));
        if (taunter) target = taunter;
      }
      if (!target && targetUid) {
        target = foes.find((f) => f.uid === targetUid && f.alive);
      }
      if (!target) {
        target = foes.find((f) => f.alive);
      }
      targets = target ? [target] : [];
    }

    events.push({
      type: 'skill',
      actorUid: actor.uid,
      skillId,
      targets: targets.map((t) => t.uid),
      fx: skill.fx,
    });

    // Custom or default log line
    if (skill.log) {
      const targetNames = targets.map((t) => t.name).join(', ') || 'wszystkich';
      const logMsg = skill.log.replace('{user}', actor.name).replace('{target}', targetNames);
      events.push({ type: 'log', text: `> ${logMsg}` });
    } else {
      events.push({ type: 'log', text: `> ${actor.name} używa ${skill.name}!` });
    }

    // Apply self effects
    if (skill.selfEffects) {
      for (const eff of skill.selfEffects) {
        applyStatus(actor, eff);
        events.push({ type: 'status', uid: actor.uid, statusId: eff.id, name: eff.name, applied: true });
      }
    }

    // Execute on targets
    for (const target of targets) {
      this.executeSkillOnTarget(actor, skill, target, events);
    }

    // Check boss phases
    this.checkBossPhases(events);

    // Check victory / defeat
    const outcome = this.outcome();
    if (outcome !== 'ongoing') {
      this.isFinished = true;
      if (outcome === 'victory') {
        const rew = this.rewards();
        events.push({ type: 'victory', xp: rew.xp, items: rew.items });
        events.push({ type: 'log', text: `ZWYCIĘSTWO! Zdobyto ${rew.xp} XP!` });
      } else {
        events.push({ type: 'defeat' });
        events.push({ type: 'log', text: 'PORAŻKA... Ekipa poległa.' });
      }
    }

    return events;
  }

  private executeSkillOnTarget(
    actor: Combatant,
    skill: SkillDef,
    target: Combatant,
    events: BattleEvent[]
  ): void {
    let justRevived = false;
    // Revive
    if (skill.revivePct && !target.alive) {
      target.alive = true;
      target.hp = Math.max(1, Math.round(target.max.hp * skill.revivePct));
      justRevived = true;
      events.push({ type: 'revive', uid: target.uid, targetHp: target.hp });
      events.push({ type: 'log', text: `${target.name} wstaje do walki z ${target.hp} HP!` });
    }

    // Cleanse
    if (skill.cleanse) {
      const removed = cleanse(target);
      for (const r of removed) {
        events.push({ type: 'status', uid: target.uid, statusId: r.id, name: r.name, applied: false });
      }
    }

    // Heal
    if (!justRevived && skill.kind === 'heal' && skill.power && target.alive) {
      const mag = effectiveStat(actor, 'mag');
      const healAmt = Math.max(1, Math.round(mag * skill.power * 2));
      const oldHp = target.hp;
      target.hp = Math.min(target.max.hp, target.hp + healAmt);
      const actualHealed = target.hp - oldHp;
      events.push({ type: 'heal', uid: target.uid, amount: actualHealed, targetHp: target.hp });
      events.push({ type: 'log', text: `${target.name} odzyskuje ${actualHealed} HP!` });
    }

    // Attack / Magic Damage
    if ((skill.kind === 'physical' || skill.kind === 'magic') && skill.power && target.alive) {
      // Check stealth (enemy attack against stealthed hero misses and consumes stealth)
      if (target.side === 'hero' && hasKind(target, 'stealth')) {
        target.statuses = target.statuses.filter((s) => s.kind !== 'stealth');
        events.push({ type: 'miss', uid: target.uid });
        events.push({ type: 'log', text: `${target.name} znika w cieniu! Atak chybił!` });
        return;
      }

      // Check evasion
      const evasion = kindSum(target, 'evasion');
      if (evasion > 0 && this.rng() < evasion) {
        events.push({ type: 'miss', uid: target.uid });
        events.push({ type: 'log', text: `Unik! ${target.name} unika ataku!` });
        return;
      }

      // Physical armor / resistance checks (e.g. Kark's bouncer build)
      let armorMult = 1.0;
      if (skill.kind === 'physical' && target.immune?.physical) {
        const canBypass = target.immune.untilStatus?.some((st) => hasStatus(target, st));
        if (!canBypass) {
          // Soft resistance: 70% damage reduction when unstunned
          armorMult = 0.3;
          events.push({ type: 'log', text: `> Pancerz ${target.name} tłumi większość ciosu!` });
        } else {
          // Stunned / vulnerable: +25% bonus physical damage
          armorMult = 1.25;
          events.push({ type: 'log', text: `> Cios w odsłonięty punkt ${target.name}!` });
        }
      }

      // Damage calculation
      const atk = skill.kind === 'physical' ? effectiveStat(actor, 'atk') : effectiveStat(actor, 'mag');
      const def = skill.kind === 'physical' ? effectiveStat(target, 'def') : effectiveStat(target, 'def') / 2;
      const baseDmg = Math.max(1, (atk * 2 - def) * skill.power);
      const variance = 0.9 + this.rng() * 0.2; // 0.9 .. 1.1

      // Crit chance
      let critChance = effectiveStat(actor, 'lck') / 200;
      if (skill.id === 'backstab') critChance += 0.25;
      const isCrit = this.rng() < critChance;
      const critMult = isCrit ? 2.0 : 1.0;

      // Damage reduction from statuses
      const dmgRed = kindSum(target, 'dmgReduction'); // e.g. 0.8
      const redMult = Math.max(0, 1 - dmgRed);

      // Defending halves damage
      const defMult = target.defending ? 0.5 : 1.0;

      let finalDmg = Math.max(1, Math.round(baseDmg * variance * critMult * redMult * defMult * armorMult));

      target.hp = Math.max(0, target.hp - finalDmg);
      events.push({
        type: 'damage',
        uid: target.uid,
        amount: finalDmg,
        crit: isCrit,
        targetHp: target.hp,
      });

      const critText = isCrit ? ' [KRYTYK!]' : '';
      events.push({ type: 'log', text: `${target.name} otrzymuje ${finalDmg} obrażeń!${critText}` });

      if (target.hp <= 0) {
        target.alive = false;
        target.statuses = [];
        events.push({ type: 'ko', uid: target.uid });
        events.push({ type: 'log', text: `${target.name} zostaje pokonany!` });
      }
    }

    // Apply target effects
    if (skill.effects && target.alive) {
      for (const eff of skill.effects) {
        applyStatus(target, eff);
        events.push({ type: 'status', uid: target.uid, statusId: eff.id, name: eff.name, applied: true });
      }
    }
  }

  defend(actorUid: string): BattleEvent[] {
    const events: BattleEvent[] = [];
    const actor = this.getCombatant(actorUid);
    if (!actor || !actor.alive) return events;

    actor.defending = true;
    actor.atb = 0;
    if (actor.side === 'hero') {
      this.waitingHero = null;
    }
    events.push({ type: 'log', text: `${actor.name} przyjmuje postawę obronną!` });
    return events;
  }

  useItem(actorUid: string, itemId: string, targetUid?: string): BattleEvent[] {
    const events: BattleEvent[] = [];
    const actor = this.getCombatant(actorUid);
    if (!actor || !actor.alive) return events;

    const item = ITEMS[itemId];
    if (!item) return events;

    actor.atb = 0;
    if (actor.side === 'hero') {
      this.waitingHero = null;
    }

    const allies = actor.side === 'hero' ? this.heroes : this.enemies;
    let targets: Combatant[] = [];
    if (item.target === 'allAllies') {
      targets = allies.filter((a) => a.alive);
    } else if (item.target === 'deadAlly') {
      const dead = allies.find((a) => a.uid === targetUid && !a.alive) ?? allies.find((a) => !a.alive);
      targets = dead ? [dead] : [];
    } else {
      const t = allies.find((a) => a.uid === targetUid && a.alive) ?? allies.find((a) => a.alive);
      targets = t ? [t] : [];
    }

    events.push({
      type: 'item',
      actorUid: actor.uid,
      itemId,
      targets: targets.map((t) => t.uid),
    });
    events.push({ type: 'log', text: `> ${actor.name} używa ${item.name}!` });

    for (const target of targets) {
      if (item.heal && target.alive) {
        const oldHp = target.hp;
        target.hp = Math.min(target.max.hp, target.hp + item.heal);
        events.push({ type: 'heal', uid: target.uid, amount: target.hp - oldHp, targetHp: target.hp });
      }
      if (item.mp && target.alive) {
        target.mp = Math.min(target.max.mp, target.mp + item.mp);
        events.push({ type: 'mp', uid: target.uid, delta: item.mp, currentMp: target.mp });
      }
      if (item.cleanse) {
        cleanse(target);
        events.push({ type: 'log', text: `Wszystkie debuffy ${target.name} usunięte!` });
      }
      if (item.effects) {
        for (const eff of item.effects) {
          applyStatus(target, eff);
          events.push({ type: 'status', uid: target.uid, statusId: eff.id, name: eff.name, applied: true });
        }
      }
    }

    return events;
  }

  private executeEnemyTurn(enemy: Combatant): BattleEvent[] {
    const liveHeroes = this.heroes.filter((h) => h.alive);
    if (!liveHeroes.length) return [];

    // Choose target
    let target = liveHeroes[0];
    const taunter = liveHeroes.find((h) => hasKind(h, 'taunt'));
    if (taunter) {
      target = taunter;
    } else {
      const def = this.enemyDefs.get(enemy.defId);
      if (def?.ai === 'weakest') {
        target = [...liveHeroes].sort((a, b) => a.hp - b.hp)[0];
      } else {
        const idx = Math.floor(this.rng() * liveHeroes.length);
        target = liveHeroes[idx];
      }
    }

    // Pick skill
    const usable = enemy.skills
      .map((sid) => SKILLS[sid])
      .filter((s) => s && enemy.mp >= s.mpCost);
    const chosen = usable.length > 0 ? usable[Math.floor(this.rng() * usable.length)] : SKILLS.attack;

    return this.act(enemy.uid, chosen.id, target.uid);
  }

  private checkBossPhases(events: BattleEvent[]): void {
    for (const enemy of this.enemies) {
      if (!enemy.alive) continue;
      const def = this.enemyDefs.get(enemy.defId);
      if (!def?.phases) continue;

      const hpRatio = enemy.hp / enemy.max.hp;
      for (let i = 0; i < def.phases.length; i++) {
        const phase = def.phases[i];
        const key = `${enemy.uid}_phase_${i}`;
        if (this.triggeredPhases.has(key)) continue;

        let shouldTrigger = false;
        if (phase.when.hpBelow !== undefined && hpRatio <= phase.when.hpBelow) {
          shouldTrigger = true;
        }

        if (shouldTrigger) {
          this.triggeredPhases.add(key);
          if (phase.say) {
            events.push({ type: 'phase', say: phase.say });
            events.push({ type: 'log', text: `> ${enemy.name}: "${phase.say}"` });
          }
        }
      }
    }
  }
}
