#!/usr/bin/env python3
"""generate_m2_assets.py - generates assets for Milestone 2 (Chapter 2 & Chapter 3):
1. Enemies:
   - public/assets/enemies/sasiadSzkodnik.png (48x48 x 2 frames = 96x48)
   - public/assets/enemies/autoTuneHipster.png (48x48 x 2 frames = 96x48)
   - public/assets/enemies/drogiePiwo.png (48x48 x 2 frames = 96x48)
2. Backgrounds:
   - public/assets/bg/battle_garage.png (480x270)
   - public/assets/bg/battle_pub.png (480x270)
3. Tilesets:
   - public/assets/tiles/garage.png (128x64)
   - public/assets/tiles/pub.png (128x64)
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

def make_enemies():
    # 1. Sąsiad Szkodnik (cranky neighbor in bathrobe holding a broom)
    img = Image.new("RGBA", (96, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for f in range(2):
        fx = f * 48
        bob = 1 if f == 1 else 0
        cx, cy = fx + 24, 24 + bob
        # Head with balding grey hair
        d.rectangle([cx - 5, cy - 14, cx + 5, cy - 5], fill=SKIN)
        d.rectangle([cx - 6, cy - 14, cx - 4, cy - 8], fill=SILVER)
        d.rectangle([cx + 4, cy - 14, cx + 6, cy - 8], fill=SILVER)
        # Angry eyes + furrowed brows
        d.point([cx - 2, cy - 9], fill=RED)
        d.point([cx + 2, cy - 9], fill=RED)
        d.line([cx - 4, cy - 11, cx + 4, cy - 11], fill=PLUM)
        # Bathrobe body (dirty blue/grey)
        d.rectangle([cx - 7, cy - 4, cx + 7, cy + 12], fill=SLATE)
        d.rectangle([cx - 2, cy - 4, cx + 2, cy + 12], fill=GREY)
        # Slippers
        d.rectangle([cx - 6, cy + 13, cx - 2, cy + 16], fill=FIRE)
        d.rectangle([cx + 2, cy + 13, cx + 6, cy + 16], fill=FIRE)
        # Broom in hand
        broom_angle = -2 if f == 1 else 2
        d.line([cx + 8, cy - 10 + broom_angle, cx + 14, cy + 16], fill=WOOD, width=2)
        d.rectangle([cx + 6, cy - 14 + broom_angle, cx + 11, cy - 9 + broom_angle], fill=YELLOW)
    p = os.path.join(ASSETS, "enemies", "sasiadSzkodnik.png")
    P.binarize_alpha(P.quantize(img, q)).save(p)

    # 2. Auto-Tune Hipster (hipster with beanie, round glasses, holding a glowing laptop)
    img = Image.new("RGBA", (96, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for f in range(2):
        fx = f * 48
        bob = math.sin(f * 3.14) * 2
        cx, cy = fx + 24, 24 + int(bob)
        # Beanie & round glasses
        d.rectangle([cx - 5, cy - 16, cx + 5, cy - 10], fill=FIRE)
        d.rectangle([cx - 5, cy - 9, cx + 5, cy - 2], fill=SKIN)
        d.rectangle([cx - 4, cy - 2, cx + 4, cy + 2], fill=(0x4A, 0x2E, 0x22, 255)) # groomed beard
        # Thick round glasses
        d.rectangle([cx - 4, cy - 7, cx - 1, cy - 5], outline=PLUM)
        d.rectangle([cx + 1, cy - 7, cx + 4, cy - 5], outline=PLUM)
        # Flannel shirt
        d.rectangle([cx - 7, cy + 3, cx + 7, cy + 13], fill=RED)
        d.line([cx, cy + 3, cx, cy + 13], fill=WHITE)
        # Glowing laptop
        d.rectangle([cx - 10, cy + 5, cx - 2, cy + 11], fill=CYAN)
        d.point([cx - 6, cy + 8], fill=WHITE)
        # Skinny jeans
        d.rectangle([cx - 6, cy + 14, cx + 6, cy + 18], fill=NAVY)
    p = os.path.join(ASSETS, "enemies", "autoTuneHipster.png")
    P.binarize_alpha(P.quantize(img, q)).save(p)

    # 3. Zbyt Drogie Piwo (Craft Beer Monster with foam and hop cones)
    img = Image.new("RGBA", (96, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for f in range(2):
        fx = f * 48
        bob = math.cos(f * 3.14) * 2
        cx, cy = fx + 24, 24 + int(bob)
        # Dark glass bottle
        d.rectangle([cx - 7, cy - 10, cx + 7, cy + 16], fill=(0x3A, 0x2A, 0x1E, 255))
        d.rectangle([cx - 3, cy - 18, cx + 3, cy - 10], fill=(0x3A, 0x2A, 0x1E, 255))
        # Foaming bubbling head
        d.ellipse([cx - 9, cy - 20, cx + 9, cy - 10], fill=WHITE)
        d.point([cx - 2, cy - 15], fill=YELLOW)
        d.point([cx + 3, cy - 13], fill=YELLOW)
        # Craft hipster label ("IPA 48 zł")
        d.rectangle([cx - 6, cy - 4, cx + 6, cy + 8], fill=YELLOW)
        d.rectangle([cx - 4, cy - 1, cx + 4, cy + 5], fill=GREEN) # hop cone
        # Angry eyes on bottle
        d.rectangle([cx - 4, cy - 8, cx - 2, cy - 6], fill=WHITE)
        d.point([cx - 3, cy - 7], fill=RED)
        d.rectangle([cx + 2, cy - 8, cx + 4, cy - 6], fill=WHITE)
        d.point([cx + 3, cy - 7], fill=RED)
    p = os.path.join(ASSETS, "enemies", "drogiePiwo.png")
    P.binarize_alpha(P.quantize(img, q)).save(p)
    print("Generated M2 enemies")

def make_backgrounds():
    # 1. battle_garage.png (Underground garage with tires and projector beam)
    bg = Image.new("RGBA", (480, 270), INK)
    d = ImageDraw.Draw(bg)
    # Concrete wall
    d.rectangle([0, 0, 479, 160], fill=PANEL)
    for gy in range(0, 160, 20):
        d.line([0, gy, 479, gy], fill=STEEL)
    # Projector cone of light (UFC 300)
    d.polygon([(100, 30), (400, 160), (0, 160)], fill=(0x10, 0x2D, 0x3B, 255))
    # Concrete oily floor
    d.rectangle([0, 160, 479, 269], fill=(0x1E, 0x28, 0x44, 255))
    # Tire stacks in background
    for tx in [30, 70, 420]:
        for ty in range(120, 160, 12):
            d.rectangle([tx, ty, tx + 24, ty + 10], fill=VOID, outline=PLUM)
    p = os.path.join(ASSETS, "bg", "battle_garage.png")
    P.binarize_alpha(P.quantize(bg, q)).save(p)

    # 2. battle_pub.png (Pub Czarny Krążek with wood shelves and vinyl records)
    bg = Image.new("RGBA", (480, 270), WOOD_DK)
    d = ImageDraw.Draw(bg)
    # Back bar wall with dark wood paneling
    d.rectangle([0, 0, 479, 160], fill=(0x2A, 0x1A, 0x14, 255))
    # Vinyl records on wall
    for vx in range(40, 460, 60):
        d.ellipse([vx, 40, vx + 36, 76], fill=VOID, outline=PLUM)
        d.ellipse([vx + 12, 52, vx + 24, 64], fill=RED)
        d.point([vx + 18, 58], fill=WHITE)
    # Bar counter with beer taps
    d.rectangle([0, 130, 479, 160], fill=WOOD)
    d.line([0, 130, 479, 130], fill=YELLOW, width=2)
    for bx in [120, 240, 360]:
        d.rectangle([bx, 105, bx + 6, 130], fill=SILVER) # taps
    # Pub floor
    d.rectangle([0, 160, 479, 269], fill=(0x1B, 0x13, 0x19, 255))
    p = os.path.join(ASSETS, "bg", "battle_pub.png")
    P.binarize_alpha(P.quantize(bg, q)).save(p)
    print("Generated M2 backgrounds")

def make_tiles():
    # Garage tileset 128x64 (8 tiles per row)
    gt = Image.new("RGBA", (128, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(gt)
    # 0: concrete garage floor
    d.rectangle([0, 0, 15, 15], fill=(0x2E, 0x3B, 0x4D, 255))
    d.point([4, 4], fill=(0x1E, 0x28, 0x44, 255)) # oil spot
    # 1: concrete wall with pipes
    d.rectangle([16, 0, 31, 15], fill=STEEL)
    d.line([16, 4, 31, 4], fill=CYAN)
    # 2: wall top
    d.rectangle([32, 0, 47, 15], fill=INK)
    # 3: tire stack (solid)
    d.rectangle([48, 0, 63, 15], fill=(0x2E, 0x3B, 0x4D, 255))
    d.ellipse([49, 2, 62, 13], fill=VOID, outline=PLUM)
    # 4: weights / barbell (solid)
    d.rectangle([64, 0, 79, 15], fill=(0x2E, 0x3B, 0x4D, 255))
    d.line([65, 8, 78, 8], fill=SILVER, width=2)
    d.rectangle([66, 4, 69, 12], fill=PLUM)
    d.rectangle([74, 4, 77, 12], fill=PLUM)
    # 5: beer fridge (solid)
    d.rectangle([80, 0, 95, 15], fill=PANEL_HI)
    d.rectangle([82, 3, 93, 13], fill=CYAN)
    # 6: projector screen (solid)
    d.rectangle([96, 0, 111, 15], fill=WHITE)
    d.rectangle([98, 2, 109, 13], fill=NAVY)
    # 7: exit door
    d.rectangle([112, 0, 127, 15], fill=STEEL)
    d.point([124, 8], fill=YELLOW)
    p = os.path.join(ASSETS, "tiles", "garage.png")
    P.binarize_alpha(P.quantize(gt, q)).save(p)

    # Pub tileset 128x64
    pt = Image.new("RGBA", (128, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(pt)
    # 0: pub dark wood floor
    d.rectangle([0, 0, 15, 15], fill=WOOD)
    d.line([0, 7, 15, 7], fill=WOOD_DK)
    # 1: wood paneled wall
    d.rectangle([16, 0, 31, 15], fill=WOOD_DK)
    d.line([16, 15, 31, 15], fill=YELLOW)
    # 2: wall top
    d.rectangle([32, 0, 47, 15], fill=PLUM)
    # 3: bar counter top (solid)
    d.rectangle([48, 0, 63, 15], fill=WOOD_DK)
    d.rectangle([48, 0, 63, 6], fill=YELLOW)
    # 4: beer taps (solid)
    d.rectangle([64, 0, 79, 15], fill=WOOD_DK)
    d.rectangle([70, 2, 73, 14], fill=SILVER)
    # 5: vinyl rack (solid)
    d.rectangle([80, 0, 95, 15], fill=WOOD_DK)
    d.ellipse([82, 2, 93, 13], fill=VOID)
    d.ellipse([85, 5, 90, 10], fill=RED)
    # 6: DJ turntable desk (solid)
    d.rectangle([96, 0, 111, 15], fill=STEEL)
    d.ellipse([98, 2, 108, 12], fill=VOID)
    d.line([106, 3, 103, 7], fill=SILVER) # tonearm
    # 7: pub exit door
    d.rectangle([112, 0, 127, 15], fill=WOOD_DK)
    d.point([124, 8], fill=YELLOW)
    p = os.path.join(ASSETS, "tiles", "pub.png")
    P.binarize_alpha(P.quantize(pt, q)).save(p)
    print("Generated M2 tilesets")

def update_manifest():
    mpath = os.path.join(ASSETS, "manifest.json")
    with open(mpath) as f:
        data = json.load(f)

    data["images"]["battle_garage_bg"] = "assets/bg/battle_garage.png"
    data["images"]["battle_pub_bg"] = "assets/bg/battle_pub.png"
    data["images"]["tiles_garage"] = "assets/tiles/garage.png"
    data["images"]["tiles_pub"] = "assets/tiles/pub.png"

    data["spritesheets"]["enemy_sasiadSzkodnik"] = {"path": "assets/enemies/sasiadSzkodnik.png", "frameWidth": 48, "frameHeight": 48}
    data["spritesheets"]["enemy_autoTuneHipster"] = {"path": "assets/enemies/autoTuneHipster.png", "frameWidth": 48, "frameHeight": 48}
    data["spritesheets"]["enemy_drogiePiwo"] = {"path": "assets/enemies/drogiePiwo.png", "frameWidth": 48, "frameHeight": 48}

    with open(mpath, "w") as f:
        json.dump(data, f, indent=2)
    print("Updated manifest.json")

if __name__ == "__main__":
    make_enemies()
    make_backgrounds()
    make_tiles()
    update_manifest()
