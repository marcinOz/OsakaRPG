import type { SkillDef } from '@/types';

export const SKILLS: Record<string, SkillDef> = {
  attack: { id: 'attack', name: 'ATAK', description: 'Zwykły cios.', mpCost: 0, target: 'enemy', power: 1, kind: 'physical', log: '{user} atakuje {target}!' },

  // --- Signatures ---
  steelWall: {
    id: 'steelWall', name: 'STEEL WALL', description: 'Prowokuje wrogów, blokuje 80% obrażeń.', mpCost: 8, target: 'self', kind: 'none',
    selfEffects: [
      { id: 'steelWall', name: 'Steel Wall', kind: 'dmgReduction', value: 0.8, turns: 2 },
      { id: 'taunt', name: 'Prowokacja', kind: 'taunt', value: 1, turns: 2 },
    ],
    fx: 'shield', log: '{user} uses STEEL WALL! Incoming DMG reduced by 80%!',
  },
  frameTrap: {
    id: 'frameTrap', name: 'FRAME TRAP', description: 'Ogłusza wroga, wykorzystując opóźnienie animacji.', mpCost: 10, target: 'enemy', power: 0.6, kind: 'physical',
    effects: [{ id: 'stun', name: 'Ogłuszenie', kind: 'stun', value: 1, turns: 1, debuff: true }],
    fx: 'glitch', log: '{user} uses FRAME TRAP! {target} skipped turn!',
  },
  smokeScreen: {
    id: 'smokeScreen', name: 'SMOKE SCREEN', description: '+50% uniku drużyny i ukrycie.', mpCost: 9, target: 'allAllies', kind: 'none',
    effects: [
      { id: 'smoke', name: 'Zasłona Dymna', kind: 'evasion', value: 0.5, turns: 3 },
      { id: 'stealth', name: 'Ukrycie', kind: 'stealth', value: 1, turns: 2 },
    ],
    fx: 'smoke', log: '{user} uses SMOKE SCREEN! Party evasion +50%!',
  },
  bassBlast: {
    id: 'bassBlast', name: 'BASS BLAST', description: 'Obszarowe obrażenia i morale drużyny.', mpCost: 14, target: 'allEnemies', power: 1.4, kind: 'magic',
    selfEffects: [{ id: 'morale', name: 'Morale', kind: 'statMod', stat: 'atk', value: 0.15, turns: 3 }],
    fx: 'bass', log: '{user} drops the needle -> BASS BLAST!',
  },
  wildernessSurvival: {
    id: 'wildernessSurvival', name: 'WILDERNESS SURVIVAL', description: 'Leczy drużynę ziołami i daje regenerację.', mpCost: 14, target: 'allAllies', power: 0.9, kind: 'heal',
    effects: [{ id: 'herbs', name: 'Leśne Zioła', kind: 'regen', value: 0.06, turns: 3 }],
    fx: 'leaves', log: '{user} uses WILDERNESS SURVIVAL! The party is healing!',
  },
  aquaRescue: {
    id: 'aquaRescue', name: 'TIPSY AQUA-RESCUE', description: 'Usuwa debuffy i wskrzesza poległych.', mpCost: 16, target: 'allAllies', kind: 'heal', power: 0.3,
    cleanse: true, revivePct: 0.5,
    fx: 'splash', log: '{user} uses TIPSY AQUA-RESCUE! Debuffs cleansed!',
  },

  // --- Secondary hero skills ---
  shakerSlam: { id: 'shakerSlam', name: 'SHAKER SLAM', description: 'Cios szejkerem z białkiem.', mpCost: 4, target: 'enemy', power: 1.6, kind: 'physical', fx: 'hit', log: '{user} wali {target} szejkerem!' },
  comboString: { id: 'comboString', name: 'COMBO STRING', description: 'Seria trzech szybkich ciosów.', mpCost: 6, target: 'enemy', power: 1.5, kind: 'physical', fx: 'hit', log: '{user} wbija 10-hit combo!' },
  backstab: { id: 'backstab', name: 'BACKSTAB', description: 'Cios z cienia, wysoka szansa kryta.', mpCost: 5, target: 'enemy', power: 1.8, kind: 'physical', fx: 'hit', log: '{user} wyskakuje zza śmietnika!' },
  scratch: { id: 'scratch', name: 'SCRATCH', description: 'Skrecz w ucho wroga.', mpCost: 5, target: 'enemy', power: 1.5, kind: 'magic', fx: 'bass', log: '{user} skreczuje {target}!' },
  multitool: { id: 'multitool', name: 'MULTI-TOOL', description: 'Precyzyjny cios multitoolem.', mpCost: 4, target: 'enemy', power: 1.5, kind: 'physical', fx: 'hit', log: '{user} wyciąga multitool!' },
  lifebuoyThrow: { id: 'lifebuoyThrow', name: 'RZUT KOŁEM', description: 'Leczy jednego sojusznika.', mpCost: 6, target: 'ally', power: 1.4, kind: 'heal', fx: 'splash', log: '{user} rzuca koło do {target}!' },

  // --- Enemy skills ---
  backPain: { id: 'backPain', name: 'Strzyknięcie', description: '', mpCost: 0, target: 'enemy', power: 1.2, kind: 'physical', log: '{user}: strzyka w krzyżu {target}!' },
  slackPing: { id: 'slackPing', name: '@channel', description: '', mpCost: 0, target: 'allEnemies', power: 0.6, kind: 'magic', log: '{user} pinguje @channel!' },
  stressDebuff: {
    id: 'stressDebuff', name: 'Deadline', description: '', mpCost: 0, target: 'enemy', power: 0.4, kind: 'magic',
    effects: [{ id: 'stress', name: 'Stres', kind: 'statMod', stat: 'atk', value: -0.2, turns: 3, debuff: true }],
    log: '{user} wysyła deadline na piątek!',
  },
};
