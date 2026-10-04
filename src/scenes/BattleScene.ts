import Phaser from 'phaser';
import { GAME_W, GAME_H, PAL } from '@/config';
import type { BattleParams, HeroId } from '@/types';
import { GameData, grantXp, applyBattleResult } from '@/systems/GameState';
import { BattleEngine, BattleEvent } from '@/systems/BattleEngine';
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
import { applyStatus } from '@/systems/StatusFx';
import { Combatant } from '@/systems/Combatant';
import { resolveBattleConfig, ResolvedBattleConfig, getEnemySpriteSize } from '@/systems/EncounterFactory';

export class BattleScene extends Phaser.Scene {
  private config!: ResolvedBattleConfig;
  private state!: GameData;
  private engine!: BattleEngine;
  private inputHandler!: Input;

  private heroSprites: Map<string, Phaser.GameObjects.Sprite> = new Map();
  private enemySprites: Map<string, Phaser.GameObjects.Sprite> = new Map();

  private uiContainer!: Phaser.GameObjects.Container;
  private logText!: Phaser.GameObjects.BitmapText | Phaser.GameObjects.Text;
  private commandMenu: Menu | null = null;
  private subMenu: Menu | null = null;
  private subMenuMode: 'skill' | 'item' = 'skill';

  private returnScene = 'World';
  private bgKey = 'battle_apartment_bg';
  private isResolving = false;
  private isActionPlaying = false;
  private actionTimerMs = 0;
  private gaugesGraphics!: Phaser.GameObjects.Graphics;
  private statusText!: Phaser.GameObjects.BitmapText | Phaser.GameObjects.Text;

  private actionBannerContainer!: Phaser.GameObjects.Container;
  private actionBannerBg!: Phaser.GameObjects.Graphics;
  private actionBannerText!: Phaser.GameObjects.BitmapText | Phaser.GameObjects.Text;

  constructor() {
    super('Battle');
  }

  init(data: BattleParams): void {
    this.isResolving = false;
    this.isActionPlaying = false;
    this.actionTimerMs = 0;
    this.commandMenu = null;
    this.subMenu = null;
    this.heroSprites.clear();
    this.enemySprites.clear();

    this.config = resolveBattleConfig(data);
    this.state = this.config.state;
    this.bgKey = this.config.bg;
    this.returnScene = this.config.returnScene;
  }

  create(): void {
    this.isResolving = false;
    this.isActionPlaying = false;
    this.actionTimerMs = 0;
    this.commandMenu = null;
    this.subMenu = null;
    this.heroSprites.clear();
    this.enemySprites.clear();

    applyCrtToCamera(this);
    Audio.playSong(this.config.music as any, { fadeMs: 300 });

    // Background
    this.add.image(GAME_W / 2, GAME_H / 2, this.bgKey).setDisplaySize(GAME_W, GAME_H);

    // Initialize BattleEngine with resolved combatants and status effects
    const enemyDefsList = Object.values(ENEMIES);
    this.engine = new BattleEngine(this.config.heroes, this.config.enemies, enemyDefsList, {
      partyEffects: this.config.partyEffects,
    });

    // Apply any initial enemy status effects
    if (this.config.enemyEffects && this.config.enemyEffects.length > 0) {
      for (const e of this.engine.enemies) {
        for (const eff of this.config.enemyEffects) {
          applyStatus(e, eff);
        }
      }
    }

    this.gaugesGraphics = this.add.graphics().setDepth(200);
    this.uiContainer = this.add.container(0, 0).setDepth(800).setScrollFactor(0);

    // Bottom Combat Log Panel (1024x576 wide)
    const lg = this.add.graphics();
    drawPanel(lg, 12, GAME_H - 74, GAME_W - 24, 62, { fill: PAL.navy, border: PAL.steel, glow: true });
    this.uiContainer.add(lg);

    // Status Header Badge
    const badgeBg = this.add.graphics();
    badgeBg.fillStyle(PAL.panel, 0.9);
    badgeBg.fillRoundedRect(22, GAME_H - 68, 140, 18, 3);
    this.uiContainer.add(badgeBg);
    this.uiContainer.add(txt(this, 28, GAME_H - 66, '★ RAPORT BOJOWY [v1.2]', { color: PAL.yellow }));

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

    // Action Keys Legend HUD (frame 1 = battle)
    const legendImg = this.add.image(GAME_W / 2, 16, 'keys_legend', 1)
      .setDepth(850)
      .setScrollFactor(0);
    this.uiContainer.add(legendImg);

    // Floating Action Banner (top center)
    this.actionBannerContainer = this.add.container(GAME_W / 2, 60).setDepth(960).setScrollFactor(0);
    this.actionBannerBg = this.add.graphics();
    this.actionBannerText = txt(this, 0, 0, '', { color: PAL.yellow, big: true });
    this.actionBannerText.setOrigin(0.5, 0.5);
    this.actionBannerContainer.add([this.actionBannerBg, this.actionBannerText]);
    this.actionBannerContainer.setAlpha(0);

    // Display title banner if battle title was specified
    if (this.config.battleTitle) {
      this.showTitleBanner(this.config.battleTitle);
    }

    // Immediately trigger turn start for any ready hero so the action menu is open on frame 1
    const initialEvents = this.engine.tick(0);
    if (initialEvents.length > 0) {
      this.processBattleEvents(initialEvents);
    }
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

      const sz = this.getEnemySpriteSize(e);
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

  private getEnemySpriteSize(combatant: Combatant): number {
    return getEnemySpriteSize(combatant);
  }

  override update(_time: number, delta: number): void {
    // Tick down action timer with delta so action locks can NEVER hang permanently
    const dt = typeof delta === 'number' && !isNaN(delta) && delta > 0 ? delta : 16.6;
    if (this.actionTimerMs > 0) {
      this.actionTimerMs -= dt;
      if (this.actionTimerMs <= 0 || isNaN(this.actionTimerMs)) {
        this.actionTimerMs = 0;
        this.isActionPlaying = false;
        if (!this.commandMenu && !this.subMenu && !this.isResolving) {
          (this.statusText as any).setText('STATUS: ŁADOWANIE ATB...');
        }
      }
    } else if (this.isActionPlaying) {
      this.isActionPlaying = false;
    }

    this.renderGauges();

    if (this.subMenu) {
      if (!this.engine.waitingHero) {
        this.subMenu.destroy();
        this.subMenu = null;
      } else {
        this.handleSubMenu();
        return;
      }
    }

    if (this.commandMenu) {
      // Defensive safeguard: if menu exists without a waiting hero, destroy orphan menu
      if (!this.engine.waitingHero) {
        this.commandMenu.destroy();
        this.commandMenu = null;
      } else {
        this.handleCommandMenu();
        return;
      }
    }

    if (this.isResolving || this.isActionPlaying) return;

    // Safety fallback: if engine has a waiting hero but no menu is open, open it!
    if (this.engine.waitingHero && !this.commandMenu && !this.subMenu) {
      this.openHeroCommandMenu(this.engine.waitingHero.uid);
      return;
    }

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
      const sz = this.getEnemySpriteSize(e);
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
        const targetSpr = this.heroSprites.get(ev.uid) ?? this.enemySprites.get(ev.uid);
        if (targetSpr) {
          damageNumber(this, targetSpr.x, targetSpr.y, `+${ev.amount}`, PAL.green);
        }
      } else if (ev.type === 'mp') {
        const targetSpr = this.heroSprites.get(ev.uid);
        if (targetSpr && ev.delta !== 0) {
          damageNumber(this, targetSpr.x, targetSpr.y - 14, `${ev.delta > 0 ? '+' : ''}${ev.delta} MP`, PAL.cyan);
        }
      } else if (ev.type === 'revive') {
        const hspr = this.heroSprites.get(ev.uid);
        const hero = this.engine.heroes.find((h) => h.uid === ev.uid);
        if (hspr && hero) {
          hspr.setAlpha(1);
          if (this.anims.exists(`anim_${hero.defId}_battle_idle`)) {
            hspr.play(`anim_${hero.defId}_battle_idle`);
          }
          damageNumber(this, hspr.x, hspr.y, 'POWRÓT!', PAL.cyanHi);
        }
      } else if (ev.type === 'item') {
        Audio.sfx('confirm');
      } else if (ev.type === 'miss') {
        const targetSpr = this.heroSprites.get(ev.uid) ?? this.enemySprites.get(ev.uid);
        if (targetSpr) {
          damageNumber(this, targetSpr.x, targetSpr.y, 'MISS', PAL.silver);
        }
      } else if (ev.type === 'skill') {
        const actorHero = this.engine.heroes.find((h) => h.uid === ev.actorUid);
        const actorEnemy = this.engine.enemies.find((e) => e.uid === ev.actorUid);
        const skill = SKILLS[ev.skillId];
        const actorName = actorHero ? actorHero.name : (actorEnemy ? actorEnemy.name : 'Nieznany');
        const skillName = skill ? skill.name : ev.skillId;
        const isEnemy = !actorHero;

        this.showActionBanner(actorName, skillName, isEnemy);
        (this.statusText as any).setText(`AKCJA: ${skillName.toUpperCase()}`);

        this.isActionPlaying = true;
        this.actionTimerMs = 450;
        this.time.delayedCall(450, () => {
          this.isActionPlaying = false;
          this.actionTimerMs = 0;
          if (!this.commandMenu && !this.subMenu && !this.isResolving) {
            (this.statusText as any).setText('STATUS: ŁADOWANIE ATB...');
          }
        });

        // Trigger actor hero battle animation
        const actorHeroSpr = this.heroSprites.get(ev.actorUid);
        if (actorHero && actorHeroSpr) {
          const isAttack = ev.skillId === 'attack';
          const animKey = isAttack ? `anim_${actorHero.defId}_battle_attack` : `anim_${actorHero.defId}_battle_skill`;
          if (this.anims.exists(animKey)) {
            const origX = actorHeroSpr.x;
            this.tweens.add({
              targets: actorHeroSpr,
              x: origX - 25,
              duration: 100,
              yoyo: true,
              onYoyo: () => {
                actorHeroSpr.play(animKey);
              },
              onComplete: () => {
                actorHeroSpr.x = origX;
                if (actorHero.alive && this.anims.exists(`anim_${actorHero.defId}_battle_idle`)) {
                  actorHeroSpr.play(`anim_${actorHero.defId}_battle_idle`);
                }
              },
            });
          }
        }

        // Trigger actor enemy battle animation (lunge & punchy squash/stretch)
        const actorEnemySpr = this.enemySprites.get(ev.actorUid);
        if (actorEnemy && actorEnemySpr) {
          const origX = actorEnemySpr.x;
          const origScaleX = actorEnemySpr.scaleX;
          const origScaleY = actorEnemySpr.scaleY;
          this.tweens.add({
            targets: actorEnemySpr,
            x: origX + 32,
            scaleX: origScaleX * 1.18,
            scaleY: origScaleY * 0.88,
            duration: 120,
            yoyo: true,
            ease: 'Quad.easeOut',
            onComplete: () => {
              actorEnemySpr.x = origX;
              actorEnemySpr.setScale(origScaleX, origScaleY);
            },
          });
        }

        // Play FX animation on target(s)
        if (ev.fx && this.textures.exists(`fx_${ev.fx}`)) {
          for (const tid of ev.targets) {
            const tspr = this.heroSprites.get(tid) ?? this.enemySprites.get(tid);
            if (tspr) {
              const fxSpr = this.add.sprite(tspr.x, tspr.y, `fx_${ev.fx}`).setDepth(300);
              fxSpr.play(`anim_fx_${ev.fx}`);
              fxSpr.once(Phaser.Animations.Events.ANIMATION_COMPLETE, () => fxSpr.destroy());
            }
          }
        }

        // Play corresponding signature sound effect
        if (ev.skillId === 'slackPing') {
          Audio.sfx('notification');
        } else if (ev.skillId === 'stressDebuff') {
          Audio.sfx('debuff');
        } else if (ev.skillId === 'attack' || ev.skillId === 'backPain') {
          Audio.sfx('hit');
        } else {
          try {
            Audio.sfx(ev.skillId as any);
          } catch {
            Audio.sfx('hit');
          }
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
      } else if (ev.type === 'status') {
        const targetSpr = this.heroSprites.get(ev.uid) ?? this.enemySprites.get(ev.uid);
        if (targetSpr && ev.applied) {
          damageNumber(this, targetSpr.x, targetSpr.y - 18, `[${ev.name.toUpperCase()}]`, PAL.yellow);
        }
      } else if (ev.type === 'defeat') {
        (this.statusText as any).setText('STATUS: PORAŻKA');
        this.handleDefeat();
      }
    }
  }

  private openHeroCommandMenu(heroUid: string): void {
    const hero = this.engine.getCombatant(heroUid);
    if (!hero) return;

    // Clean up any existing stale menus to prevent leaks or orphan overlays
    if (this.commandMenu) {
      this.commandMenu.destroy();
      this.commandMenu = null;
    }
    if (this.subMenu) {
      this.subMenu.destroy();
      this.subMenu = null;
    }

    const items = [
      { label: 'ATAK', hint: 'Podstawowy atak fizyczny na wroga.' },
      { label: 'UMIEJĘTNOŚĆ', hint: 'Użyj unikalnej umiejętności bojowej.', disabled: !hero.skills || hero.skills.length === 0 },
      { label: 'PRZEDMIOT', hint: 'Użyj przedmiotu z ekwipunku drużyny.', disabled: Object.keys(this.state.inventory).length === 0 },
      { label: 'OBRONA', hint: 'Przyjmij postawę obronną (-50% obrażeń, redukcja stresu).' },
    ];

    if (this.config.canFlee) {
      items.push({ label: 'UCIECZKA', hint: 'Spróbuj uciec z pola walki.' });
    }

    this.commandMenu = new Menu(this, 24, GAME_H - 220, 160, items, 950, (it) => {
      if (it.hint) (this.logText as any).setText(it.hint);
    });
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
      this.subMenuMode = 'skill';
      const skillItems = hero.skills.map((sid) => {
        const sdef = SKILLS[sid];
        const canAfford = sdef ? hero.mp >= sdef.mpCost : false;
        return {
          label: `${sdef?.name ?? sid} (${sdef?.mpCost ?? 0}MP)`,
          hint: sdef ? `${sdef.description} (Koszt: ${sdef.mpCost} MP)` : undefined,
          disabled: !canAfford,
        };
      });
      this.subMenu = new Menu(this, 195, GAME_H - 220, 260, skillItems, 960, (it) => {
        if (it.hint) (this.logText as any).setText(it.hint);
      });
    } else if (pick === 2) {
      // Items submenu
      this.commandMenu.setVisible(false);
      this.subMenuMode = 'item';
      const itemKeys = Object.keys(this.state.inventory).filter((k) => this.state.inventory[k] > 0);
      if (itemKeys.length === 0) {
        (this.logText as any).setText('Brak przedmiotów w ekwipunku!');
        this.commandMenu.setVisible(true);
        return;
      }
      const menuItems = itemKeys.map((k) => {
        const idef = ITEMS[k];
        return {
          label: `${idef?.name ?? k} x${this.state.inventory[k]}`,
          hint: idef?.description,
        };
      });
      this.subMenu = new Menu(this, 195, GAME_H - 220, 240, menuItems, 960, (it) => {
        if (it.hint) (this.logText as any).setText(it.hint);
      });
    } else if (pick === 3) {
      // Defend
      this.commandMenu.destroy();
      this.commandMenu = null;
      const evs = this.engine.defend(hero.uid);
      this.processBattleEvents(evs);
    } else if (pick === 4 && this.config.canFlee) {
      // Flee
      this.commandMenu.destroy();
      this.commandMenu = null;
      this.handleFlee(hero);
    }
  }

  private handleFlee(hero: Combatant): void {
    const success = Math.random() < this.config.fleeSuccessChance;
    if (success) {
      this.isResolving = true;
      Audio.sfx('confirm');
      (this.logText as any).setText('UCIECZKA UDANA! Ekipa zrywa się z pola walki.');
      this.time.delayedCall(1200, () => {
        this.cameras.main.fadeOut(300, 0, 3, 11);
        this.cameras.main.once(Phaser.Cameras.Scene2D.Events.FADE_OUT_COMPLETE, () => {
          this.scene.start(this.returnScene, {
            state: this.state,
            returnFromBattle: true,
            battleResult: 'fled',
            ...this.config.returnSceneData,
          });
        });
      });
    } else {
      Audio.sfx('cancel');
      (this.logText as any).setText('UCIECZKA NIEUDANA! Przeciwnicy blokują drogę ucieczki.');
      hero.atb = 0;
      this.engine.waitingHero = null;
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
      const curr = this.commandMenu?.selectedItem;
      if (curr?.hint) {
        (this.logText as any).setText(curr.hint);
      } else {
        (this.logText as any).setText(`Tura: ${hero.name}. Wybierz działanie.`);
      }
    } else if (pick >= 0) {
      if (this.subMenuMode === 'skill') {
        const skillId = hero.skills[pick];
        if (!skillId) return;
        this.subMenu.destroy();
        this.subMenu = null;
        this.commandMenu?.destroy();
        this.commandMenu = null;

        const foe = this.engine.enemies.find((e) => e.alive);
        const evs = this.engine.act(hero.uid, skillId, foe?.uid);
        this.processBattleEvents(evs);
      } else if (this.subMenuMode === 'item') {
        const itemKeys = Object.keys(this.state.inventory).filter((k) => this.state.inventory[k] > 0);
        const itemId = itemKeys[pick];
        this.subMenu.destroy();
        this.subMenu = null;
        this.commandMenu?.destroy();
        this.commandMenu = null;

        if (itemId && this.state.inventory[itemId]) {
          this.state.inventory[itemId]--;
          if (this.state.inventory[itemId] <= 0) {
            delete this.state.inventory[itemId];
          }
          const evs = this.engine.useItem(hero.uid, itemId);
          this.processBattleEvents(evs);
        }
      }
    }
  }

  private handleVictory(xp: number): void {
    this.isResolving = true;
    Audio.playSong(this.config.victoryMusic as any, { loop: false });

    // Grant XP and apply battle result to GameState if grantProgression is enabled
    const scaledXp = Math.round(xp * this.config.rewards.xpMultiplier + this.config.rewards.bonusXp);
    let levelUps: any[] = [];
    if (this.config.rewards.grantProgression) {
      levelUps = grantXp(this.state, scaledXp);
      applyBattleResult(this.state, this.engine);
    }

    // Award bonus items if any
    for (const itm of this.config.rewards.bonusItems) {
      this.state.inventory[itm] = (this.state.inventory[itm] ?? 0) + 1;
    }

    let msg = `ZWYCIĘSTWO! +${scaledXp} XP.`;
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
          ...this.config.returnSceneData,
        });
      });
    });
  }

  private showTitleBanner(title: string): void {
    this.showActionBanner('', title, false);
  }

  private showActionBanner(actorName: string, actionName: string, isEnemy = false): void {
    const textStr = actorName.trim().length > 0
      ? `${actorName.toUpperCase()}: ${actionName.toUpperCase()}`
      : actionName.toUpperCase();
    (this.actionBannerText as any).setText(textStr);

    const bannerW = Math.max(260, textStr.length * 11 + 40);
    const bannerH = 32;

    this.actionBannerBg.clear();
    const borderColor = isEnemy ? PAL.fireHi : PAL.cyanHi;
    drawPanel(this.actionBannerBg, -bannerW / 2, -bannerH / 2, bannerW, bannerH, {
      fill: PAL.navy,
      border: borderColor,
      glow: true,
    });

    (this.actionBannerText as any).setColor?.(isEnemy ? '#ff7777' : '#ffff55');

    this.tweens.killTweensOf(this.actionBannerContainer);
    this.actionBannerContainer.setAlpha(0);
    this.actionBannerContainer.setScale(0.9);

    this.tweens.add({
      targets: this.actionBannerContainer,
      alpha: 1,
      scaleX: 1,
      scaleY: 1,
      duration: 100,
      ease: 'Back.easeOut',
      hold: 250,
      yoyo: true,
      onComplete: () => {
        this.actionBannerContainer.setAlpha(0);
      },
    });
  }

  private handleDefeat(): void {
    this.isResolving = true;
    Audio.sfx('ko');

    if (this.config.allowDefeat) {
      // Scripted defeat: restore heroes to at least 1 HP so caller scene can proceed
      for (const h of this.engine.heroes) {
        const hid = h.defId as HeroId;
        const member = this.state.roster[hid];
        if (member) {
          member.hp = 1;
        }
      }
      (this.logText as any).setText('PORAŻKA... Ale to jeszcze nie koniec!');

      this.time.delayedCall(2000, () => {
        this.cameras.main.fadeOut(400, 0, 3, 11);
        this.cameras.main.once(Phaser.Cameras.Scene2D.Events.FADE_OUT_COMPLETE, () => {
          this.scene.start(this.returnScene, {
            state: this.state,
            returnFromBattle: true,
            battleResult: 'defeat',
            ...this.config.returnSceneData,
          });
        });
      });
      return;
    }

    (this.logText as any).setText('PORAŻKA... Ekipa wraca do łóżka.');

    this.time.delayedCall(2000, () => {
      this.cameras.main.fadeOut(400, 0, 3, 11);
      this.cameras.main.once(Phaser.Cameras.Scene2D.Events.FADE_OUT_COMPLETE, () => {
        this.scene.start(this.config.defeatScene, {
          state: this.state,
          returnFromBattle: true,
          battleResult: 'defeat',
          ...this.config.returnSceneData,
        });
      });
    });
  }
}
