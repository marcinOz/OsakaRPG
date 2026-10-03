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
  private enemyIds: string[] = ['bolKregoslupa'];
  private statusText!: Phaser.GameObjects.BitmapText | Phaser.GameObjects.Text;

  constructor() {
    super('Battle');
  }

  init(data: { state: GameData; enemies?: string[]; bg?: string; returnScene?: string }): void {
    this.state = data.state;
    this.bgKey = data.bg ?? 'battle_apartment_bg';
    this.returnScene = data.returnScene ?? 'World';
    this.enemyIds = data.enemies && data.enemies.length > 0 ? data.enemies : ['bolKregoslupa'];
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

    const enemyCombatants = this.enemyIds.map((eid, idx) => {
      const def = (ENEMIES as Record<string, any>)[eid] ?? ENEMIES.bolKregoslupa;
      return makeEnemyCombatant(def, idx);
    });

    const enemyDefsList = Object.values(ENEMIES);
    this.engine = new BattleEngine(heroCombatants, enemyCombatants, enemyDefsList, {
      partyEffects: partyEffects(this.state),
    });

    this.gaugesGraphics = this.add.graphics().setDepth(200);
    this.uiContainer = this.add.container(0, 0).setDepth(800).setScrollFactor(0);

    // Bottom Combat Log Panel (1024x576 wide)
    const lg = this.add.graphics();
    drawPanel(lg, 12, GAME_H - 74, GAME_W - 24, 62, { fill: PAL.navy, border: PAL.steel, glow: true });
    this.uiContainer.add(lg);

    // Status Header Badge
    const badgeBg = this.add.graphics();
    badgeBg.fillStyle(PAL.panel, 0.9);
    badgeBg.fillRoundedRect(22, GAME_H - 68, 120, 18, 3);
    this.uiContainer.add(badgeBg);
    this.uiContainer.add(txt(this, 28, GAME_H - 66, '★ RAPORT BOJOWY', { color: PAL.yellow }));

    // Combat status indicator on the right
    this.statusText = txt(this, GAME_W - 190, GAME_H - 66, 'STATUS: ATB AKTYWNE', { color: PAL.green });
    this.uiContainer.add(this.statusText);

    // Main Log Text with styled typography
    this.logText = txt(this, 28, GAME_H - 42, 'WALKA ROZPOCZĘTA! Wybierz działanie, gdy wskaźnik ATB będzie pełny.', {
      color: PAL.cyanHi,
    });
    this.uiContainer.add(this.logText);

    // Spawn Heroes on Right (facing left)
    this.heroCombatantsVisuals();

    // Spawn Enemies on Left (facing right)
    this.enemyCombatantsVisuals();

    this.inputHandler = new Input(this);
  }

  private heroCombatantsVisuals(): void {
    const totalHeroes = this.engine.heroes.length;
    this.engine.heroes.forEach((h, i) => {
      let hx = 800;
      let hy = 280;
      if (totalHeroes === 1) {
        hx = 800; hy = 285;
      } else if (totalHeroes === 2) {
        hx = i === 0 ? 770 : 840;
        hy = i === 0 ? 220 : 340;
      } else if (totalHeroes === 3) {
        const coords = [
          { x: 765, y: 195 },
          { x: 850, y: 280 },
          { x: 765, y: 365 },
        ];
        hx = coords[i].x; hy = coords[i].y;
      } else if (totalHeroes === 4) {
        const coords = [
          { x: 755, y: 205 },
          { x: 860, y: 215 },
          { x: 755, y: 350 },
          { x: 860, y: 360 },
        ];
        hx = coords[i].x; hy = coords[i].y;
      } else {
        // 5 or 6 heroes
        const col = i % 2; // 0 = front (755), 1 = back (865)
        const row = Math.floor(i / 2); // 0, 1, 2
        hx = col === 0 ? 755 : 865;
        hy = 185 + row * 92 + (col === 1 ? 14 : 0);
      }

      // Grounded shadow beneath hero
      this.add.ellipse(hx, hy + 36, 46, 14, 0x000000, 0.45).setDepth(130);

      // Hero sprite facing left (natural orientation)
      const spr = this.add.sprite(hx, hy, `${h.defId}_battle`, 0).setDepth(150);
      spr.setOrigin(0.5, 0.5);
      if (this.anims.exists(`anim_${h.defId}_battle_idle`)) {
        spr.play(`anim_${h.defId}_battle_idle`);
      }

      // Subtle breathing idle bounce tween
      this.tweens.add({
        targets: spr,
        y: hy - 2,
        duration: 1200 + i * 150,
        yoyo: true,
        repeat: -1,
        ease: 'Sine.easeInOut',
      });

      this.heroSprites.set(h.uid, spr);
    });
  }

  private enemyCombatantsVisuals(): void {
    const totalEnemies = this.engine.enemies.length;
    this.engine.enemies.forEach((e, i) => {
      let ex = 260;
      let ey = 280;
      if (totalEnemies === 1) {
        ex = 260; ey = 285;
      } else if (totalEnemies === 2) {
        ex = i === 0 ? 220 : 300;
        ey = i === 0 ? 215 : 345;
      } else if (totalEnemies === 3) {
        const coords = [
          { x: 200, y: 195 },
          { x: 315, y: 280 },
          { x: 200, y: 365 },
        ];
        ex = coords[i].x; ey = coords[i].y;
      } else {
        // 4 or more enemies
        const coords = [
          { x: 185, y: 200 },
          { x: 330, y: 210 },
          { x: 185, y: 360 },
          { x: 330, y: 370 },
        ];
        ex = coords[i]?.x ?? (200 + (i % 2) * 120);
        ey = coords[i]?.y ?? (190 + Math.floor(i / 2) * 120);
      }

      const sz = this.getEnemySpriteSize(e.sprite);
      // Grounded shadow beneath enemy
      this.add.ellipse(ex, ey + sz * 0.44, sz * 0.65, sz * 0.18, 0x000000, 0.45).setDepth(130);

      const spr = this.add.sprite(ex, ey, e.sprite ?? 'enemy_bolKregoslupa', 0).setDepth(150);
      spr.setOrigin(0.5, 0.5);
      if (this.anims.exists(`anim_${e.sprite}`)) {
        spr.play(`anim_${e.sprite}`);
      }
      this.enemySprites.set(e.uid, spr);
    });
  }

  private getEnemySpriteSize(spriteKey?: string): number {
    if (!spriteKey) return 96;
    if (spriteKey.includes('panJanusz') || spriteKey.includes('kredyt') || spriteKey.includes('audyt')) {
      return 144;
    }
    if (spriteKey.includes('bolKregoslupa') || spriteKey.includes('slacki')) {
      return 96;
    }
    return 128;
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
    this.engine.heroes.forEach((h) => {
      const spr = this.heroSprites.get(h.uid);
      if (!spr) return;
      const gx = spr.x - 38;
      const gy = spr.y - 56;

      // Dark backing container
      this.gaugesGraphics.fillStyle(PAL.navy, 0.85);
      this.gaugesGraphics.fillRoundedRect(gx - 2, gy - 2, 76, 21, 2);

      // HP Bar (green)
      gauge(this.gaugesGraphics, gx, gy, 72, 5, Math.max(0, h.hp / h.max.hp), PAL.green);
      // MP Bar (cyan)
      gauge(this.gaugesGraphics, gx, gy + 7, 72, 4, Math.max(0, h.mp / h.max.mp), PAL.cyan);
      // ATB Bar (yellow/gold)
      gauge(this.gaugesGraphics, gx, gy + 13, 72, 3, Math.min(1, h.atb / 100), PAL.yellow);
    });

    // Render Enemy Gauges
    this.engine.enemies.forEach((e) => {
      const spr = this.enemySprites.get(e.uid);
      if (!spr || !e.alive) return;
      const sz = this.getEnemySpriteSize(e.sprite);
      const gx = spr.x - 45;
      const gy = spr.y - sz / 2 - 16;

      // Dark backing container
      this.gaugesGraphics.fillStyle(PAL.navy, 0.85);
      this.gaugesGraphics.fillRoundedRect(gx - 2, gy - 2, 94, 14, 2);

      // HP Bar (red)
      gauge(this.gaugesGraphics, gx, gy, 90, 6, Math.max(0, e.hp / e.max.hp), PAL.red);
      // ATB Bar (amber)
      gauge(this.gaugesGraphics, gx, gy + 8, 90, 3, Math.min(1, e.atb / 100), PAL.fireHi);
    });
  }

  private processBattleEvents(events: BattleEvent[]): void {
    for (const ev of events) {
      if (ev.type === 'ready') {
        Audio.sfx('confirm');
        const hero = this.engine.getCombatant(ev.uid);
        if (hero) {
          (this.statusText as any).setText(`TURA: ${hero.name.toUpperCase()}`);
        }
        this.openHeroCommandMenu(ev.uid);
        break;
      } else if (ev.type === 'log') {
        (this.logText as any).setText(ev.text);
      } else if (ev.type === 'damage') {
        const targetSpr = this.heroSprites.get(ev.uid) ?? this.enemySprites.get(ev.uid);
        if (targetSpr) {
          damageNumber(this, targetSpr.x, targetSpr.y, `${ev.amount}`, ev.crit ? PAL.yellow : PAL.white, ev.crit);
          screenShake(this, ev.crit ? 0.02 : 0.01, 150);

          // Damage flash and hurt animation
          targetSpr.setTint(0xff5555);
          this.time.delayedCall(160, () => targetSpr.clearTint());

          const hero = this.engine.heroes.find((h) => h.uid === ev.uid);
          if (hero && hero.alive && this.anims.exists(`anim_${hero.defId}_battle_hurt`)) {
            targetSpr.play(`anim_${hero.defId}_battle_hurt`);
            this.time.delayedCall(350, () => {
              if (hero.alive && this.anims.exists(`anim_${hero.defId}_battle_idle`)) {
                targetSpr.play(`anim_${hero.defId}_battle_idle`);
              }
            });
          }
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
        // Trigger actor hero battle animation
        const actorHero = this.engine.heroes.find((h) => h.uid === ev.actorUid);
        const actorSpr = this.heroSprites.get(ev.actorUid);
        if (actorHero && actorSpr) {
          const isAttack = ev.skillId === 'attack';
          const animKey = isAttack ? `anim_${actorHero.defId}_battle_attack` : `anim_${actorHero.defId}_battle_skill`;
          if (this.anims.exists(animKey)) {
            const origX = actorSpr.x;
            this.tweens.add({
              targets: actorSpr,
              x: origX - 25,
              duration: 100,
              yoyo: true,
              onYoyo: () => {
                actorSpr.play(animKey);
              },
              onComplete: () => {
                actorSpr.x = origX;
                if (actorHero.alive && this.anims.exists(`anim_${actorHero.defId}_battle_idle`)) {
                  actorSpr.play(`anim_${actorHero.defId}_battle_idle`);
                }
              },
            });
          }
        }

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
        const espr = this.enemySprites.get(ev.uid);
        if (espr) {
          this.tweens.add({ targets: espr, alpha: 0, scale: 0.8, duration: 450 });
        }
        const hspr = this.heroSprites.get(ev.uid);
        const hero = this.engine.heroes.find((h) => h.uid === ev.uid);
        if (hspr && hero) {
          if (this.anims.exists(`anim_${hero.defId}_battle_ko`)) {
            hspr.play(`anim_${hero.defId}_battle_ko`);
          }
          hspr.setAlpha(0.5);
        }
      } else if (ev.type === 'victory') {
        (this.statusText as any).setText('STATUS: ZWYCIĘSTWO!');
        // All alive heroes play victory animation
        this.engine.heroes.forEach((h) => {
          if (h.alive) {
            const spr = this.heroSprites.get(h.uid);
            if (spr && this.anims.exists(`anim_${h.defId}_battle_victory`)) {
              spr.play(`anim_${h.defId}_battle_victory`);
              this.tweens.add({
                targets: spr,
                y: spr.y - 12,
                duration: 250,
                yoyo: true,
                repeat: 2,
              });
            }
          }
        });
        this.handleVictory(ev.xp);
      } else if (ev.type === 'defeat') {
        (this.statusText as any).setText('STATUS: PORAŻKA');
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
