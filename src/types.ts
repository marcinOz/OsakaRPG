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

/** Game state contracts */
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

/** Battle configuration and parameter contracts */
export type BattleAdvantage = 'normal' | 'preemptive' | 'ambush';

export interface EnemySpec {
  id: string;               // Key in ENEMIES registry
  name?: string;           // Custom display name override
  level?: number;          // Level override / scaling
  stats?: Partial<Stats>;  // Stat overrides (HP, ATK, DEF, etc.)
  hp?: number;             // Current HP override
  mp?: number;             // Current MP override
  atb?: number;            // Starting ATB (0..100)
  sprite?: string;         // Texture key override
  spriteSize?: number;     // Visual dimension (default: automatic based on texture/metadata)
  boss?: boolean;          // Boss phase logic flag
}

export type EnemyParam = string | EnemySpec;

export interface HeroSpec {
  id: HeroId;              // Hero definition key
  level?: number;          // Level override
  stats?: Partial<Stats>;  // Stat overrides
  hp?: number;             // Current HP override
  mp?: number;             // Current MP override
  atb?: number;            // Starting ATB override (0..100)
  skills?: string[];       // Skill set override
}

export type HeroParam = HeroId | HeroSpec | any;

export interface BattleRewardConfig {
  xpMultiplier?: number;
  bonusXp?: number;
  bonusItems?: string[];
  grantProgression?: boolean; // Set false for simulations / minigames
}

export interface BattleParams {
  /** Global game state. Created automatically if omitted (for standalone/tests). */
  state?: GameData;

  /** Visual background texture key (e.g. 'battle_apartment_bg', 'battle_garage_bg', 'battle_rift_bg') */
  bg?: string;

  /** Battle BGM song ID (e.g. 'ch01_battle', 'ch09_finalboss'). Defaults to 'ch01_battle'. */
  music?: string;

  /** Victory fanfare song ID. Defaults to 'victory'. */
  victoryMusic?: string;

  /** Optional intro announcement banner displayed across screen at battle start */
  battleTitle?: string;

  /** Enemies in encounter (string IDs or EnemySpec objects) */
  enemies: EnemyParam[];

  /** Heroes in combat. Defaults to state.party if omitted. */
  heroes?: HeroParam[];

  /** Tactical advantage preset:
   * - 'normal': Hero 1 starts at 100 ATB, others at 70, enemies at 25
   * - 'preemptive': All heroes start at 100 ATB, enemies at 0
   * - 'ambush': All enemies start at 100 ATB, heroes at 0
   */
  advantage?: BattleAdvantage;

  /** Direct numeric ATB overrides */
  heroAtbStart?: number | number[] | ((idx: number) => number);
  enemyAtbStart?: number | number[] | ((idx: number) => number);

  /** Whether player can escape / flee ('UCIECZKA' option in command menu) */
  canFlee?: boolean;
  fleeSuccessChance?: number;

  /** Whether defeat continues story without Game Over */
  allowDefeat?: boolean;

  /** Destination scene on defeat if not Game Over (defaults to 'Title') */
  defeatScene?: string;

  /** Destination scene on victory (defaults to 'World') */
  returnScene?: string;

  /** Extra custom payload passed back to returnScene / defeatScene */
  returnSceneData?: Record<string, any>;

  /** Environmental or passive status effects applied at start */
  partyEffects?: StatusEffectDef[];
  enemyEffects?: StatusEffectDef[];

  /** Progression and reward tuning */
  rewards?: BattleRewardConfig;
}

