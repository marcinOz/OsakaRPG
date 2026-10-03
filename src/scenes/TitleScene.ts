import Phaser from 'phaser';
import { GAME_W, GAME_H, PAL } from '@/config';
import { txt } from '@/ui/Text';
import { Input } from '@/ui/Input';
import { Menu } from '@/ui/Menu';
import { Audio } from '@/audio/ChipAudio';
import { addWeather } from '@/fx/Weather';
import { isCrtEnabled, setCrtEnabled, applyCrtToCamera } from '@/fx/CrtPipeline';
import { Saves } from '@/systems/Save';

export class TitleScene extends Phaser.Scene {
  private inputHandler!: Input;
  private menu!: Menu;

  constructor() {
    super('Title');
  }

  create(): void {
    applyCrtToCamera(this);
    Audio.unlock();
    Audio.playSong('title', { fadeMs: 600 });

    // Background
    this.add.image(GAME_W / 2, GAME_H / 2, 'title_bg').setDisplaySize(GAME_W, GAME_H);

    // Weather particles: wandering fireflies
    addWeather(this, 'fireflies');

    // Retro monitor top bar
    const bar = this.add.graphics();
    bar.fillStyle(PAL.panel, 0.95);
    bar.fillRect(0, 0, GAME_W, 20);
    bar.fillStyle(PAL.steel, 1);
    bar.fillRect(0, 19, GAME_W, 1);
    txt(this, 12, 4, 'THE PACK: RETRO ENGINE v2.0 [HD PIXEL-PERFECT EDITION]', { color: PAL.cyan, big: false });
    // Window control buttons ▢ ▢ ✕
    txt(this, GAME_W - 48, 4, '― ▢ ✕', { color: PAL.silver });

    // Main Logo
    txt(this, GAME_W / 2, 120, 'THE PACK', {
      color: PAL.yellow,
      big: true,
      align: 'center',
      origin: [0.5, 0.5],
    });

    txt(this, GAME_W / 2, 155, 'LEGEND OF THE FOREST FIREPLACE', {
      color: PAL.cyanHi,
      big: true,
      align: 'center',
      origin: [0.5, 0.5],
    });

    txt(this, GAME_W / 2, 185, 'Ekipa 36+ • Kronika Przyjaźni i Ognia', {
      color: PAL.silver,
      big: false,
      align: 'center',
      origin: [0.5, 0.5],
    });

    // Check existing save
    const saveList = Saves.list();
    const hasSave = saveList[0].exists;

    const crtState = isCrtEnabled();
    const menuItems = [
      { label: 'NOWA GRA' },
      { label: 'ROZDZIAŁ 7: OGNISKO (PREVIEW)' },
      { label: hasSave ? `KONTYNUUJ (${saveList[0].leader})` : 'KONTYNUUJ', disabled: !hasSave },
      { label: `FILTR CRT: ${crtState ? 'WŁĄCZONY' : 'WYŁĄCZONY'}` },
    ];

    const menuW = 340;
    const menuX = (GAME_W - menuW) / 2;
    const menuY = 260;
    this.menu = new Menu(this, menuX, menuY, menuW, menuItems);

    // Footer credits
    txt(this, GAME_W / 2, GAME_H - 24, '© 2026 THE PACK CREW • [STRZAŁKI / Z: WYBIERZ]', {
      color: PAL.grey,
      align: 'center',
      origin: [0.5, 0.5],
    });

    this.inputHandler = new Input(this);
  }

  update(): void {
    const pick = this.menu.update(this.inputHandler);
    if (pick === 0) {
      // NOWA GRA -> Analyzer
      this.cameras.main.fadeOut(300, 0, 3, 11);
      this.cameras.main.once(Phaser.Cameras.Scene2D.Events.FADE_OUT_COMPLETE, () => {
        this.scene.start('Analyzer');
      });
    } else if (pick === 1) {
      // Direct jump to Chapter 7 Campfire slice!
      this.cameras.main.fadeOut(300, 0, 3, 11);
      this.cameras.main.once(Phaser.Cameras.Scene2D.Events.FADE_OUT_COMPLETE, () => {
        this.scene.start('Campfire');
      });
    } else if (pick === 2) {
      // Load slot 0
      const save = Saves.load(0);
      if (save) {
        this.cameras.main.fadeOut(300, 0, 3, 11);
        this.cameras.main.once(Phaser.Cameras.Scene2D.Events.FADE_OUT_COMPLETE, () => {
          this.scene.start('World', { loadSave: save });
        });
      }
    } else if (pick === 3) {
      // Toggle CRT
      const newState = !isCrtEnabled();
      setCrtEnabled(this, newState);
      this.menu.setItems([
        { label: 'NOWA GRA' },
        { label: 'ROZDZIAŁ 7: OGNISKO (PREVIEW)' },
        { label: Saves.list()[0].exists ? `KONTYNUUJ` : 'KONTYNUUJ', disabled: !Saves.list()[0].exists },
        { label: `FILTR CRT: ${newState ? 'WŁĄCZONY' : 'WYŁĄCZONY'}` },
      ]);
    }
  }
}
