import type { HeroId } from '@/types';

export type ChronicleTransition =
  | 'fadeBlack'
  | 'pixelReveal'
  | 'iris'
  | 'dither'
  | 'morph'
  | 'datamosh'
  | 'filmBurn'
  | 'flash';

export type EaseName = 'sineInOut' | 'quadOut' | 'linear';

export interface CamKey {
  x: number;
  y: number;
  zoom: number;
}

export interface ChronicleActor {
  kind: 'crew' | 'enemy';
  ref: string;
  from: [number, number];
  to?: [number, number];
  enterAtMs?: number;
  exitAtMs?: number;
}

export interface SfxCue {
  atMs: number;
  id: string;
}

export interface ChronicleShot {
  id: string;
  scene: string; // matches folder name in public/assets/chronicle/<scene>/ and spec file
  bg: string;    // fallback image key in manifest.json if chronicle asset not yet loaded
  durationMs: number;
  cam: {
    from: CamKey;
    to: CamKey;
    ease?: EaseName;
  };
  tag: string;
  caption: string;
  music?: string;
  transitionIn: ChronicleTransition;
  transitionMs?: number;
  joins?: HeroId[];
  sfxCues?: SfxCue[];
  actors?: ChronicleActor[];
  tint?: number;
  beatSync?: number;
}

export const CHRONICLE_JOIN_ORDER: HeroId[][] = [
  ['danny', 'alior'],
  ['barti'],
  ['lisu'],
  ['luki'],
  ['oziem'],
];

export const CHRONICLE_DEFAULT_LEADER: HeroId = 'oziem';

export const CHRONICLE_SHOTS: readonly ChronicleShot[] = [
  // Shot 0: 2006 Flashback (Generated Scene)
  {
    id: 'shot_00_flashback',
    scene: 'flashback_2006',
    bg: 'city_bg',
    durationMs: 7000,
    cam: {
      from: { x: 512, y: 300, zoom: 1.05 },
      to: { x: 530, y: 320, zoom: 1.12 },
      ease: 'sineInOut',
    },
    tag: '2006 · POCZĄTEK',
    caption: '2006. Ławka pod blokiem. Tu wszystko się zaczęło.',
    music: 'title',
    transitionIn: 'fadeBlack',
    transitionMs: 1200,
    sfxCues: [{ atMs: 500, id: 'step' }],
  },
  // Shot 1: Night Lake Title
  {
    id: 'shot_01_lake',
    scene: 'title_lake',
    bg: 'title_bg',
    durationMs: 7000,
    cam: {
      from: { x: 512, y: 300, zoom: 1.04 },
      to: { x: 620, y: 330, zoom: 1.14 },
      ease: 'sineInOut',
    },
    tag: '20 LAT PÓŹNIEJ · KRONIKA EKIPY',
    caption: 'Dwadzieścia lat przyjaźni. Jedna niezapomniana noc.',
    music: 'title',
    transitionIn: 'iris',
    transitionMs: 900,
    sfxCues: [{ atMs: 2500, id: 'blip' }],
  },
  // Shot 2: Apartment (Clean plate, Chapter 1)
  {
    id: 'shot_02_apartment',
    scene: 'apartment',
    bg: 'battle_apartment_bg',
    durationMs: 7000,
    cam: {
      from: { x: 600, y: 330, zoom: 1.08 },
      to: { x: 720, y: 360, zoom: 1.15 },
      ease: 'sineInOut',
    },
    tag: 'ROZDZIAŁ 1 · KAC GIGANT',
    caption: 'Sobota, 2026. Telefon wibruje — chłopaki już piszą na grupie.',
    music: 'ch01_explore',
    transitionIn: 'dither',
    transitionMs: 700,
    sfxCues: [
      { atMs: 600, id: 'notification' },
      { atMs: 1800, id: 'notification' },
    ],
    actors: [
      {
        kind: 'enemy',
        ref: 'bolKregoslupa',
        from: [760, 380],
        enterAtMs: 3500,
        exitAtMs: 5800,
      },
    ],
  },
  // Shot 3: Morning City
  {
    id: 'shot_03_city',
    scene: 'city',
    bg: 'battle_city_bg',
    durationMs: 7000,
    cam: {
      from: { x: 480, y: 320, zoom: 1.05 },
      to: { x: 640, y: 340, zoom: 1.14 },
      ease: 'sineInOut',
    },
    tag: 'PORANNE MIASTO',
    caption: 'Kręgosłup rozruszany, Slack zamknięty. Czas zebrać ekipę.',
    music: 'ch01_explore',
    transitionIn: 'dither',
    transitionMs: 700,
    actors: [
      {
        kind: 'crew',
        ref: 'walkers',
        from: [40, 480],
        to: [420, 480],
        enterAtMs: 800,
      },
    ],
  },
  // Shot 4: Garage (Chapter 2) - Danny & Alior join
  {
    id: 'shot_04_garage',
    scene: 'garage',
    bg: 'battle_garage_bg',
    durationMs: 7000,
    cam: {
      from: { x: 500, y: 300, zoom: 1.05 },
      to: { x: 600, y: 330, zoom: 1.15 },
      ease: 'sineInOut',
    },
    tag: 'ROZDZIAŁ 2 · GARAŻOWY KRĄG WALKI',
    caption: 'Danny i Alior. Żelazna defensywa, klatka UFC i zero lagów.',
    music: 'ch02_garage',
    transitionIn: 'dither',
    transitionMs: 700,
    joins: ['danny', 'alior'],
    sfxCues: [
      { atMs: 2200, id: 'steelWall' },
      { atMs: 3800, id: 'frameTrap' },
    ],
    actors: [
      {
        kind: 'enemy',
        ref: 'sasiadSzkodnik',
        from: [820, 420],
        enterAtMs: 1200,
        exitAtMs: 3400,
      },
    ],
  },
  // Shot 5: Pub Czarny Krążek (Chapter 3) - Barti joins
  {
    id: 'shot_05_pub',
    scene: 'pub',
    bg: 'battle_pub_bg',
    durationMs: 7000,
    cam: {
      from: { x: 512, y: 320, zoom: 1.05 },
      to: { x: 512, y: 350, zoom: 1.16 },
      ease: 'sineInOut',
    },
    tag: 'ROZDZIAŁ 3 · VINYL & STARE BITY',
    caption: 'Barti wrzuca winyl. Auto-Tune nie przetrwał pierwszego dropu.',
    music: 'ch03_pub',
    beatSync: 90,
    transitionIn: 'dither',
    transitionMs: 700,
    joins: ['barti'],
    sfxCues: [{ atMs: 2500, id: 'bassBlast' }],
  },
  // Shot 6: Alley (Chapter 4) - Lisu joins
  {
    id: 'shot_06_alley',
    scene: 'alley',
    bg: 'battle_alley_bg',
    durationMs: 7000,
    cam: {
      from: { x: 520, y: 300, zoom: 1.06 },
      to: { x: 470, y: 330, zoom: 1.15 },
      ease: 'sineInOut',
    },
    tag: 'ROZDZIAŁ 4 · NOCNY PATROL',
    caption: 'Lisu zniknął we mgle. Kark i Straż Miejska stanęli na drodze.',
    music: 'ch04_alley',
    transitionIn: 'dither',
    transitionMs: 700,
    joins: ['lisu'],
    sfxCues: [{ atMs: 2600, id: 'smokeScreen' }],
    actors: [
      {
        kind: 'enemy',
        ref: 'kark',
        from: [780, 420],
        enterAtMs: 1000,
        exitAtMs: 3000,
      },
    ],
  },
  // Shot 7: Marina (Chapter 5) - Łuki joins
  {
    id: 'shot_07_marina',
    scene: 'marina',
    bg: 'battle_marina_bg',
    durationMs: 7000,
    cam: {
      from: { x: 512, y: 310, zoom: 1.05 },
      to: { x: 560, y: 340, zoom: 1.14 },
      ease: 'sineInOut',
    },
    tag: 'ROZDZIAŁ 5 · MISJA NAD RZEKĄ',
    caption: 'Łuki zatankował łódź. Kamizelki są. Nikt nie skacze po shotach!',
    music: 'ch05_marina',
    transitionIn: 'dither',
    transitionMs: 700,
    joins: ['luki'],
    sfxCues: [{ atMs: 2400, id: 'aquaRescue' }],
  },
  // Shot 8: Forest Camp (Chapter 6) - Oziem joins
  {
    id: 'shot_08_forest',
    scene: 'forest',
    bg: 'battle_forest_bg',
    durationMs: 7000,
    cam: {
      from: { x: 480, y: 320, zoom: 1.06 },
      to: { x: 540, y: 350, zoom: 1.15 },
      ease: 'sineInOut',
    },
    tag: 'ROZDZIAŁ 6 · LEŚNE OBOZOWISKO',
    caption: 'Za jeziorem, w głębi wilczego lasu, czekał Oziem i ogień.',
    music: 'camp',
    transitionIn: 'dither',
    transitionMs: 700,
    joins: ['oziem'],
    sfxCues: [{ atMs: 2200, id: 'wildernessSurvival' }],
  },
  // Shot 9: Campfire Reunion (Chapter 7) - All 6 sit
  {
    id: 'shot_09_campfire',
    scene: 'campfire',
    bg: 'campfire_bg',
    durationMs: 8000,
    cam: {
      from: { x: 512, y: 320, zoom: 1.05 },
      to: { x: 512, y: 360, zoom: 1.15 },
      ease: 'sineInOut',
    },
    tag: 'ROZDZIAŁ 7 · OGNISKO, RAP I ZŁOTE CZASY',
    caption: 'Sześciu. Znowu razem przy jednym ogniu. Jak dwadzieścia lat temu.',
    music: 'camp',
    transitionIn: 'fadeBlack',
    transitionMs: 800,
    sfxCues: [{ atMs: 500, id: 'fireCrackle' }],
  },
  // Shot 10: Curse of Adulthood (Chapter 8) - Blue fire transformation
  {
    id: 'shot_10_curse',
    scene: 'curse',
    bg: 'campfire_bg',
    durationMs: 7500,
    cam: {
      from: { x: 512, y: 340, zoom: 1.12 },
      to: { x: 512, y: 320, zoom: 1.20 },
      ease: 'sineInOut',
    },
    tag: 'ROZDZIAŁ 8 · KLĄTWA DOROSŁOŚCI',
    caption: 'Płomień zgasł... i zapłonął upiornym, lodowatym błękitem!',
    music: 'ch08_industrial',
    transitionIn: 'morph',
    transitionMs: 1000,
    sfxCues: [
      { atMs: 400, id: 'debuff' },
      { atMs: 2500, id: 'encounter' },
    ],
    actors: [
      {
        kind: 'enemy',
        ref: 'panJanusz',
        from: [512, 380],
        enterAtMs: 2600,
        exitAtMs: 6500,
      },
    ],
  },
  // Shot 11: Rift Battle (Chapter 9) - Boss battle climax
  {
    id: 'shot_11_rift',
    scene: 'rift',
    bg: 'battle_rift_bg',
    durationMs: 8500,
    cam: {
      from: { x: 512, y: 300, zoom: 1.08 },
      to: { x: 512, y: 320, zoom: 1.20 },
      ease: 'quadOut',
    },
    tag: 'ROZDZIAŁ 9 · OSTATECZNA BATALIA',
    caption: 'Rzeczywistość pękła! Kredyt, Audyt, Rwa Kulszowa i Pan Janusz!',
    music: 'ch09_finalboss',
    transitionIn: 'datamosh',
    transitionMs: 800,
    sfxCues: [
      { atMs: 300, id: 'hit' },
      { atMs: 2200, id: 'crit' },
      { atMs: 4500, id: 'bassBlast' },
      { atMs: 7200, id: 'levelup' },
    ],
  },
  // Shot 12: Sunrise Epilogue (Chapter 10)
  {
    id: 'shot_12_sunrise',
    scene: 'sunrise',
    bg: 'sunrise_bg',
    durationMs: 8000,
    cam: {
      from: { x: 512, y: 300, zoom: 1.05 },
      to: { x: 512, y: 330, zoom: 1.15 },
      ease: 'sineInOut',
    },
    tag: 'ROZDZIAŁ 10 · LEGENDA WIECZNIE ŻYWA',
    caption: 'Mgła opadła. Złote promienie słońca zalały jezioro. Przetrwaliśmy.',
    music: 'ch10_sunrise',
    transitionIn: 'filmBurn',
    transitionMs: 900,
  },
  // Shot 13: Commemorative Photo & Final Bookend
  {
    id: 'shot_13_photo',
    scene: 'photo',
    bg: 'memorial_photo',
    durationMs: 9000,
    cam: {
      from: { x: 512, y: 288, zoom: 1.03 },
      to: { x: 512, y: 288, zoom: 1.10 },
      ease: 'sineInOut',
    },
    tag: '★ FRIEND PACK ANALYZER · 2006 – 2026 ★',
    caption: '[KLIK!] Prawdziwa ekipa jest wieczna. Do zobaczenia przy kolejnym ognisku!',
    music: 'ch10_sunrise',
    transitionIn: 'flash',
    transitionMs: 800,
    sfxCues: [{ atMs: 300, id: 'confirm' }],
  },
];
