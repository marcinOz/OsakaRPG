import Phaser from 'phaser';
import { GAME_W, GAME_H, PAL } from '@/config';
import { HERO_IDS } from '@/types';
import { registerCrt } from '@/fx/CrtPipeline';

export class BootScene extends Phaser.Scene {
  constructor() {
    super('Boot');
  }

  preload(): void {
    // Background and loading bar
    this.cameras.main.setBackgroundColor(PAL.void);
    const bar = this.add.graphics();
    this.load.on('progress', (p: number) => {
      bar.clear();
      bar.fillStyle(PAL.panel, 1);
      bar.fillRect(GAME_W / 4, GAME_H / 2 - 4, GAME_W / 2, 8);
      bar.fillStyle(PAL.cyan, 1);
      bar.fillRect(GAME_W / 4 + 1, GAME_H / 2 - 3, (GAME_W / 2 - 2) * p, 6);
    });

    // Bitmap Fonts
    this.load.bitmapFont('pixel', 'assets/fonts/pixel.png', 'assets/fonts/pixel.fnt');
    this.load.bitmapFont('pixel_big', 'assets/fonts/pixel_big.png', 'assets/fonts/pixel_big.fnt');

    // Backgrounds
    this.load.image('title_bg', 'assets/bg/title.png');
    this.load.image('campfire_bg', 'assets/bg/campfire.png');
    this.load.image('battle_apartment_bg', 'assets/bg/battle_apartment.png');
    this.load.image('battle_city_bg', 'assets/bg/battle_city.png');
    this.load.image('battle_forest_bg', 'assets/bg/battle_forest.png');
    this.load.image('battle_garage_bg', 'assets/bg/battle_garage.png');
    this.load.image('battle_pub_bg', 'assets/bg/battle_pub.png');
    this.load.image('battle_alley_bg', 'assets/bg/battle_alley.png');
    this.load.image('battle_marina_bg', 'assets/bg/battle_marina.png');
    this.load.image('battle_rift_bg', 'assets/bg/battle_rift.png');
    this.load.image('sunrise_bg', 'assets/bg/sunrise.png');

    // UI Thumbnails
    this.load.image('thumb_group', 'assets/ui/thumb_group.png');
    this.load.image('thumb_travel', 'assets/ui/thumb_travel.png');
    this.load.image('thumb_funny', 'assets/ui/thumb_funny.png');
    this.load.image('thumb_moments', 'assets/ui/thumb_moments.png');

    // Tilesets
    this.load.image('tiles_apartment', 'assets/tiles/apartment.png');
    this.load.image('tiles_city', 'assets/tiles/city.png');
    this.load.image('tiles_forest', 'assets/tiles/forest.png');
    this.load.image('tiles_garage', 'assets/tiles/garage.png');
    this.load.image('tiles_pub', 'assets/tiles/pub.png');
    this.load.image('tiles_alley', 'assets/tiles/alley.png');
    this.load.image('tiles_marina', 'assets/tiles/marina.png');

    // Spritesheets
    this.load.spritesheet('fire', 'assets/bg/fire.png', { frameWidth: 32, frameHeight: 40 });
    this.load.spritesheet('enemy_bolKregoslupa', 'assets/enemies/bolKregoslupa.png', { frameWidth: 48, frameHeight: 48 });
    this.load.spritesheet('enemy_slacki', 'assets/enemies/slacki.png', { frameWidth: 48, frameHeight: 48 });
    this.load.spritesheet('enemy_sasiadSzkodnik', 'assets/enemies/sasiadSzkodnik.png', { frameWidth: 48, frameHeight: 48 });
    this.load.spritesheet('enemy_autoTuneHipster', 'assets/enemies/autoTuneHipster.png', { frameWidth: 48, frameHeight: 48 });
    this.load.spritesheet('enemy_drogiePiwo', 'assets/enemies/drogiePiwo.png', { frameWidth: 48, frameHeight: 48 });
    this.load.spritesheet('enemy_kark', 'assets/enemies/kark.png', { frameWidth: 48, frameHeight: 48 });
    this.load.spritesheet('enemy_straznik', 'assets/enemies/straznik.png', { frameWidth: 48, frameHeight: 48 });
    this.load.spritesheet('enemy_panJanusz', 'assets/enemies/panJanusz.png', { frameWidth: 48, frameHeight: 48 });
    this.load.spritesheet('enemy_kredyt', 'assets/enemies/kredyt.png', { frameWidth: 48, frameHeight: 48 });
    this.load.spritesheet('enemy_audyt', 'assets/enemies/audyt.png', { frameWidth: 48, frameHeight: 48 });
    this.load.spritesheet('enemy_rwaKulszowa', 'assets/enemies/rwaKulszowa.png', { frameWidth: 48, frameHeight: 48 });

    // Heroes
    for (const hid of HERO_IDS) {
      this.load.image(`portrait_${hid}_96`, `assets/portraits/${hid}_96.png`);
      this.load.image(`portrait_${hid}_64`, `assets/portraits/${hid}_64.png`);
      this.load.spritesheet(`${hid}_walk`, `assets/sprites/${hid}_walk.png`, { frameWidth: 16, frameHeight: 24 });
      this.load.spritesheet(`${hid}_battle`, `assets/sprites/${hid}_battle.png`, { frameWidth: 32, frameHeight: 40 });
      this.load.spritesheet(`${hid}_sit`, `assets/sprites/${hid}_sit.png`, { frameWidth: 24, frameHeight: 24 });
    }

    // Items
    const items = [
      'shield', 'gauntlets', 'shaker', 'controller', 'cartridge', 'goggles',
      'binoculars', 'fox', 'sneakers', 'vinyl', 'turntable', 'speaker',
      'rope', 'multitool', 'campfire', 'divingGoggles', 'lifebuoy', 'backpack'
    ];
    for (const item of items) {
      this.load.image(`item_${item}`, `assets/items/${item}.png`);
    }

    // FX
    for (const fx of ['shield', 'glitch', 'smoke', 'bass', 'leaves', 'splash', 'hit']) {
      this.load.spritesheet(`fx_${fx}`, `assets/fx/${fx}.png`, { frameWidth: 32, frameHeight: 32 });
    }
  }

  create(): void {
    registerCrt(this.game);
    this.createGlobalAnimations();
    this.scene.start('Title');
  }

  private createGlobalAnimations(): void {
    // Fire anim
    if (!this.anims.exists('anim_fire')) {
      this.anims.create({
        key: 'anim_fire',
        frames: this.anims.generateFrameNumbers('fire', { start: 0, end: 5 }),
        frameRate: 8,
        repeat: -1,
      });
    }

    // Enemies
    const allEnemies = [
      'bolKregoslupa', 'slacki', 'sasiadSzkodnik', 'autoTuneHipster', 'drogiePiwo',
      'kark', 'straznik', 'panJanusz', 'kredyt', 'audyt', 'rwaKulszowa'
    ];
    for (const eid of allEnemies) {
      if (!this.anims.exists(`anim_enemy_${eid}`)) {
        this.anims.create({
          key: `anim_enemy_${eid}`,
          frames: this.anims.generateFrameNumbers(`enemy_${eid}`, { start: 0, end: 1 }),
          frameRate: 3,
          repeat: -1,
        });
      }
    }

    // Hero walk anims
    for (const hid of HERO_IDS) {
      const dirs = ['down', 'left', 'right', 'up'];
      dirs.forEach((dir, r) => {
        const start = r * 3;
        const key = `anim_${hid}_walk_${dir}`;
        if (!this.anims.exists(key)) {
          this.anims.create({
            key,
            frames: [
              { key: `${hid}_walk`, frame: start },
              { key: `${hid}_walk`, frame: start + 1 },
              { key: `${hid}_walk`, frame: start + 2 },
              { key: `${hid}_walk`, frame: start + 1 },
            ],
            frameRate: 6,
            repeat: -1,
          });
        }
      });

      // Sitting anim
      if (!this.anims.exists(`anim_${hid}_sit`)) {
        this.anims.create({
          key: `anim_${hid}_sit`,
          frames: this.anims.generateFrameNumbers(`${hid}_sit`, { start: 0, end: 1 }),
          frameRate: 2,
          repeat: -1,
        });
      }
    }

    // FX anims
    for (const fx of ['shield', 'glitch', 'smoke', 'bass', 'leaves', 'splash', 'hit']) {
      if (!this.anims.exists(`anim_fx_${fx}`)) {
        this.anims.create({
          key: `anim_fx_${fx}`,
          frames: this.anims.generateFrameNumbers(`fx_${fx}`, { start: 0, end: 5 }),
          frameRate: 12,
          repeat: 0,
        });
      }
    }
  }
}
