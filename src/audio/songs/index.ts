import type { ChipSong } from '../types';
import { seq, drum } from '../types';

export const TITLE_SONG: ChipSong = {
  id: 'title',
  label: 'THE PACK – Main Theme',
  bpm: 78,
  steps: 16,
  tracks: [
    {
      inst: 'triangle',
      vol: 0.7,
      patterns: [
        seq('C3 . . . G2 . . . A2 . . . F2 . . .'),
        seq('C3 . . . G2 . . . A2 . . . G2 . . .'),
      ],
      order: [0, 1],
    },
    {
      inst: 'pulse',
      vol: 0.45,
      duty: 0.25,
      patterns: [
        seq('E4 . G4 . C5:2 . B4 . A4 . G4 . E4 .'),
        seq('D4 . F4 . A4:2 . G4 . F4 . E4 . D4 .'),
      ],
      order: [0, 1],
    },
    {
      inst: 'pad',
      vol: 0.3,
      patterns: [
        seq('C4+E4+G4:16'),
        seq('A3+C4+E4:16'),
        seq('F3+A3+C4:16'),
        seq('G3+B3+D4:16'),
      ],
      order: [0, 1, 2, 3],
    },
    {
      inst: 'hat',
      vol: 0.18,
      patterns: [
        drum('x.x.x.x.x.x.x.x.'),
      ],
      order: [0],
    },
  ],
};

export const ANALYZER_SONG: ChipSong = {
  id: 'analyzer',
  label: 'Friend Pack Analyzer v1.0',
  bpm: 110,
  steps: 16,
  tracks: [
    {
      inst: 'saw',
      vol: 0.35,
      patterns: [
        seq('C4 E4 G4 B4 C5 B4 G4 E4 A3 C4 E4 G4 A4 G4 E4 C4'),
        seq('F3 A3 C4 E4 F4 E4 C4 A3 G3 B3 D4 F4 G4 F4 D4 B3'),
      ],
      order: [0, 1],
    },
    {
      inst: 'triangle',
      vol: 0.6,
      patterns: [
        seq('C2 . . C2 . . C2 . A1 . . A1 . . A1 .'),
        seq('F1 . . F1 . . F1 . G1 . . G1 . . G1 .'),
      ],
      order: [0, 1],
    },
    {
      inst: 'kick',
      vol: 0.5,
      patterns: [
        drum('x...x...x...x...'),
      ],
      order: [0],
    },
    {
      inst: 'hat',
      vol: 0.2,
      patterns: [
        drum('..x...x...x...x.'),
      ],
      order: [0],
    },
  ],
};

export const CH01_EXPLORE_SONG: ChipSong = {
  id: 'ch01_explore',
  label: 'Poranek (inspirowane O.S.T.R. – Mówiłaś Mi)',
  bpm: 85,
  steps: 16,
  swing: 0.15,
  crackle: 0.12,
  tracks: [
    {
      inst: 'triangle',
      vol: 0.75,
      patterns: [
        seq('C2 . . C2 . . G1 . A1 . . A1 . . E2 .'),
        seq('F1 . . F1 . . C2 . G1 . . G1 . . B1 .'),
      ],
      order: [0, 1],
    },
    {
      inst: 'pulse',
      vol: 0.35,
      duty: 0.125,
      patterns: [
        seq('. . E4 . . G4 . . A4 . . B4 . . C5 .'),
        seq('. . B4 . . A4 . . G4 . . E4 . . D4 .'),
      ],
      order: [0, 1],
    },
    {
      inst: 'kick',
      vol: 0.6,
      patterns: [
        drum('x.....x...x.....'),
      ],
      order: [0],
    },
    {
      inst: 'snare',
      vol: 0.45,
      patterns: [
        drum('....x.......x...'),
      ],
      order: [0],
    },
    {
      inst: 'hat',
      vol: 0.22,
      patterns: [
        drum('x.x.x.x.x.x.x.x.'),
      ],
      order: [0],
    },
  ],
};

export const CH01_BATTLE_SONG: ChipSong = {
  id: 'ch01_battle',
  label: 'Batalia Blokowiska (90s Boom-Bap)',
  bpm: 92,
  steps: 16,
  swing: 0.1,
  tracks: [
    {
      inst: 'saw',
      vol: 0.45,
      patterns: [
        seq('A3 . C4 . E4 . A4 . G4:2 . E4:2 . D4:2 .'),
        seq('F3 . A3 . C4 . F4 . E4:2 . C4:2 . B3:2 .'),
      ],
      order: [0, 1],
    },
    {
      inst: 'triangle',
      vol: 0.8,
      patterns: [
        seq('A1 . . A1 . . A1 . G1 . . G1 . . G1 .'),
        seq('F1 . . F1 . . F1 . E1 . . E1 . . E1 .'),
      ],
      order: [0, 1],
    },
    {
      inst: 'kick',
      vol: 0.75,
      patterns: [
        drum('x...x.....x...x.'),
      ],
      order: [0],
    },
    {
      inst: 'snare',
      vol: 0.6,
      patterns: [
        drum('....x.......x...'),
      ],
      order: [0],
    },
    {
      inst: 'hat',
      vol: 0.25,
      patterns: [
        drum('x.x.x.x.x.x.x.x.'),
      ],
      order: [0],
    },
  ],
};

export const CAMP_SONG: ChipSong = {
  id: 'camp',
  label: 'Medley inspirowane Paktofonika / Kaliber 44 / Gural',
  bpm: 80,
  steps: 16,
  crackle: 0.2,
  crickets: 0.15,
  tracks: [
    {
      inst: 'pulse',
      vol: 0.4,
      duty: 0.5,
      patterns: [
        seq('A3 . C4 . E4 . G4 . A4:4 . . . G4:2 .'),
        seq('F3 . A3 . C4 . E4 . D4:4 . . . C4:2 .'),
      ],
      order: [0, 1],
    },
    {
      inst: 'triangle',
      vol: 0.7,
      patterns: [
        seq('A1 . . . . . A1 . F1 . . . . . F1 .'),
        seq('D1 . . . . . D1 . E1 . . . . . E1 .'),
      ],
      order: [0, 1],
    },
    {
      inst: 'pad',
      vol: 0.25,
      patterns: [
        seq('A2+C3+E3:16'),
        seq('F2+A2+C3:16'),
        seq('D2+F2+A2:16'),
        seq('E2+G#2+B2:16'),
      ],
      order: [0, 1, 2, 3],
    },
    {
      inst: 'kick',
      vol: 0.55,
      patterns: [
        drum('x.......x...x...'),
      ],
      order: [0],
    },
    {
      inst: 'snare',
      vol: 0.4,
      patterns: [
        drum('....x.......x...'),
      ],
      order: [0],
    },
  ],
};

export const VICTORY_SONG: ChipSong = {
  id: 'victory',
  label: 'Fanfara Zwycięstwa',
  bpm: 120,
  steps: 16,
  loop: false,
  tracks: [
    {
      inst: 'pulse',
      vol: 0.6,
      duty: 0.25,
      patterns: [
        seq('C4:2 E4:2 G4:2 C5:4 G4:2 C5:6'),
      ],
      order: [0],
    },
    {
      inst: 'triangle',
      vol: 0.6,
      patterns: [
        seq('C3:2 E3:2 G3:2 C4:4 G3:2 C4:6'),
      ],
      order: [0],
    },
    {
      inst: 'snare',
      vol: 0.4,
      patterns: [
        drum('x.x.x.x.x...x...'),
      ],
      order: [0],
    },
  ],
};

export const CH02_GARAGE_SONG: ChipSong = {
  id: 'ch02_garage',
  label: 'UFC Garaż (inspirowane Paktofonika – Jestem Bogiem)',
  bpm: 90,
  steps: 16,
  swing: 0.12,
  tracks: [
    {
      inst: 'triangle',
      vol: 0.8,
      patterns: [
        seq('E2 . . E2 . . G2 . A2 . . A2 . . B2 .'),
        seq('C2 . . C2 . . D2 . E2 . . E2 . . G2 .'),
      ],
      order: [0, 1],
    },
    {
      inst: 'pulse',
      vol: 0.45,
      duty: 0.25,
      patterns: [
        seq('E4:2 . G4:2 . B4:4 A4:2 . G4:2 . E4:4'),
        seq('D4:2 . F4:2 . A4:4 G4:2 . F4:2 . D4:4'),
      ],
      order: [0, 1],
    },
    {
      inst: 'kick',
      vol: 0.7,
      patterns: [
        drum('x...x.....x...x.'),
      ],
      order: [0],
    },
    {
      inst: 'snare',
      vol: 0.5,
      patterns: [
        drum('....x.......x...'),
      ],
      order: [0],
    },
    {
      inst: 'hat',
      vol: 0.2,
      patterns: [
        drum('x.x.x.x.x.x.x.x.'),
      ],
      order: [0],
    },
  ],
};

export const CH03_PUB_SONG: ChipSong = {
  id: 'ch03_pub',
  label: 'Czarny Krążek (inspirowane Kaliber 44 – Film)',
  bpm: 86,
  steps: 16,
  crackle: 0.2,
  swing: 0.18,
  tracks: [
    {
      inst: 'triangle',
      vol: 0.85,
      patterns: [
        seq('C2 . . . . . G1 . Ab1 . . . . . D2 .'),
        seq('F1 . . . . . C2 . G1 . . . . . B1 .'),
      ],
      order: [0, 1],
    },
    {
      inst: 'pad',
      vol: 0.35,
      patterns: [
        seq('C3+Eb3+G3:16'),
        seq('Ab2+C3+Eb3:16'),
        seq('F2+Ab2+C3:16'),
        seq('G2+B2+D3:16'),
      ],
      order: [0, 1, 2, 3],
    },
    {
      inst: 'saw',
      vol: 0.3,
      patterns: [
        seq('. . G4 . . Bb4 . C5:4 . . Bb4:2 . G4:2 .'),
      ],
      order: [0],
    },
    {
      inst: 'kick',
      vol: 0.65,
      patterns: [
        drum('x.....x...x.....'),
      ],
      order: [0],
    },
    {
      inst: 'snare',
      vol: 0.5,
      patterns: [
        drum('....x.......x...'),
      ],
      order: [0],
    },
  ],
};

export const CH04_ALLEY_SONG: ChipSong = {
  id: 'ch04_alley',
  label: 'Zaułki Starówki (inspirowane DonGuralesko – El Polako)',
  bpm: 90,
  steps: 16,
  swing: 0.2,
  tracks: [
    {
      inst: 'triangle',
      vol: 0.9,
      patterns: [
        seq('D2 . . D2 . . F2 . G2 . . G2 . Ab2 .'),
        seq('D2 . . D2 . . F2 . C2 . . C2 . D2 .'),
      ],
      order: [0, 1],
    },
    {
      inst: 'saw',
      vol: 0.35,
      patterns: [
        seq('D4:2 . F4:2 . G4:4 . F4:2 . D4:2 . C4:4'),
      ],
      order: [0],
    },
    {
      inst: 'kick',
      vol: 0.7,
      patterns: [
        drum('x..x..x...x.x...'),
      ],
      order: [0],
    },
    {
      inst: 'snare',
      vol: 0.55,
      patterns: [
        drum('....x.......x...'),
      ],
      order: [0],
    },
    {
      inst: 'hat',
      vol: 0.25,
      patterns: [
        drum('x.x.x.x.x.x.x.x.'),
      ],
      order: [0],
    },
  ],
};

export const CH05_MARINA_SONG: ChipSong = {
  id: 'ch05_marina',
  label: 'Przystań i Jezioro (Nocna Misja)',
  bpm: 80,
  steps: 16,
  crackle: 0.15,
  tracks: [
    {
      inst: 'pad',
      vol: 0.35,
      patterns: [
        seq('A3+C4+E4:16'),
        seq('F3+A3+C4:16'),
        seq('D3+F3+A3:16'),
        seq('E3+G3+B3:16'),
      ],
      order: [0, 1, 2, 3],
    },
    {
      inst: 'pulse',
      vol: 0.4,
      duty: 0.5,
      patterns: [
        seq('E4 . . A4 . . C5 . B4 . A4 . E4 . .'),
        seq('D4 . . F4 . . A4 . G4 . F4 . D4 . .'),
      ],
      order: [0, 1],
    },
    {
      inst: 'triangle',
      vol: 0.6,
      patterns: [
        seq('A2:8 . . . . . . . F2:8 . . . . . . .'),
      ],
      order: [0],
    },
    {
      inst: 'hat',
      vol: 0.15,
      patterns: [
        drum('..x...x...x...x.'),
      ],
      order: [0],
    },
  ],
};

export const CH08_INDUSTRIAL_SONG: ChipSong = {
  id: 'ch08_industrial',
  label: 'Klątwa Dorosłości (Industrial Synth)',
  bpm: 105,
  steps: 16,
  tracks: [
    {
      inst: 'saw',
      vol: 0.4,
      patterns: [
        seq('C3 C3 Eb3 C3 F3 C3 Gb3 C3 G3 C3 Gb3 C3 F3 C3 Eb3 C3'),
      ],
      order: [0],
    },
    {
      inst: 'triangle',
      vol: 0.85,
      patterns: [
        seq('C2:4 . . . G1:4 . . . Ab1:4 . . . F1:4 . . .'),
      ],
      order: [0],
    },
    {
      inst: 'kick',
      vol: 0.75,
      patterns: [
        drum('x...x...x...x...'),
      ],
      order: [0],
    },
    {
      inst: 'snare',
      vol: 0.6,
      patterns: [
        drum('..x...x...x...x.'),
      ],
      order: [0],
    },
  ],
};

export const CH09_FINALBOSS_SONG: ChipSong = {
  id: 'ch09_finalboss',
  label: 'Ostateczna Batalia o Wolność (O.S.T.R. vs Gural Chiptune Battle)',
  bpm: 120,
  steps: 16,
  swing: 0.12,
  tracks: [
    {
      inst: 'saw',
      vol: 0.45,
      patterns: [
        seq('C4:2 Eb4:2 G4:2 C5:2 Bb4:2 G4:2 F4:2 G4:2'),
        seq('Ab4:2 C5:2 Eb5:2 D5:2 C5:2 Bb4:2 G4:2 F4:2'),
      ],
      order: [0, 1],
    },
    {
      inst: 'pulse',
      vol: 0.35,
      duty: 0.25,
      patterns: [
        seq('C5:2 . . Bb4:2 . . G4:2 . . F4:2 . .'),
      ],
      order: [0],
    },
    {
      inst: 'triangle',
      vol: 0.9,
      patterns: [
        seq('C2 . C2 . G1 . Ab1 . . Ab1 . F1 . G1 .'),
      ],
      order: [0],
    },
    {
      inst: 'kick',
      vol: 0.75,
      patterns: [
        drum('x..x.x..x..x.x..'),
      ],
      order: [0],
    },
    {
      inst: 'snare',
      vol: 0.65,
      patterns: [
        drum('....x.......x...'),
      ],
      order: [0],
    },
    {
      inst: 'hat',
      vol: 0.3,
      patterns: [
        drum('xxxxxxxxxxxxxxxx'),
      ],
      order: [0],
    },
  ],
};

export const CH10_SUNRISE_SONG: ChipSong = {
  id: 'ch10_sunrise',
  label: 'Wschód Słońca nad Jeziorem (Epilog)',
  bpm: 72,
  steps: 16,
  crackle: 0.1,
  tracks: [
    {
      inst: 'pad',
      vol: 0.4,
      patterns: [
        seq('C3+E3+G3+B3:16'),
        seq('F3+A3+C4+E4:16'),
        seq('A2+C3+E3+G3:16'),
        seq('G2+B2+D3+F3:16'),
      ],
      order: [0, 1, 2, 3],
    },
    {
      inst: 'triangle',
      vol: 0.7,
      patterns: [
        seq('C2:8 . . . . . . . F2:8 . . . . . . .'),
        seq('A1:8 . . . . . . . G1:8 . . . . . . .'),
      ],
      order: [0, 1],
    },
    {
      inst: 'pulse',
      vol: 0.35,
      duty: 0.5,
      patterns: [
        seq('G4:4 E4:4 C5:4 B4:4'),
        seq('A4:4 F4:4 D5:4 C5:4'),
      ],
      order: [0, 1],
    },
  ],
};

export const ALL_SONGS: Record<string, ChipSong> = {
  title: TITLE_SONG,
  analyzer: ANALYZER_SONG,
  ch01_explore: CH01_EXPLORE_SONG,
  ch01_battle: CH01_BATTLE_SONG,
  ch02_garage: CH02_GARAGE_SONG,
  ch03_pub: CH03_PUB_SONG,
  ch04_alley: CH04_ALLEY_SONG,
  ch05_marina: CH05_MARINA_SONG,
  camp: CAMP_SONG,
  ch08_industrial: CH08_INDUSTRIAL_SONG,
  ch09_finalboss: CH09_FINALBOSS_SONG,
  ch10_sunrise: CH10_SUNRISE_SONG,
  victory: VICTORY_SONG,
};
