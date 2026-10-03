import type { DialogueLine, HeroId } from '@/types';
import { HEROES } from '@/content/heroes';
import { PAL } from '@/config';
import type { BoxLine } from '@/ui/DialogueBox';

export interface ResolvedLine extends BoxLine {
  speakerId: string;
}

export class DialogueRunner {
  private index = 0;

  constructor(
    private readonly lines: DialogueLine[],
    private readonly leader: HeroId,
    _party: HeroId[] = [leader]
  ) {}

  get isDone(): boolean {
    return this.index >= this.lines.length;
  }

  current(): ResolvedLine | null {
    if (this.isDone) return null;
    return this.resolveLine(this.lines[this.index]);
  }

  next(): ResolvedLine | null {
    if (this.isDone) return null;
    const line = this.lines[this.index++];
    return this.resolveLine(line);
  }

  allResolved(): ResolvedLine[] {
    return this.lines.map((l) => this.resolveLine(l));
  }

  private resolveLine(line: DialogueLine): ResolvedLine {
    const leaderDef = HEROES[this.leader];
    const leaderName = leaderDef?.name ?? this.leader;

    // Check leader-specific text override
    let text = line.leader?.[this.leader] ?? line.text;
    text = text.replace(/{leader}/g, leaderName);

    let speakerId = line.speaker;
    let name = line.speaker;
    let portrait = line.portrait;
    let color: number = PAL.white;
    let pitch = 1.0;

    if (line.speaker === 'player') {
      speakerId = this.leader;
      name = leaderName;
      portrait = portrait ?? `portrait_${this.leader}_64`;
      color = leaderDef?.color ?? PAL.yellow;
      pitch = this.pitchForHero(this.leader);
    } else if (line.speaker in HEROES) {
      const hid = line.speaker as HeroId;
      const hdef = HEROES[hid];
      name = hdef.name;
      portrait = portrait ?? `portrait_${hid}_64`;
      color = hdef.color;
      pitch = this.pitchForHero(hid);
    } else if (line.speaker === 'SYSTEM') {
      name = ''; // Narration
      color = PAL.cyan;
      pitch = 1.4;
    } else {
      // Named NPC / Enemy
      color = PAL.yellow;
      pitch = 0.9;
    }

    return {
      speakerId,
      name,
      text,
      portrait,
      color,
      pitch,
    };
  }

  private pitchForHero(hid: HeroId): number {
    switch (hid) {
      case 'danny':
        return 0.75; // deep
      case 'alior':
        return 1.1; // crisp
      case 'lisu':
        return 1.25; // light/quick
      case 'barti':
        return 0.95; // warm
      case 'oziem':
        return 0.85; // grounded
      case 'luki':
        return 1.05; // calm
      default:
        return 1.0;
    }
  }
}
