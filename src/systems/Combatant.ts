import type { EnemyDef, Stats, StatusInstance } from '@/types';

/** A unit taking part in a battle (hero or enemy). Pure data, mutated by BattleEngine / StatusFx. */
export interface Combatant {
  uid: string;
  side: 'hero' | 'enemy';
  defId: string;
  name: string;
  level: number;
  max: Stats;
  hp: number;
  mp: number;
  statuses: StatusInstance[];
  /** ATB gauge 0..100 */
  atb: number;
  skills: string[];
  alive: boolean;
  defending: boolean;
  sprite?: string;
  boss?: boolean;
  immune?: EnemyDef['immune'];
}

/** Random number source in [0,1). Injectable for deterministic tests. */
export type Rng = () => number;
