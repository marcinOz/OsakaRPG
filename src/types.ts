/**
 * Core shared contracts. All systems (engine, scenes, content, audio) depend on these.
 * Keep this file framework-free (no Phaser imports) so logic stays unit-testable.
 */

export type HeroId = 'danny' | 'alior' | 'lisu' | 'barti' | 'oziem' | 'luki';
export const HERO_IDS: HeroId[] = ['danny', 'alior', 'lisu', 'barti', 'oziem', 'luki'];

export interface Stats {
  hp: number;
  mp: number;
  atk: number;
  def: number;
  mag: number;
  spd: number;
  lck: number;
}

export type StatKey = keyof Stats;

export interface HeroDef {
  id: HeroId;
  name: string;          // display name, e.g. "Danny"
  fullName: string;      // e.g. "DANIEL G."
  className: string;     // e.g. "The Tank"
  role: string;
  signature: string;     // SkillId of signature ability
  skills: string[];      // all SkillIds known at start
  base: Stats;
  growth: Partial<Stats>; // per level
  items: string[];       // detected item icon keys (analyzer)
  leaderQuote: string;
  leaderBonus: { label: string; effect: StatusEffectDef };
  color: number;         // accent color for UI
}

export type TargetType = 'self' | 'ally' | 'allAllies' | 'enemy' | 'allEnemies' | 'deadAlly';

export interface SkillDef {
  id: string;
  name: string;          // "STEEL WALL"
  description: string;
  mpCost: number;
  target: TargetType;
  /** damage power multiplier; 0 = no damage */
  power?: number;
  kind?: 'physical' | 'magic' | 'heal' | 'none';
  /** effects applied to each target */
  effects?: StatusEffectDef[];
  /** effects applied to caster */
  selfEffects?: StatusEffectDef[];
  cleanse?: boolean;
  revivePct?: number;    // 0..1 HP on revive
  fx?: string;           // FX key for scenes
  log?: string;          // combat log template, {user} {target}
}

export type StatusKind =
  | 'statMod'        // multiplicative stat modifier
  | 'dmgReduction'   // reduces incoming damage by value (0..1)
  | 'taunt'          // enemies must target this unit
  | 'stun'           // skip turns
  | 'evasion'        // additive evasion chance
  | 'stealth'        // next enemy targeted attack misses
  | 'regen'          // heal value*maxHp each turn
  | 'poison'         // damage value*maxHp each turn
  | 'walkSpeed';     // overworld movement multiplier

export interface StatusEffectDef {
  id: string;            // unique key, e.g. 'steelWall', 'kacGigant'
  name: string;
  kind: StatusKind;
  value: number;
  stat?: StatKey | 'all';
  turns: number;         // -1 = permanent until removed
  debuff?: boolean;
}

export interface StatusInstance extends StatusEffectDef {
  remaining: number;
  sourceId?: string;
}

export interface EnemyDef {
  id: string;
  name: string;
  level: number;
  stats: Stats;
  skills: string[];      // SkillIds
  sprite: string;        // texture key
  xp: number;
  immune?: { physical?: boolean; untilStatus?: string[] }; // e.g. Kark immune until stunned
  boss?: boolean;
  phases?: BossPhase[];
  ai?: 'random' | 'weakest' | 'strongest';
}

export interface BossPhase {
  when: { hpBelow?: number; turn?: number; statusApplied?: string };
  say?: string;
  addSkills?: string[];
  spawn?: string[];
}

/** Dialogue */
export interface DialogueLine {
  speaker: HeroId | string;   // HeroId or literal name ("Pan Janusz", "SYSTEM")
  text: string;
  /** leader-specific overrides */
  leader?: Partial<Record<HeroId, string>>;
  portrait?: string;          // override portrait key
}

export interface DialogueChoice {
  label: string;
  next?: DialogueLine[];
  action?: string;            // event id fired on pick
}

/** Chapters / maps */
export interface ChapterDef {
  id: number;
  title: string;
  location: string;
  music: { explore: string; battle?: string; label: string };
  maps: string[];
  joins?: HeroId[];
}

export interface SongDef {
  id: string;
  label: string;           // "inspired by …"
  bpm: number;
  steps: number;           // steps per pattern (16)
  swing?: number;
  tracks: SongTrack[];
}

export interface SongTrack {
  inst: 'pulse' | 'square' | 'triangle' | 'saw' | 'noise' | 'kick' | 'snare' | 'hat' | 'pad';
  vol: number;
  /** pattern list: each pattern is array of note names or null ("C4", "D#3", "x" for drums) */
  patterns: (string | null)[][];
  order: number[];
  duty?: number;
}
