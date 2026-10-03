import type { DialogueLine, HeroId } from '@/types';

export type CutsceneStep =
  | { t: 'say'; lines: DialogueLine[] }
  | { t: 'move'; who: string; path: [number, number][]; speed?: number }
  | { t: 'wait'; ms: number }
  | { t: 'flag'; key: string; value?: boolean | number | string }
  | { t: 'status'; add?: string; remove?: string }
  | { t: 'join'; hero: HeroId }
  | { t: 'fade'; to: 'black' | 'clear'; ms?: number }
  | { t: 'music'; id: string }
  | { t: 'sfx'; id: string }
  | { t: 'popup'; title: string; body: string }
  | { t: 'battle'; enemies: string[]; bg?: string }
  | { t: 'emit'; event: string; data?: any };

export class CutsceneQueue {
  private queue: CutsceneStep[] = [];

  constructor(steps: CutsceneStep[] = []) {
    this.queue = [...steps];
  }

  enqueue(...steps: CutsceneStep[]): void {
    this.queue.push(...steps);
  }

  next(): CutsceneStep | null {
    return this.queue.shift() ?? null;
  }

  get isEmpty(): boolean {
    return this.queue.length === 0;
  }

  clear(): void {
    this.queue = [];
  }
}
