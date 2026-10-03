import { SAVE_KEY } from '@/config';
import { HEROES } from '@/content/heroes';
import type { GameData } from './GameState';

export interface StorageAdapter {
  getItem(key: string): string | null;
  setItem(key: string, value: string): void;
  removeItem(key: string): void;
}

export class MemoryStorage implements StorageAdapter {
  private map = new Map<string, string>();
  getItem(key: string): string | null {
    return this.map.get(key) ?? null;
  }
  setItem(key: string, value: string): void {
    this.map.set(key, value);
  }
  removeItem(key: string): void {
    this.map.delete(key);
  }
}

export interface SaveSlotSummary {
  slot: number;
  exists: boolean;
  leader?: string;
  chapter?: number;
  playtime?: number;
  date?: string;
}

export class SaveSystem {
  constructor(private storage: StorageAdapter = typeof localStorage !== 'undefined' ? localStorage : new MemoryStorage()) {}

  private key(slot: number): string {
    return `${SAVE_KEY}.slot_${slot}`;
  }

  save(slot: number, data: GameData): boolean {
    try {
      data.timestamp = Date.now();
      this.storage.setItem(this.key(slot), JSON.stringify(data));
      return true;
    } catch {
      return false;
    }
  }

  load(slot: number): GameData | null {
    try {
      const raw = this.storage.getItem(this.key(slot));
      if (!raw) return null;
      return JSON.parse(raw) as GameData;
    } catch {
      return null;
    }
  }

  delete(slot: number): void {
    this.storage.removeItem(this.key(slot));
  }

  list(): SaveSlotSummary[] {
    const out: SaveSlotSummary[] = [];
    for (let slot = 0; slot < 3; slot++) {
      const data = this.load(slot);
      if (data) {
        const leaderName = HEROES[data.leader]?.name ?? data.leader;
        const d = new Date(data.timestamp);
        const dateStr = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
        out.push({
          slot,
          exists: true,
          leader: leaderName,
          chapter: data.chapter,
          playtime: data.playtime,
          date: dateStr,
        });
      } else {
        out.push({ slot, exists: false });
      }
    }
    return out;
  }
}

export const Saves = new SaveSystem();
