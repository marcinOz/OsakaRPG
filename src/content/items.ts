import type { StatusEffectDef } from '@/types';

export interface ItemDef {
  id: string;
  name: string;
  description: string;
  icon: string;               // texture key
  target: 'ally' | 'allAllies' | 'deadAlly';
  heal?: number;              // flat HP
  mp?: number;                // flat MP
  revivePct?: number;         // revive KO'd target at % max HP
  cleanse?: boolean;          // remove all debuffs
  removeStatus?: string[];    // remove specific statuses (also world statuses on field/after battle)
  effects?: StatusEffectDef[];
  battle?: boolean;           // usable in battle (default true)
  field?: boolean;            // usable on the overworld (default true)
}

export const ITEMS: Record<string, ItemDef> = {
  kawa: {
    id: 'kawa', name: 'Kawa', icon: 'item_kawa', target: 'ally',
    description: 'Czarna jak noc. +40 HP, leczy Kaca Giganta.',
    heal: 40, removeStatus: ['kacGigant'],
  },
  kebab: {
    id: 'kebab', name: 'Kebab', icon: 'item_kebab', target: 'ally',
    description: 'Ostry, z baraniną. +80 HP.',
    heal: 80,
  },
  piwo: {
    id: 'piwo', name: 'Piwo', icon: 'item_piwo', target: 'ally',
    description: '+20 MP i odrobina odwagi (+10% ATK, 3 tury).',
    mp: 20,
    effects: [{ id: 'piwoBuff', name: 'Odwaga', kind: 'statMod', stat: 'atk', value: 0.1, turns: 3 }],
  },
  zimnyBrowar: {
    id: 'zimnyBrowar', name: 'Zimny Browar', icon: 'item_browar', target: 'allAllies',
    description: 'Zgrzewka dla całej ekipy. +30 HP drużynie.',
    heal: 30,
  },
  elektrolity: {
    id: 'elektrolity', name: 'Elektrolity', icon: 'item_elektrolity', target: 'ally',
    description: 'Usuwa wszystkie negatywne efekty.',
    cleanse: true,
  },
};
