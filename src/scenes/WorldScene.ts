import Phaser from 'phaser';
import { GAME_W, GAME_H, PAL, TILE } from '@/config';
import { HeroId } from '@/types';
import { GameData, newGame, walkSpeedMultiplier, hasFlag, setFlag, removeWorldStatus, addToParty } from '@/systems/GameState';
import { CH01 } from '@/content/chapters/ch01';
import { CH02 } from '@/content/chapters/ch02';
import { CH03 } from '@/content/chapters/ch03';
import { CH04 } from '@/content/chapters/ch04';
import { CH05 } from '@/content/chapters/ch05';
import { CH06 } from '@/content/chapters/ch06';
import { DialogueBox } from '@/ui/DialogueBox';
import { DialogueRunner } from '@/systems/Dialogue';
import { Input } from '@/ui/Input';
import { Audio } from '@/audio/ChipAudio';
import { applyCrtToCamera } from '@/fx/CrtPipeline';
import { txt } from '@/ui/Text';
import { drawPanel } from '@/ui/Panel';
import { setTimeOfDay } from '@/fx/Palette';
import { InteractPrompt } from '@/ui/InteractPrompt';
import { startBattle } from '@/content/encounters';

interface TrailPoint {
  x: number;
  y: number;
  dir: string;
}

interface MapExitDef {
  x: number;
  y: number;
  targetMap: string;
  targetX: number;
  targetY: number;
  isUnlocked: (state: GameData) => boolean;
  lockedReason: string;
}

export interface Interactable {
  id: string;
  x: number;
  y: number;
  label: string;
  isAlert?: boolean;
  action: () => void | Promise<void>;
  isAvailable?: () => boolean;
}

const MAP_EXITS: Record<string, MapExitDef> = {
  apartment: {
    x: 10,
    y: 11,
    targetMap: 'city',
    targetX: 5,
    targetY: 4,
    isUnlocked: (state) => hasFlag(state, 'ch1_fought_spine') && hasFlag(state, 'ch1_fought_slack'),
    lockedReason: '[!] Najpierw muszę ogarnąć kręgosłup i wyciszyć Slacka na biurku!',
  },
  city: {
    x: 38,
    y: 5,
    targetMap: 'garage',
    targetX: 2,
    targetY: 5,
    isUnlocked: (state) => hasFlag(state, 'bought_coffee'),
    lockedReason: '[!] Najpierw muszę wejść do Żabki po kawę i elektrolity!',
  },
  zabka: {
    x: 5,
    y: 7,
    targetMap: 'city',
    targetX: 5,
    targetY: 4,
    isUnlocked: () => true,
    lockedReason: '',
  },
  garage: {
    x: 16,
    y: 6,
    targetMap: 'pub',
    targetX: 2,
    targetY: 5,
    isUnlocked: (state) => hasFlag(state, 'danny_alior_joined'),
    lockedReason: '[!] Najpierw musimy ogarnąć sprawę w garażu!',
  },
  pub: {
    x: 16,
    y: 6,
    targetMap: 'alley',
    targetX: 2,
    targetY: 5,
    isUnlocked: (state) => hasFlag(state, 'barti_joined'),
    lockedReason: '[!] Najpierw musimy pomóc Bartiemu przy konsoli!',
  },
  alley: {
    x: 16,
    y: 5,
    targetMap: 'marina',
    targetX: 2,
    targetY: 4,
    isUnlocked: (state) => hasFlag(state, 'lisu_joined'),
    lockedReason: '[!] Nie możemy iść dalej bez Lisa!',
  },
  marina: {
    x: 14,
    y: 4,
    targetMap: 'forest',
    targetX: 3,
    targetY: 5,
    isUnlocked: (state) => hasFlag(state, 'luki_joined'),
    lockedReason: '[!] Najpierw musimy wyłowić Łukiego z wody!',
  },
  forest: {
    x: 8,
    y: 4,
    targetMap: 'campfire',
    targetX: 0,
    targetY: 0,
    isUnlocked: (state) => hasFlag(state, 'oziem_joined'),
    lockedReason: '[!] Odszukajmy najpierw Oziema przy szałasie!',
  },
};

export class WorldScene extends Phaser.Scene {
  private state!: GameData;
  private inputHandler!: Input;
  private dialogueBox!: DialogueBox;
  private interactPrompt!: InteractPrompt;
  private playerSprite!: Phaser.GameObjects.Sprite;
  private followerSprites: Map<string, Phaser.GameObjects.Sprite> = new Map();
  private trail: TrailPoint[] = [];

  private mapContainer!: Phaser.GameObjects.Container;
  private npcSprites: Phaser.GameObjects.Sprite[] = [];
  private propSprites: Phaser.GameObjects.Image[] = [];
  private hudContainer!: Phaser.GameObjects.Container;
  private hudText!: Phaser.GameObjects.BitmapText | Phaser.GameObjects.Text;
  private isBusy = false;
  private currentMap = 'apartment';

  private exitBeaconSprite: Phaser.GameObjects.Sprite | null = null;
  private toastContainer: Phaser.GameObjects.Container | null = null;
  private toastCooldown = 0;
  private isPhoneOpen = false;

  private mapW = 18;
  private mapH = 12;
  private solids: boolean[][] = [];

  // QTE state
  private qteContainer: Phaser.GameObjects.Container | null = null;
  private qteMarkerX = 0;
  private qteMarkerSpeed = 160;
  private qteCallback: ((success: boolean) => void) | null = null;

  constructor() {
    super('World');
  }

  init(data: { leader?: HeroId; loadSave?: GameData; returnFromBattle?: boolean; battleResult?: 'victory' | 'defeat'; state?: GameData }): void {
    if (data.loadSave) {
      this.state = data.loadSave;
    } else if (data.state) {
      this.state = data.state;
    } else if (data.leader) {
      this.state = newGame(data.leader);
    } else if (!this.state) {
      this.state = newGame('danny');
    }

    if (this.state?.mapId) {
      this.currentMap = this.state.mapId;
    }

    // Clean up lingering GameObjects and caches on scene shutdown
    this.events.once(Phaser.Scenes.Events.SHUTDOWN, () => {
      this.followerSprites.clear();
      this.trail = [];
      this.npcSprites = [];
      this.propSprites = [];
      this.toastContainer = null;
      this.qteContainer = null;
      this.exitBeaconSprite = null;
    });

    if (data.returnFromBattle) {
      this.isBusy = false;
      // Handle post-battle storyline
      if (this.currentMap === 'apartment') {
        if (hasFlag(this.state, 'ch1_fought_spine') && !hasFlag(this.state, 'ch1_spine_reported')) {
          setFlag(this.state, 'ch1_spine_reported', true);
          this.time.delayedCall(300, async () => {
            this.isBusy = true;
            const runner = new DialogueRunner(CH01.afterSpineFight, this.state.leader);
            await this.dialogueBox.play(runner.allResolved());
            this.isBusy = false;
          });
        } else if (hasFlag(this.state, 'ch1_fought_slack') && !hasFlag(this.state, 'ch1_slack_reported')) {
          setFlag(this.state, 'ch1_slack_reported', true);
          this.time.delayedCall(300, async () => {
            this.isBusy = true;
            const runner = new DialogueRunner(CH01.afterSlackFight, this.state.leader);
            await this.dialogueBox.play(runner.allResolved());
            this.updateExitBeacon();
            this.isBusy = false;
          });
        }
      } else if (this.currentMap === 'garage' && hasFlag(this.state, 'fought_sasiad') && !hasFlag(this.state, 'danny_alior_joined')) {
        this.time.delayedCall(300, () => this.afterSasiadBoss());
      } else if (this.currentMap === 'pub' && hasFlag(this.state, 'fought_hipsters') && !hasFlag(this.state, 'barti_joined')) {
        this.time.delayedCall(300, () => this.afterPubBattle());
      } else if (this.currentMap === 'alley' && hasFlag(this.state, 'fought_kark') && !hasFlag(this.state, 'lisu_joined')) {
        this.time.delayedCall(300, () => this.afterKarkBattle());
      }
    }
  }

  create(): void {
    applyCrtToCamera(this);
    this.cameras.main.setBackgroundColor(PAL.void);
    this.cameras.main.fadeIn(300, 0, 3, 11);

    this.mapContainer = this.add.container(0, 0).setDepth(10);
    this.hudContainer = this.add.container(0, 0).setDepth(900).setScrollFactor(0);

    this.buildMap(this.currentMap);
    this.updateAtmosphere();

    // Player sprite (32x48 frame, origin 0.5, 0.75 for 32px tile grid)
    const px = this.state.x * TILE + TILE / 2;
    const py = this.state.y * TILE + TILE / 2;
    this.playerSprite = this.add.sprite(px, py, `${this.state.leader}_walk`, 0);
    this.playerSprite.setOrigin(0.5, 0.75);
    this.playerSprite.setDepth(this.playerSprite.y + 12);
    this.playerSprite.play(`anim_${this.state.leader}_walk_down`);
    this.playerSprite.stop();

    this.cameras.main.startFollow(this.playerSprite, true, 0.1, 0.1);
    this.cameras.main.setBounds(0, 0, this.mapW * TILE, this.mapH * TILE);

    // Initialize fresh follower sprites and trail buffer
    this.followerSprites.clear();
    this.trail = [];
    const initialFacing = this.state.facing || 'down';
    for (let i = 0; i < 40; i++) {
      this.trail.push({ x: this.playerSprite.x, y: this.playerSprite.y, dir: initialFacing });
    }
    this.syncFollowerSprites();

    // HUD Top Bar
    const hg = this.add.graphics();
    drawPanel(hg, 4, 4, GAME_W - 8, 16, { fill: PAL.navy, border: PAL.steel, glow: false });
    this.hudContainer.add(hg);

    this.hudText = txt(this, 10, 8, '', { color: PAL.cyan });
    this.hudContainer.add(this.hudText);
    this.updateHud();

    // Persistent Action Keys Legend HUD (560x28, frame 0 = overworld)
    const legendImg = this.add.image(GAME_W / 2, GAME_H - 18, 'keys_legend', 0);
    this.hudContainer.add(legendImg);

    this.dialogueBox = new DialogueBox(this, 1000);
    this.interactPrompt = new InteractPrompt(this);
    this.inputHandler = new Input(this);

    // Initial wake-up sequence
    if (this.currentMap === 'apartment' && !hasFlag(this.state, 'ch1_woke_up')) {
      this.time.delayedCall(400, () => this.runWakeUpSequence());
    }
  }

  private updateAtmosphere(): void {
    if (this.currentMap === 'apartment' || this.currentMap === 'city' || this.currentMap === 'zabka') {
      setTimeOfDay(this, 'morning');
      Audio.playSong('ch01_explore', { fadeMs: 500 });
    } else if (this.currentMap === 'garage') {
      setTimeOfDay(this, 'day');
      Audio.playSong('ch02_garage', { fadeMs: 500 });
    } else if (this.currentMap === 'pub') {
      setTimeOfDay(this, 'dusk');
      Audio.playSong('ch03_pub', { fadeMs: 500 });
    } else if (this.currentMap === 'alley') {
      setTimeOfDay(this, 'night');
      Audio.playSong('ch04_alley', { fadeMs: 500 });
    } else if (this.currentMap === 'marina') {
      setTimeOfDay(this, 'night');
      Audio.playSong('ch05_marina', { fadeMs: 500 });
    } else if (this.currentMap === 'forest') {
      setTimeOfDay(this, 'night');
      Audio.playSong('camp', { fadeMs: 500 });
    }
  }

  private updateHud(): void {
    const leaderName = this.state.leader.toUpperCase();
    const partyCount = this.state.party.length;
    let loc = 'MIESZKANIE';
    if (this.currentMap === 'city') loc = 'PORANNE MIASTO';
    else if (this.currentMap === 'zabka') loc = 'ŻABKA (24/7)';
    else if (this.currentMap === 'garage') loc = 'GARAŻ (UFC HQ)';
    else if (this.currentMap === 'pub') loc = 'PUB CZARNY KRĄŻEK';
    else if (this.currentMap === 'alley') loc = 'ZAUŁKI STARÓWKI';
    else if (this.currentMap === 'marina') loc = 'PRZYSTAŃ MARINA';
    else if (this.currentMap === 'forest') loc = 'LEŚNE OBOZOWISKO';

    const hasHangover = this.state.worldStatuses.includes('kacGigant');
    const statusTag = hasHangover ? ' [DEBUFF: KAC GIGANT]' : ' [STATUS: OK]';
    (this.hudText as any).setText(`LIDER: ${leaderName} | EKIPA: ${partyCount}/6 | R${this.state.chapter}: ${loc}${statusTag}`);
  }

  private syncFollowerSprites(): void {
    const followers = this.state.party.slice(1);
    for (const [hid, spr] of this.followerSprites.entries()) {
      if (!followers.includes(hid as HeroId) || !spr.scene || !spr.active || !spr.anims) {
        if (spr.scene && spr.active) {
          spr.destroy();
        }
        this.followerSprites.delete(hid);
      }
    }

    followers.forEach((hid) => {
      const existing = this.followerSprites.get(hid);
      if (!existing || !existing.scene || !existing.active || !existing.anims) {
        const fspr = this.add.sprite(this.playerSprite.x, this.playerSprite.y, `${hid}_walk`, 0);
        fspr.setOrigin(0.5, 0.75);
        fspr.setDepth(fspr.y + 12);
        fspr.play(`anim_${hid}_walk_down`);
        fspr.stop();
        this.followerSprites.set(hid, fspr);
      }
    });
  }

  private addTile(x: number, y: number, key: string, tileIdx: number, isSolid = false, isUprightProp = false): void {
    if (y < 0 || y >= this.mapH || x < 0 || x >= this.mapW) return;
    this.solids[y][x] = isSolid;
    const px = x * TILE + TILE / 2;
    const py = y * TILE + TILE / 2;
    if (isUprightProp) {
      // Upright prop sprite depth-sorted at prop base
      const propSpr = this.add.image(px, py, key).setDepth(y * TILE + 24);
      propSpr.setCrop(tileIdx * TILE, 0, TILE, TILE);
      this.propSprites.push(propSpr);
    }
  }

  private addNpc(x: number, y: number, hid: string): void {
    const npc = this.add.sprite(x * TILE + TILE / 2, y * TILE + TILE / 2, `${hid}_walk`, 0);
    npc.setOrigin(0.5, 0.75);
    npc.setDepth(y * TILE + TILE / 2 + 12);
    this.npcSprites.push(npc);
  }

  private removeNpcSprite(hid: string): void {
    this.npcSprites = this.npcSprites.filter((spr) => {
      if (spr.texture.key.startsWith(hid)) {
        spr.destroy();
        return false;
      }
      return true;
    });
  }

  private buildMap(mapName: string): void {
    this.mapContainer.removeAll(true);
    this.propSprites.forEach((p) => p.destroy());
    this.propSprites = [];
    this.npcSprites.forEach((n) => n.destroy());
    this.npcSprites = [];
    if (this.exitBeaconSprite) {
      this.exitBeaconSprite.destroy();
      this.exitBeaconSprite = null;
    }
    this.interactPrompt?.hide();

    if (mapName === 'apartment' || mapName === 'zabka' || mapName === 'garage' || mapName === 'pub') {
      this.mapW = 32;
      this.mapH = 18;
    } else if (mapName === 'city' || mapName === 'alley' || mapName === 'marina' || mapName === 'forest') {
      this.mapW = 40;
      this.mapH = 18;
    }
    this.cameras.main.setBounds(0, 0, this.mapW * TILE, this.mapH * TILE);

    // Render HD map background layer for all maps
    const bg = this.add.image(0, 0, `map_${mapName}_bg`).setOrigin(0, 0);
    this.mapContainer.add(bg);

    this.solids = [];
    for (let y = 0; y < this.mapH; y++) {
      this.solids[y] = [];
      for (let x = 0; x < this.mapW; x++) {
        this.solids[y][x] = false;
      }
    }

    if (mapName === 'apartment') {
      this.buildApartmentMap();
    } else if (mapName === 'city') {
      this.buildCityMap();
    } else if (mapName === 'zabka') {
      this.buildZabkaMap();
    } else if (mapName === 'garage') {
      this.buildGarageMap();
    } else if (mapName === 'pub') {
      this.buildPubMap();
    } else if (mapName === 'alley') {
      this.buildAlleyMap();
    } else if (mapName === 'marina') {
      this.buildMarinaMap();
    } else if (mapName === 'forest') {
      this.buildForestMap();
    }

    this.setupExitBeacon(mapName);
  }

  private buildApartmentMap(): void {
    for (let y = 0; y < this.mapH; y++) {
      for (let x = 0; x < this.mapW; x++) {
        let tileIdx = 0;
        let isSolid = false;
        let isProp = false;

        // Outer perimeter solid walls (left x=0, right x=31, top y=0,1, bottom y=17)
        if (y === 0 || y === 1 || y === this.mapH - 1 || x === 0 || x === this.mapW - 1) {
          tileIdx = 1;
          isSolid = true;
        }

        // Architectural partition walls dividing bedroom from living room
        if (x === 11 && (y <= 4 || (y >= 7 && y <= 10))) {
          tileIdx = 1;
          isSolid = true;
        }
        // Bedroom south wall (y = 11, x = 1..9)
        if (y === 11 && x >= 1 && x <= 9) {
          tileIdx = 1;
          isSolid = true;
        }
        // Outer wall behind the entrance door (y = 12, x = 9..11)
        if (y >= 12 && x >= 9 && x <= 11) {
          tileIdx = 1;
          isSolid = true;
        }

        // Furniture & Upright Props in bedroom
        if (x === 3 && y === 2) { tileIdx = 3; isSolid = true; isProp = true; } // battlestation desk
        if (x === 3 && y === 3) { tileIdx = 4; isSolid = false; isProp = true; } // gaming chair (walkable)
        if ((x === 6 || x === 7) && y === 5) { tileIdx = 5; isSolid = true; isProp = true; } // platform bed
        if (x === 8 && y === 2) { tileIdx = 6; isSolid = true; isProp = true; } // monstera plant
        if (x === 1 && y === 7) { isSolid = true; } // gym weights

        // Kitchenette & Lounge obstacles
        if (x === 16 && y === 2) { isSolid = true; } // fridge
        if (x >= 17 && x <= 24 && y === 2) { isSolid = true; } // kitchen counter
        if (x >= 20 && x <= 24 && y === 8) { isSolid = true; } // sofa
        if (x >= 27 && x <= 29 && y === 10) { isSolid = true; } // TV credenza / Pegasus

        // Exit Door at (10, 11) - must be WALKABLE so player triggers exit check!
        if (x === 10 && y === 11) {
          tileIdx = 7;
          isSolid = false;
          isProp = false;
        }

        this.addTile(x, y, 'tiles_apartment', tileIdx, isSolid, isProp);
      }
    }
  }

  private buildCityMap(): void {
    for (let y = 0; y < this.mapH; y++) {
      for (let x = 0; x < this.mapW; x++) {
        let tileIdx = 1; // sidewalk
        let isSolid = false;
        let isProp = false;

        // Rows 0, 1, 2: Historic tenement building facades
        if (y <= 2) {
          tileIdx = (x % 2 === 0) ? 2 : 3;
          isSolid = true;
        }

        // Żabka entrance doors at (5, 3) (walkable trigger to enter Żabka)
        if (x === 5 && y === 3) {
          tileIdx = 6;
          isSolid = false;
          isProp = false;
        }

        // Outer borders: west column 0, south row 17, east column 39 (except garage ramp at y=5)
        if (x === 0 || y === this.mapH - 1) {
          isSolid = true;
        }
        if (x === this.mapW - 1 && y !== 5) {
          isSolid = true;
        }

        // Sidewalk obstacles & props
        if (x === 8 && y === 4) { isSolid = true; } // Sąsiadka on bench
        if (x === 10 && y === 4) { tileIdx = 8; isSolid = true; isProp = true; } // Streetlamp
        if ((x === 24 || x === 34) && y === 4) { tileIdx = 8; isSolid = true; isProp = true; } // Streetlamps

        // Garage entrance shutter at (38, 5)
        if (x === 38 && y === 5) {
          tileIdx = 10;
          isSolid = false;
          isProp = false;
        }

        this.addTile(x, y, 'tiles_city', tileIdx, isSolid, isProp);
      }
    }
  }

  private buildZabkaMap(): void {
    for (let y = 0; y < this.mapH; y++) {
      for (let x = 0; x < this.mapW; x++) {
        let tileIdx = 0; // Checkered linoleum floor
        let isSolid = false;
        let isProp = false;

        // Perimeter walls: top row 0, west column 0, east column 31, south row 17
        if (y === 0 || x === 0 || x === this.mapW - 1 || y === this.mapH - 1) {
          tileIdx = 7;
          isSolid = true;
        }

        // Top wall shelves & coolers at row 1
        if (y === 1) {
          if (x >= 1 && x <= 4) {
            tileIdx = 2; // Snack shelves
            isSolid = true;
            isProp = true;
          } else if (x >= 7 && x <= 24) {
            tileIdx = 1; // Beverage refrigerators
            isSolid = true;
            isProp = true;
          } else if (x >= 25 && x <= 30) {
            isSolid = true; // Bakery display
          }
        }

        // Checkout Counter row at y=2
        if (y === 2 && x >= 3 && x <= 6) {
          isSolid = true;
          isProp = true;
          if (x === 4) {
            tileIdx = 4; // Hot dog grill & coffee machine
          } else if (x === 5) {
            tileIdx = 3; // POS cash register counter
          }
        }

        // Center gondolas at rows 4..5 and 8..9
        if ((y === 4 || y === 5 || y === 8 || y === 9)) {
          if ((x >= 8 && x <= 14) || (x >= 18 && x <= 24)) {
            tileIdx = 6; // Promo gondola
            isSolid = true;
            isProp = true;
          }
        }

        // Ice cream freezer at x = 27..30, y = 6..8
        if (x >= 27 && x <= 30 && y >= 6 && y <= 8) {
          isSolid = true;
        }

        // Exit doormats at (5, 7) and (5, 16) / (5, 17)
        if (x === 5 && (y === 7 || y === 16 || y === 17)) {
          tileIdx = 5;
          isSolid = false;
          isProp = false;
        }

        this.addTile(x, y, 'tiles_zabka', tileIdx, isSolid, isProp);
      }
    }
  }

  private buildGarageMap(): void {
    for (let y = 0; y < this.mapH; y++) {
      for (let x = 0; x < this.mapW; x++) {
        let tileIdx = 0; // concrete
        let isSolid = false;
        let isProp = false;

        // Perimeter walls: rows 0, 1 solid; bottom row 17 solid; west col 0 solid; east col 31 solid
        if (y === 0) {
          tileIdx = 2;
          isSolid = true;
        } else if (y === 1) {
          tileIdx = 1;
          isSolid = true;
        } else if (y === this.mapH - 1 || x === 0 || x === this.mapW - 1) {
          tileIdx = 1;
          isSolid = true;
        }

        // Props & Obstacles
        if (x === 3 && y === 2) { tileIdx = 3; isSolid = true; isProp = true; } // tires
        if (x === 4 && y === 2) { tileIdx = 4; isSolid = true; isProp = true; } // weights / tool chest
        if (x === 6 && y === 2) { isSolid = true; } // punching bag
        if (x === 8 && y === 2) { tileIdx = 6; isSolid = true; isProp = true; } // projector UFC
        if (x === 14 && y === 2) { tileIdx = 5; isSolid = true; isProp = true; } // beer fridge
        if (x === 7 && y === 4) { isSolid = true; } // barbell on floor
        if (x >= 20 && x <= 23 && y === 6) { isSolid = true; } // leather sofa

        // Exit to Pub at (16, 6) / (17, 6) - WALKABLE!
        if ((x === 16 || x === 17) && y === 6) {
          tileIdx = 7;
          isSolid = false;
          isProp = false;
        }

        this.addTile(x, y, 'tiles_garage', tileIdx, isSolid, isProp);
      }
    }

    // Spawn Danny & Alior NPCs if they haven't joined yet
    if (!this.state.party.includes('danny')) {
      this.addNpc(5, 4, 'danny');
    }
    if (!this.state.party.includes('alior')) {
      this.addNpc(8, 4, 'alior');
    }
  }

  private buildPubMap(): void {
    for (let y = 0; y < this.mapH; y++) {
      for (let x = 0; x < this.mapW; x++) {
        let tileIdx = 0; // dark wood floor
        let isSolid = false;
        let isProp = false;

        // Perimeter walls: rows 0, 1 solid; bottom row 17 solid; west col 0 solid; east col 31 solid
        if (y === 0) {
          tileIdx = 2;
          isSolid = true;
        } else if (y === 1) {
          tileIdx = 1;
          isSolid = true;
        } else if (y === this.mapH - 1 || x === 0 || x === this.mapW - 1) {
          tileIdx = 1;
          isSolid = true;
        }

        // Bar counter & DJ setup
        if (y === 3 && x >= 4 && x <= 12) {
          tileIdx = (x === 8) ? 4 : (x === 10 ? 6 : 3);
          isSolid = true;
          isProp = true;
        }
        // Back shelves behind bar (except Barti position at x=10, y=2)
        if (y === 2 && x >= 4 && x <= 12 && x !== 10) {
          isSolid = true;
        }
        if (x === 14 && y === 2) { tileIdx = 5; isSolid = true; isProp = true; } // vinyl rack

        // Lounge tables
        if ((x === 22 && y === 9) || (x === 26 && y === 12)) {
          isSolid = true;
        }

        // Exit to Alley at (16, 6) / (17, 6) - WALKABLE!
        if ((x === 16 || x === 17) && y === 6) {
          tileIdx = 7;
          isSolid = false;
          isProp = false;
        }

        this.addTile(x, y, 'tiles_pub', tileIdx, isSolid, isProp);
      }
    }

    // Spawn Barti NPC behind DJ decks if not joined yet
    if (!this.state.party.includes('barti')) {
      this.addNpc(10, 2, 'barti');
    }
  }

  private buildAlleyMap(): void {
    for (let y = 0; y < this.mapH; y++) {
      for (let x = 0; x < this.mapW; x++) {
        let tileIdx = 0; // cobblestone
        let isSolid = false;
        let isProp = false;

        // Rows 0, 1, 2: Tenement building facades
        if (y === 0) {
          tileIdx = 2;
          isSolid = true;
        } else if (y === 1 || y === 2) {
          tileIdx = 1;
          isSolid = true;
        }

        // Outer borders: west col 0 solid, south row 17 solid, east col 39 solid (except archway exit at y=5,6)
        if (x === 0 || y === this.mapH - 1) {
          isSolid = true;
        }
        if (x === this.mapW - 1 && y !== 5 && y !== 6) {
          isSolid = true;
        }

        // Props & Obstacles
        if (x === 10 && y === 4) { tileIdx = 3; isSolid = true; isProp = true; } // dumpster
        if ((x === 5 || x === 13 || x === 24 || x === 35) && y === 3) { tileIdx = 4; isSolid = true; isProp = true; } // streetlamps
        if ((x === 3 || x === 20) && y === 4) { tileIdx = 5; isSolid = true; isProp = true; } // wooden crates

        // Exit archway to Marina: both (16..17, 5..6) and far right (38..39, 5..6) are WALKABLE exits!
        if ((x === 16 || x === 17) && (y === 5 || y === 6)) {
          tileIdx = 7;
          isSolid = false;
          isProp = false;
        }
        if ((x === 38 || x === 39) && (y === 5 || y === 6)) {
          tileIdx = 7;
          isSolid = false;
          isProp = false;
        }

        this.addTile(x, y, 'tiles_alley', tileIdx, isSolid, isProp);
      }
    }

    // Spawn Lisu NPC near dumpster if not joined yet
    if (!this.state.party.includes('lisu')) {
      this.addNpc(10, 3, 'lisu');
    }
  }

  private buildMarinaMap(): void {
    for (let y = 0; y < this.mapH; y++) {
      for (let x = 0; x < this.mapW; x++) {
        let tileIdx = 0; // pier plank
        let isSolid = false;
        let isProp = false;

        // Lake water top (y < 3) and bottom (y > 7)
        if (y < 3 || y > 7) {
          tileIdx = 1; // water
          isSolid = true;
        } else if (y === 3) {
          tileIdx = 6; // pier railing
          isSolid = true;
          isProp = true;
        } else if (y === 7) {
          tileIdx = 2; // pier edge
          isSolid = true;
        }

        // West border & East border
        if (x === 0 || x === this.mapW - 1) {
          isSolid = true;
        }

        // Props & Equipment
        if (x === 6 && y === 3) { tileIdx = 4; isSolid = true; isProp = true; } // lifebuoy rack
        if ((x === 11 || x === 25) && y === 3) { tileIdx = 7; isSolid = true; isProp = true; } // pier lanterns
        if ((x === 4 || x === 12 || x === 22 || x === 32) && y === 7) { tileIdx = 3; isSolid = true; isProp = true; } // mooring bollards
        if (x === 15 && (y === 4 || y === 5)) { tileIdx = 5; isSolid = false; isProp = true; } // rescue motorboat (walkable / boardable)

        this.addTile(x, y, 'tiles_marina', tileIdx, isSolid, isProp);
      }
    }

    // Spawn Łuki NPC at pier edge if not joined yet
    if (!this.state.party.includes('luki')) {
      this.addNpc(10, 4, 'luki');
    }
  }

  private buildForestMap(): void {
    for (let y = 0; y < this.mapH; y++) {
      for (let x = 0; x < this.mapW; x++) {
        let tileIdx = 0; // pine needle floor
        let isSolid = false;
        let isProp = false;

        // Dense impassable pine tree wall enclosing clearing on all sides
        if (y <= 2 || y >= this.mapH - 2 || x <= 1 || x >= this.mapW - 2) {
          tileIdx = 2; // dense ancient pine trunks
          isSolid = true;
        }

        // Dirt path across clearing
        if (y === 5 && x >= 2 && x <= this.mapW - 3) {
          tileIdx = 1;
        }

        // Props
        if (x === 9 && y === 5) {
          tileIdx = 5;
          isSolid = true;
          isProp = true;
        } // stone campfire ring
        if ((x === 5 && y === 3) || (x === 13 && y === 3)) {
          tileIdx = 6;
          isSolid = true;
          isProp = true;
        } // ripstop camping hammocks
        if ((x === 7 && y === 5) || (x === 11 && y === 5)) {
          isSolid = true; // split log benches
        }
        if ((x === 4 && y === 10) || (x === 16 && y === 12) || (x === 28 && y === 8)) {
          tileIdx = 4;
          isSolid = true;
          isProp = true;
        } // mossy granite boulders

        this.addTile(x, y, 'tiles_forest', tileIdx, isSolid, isProp);
      }
    }

    // Spawn Oziem NPC near campfire if not joined yet
    if (!this.state.party.includes('oziem')) {
      this.addNpc(8, 4, 'oziem');
    }
  }

  private async runWakeUpSequence(): Promise<void> {
    this.isBusy = true;
    setFlag(this.state, 'ch1_woke_up', true);
    Audio.sfx('notification');

    const runner = new DialogueRunner(CH01.wake, this.state.leader);
    await this.dialogueBox.play(runner.allResolved());
    await this.showPhonePopup();

    const hangRunner = new DialogueRunner(CH01.hangover, this.state.leader);
    await this.dialogueBox.play(hangRunner.allResolved());

    // Immediate tutorial combat: Back Pain Ambush!
    setFlag(this.state, 'ch1_fought_spine', true);
    await this.startSpineEncounter();
  }

  private async showPhonePopup(): Promise<void> {
    if (this.isPhoneOpen) return;
    this.isPhoneOpen = true;
    this.isBusy = true;

    // Dark semi-transparent overlay
    const overlay = this.add.rectangle(GAME_W / 2, GAME_H / 2, GAME_W, GAME_H, 0x000000, 0.65)
      .setDepth(920)
      .setScrollFactor(0)
      .setInteractive();

    // Centered smartphone modal container
    const pop = this.add.container(GAME_W / 2, GAME_H / 2)
      .setDepth(930)
      .setScrollFactor(0);

    // Phone frame (400x540)
    const phone = this.add.image(0, 0, 'phone_frame');
    pop.add(phone);

    const leaderId = this.state.leader;
    const isDannyLeader = leaderId === 'danny';

    interface ChatMsg {
      fromId: HeroId;
      name: string;
      color: string;
      text: string;
      time: string;
      isOutgoing: boolean;
    }

    const messages: ChatMsg[] = [
      {
        fromId: isDannyLeader ? 'barti' : 'danny',
        name: isDannyLeader ? 'Barti' : 'Danny',
        color: isDannyLeader ? '#99BBFF' : '#FFAA33',
        text: 'Siema ekipa! Dzisiaj o 20:00 zbiórka w garażu. Nie ma wymówek!',
        time: '08:02',
        isOutgoing: false,
      },
      {
        fromId: 'alior',
        name: 'Alior',
        color: '#00FFFF',
        text: 'Ogarnąłem projektor i UFC 300! Będą grane turnieje!',
        time: '08:05',
        isOutgoing: false,
      },
      {
        fromId: 'lisu',
        name: 'Lisu',
        color: '#FF5555',
        text: 'Kupiłem kiełbasy i browary, wbijam tyłami przez Starówkę!',
        time: '08:09',
        isOutgoing: false,
      },
      {
        fromId: leaderId,
        name: `${leaderId.toUpperCase()} (TY)`,
        color: '#25D366',
        text: 'Dobra, zbieram się z łóżka. Tylko ogarnę kawę w Żabce i lecę do garażu.',
        time: '08:14 ✓✓',
        isOutgoing: true,
      },
    ];

    const startY = -120;
    const rowStep = 74;

    messages.forEach((m, idx) => {
      const my = startY + idx * rowStep;
      if (!m.isOutgoing) {
        // Incoming bubble: Left side
        const avatar = this.add.image(-158, my, `avatar_${m.fromId}`).setDisplaySize(32, 32);
        pop.add(avatar);

        const bubble = this.add.image(-10, my, 'chat_bubble_in');
        pop.add(bubble);

        const nameText = this.add.text(-138, my - 22, m.name, {
          fontFamily: 'Helvetica Neue, Arial, sans-serif',
          fontSize: '11px',
          fontStyle: 'bold',
          color: m.color,
        });
        pop.add(nameText);

        const bodyText = this.add.text(-138, my - 8, m.text, {
          fontFamily: 'Helvetica Neue, Arial, sans-serif',
          fontSize: '10px',
          color: '#E9EDEF',
          wordWrap: { width: 205 },
        });
        pop.add(bodyText);

        const timeText = this.add.text(105, my + 13, m.time, {
          fontFamily: 'Helvetica Neue, Arial, sans-serif',
          fontSize: '9px',
          color: '#8696A0',
        }).setOrigin(1, 0.5);
        pop.add(timeText);
      } else {
        // Outgoing bubble: Right side
        const bubble = this.add.image(10, my, 'chat_bubble_out');
        pop.add(bubble);

        const avatar = this.add.image(158, my, `avatar_${m.fromId}`).setDisplaySize(32, 32);
        pop.add(avatar);

        const nameText = this.add.text(-118, my - 22, m.name, {
          fontFamily: 'Helvetica Neue, Arial, sans-serif',
          fontSize: '11px',
          fontStyle: 'bold',
          color: m.color,
        });
        pop.add(nameText);

        const bodyText = this.add.text(-118, my - 8, m.text, {
          fontFamily: 'Helvetica Neue, Arial, sans-serif',
          fontSize: '10px',
          color: '#E9EDEF',
          wordWrap: { width: 205 },
        });
        pop.add(bodyText);

        const timeText = this.add.text(98, my + 13, m.time, {
          fontFamily: 'Helvetica Neue, Arial, sans-serif',
          fontSize: '9px',
          color: '#8696A0',
        }).setOrigin(1, 0.5);
        pop.add(timeText);
      }
    });

    // Action button "[Z] DALEJ ▶"
    const btnZone = this.add.zone(127, 228, 110, 36).setInteractive({ useHandCursor: true });
    pop.add(btnZone);

    // Initial entrance animation
    pop.setScale(0.85);
    pop.setAlpha(0);
    this.tweens.add({
      targets: pop,
      scale: 1,
      alpha: 1,
      duration: 200,
      ease: 'Back.easeOut',
    });

    Audio.sfx('notification');

    await new Promise<void>((resolve) => {
      let dismissed = false;

      const dismiss = () => {
        if (dismissed) return;
        dismissed = true;
        Audio.sfx('confirm');

        this.tweens.add({
          targets: [pop, overlay],
          scale: 0.85,
          alpha: 0,
          duration: 180,
          ease: 'Quad.easeIn',
          onComplete: () => {
            pop.destroy();
            overlay.destroy();
            this.isPhoneOpen = false;
            this.isBusy = false;
            resolve();
          },
        });
      };

      btnZone.on('pointerdown', dismiss);
      overlay.on('pointerdown', dismiss);

      const checkInput = () => {
        if (dismissed) return;
        if (this.inputHandler.okOrTap() || this.inputHandler.pressed('cancel') || this.inputHandler.pressed('menu')) {
          dismiss();
        } else {
          this.time.delayedCall(50, checkInput);
        }
      };
      this.time.delayedCall(200, checkInput);
    });
  }

  private setupExitBeacon(mapName: string): void {
    if (this.exitBeaconSprite) {
      this.exitBeaconSprite.destroy();
      this.exitBeaconSprite = null;
    }

    const exitDef = MAP_EXITS[mapName];
    if (!exitDef) return;

    const px = exitDef.x * TILE + TILE / 2;
    const py = exitDef.y * TILE + TILE / 2;
    const unlocked = exitDef.isUnlocked(this.state);

    this.exitBeaconSprite = this.add.sprite(px, py, 'exit_beacon', 0);
    this.exitBeaconSprite.setOrigin(0.5, 0.75);
    this.exitBeaconSprite.setDepth(25);
    this.exitBeaconSprite.play(unlocked ? 'anim_exit_beacon' : 'anim_exit_locked');

    this.tweens.add({
      targets: this.exitBeaconSprite,
      y: py - 4,
      duration: 800,
      yoyo: true,
      repeat: -1,
      ease: 'Sine.easeInOut',
    });
  }

  private updateExitBeacon(): void {
    const exitDef = MAP_EXITS[this.currentMap];
    if (!exitDef || !this.exitBeaconSprite) return;

    const unlocked = exitDef.isUnlocked(this.state);
    const targetKey = unlocked ? 'anim_exit_beacon' : 'anim_exit_locked';
    if (this.exitBeaconSprite.anims.currentAnim?.key !== targetKey) {
      this.exitBeaconSprite.play(targetKey);
      if (unlocked) {
        Audio.sfx('crit');
        this.cameras.main.flash(150, 0, 255, 200);
      }
    }
  }

  private showToast(msg: string, force = false): void {
    const now = this.time.now;
    if (!force && now < this.toastCooldown) return;
    this.toastCooldown = now + 1500;

    if (this.toastContainer) {
      this.toastContainer.destroy();
      this.toastContainer = null;
    }

    Audio.sfx('hit');

    const tc = this.add.container(GAME_W / 2, 42).setDepth(960).setScrollFactor(0);
    const tg = this.add.graphics();
    const padW = Math.max(360, msg.length * 9 + 40);
    drawPanel(tg, -padW / 2, -16, padW, 32, { fill: PAL.void, border: PAL.red, glow: true });
    tc.add(tg);

    const t = txt(this, 0, 0, msg, { color: PAL.yellow, origin: [0.5, 0.5] });
    tc.add(t);

    tc.setAlpha(0);
    this.tweens.add({
      targets: tc,
      alpha: 1,
      duration: 150,
      yoyo: true,
      hold: 1800,
      ease: 'Quad.easeInOut',
      onComplete: () => {
        tc.destroy();
        if (this.toastContainer === tc) this.toastContainer = null;
      },
    });
    this.toastContainer = tc;
  }

  private checkExitTriggers(): void {
    if (this.isBusy || this.dialogueBox.active) return;
    const exitDef = MAP_EXITS[this.currentMap];
    if (!exitDef) return;

    const px = this.playerSprite.x / TILE;
    const py = this.playerSprite.y / TILE;
    const exitCenterX = exitDef.x + 0.5;
    const exitCenterY = exitDef.y + 0.5;

    let dist = Phaser.Math.Distance.Between(px, py, exitCenterX, exitCenterY);
    if (this.currentMap === 'city') {
      const dist17 = Phaser.Math.Distance.Between(px, py, 17.5, 5.5);
      if (dist17 < dist) dist = dist17;
    } else if (this.currentMap === 'garage') {
      const dist17 = Phaser.Math.Distance.Between(px, py, 17.5, 6.5);
      if (dist17 < dist) dist = dist17;
    } else if (this.currentMap === 'pub') {
      const dist17 = Phaser.Math.Distance.Between(px, py, 17.5, 6.5);
      if (dist17 < dist) dist = dist17;
    } else if (this.currentMap === 'alley') {
      const dist16 = Phaser.Math.Distance.Between(px, py, 16.5, 5.5);
      const dist17 = Phaser.Math.Distance.Between(px, py, 17.5, 5.5);
      const dist176 = Phaser.Math.Distance.Between(px, py, 17.5, 6.5);
      const dist38 = Phaser.Math.Distance.Between(px, py, 38.5, 5.5);
      dist = Math.min(dist, dist16, dist17, dist176, dist38);
    } else if (this.currentMap === 'marina') {
      const distBoat = Phaser.Math.Distance.Between(px, py, 15.5, 5.0);
      const distBoat4 = Phaser.Math.Distance.Between(px, py, 14.5, 4.5);
      dist = Math.min(dist, distBoat, distBoat4);
    } else if (this.currentMap === 'forest') {
      const distFire = Phaser.Math.Distance.Between(px, py, 9.5, 5.5);
      dist = Math.min(dist, distFire);
    }
    if (dist > 1.6) return;

    const actionPressed = this.inputHandler.okOrTap();

    // Trigger condition: within 1.25 tiles, or action key pressed near exit
    if (dist <= 1.25 || actionPressed) {
      const unlocked = exitDef.isUnlocked(this.state);
      if (!unlocked) {
        this.showToast(exitDef.lockedReason, actionPressed);
      } else {
        if (this.currentMap === 'marina') {
          this.triggerBoatCrossing();
        } else if (this.currentMap === 'forest') {
          this.triggerForestCamp();
        } else {
          this.transitionToMap(exitDef.targetMap, exitDef.targetX, exitDef.targetY);
        }
      }
    }
  }

  override update(_time: number, delta: number): void {
    if (this.qteContainer) {
      this.updateQte(delta);
      return;
    }

    if (this.dialogueBox.active) {
      this.dialogueBox.update(this.inputHandler, delta);
      this.interactPrompt?.hide();
      return;
    }

    if (this.isBusy) {
      this.interactPrompt?.hide();
      return;
    }

    // Check menu / phone shortcut (M / TAB)
    if (!this.isPhoneOpen && this.inputHandler.pressed('menu')) {
      this.showPhonePopup();
      return;
    }

    // Movement
    const axis = this.inputHandler.axis();
    if (axis.x !== 0 || axis.y !== 0) {
      const speedMult = walkSpeedMultiplier(this.state);
      const speed = 70 * speedMult * (delta / 1000);

      const targetX = this.playerSprite.x + axis.x * speed;
      const targetY = this.playerSprite.y + axis.y * speed;

      const tileX = Math.floor(targetX / TILE);
      const tileY = Math.floor(targetY / TILE);

      const dir = axis.x > 0 ? 'right' : axis.x < 0 ? 'left' : axis.y > 0 ? 'down' : 'up';
      this.state.facing = dir;

      if (this.isWalkable(tileX, tileY)) {
        this.playerSprite.x = targetX;
        this.playerSprite.y = targetY;
        this.playerSprite.setDepth(this.playerSprite.y + 12);
        this.state.x = tileX;
        this.state.y = tileY;

        // Record breadcrumb trail for followers with distance threshold
        const lastPt = this.trail[this.trail.length - 1];
        if (!lastPt || Phaser.Math.Distance.Between(targetX, targetY, lastPt.x, lastPt.y) >= 4) {
          this.trail.push({ x: targetX, y: targetY, dir });
          if (this.trail.length > 250) this.trail.shift();
        }

        this.updateFollowers();
      }

      this.playerSprite.play(`anim_${this.state.leader}_walk_${dir}`, true);

      this.checkTriggers(tileX, tileY);
      this.checkExitTriggers();
    } else {
      if (this.playerSprite && this.playerSprite.active && this.playerSprite.anims) {
        this.playerSprite.stop();
      }
      this.followerSprites.forEach((spr) => {
        if (spr && spr.active && spr.anims) {
          spr.stop();
          spr.setDepth(spr.y + 12);
        }
      });
      this.checkExitTriggers();
    }

    // Contextual interaction prompt check (both during movement and when standing)
    this.updateInteraction();
  }

  private getInteractablesForCurrentMap(): Interactable[] {
    const map = this.currentMap;
    const items: Interactable[] = [];

    if (map === 'apartment') {
      // Desk / Laptop (at desk tile 3,2 or chair tile 3,3)
      if (!hasFlag(this.state, 'ch1_fought_slack')) {
        items.push({
          id: 'apt_desk',
          x: 3,
          y: 2,
          label: 'SPRAWDŹ SLACKA',
          isAlert: true,
          action: () => this.startSlackEncounter(),
        });
        items.push({
          id: 'apt_desk_chair',
          x: 3,
          y: 3,
          label: 'SPRAWDŹ SLACKA',
          isAlert: true,
          action: () => this.startSlackEncounter(),
        });
      } else {
        items.push({
          id: 'apt_desk',
          x: 3,
          y: 2,
          label: 'ZBADAJ BIURKO',
          action: async () => {
            this.isBusy = true;
            const r = new DialogueRunner(CH01.examine.desk, this.state.leader);
            await this.dialogueBox.play(r.allResolved());
            this.isBusy = false;
          },
        });
        items.push({
          id: 'apt_desk_chair',
          x: 3,
          y: 3,
          label: 'ZBADAJ BIURKO',
          action: async () => {
            this.isBusy = true;
            const r = new DialogueRunner(CH01.examine.desk, this.state.leader);
            await this.dialogueBox.play(r.allResolved());
            this.isBusy = false;
          },
        });
      }

      // Bed
      items.push({
        id: 'apt_bed',
        x: 6,
        y: 5,
        label: 'ZBADAJ ŁÓŻKO',
        action: async () => {
          this.isBusy = true;
          const r = new DialogueRunner(CH01.examine.bed, this.state.leader);
          await this.dialogueBox.play(r.allResolved());
          this.isBusy = false;
        },
      });

      // Exit Door
      const unlocked = hasFlag(this.state, 'ch1_fought_spine') && hasFlag(this.state, 'ch1_fought_slack');
      items.push({
        id: 'apt_door',
        x: 10,
        y: 11,
        label: unlocked ? 'WYJDŹ NA MIASTO' : 'WYJŚCIE (ZABLOKOWANE)',
        isAlert: !unlocked,
        action: async () => {
          if (!unlocked) {
            this.isBusy = true;
            const r = new DialogueRunner(CH01.examine.doorLocked, this.state.leader);
            await this.dialogueBox.play(r.allResolved());
            this.isBusy = false;
          } else {
            this.transitionToMap('city', 5, 4);
          }
        },
      });

      // Kitchenette fridge & coffee machine, and Pegasus CRT TV
      items.push({
        id: 'apt_fridge',
        x: 16,
        y: 2,
        label: 'ZBADAJ LODÓWKĘ',
        action: async () => {
          this.isBusy = true;
          const r = new DialogueRunner(CH01.examine.fridge, this.state.leader);
          await this.dialogueBox.play(r.allResolved());
          this.isBusy = false;
        },
      });
      items.push({
        id: 'apt_coffee',
        x: 22,
        y: 2,
        label: 'EKSPRES DO KAWY',
        action: async () => {
          this.isBusy = true;
          const r = new DialogueRunner(CH01.examine.coffeeMachine, this.state.leader);
          await this.dialogueBox.play(r.allResolved());
          this.isBusy = false;
        },
      });
      items.push({
        id: 'apt_tv',
        x: 27,
        y: 10,
        label: 'PEGASUS / TV',
        action: async () => {
          this.isBusy = true;
          const r = new DialogueRunner(CH01.examine.tv, this.state.leader);
          await this.dialogueBox.play(r.allResolved());
          this.isBusy = false;
        },
      });
    } else if (map === 'city') {
      // Żabka Door
      items.push({
        id: 'city_zabka_door',
        x: 5,
        y: 3,
        label: 'WEJDŹ DO ŻABKI',
        action: () => this.transitionToMap('zabka', 5, 5, 'up'),
      });

      // Sąsiadka
      items.push({
        id: 'city_old_lady',
        x: 8,
        y: 4,
        label: 'SĄSIADKA',
        action: async () => {
          this.isBusy = true;
          const r = new DialogueRunner(CH01.city.oldLady, this.state.leader);
          await this.dialogueBox.play(r.allResolved());
          this.isBusy = false;
        },
      });

      // Gołąb
      items.push({
        id: 'city_pigeon',
        x: 12,
        y: 5,
        label: 'GOŁĄB',
        action: async () => {
          this.isBusy = true;
          const r = new DialogueRunner(CH01.city.pigeon, this.state.leader);
          await this.dialogueBox.play(r.allResolved());
          this.isBusy = false;
        },
      });

      // Biegacz
      items.push({
        id: 'city_jogger',
        x: 14,
        y: 4,
        label: 'BIEGACZ',
        action: async () => {
          this.isBusy = true;
          const r = new DialogueRunner(CH01.city.jogger, this.state.leader);
          await this.dialogueBox.play(r.allResolved());
          this.isBusy = false;
        },
      });

      // Latarnia
      items.push({
        id: 'city_lamp',
        x: 10,
        y: 4,
        label: 'LATARNIA',
        action: async () => {
          this.isBusy = true;
          const r = new DialogueRunner(CH01.city.lamp, this.state.leader);
          await this.dialogueBox.play(r.allResolved());
          this.isBusy = false;
        },
      });

      // Garage exit (at 38, 5 and fallback at 17, 5)
      const hasCoffee = hasFlag(this.state, 'bought_coffee');
      items.push({
        id: 'city_garage_door',
        x: 38,
        y: 5,
        label: hasCoffee ? 'WEJDŹ DO GARAŻU' : 'GARAŻ (ZABLOKOWANE)',
        isAlert: !hasCoffee,
        action: async () => {
          if (!hasCoffee) {
            this.isBusy = true;
            const r = new DialogueRunner(CH01.city.blocked, this.state.leader);
            await this.dialogueBox.play(r.allResolved());
            this.isBusy = false;
          } else {
            this.transitionToMap('garage', 2, 5);
          }
        },
      });
      items.push({
        id: 'city_garage_door_17',
        x: 17,
        y: 5,
        label: hasCoffee ? 'WEJDŹ DO GARAŻU' : 'GARAŻ (ZABLOKOWANE)',
        isAlert: !hasCoffee,
        action: async () => {
          if (!hasCoffee) {
            this.isBusy = true;
            const r = new DialogueRunner(CH01.city.blocked, this.state.leader);
            await this.dialogueBox.play(r.allResolved());
            this.isBusy = false;
          } else {
            this.transitionToMap('garage', 2, 5);
          }
        },
      });
    } else if (map === 'zabka') {
      // Kasjer
      const hasCoffee = hasFlag(this.state, 'bought_coffee');
      items.push({
        id: 'zabka_cashier',
        x: 5,
        y: 2,
        label: hasCoffee ? 'KASJER' : 'KUP KAWĘ I HOT DOGA',
        isAlert: !hasCoffee,
        action: async () => {
          if (!hasCoffee) {
            await this.buyCoffee();
          } else {
            this.isBusy = true;
            const r = new DialogueRunner(CH01.zabka.cashierAgain, this.state.leader);
            await this.dialogueBox.play(r.allResolved());
            this.isBusy = false;
          }
        },
      });

      // Hot dogs
      items.push({
        id: 'zabka_hotdogs',
        x: 4,
        y: 2,
        label: 'ROLLER GRILL',
        action: async () => {
          this.isBusy = true;
          const r = new DialogueRunner(CH01.zabka.hotdogs, this.state.leader);
          await this.dialogueBox.play(r.allResolved());
          this.isBusy = false;
        },
      });

      // Beverage fridges
      items.push({
        id: 'zabka_fridges',
        x: 8,
        y: 0,
        label: 'CHŁODZIARKI',
        action: async () => {
          this.isBusy = true;
          const r = new DialogueRunner(CH01.zabka.fridges, this.state.leader);
          await this.dialogueBox.play(r.allResolved());
          this.isBusy = false;
        },
      });
      items.push({
        id: 'zabka_fridges_1',
        x: 8,
        y: 1,
        label: 'CHŁODZIARKI',
        action: async () => {
          this.isBusy = true;
          const r = new DialogueRunner(CH01.zabka.fridges, this.state.leader);
          await this.dialogueBox.play(r.allResolved());
          this.isBusy = false;
        },
      });

      // Snack shelves
      items.push({
        id: 'zabka_shelves',
        x: 2,
        y: 0,
        label: 'PRZEKĄSKI',
        action: async () => {
          this.isBusy = true;
          const r = new DialogueRunner(CH01.zabka.shelves, this.state.leader);
          await this.dialogueBox.play(r.allResolved());
          this.isBusy = false;
        },
      });
      items.push({
        id: 'zabka_shelves_1',
        x: 2,
        y: 1,
        label: 'PRZEKĄSKI',
        action: async () => {
          this.isBusy = true;
          const r = new DialogueRunner(CH01.zabka.shelves, this.state.leader);
          await this.dialogueBox.play(r.allResolved());
          this.isBusy = false;
        },
      });

      // Exit doormat (5, 7) and (5, 16)
      items.push({
        id: 'zabka_exit',
        x: 5,
        y: 7,
        label: 'WYJDŹ NA ULICĘ',
        action: () => this.transitionToMap('city', 5, 4, 'down'),
      });
      items.push({
        id: 'zabka_exit_16',
        x: 5,
        y: 16,
        label: 'WYJDŹ NA ULICĘ',
        action: () => this.transitionToMap('city', 5, 4, 'down'),
      });
    } else if (map === 'garage') {
      if (!this.state.party.includes('danny') || !this.state.party.includes('alior')) {
        items.push({
          id: 'garage_crew',
          x: 5,
          y: 4,
          label: 'ROZMAWIAJ Z DANNYM',
          action: () => this.triggerGarageEncounter(),
        });
      }
      items.push({
        id: 'garage_projector',
        x: 8,
        y: 2,
        label: 'PROJEKTOR UFC',
        action: async () => {
          this.isBusy = true;
          await this.dialogueBox.play([{ name: 'SYSTEM', text: 'Projektor rzuca na ścianę galę UFC 300. Holloway nokautuje Gaethje w ostatniej sekundzie!' }]);
          this.isBusy = false;
        },
      });
      items.push({
        id: 'garage_beer',
        x: 14,
        y: 2,
        label: 'LODÓWKA Z BROWARAMI',
        action: async () => {
          this.isBusy = true;
          await this.dialogueBox.play([{ name: 'SYSTEM', text: 'Lodówka turystyczna Danny\'ego. Po brzegi zasypana lodem i zimnymi kraftami.' }]);
          this.isBusy = false;
        },
      });
    } else if (map === 'pub') {
      if (!this.state.party.includes('barti')) {
        items.push({
          id: 'pub_barti',
          x: 10,
          y: 2,
          label: 'ROZMAWIAJ Z BARTIM',
          action: () => this.triggerPubEncounter(),
        });
      }
      items.push({
        id: 'pub_vinyls',
        x: 14,
        y: 2,
        label: 'PŁYTY WINYLOWE',
        action: async () => {
          this.isBusy = true;
          await this.dialogueBox.play([{ name: 'SYSTEM', text: 'Stojak z winylami: Kaliber 44, Paktofonika, O.S.T.R. Czysty analogowy sound.' }]);
          this.isBusy = false;
        },
      });
    } else if (map === 'alley') {
      if (!this.state.party.includes('lisu')) {
        items.push({
          id: 'alley_lisu',
          x: 10,
          y: 3,
          label: 'ROZMAWIAJ Z LISEM',
          action: () => this.triggerAlleyEncounter(),
        });
      }
      items.push({
        id: 'alley_dumpster',
        x: 10,
        y: 4,
        label: 'KONTENER',
        action: async () => {
          this.isBusy = true;
          await this.dialogueBox.play([{ name: 'SYSTEM', text: 'Metalowy kontener na śmieci. Pachnie wczorajszą pizzą i tajemnicą.' }]);
          this.isBusy = false;
        },
      });
      items.push({
        id: 'alley_lamp_5',
        x: 5,
        y: 3,
        label: 'LATARNIA',
        action: async () => {
          this.isBusy = true;
          await this.dialogueBox.play([{ name: 'SYSTEM', text: 'Zabytkowa latarnia z żeliwną podstawą. Rzuca ciepłe, sodowe światło na mokry bruk.' }]);
          this.isBusy = false;
        },
      });
      items.push({
        id: 'alley_lamp_13',
        x: 13,
        y: 3,
        label: 'LATARNIA',
        action: async () => {
          this.isBusy = true;
          await this.dialogueBox.play([{ name: 'SYSTEM', text: 'Zabytkowa latarnia z żeliwną podstawą. Rzuca ciepłe, sodowe światło na mokry bruk.' }]);
          this.isBusy = false;
        },
      });
      items.push({
        id: 'alley_crates',
        x: 3,
        y: 4,
        label: 'SKRZYNIE',
        action: async () => {
          this.isBusy = true;
          await this.dialogueBox.play([{ name: 'SYSTEM', text: 'Drewniane skrzynie transportowe i palety Euro. Pachną żywicą i wilgocią.' }]);
          this.isBusy = false;
        },
      });
    } else if (map === 'marina') {
      if (!this.state.party.includes('luki')) {
        items.push({
          id: 'marina_luki',
          x: 10,
          y: 4,
          label: 'RATUJ ŁUKIEGO!',
          isAlert: true,
          action: () => this.triggerMarinaRescue(),
        });
      }
      items.push({
        id: 'marina_boat',
        x: 15,
        y: 5,
        label: 'MOTORÓWKA',
        action: () => this.checkExitTriggers(),
      });
      items.push({
        id: 'marina_lifebuoy',
        x: 6,
        y: 3,
        label: 'KOŁO RATUNKOWE',
        action: async () => {
          this.isBusy = true;
          await this.dialogueBox.play([{ name: 'SYSTEM', text: 'Czerwono-białe koło ratunkowe z liną asekuracyjną. W razie wpadnięcia do wody – bezcenne.' }]);
          this.isBusy = false;
        },
      });
      items.push({
        id: 'marina_lantern',
        x: 11,
        y: 3,
        label: 'LATARNIA SZTORMOWA',
        action: async () => {
          this.isBusy = true;
          await this.dialogueBox.play([{ name: 'SYSTEM', text: 'Mosiężna latarnia sztormowa. Jej ciepłe światło odbija się w tafli jeziora.' }]);
          this.isBusy = false;
        },
      });
    } else if (map === 'forest') {
      if (!this.state.party.includes('oziem')) {
        items.push({
          id: 'forest_oziem',
          x: 8,
          y: 4,
          label: 'ROZMAWIAJ Z OZIEMEM',
          action: () => this.triggerForestCamp(),
        });
      }
      items.push({
        id: 'forest_fire',
        x: 9,
        y: 5,
        label: 'OGNISKO',
        action: () => this.triggerForestCamp(),
      });
      items.push({
        id: 'forest_hammock_5',
        x: 5,
        y: 3,
        label: 'HAMAK',
        action: async () => {
          this.isBusy = true;
          await this.dialogueBox.play([{ name: 'SYSTEM', text: 'Wyprawowy hamak z pomarańczowego ripstop nylonu. Idealny na leśny biwak.' }]);
          this.isBusy = false;
        },
      });
      items.push({
        id: 'forest_hammock_13',
        x: 13,
        y: 3,
        label: 'HAMAK',
        action: async () => {
          this.isBusy = true;
          await this.dialogueBox.play([{ name: 'SYSTEM', text: 'Wyprawowy hamak z zielonego ripstop nylonu, rozwieszony między drzewami.' }]);
          this.isBusy = false;
        },
      });
    }

    return items;
  }

  private getNearbyInteractable(): Interactable | null {
    const list = this.getInteractablesForCurrentMap();
    const px = this.state.x;
    const py = this.state.y;
    const facing = this.state.facing ?? 'down';

    const frontX = px + (facing === 'left' ? -1 : facing === 'right' ? 1 : 0);
    const frontY = py + (facing === 'up' ? -1 : facing === 'down' ? 1 : 0);

    // 1. Direct tile in front
    for (const item of list) {
      if (item.isAvailable && !item.isAvailable()) continue;
      if (item.x === frontX && item.y === frontY) {
        return item;
      }
    }

    // 2. Same tile (e.g. door mat)
    for (const item of list) {
      if (item.isAvailable && !item.isAvailable()) continue;
      if (item.x === px && item.y === py) {
        return item;
      }
    }

    // 3. Proximity <= 1.4 tiles
    let closest: Interactable | null = null;
    let closestDist = 1.4;
    for (const item of list) {
      if (item.isAvailable && !item.isAvailable()) continue;
      const dist = Phaser.Math.Distance.Between(px, py, item.x, item.y);
      if (dist <= closestDist) {
        closestDist = dist;
        closest = item;
      }
    }

    return closest;
  }

  private updateInteraction(): void {
    if (this.isBusy || this.dialogueBox.active || this.isPhoneOpen || this.qteContainer) {
      this.interactPrompt.hide();
      return;
    }

    const item = this.getNearbyInteractable();
    if (item) {
      const wx = item.x * TILE + TILE / 2;
      const wy = item.y * TILE + TILE / 2;
      this.interactPrompt.show(item.id, wx, wy, item.label, item.isAlert);

      if (this.inputHandler.okOrTap()) {
        Audio.sfx('cursor');
        item.action();
      }
    } else {
      this.interactPrompt.hide();
    }
  }

  private updateFollowers(): void {
    const followers = this.state.party.slice(1);
    const stepSpacing = 7; // ~28px distance per follower for natural 32px trail
    followers.forEach((hid, idx) => {
      const spr = this.followerSprites.get(hid);
      if (!spr || !spr.active || !spr.anims) return;
      const targetIndex = this.trail.length - 1 - (idx + 1) * stepSpacing;
      if (targetIndex >= 0) {
        const pt = this.trail[targetIndex];
        spr.setPosition(pt.x, pt.y);
        spr.setDepth(spr.y + 12);
        spr.play(`anim_${hid}_walk_${pt.dir}`, true);
      }
    });
  }

  private isWalkable(x: number, y: number): boolean {
    if (x < 0 || x >= this.mapW || y < 0 || y >= this.mapH) return false;
    return !this.solids[y]?.[x];
  }

  private checkTriggers(x: number, y: number): void {
    if (this.currentMap === 'city') {
      if (x === 5 && y === 3) {
        this.transitionToMap('zabka', 5, 5, 'up');
        return;
      }
    } else if (this.currentMap === 'zabka') {
      if (x === 5 && (y === 7 || y === 16 || y === 17)) {
        this.transitionToMap('city', 5, 4, 'down');
        return;
      }
    } else if (this.currentMap === 'garage') {
      // Meet Danny & Alior in garage
      if ((x === 5 || x === 6) && (y === 4 || y === 5) && !hasFlag(this.state, 'garage_wrestled')) {
        this.triggerGarageEncounter();
        return;
      }
    } else if (this.currentMap === 'pub') {
      // Approach Barti at DJ desk
      if ((x === 9 || x === 10) && (y === 4 || y === 5) && !hasFlag(this.state, 'pub_cleared')) {
        this.triggerPubEncounter();
        return;
      }
    } else if (this.currentMap === 'alley') {
      // Approach Lisu near dumpster (x: 10, y: 4)
      if ((x === 9 || x === 10) && (y === 4 || y === 5) && !hasFlag(this.state, 'lisu_found')) {
        this.triggerAlleyEncounter();
        return;
      }
    } else if (this.currentMap === 'marina') {
      // Approach Łuki at pier edge (x: 10, y: 4)
      if ((x === 9 || x === 10) && (y === 3 || y === 4 || y === 5) && !hasFlag(this.state, 'luki_rescued')) {
        this.triggerMarinaRescue();
        return;
      }
    } else if (this.currentMap === 'forest') {
      // Approach Oziem at bivouac (x: 8, y: 4)
      if ((x === 7 || x === 8) && (y === 4 || y === 5) && !hasFlag(this.state, 'oziem_joined')) {
        this.triggerForestCamp();
        return;
      }
    }
  }

  private async startSpineEncounter(): Promise<void> {
    this.isBusy = true;
    const runner = new DialogueRunner(CH01.backPainAmbush, this.state.leader);
    await this.dialogueBox.play(runner.allResolved());

    this.cameras.main.flash(300, 255, 255, 255);
    Audio.sfx('encounter');
    this.time.delayedCall(400, () => {
      startBattle(this, 'spineAmbush', { state: this.state });
    });
  }

  private async startSlackEncounter(): Promise<void> {
    this.isBusy = true;
    setFlag(this.state, 'ch1_fought_slack', true);
    const runner = new DialogueRunner(CH01.laptop, this.state.leader);
    await this.dialogueBox.play(runner.allResolved());

    const sRunner = new DialogueRunner(CH01.slackFight, this.state.leader);
    await this.dialogueBox.play(sRunner.allResolved());

    this.cameras.main.flash(300, 255, 255, 255);
    Audio.sfx('encounter');
    this.time.delayedCall(400, () => {
      startBattle(this, 'slackInvasion', { state: this.state });
    });
  }

  private async buyCoffee(): Promise<void> {
    this.isBusy = true;
    removeWorldStatus(this.state, 'kacGigant');
    setFlag(this.state, 'bought_coffee', true);

    // Provisions from Żabka
    this.state.inventory.kawa = (this.state.inventory.kawa ?? 0) + 2;
    this.state.inventory.hotDog = (this.state.inventory.hotDog ?? 0) + 1;
    this.state.inventory.elektrolity = (this.state.inventory.elektrolity ?? 0) + 1;

    // Full restore
    for (const member of Object.values(this.state.roster)) {
      member.hp = 999;
      member.mp = 999;
    }

    Audio.sfx('crit');
    this.updateHud();
    this.updateExitBeacon();

    const runner = new DialogueRunner(CH01.zabka.cashierWelcome, this.state.leader);
    await this.dialogueBox.play(runner.allResolved());
    this.isBusy = false;
  }

  // Chapter 2: Garage & Wrestling QTE
  private async triggerGarageEncounter(): Promise<void> {
    this.isBusy = true;
    this.state.chapter = 2;
    this.updateHud();

    const runner = new DialogueRunner(CH02.enter, this.state.leader);
    await this.dialogueBox.play(runner.allResolved());

    const wRunner = new DialogueRunner(CH02.wrestlingPrompt, this.state.leader);
    await this.dialogueBox.play(wRunner.allResolved());

    // Launch Wrestling QTE Bar
    this.startQte('POWAL DANNY\'EGO! [Z / ENTER]', (_isSuccess) => {
      setFlag(this.state, 'garage_wrestled', true);
      this.afterWrestling();
    });
  }

  private startQte(title: string, onComplete: (success: boolean) => void): void {
    this.qteContainer = this.add.container(GAME_W / 2, GAME_H / 2).setDepth(850).setScrollFactor(0);
    const qg = this.add.graphics();
    drawPanel(qg, -240, -60, 480, 120, { fill: PAL.navy, border: PAL.steel, glow: true });
    // Bar frame track
    qg.fillStyle(PAL.ink, 1);
    qg.fillRect(-180, 6, 360, 24);
    // Green sweet spot (-36..36)
    qg.fillStyle(PAL.green, 1);
    qg.fillRect(-36, 6, 72, 24);
    // Center bullseye (-14..14)
    qg.fillStyle(PAL.fireHi, 1);
    qg.fillRect(-14, 6, 28, 24);

    this.qteContainer.add(qg);
    this.qteContainer.add(txt(this, 0, -36, title, { color: PAL.yellow, origin: [0.5, 0.5] }));
    this.qteContainer.add(txt(this, 0, -18, '[ WYCZUJ MOMENT I WCIŚNIJ SPACJĘ / ENTER / Z ]', { color: PAL.cyan, origin: [0.5, 0.5] }));

    this.qteMarkerX = -170;
    this.qteMarkerSpeed = 260;
    this.qteCallback = onComplete;
  }

  private updateQte(delta: number): void {
    if (!this.qteContainer) return;

    this.qteMarkerX += this.qteMarkerSpeed * (delta / 1000);
    if (this.qteMarkerX > 170) {
      this.qteMarkerX = 170;
      this.qteMarkerSpeed = -Math.abs(this.qteMarkerSpeed);
    } else if (this.qteMarkerX < -170) {
      this.qteMarkerX = -170;
      this.qteMarkerSpeed = Math.abs(this.qteMarkerSpeed);
    }

    // Redraw marker
    const g = this.qteContainer.getAt(0) as Phaser.GameObjects.Graphics;
    g.clear();
    drawPanel(g, -240, -60, 480, 120, { fill: PAL.navy, border: PAL.steel, glow: true });
    g.fillStyle(PAL.ink, 1);
    g.fillRect(-180, 6, 360, 24);
    g.fillStyle(PAL.green, 1);
    g.fillRect(-36, 6, 72, 24);
    g.fillStyle(PAL.fireHi, 1);
    g.fillRect(-14, 6, 28, 24);

    // Marker line
    g.fillStyle(PAL.white, 1);
    g.fillRect(this.qteMarkerX - 3, 2, 6, 32);

    if (this.inputHandler.okOrTap()) {
      const isSuccess = Math.abs(this.qteMarkerX) <= 36;
      this.qteContainer.destroy();
      this.qteContainer = null;

      if (isSuccess) {
        Audio.sfx('crit');
      } else {
        Audio.sfx('hit');
      }
      const cb = this.qteCallback;
      this.qteCallback = null;
      cb?.(isSuccess);
    }
  }

  private async afterWrestling(): Promise<void> {
    const wWin = new DialogueRunner(CH02.wrestlingWin, this.state.leader);
    await this.dialogueBox.play(wWin.allResolved());

    // Neighbour bangs on the door!
    Audio.sfx('hit');
    this.cameras.main.shake(200, 0.015);
    const nInter = new DialogueRunner(CH02.neighbourInterruption, this.state.leader);
    await this.dialogueBox.play(nInter.allResolved());

    // Boss fight against Sąsiad Szkodnik!
    setFlag(this.state, 'fought_sasiad', true);
    this.cameras.main.flash(300, 255, 255, 255);
    Audio.sfx('encounter');
    this.time.delayedCall(400, () => {
      startBattle(this, 'sasiadBoss', { state: this.state });
    });
  }

  private async afterSasiadBoss(): Promise<void> {
    this.isBusy = true;
    setFlag(this.state, 'danny_alior_joined', true);
    this.removeNpcSprite('danny');
    this.removeNpcSprite('alior');
    addToParty(this.state, 'danny');
    addToParty(this.state, 'alior');
    this.syncFollowerSprites();
    this.updateHud();
    this.updateExitBeacon();

    const runner = new DialogueRunner(CH02.afterBoss, this.state.leader);
    await this.dialogueBox.play(runner.allResolved());
    this.isBusy = false;
  }

  // Chapter 3: Pub "Czarny Krążek"
  private async triggerPubEncounter(): Promise<void> {
    this.isBusy = true;
    this.state.chapter = 3;
    setFlag(this.state, 'pub_cleared', true);
    this.updateHud();

    const pEnter = new DialogueRunner(CH03.enter, this.state.leader);
    await this.dialogueBox.play(pEnter.allResolved());

    const pFight = new DialogueRunner(CH03.beforeFight, this.state.leader);
    await this.dialogueBox.play(pFight.allResolved());

    // Battle against Auto-Tune Hipster & Drogie Piwo!
    setFlag(this.state, 'fought_hipsters', true);
    this.cameras.main.flash(300, 255, 255, 255);
    Audio.sfx('encounter');
    this.time.delayedCall(400, () => {
      startBattle(this, 'pubHipsters', { state: this.state });
    });
  }

  private async afterPubBattle(): Promise<void> {
    this.isBusy = true;
    setFlag(this.state, 'barti_joined', true);
    this.removeNpcSprite('barti');
    addToParty(this.state, 'barti');
    this.syncFollowerSprites();
    this.updateHud();
    this.updateExitBeacon();

    const runner = new DialogueRunner(CH03.afterFight, this.state.leader);
    await this.dialogueBox.play(runner.allResolved());
    this.isBusy = false;
  }

  // Chapter 4: Alley & Lisu
  private async triggerAlleyEncounter(): Promise<void> {
    this.isBusy = true;
    this.state.chapter = 4;
    setFlag(this.state, 'lisu_found', true);
    this.updateHud();

    const pEnter = new DialogueRunner(CH04.enter, this.state.leader, this.state.party);
    await this.dialogueBox.play(pEnter.allResolved());

    const pLisu = new DialogueRunner(CH04.findLisu, this.state.leader, this.state.party);
    await this.dialogueBox.play(pLisu.allResolved());

    const pKark = new DialogueRunner(CH04.karkAmbush, this.state.leader, this.state.party);
    await this.dialogueBox.play(pKark.allResolved());

    // Boss battle against Szef Ochrony "Kark" and Strażnik Miejski!
    setFlag(this.state, 'fought_kark', true);
    this.cameras.main.flash(300, 255, 255, 255);
    Audio.sfx('encounter');
    this.time.delayedCall(400, () => {
      startBattle(this, 'karkAmbush', { state: this.state });
    });
  }

  private async afterKarkBattle(): Promise<void> {
    this.isBusy = true;
    setFlag(this.state, 'lisu_joined', true);
    this.removeNpcSprite('lisu');
    addToParty(this.state, 'lisu');
    this.syncFollowerSprites();
    this.updateHud();
    this.updateExitBeacon();

    const runner = new DialogueRunner(CH04.afterKark, this.state.leader, this.state.party);
    await this.dialogueBox.play(runner.allResolved());
    this.isBusy = false;
  }

  // Chapter 5: Marina & Water Rescue
  private async triggerMarinaRescue(): Promise<void> {
    this.isBusy = true;
    this.state.chapter = 5;
    setFlag(this.state, 'luki_rescued', true);
    this.updateHud();

    const mEnter = new DialogueRunner(CH05.enter, this.state.leader, this.state.party);
    await this.dialogueBox.play(mEnter.allResolved());

    const mPrompt = new DialogueRunner(CH05.rescuePrompt, this.state.leader, this.state.party);
    await this.dialogueBox.play(mPrompt.allResolved());

    // Launch rescue QTE
    this.startQte('RZUĆ KOŁO ŁUKIEMU! [Z / ENTER]', async (_success) => {
      setFlag(this.state, 'luki_joined', true);
      this.removeNpcSprite('luki');
      addToParty(this.state, 'luki');
      this.syncFollowerSprites();
      this.updateHud();
      this.updateExitBeacon();

      const mSuccess = new DialogueRunner(CH05.rescueSuccess, this.state.leader, this.state.party);
      await this.dialogueBox.play(mSuccess.allResolved());
      this.isBusy = false;
    });
  }

  private async triggerBoatCrossing(): Promise<void> {
    this.isBusy = true;
    Audio.sfx('confirm');
    await this.dialogueBox.play([
      { name: 'ŁUKI', text: 'Wszyscy na pokład! Odpalam silnik!', portrait: 'portrait_luki_64', color: PAL.cyan },
      { name: 'SYSTEM', text: 'Motorówka płynie przez ciemne, ciche wody jeziora ku leśnej przystani...', color: PAL.cyanHi },
    ]);

    this.transitionToMap('forest', 3, 5);
  }

  // Chapter 6: Deep Wildwood Forest Camp
  private async triggerForestCamp(): Promise<void> {
    this.isBusy = true;
    this.state.chapter = 6;
    setFlag(this.state, 'oziem_joined', true);
    this.removeNpcSprite('oziem');
    addToParty(this.state, 'oziem');
    this.syncFollowerSprites();
    this.updateHud();

    const fEnter = new DialogueRunner(CH06.enter, this.state.leader, this.state.party);
    await this.dialogueBox.play(fEnter.allResolved());

    // All 6 heroes assembled! Transition smoothly into Campfire scene (Chapter 7)!
    this.cameras.main.fadeOut(800, 0, 3, 11);
    this.cameras.main.once(Phaser.Cameras.Scene2D.Events.FADE_OUT_COMPLETE, () => {
      this.scene.start('Campfire', { state: this.state });
    });
  }

  private transitionToMap(mapName: string, targetX: number, targetY: number, facing: 'down' | 'up' | 'left' | 'right' = 'down'): void {
    this.isBusy = true;
    this.cameras.main.fadeOut(250, 0, 3, 11);
    this.cameras.main.once(Phaser.Cameras.Scene2D.Events.FADE_OUT_COMPLETE, () => {
      this.currentMap = mapName;
      this.state.mapId = mapName;
      this.buildMap(mapName);
      this.updateAtmosphere();
      this.playerSprite.setPosition(targetX * TILE + TILE / 2, targetY * TILE + TILE / 2);
      this.playerSprite.setDepth(this.playerSprite.y + 12);
      this.state.x = targetX;
      this.state.y = targetY;
      this.state.facing = facing;
      if (this.playerSprite && this.playerSprite.active && this.playerSprite.anims) {
        this.playerSprite.play(`anim_${this.state.leader}_walk_${facing}`);
        this.playerSprite.stop();
      }
      this.trail = [];
      for (let i = 0; i < 40; i++) {
        this.trail.push({ x: this.playerSprite.x, y: this.playerSprite.y, dir: facing });
      }
      this.syncFollowerSprites();
      this.followerSprites.forEach((spr, hid) => {
        if (spr && spr.active && spr.anims) {
          spr.setPosition(this.playerSprite.x, this.playerSprite.y);
          spr.setDepth(spr.y + 12);
          spr.play(`anim_${hid}_walk_${facing}`);
          spr.stop();
        }
      });
      this.updateHud();
      this.cameras.main.fadeIn(250, 0, 3, 11);
      this.isBusy = false;
    });
  }
}
