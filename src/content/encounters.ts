import type Phaser from 'phaser';
import type { BattleParams } from '@/types';

export interface EncounterDef extends Omit<BattleParams, 'state'> {
  id: string;
  name: string;
}

export const ENCOUNTERS: Record<string, EncounterDef> = {
  spineAmbush: {
    id: 'spineAmbush',
    name: 'Ból Kręgosłupa',
    bg: 'battle_apartment_bg',
    music: 'ch01_battle',
    enemies: ['bolKregoslupa'],
    battleTitle: 'ZASADZKA: BÓL KRĘGOSŁUPA',
    returnScene: 'World',
  },
  slackInvasion: {
    id: 'slackInvasion',
    name: 'Nieprzeczytane Wiadomości',
    bg: 'battle_apartment_bg',
    music: 'ch01_battle',
    enemies: ['slacki'],
    enemyAtbStart: 70,
    battleTitle: 'ALERT: NIEPRZECZYTANE SLACKI',
    returnScene: 'World',
  },
  sasiadBoss: {
    id: 'sasiadBoss',
    name: 'Sąsiad Szkodnik',
    bg: 'battle_garage_bg',
    music: 'ch01_battle',
    enemies: ['sasiadSzkodnik'],
    battleTitle: 'BOSS: SĄSIAD SZKODNIK',
    returnScene: 'World',
  },
  pubHipsters: {
    id: 'pubHipsters',
    name: 'Awantura w Pubie',
    bg: 'battle_pub_bg',
    music: 'ch01_battle',
    enemies: ['autoTuneHipster', 'drogiePiwo'],
    battleTitle: 'BAROWA BÓJKA',
    returnScene: 'World',
  },
  karkAmbush: {
    id: 'karkAmbush',
    name: 'Szef Ochrony Kark',
    bg: 'battle_alley_bg',
    music: 'ch01_battle',
    enemies: ['kark', 'straznik'],
    battleTitle: 'BOSS: SZEF OCHRONY KARK',
    returnScene: 'World',
    retryOnDefeat: true,
    rewards: {
      bonusItems: ['zimnyBrowar', 'kebab', 'elektrolity'],
    },
  },
  finalBossRift: {
    id: 'finalBossRift',
    name: 'Korpo-Deworator',
    bg: 'battle_rift_bg',
    music: 'ch09_finalboss',
    enemies: ['panJanusz', 'kredyt', 'audyt', 'rwaKulszowa'],
    battleTitle: 'FINAŁ: KORPO-DEWORATOR',
    returnScene: 'Outro',
    retryOnDefeat: true,
  },
};

/**
 * Universal battle launcher supporting registered encounter IDs and ad-hoc inline parameters.
 *
 * Examples:
 *   startBattle(this, 'sasiadBoss', { state: this.state });
 *   startBattle(this, { state: this.state, bg: 'battle_pub_bg', enemies: ['drogiePiwo'] });
 */
export function startBattle(
  callerScene: Phaser.Scene,
  encounterOrParams: string | BattleParams,
  overrides?: Partial<BattleParams>
): void {
  let finalParams: BattleParams;

  if (typeof encounterOrParams === 'string') {
    const preset = ENCOUNTERS[encounterOrParams];
    if (!preset) {
      console.warn(`[startBattle] Encounter "${encounterOrParams}" not found in registry. Using default fallback.`);
      finalParams = {
        enemies: ['bolKregoslupa'],
        bg: 'battle_apartment_bg',
        music: 'ch01_battle',
        ...(overrides ?? {}),
      };
    } else {
      finalParams = {
        ...preset,
        ...(overrides ?? {}),
      };
    }
  } else {
    finalParams = {
      ...encounterOrParams,
      ...(overrides ?? {}),
    };
  }

  callerScene.scene.start('Battle', finalParams);
}
