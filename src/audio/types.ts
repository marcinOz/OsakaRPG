/**
 * Audio-local extensions of the shared SongDef / SongTrack contracts (src/types.ts).
 * A ChipSong IS a SongDef (structurally assignable), it only adds optional synth hints.
 *
 * Pattern token grammar (each array slot = one 16th step, `null` = nothing new):
 *   "C4"            single note (default length = track.len ?? 1 step)
 *   "C4:4"          note held 4 steps
 *   "A3+C4+E4:16"   chord (all notes share the length suffix)
 *   drums: "x" normal hit, "X" accent, "g" ghost (quiet), "o" open hat / long noise
 */
import type { SongDef, SongTrack } from '@/types';

export interface ChipTrack extends SongTrack {
  /** default note length in steps (when no ":n" suffix). */
  len?: number;
  /** attack seconds */
  attack?: number;
  /** release seconds */
  release?: number;
  /** if set → plucky envelope: exponential decay time constant (s) instead of sustain */
  decay?: number;
  /** lowpass cutoff Hz (saw / pad / pulse) */
  cutoff?: number;
  /** detune in cents for pad voices / chorus */
  detune?: number;
  /** stereo pan -1..1 */
  pan?: number;
}

export interface ChipSong extends SongDef {
  tracks: ChipTrack[];
  /** default loop behaviour (playSong opts override) */
  loop?: boolean;
  /** vinyl crackle layer level 0..1 */
  crackle?: number;
  /** cricket night texture level 0..1 */
  crickets?: number;
}

export type SfxName =
  | 'cursor' | 'confirm' | 'cancel' | 'blip' | 'hit' | 'crit' | 'miss' | 'heal' | 'buff'
  | 'debuff' | 'ko' | 'levelup' | 'notification' | 'door' | 'step' | 'encounter'
  | 'steelWall' | 'frameTrap' | 'smokeScreen' | 'bassBlast' | 'wildernessSurvival'
  | 'aquaRescue' | 'fireCrackle';

export interface SfxOpts {
  /** pitch multiplier (1 = default). Values >= 20 are interpreted as an absolute Hz base. */
  pitch?: number;
  /** extra volume multiplier */
  vol?: number;
}

/** Turn "C4 . . E4:2 . G4" into a 16-slot pattern ('.' / '_' = null, '|' ignored). */
export function seq(s: string, steps = 16): (string | null)[] {
  const out: (string | null)[] = s
    .trim()
    .split(/\s+/)
    .filter((t) => t !== '|' && t !== '')
    .map((t) => (t === '.' || t === '_' ? null : t));
  while (out.length < steps) out.push(null);
  return out.slice(0, steps);
}

/** Character drum pattern: "x...x...X...x.g." → 16 slots. */
export function drum(s: string, steps = 16): (string | null)[] {
  const out: (string | null)[] = s
    .replace(/[\s|]/g, '')
    .split('')
    .map((c) => (c === '.' || c === '-' ? null : c));
  while (out.length < steps) out.push(null);
  return out.slice(0, steps);
}

/** Empty (rest) bar. */
export const REST = (steps = 16): (string | null)[] => new Array(steps).fill(null);
