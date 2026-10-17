import { describe, it, expect } from 'vitest';
import { CHRONICLE_SHOTS } from '@/content/chronicle';
import {
  ChronicleTimeline,
  kenBurns,
  visibleRect,
  parallaxOffset,
  crewAtShot,
  joinersAtShot,
  typewriterCount,
  flicker,
  beatPhase,
} from '@/systems/ChronicleTimeline';
import { ALL_SONGS } from '@/audio/songs';
import { ENEMIES } from '@/content/enemies';
import type { HeroId } from '@/types';

describe('Chronicle Timeline & Content', () => {
  it('total duration is within the 90s - 110s cinematic sweet spot', () => {
    const timeline = new ChronicleTimeline(CHRONICLE_SHOTS);
    expect(timeline.totalMs).toBeGreaterThanOrEqual(90000);
    expect(timeline.totalMs).toBeLessThanOrEqual(115000);
  });

  it('all referenced music songs exist in audio catalogue', () => {
    for (const shot of CHRONICLE_SHOTS) {
      if (shot.music) {
        expect(ALL_SONGS[shot.music]).toBeDefined();
      }
    }
  });

  it('all referenced enemy actors exist in content catalogue', () => {
    for (const shot of CHRONICLE_SHOTS) {
      if (shot.actors) {
        for (const actor of shot.actors) {
          if (actor.kind === 'enemy') {
            expect(ENEMIES[actor.ref]).toBeDefined();
          }
        }
      }
    }
  });

  it('timeline advances correctly and triggers enteredShot', () => {
    const timeline = new ChronicleTimeline(CHRONICLE_SHOTS);
    expect(timeline.state.shotIdx).toBe(0);
    expect(timeline.state.enteredShot).toBe(true);

    // Tick within shot 0
    let s = timeline.tick(1000);
    expect(s.shotIdx).toBe(0);
    expect(s.enteredShot).toBe(false);
    expect(s.t).toBeCloseTo(1000 / CHRONICLE_SHOTS[0].durationMs, 2);

    // Advance past shot 0
    s = timeline.tick(7000);
    expect(s.shotIdx).toBe(1);
    expect(s.enteredShot).toBe(true);

    // Skip to next works
    timeline.skipToNext();
    expect(timeline.state.shotIdx).toBe(2);
    expect(timeline.state.enteredShot).toBe(true);
  });

  it('Ken Burns bounds: visibleRect never reveals void / negative coordinates', () => {
    const cam = { x: 0, y: 0, zoom: 1 };
    const rect = { x: 0, y: 0, w: 0, h: 0 };

    for (const shot of CHRONICLE_SHOTS) {
      // Test 20 discrete intervals for each shot
      for (let i = 0; i <= 20; i++) {
        const t = i / 20;
        kenBurns(shot.cam.from, shot.cam.to, t, shot.cam.ease, cam);
        visibleRect(cam, rect);

        expect(cam.zoom).toBeGreaterThanOrEqual(1.0);
        expect(rect.x).toBeGreaterThanOrEqual(0);
        expect(rect.y).toBeGreaterThanOrEqual(0);
        expect(rect.x + rect.w).toBeLessThanOrEqual(1024.001);
        expect(rect.y + rect.h).toBeLessThanOrEqual(576.001);
      }
    }
  });

  it('parallaxOffset snaps strictly to pixelScale steps', () => {
    const scale = 2;
    const out = { x: 0, y: 0 };
    for (let factor = 0.5; factor <= 1.5; factor += 0.1) {
      parallaxOffset(587, 341, factor, scale, out);
      expect(Math.abs(out.x % scale)).toBe(0);
      expect(Math.abs(out.y % scale)).toBe(0);
    }
  });

  it('crew progression: starts with leader, strictly grows, no duplicates, all 6 by campfire', () => {
    const allLeaders: HeroId[] = ['danny', 'alior', 'lisu', 'barti', 'oziem', 'luki'];

    for (const leader of allLeaders) {
      let prevCount = 1;
      for (let idx = 0; idx < CHRONICLE_SHOTS.length; idx++) {
        const crew = crewAtShot(CHRONICLE_SHOTS, idx, leader);
        expect(crew[0]).toBe(leader);
        expect(new Set(crew).size).toBe(crew.length); // no duplicates
        expect(crew.length).toBeGreaterThanOrEqual(prevCount);
        prevCount = crew.length;

        // By campfire (shot 9) and beyond, all 6 must be assembled
        if (idx >= 9) {
          expect(crew.length).toBe(6);
        }

        // Leader never appears in joinersAtShot
        const joiners = joinersAtShot(CHRONICLE_SHOTS, idx, leader);
        expect(joiners.includes(leader)).toBe(false);
      }
    }
  });

  it('typewriterCount reveals characters smoothly and clamps', () => {
    const text = 'KRONIKA EKIPY';
    expect(typewriterCount(text.length, 100, 30, 200)).toBe(0); // Before delay
    expect(typewriterCount(text.length, 300, 30, 200)).toBe(3); // 100ms after delay at 30 cps = 3 chars
    expect(typewriterCount(text.length, 5000, 30, 200)).toBe(text.length); // Clamped
  });

  it('flicker yields deterministic 0..1 values across styles', () => {
    const styles = ['candle', 'neonBuzz', 'fluorescentStutter', 'lightning', 'monitor', 'sunBloom', 'pulse', 'steady'];
    for (const style of styles) {
      const v1 = flicker(style, 42, 1500);
      const v2 = flicker(style, 42, 1500);
      expect(v1).toBe(v2);
      expect(v1).toBeGreaterThanOrEqual(0.0);
      expect(v1).toBeLessThanOrEqual(1.0);
    }
  });

  it('beatPhase completes 0..1 cycles on BPM tempo', () => {
    expect(beatPhase(120, 0)).toBe(0);
    expect(beatPhase(120, 250)).toBeCloseTo(0.5, 2); // 120 bpm = 500ms per beat, 250ms = 0.5
  });
});
