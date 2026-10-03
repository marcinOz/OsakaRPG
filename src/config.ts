/** Global render + layout constants. Internal resolution is 1024x576 (16:9), integer-scaled. */
export const GAME_W = 1024;
export const GAME_H = 576;
export const TILE = 32;

/** Master palette – UI / environment base sampled from the Friend Pack Analyzer reference. */
export const PAL = {
  void: 0x00030b,
  ink: 0x061220,
  navy: 0x0a182b,
  panel: 0x0c2134,
  panelHi: 0x102d3b,
  steel: 0x203d54,
  indigo: 0x1e2844,
  slate: 0x2e3b4d,
  teal: 0x406a6a,
  grey: 0x5e6f7a,
  taupe: 0x81797a,
  silver: 0x97a0a6,
  cyan: 0x9ecbd4,
  cyanHi: 0xc8eef4,
  white: 0xd8dada,
  brownDk: 0x4f4141,
  plum: 0x1b1319,
  yellow: 0xe8d84a,
  green: 0x5fc85a,
  fire: 0xe0742c,
  fireHi: 0xf6c04a,
  red: 0xc0392b,
  denim: 0x3f6b8f,
  blueFire: 0x4fa8ff,
} as const;

export const hex = (c: number): string => '#' + c.toString(16).padStart(6, '0');

export const FONT = 'pixel'; // bitmap font key (generated in BootScene)

export const SAVE_KEY = 'thepack.save.v1';
