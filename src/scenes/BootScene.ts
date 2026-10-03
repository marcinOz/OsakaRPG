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
    this.load.image('analyzer_bg', 'assets/bg/analyzer_bg.png');

    // UI Thumbnails & Phone Modal
    this.load.image('thumb_group', 'assets/ui/thumb_group.png');
    this.load.image('thumb_travel', 'assets/ui/thumb_travel.png');
    this.load.image('thumb_funny', 'assets/ui/thumb_funny.png');
    this.load.image('thumb_moments', 'assets/ui/thumb_moments.png');
    this.load.image('phone_frame', 'assets/ui/phone_frame.png');
    this.load.image('avatar_group', 'assets/ui/avatar_group.png');
    this.load.image('avatar_danny', 'assets/ui/avatar_danny.png');
    this.load.image('avatar_alior', 'assets/ui/avatar_alior.png');
    this.load.image('avatar_lisu', 'assets/ui/avatar_lisu.png');
    this.load.image('avatar_barti', 'assets/ui/avatar_barti.png');
    this.load.image('avatar_oziem', 'assets/ui/avatar_oziem.png');
    this.load.image('avatar_luki', 'assets/ui/avatar_luki.png');
    this.load.image('chat_bubble_in', 'assets/ui/chat_bubble_in.png');
    this.load.image('chat_bubble_out', 'assets/ui/chat_bubble_out.png');
    this.load.image('keycaps', 'assets/ui/keycaps.png');
    this.load.spritesheet('keys_legend', 'assets/ui/keys_legend.png', { frameWidth: 560, frameHeight: 28 });
    this.load.spritesheet('exit_beacon', 'assets/fx/exit_beacon.png', { frameWidth: 32, frameHeight: 48 });
    this.load.spritesheet('exit_locked', 'assets/fx/exit_locked.png', { frameWidth: 32, frameHeight: 48 });

    // Tilesets
    this.load.image('tiles_apartment', 'assets/tiles/apartment.png');
    this.load.image('tiles_city', 'assets/tiles/city.png');
    this.load.image('tiles_zabka', 'assets/tiles/zabka.png');
    this.load.image('tiles_forest', 'assets/tiles/forest.png');
    this.load.image('tiles_garage', 'assets/tiles/garage.png');
    this.load.image('tiles_pub', 'assets/tiles/pub.png');
    this.load.image('tiles_alley', 'assets/tiles/alley.png');
    this.load.image('tiles_marina', 'assets/tiles/marina.png');

    // Spritesheets
    this.load.spritesheet('fire', 'assets/bg/fire.png', { frameWidth: 64, frameHeight: 80 });
    const enemySizes: Record<string, number> = {
      bolKregoslupa: 96,
      slacki: 96,
      sasiadSzkodnik: 128,
      autoTuneHipster: 128,
      drogiePiwo: 128,
      kark: 128,
      straznik: 128,
      rwaKulszowa: 128,
      panJanusz: 144,
      kredyt: 144,
      audyt: 144,
    };
    for (const [eid, sz] of Object.entries(enemySizes)) {
      this.load.spritesheet(`enemy_${eid}`, `assets/enemies/${eid}.png`, { frameWidth: sz, frameHeight: sz });
    }

    // Heroes
    for (const hid of HERO_IDS) {
      this.load.image(`portrait_${hid}_128`, `assets/portraits/${hid}_128.png`);
      this.load.image(`portrait_${hid}_96`, `assets/portraits/${hid}_96.png`);
      this.load.image(`portrait_${hid}_64`, `assets/portraits/${hid}_64.png`);
      this.load.image(`card_${hid}`, `assets/cards/${hid}.png`);
      this.load.spritesheet(`${hid}_walk`, `assets/sprites/${hid}_walk.png`, { frameWidth: 32, frameHeight: 48 });
      this.load.spritesheet(`${hid}_battle`, `assets/sprites/${hid}_battle.png`, { frameWidth: 64, frameHeight: 80 });
      this.load.spritesheet(`${hid}_sit`, `assets/sprites/${hid}_sit.png`, { frameWidth: 32, frameHeight: 32 });
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

    // Enemies (2 frames idle)
    const enemySizes: Record<string, number> = {
      bolKregoslupa: 96,
      slacki: 96,
      sasiadSzkodnik: 128,
      autoTuneHipster: 128,
      drogiePiwo: 128,
      kark: 128,
      straznik: 128,
      rwaKulszowa: 128,
      panJanusz: 144,
      kredyt: 144,
      audyt: 144,
    };
    for (const eid of Object.keys(enemySizes)) {
      if (!this.anims.exists(`anim_enemy_${eid}`)) {
        this.anims.create({
          key: `anim_enemy_${eid}`,
          frames: this.anims.generateFrameNumbers(`enemy_${eid}`, { start: 0, end: 1 }),
          frameRate: 3,
          repeat: -1,
        });
      }
    }

    // Hero anims (walk, sit, battle states)
    for (const hid of HERO_IDS) {
      // Walk: down, left, right, up
      const dirs = ['down', 'left', 'right', 'up'];
      dirs.forEach((dir, r) => {
        const start = r * 4;
        const key = `anim_${hid}_walk_${dir}`;
        if (!this.anims.exists(key)) {
          this.anims.create({
            key,
            frames: [
              { key: `${hid}_walk`, frame: start },
              { key: `${hid}_walk`, frame: start + 1 },
              { key: `${hid}_walk`, frame: start + 2 },
              { key: `${hid}_walk`, frame: start + 3 },
            ],
            frameRate: 6,
            repeat: -1,
          });
        }
      });

      // Sitting anim (2 breathing frames)
      if (!this.anims.exists(`anim_${hid}_sit`)) {
        this.anims.create({
          key: `anim_${hid}_sit`,
          frames: this.anims.generateFrameNumbers(`${hid}_sit`, { start: 0, end: 1 }),
          frameRate: 2,
          repeat: -1,
        });
      }

      // Battle states: idle, windup, attack, skill, hurt, ko, victory
      const battleStates: Record<string, { frames: number[]; rate: number; repeat: number }> = {
        idle: { frames: [0, 1], rate: 3, repeat: -1 },
        windup: { frames: [2], rate: 4, repeat: 0 },
        attack: { frames: [2, 3], rate: 6, repeat: 0 },
        skill: { frames: [2, 4], rate: 6, repeat: 0 },
        hurt: { frames: [5], rate: 4, repeat: 0 },
        ko: { frames: [6], rate: 1, repeat: -1 },
        victory: { frames: [7], rate: 3, repeat: -1 },
      };
      for (const [state, cfg] of Object.entries(battleStates)) {
        const key = `anim_${hid}_battle_${state}`;
        if (!this.anims.exists(key)) {
          this.anims.create({
            key,
            frames: cfg.frames.map((f) => ({ key: `${hid}_battle`, frame: f })),
            frameRate: cfg.rate,
            repeat: cfg.repeat,
          });
        }
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

    // Exit beacons
    if (!this.anims.exists('anim_exit_beacon')) {
      this.anims.create({
        key: 'anim_exit_beacon',
        frames: this.anims.generateFrameNumbers('exit_beacon', { start: 0, end: 3 }),
        frameRate: 6,
        repeat: -1,
      });
    }
    if (!this.anims.exists('anim_exit_locked')) {
      this.anims.create({
        key: 'anim_exit_locked',
        frames: this.anims.generateFrameNumbers('exit_locked', { start: 0, end: 3 }),
        frameRate: 6,
        repeat: -1,
      });
    }
  }
}
