import type { HeroId } from '@/types';
import type { ChronicleShot, CamKey, EaseName } from '@/content/chronicle';
import { CHRONICLE_DEFAULT_LEADER } from '@/content/chronicle';

export interface TimelineState {
  shotIdx: number;
  prevIdx: number;
  localMs: number;
  t: number;
  transitionAlpha: number;
  enteredShot: boolean;
  done: boolean;
}

export interface CamXform {
  x: number;
  y: number;
  zoom: number;
}

export interface Rect {
  x: number;
  y: number;
  w: number;
  h: number;
}

export interface GradeKey {
  t: number;
  mul?: string | number;
  add?: string | number;
  sat?: number;
}

export interface GradeOutput {
  mul: number;
  add: number;
  sat: number;
}

const VIEW_W = 1024;
const VIEW_H = 576;

export class ChronicleTimeline {
  readonly state: TimelineState = {
    shotIdx: 0,
    prevIdx: -1,
    localMs: 0,
    t: 0,
    transitionAlpha: 1,
    enteredShot: true,
    done: false,
  };

  readonly totalMs: number;
  private readonly startTimes: number[] = [];
  private currentGlobalMs = 0;
  private pendingEnter = false;

  constructor(readonly shots: readonly ChronicleShot[]) {
    let accum = 0;
    for (let i = 0; i < shots.length; i++) {
      this.startTimes.push(accum);
      accum += shots[i].durationMs;
    }
    this.totalMs = accum;
  }

  shotStartMs(idx: number): number {
    if (idx < 0) return 0;
    if (idx >= this.startTimes.length) return this.totalMs;
    return this.startTimes[idx];
  }

  tick(deltaMs: number): TimelineState {
    if (this.state.done) {
      this.state.enteredShot = false;
      return this.state;
    }

    this.currentGlobalMs += deltaMs;

    if (this.currentGlobalMs >= this.totalMs) {
      this.state.shotIdx = this.shots.length - 1;
      this.state.localMs = this.shots[this.state.shotIdx].durationMs;
      this.state.t = 1;
      this.state.transitionAlpha = 1;
      this.state.enteredShot = false;
      this.state.done = true;
      return this.state;
    }

    // Determine current shot
    let newIdx = 0;
    for (let i = this.startTimes.length - 1; i >= 0; i--) {
      if (this.currentGlobalMs >= this.startTimes[i]) {
        newIdx = i;
        break;
      }
    }

    const shot = this.shots[newIdx];
    const localMs = this.currentGlobalMs - this.startTimes[newIdx];
    const transMs = shot.transitionMs ?? 700;

    let entered = false;
    if (newIdx !== this.state.shotIdx || this.pendingEnter) {
      this.state.prevIdx = this.state.shotIdx !== newIdx ? this.state.shotIdx : -1;
      this.state.shotIdx = newIdx;
      entered = true;
      this.pendingEnter = false;
    }

    this.state.localMs = localMs;
    this.state.t = Math.min(1, Math.max(0, localMs / shot.durationMs));
    this.state.transitionAlpha = transMs > 0 ? Math.min(1, Math.max(0, localMs / transMs)) : 1;
    this.state.enteredShot = entered;

    return this.state;
  }

  skipToNext(): void {
    if (this.state.done) return;
    const nextIdx = this.state.shotIdx + 1;
    if (nextIdx >= this.shots.length) {
      this.currentGlobalMs = this.totalMs;
      this.state.done = true;
      this.state.enteredShot = false;
    } else {
      this.currentGlobalMs = this.startTimes[nextIdx];
      this.pendingEnter = true;
      this.tick(0);
    }
  }

  seek(ms: number): void {
    this.currentGlobalMs = Math.max(0, Math.min(this.totalMs, ms));
    this.pendingEnter = true;
    this.tick(0);
  }
}

function easeValue(t: number, ease?: EaseName): number {
  const clamped = Math.max(0, Math.min(1, t));
  if (ease === 'quadOut') {
    return 1 - (1 - clamped) * (1 - clamped);
  }
  if (ease === 'linear') {
    return clamped;
  }
  // Default: sineInOut
  return -(Math.cos(Math.PI * clamped) - 1) / 2;
}

/**
 * Ken Burns interpolation with safety bounds clamping:
 * Ensures the camera view never moves outside the [0, VIEW_W] x [0, VIEW_H] canvas boundary.
 */
export function kenBurns(
  from: CamKey,
  to: CamKey,
  t: number,
  ease: EaseName = 'sineInOut',
  out: CamXform = { x: 0, y: 0, zoom: 1 }
): CamXform {
  const p = easeValue(t, ease);
  const zoom = Math.max(1.0, from.zoom + (to.zoom - from.zoom) * p);
  const rawX = from.x + (to.x - from.x) * p;
  const rawY = from.y + (to.y - from.y) * p;

  // View half dimensions in source pixel coordinates
  const halfW = VIEW_W / (2 * zoom);
  const halfH = VIEW_H / (2 * zoom);

  // Clamp focus point so edges are always covered
  out.zoom = zoom;
  out.x = Math.max(halfW, Math.min(VIEW_W - halfW, rawX));
  out.y = Math.max(halfH, Math.min(VIEW_H - halfH, rawY));

  return out;
}

/**
 * Returns the source rectangle visible on screen for a given camera transform.
 */
export function visibleRect(cam: CamXform, out: Rect = { x: 0, y: 0, w: 0, h: 0 }): Rect {
  const halfW = VIEW_W / (2 * cam.zoom);
  const halfH = VIEW_H / (2 * cam.zoom);
  out.x = cam.x - halfW;
  out.y = cam.y - halfH;
  out.w = halfW * 2;
  out.h = halfH * 2;
  return out;
}

/**
 * Grid-snapped parallax offset calculation.
 */
export function parallaxOffset(
  camX: number,
  camY: number,
  factor: number,
  pixelScale = 2,
  out: { x: number; y: number } = { x: 0, y: 0 }
): { x: number; y: number } {
  const centerDiffX = (camX - VIEW_W / 2) * (factor - 1.0);
  const centerDiffY = (camY - VIEW_H / 2) * (factor - 1.0);

  // Quantize strictly to integer multiples of pixelScale
  const step = Math.max(1, Math.round(pixelScale));
  out.x = Math.round(centerDiffX / step) * step || 0;
  out.y = Math.round(centerDiffY / step) * step || 0;
  return out;
}

/**
 * Crew present up to shotIdx.
 * Leader always comes first, followed by joins up to this shot (excluding duplicate leader).
 */
export function crewAtShot(
  shots: readonly ChronicleShot[],
  shotIdx: number,
  leader: HeroId = CHRONICLE_DEFAULT_LEADER
): HeroId[] {
  const result: HeroId[] = [leader];
  const seen = new Set<HeroId>([leader]);

  for (let i = 0; i <= shotIdx && i < shots.length; i++) {
    const joins = shots[i].joins;
    if (joins) {
      for (const hid of joins) {
        if (!seen.has(hid)) {
          seen.add(hid);
          result.push(hid);
        }
      }
    }
  }

  return result;
}

/**
 * Heroes joining on this specific shot (excluding the current leader if they are in this group).
 */
export function joinersAtShot(
  shots: readonly ChronicleShot[],
  shotIdx: number,
  leader: HeroId = CHRONICLE_DEFAULT_LEADER
): HeroId[] {
  if (shotIdx < 0 || shotIdx >= shots.length) return [];
  const joins = shots[shotIdx].joins;
  if (!joins) return [];
  return joins.filter((hid) => hid !== leader);
}

/**
 * Character count revealed at a given elapsed time.
 */
export function typewriterCount(
  len: number,
  elapsedMs: number,
  cps = 35,
  delayMs = 300
): number {
  if (elapsedMs <= delayMs) return 0;
  const activeMs = elapsedMs - delayMs;
  const chars = Math.floor((activeMs / 1000) * cps);
  return Math.min(len, Math.max(0, chars));
}

/**
 * Simple pseudo-random hash for deterministic procedural noise.
 */
function hashNoise(seed: number, t: number): number {
  const v = Math.sin(seed * 12.9898 + t * 78.233) * 43758.5453;
  return v - Math.floor(v);
}

/**
 * Deterministic light flicker generator.
 * Output: normalized 0..1 intensity.
 */
export function flicker(style: string, seed: number, timeMs: number): number {
  const sec = timeMs / 1000;
  switch (style) {
    case 'candle': {
      // Warm organic jitter
      const n1 = hashNoise(seed, Math.floor(sec * 12));
      const n2 = Math.sin(sec * 7.5 + seed);
      return 0.7 + 0.3 * (0.6 * n1 + 0.4 * (n2 * 0.5 + 0.5));
    }
    case 'neonBuzz': {
      // Mostly steady at 1.0, rare micro-dropouts
      const n = hashNoise(seed, Math.floor(sec * 24));
      return n > 0.92 ? 0.2 + 0.3 * n : 0.95 + 0.05 * hashNoise(seed + 1, Math.floor(sec * 8));
    }
    case 'fluorescentStutter': {
      // Periodic flickering with occasional dull phases
      const period = Math.floor(sec * 15);
      const spike = hashNoise(seed, period);
      return spike > 0.85 ? 0.3 : 0.9 + 0.1 * hashNoise(seed + 2, period);
    }
    case 'lightning': {
      // Mostly zero, sharp lightning strikes
      const burstWindow = (timeMs % 4000) / 4000;
      if (burstWindow > 0.15 && burstWindow < 0.22) {
        return hashNoise(seed, Math.floor(timeMs / 40)) > 0.3 ? 1.0 : 0.0;
      }
      return 0.0;
    }
    case 'monitor': {
      // Scanline hum
      return 0.88 + 0.12 * Math.sin(sec * 18 + seed);
    }
    case 'sunBloom': {
      // Slow breathing
      return 0.85 + 0.15 * Math.sin(sec * 1.5 + seed);
    }
    case 'pulse': {
      return 0.5 + 0.5 * Math.sin(sec * 3.14159 + seed);
    }
    case 'steady':
    default:
      return 1.0;
  }
}

/**
 * Calculates phase 0..1 based on song BPM.
 */
export function beatPhase(bpm: number, timeMs: number): number {
  if (bpm <= 0) return 0;
  const beatDurationMs = (60 / bpm) * 1000;
  return (timeMs % beatDurationMs) / beatDurationMs;
}
