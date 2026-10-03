import Phaser from 'phaser';
import { GAME_W, GAME_H, PAL } from '@/config';
import { BootScene } from '@/scenes/BootScene';
import { TitleScene } from '@/scenes/TitleScene';
import { AnalyzerScene } from '@/scenes/AnalyzerScene';
import { WorldScene } from '@/scenes/WorldScene';
import { BattleScene } from '@/scenes/BattleScene';
import { CampfireScene } from '@/scenes/CampfireScene';
import { OutroScene } from '@/scenes/OutroScene';
import { CrtPipeline } from '@/fx/CrtPipeline';

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
    autoCenter: Phaser.Scale.CENTER_BOTH,
  },
  pipeline: {
    Crt: CrtPipeline as any,
  },
  scene: [
    BootScene,
    TitleScene,
    AnalyzerScene,
    WorldScene,
    BattleScene,
    CampfireScene,
    OutroScene,
  ],
};

new Phaser.Game(config);
