import Phaser from 'phaser';
import { GAME_W, GAME_H, PAL } from '@/config';
import { GameData, grantXp, applyBattleResult, partyEffects } from '@/systems/GameState';
import { HEROES } from '@/content/heroes';
import { BattleEngine, makeEnemyCombatant, makeHeroCombatant, BattleEvent } from '@/systems/BattleEngine';
import { ENEMIES } from '@/content/enemies';
import { SKILLS } from '@/content/skills';
import { ITEMS } from '@/content/items';
import { drawPanel, gauge } from '@/ui/Panel';
import { txt } from '@/ui/Text';
import { Menu } from '@/ui/Menu';
import { Input } from '@/ui/Input';
import { Audio } from '@/audio/ChipAudio';
import { damageNumber, screenShake } from '@/fx/Juice';
import { applyCrtToCamera } from '@/fx/CrtPipeline';

export class BattleScene extends Phaser.Scene {
  private state!: GameData;
  private engine!: BattleEngine;
  private inputHandler!: Input;

  private heroSprites: Map<string, Phaser.GameObjects.Sprite> = new Map();
  private enemySprites: Map<string, Phaser.GameObjects.Sprite> = new Map();

  private uiContainer!: Phaser.GameObjects.Container;
  private logText!: Phaser.GameObjects.BitmapText | Phaser.GameObjects.Text;
  private commandMenu: Menu | null = null;
  private subMenu: Menu | null = null;

  private returnScene = 'World';
  private bgKey = 'battle_apartment_bg';
  private isResolving = false;
  private gaugesGraphics!: Phaser.GameObjects.Graphics;

  constructor() {
    super('Battle');
  }

  init(data: { state: GameData; enemies: string[]; bg?: string; returnScene?: string }): void {
    this.state = data.state;
    this.bgKey = data.bg ?? 'battle_apartment_bg';
    this.returnScene = data.returnScene ?? 'World';
  }

  create(): void {
    applyCrtToCamera(this);
    Audio.playSong('ch01_battle', { fadeMs: 300 });

    // Background
    this.add.image(GAME_W / 2, GAME_H / 2, this.bgKey).setDisplaySize(GAME_W, GAME_H);

    // Build Combatants using GameState
    const heroCombatants = this.state.party.map((hid) => {
      const def = HEROES[hid];
      const member = this.state.roster[hid];
      return makeHeroCombatant(def, member.level, member.hp, member.mp);
    });

    const enemyCombatants = [makeEnemyCombatant(ENEMIES.bolKregoslupa, 0)];

    const enemyDefsList = Object.values(ENEMIES);
    this.engine = new BattleEngine(heroCombatants, enemyCombatants, enemyDefsList, {
      partyEffects: partyEffects(this.state),
    });

    this.gaugesGraphics = this.add.graphics().setDepth(200);
    this.uiContainer = this.add.container(0, 0).setDepth(800).setScrollFactor(0);

    // Bottom Combat Log Panel
    const lg = this.add.graphics();
    drawPanel(lg, 16, GAME_H - 68, GAME_W - 32, 56, { fill: PAL.navy, border: PAL.steel });
    this.uiContainer.add(lg);
    this.logText = txt(this, 28, GAME_H - 52, 'WALKA ROZPOCZĘTA!', { color: PAL.cyanHi });
    this.uiContainer.add(this.logText);

    // Spawn Heroes on Right (facing left)
    this.heroCombatantsVisuals();

    // Spawn Enemies on Left (facing right)
    this.enemyCombatantsVisuals();

    this.inputHandler = new Input(this);
  }

  private heroCombatantsVisuals(): void {
    this.engine.heroes.forEach((h, i) => {
      const hx = GAME_W - 160 - (i % 2) * 80;
      const hy = 180 + i * 85;
      const spr = this.add.sprite(hx, hy, `${h.defId}_battle`, 0).setDepth(150);
      spr.setOrigin(0.5, 0.5);
      this.heroSprites.set(h.uid, spr);
    });
  }

  private enemyCombatantsVisuals(): void {
    this.engine.enemies.forEach((e, i) => {
      const ex = 180 + (i % 2) * 90;
      const ey = 190 + i * 85;
      const spr = this.add.sprite(ex, ey, e.sprite ?? 'enemy_bolKregoslupa', 0).setDepth(150);
      spr.setOrigin(0.5, 0.5);
      if (this.anims.exists(`anim_${e.sprite}`)) {
        spr.play(`anim_${e.sprite}`);
      }
      this.enemySprites.set(e.uid, spr);
    });
  }

  override update(_time: number, delta: number): void {
    this.renderGauges();

    if (this.commandMenu) {
      this.handleCommandMenu();
      return;
    }

    if (this.subMenu) {
      this.handleSubMenu();
      return;
    }

    if (this.isResolving) return;

    // Run ATB tick
    const events = this.engine.tick(delta);
    if (events.length > 0) {
      this.processBattleEvents(events);
    }
  }

  private renderGauges(): void {
    this.gaugesGraphics.clear();

    // Render Hero Gauges (HP, MP, ATB)
    this.engine.heroes.forEach((h, _i) => {
      const spr = this.heroSprites.get(h.uid);
      if (!spr) return;
      const gx = spr.x - 36;
      const gy = spr.y - 52;

      // Name & HP
      gauge(this.gaugesGraphics, gx, gy, 72, 6, h.hp / h.max.hp, PAL.green);
      gauge(this.gaugesGraphics, gx, gy + 8, 72, 5, h.mp / h.max.mp, PAL.cyan);
      gauge(this.gaugesGraphics, gx, gy + 15, 72, 4, h.atb / 100, PAL.yellow);
    });

    // Render Enemy Gauges
    this.engine.enemies.forEach((e) => {
      const spr = this.enemySprites.get(e.uid);
      if (!spr || !e.alive) return;
      const gx = spr.x - 45;
      const gy = spr.y - 65;
      gauge(this.gaugesGraphics, gx, gy, 90, 6, e.hp / e.max.hp, PAL.red);
    });
  }

  private processBattleEvents(events: BattleEvent[]): void {
    for (const ev of events) {
      if (ev.type === 'ready') {
        Audio.sfx('confirm');
        this.openHeroCommandMenu(ev.uid);
        break;
      } else if (ev.type === 'log') {
        (this.logText as any).setText(ev.text);
      } else if (ev.type === 'damage') {
        const targetSpr = this.heroSprites.get(ev.uid) ?? this.enemySprites.get(ev.uid);
        if (targetSpr) {
          damageNumber(this, targetSpr.x, targetSpr.y, `${ev.amount}`, ev.crit ? PAL.yellow : PAL.white, ev.crit);
          screenShake(this, ev.crit ? 0.02 : 0.01, 150);
        }
      } else if (ev.type === 'heal') {
        const targetSpr = this.heroSprites.get(ev.uid);
        if (targetSpr) {
          damageNumber(this, targetSpr.x, targetSpr.y, `+${ev.amount}`, PAL.green);
        }
      } else if (ev.type === 'miss') {
        const targetSpr = this.heroSprites.get(ev.uid) ?? this.enemySprites.get(ev.uid);
        if (targetSpr) {
          damageNumber(this, targetSpr.x, targetSpr.y, 'MISS', PAL.silver);
        }
      } else if (ev.type === 'skill') {
        // Play FX animation on target
        if (ev.fx && this.textures.exists(`fx_${ev.fx}`)) {
          const firstTarget = ev.targets[0];
          const tspr = this.heroSprites.get(firstTarget) ?? this.enemySprites.get(firstTarget);
          if (tspr) {
            const fxSpr = this.add.sprite(tspr.x, tspr.y, `fx_${ev.fx}`).setDepth(300);
            fxSpr.play(`anim_fx_${ev.fx}`);
            fxSpr.once(Phaser.Animations.Events.ANIMATION_COMPLETE, () => fxSpr.destroy());
          }
        }
        // Play corresponding signature sound effect
        if (ev.skillId in Audio) {
          (Audio as any)[ev.skillId]?.();
        } else {
          Audio.sfx('hit');
        }
      } else if (ev.type === 'ko') {
        const spr = this.enemySprites.get(ev.uid);
        if (spr) {
          this.tweens.add({ targets: spr, alpha: 0, duration: 400 });
        }
      } else if (ev.type === 'victory') {
        this.handleVictory(ev.xp);
      } else if (ev.type === 'defeat') {
        this.handleDefeat();
      }
    }
  }

  private openHeroCommandMenu(heroUid: string): void {
    const hero = this.engine.getCombatant(heroUid);
    if (!hero) return;

    const items = [
      { label: 'ATAK' },
      { label: 'UMIEJĘTNOŚĆ' },
      { label: 'PRZEDMIOT' },
      { label: 'OBRONA' },
    ];

    this.commandMenu = new Menu(this, 24, GAME_H - 220, 160, items, 950);
  }

  private handleCommandMenu(): void {
    if (!this.commandMenu) return;
    const hero = this.engine.waitingHero;
    if (!hero) return;

    const pick = this.commandMenu.update(this.inputHandler);
    if (pick === 0) {
      // Basic Attack
      this.commandMenu.destroy();
      this.commandMenu = null;
      const foe = this.engine.enemies.find((e) => e.alive);
      if (foe) {
        const evs = this.engine.act(hero.uid, 'attack', foe.uid);
        this.processBattleEvents(evs);
      }
    } else if (pick === 1) {
      // Skills submenu
      this.commandMenu.setVisible(false);
      const skillItems = hero.skills.map((sid) => {
        const sdef = SKILLS[sid];
        return { label: `${sdef.name} (${sdef.mpCost}MP)`, hint: sdef.description };
      });
      this.subMenu = new Menu(this, 195, GAME_H - 220, 240, skillItems, 960);
    } else if (pick === 2) {
      // Items submenu
      this.commandMenu.setVisible(false);
      const itemKeys = Object.keys(this.state.inventory);
      const menuItems = itemKeys.map((k) => ({ label: `${ITEMS[k]?.name ?? k} x${this.state.inventory[k]}` }));
      this.subMenu = new Menu(this, 195, GAME_H - 220, 220, menuItems, 960);
    } else if (pick === 3) {
      // Defend
      this.commandMenu.destroy();
      this.commandMenu = null;
      const evs = this.engine.defend(hero.uid);
      this.processBattleEvents(evs);
    }
  }

  private handleSubMenu(): void {
    if (!this.subMenu) return;
    const hero = this.engine.waitingHero;
    if (!hero) return;

    const pick = this.subMenu.update(this.inputHandler);
    if (pick === -2) {
      // Cancelled -> return to main command menu
      this.subMenu.destroy();
      this.subMenu = null;
      this.commandMenu?.setVisible(true);
    } else if (pick >= 0) {
      const skillId = hero.skills[pick];
      this.subMenu.destroy();
      this.subMenu = null;
      this.commandMenu?.destroy();
      this.commandMenu = null;

      const foe = this.engine.enemies.find((e) => e.alive);
      const evs = this.engine.act(hero.uid, skillId, foe?.uid);
      this.processBattleEvents(evs);
    }
  }

  private handleVictory(xp: number): void {
    this.isResolving = true;
    Audio.playSong('victory', { loop: false });

    // Grant XP and apply battle result to GameState
    const levelUps = grantXp(this.state, xp);
    applyBattleResult(this.state, this.engine);

    let msg = `ZWYCIĘSTWO! +${xp} XP.`;
    if (levelUps.length > 0) {
      msg += ` Awans: ${levelUps.map((l) => `${l.heroId} -> Lvl ${l.newLevel}`).join(', ')}!`;
    }
    (this.logText as any).setText(msg);

    this.time.delayedCall(2000, () => {
      this.cameras.main.fadeOut(400, 0, 3, 11);
      this.cameras.main.once(Phaser.Cameras.Scene2D.Events.FADE_OUT_COMPLETE, () => {
        this.scene.start(this.returnScene, {
          state: this.state,
          returnFromBattle: true,
          battleResult: 'victory',
        });
      });
    });
  }

  private handleDefeat(): void {
    this.isResolving = true;
    Audio.sfx('ko');
    (this.logText as any).setText('PORAŻKA... Ekipa wraca do łóżka.');

    this.time.delayedCall(2000, () => {
      this.cameras.main.fadeOut(400, 0, 3, 11);
      this.cameras.main.once(Phaser.Cameras.Scene2D.Events.FADE_OUT_COMPLETE, () => {
        this.scene.start('Title');
      });
    });
  }
}
