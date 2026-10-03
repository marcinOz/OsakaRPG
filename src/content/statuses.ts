import type { StatusEffectDef } from '@/types';

/**
 * World (overworld-persistent) statuses. One world status can bundle several effects:
 * `walkSpeed` effects affect overworld movement, everything else is applied to heroes in battle.
 */
export interface WorldStatusDef {
  id: string;
  name: string;
  description: string;
  debuff?: boolean;
  effects: StatusEffectDef[];
}

export const WORLD_STATUSES: Record<string, WorldStatusDef> = {
  kacGigant: {
    id: 'kacGigant',
    name: 'Kac Gigant',
    description: '-20% prędkości chodzenia, -20% SPD w walce.',
    debuff: true,
    effects: [
      { id: 'kacGigant', name: 'Kac Gigant', kind: 'walkSpeed', value: 0.8, turns: -1, debuff: true },
      { id: 'kacGigant_spd', name: 'Kac Gigant', kind: 'statMod', stat: 'spd', value: -0.2, turns: -1, debuff: true },
    ],
  },
  klimatLatMlodosci: {
    id: 'klimatLatMlodosci',
    name: 'Klimat Lat Młodości',
    description: '+50% do wszystkich statystyk.',
    effects: [
      { id: 'klimatLatMlodosci', name: 'Klimat Lat Młodości', kind: 'statMod', stat: 'all', value: 0.5, turns: -1 },
    ],
  },
};
