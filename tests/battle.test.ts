import { describe, it, expect } from 'vitest';
import { HEROES } from '@/content/heroes';
import { ENEMIES } from '@/content/enemies';
import { BattleEngine, makeEnemyCombatant, makeHeroCombatant } from '@/systems/BattleEngine';
import { hasStatus } from '@/systems/StatusFx';

describe('BattleEngine', () => {
  it('initializes combatants correctly', () => {
    const danny = makeHeroCombatant(HEROES.danny, 1);
    const bol = makeEnemyCombatant(ENEMIES.bolKregoslupa, 0);
    const engine = new BattleEngine([danny], [bol]);

    expect(engine.heroes[0].hp).toBe(HEROES.danny.base.hp);
    expect(engine.enemies[0].hp).toBe(ENEMIES.bolKregoslupa.stats.hp);
    expect(engine.outcome()).toBe('ongoing');
  });

  it('Danny Steel Wall applies taunt and 80% damage reduction', () => {
    const danny = makeHeroCombatant(HEROES.danny, 1);
    const bol = makeEnemyCombatant(ENEMIES.bolKregoslupa, 0);
    // Use fixed deterministic RNG = 0.5 (middle variance, no crit)
    const engine = new BattleEngine([danny], [bol], [ENEMIES.bolKregoslupa], { rng: () => 0.5 });

    // Danny uses Steel Wall
    engine.act(danny.uid, 'steelWall');
    expect(hasStatus(danny, 'steelWall')).toBe(true);
    expect(hasStatus(danny, 'taunt')).toBe(true);

    // Bol attacks Danny
    const prevHp = danny.hp;
    engine.act(bol.uid, 'attack', danny.uid);
    const dmgTaken = prevHp - danny.hp;

    // Normal damage without Steel Wall would be: (12*2 - 18) * 1.0 * 1.0 = 6 dmg
    // With 80% reduction: 6 * 0.2 = 1.2 -> rounded to 1 dmg
    expect(dmgTaken).toBeLessThanOrEqual(2);
    expect(dmgTaken).toBeGreaterThanOrEqual(1);
  });

  it('Alior Frame Trap stuns enemy and skips their turn', () => {
    const alior = makeHeroCombatant(HEROES.alior, 1);
    const bol = makeEnemyCombatant(ENEMIES.bolKregoslupa, 0);
    const engine = new BattleEngine([alior], [bol], [ENEMIES.bolKregoslupa], { rng: () => 0.5 });

    engine.act(alior.uid, 'frameTrap', bol.uid);
    expect(hasStatus(bol, 'stun')).toBe(true);

    // Bol's ATB reaches 100
    bol.atb = 100;
    const events = engine.tick(16);
    expect(events.some((e) => e.type === 'skip')).toBe(true);
    expect(hasStatus(bol, 'stun')).toBe(false);
  });

  it('Lisu Smoke Screen grants evasion and stealth (first attack misses)', () => {
    const lisu = makeHeroCombatant(HEROES.lisu, 1);
    const bol = makeEnemyCombatant(ENEMIES.bolKregoslupa, 0);
    const engine = new BattleEngine([lisu], [bol], [ENEMIES.bolKregoslupa], { rng: () => 0.5 });

    engine.act(lisu.uid, 'smokeScreen');
    expect(hasStatus(lisu, 'stealth')).toBe(true);

    // Bol attacks Lisu -> stealth guarantees a miss
    const prevHp = lisu.hp;
    const events = engine.act(bol.uid, 'attack', lisu.uid);
    expect(events.some((e) => e.type === 'miss')).toBe(true);
    expect(lisu.hp).toBe(prevHp);
    // Stealth should now be consumed
    expect(hasStatus(lisu, 'stealth')).toBe(false);
  });

  it('Barti Bass Blast deals AoE damage and buffs party morale', () => {
    const barti = makeHeroCombatant(HEROES.barti, 1);
    const bol1 = makeEnemyCombatant(ENEMIES.bolKregoslupa, 0);
    const bol2 = makeEnemyCombatant(ENEMIES.bolKregoslupa, 1);
    const engine = new BattleEngine([barti], [bol1, bol2], [ENEMIES.bolKregoslupa], { rng: () => 0.5 });

    const prevHp1 = bol1.hp;
    const prevHp2 = bol2.hp;
    engine.act(barti.uid, 'bassBlast');

    expect(bol1.hp).toBeLessThan(prevHp1);
    expect(bol2.hp).toBeLessThan(prevHp2);
    expect(hasStatus(barti, 'morale')).toBe(true);
  });

  it('Łuki Tipsy Aqua-Rescue cleanses debuffs and revives fallen allies', () => {
    const luki = makeHeroCombatant(HEROES.luki, 1);
    const danny = makeHeroCombatant(HEROES.danny, 1);
    danny.alive = false;
    danny.hp = 0;
    // Luki has a debuff
    luki.statuses.push({ id: 'stress', name: 'Stres', kind: 'statMod', stat: 'atk', value: -0.2, turns: 2, remaining: 2, debuff: true });

    const bol = makeEnemyCombatant(ENEMIES.bolKregoslupa, 0);
    const engine = new BattleEngine([luki, danny], [bol]);

    engine.act(luki.uid, 'aquaRescue');
    // Danny should be revived with 50% HP
    expect(danny.alive).toBe(true);
    expect(danny.hp).toBe(Math.round(danny.max.hp * 0.5));
    // Luki's debuff should be cleansed
    expect(hasStatus(luki, 'stress')).toBe(false);
  });

  it('Kark physical resistance softens incoming damage and becomes vulnerable when stunned', () => {
    const danny = makeHeroCombatant(HEROES.danny, 4); // L4 Danny
    const kark = makeEnemyCombatant(ENEMIES.kark, 0);
    const engine = new BattleEngine([danny], [kark], [ENEMIES.kark], { rng: () => 0.5 });

    // Physical attack while Kark is not stunned -> damage is reduced by 70% (armorMult = 0.3)
    const prevHp = kark.hp;
    const events = engine.act(danny.uid, 'attack', kark.uid);
    const dmgEvent = events.find((e) => e.type === 'damage') as any;
    expect(dmgEvent).toBeDefined();
    expect(dmgEvent.amount).toBeGreaterThan(0); // Deal chipped damage, never hard 0
    expect(events.some((e) => e.type === 'log' && e.text.includes('Pancerz'))).toBe(true);
    const unstunnedDmg = prevHp - kark.hp;

    // Apply stun to Kark (e.g. from Alior's Frame Trap)
    kark.statuses.push({ id: 'stun', name: 'Ogłuszenie', kind: 'stun', value: 1, turns: 1, remaining: 1, debuff: true });

    // Attack again -> stun provides +25% damage bonus
    const hpBeforeStunnedHit = kark.hp;
    const stunnedEvents = engine.act(danny.uid, 'attack', kark.uid);
    expect(stunnedEvents.some((e) => e.type === 'log' && e.text.includes('odsłonięty punkt'))).toBe(true);
    const stunnedDmg = hpBeforeStunnedHit - kark.hp;
    expect(stunnedDmg).toBeGreaterThan(unstunnedDmg * 3); // ~4x more damage when stunned vs shielded!
  });

  it('Pan Janusz triggers boss dialogue phases when HP falls below thresholds', () => {
    const danny = makeHeroCombatant(HEROES.danny, 50); // high level so Danny hits hard
    const janusz = makeEnemyCombatant(ENEMIES.panJanusz, 0);
    const engine = new BattleEngine([danny], [janusz], [ENEMIES.panJanusz], { rng: () => 0.5 });

    // Reduce Janusz's HP to 50%
    janusz.hp = janusz.max.hp * 0.5;
    const events = engine.act(danny.uid, 'attack', janusz.uid);
    expect(events.some((e) => e.type === 'phase' && e.say.includes('Nielegalne obozowisko'))).toBe(true);
  });

  it('Slacki actions execute properly with damage, debuffs and fx', () => {
    const danny = makeHeroCombatant(HEROES.danny, 1);
    const alior = makeHeroCombatant(HEROES.alior, 1);
    const slack = makeEnemyCombatant(ENEMIES.slacki, 0);
    const engine = new BattleEngine([danny, alior], [slack], [ENEMIES.slacki], { rng: () => 0.5 });

    // 1. Basic attack by Slack
    const prevDannyHp = danny.hp;
    const atkEvents = engine.act(slack.uid, 'attack', danny.uid);
    expect(atkEvents.some((e) => e.type === 'skill' && e.skillId === 'attack' && e.fx === 'hit')).toBe(true);
    expect(danny.hp).toBeLessThan(prevDannyHp);

    // 2. @channel AoE attack by Slack
    const prevAliorHp = alior.hp;
    const prevDannyHp2 = danny.hp;
    const pingEvents = engine.act(slack.uid, 'slackPing');
    expect(pingEvents.some((e) => e.type === 'skill' && e.skillId === 'slackPing' && e.fx === 'glitch')).toBe(true);
    // Should target both heroes
    const skillEv = pingEvents.find((e) => e.type === 'skill' && e.skillId === 'slackPing') as any;
    expect(skillEv.targets).toContain(danny.uid);
    expect(skillEv.targets).toContain(alior.uid);
    expect(danny.hp).toBeLessThan(prevDannyHp2);
    expect(alior.hp).toBeLessThan(prevAliorHp);

    // 3. Deadline debuff by Slack
    const debuffEvents = engine.act(slack.uid, 'stressDebuff', danny.uid);
    expect(debuffEvents.some((e) => e.type === 'skill' && e.skillId === 'stressDebuff' && e.fx === 'glitch')).toBe(true);
    expect(hasStatus(danny, 'stress')).toBe(true);
  });

  it('simulation: Alior vs Slacki ATB progression reaches ready state', () => {
    const alior = makeHeroCombatant(HEROES.alior, 1);
    const slack = makeEnemyCombatant(ENEMIES.slacki, 0);
    const engine = new BattleEngine([alior], [slack], [ENEMIES.slacki], { rng: () => 0.5 });
    alior.atb = 40;
    slack.atb = 25;

    let time = 0;
    const allEvents: any[] = [];
    while (time < 5000 && !engine.waitingHero) {
      time += 16;
      const evs = engine.tick(16);
      if (evs.length > 0) {
        allEvents.push(...evs);
      }
    }

    expect(engine.waitingHero?.uid).toBe(alior.uid);
    expect(allEvents.some((e) => e.type === 'ready' && e.uid === alior.uid)).toBe(true);
  });

  it('slackInvasion encounter: hero attacks, waitingHero clears, Slack responds swiftly without hanging', () => {
    const danny = makeHeroCombatant(HEROES.danny, 1);
    const slack = makeEnemyCombatant(ENEMIES.slacki, 0);
    // Simulating slackInvasion preset with hero 100 ATB and enemy 70 ATB
    danny.atb = 100;
    slack.atb = 70;

    const engine = new BattleEngine([danny], [slack], [ENEMIES.slacki], { rng: () => 0.5 });
    // Frame 0: tick(0) triggers ready for Danny
    const initEvs = engine.tick(0);
    expect(initEvs.some((e) => e.type === 'ready' && e.uid === danny.uid)).toBe(true);
    expect(engine.waitingHero?.uid).toBe(danny.uid);

    // Danny attacks Slack
    const attackEvs = engine.act(danny.uid, 'attack', slack.uid);
    expect(attackEvs.some((e) => e.type === 'damage')).toBe(true);
    expect(engine.waitingHero).toBeNull();
    expect(danny.atb).toBe(0);

    // Within ~400ms (25 frames of 16ms), Slack (spd 11, starting at 70) reaches 100 ATB and acts!
    let time = 0;
    const enemyTurns: any[] = [];
    while (time < 600) {
      time += 16;
      const evs = engine.tick(16);
      if (evs.some((e) => e.type === 'skill' && e.actorUid === slack.uid)) {
        enemyTurns.push(...evs);
        break;
      }
    }

    expect(enemyTurns.length).toBeGreaterThan(0);
    expect(time).toBeLessThanOrEqual(500); // Swift response!

    // Continuing ticks: Danny charges and receives next turn
    let secondHeroTurn = false;
    while (time < 3000) {
      time += 16;
      const evs = engine.tick(16);
      if (evs.some((e) => e.type === 'ready' && e.uid === danny.uid)) {
        secondHeroTurn = true;
        break;
      }
    }
    expect(secondHeroTurn).toBe(true);
    expect(engine.waitingHero?.uid).toBe(danny.uid);
  });
});
