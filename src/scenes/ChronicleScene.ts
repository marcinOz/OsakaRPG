import Phaser from 'phaser';
import { GAME_W, GAME_H, PAL } from '@/config';
import { txt, TextObj } from '@/ui/Text';
import { Input } from '@/ui/Input';
import { Audio } from '@/audio/ChipAudio';
import { applyCrtToCamera } from '@/fx/CrtPipeline';
import { LivingPaintingPipeline } from '@/fx/LivingPaintingPipeline';
import {
  spawnParticlePreset,
  spawnLightGlow,
  FxHandle,
  ensureChronicleTextures,
} from '@/fx/ChronicleFx';
import {
  ChronicleTimeline,
  kenBurns,
  visibleRect,
  parallaxOffset,
  crewAtShot,
  joinersAtShot,
  typewriterCount,
  CamXform,
  Rect,
} from '@/systems/ChronicleTimeline';
import {
  CHRONICLE_SHOTS,
  CHRONICLE_DEFAULT_LEADER,
  ChronicleShot,
} from '@/content/chronicle';
import { Saves } from '@/systems/Save';
import type { HeroId } from '@/types';
import type { SfxName } from '@/audio/types';

export class ChronicleScene extends Phaser.Scene {
  private inputHandler!: Input;
  private timeline!: ChronicleTimeline;
  private leader: HeroId = CHRONICLE_DEFAULT_LEADER;
  private manifestData: any = null;

  // Render containers
  private rootContainer!: Phaser.GameObjects.Container;
  private shotLayerContainer!: Phaser.GameObjects.Container;
  private uiContainer!: Phaser.GameObjects.Container;

  // Background display slots
  private activeBgSprite!: Phaser.GameObjects.Image;
  private lightsImage: Phaser.GameObjects.Image | null = null;
  private regionSprites: Phaser.GameObjects.Image[] = [];
  private layerSprites: { sprite: Phaser.GameObjects.Image; layerDef: any }[] = [];
  private activeFxHandles: FxHandle[] = [];
  private activeActorsContainer!: Phaser.GameObjects.Container;

  // Letterbox UI
  private topBarText!: TextObj;
  private bottomBarText!: TextObj;
  private pipsGraphics!: Phaser.GameObjects.Graphics;
  private displayedCaptionLen = -1;
  private currentFullCaption = '';

  // Preallocated scratch variables to maintain zero allocation on hot-path update
  private readonly scratchCam: CamXform = { x: 512, y: 288, zoom: 1 };
  private readonly scratchRect: Rect = { x: 0, y: 0, w: 1024, h: 576 };
  private readonly scratchParallax: { x: number; y: number } = { x: 0, y: 0 };

  private isEnding = false;
  private currentSong: string | null = null;

  constructor() {
    super('Chronicle');
  }

  init(data?: { leader?: HeroId }): void {
    const saveList = Saves.list();
    this.leader = data?.leader ?? (saveList[0]?.exists ? (saveList[0].leader as HeroId) : CHRONICLE_DEFAULT_LEADER);
    this.isEnding = false;
    this.displayedCaptionLen = -1;
    this.activeFxHandles = [];
    this.regionSprites = [];
    this.layerSprites = [];
  }

  preload(): void {
    this.load.json('chronicle_manifest', 'assets/chronicle/manifest.json');

    // Load custom chronicle spritesheets
    this.load.spritesheet('chronicle_ice_blue_fire', 'assets/chronicle/sprites/ice_blue_fire.png', {
      frameWidth: 64,
      frameHeight: 80,
    });
    this.load.spritesheet('chronicle_spinning_vinyl', 'assets/chronicle/sprites/spinning_vinyl_deck.png', {
      frameWidth: 48,
      frameHeight: 26,
    });
    this.load.spritesheet('chronicle_birds_v', 'assets/chronicle/sprites/birds_v_formation.png', {
      frameWidth: 48,
      frameHeight: 24,
    });
    this.load.spritesheet('chronicle_shooting_star', 'assets/chronicle/sprites/shooting_star_anim.png', {
      frameWidth: 64,
      frameHeight: 32,
    });
    this.load.spritesheet('chronicle_alley_cat', 'assets/chronicle/sprites/alley_cat.png', {
      frameWidth: 32,
      frameHeight: 20,
    });
    this.load.spritesheet('chronicle_ufc_fight', 'assets/chronicle/sprites/ufc_screen_fight.png', {
      frameWidth: 96,
      frameHeight: 70,
    });
    this.load.image('chronicle_polaroid_2006', 'assets/chronicle/sprites/polaroid_2006.png');
  }

  create(): void {
    applyCrtToCamera(this);
    ensureChronicleTextures(this);

    this.inputHandler = new Input(this);
    this.timeline = new ChronicleTimeline(CHRONICLE_SHOTS);
    this.manifestData = this.cache.json.get('chronicle_manifest');

    // Create scene anims
    this.createChronicleAnimations();

    // Scene layers
    this.rootContainer = this.add.container(0, 0);
    this.shotLayerContainer = this.add.container(0, 0);
    this.activeActorsContainer = this.add.container(0, 0);
    this.uiContainer = this.add.container(0, 0).setDepth(1000);

    this.rootContainer.add(this.shotLayerContainer);
    this.rootContainer.add(this.activeActorsContainer);

    // Primary background display image
    this.activeBgSprite = this.add.image(GAME_W / 2, GAME_H / 2, 'title_bg');
    this.activeBgSprite.setOrigin(0.5, 0.5);
    this.shotLayerContainer.add(this.activeBgSprite);

    // Letterbox & UI setup
    this.setupLetterbox();

    // Fade camera in from black
    this.cameras.main.fadeIn(600, 0, 3, 11);

    // Enter initial shot (support ?shot=N)
    let startShot = 0;
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      const sParam = params.get('shot');
      if (sParam !== null) {
        const parsed = parseInt(sParam, 10);
        if (!isNaN(parsed) && parsed >= 0 && parsed < CHRONICLE_SHOTS.length) {
          startShot = parsed;
          this.timeline.seek(this.timeline.shotStartMs(startShot));
        }
      }
    }
    this.enterShot(startShot);

    // Touch support: tap to skip to next shot
    this.input.on('pointerdown', () => {
      this.handleSkipOrAdvance();
    });

    // Cleanup on scene shutdown
    this.events.once(Phaser.Scenes.Events.SHUTDOWN, () => {
      this.teardownScene();
    });
  }

  private createChronicleAnimations(): void {
    if (!this.anims.exists('anim_ice_blue_fire')) {
      this.anims.create({
        key: 'anim_ice_blue_fire',
        frames: this.anims.generateFrameNumbers('chronicle_ice_blue_fire', { start: 0, end: 5 }),
        frameRate: 8,
        repeat: -1,
      });
    }
    if (!this.anims.exists('anim_spinning_vinyl')) {
      this.anims.create({
        key: 'anim_spinning_vinyl',
        frames: this.anims.generateFrameNumbers('chronicle_spinning_vinyl', { start: 0, end: 3 }),
        frameRate: 10,
        repeat: -1,
      });
    }
    if (!this.anims.exists('anim_birds_v')) {
      this.anims.create({
        key: 'anim_birds_v',
        frames: this.anims.generateFrameNumbers('chronicle_birds_v', { start: 0, end: 5 }),
        frameRate: 6,
        repeat: -1,
      });
    }
    if (!this.anims.exists('anim_shooting_star')) {
      this.anims.create({
        key: 'anim_shooting_star',
        frames: this.anims.generateFrameNumbers('chronicle_shooting_star', { start: 0, end: 5 }),
        frameRate: 12,
        repeat: 0,
      });
    }
    if (!this.anims.exists('anim_alley_cat')) {
      this.anims.create({
        key: 'anim_alley_cat',
        frames: this.anims.generateFrameNumbers('chronicle_alley_cat', { start: 0, end: 5 }),
        frameRate: 8,
        repeat: -1,
      });
    }
    if (!this.anims.exists('anim_ufc_fight')) {
      this.anims.create({
        key: 'anim_ufc_fight',
        frames: this.anims.generateFrameNumbers('chronicle_ufc_fight', { start: 0, end: 5 }),
        frameRate: 6,
        repeat: -1,
      });
    }
  }

  private setupLetterbox(): void {
    const g = this.add.graphics();
    // Top letterbox bar (0..56)
    g.fillStyle(PAL.void, 0.96);
    g.fillRect(0, 0, GAME_W, 56);
    g.lineStyle(1, PAL.steel, 0.75);
    g.lineBetween(0, 56, GAME_W, 56);

    // Bottom letterbox bar (520..576)
    g.fillRect(0, 520, GAME_W, 56);
    g.lineBetween(0, 520, GAME_W, 520);
    this.uiContainer.add(g);

    // Top Bar text (Chapter tag)
    this.topBarText = txt(this, 32, 28, '', {
      color: PAL.yellow,
      big: true,
      origin: [0, 0.5],
    });
    this.uiContainer.add(this.topBarText);

    // Chapter progress pips
    this.pipsGraphics = this.add.graphics();
    this.uiContainer.add(this.pipsGraphics);

    // Bottom Bar typewriter caption
    this.bottomBarText = txt(this, 32, 546, '', {
      color: PAL.white,
      fontSize: '13px',
      fontFamily: 'monospace, sans-serif',
      resolution: 2,
      origin: [0, 0.5],
    });
    this.uiContainer.add(this.bottomBarText);

    // Control hint
    const hintText = txt(this, GAME_W - 32, 546, '[Z / ENTER: DALEJ   •   ESC: MENU]', {
      color: PAL.grey,
      fontSize: '11px',
      fontFamily: 'monospace, sans-serif',
      resolution: 2,
      origin: [1, 0.5],
    });
    this.uiContainer.add(hintText);
  }

  private updatePips(currentIdx: number): void {
    this.pipsGraphics.clear();
    const total = CHRONICLE_SHOTS.length;
    const pipW = 14;
    const gap = 5;
    const totalW = total * pipW + (total - 1) * gap;
    const startX = GAME_W - 32 - totalW;
    const y = 28;

    for (let i = 0; i < total; i++) {
      const px = startX + i * (pipW + gap);
      if (i === currentIdx) {
        this.pipsGraphics.fillStyle(PAL.yellow, 1);
        this.pipsGraphics.fillRect(px, y - 3, pipW, 6);
      } else if (i < currentIdx) {
        this.pipsGraphics.fillStyle(PAL.cyan, 0.8);
        this.pipsGraphics.fillRect(px, y - 2, pipW, 4);
      } else {
        this.pipsGraphics.fillStyle(PAL.steel, 0.45);
        this.pipsGraphics.fillRect(px, y - 2, pipW, 4);
      }
    }
  }

  private enterShot(idx: number): void {
    const shot = CHRONICLE_SHOTS[idx];
    if (!shot) return;

    // Clean up previous shot layers and handles
    this.cleanupCurrentShotFx();

    // 1. Music handling
    if (shot.music && shot.music !== this.currentSong) {
      Audio.playSong(shot.music, { fadeMs: 800 });
      this.currentSong = shot.music;
    }

    // 2. Load background image from manifest if available, else fallback
    const sceneDef = this.manifestData?.scenes?.[shot.scene];
    const bgKey = sceneDef?.base ? `chronicle_${shot.scene}_base` : shot.bg;

    // Dynamically load image if needed
    if (sceneDef?.base && !this.textures.exists(bgKey)) {
      this.load.image(bgKey, sceneDef.base);
      this.load.once(Phaser.Loader.Events.COMPLETE, () => {
        if (this.activeBgSprite?.active) {
          this.activeBgSprite.setTexture(bgKey);
          this.activeBgSprite.setDisplaySize(GAME_W, GAME_H);
        }
      });
      this.load.start();
    } else {
      this.activeBgSprite.setTexture(bgKey);
      this.activeBgSprite.setDisplaySize(GAME_W, GAME_H);
    }

    // 3. Emissive light map
    if (sceneDef?.lightsAsset) {
      const lightsKey = `chronicle_${shot.scene}_lights`;
      if (!this.textures.exists(lightsKey)) {
        this.load.image(lightsKey, sceneDef.lightsAsset);
        this.load.once(Phaser.Loader.Events.COMPLETE, () => {
          this.setupLightsOverlay(lightsKey, sceneDef.lights);
        });
        this.load.start();
      } else {
        this.setupLightsOverlay(lightsKey, sceneDef.lights);
      }
    }

    // 4. Parallax layers from manifest
    if (sceneDef?.layers) {
      for (const layerDef of sceneDef.layers) {
        const lKey = `chronicle_${shot.scene}_${layerDef.id}`;
        if (!this.textures.exists(lKey)) {
          this.load.image(lKey, layerDef.path);
          this.load.once(Phaser.Loader.Events.COMPLETE, () => {
            this.setupLayerSprite(lKey, layerDef);
          });
          this.load.start();
        } else {
          this.setupLayerSprite(lKey, layerDef);
        }
      }
    }

    // 5. Shader regions from manifest
    if (sceneDef?.regions) {
      for (const regionDef of sceneDef.regions) {
        const rKey = `chronicle_${shot.scene}_${regionDef.id}`;
        if (!this.textures.exists(rKey)) {
          this.load.image(rKey, regionDef.path);
          this.load.once(Phaser.Loader.Events.COMPLETE, () => {
            this.setupRegionSprite(rKey, regionDef);
          });
          this.load.start();
        } else {
          this.setupRegionSprite(rKey, regionDef);
        }
      }
    }

    // 6. Spawn procedural particles & FX
    this.setupShotParticles(shot.scene, sceneDef);

    // 7. Spawn hero and enemy actors
    this.setupShotActors(shot, idx);

    // 8. Schedule audio cues
    if (shot.sfxCues) {
      for (const cue of shot.sfxCues) {
        this.time.delayedCall(cue.atMs, () => {
          if (!this.isEnding) Audio.sfx(cue.id as SfxName);
        });
      }
    }

    // 9. Update UI headers
    this.topBarText.setText(shot.tag);
    this.updatePips(idx);
    this.currentFullCaption = shot.caption;
    this.displayedCaptionLen = -1;
    this.bottomBarText.setText('');
  }

  private setupLightsOverlay(key: string, lightList: any[]): void {
    if (this.lightsImage) {
      this.lightsImage.destroy();
    }
    this.lightsImage = this.add.image(GAME_W / 2, GAME_H / 2, key);
    this.lightsImage.setDisplaySize(GAME_W, GAME_H);
    this.lightsImage.setBlendMode('ADD');
    this.lightsImage.setAlpha(0.9);
    this.shotLayerContainer.add(this.lightsImage);

    // Also spawn individual radial glow halos
    if (lightList) {
      for (const ldef of lightList) {
        if (ldef.glow) {
          const handle = spawnLightGlow(this, this.shotLayerContainer, ldef);
          this.activeFxHandles.push(handle);
        }
      }
    }
  }

  private setupLayerSprite(key: string, layerDef: any): void {
    const spr = this.add.image(GAME_W / 2, GAME_H / 2, key);
    spr.setDisplaySize(GAME_W, GAME_H);
    this.shotLayerContainer.add(spr);
    this.layerSprites.push({ sprite: spr, layerDef });
  }

  private setupRegionSprite(key: string, regionDef: any): void {
    const spr = this.add.image(GAME_W / 2, GAME_H / 2, key);
    spr.setDisplaySize(GAME_W, GAME_H);

    // Apply LivingPaintingPipeline
    try {
      if ((spr as any).setPostPipeline) {
        spr.setPostPipeline(LivingPaintingPipeline);
        const pipeline = (spr as any).getPostPipeline?.(LivingPaintingPipeline) as LivingPaintingPipeline;
        if (pipeline) {
          if (regionDef.shader === 'water') {
            pipeline.mode = 0;
            pipeline.params = [regionDef.params?.amp ?? 2.0, regionDef.params?.wavelength ?? 22.0, regionDef.params?.speed ?? 0.6, 0.8];
          } else if (regionDef.shader === 'sway') {
            pipeline.mode = 1;
            pipeline.params = [regionDef.params?.amp ?? 3.0, 16.0, 1.2, 0.0];
          } else if (regionDef.shader === 'swirl') {
            pipeline.mode = 2;
            pipeline.params = [0.8, 0.0001, 1.0, 0.0];
            pipeline.center = regionDef.params?.center ?? [540, 220];
          } else if (regionDef.shader === 'haze') {
            pipeline.mode = 3;
            pipeline.params = [regionDef.params?.amp ?? 2.5, 30.0, 3.5, 0.0];
          }
        }
      }
    } catch {
      // Pipeline fallback
    }

    this.shotLayerContainer.add(spr);
    this.regionSprites.push(spr);
  }

  private setupShotParticles(sceneKey: string, sceneDef: any): void {
    const presets = sceneDef?.particles ?? [];
    for (const p of presets) {
      const handle = spawnParticlePreset(this, this.shotLayerContainer, p.preset, p.params);
      this.activeFxHandles.push(handle);
    }

    // Default per-scene environmental ambience
    if (sceneKey === 'title_lake' || sceneKey === 'marina') {
      const h = spawnParticlePreset(this, this.shotLayerContainer, 'fireflies');
      this.activeFxHandles.push(h);
    } else if (sceneKey === 'campfire') {
      const h = spawnParticlePreset(this, this.shotLayerContainer, 'embers', { x: 512, y: 440 });
      this.activeFxHandles.push(h);
    } else if (sceneKey === 'alley') {
      const h = spawnParticlePreset(this, this.shotLayerContainer, 'rain');
      this.activeFxHandles.push(h);
    } else if (sceneKey === 'forest') {
      const h = spawnParticlePreset(this, this.shotLayerContainer, 'leaves');
      this.activeFxHandles.push(h);
    } else if (sceneKey === 'rift') {
      const h = spawnParticlePreset(this, this.shotLayerContainer, 'debrisSpiral', { x: 540, y: 220 });
      this.activeFxHandles.push(h);
    }
  }

  private setupShotActors(shot: ChronicleShot, shotIdx: number): void {
    this.activeActorsContainer.removeAll(true);

    const crew = crewAtShot(CHRONICLE_SHOTS, shotIdx, this.leader);
    const joiners = joinersAtShot(CHRONICLE_SHOTS, shotIdx, this.leader);

    // Scene-specific staging:
    if (shot.scene === 'flashback_2006') {
      // In Shot 0, 2006 flashback keyframe already depicts the teenage crew on the bench.
      return;
    }

    if (shot.scene === 'campfire' || shot.scene === 'curse') {
      // 6 seated friends around the fire
      const startX = GAME_W / 2 - 250;
      crew.forEach((hid, i) => {
        const x = startX + i * 100;
        const y = 475;
        this.add.ellipse(x, y + 10, 26, 8, 0x000000, 0.45).setDepth(150);
        const spr = this.add.sprite(x, y, `${hid}_sit`, 0).setDepth(160);
        spr.play(`anim_${hid}_sit`);
        this.activeActorsContainer.add(spr);
      });

      // Animated central campfire
      const fireKey = shot.scene === 'curse' ? 'chronicle_ice_blue_fire' : 'fire';
      const animKey = shot.scene === 'curse' ? 'anim_ice_blue_fire' : 'anim_fire';
      const fire = this.add.sprite(512, 455, fireKey, 0).setOrigin(0.5, 0.9).setDepth(200);
      fire.play(animKey);
      this.activeActorsContainer.add(fire);
      return;
    }

    if (shot.scene === 'sunrise' || shot.scene === 'photo') {
      // 6 seated friends on the shoreline watching sunrise
      const startX = GAME_W / 2 - 250;
      crew.forEach((hid, i) => {
        const x = startX + i * 100;
        const y = 490;
        this.add.ellipse(x, y + 10, 26, 8, 0x000000, 0.4).setDepth(150);
        const spr = this.add.sprite(x, y, `${hid}_sit`, 0).setDepth(160);
        spr.play(`anim_${hid}_sit`);
        this.activeActorsContainer.add(spr);
      });
      return;
    }

    // Walking crew formation (Danny, Alior, Barti, etc.)
    const startX = 180;
    crew.forEach((hid, i) => {
      const x = startX + i * 55;
      const y = 475;
      this.add.ellipse(x, y + 10, 22, 6, 0x000000, 0.4).setDepth(150);
      const spr = this.add.sprite(x, y, `${hid}_walk`, 0).setDepth(160);
      spr.play(`anim_${hid}_walk_right`);
      this.activeActorsContainer.add(spr);
    });

    // Joining heroes pop-in highlight
    if (joiners.length > 0) {
      joiners.forEach((jHid, jIdx) => {
        const jX = 540 + jIdx * 70;
        const jY = 475;
        const jSpr = this.add.sprite(jX, jY - 20, `${jHid}_battle`, 0).setDepth(210);
        jSpr.setAlpha(0);
        this.activeActorsContainer.add(jSpr);

        this.time.delayedCall(1600 + jIdx * 600, () => {
          if (!jSpr.active) return;
          jSpr.setAlpha(1);
          Audio.sfx('buff');
          this.tweens.add({
            targets: jSpr,
            y: jY,
            scaleX: { from: 1.4, to: 1.0 },
            scaleY: { from: 1.4, to: 1.0 },
            duration: 350,
            ease: 'Back.easeOut',
          });

          // "+ DOŁĄCZA: NAZWA" tag
          const joinTag = txt(this, jX, jY - 45, `+ DOŁĄCZA: ${jHid.toUpperCase()}`, {
            color: PAL.green,
            origin: [0.5, 0.5],
          }).setDepth(220);
          this.activeActorsContainer.add(joinTag);

          this.tweens.add({
            targets: joinTag,
            y: jY - 55,
            alpha: 0,
            duration: 1800,
            delay: 800,
            onComplete: () => joinTag.destroy(),
          });
        });
      });
    }

    // Enemy cameo
    if (shot.actors) {
      for (const actor of shot.actors) {
        if (actor.kind === 'enemy') {
          const eid = actor.ref;
          const eSpr = this.add.sprite(actor.from[0], actor.from[1], `enemy_${eid}`, 0).setDepth(180);
          eSpr.setAlpha(0);
          this.activeActorsContainer.add(eSpr);

          this.time.delayedCall(actor.enterAtMs ?? 1000, () => {
            if (!eSpr.active) return;
            this.tweens.add({
              targets: eSpr,
              alpha: 0.95,
              duration: 400,
              ease: 'Sine.easeIn',
            });
          });

          if (actor.exitAtMs) {
            this.time.delayedCall(actor.exitAtMs, () => {
              if (!eSpr.active) return;
              this.tweens.add({
                targets: eSpr,
                alpha: 0,
                duration: 400,
                onComplete: () => eSpr.destroy(),
              });
            });
          }
        }
      }
    }
  }

  private cleanupCurrentShotFx(): void {
    for (const h of this.activeFxHandles) {
      h.destroy();
    }
    this.activeFxHandles = [];

    for (const spr of this.regionSprites) {
      spr.destroy();
    }
    this.regionSprites = [];

    for (const item of this.layerSprites) {
      item.sprite.destroy();
    }
    this.layerSprites = [];

    if (this.lightsImage) {
      this.lightsImage.destroy();
      this.lightsImage = null;
    }
  }

  private handleSkipOrAdvance(): void {
    if (this.isEnding) return;
    Audio.sfx('confirm');
    this.timeline.skipToNext();
  }

  private finishChronicle(): void {
    if (this.isEnding) return;
    this.isEnding = true;
    Audio.sfx('confirm');

    this.cameras.main.fadeOut(800, 0, 3, 11);
    this.cameras.main.once(Phaser.Cameras.Scene2D.Events.FADE_OUT_COMPLETE, () => {
      this.scene.start('Title');
    });
  }

  private teardownScene(): void {
    this.cleanupCurrentShotFx();
    this.activeActorsContainer.removeAll(true);
    this.time.removeAllEvents();
    this.tweens.killAll();
  }

  override update(_time: number, delta: number): void {
    if (this.isEnding) return;

    // Handle button inputs
    if (this.inputHandler.pressed('cancel') || this.inputHandler.pressed('menu')) {
      this.finishChronicle();
      return;
    }
    if (this.inputHandler.pressed('ok')) {
      this.handleSkipOrAdvance();
      return;
    }

    // Advance pure simulation timeline
    const s = this.timeline.tick(delta);

    if (s.enteredShot) {
      this.enterShot(s.shotIdx);
    }

    if (s.done) {
      this.finishChronicle();
      return;
    }

    const shot = CHRONICLE_SHOTS[s.shotIdx];
    if (!shot) return;

    // Apply Ken Burns zoom & pan to active background
    kenBurns(shot.cam.from, shot.cam.to, s.t, shot.cam.ease, this.scratchCam);
    visibleRect(this.scratchCam, this.scratchRect);

    // Set scale & position on background
    this.activeBgSprite.setScale(this.scratchCam.zoom);
    this.activeBgSprite.setPosition(
      GAME_W / 2 + (GAME_W / 2 - this.scratchCam.x) * (this.scratchCam.zoom - 1),
      GAME_H / 2 + (GAME_H / 2 - this.scratchCam.y) * (this.scratchCam.zoom - 1)
    );

    // Apply parallax to active layers
    for (const item of this.layerSprites) {
      const factor = item.layerDef.parallax ?? 1.0;
      parallaxOffset(this.scratchCam.x, this.scratchCam.y, factor, 2, this.scratchParallax);
      item.sprite.setPosition(GAME_W / 2 + this.scratchParallax.x, GAME_H / 2 + this.scratchParallax.y);
      item.sprite.setScale(this.scratchCam.zoom);
    }

    // Update lights map transform to match base
    if (this.lightsImage) {
      this.lightsImage.setScale(this.scratchCam.zoom);
      this.lightsImage.setPosition(this.activeBgSprite.x, this.activeBgSprite.y);
    }

    // Update region shaders transform
    for (const spr of this.regionSprites) {
      spr.setScale(this.scratchCam.zoom);
      spr.setPosition(this.activeBgSprite.x, this.activeBgSprite.y);
    }

    // Update Typewriter caption
    const charsToShow = typewriterCount(this.currentFullCaption.length, s.localMs, 32, 200);
    if (charsToShow !== this.displayedCaptionLen) {
      this.displayedCaptionLen = charsToShow;
      this.bottomBarText.setText(this.currentFullCaption.substring(0, charsToShow));
      if (charsToShow > 0 && charsToShow % 3 === 0 && charsToShow < this.currentFullCaption.length) {
        Audio.sfx('blip', { vol: 0.12 });
      }
    }

    // Tick active FX handles (particles, swinging lights)
    for (const h of this.activeFxHandles) {
      h.update(delta, s.t);
    }
  }
}
