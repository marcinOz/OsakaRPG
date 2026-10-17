import Phaser from 'phaser';
import { GAME_W, GAME_H, PAL } from '@/config';
import { BootScene } from '@/scenes/BootScene';
import { TitleScene } from '@/scenes/TitleScene';
import { AnalyzerScene } from '@/scenes/AnalyzerScene';
import { WorldScene } from '@/scenes/WorldScene';
import { BattleScene } from '@/scenes/BattleScene';
import { CampfireScene } from '@/scenes/CampfireScene';
import { OutroScene } from '@/scenes/OutroScene';
import { ChronicleScene } from '@/scenes/ChronicleScene';
import { CrtPipeline } from '@/fx/CrtPipeline';
import { LivingPaintingPipeline } from '@/fx/LivingPaintingPipeline';
import { DitherDissolvePipeline } from '@/fx/DitherDissolvePipeline';

const config: Phaser.Types.Core.GameConfig = {
  type: Phaser.WEBGL,
  parent: 'game',
  width: GAME_W,
  height: GAME_H,
  backgroundColor: PAL.void,
  pixelArt: true,
  roundPixels: true,
  scale: {
    mode: Phaser.Scale.FIT,
    autoCenter: Phaser.Scale.NO_CENTER,
  },
  pipeline: {
    Crt: CrtPipeline as any,
    LivingPainting: LivingPaintingPipeline as any,
    DitherDissolve: DitherDissolvePipeline as any,
  },
  scene: [
    BootScene,
    TitleScene,
    AnalyzerScene,
    WorldScene,
    BattleScene,
    CampfireScene,
    OutroScene,
    ChronicleScene,
  ],
};

new Phaser.Game(config);
