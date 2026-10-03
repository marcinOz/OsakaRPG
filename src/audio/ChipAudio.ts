import type { ChipSong, ChipTrack, SfxName, SfxOpts } from './types';
import { ALL_SONGS } from './songs';

const NOTE_OFFSETS: Record<string, number> = {
  C: 0, 'C#': 1, Db: 1, D: 2, 'D#': 3, Eb: 3, E: 4, F: 5,
  'F#': 6, Gb: 6, G: 7, 'G#': 8, Ab: 8, A: 9, 'A#': 10, Bb: 10, B: 11,
};

function noteToFreq(note: string): number {
  const match = note.match(/^([A-G][#b]?)(-?\d+)$/);
  if (!match) return 440;
  const name = match[1];
  const octave = parseInt(match[2], 10);
  const semitone = NOTE_OFFSETS[name] ?? 0;
  const midi = 12 + octave * 12 + semitone;
  return 440 * Math.pow(2, (midi - 69) / 12);
}

class ChipAudioEngine {
  private ctx: AudioContext | null = null;
  private musicBus: GainNode | null = null;
  private sfxBus: GainNode | null = null;
  private masterGain: GainNode | null = null;
  private noiseBuffer: AudioBuffer | null = null;

  private currentSongId: string | null = null;
  private songTimer: number | null = null;
  private songStep = 0;
  private nextStepTime = 0;
  private currentSongDef: ChipSong | null = null;
  private shouldLoop = true;

  private musicVol = 0.7;
  private sfxVol = 0.8;

  private initCtx(): AudioContext {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      this.ctx = new AudioCtx();
      this.masterGain = this.ctx.createGain();
      this.masterGain.connect(this.ctx.destination);

      this.musicBus = this.ctx.createGain();
      this.musicBus.gain.value = this.musicVol;
      this.musicBus.connect(this.masterGain);

      this.sfxBus = this.ctx.createGain();
      this.sfxBus.gain.value = this.sfxVol;
      this.sfxBus.connect(this.masterGain);

      // 1-second white noise buffer
      const bufferSize = this.ctx.sampleRate;
      this.noiseBuffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
      const data = this.noiseBuffer.getChannelData(0);
      for (let i = 0; i < bufferSize; i++) {
        data[i] = Math.random() * 2 - 1;
      }
    }
    if (this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
    return this.ctx;
  }

  unlock(): void {
    this.initCtx();
  }

  setMusicVolume(v: number): void {
    this.musicVol = Math.max(0, Math.min(1, v));
    if (this.musicBus) this.musicBus.gain.value = this.musicVol;
  }

  setSfxVolume(v: number): void {
    this.sfxVol = Math.max(0, Math.min(1, v));
    if (this.sfxBus) this.sfxBus.gain.value = this.sfxVol;
  }

  currentSong(): string | null {
    return this.currentSongId;
  }

  songLabel(id: string): string {
    return ALL_SONGS[id]?.label ?? id;
  }

  playSong(id: string, opts: { fadeMs?: number; loop?: boolean } = {}): void {
    if (this.currentSongId === id) return;
    this.initCtx();
    this.stopSong(opts.fadeMs ?? 200);

    const song = ALL_SONGS[id];
    if (!song) return;

    this.currentSongId = id;
    this.currentSongDef = song;
    this.shouldLoop = opts.loop ?? (song.loop !== false);
    this.songStep = 0;
    this.nextStepTime = this.ctx!.currentTime + 0.05;

    // Scheduler tick every 25ms, look ahead 100ms
    this.songTimer = window.setInterval(() => this.scheduleNextSteps(), 25);
  }

  crossfadeTo(id: string, ms = 800): void {
    this.playSong(id, { fadeMs: ms });
  }

  stopSong(_fadeMs = 200): void {
    if (this.songTimer !== null) {
      clearInterval(this.songTimer);
      this.songTimer = null;
    }
    this.currentSongId = null;
    this.currentSongDef = null;
  }

  private scheduleNextSteps(): void {
    if (!this.ctx || !this.currentSongDef) return;

    const secondsPerBeat = 60 / this.currentSongDef.bpm;
    const stepDuration = secondsPerBeat / 4; // 16th note step

    while (this.nextStepTime < this.ctx.currentTime + 0.1) {
      this.playStepAtTime(this.songStep, this.nextStepTime, stepDuration);

      // Swing: delay odd 16th notes slightly
      const swingOffset = (this.songStep % 2 === 1 && this.currentSongDef.swing)
        ? this.currentSongDef.swing * stepDuration * 0.5
        : 0;

      this.nextStepTime += stepDuration + swingOffset;
      this.songStep++;

      const maxSteps = this.getSongTotalSteps(this.currentSongDef);
      if (this.songStep >= maxSteps) {
        if (this.shouldLoop) {
          this.songStep = 0;
        } else {
          this.stopSong();
          break;
        }
      }
    }
  }

  private getSongTotalSteps(song: ChipSong): number {
    let max = 16;
    for (const tr of song.tracks) {
      const trackSteps = tr.order.length * (song.steps || 16);
      if (trackSteps > max) max = trackSteps;
    }
    return max;
  }

  private playStepAtTime(globalStep: number, time: number, stepSec: number): void {
    if (!this.currentSongDef || !this.ctx || !this.musicBus) return;
    const stepsPerPattern = this.currentSongDef.steps || 16;

    for (const track of this.currentSongDef.tracks) {
      const patternIdx = Math.floor(globalStep / stepsPerPattern) % track.order.length;
      const patternId = track.order[patternIdx];
      const pattern = track.patterns[patternId];
      if (!pattern) continue;

      const stepInPattern = globalStep % stepsPerPattern;
      const token = pattern[stepInPattern];
      if (!token) continue;

      this.renderTrackNote(track, token, time, stepSec);
    }
  }

  private renderTrackNote(track: ChipTrack, token: string, time: number, stepSec: number): void {
    if (!this.ctx || !this.musicBus) return;

    const parts = token.split(':');
    const noteExpr = parts[0];
    const durationMultiplier = parts[1] ? parseFloat(parts[1]) : (track.len ?? 1);
    const duration = stepSec * durationMultiplier;

    // Drum tokens
    if (track.inst === 'kick' || noteExpr === 'x' && track.inst !== 'saw' && track.inst !== 'pulse' && track.inst !== 'triangle') {
      this.playKick(time, track.vol);
      return;
    }
    if (track.inst === 'snare') {
      this.playSnare(time, track.vol);
      return;
    }
    if (track.inst === 'hat') {
      this.playHat(time, track.vol);
      return;
    }

    // Melodic notes / chords: "C4" or "C4+E4+G4"
    const notes = noteExpr.split('+');
    for (const note of notes) {
      const freq = noteToFreq(note);
      this.playTone(track.inst, freq, time, duration, track.vol, track.duty);
    }
  }

  private playTone(
    type: 'pulse' | 'square' | 'triangle' | 'saw' | 'pad' | 'noise' | 'kick' | 'snare' | 'hat',
    freq: number,
    time: number,
    duration: number,
    vol: number,
    _duty = 0.5
  ): void {
    if (!this.ctx || !this.musicBus) return;

    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    if (type === 'triangle') osc.type = 'triangle';
    else if (type === 'saw') osc.type = 'sawtooth';
    else if (type === 'pad') osc.type = 'sine';
    else osc.type = 'square';

    osc.frequency.setValueAtTime(freq, time);

    gain.gain.setValueAtTime(0.001, time);
    gain.gain.linearRampToValueAtTime(vol * 0.4, time + 0.01);
    gain.gain.setValueAtTime(vol * 0.4, time + Math.max(0.02, duration - 0.02));
    gain.gain.exponentialRampToValueAtTime(0.001, time + duration);

    osc.connect(gain);
    gain.connect(this.musicBus);

    osc.start(time);
    osc.stop(time + duration);
  }

  private playKick(time: number, vol = 0.6): void {
    if (!this.ctx || !this.musicBus) return;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.frequency.setValueAtTime(140, time);
    osc.frequency.exponentialRampToValueAtTime(35, time + 0.12);

    gain.gain.setValueAtTime(vol * 0.8, time);
    gain.gain.exponentialRampToValueAtTime(0.001, time + 0.15);

    osc.connect(gain);
    gain.connect(this.musicBus);

    osc.start(time);
    osc.stop(time + 0.15);
  }

  private playSnare(time: number, vol = 0.5): void {
    if (!this.ctx || !this.musicBus || !this.noiseBuffer) return;
    // Noise burst
    const noise = this.ctx.createBufferSource();
    noise.buffer = this.noiseBuffer;
    const filter = this.ctx.createBiquadFilter();
    filter.type = 'highpass';
    filter.frequency.setValueAtTime(1000, time);

    const gain = this.ctx.createGain();
    gain.gain.setValueAtTime(vol * 0.6, time);
    gain.gain.exponentialRampToValueAtTime(0.001, time + 0.14);

    noise.connect(filter);
    filter.connect(gain);
    gain.connect(this.musicBus);

    noise.start(time);
    noise.stop(time + 0.14);
  }

  private playHat(time: number, vol = 0.2): void {
    if (!this.ctx || !this.musicBus || !this.noiseBuffer) return;
    const noise = this.ctx.createBufferSource();
    noise.buffer = this.noiseBuffer;
    const filter = this.ctx.createBiquadFilter();
    filter.type = 'highpass';
    filter.frequency.setValueAtTime(6000, time);

    const gain = this.ctx.createGain();
    gain.gain.setValueAtTime(vol * 0.4, time);
    gain.gain.exponentialRampToValueAtTime(0.001, time + 0.05);

    noise.connect(filter);
    filter.connect(gain);
    gain.connect(this.musicBus);

    noise.start(time);
    noise.stop(time + 0.05);
  }

  sfx(name: SfxName, opts: SfxOpts = {}): void {
    try {
      this.initCtx();
      if (!this.ctx || !this.sfxBus) return;
      const t = this.ctx.currentTime;
      const p = opts.pitch ?? 1.0;
      const v = (opts.vol ?? 1.0) * this.sfxVol;

      switch (name) {
        case 'cursor': {
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          osc.type = 'square';
          osc.frequency.setValueAtTime(480 * p, t);
          gain.gain.setValueAtTime(0.12 * v, t);
          gain.gain.exponentialRampToValueAtTime(0.001, t + 0.04);
          osc.connect(gain);
          gain.connect(this.sfxBus);
          osc.start(t);
          osc.stop(t + 0.04);
          break;
        }
        case 'confirm': {
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          osc.type = 'square';
          osc.frequency.setValueAtTime(520 * p, t);
          osc.frequency.setValueAtTime(780 * p, t + 0.05);
          gain.gain.setValueAtTime(0.18 * v, t);
          gain.gain.exponentialRampToValueAtTime(0.001, t + 0.12);
          osc.connect(gain);
          gain.connect(this.sfxBus);
          osc.start(t);
          osc.stop(t + 0.12);
          break;
        }
        case 'cancel': {
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          osc.type = 'triangle';
          osc.frequency.setValueAtTime(380 * p, t);
          osc.frequency.setValueAtTime(220 * p, t + 0.06);
          gain.gain.setValueAtTime(0.18 * v, t);
          gain.gain.exponentialRampToValueAtTime(0.001, t + 0.12);
          osc.connect(gain);
          gain.connect(this.sfxBus);
          osc.start(t);
          osc.stop(t + 0.12);
          break;
        }
        case 'blip': {
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          osc.type = 'triangle';
          const baseFreq = p >= 20 ? p : 400 * p;
          osc.frequency.setValueAtTime(baseFreq, t);
          gain.gain.setValueAtTime(0.07 * v, t);
          gain.gain.exponentialRampToValueAtTime(0.001, t + 0.03);
          osc.connect(gain);
          gain.connect(this.sfxBus);
          osc.start(t);
          osc.stop(t + 0.03);
          break;
        }
        case 'hit': {
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          osc.type = 'sawtooth';
          osc.frequency.setValueAtTime(160 * p, t);
          osc.frequency.exponentialRampToValueAtTime(40, t + 0.12);
          gain.gain.setValueAtTime(0.3 * v, t);
          gain.gain.exponentialRampToValueAtTime(0.001, t + 0.15);
          osc.connect(gain);
          gain.connect(this.sfxBus);
          osc.start(t);
          osc.stop(t + 0.15);
          break;
        }
        case 'crit': {
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          osc.type = 'sawtooth';
          osc.frequency.setValueAtTime(320 * p, t);
          osc.frequency.exponentialRampToValueAtTime(60, t + 0.25);
          gain.gain.setValueAtTime(0.4 * v, t);
          gain.gain.exponentialRampToValueAtTime(0.001, t + 0.28);
          osc.connect(gain);
          gain.connect(this.sfxBus);
          osc.start(t);
          osc.stop(t + 0.28);
          break;
        }
        case 'miss': {
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(300 * p, t);
          osc.frequency.linearRampToValueAtTime(150, t + 0.1);
          gain.gain.setValueAtTime(0.12 * v, t);
          gain.gain.exponentialRampToValueAtTime(0.001, t + 0.12);
          osc.connect(gain);
          gain.connect(this.sfxBus);
          osc.start(t);
          osc.stop(t + 0.12);
          break;
        }
        case 'heal':
        case 'aquaRescue': {
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(330 * p, t);
          osc.frequency.linearRampToValueAtTime(660 * p, t + 0.2);
          gain.gain.setValueAtTime(0.25 * v, t);
          gain.gain.exponentialRampToValueAtTime(0.001, t + 0.25);
          osc.connect(gain);
          gain.connect(this.sfxBus);
          osc.start(t);
          osc.stop(t + 0.25);
          break;
        }
        case 'steelWall': {
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          osc.type = 'square';
          osc.frequency.setValueAtTime(120 * p, t);
          osc.frequency.linearRampToValueAtTime(240 * p, t + 0.15);
          gain.gain.setValueAtTime(0.3 * v, t);
          gain.gain.exponentialRampToValueAtTime(0.001, t + 0.25);
          osc.connect(gain);
          gain.connect(this.sfxBus);
          osc.start(t);
          osc.stop(t + 0.25);
          break;
        }
        case 'frameTrap': {
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          osc.type = 'sawtooth';
          osc.frequency.setValueAtTime(900 * p, t);
          osc.frequency.setValueAtTime(200 * p, t + 0.05);
          osc.frequency.setValueAtTime(800 * p, t + 0.1);
          gain.gain.setValueAtTime(0.25 * v, t);
          gain.gain.exponentialRampToValueAtTime(0.001, t + 0.2);
          osc.connect(gain);
          gain.connect(this.sfxBus);
          osc.start(t);
          osc.stop(t + 0.2);
          break;
        }
        case 'smokeScreen': {
          if (!this.noiseBuffer) return;
          const noise = this.ctx.createBufferSource();
          noise.buffer = this.noiseBuffer;
          const filter = this.ctx.createBiquadFilter();
          filter.type = 'lowpass';
          filter.frequency.setValueAtTime(600, t);
          const gain = this.ctx.createGain();
          gain.gain.setValueAtTime(0.25 * v, t);
          gain.gain.exponentialRampToValueAtTime(0.001, t + 0.35);
          noise.connect(filter);
          filter.connect(gain);
          gain.connect(this.sfxBus);
          noise.start(t);
          noise.stop(t + 0.35);
          break;
        }
        case 'bassBlast': {
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          osc.type = 'triangle';
          osc.frequency.setValueAtTime(70 * p, t);
          osc.frequency.exponentialRampToValueAtTime(30, t + 0.4);
          gain.gain.setValueAtTime(0.5 * v, t);
          gain.gain.exponentialRampToValueAtTime(0.001, t + 0.45);
          osc.connect(gain);
          gain.connect(this.sfxBus);
          osc.start(t);
          osc.stop(t + 0.45);
          break;
        }
        case 'notification': {
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(587.33 * p, t); // D5
          osc.frequency.setValueAtTime(880 * p, t + 0.08); // A5
          gain.gain.setValueAtTime(0.25 * v, t);
          gain.gain.exponentialRampToValueAtTime(0.001, t + 0.3);
          osc.connect(gain);
          gain.connect(this.sfxBus);
          osc.start(t);
          osc.stop(t + 0.3);
          break;
        }
        default: {
          // Standard fallback blip
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(440 * p, t);
          gain.gain.setValueAtTime(0.15 * v, t);
          gain.gain.exponentialRampToValueAtTime(0.001, t + 0.08);
          osc.connect(gain);
          gain.connect(this.sfxBus);
          osc.start(t);
          osc.stop(t + 0.08);
          break;
        }
      }
    } catch {
      // AudioContext could be blocked by browser autoplay policy until user gesture
    }
  }
}

export const Audio = new ChipAudioEngine();
