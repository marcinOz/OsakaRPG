#!/usr/bin/env python3
"""generate_m3_assets.py - generates pixel art assets for Milestone 3, 4, 5 (Chapters 4 - 10):
1. Enemies:
   - public/assets/enemies/kark.png (48x48 x 2 frames = 96x48)
   - public/assets/enemies/straznik.png (48x48 x 2 frames = 96x48)
   - public/assets/enemies/panJanusz.png (48x48 x 2 frames = 96x48)
   - public/assets/enemies/kredyt.png (48x48 x 2 frames = 96x48)
   - public/assets/enemies/audyt.png (48x48 x 2 frames = 96x48)
   - public/assets/enemies/rwaKulszowa.png (48x48 x 2 frames = 96x48)
2. Backgrounds:
   - public/assets/bg/battle_alley.png (480x270)
   - public/assets/bg/battle_marina.png (480x270)
   - public/assets/bg/battle_rift.png (480x270)
   - public/assets/bg/sunrise.png (480x270)
3. Tilesets:
   - public/assets/tiles/alley.png (128x64)
   - public/assets/tiles/marina.png (128x64)
4. Update manifest.json
"""
import json
import math
import os
import sys
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pixelize as P

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "public", "assets")
pal = P.load_palette()
q = P.Quantizer(pal)

# Master palette colors
VOID = (0x00, 0x03, 0x0B, 255)
INK = (0x06, 0x12, 0x20, 255)
NAVY = (0x0A, 0x18, 0x2B, 255)
PANEL = (0x0C, 0x21, 0x34, 255)
PANEL_HI = (0x10, 0x2D, 0x3B, 255)
STEEL = (0x20, 0x3D, 0x54, 255)
SLATE = (0x2E, 0x3B, 0x4D, 255)
GREY = (0x5E, 0x6F, 0x7A, 255)
SILVER = (0x97, 0xA0, 0xA6, 255)
CYAN = (0x9E, 0xCB, 0xD4, 255)
WHITE = (0xD8, 0xDA, 0xDA, 255)
PLUM = (0x1B, 0x13, 0x19, 255)
YELLOW = (0xE8, 0xD8, 0x4A, 255)
GREEN = (0x5F, 0xC8, 0x5A, 255)
FIRE = (0xE0, 0x74, 0x2C, 255)
RED = (0xC0, 0x39, 0x2B, 255)
DENIM = (0x3F, 0x6B, 0x8F, 255)
WOOD = (0x5C, 0x46, 0x30, 255)
WOOD_DK = (0x3A, 0x2A, 0x1E, 255)
SKIN = (0xD9, 0xA0, 0x66, 255)
PURPLE = (0x68, 0x38, 0x6C, 255)

def make_enemies():
    # 1. Szef Ochrony "Kark" (Broad-shouldered bouncer with black security jacket & sunglasses)
    img = Image.new("RGBA", (96, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for f in range(2):
        fx = f * 48
        bob = 1 if f == 1 else 0
        cx, cy = fx + 24, 22 + bob
        # Shaved head & neck
        d.rectangle([cx - 6, cy - 13, cx + 6, cy - 4], fill=SKIN)
        d.rectangle([cx - 5, cy - 15, cx + 5, cy - 13], fill=(0x4A, 0x2E, 0x22, 255))
        # Sunglasses
        d.rectangle([cx - 5, cy - 8, cx - 1, cy - 6], fill=VOID)
        d.rectangle([cx + 1, cy - 8, cx + 5, cy - 6], fill=VOID)
        d.line([cx - 1, cy - 7, cx + 1, cy - 7], fill=VOID)
        # Broad black security bomber jacket
        d.rectangle([cx - 11, cy - 3, cx + 11, cy + 13], fill=INK)
        d.rectangle([cx - 9, cy - 1, cx + 9, cy + 11], fill=PANEL)
        # Gold security badge
        d.rectangle([cx - 6, cy + 1, cx - 2, cy + 4], fill=YELLOW)
        # Thick arms crossed
        d.rectangle([cx - 9, cy + 5, cx + 9, cy + 9], fill=INK)
        # Black trousers & boots
        d.rectangle([cx - 8, cy + 14, cx - 2, cy + 22], fill=VOID)
        d.rectangle([cx + 2, cy + 14, cx + 8, cy + 22], fill=VOID)
    p = os.path.join(ASSETS, "enemies", "kark.png")
    P.binarize_alpha(P.quantize(img, q)).save(p)

    # 2. Strażnik Miejski (Municipal guard with navy cap & neon yellow vest)
    img = Image.new("RGBA", (96, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for f in range(2):
        fx = f * 48
        bob = math.sin(f * 3.14) * 2
        cx, cy = fx + 24, 24 + int(bob)
        # Guard cap with checkered band
        d.rectangle([cx - 5, cy - 15, cx + 5, cy - 11], fill=NAVY)
        d.line([cx - 5, cy - 11, cx + 5, cy - 11], fill=YELLOW)
        # Head
        d.rectangle([cx - 4, cy - 10, cx + 4, cy - 4], fill=SKIN)
        d.point([cx - 2, cy - 7], fill=VOID)
        d.point([cx + 2, cy - 7], fill=VOID)
        # Neon high-vis vest
        d.rectangle([cx - 7, cy - 3, cx + 7, cy + 11], fill=YELLOW)
        d.line([cx - 5, cy + 3, cx + 5, cy + 3], fill=WHITE, width=2)
        # Baton at belt
        d.line([cx + 7, cy + 4, cx + 11, cy + 16], fill=VOID, width=2)
        # Dark trousers
        d.rectangle([cx - 5, cy + 12, cx - 1, cy + 19], fill=NAVY)
        d.rectangle([cx + 1, cy + 12, cx + 5, cy + 19], fill=NAVY)
    p = os.path.join(ASSETS, "enemies", "straznik.png")
    P.binarize_alpha(P.quantize(img, q)).save(p)

    # 3. Pan Janusz (Komendant Straży Leśnej with green coat, forester cap, ticket book & megaphone)
    img = Image.new("RGBA", (96, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for f in range(2):
        fx = f * 48
        bob = 1 if f == 1 else 0
        cx, cy = fx + 24, 23 + bob
        # Forester cap
        d.rectangle([cx - 6, cy - 16, cx + 6, cy - 12], fill=(0x2E, 0x4B, 0x2A, 255))
        d.point([cx, cy - 14], fill=YELLOW) # gold pine badge
        # Scowling face with thick grey moustache
        d.rectangle([cx - 5, cy - 11, cx + 5, cy - 4], fill=SKIN)
        d.point([cx - 2, cy - 9], fill=RED)
        d.point([cx + 2, cy - 9], fill=RED)
        d.rectangle([cx - 4, cy - 6, cx + 4, cy - 4], fill=SILVER) # bushy moustache
        # Green forestry coat with collar
        d.rectangle([cx - 8, cy - 3, cx + 8, cy + 13], fill=(0x1D, 0x36, 0x1A, 255))
        d.line([cx, cy - 3, cx, cy + 13], fill=YELLOW) # gold buttons
        # Megaphone in left hand
        d.polygon([(cx - 7, cy + 1), (cx - 14, cy - 3), (cx - 14, cy + 5)], fill=FIRE)
        # Ticket/fine book in right hand
        d.rectangle([cx + 6, cy + 2, cx + 11, cy + 9], fill=WHITE, outline=RED)
        # Forestry trousers & heavy boots
        d.rectangle([cx - 6, cy + 14, cx - 2, cy + 21], fill=WOOD_DK)
        d.rectangle([cx + 2, cy + 14, cx + 6, cy + 21], fill=WOOD_DK)
    p = os.path.join(ASSETS, "enemies", "panJanusz.png")
    P.binarize_alpha(P.quantize(img, q)).save(p)

    # 4. Kredyt na 30 Lat (Monolithic stone tablet with mortgage deed wrapped in red caution tape)
    img = Image.new("RGBA", (96, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for f in range(2):
        fx = f * 48
        bob = math.sin(f * 3.14) * 2
        cx, cy = fx + 24, 24 + int(bob)
        # Giant stone deed slab
        d.rectangle([cx - 12, cy - 18, cx + 12, cy + 18], fill=SLATE, outline=VOID)
        d.rectangle([cx - 10, cy - 16, cx + 10, cy + 16], fill=STEEL)
        # Red mortgage stamp "30 LAT"
        d.line([cx - 12, cy - 10, cx + 12, cy - 2], fill=RED, width=3)
        d.line([cx - 12, cy + 2, cx + 12, cy + 10], fill=RED, width=3)
        d.rectangle([cx - 7, cy - 3, cx + 7, cy + 3], fill=YELLOW)
        # Glowing sinister eyes
        eye_col = FIRE if f == 1 else RED
        d.rectangle([cx - 6, cy - 12, cx - 2, cy - 10], fill=eye_col)
        d.rectangle([cx + 2, cy - 12, cx + 6, cy - 10], fill=eye_col)
    p = os.path.join(ASSETS, "enemies", "kredyt.png")
    P.binarize_alpha(P.quantize(img, q)).save(p)

    # 5. Audyt Korporacyjny (Spreadsheet monster with red pie charts and magnifying glass)
    img = Image.new("RGBA", (96, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for f in range(2):
        fx = f * 48
        bob = math.cos(f * 3.14) * 2
        cx, cy = fx + 24, 24 + int(bob)
        # Spreadsheet grid body
        d.rectangle([cx - 13, cy - 16, cx + 13, cy + 15], fill=WHITE, outline=NAVY)
        # Grid lines
        for gy in range(cy - 12, cy + 14, 5):
            d.line([cx - 12, gy, cx + 12, gy], fill=CYAN)
        d.line([cx - 3, cy - 15, cx - 3, cy + 14], fill=CYAN)
        d.line([cx + 5, cy - 15, cx + 5, cy + 14], fill=CYAN)
        # Pie chart eye
        d.ellipse([cx - 8, cy - 8, cx, cy], fill=RED)
        d.polygon([(cx - 4, cy - 4), (cx, cy - 8), (cx, cy - 4)], fill=YELLOW)
        # Magnifying glass weapon
        d.ellipse([cx + 3, cy - 6, cx + 11, cy + 2], fill=CYAN, outline=FIRE)
        d.line([cx + 9, cy + 1, cx + 14, cy + 8], fill=FIRE, width=2)
        # Red KPI deficit markers
        d.point([cx - 10, cy + 6], fill=RED)
        d.point([cx - 6, cy + 9], fill=RED)
        d.point([cx + 1, cy + 11], fill=RED)
    p = os.path.join(ASSETS, "enemies", "audyt.png")
    P.binarize_alpha(P.quantize(img, q)).save(p)

    # 6. Rwa Kulszowa (Crackling violet/red sciatic nerve / lightning spine monster)
    img = Image.new("RGBA", (96, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for f in range(2):
        fx = f * 48
        cx, cy = fx + 24, 24
        # Glowing spinal column segments
        for i in range(-5, 6):
            sy = cy + i * 3
            w = 5 - abs(i) // 2
            col = FIRE if (f + i) % 2 == 0 else RED
            d.rectangle([cx - w, sy - 1, cx + w, sy + 1], fill=col)
        # Crackling electric nerve tendrils
        sparks = [(cx - 9, cy - 10), (cx + 10, cy - 6), (cx - 12, cy + 4), (cx + 8, cy + 12), (cx - 7, cy + 14)]
        if f == 1:
            sparks = [(cx + 9, cy - 9), (cx - 10, cy - 5), (cx + 12, cy + 3), (cx - 8, cy + 11), (cx + 7, cy + 15)]
        for sx, sy in sparks:
            d.line([cx, sy, sx, sy], fill=YELLOW)
            d.point([sx, sy], fill=WHITE)
    p = os.path.join(ASSETS, "enemies", "rwaKulszowa.png")
    P.binarize_alpha(P.quantize(img, q)).save(p)
    print("Generated M3/M4/M5 enemies")

def make_backgrounds():
    # 1. battle_alley.png (Old Town cobblestone alleyway at night with streetlamp)
    bg = Image.new("RGBA", (480, 270), INK)
    d = ImageDraw.Draw(bg)
    # Brick walls on both sides
    d.rectangle([0, 0, 160, 180], fill=(0x2A, 0x1A, 0x14, 255))
    d.rectangle([320, 0, 479, 180], fill=(0x2A, 0x1A, 0x14, 255))
    # Brick courses
    for by in range(0, 180, 12):
        d.line([0, by, 160, by], fill=WOOD_DK)
        d.line([320, by, 479, by], fill=WOOD_DK)
    # Night sky in alley center
    d.rectangle([161, 0, 319, 130], fill=NAVY)
    # Cobblestone ground
    d.rectangle([0, 160, 479, 269], fill=(0x1E, 0x24, 0x30, 255))
    for gy in range(160, 270, 14):
        d.line([0, gy, 479, gy], fill=PLUM)
    # Streetlamp casting yellow glow cone
    d.line([340, 60, 340, 160], fill=STEEL, width=3)
    d.rectangle([336, 50, 344, 60], fill=YELLOW)
    d.polygon([(340, 60), (220, 240), (460, 240)], fill=(0x2A, 0x30, 0x20, 255))
    # Dumpster in background
    d.rectangle([40, 130, 110, 175], fill=STEEL, outline=VOID)
    p = os.path.join(ASSETS, "bg", "battle_alley.png")
    P.binarize_alpha(P.quantize(bg, q)).save(p)

    # 2. battle_marina.png (Wooden marina pier over shimmering lake)
    bg = Image.new("RGBA", (480, 270), NAVY)
    d = ImageDraw.Draw(bg)
    # Night sky with stars
    d.rectangle([0, 0, 479, 110], fill=INK)
    for star in [(50, 20), (120, 35), (280, 15), (390, 40), (450, 25)]:
        d.point(star, fill=CYAN)
    # Distant forest ridge
    d.polygon([(0, 110), (100, 85), (240, 100), (360, 80), (480, 105), (480, 130), (0, 130)], fill=(0x0E, 0x1E, 0x22, 255))
    # Dark lake water
    d.rectangle([0, 120, 479, 269], fill=(0x08, 0x1C, 0x2C, 255))
    for ry in range(125, 170, 8):
        d.line([50, ry, 430, ry], fill=(0x10, 0x32, 0x48, 255))
    # Wooden pier platform where heroes stand
    d.rectangle([0, 165, 479, 269], fill=WOOD)
    for px in range(0, 480, 40):
        d.line([px, 165, px, 269], fill=WOOD_DK, width=2)
    d.line([0, 165, 479, 165], fill=YELLOW, width=2)
    # Dock pilings
    for dx in [30, 180, 320, 450]:
        d.rectangle([dx, 145, dx + 10, 175], fill=WOOD_DK, outline=VOID)
    p = os.path.join(ASSETS, "bg", "battle_marina.png")
    P.binarize_alpha(P.quantize(bg, q)).save(p)

    # 3. battle_rift.png (Dimensional Forest Rift for Ch.9 final battle)
    bg = Image.new("RGBA", (480, 270), INK)
    d = ImageDraw.Draw(bg)
    # Swirling vortex layers in sky
    d.rectangle([0, 0, 479, 180], fill=(0x16, 0x0A, 0x22, 255))
    for rad in [140, 100, 60, 25]:
        d.ellipse([240 - rad, 90 - rad // 2, 240 + rad, 90 + rad // 2], outline=CYAN if rad < 70 else PURPLE, width=2)
    d.ellipse([230, 80, 250, 100], fill=CYAN)
    # Twisted dark ancient trees framing the rift
    d.polygon([(0, 0), (70, 0), (40, 180), (0, 180)], fill=VOID)
    d.polygon([(480, 0), (410, 0), (440, 180), (480, 180)], fill=VOID)
    # Shattered cosmic ground
    d.rectangle([0, 170, 479, 269], fill=(0x1A, 0x14, 0x28, 255))
    for lx in range(40, 440, 50):
        d.line([lx, 170, lx - 20, 269], fill=PURPLE)
    p = os.path.join(ASSETS, "bg", "battle_rift.png")
    P.binarize_alpha(P.quantize(bg, q)).save(p)

    # 4. sunrise.png (Ch.10 Sunrise over the forest lake)
    bg = Image.new("RGBA", (480, 270), (0, 0, 0, 255))
    d = ImageDraw.Draw(bg)
    # Sky dawn gradient: navy -> violet -> rose -> orange -> gold
    sky_bands = [
        (0, 30, (0x1B, 0x13, 0x28, 255)),
        (30, 65, (0x3A, 0x1E, 0x36, 255)),
        (65, 100, (0x7A, 0x2C, 0x3C, 255)),
        (100, 130, FIRE),
        (130, 155, YELLOW),
    ]
    for y1, y2, col in sky_bands:
        d.rectangle([0, y1, 479, y2], fill=col)
    # Golden sun cresting the horizon
    d.ellipse([215, 125, 265, 175], fill=WHITE, outline=YELLOW)
    # Pine forest horizon silhouette
    for x in range(0, 480, 16):
        h = 15 + (x % 37) % 15
        d.polygon([(x, 155), (x + 8, 155 - h), (x + 16, 155)], fill=INK)
    # Shimmering lake reflecting the morning sun
    d.rectangle([0, 155, 479, 269], fill=(0x28, 0x1C, 0x30, 255))
    # Golden water reflection beam
    d.polygon([(240, 155), (180, 269), (300, 269)], fill=(0x5C, 0x36, 0x20, 255))
    for ry in range(160, 270, 7):
        d.line([200 - (ry - 160) // 3, ry, 280 + (ry - 160) // 3, ry], fill=YELLOW)
    p = os.path.join(ASSETS, "bg", "sunrise.png")
    P.binarize_alpha(P.quantize(bg, q)).save(p)
    print("Generated M3/M4/M5 backgrounds")

def make_tiles():
    # 1. Alley tileset 128x64 (8 tiles per row, 16x16 each)
    at = Image.new("RGBA", (128, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(at)
    # 0: Cobblestone ground
    d.rectangle([0, 0, 15, 15], fill=SLATE)
    d.point([3, 4], fill=GREY)
    d.point([11, 10], fill=GREY)
    d.line([0, 8, 15, 8], fill=PLUM)
    # 1: Brick wall
    d.rectangle([16, 0, 31, 15], fill=(0x2A, 0x1A, 0x14, 255))
    d.line([16, 7, 31, 7], fill=WOOD_DK)
    d.line([23, 0, 23, 7], fill=WOOD_DK)
    d.line([27, 7, 27, 15], fill=WOOD_DK)
    # 2: Brick wall top
    d.rectangle([32, 0, 47, 15], fill=INK)
    # 3: Dumpster body (solid)
    d.rectangle([48, 0, 63, 15], fill=STEEL)
    d.rectangle([49, 2, 62, 5], fill=GREY) # lid
    d.point([53, 9], fill=VOID) # graffiti
    # 4: Streetlamp post (solid)
    d.rectangle([64, 0, 79, 15], fill=SLATE)
    d.rectangle([71, 0, 72, 15], fill=STEEL)
    d.rectangle([69, 2, 74, 6], fill=YELLOW) # lantern
    # 5: Wooden crate stack (solid)
    d.rectangle([80, 0, 95, 15], fill=WOOD)
    d.rectangle([81, 1, 94, 14], outline=WOOD_DK)
    d.line([81, 1, 94, 14], fill=WOOD_DK)
    # 6: Dark shadow puddle / hide spot
    d.rectangle([96, 0, 111, 15], fill=SLATE)
    d.ellipse([98, 4, 109, 12], fill=INK)
    # 7: Exit passage
    d.rectangle([112, 0, 127, 15], fill=STEEL)
    d.line([112, 15, 127, 15], fill=YELLOW)
    p = os.path.join(ASSETS, "tiles", "alley.png")
    P.binarize_alpha(P.quantize(at, q)).save(p)

    # 2. Marina tileset 128x64
    mt = Image.new("RGBA", (128, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(mt)
    # 0: Wooden pier plank walkway
    d.rectangle([0, 0, 15, 15], fill=WOOD)
    d.line([0, 5, 15, 5], fill=WOOD_DK)
    d.line([0, 11, 15, 11], fill=WOOD_DK)
    # 1: Lake water (solid - impassable without boat)
    d.rectangle([16, 0, 31, 15], fill=(0x0A, 0x22, 0x36, 255))
    d.line([18, 6, 28, 6], fill=CYAN)
    # 2: Pier edge with water
    d.rectangle([32, 0, 47, 8], fill=WOOD)
    d.rectangle([32, 9, 47, 15], fill=(0x0A, 0x22, 0x36, 255))
    d.line([32, 8, 47, 8], fill=WOOD_DK)
    # 3: Dock mooring post (solid)
    d.rectangle([48, 0, 63, 15], fill=WOOD)
    d.rectangle([53, 2, 58, 13], fill=WOOD_DK, outline=VOID)
    d.line([51, 6, 60, 6], fill=WHITE) # mooring rope
    # 4: Lifebuoy stand (solid)
    d.rectangle([64, 0, 79, 15], fill=WOOD)
    d.ellipse([67, 2, 76, 11], fill=FIRE)
    d.ellipse([70, 5, 73, 8], fill=WOOD)
    # 5: Rescue boat (solid/interactive)
    d.rectangle([80, 0, 95, 15], fill=(0x0A, 0x22, 0x36, 255))
    d.polygon([(82, 3), (94, 3), (92, 13), (84, 13)], fill=WHITE, outline=NAVY)
    d.point([88, 7], fill=FIRE) # motor
    # 6: Pier railing (solid)
    d.rectangle([96, 0, 111, 15], fill=WOOD)
    d.line([96, 4, 111, 4], fill=SILVER, width=2)
    d.line([103, 4, 103, 15], fill=SILVER)
    # 7: Pier lamp
    d.rectangle([112, 0, 127, 15], fill=WOOD)
    d.rectangle([118, 3, 121, 14], fill=STEEL)
    d.rectangle([117, 1, 122, 5], fill=YELLOW)
    p = os.path.join(ASSETS, "tiles", "marina.png")
    P.binarize_alpha(P.quantize(mt, q)).save(p)
    print("Generated M3/M4/M5 tilesets")

def update_manifest():
    mpath = os.path.join(ASSETS, "manifest.json")
    with open(mpath) as f:
        data = json.load(f)

    # Backgrounds
    data["images"]["battle_alley_bg"] = "assets/bg/battle_alley.png"
    data["images"]["battle_marina_bg"] = "assets/bg/battle_marina.png"
    data["images"]["battle_rift_bg"] = "assets/bg/battle_rift.png"
    data["images"]["sunrise_bg"] = "assets/bg/sunrise.png"

    # Tiles
    data["images"]["tiles_alley"] = "assets/tiles/alley.png"
    data["images"]["tiles_marina"] = "assets/tiles/marina.png"

    # Enemies
    data["spritesheets"]["enemy_kark"] = {"path": "assets/enemies/kark.png", "frameWidth": 48, "frameHeight": 48}
    data["spritesheets"]["enemy_straznik"] = {"path": "assets/enemies/straznik.png", "frameWidth": 48, "frameHeight": 48}
    data["spritesheets"]["enemy_panJanusz"] = {"path": "assets/enemies/panJanusz.png", "frameWidth": 48, "frameHeight": 48}
    data["spritesheets"]["enemy_kredyt"] = {"path": "assets/enemies/kredyt.png", "frameWidth": 48, "frameHeight": 48}
    data["spritesheets"]["enemy_audyt"] = {"path": "assets/enemies/audyt.png", "frameWidth": 48, "frameHeight": 48}
    data["spritesheets"]["enemy_rwaKulszowa"] = {"path": "assets/enemies/rwaKulszowa.png", "frameWidth": 48, "frameHeight": 48}

    with open(mpath, "w") as f:
        json.dump(data, f, indent=2)
    print("Updated manifest.json with M3/M4/M5 assets")

if __name__ == "__main__":
    make_enemies()
    make_backgrounds()
    make_tiles()
    update_manifest()
