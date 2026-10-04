import type { HeroId, GameData, HeroState } from '@/types';
import { HEROES } from '@/content/heroes';
import { heroStatsAtLevel, xpForLevel } from './Stats';

export interface ChapterDevDef {
  id: number;
  title: string;
  subtitle: string;
  location: string;
  targetScene: 'World' | 'Campfire' | 'Battle' | 'Outro';
  mapId?: string;
  x?: number;
  y?: number;
  facing?: 'up' | 'down' | 'left' | 'right';
  recommendedLevel: number;
  battleEncounterId?: string;
}

export const ALL_HERO_IDS: HeroId[] = ['danny', 'alior', 'lisu', 'barti', 'oziem', 'luki'];

export const CHAPTER_DEV_REGISTRY: ChapterDevDef[] = [
  {
    id: 1,
    title: 'Rozdział 1',
    subtitle: 'Kac Gigant i Powiadomienie',
    location: 'Mieszkanie',
    targetScene: 'World',
    mapId: 'apartment',
    x: 4,
    y: 5,
    facing: 'down',
    recommendedLevel: 1,
  },
  {
    id: 2,
    title: 'Rozdział 2',
    subtitle: 'Garażowy Krąg Walki (UFC)',
    location: 'Podziemny Garaż',
    targetScene: 'World',
    mapId: 'garage',
    x: 3,
    y: 7,
    facing: 'down',
    recommendedLevel: 2,
  },
  {
    id: 3,
    title: 'Rozdział 3',
    subtitle: 'Vinyl & Stare Bity',
    location: 'Pub Czarny Krążek',
    targetScene: 'World',
    mapId: 'pub',
    x: 2,
    y: 7,
    facing: 'right',
    recommendedLevel: 3,
  },
  {
    id: 4,
    title: 'Rozdział 4',
    subtitle: 'Nocny Patrol i Lisu',
    location: 'Zaułki Starówki',
    targetScene: 'World',
    mapId: 'alley',
    x: 2,
    y: 5,
    facing: 'right',
    recommendedLevel: 4,
  },
  {
    id: 5,
    title: 'Rozdział 5',
    subtitle: 'Wodny Ratunek Łukiego',
    location: 'Przystań Marina',
    targetScene: 'World',
    mapId: 'marina',
    x: 2,
    y: 7,
    facing: 'right',
    recommendedLevel: 5,
  },
  {
    id: 6,
    title: 'Rozdział 6',
    subtitle: 'Leśne Obozowisko Oziema',
    location: 'Głęboki Las',
    targetScene: 'World',
    mapId: 'forest',
    x: 3,
    y: 5,
    facing: 'down',
    recommendedLevel: 6,
  },
  {
    id: 7,
    title: 'Rozdział 7',
    subtitle: 'Ognisko i Złote Czasy',
    location: 'Nocne Ognisko',
    targetScene: 'Campfire',
    recommendedLevel: 7,
  },
  {
    id: 8,
    title: 'Rozdział 8',
    subtitle: 'Błękitny Ogień & Janusz',
    location: 'Mglisty Las',
    targetScene: 'Campfire',
    recommendedLevel: 8,
  },
  {
    id: 9,
    title: 'Rozdział 9',
    subtitle: 'Ostateczna Batalia o Wolność',
    location: 'Wymiar Korporacji',
    targetScene: 'Battle',
    battleEncounterId: 'finalBossRift',
    recommendedLevel: 9,
  },
  {
    id: 10,
    title: 'Rozdział 10',
    subtitle: 'Legenda Wiecznie Żywa',
    location: 'Jezioro Powidzkie',
    targetScene: 'Outro',
    recommendedLevel: 10,
  },
];

export interface DevWarpConfig {
  state: GameData;
  targetScene: 'World' | 'Campfire' | 'Battle' | 'Outro';
  battleEncounterId?: string;
  startAtJanusz?: boolean;
}

/**
 * Creates a deterministic, valid GameData state for any chapter and leader.
 * Pure logic — 100% headless testable with Vitest without Phaser/DOM.
 */
export function createDevChapterState(leader: HeroId, chapterId: number): DevWarpConfig {
  const chapterDef = CHAPTER_DEV_REGISTRY.find((c) => c.id === chapterId) ?? CHAPTER_DEV_REGISTRY[0];
  const level = chapterDef.recommendedLevel;

  // 1. Build Storyline Party
  const party: HeroId[] = [leader];
  const addRecruits = (candidates: HeroId[]) => {
    for (const c of candidates) {
      if (!party.includes(c)) party.push(c);
    }
  };

  if (chapterId >= 3) addRecruits(['danny', 'alior']);
  if (chapterId >= 4) addRecruits(['barti']);
  if (chapterId >= 5) addRecruits(['lisu']);
  if (chapterId >= 6) addRecruits(['luki']);
  if (chapterId >= 7) addRecruits(['oziem']);

  // 2. Initialize Roster with Scaled Stats
  const roster = {} as Record<HeroId, HeroState>;
  for (const hid of ALL_HERO_IDS) {
    const def = HEROES[hid];
    const stats = heroStatsAtLevel(def, level);
    roster[hid] = {
      level,
      xp: xpForLevel(level),
      hp: stats.hp,
      mp: stats.mp,
    };
  }

  // 3. Flags based on chapter storyline progression
  const flags: Record<string, any> = {};
  if (chapterId >= 2) {
    flags.ch1_woke_up = true;
    flags.ch1_fought_spine = true;
    flags.ch1_spine_reported = true;
    flags.ch1_fought_slack = true;
    flags.ch1_slack_reported = true;
    flags.bought_coffee = true;
  }
  if (chapterId >= 3) {
    flags.fought_sasiad = true;
    flags.danny_alior_joined = true;
  }
  if (chapterId >= 4) {
    flags.fought_hipsters = true;
    flags.barti_joined = true;
  }
  if (chapterId >= 5) {
    flags.fought_kark = true;
    flags.lisu_joined = true;
  }
  if (chapterId >= 6) {
    flags.luki_saved = true;
    flags.boat_crossed = true;
    flags.luki_joined = true;
  }
  if (chapterId >= 7) {
    flags.oziem_joined = true;
  }
  if (chapterId >= 8) {
    flags.campfire_toast_done = true;
  }

  // 4. Consumable Inventory
  const inventory: Record<string, number> =
    chapterId === 1
      ? { kawa: 1, piwo: 1 }
      : chapterId === 2
      ? { kawa: 2, piwo: 2, hotDog: 1, elektrolity: 1 }
      : chapterId <= 4
      ? {
          kawa: 3,
          piwo: 3,
          hotDog: 2,
          kebab: 2,
          zimnyBrowar: 2,
          elektrolity: 2,
        }
      : {
          kawa: 4,
          piwo: 4,
          hotDog: 3,
          kebab: 4,
          zimnyBrowar: 4,
          elektrolity: 3,
        };

  // 5. Build State
  const state: GameData = {
    version: 1,
    leader,
    party,
    roster,
    inventory,
    chapter: chapterId,
    mapId: chapterDef.mapId ?? 'apartment',
    x: chapterDef.x ?? 4,
    y: chapterDef.y ?? 5,
    facing: chapterDef.facing ?? 'down',
    flags,
    worldStatuses: chapterId === 1 ? ['kacGigant'] : [],
    playtime: (chapterId - 1) * 900,
    timestamp: Date.now(),
  };

  return {
    state,
    targetScene: chapterDef.targetScene,
    battleEncounterId: chapterDef.battleEncounterId,
    startAtJanusz: chapterId === 8,
  };
}
