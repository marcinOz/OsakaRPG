#!/usr/bin/env python3
"""generate_hd_backgrounds.py - Generate 1024x576 high-detail painterly pixel backgrounds,
32x32 tilesets, animated fire spritesheet, and update manifest.json.
"""
import os
import math
import json
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "public", "assets")
BG_DIR = os.path.join(ASSETS, "bg")
TILES_DIR = os.path.join(ASSETS, "tiles")
os.makedirs(BG_DIR, exist_ok=True)
os.makedirs(TILES_DIR, exist_ok=True)

W, H = 1024, 576

# Master Palette
PAL = {
    'void': (0, 3, 11, 255),
    'ink': (6, 18, 32, 255),
    'navy': (10, 24, 43, 255),
    'panel': (12, 33, 52, 255),
    'steel': (32, 61, 84, 255),
    'slate': (46, 59, 77, 255),
    'grey': (94, 111, 122, 255),
    'silver': (151, 160, 166, 255),
    'white': (235, 240, 245, 255),
    'cyan': (158, 203, 212, 255),
    'cyan_hi': (200, 238, 244, 255),
    'yellow': (232, 216, 74, 255),
    'yellow_hi': (255, 245, 120, 255),
    'orange': (224, 116, 44, 255),
    'fire': (224, 116, 44, 255),
    'fire_hi': (246, 192, 74, 255),
    'red': (192, 57, 43, 255),
    'red_hi': (235, 87, 87, 255),
    'green': (95, 200, 90, 255),
    'green_hi': (130, 230, 120, 255),
    'forest_dk': (20, 38, 24, 255),
    'forest_mid': (35, 65, 40, 255),
    'forest_hi': (55, 95, 60, 255),
    'wood_dk': (45, 28, 18, 255),
    'wood_mid': (75, 48, 30, 255),
    'wood_hi': (110, 72, 45, 255),
    'brick_dk': (70, 30, 25, 255),
    'brick_mid': (115, 45, 35, 255),
    'brick_hi': (155, 65, 50, 255),
    'sodium': (255, 180, 50, 255),
    'zabka_green': (15, 155, 60, 255),
    'zabka_yellow': (255, 210, 0, 255),
    'purple_dk': (30, 15, 45, 255),
    'purple_mid': (70, 30, 95, 255),
    'purple_hi': (140, 60, 190, 255),
    'lake_deep': (12, 25, 48, 255),
    'lake_mid': (22, 45, 78, 255),
    'lake_hi': (40, 80, 125, 255),
    'gold': (215, 175, 45, 255),
    'olive': (75, 90, 48, 255),
    'olive_dk': (45, 58, 30, 255),
    'olive_hi': (110, 130, 70, 255),
}

def draw_v_gradient(d, y0, y1, c0, c1):
    for y in range(y0, y1):
        t = (y - y0) / max(1, (y1 - y0))
        r = int(c0[0] + (c1[0] - c0[0]) * t)
        g = int(c0[1] + (c1[1] - c0[1]) * t)
        b = int(c0[2] + (c1[2] - c0[2]) * t)
        d.line([(0, y), (W, y)], fill=(r, g, b, 255))

def generate_backgrounds():
    print("Generating 1024x576 backgrounds...")

    # 1. title.png: Midnight forest lake with starry sky & distant campfire glow
    im = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(im)
    draw_v_gradient(d, 0, 360, (2, 8, 22), (18, 38, 65)) # Starry night sky
    # Stars
    for sx, sy in [(120, 45), (280, 70), (450, 30), (620, 80), (810, 40), (950, 65),
                   (180, 120), (390, 150), (580, 110), (740, 160), (890, 130), (70, 200)]:
        d.point([sx, sy], fill=PAL['white'])
        d.point([sx + 1, sy], fill=PAL['cyan_hi'])
    # Distant pine silhouette ridge
    for px in range(0, W, 18):
        ph = 140 + int(math.sin(px * 0.02) * 35 + (px * 13) % 25)
        d.polygon([(px, 360), (px + 9, 360 - ph), (px + 18, 360)], fill=(10, 22, 28, 255))
    # Lake water
    draw_v_gradient(d, 360, H, (10, 24, 45), (4, 12, 26))
    # Campfire distant glow reflection on water
    d.ellipse([W//2 - 120, 340, W//2 + 120, 390], fill=(224, 116, 44, 110))
    d.polygon([(W//2 - 25, 350), (W//2, 320), (W//2 + 25, 350)], fill=PAL['fire'])
    # Water ripples
    for ry in range(375, H - 20, 14):
        rw = 80 + (ry - 360) * 3
        d.line([W//2 - rw//2, ry, W//2 + rw//2, ry], fill=(246, 192, 74, 80), width=2)
    im.save(os.path.join(BG_DIR, "title.png"), "PNG")
    print("Saved title.png")

    # 2. battle_apartment.png: Morning apartment, dual monitors, crumpled bed, blinds sunlight
    im = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(im)
    draw_v_gradient(d, 0, 340, (140, 155, 175), (195, 205, 215)) # Morning light wall
    # Parquet wooden floor
    draw_v_gradient(d, 340, H, (120, 80, 50), (75, 45, 25))
    for fy in range(340, H, 24):
        d.line([0, fy, W, fy], fill=(55, 32, 18, 255), width=2)
    # Window with Venetian blinds & sunlight beams
    d.rectangle([680, 40, 940, 280], fill=(240, 245, 255), outline=PAL['slate'], width=3)
    for by in range(46, 276, 8):
        d.line([680, by, 940, by], fill=(160, 175, 195), width=2)
    # Sunlight beam casting onto floor
    d.polygon([(680, 280), (940, 280), (W, 480), (520, 480)], fill=(255, 255, 230, 45))
    # Dual Monitor workstation on left
    d.rectangle([80, 180, 440, 380], fill=(45, 52, 64), outline=PAL['ink'], width=3) # desk
    d.rectangle([110, 110, 250, 200], fill=PAL['panel'], outline=PAL['cyan'], width=2) # Monitor 1
    d.rectangle([270, 110, 410, 200], fill=PAL['panel'], outline=PAL['cyan'], width=2) # Monitor 2
    # Bed on right
    d.rectangle([620, 330, 980, 460], fill=(95, 110, 135), outline=PAL['ink'], width=2)
    d.rectangle([630, 340, 720, 380], fill=PAL['white'], outline=PAL['grey']) # Pillow
    im.save(os.path.join(BG_DIR, "battle_apartment.png"), "PNG")
    print("Saved battle_apartment.png")

    # 3. battle_city.png: Polish blokowisko city street at dawn with glowing Żabka
    im = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(im)
    draw_v_gradient(d, 0, 300, (65, 75, 105), (145, 120, 110)) # Dawn sky
    # Concrete Blokowisko facades
    d.rectangle([40, 60, 380, 400], fill=(90, 98, 108), outline=PAL['ink'], width=2)
    for wy in range(80, 380, 36):
        for wx in range(60, 360, 36):
            d.rectangle([wx, wy, wx + 20, wy + 24], fill=(225, 215, 140) if (wx+wy)%5==0 else (45, 50, 60))
    # Żabka convenience store on right
    d.rectangle([600, 200, 980, 410], fill=(45, 55, 62), outline=PAL['ink'], width=3)
    d.rectangle([620, 220, 960, 260], fill=PAL['zabka_green']) # Store banner
    d.rectangle([720, 228, 860, 252], fill=PAL['zabka_yellow']) # Żabka logo box
    # Street & pavement
    draw_v_gradient(d, 400, H, (45, 50, 58), (28, 30, 36))
    for sx in range(60, W, 120):
        d.line([sx, 480, sx + 60, 480], fill=PAL['white'], width=4) # dashed road markings
    im.save(os.path.join(BG_DIR, "battle_city.png"), "PNG")
    print("Saved battle_city.png")

    # 4. battle_garage.png: Underground parking, grease stains, tires, UFC projector
    im = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(im)
    draw_v_gradient(d, 0, 320, (30, 36, 46), (55, 62, 75)) # Concrete garage wall
    # Yellow hazard stripes
    for hx in range(0, W, 60):
        d.polygon([(hx, 300), (hx + 25, 300), (hx + 45, 330), (hx + 20, 330)], fill=PAL['yellow'])
    draw_v_gradient(d, 330, H, (40, 44, 52), (20, 24, 30)) # Concrete floor
    # Projector Screen (UFC fight)
    d.rectangle([280, 40, 744, 280], fill=PAL['panel'], outline=PAL['cyan_hi'], width=3)
    d.ellipse([512 - 40, 160 - 30, 512 + 40, 160 + 30], fill=PAL['red_hi']) # UFC Octagon
    # Tire wall stacks on left
    for ty in range(240, 360, 28):
        for tx in range(60, 220, 45):
            d.ellipse([tx, ty, tx + 40, ty + 24], fill=PAL['ink'], outline=PAL['slate'], width=2)
    im.save(os.path.join(BG_DIR, "battle_garage.png"), "PNG")
    print("Saved battle_garage.png")

    # 5. battle_pub.png: Warm mahogany pub, vintage lighting, vinyl racks, dual turntables
    im = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(im)
    draw_v_gradient(d, 0, 340, (55, 25, 18), (85, 42, 28)) # Mahogany wainscot
    draw_v_gradient(d, 340, H, (42, 22, 14), (25, 12, 8)) # Floor
    # Vinyl record racks along wall
    d.rectangle([60, 100, 480, 320], fill=PAL['wood_dk'], outline=PAL['wood_hi'], width=2)
    for ry in range(120, 300, 55):
        d.line([60, ry, 480, ry], fill=PAL['wood_hi'], width=3)
        for vx in range(80, 460, 20):
            d.rectangle([vx, ry - 38, vx + 14, ry], fill=PAL['ink'], outline=PAL['silver'])
    # DJ Turntables booth on right
    d.rectangle([560, 220, 960, 360], fill=PAL['wood_mid'], outline=PAL['ink'], width=3)
    # 2 Vinyl platters
    d.ellipse([610, 240, 720, 310], fill=PAL['ink'], outline=PAL['silver'], width=2)
    d.ellipse([800, 240, 910, 310], fill=PAL['ink'], outline=PAL['silver'], width=2)
    # Warm pendant lamps
    for lx in [300, 760]:
        d.line([lx, 0, lx, 60], fill=PAL['ink'], width=2)
        d.polygon([(lx - 25, 90), (lx + 25, 90), (lx, 60)], fill=PAL['gold'])
        d.ellipse([lx - 120, 80, lx + 120, 240], fill=(255, 215, 100, 40)) # Warm glow
    im.save(os.path.join(BG_DIR, "battle_pub.png"), "PNG")
    print("Saved battle_pub.png")

    # 6. battle_alley.png: Moody Old Town cobblestones, sodium lamps, wet stone reflections
    im = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(im)
    draw_v_gradient(d, 0, 330, (15, 18, 30), (32, 28, 42)) # Night sky
    # Brick walls left and right
    d.rectangle([0, 40, 260, 380], fill=PAL['brick_mid'], outline=PAL['ink'], width=2)
    d.rectangle([764, 40, W, 380], fill=PAL['brick_mid'], outline=PAL['ink'], width=2)
    for by in range(50, 380, 16):
        d.line([0, by, 260, by], fill=PAL['brick_dk'])
        d.line([764, by, W, by], fill=PAL['brick_dk'])
    # Wet Cobblestone ground
    draw_v_gradient(d, 330, H, (35, 38, 48), (18, 20, 28))
    # Sodium Lamp on left wall
    d.polygon([(260, 120), (290, 140), (260, 150)], fill=PAL['sodium'])
    # Golden light puddle on wet stones
    d.ellipse([200, 340, 600, 520], fill=(255, 180, 50, 65))
    im.save(os.path.join(BG_DIR, "battle_alley.png"), "PNG")
    print("Saved battle_alley.png")

    # 7. battle_marina.png: Wooden lake pier, mooring pylons, lanterns, misty shoreline
    im = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(im)
    draw_v_gradient(d, 0, 320, (8, 20, 40), (22, 45, 75)) # Misty moonlight sky
    d.ellipse([780, 40, 860, 120], fill=PAL['white']) # Full Moon
    # Distant lake shore forest
    d.polygon([(0, 320), (W, 320), (W, 260), (500, 290), (0, 270)], fill=PAL['forest_dk'])
    # Rippling Lake Water
    draw_v_gradient(d, 320, H, (15, 35, 65), (8, 18, 35))
    # Moon reflection streak
    for my in range(325, 460, 8):
        mw = 30 + (my - 320) * 1.5
        d.line([820 - mw//2, my, 820 + mw//2, my], fill=(235, 240, 255, 90), width=2)
    # Wooden pier in foreground
    d.polygon([(0, 460), (W, 430), (W, H), (0, H)], fill=PAL['wood_mid'])
    # Mooring pylons
    d.rectangle([140, 380, 175, 480], fill=PAL['wood_dk'], outline=PAL['ink'], width=2)
    d.rectangle([860, 360, 895, 460], fill=PAL['wood_dk'], outline=PAL['ink'], width=2)
    im.save(os.path.join(BG_DIR, "battle_marina.png"), "PNG")
    print("Saved battle_marina.png")

    # 8. battle_forest.png: Forest clearing with moonlight rays filtering through pine canopies
    im = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(im)
    draw_v_gradient(d, 0, 300, (6, 18, 32), (18, 44, 38))
    # Tall pine trunks & canopies
    for tx in [80, 240, 440, 680, 880]:
        d.rectangle([tx, 0, tx + 32, 420], fill=PAL['wood_dk'])
        d.polygon([(tx - 60, 200), (tx + 16, 40), (tx + 92, 200)], fill=PAL['forest_dk'])
        d.polygon([(tx - 75, 300), (tx + 16, 120), (tx + 107, 300)], fill=PAL['forest_mid'])
    # Moonlight rays
    d.polygon([(300, 0), (450, 0), (650, 420), (400, 420)], fill=(180, 220, 240, 35))
    # Forest floor (mossy pine needles)
    draw_v_gradient(d, 380, H, (28, 52, 32), (14, 28, 18))
    im.save(os.path.join(BG_DIR, "battle_forest.png"), "PNG")
    print("Saved battle_forest.png")

    # 9. campfire.png: Chapter 7 bivouac clearing, hammocks between pines, central fire pit
    im = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(im)
    draw_v_gradient(d, 0, 280, (4, 12, 26), (15, 35, 45))
    # Stars
    for sx, sy in [(150, 40), (320, 60), (480, 25), (710, 50), (880, 35), (220, 110), (640, 95)]:
        d.point([sx, sy], fill=PAL['yellow_hi'])
    # Pine trees flanking clearing
    d.rectangle([60, 0, 110, 420], fill=PAL['wood_dk'])
    d.rectangle([914, 0, 964, 420], fill=PAL['wood_dk'])
    # Hammock strung on left
    d.line([110, 240, 280, 300, 340, 260], fill=PAL['olive_hi'], width=3)
    # Ground clearing
    draw_v_gradient(d, 360, H, (35, 58, 38), (18, 32, 20))
    # Stone campfire circle in center
    d.ellipse([W//2 - 90, 440, W//2 + 90, 510], fill=(45, 50, 55), outline=PAL['ink'], width=3)
    # Warm radiant glow from fire pit
    d.ellipse([W//2 - 280, 320, W//2 + 280, 560], fill=(246, 192, 74, 55))
    im.save(os.path.join(BG_DIR, "campfire.png"), "PNG")
    print("Saved campfire.png")

    # 10. battle_rift.png: Dimensional cosmic rift with violet nebula & energy ribbons
    im = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(im)
    draw_v_gradient(d, 0, H, (12, 6, 24), (35, 12, 55))
    # Swirling nebula clouds
    d.ellipse([200, 60, 824, 500], fill=(140, 60, 190, 80))
    d.ellipse([340, 140, 684, 420], fill=(220, 90, 240, 110))
    d.ellipse([450, 210, 574, 350], fill=PAL['white']) # Core singularity
    # Spacetime energy ribbons
    for rad in range(60, 280, 30):
        d.arc([W//2 - rad, H//2 - rad, W//2 + rad, H//2 + rad], start=20, end=200, fill=PAL['cyan_hi'], width=3)
    im.save(os.path.join(BG_DIR, "battle_rift.png"), "PNG")
    print("Saved battle_rift.png")

    # 11. sunrise.png: Golden dawn horizon over Lake Powidzkie with water beam & pine silhouettes
    im = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(im)
    # Radiant dawn gradient (dark violet -> fiery orange -> golden yellow)
    draw_v_gradient(d, 0, 180, (45, 22, 65), (185, 75, 60))
    draw_v_gradient(d, 180, 320, (185, 75, 60), (255, 210, 90))
    # Golden Rising Sun
    d.ellipse([W//2 - 60, 260, W//2 + 60, 380], fill=PAL['yellow_hi'])
    # Distant lake shore pine silhouettes
    for px in range(0, W, 14):
        ph = 30 + ((px * 17) % 25)
        d.polygon([(px, 320), (px + 7, 320 - ph), (px + 14, 320)], fill=(25, 15, 30, 255))
    # Lake Powidzkie rippling dawn water
    draw_v_gradient(d, 320, H, (215, 110, 60), (75, 35, 45))
    # Shimmering golden reflection beam down water
    for sy in range(325, H, 6):
        sw = 20 + (sy - 320) * 0.9
        d.line([W//2 - sw//2, sy, W//2 + sw//2, sy], fill=PAL['yellow_hi'], width=2)
    # Pier wood plank silhouette at bottom
    d.polygon([(0, 510), (W, 490), (W, H), (0, H)], fill=(20, 10, 15, 255))
    im.save(os.path.join(BG_DIR, "sunrise.png"), "PNG")
    print("Saved sunrise.png")

def generate_fire():
    """Campfire animated fire spritesheet: 64x80 per frame x 6 frames = 384x80."""
    print("Generating animated fire spritesheet (384x80)...")
    fw, fh = 64, 80
    sheet = Image.new("RGBA", (fw * 6, fh), (0, 0, 0, 0))
    d = ImageDraw.Draw(sheet)

    for i in range(6):
        ox = i * fw
        cx = ox + 32
        by = 72
        # Dark burning logs at base
        d.line([cx - 20, by, cx + 20, by - 4], fill=PAL['wood_dk'], width=5)
        d.line([cx - 18, by - 4, cx + 18, by + 2], fill=PAL['wood_mid'], width=4)
        d.ellipse([cx - 14, by - 6, cx + 14, by], fill=PAL['fire'])

        # Flame tongues (dancing by frame index)
        h1 = 45 + int(math.sin(i * 1.2) * 8)
        h2 = 52 + int(math.cos(i * 1.5) * 10)
        h3 = 40 + int(math.sin(i * 1.8 + 1) * 7)

        # Outer red flame
        d.polygon([(cx - 18, by - 2), (cx - 6, by - h1), (cx, by - 12), (cx + 8, by - h2), (cx + 18, by - 2)], fill=PAL['red'])
        # Mid orange flame
        d.polygon([(cx - 12, by - 4), (cx - 3, by - h1 + 8), (cx + 2, by - h2 + 6), (cx + 12, by - 4)], fill=PAL['fire'])
        # Hot yellow/white core
        d.polygon([(cx - 6, by - 6), (cx, by - h2 + 18), (cx + 6, by - 6)], fill=PAL['yellow_hi'])
        d.ellipse([cx - 4, by - 16, cx + 4, by - 6], fill=PAL['white'])

        # Rising embers
        d.point([cx - 8 + (i * 4) % 16, by - h2 - 6], fill=PAL['fire_hi'])
        d.point([cx + 6 - (i * 3) % 14, by - h1 - 10], fill=PAL['yellow_hi'])

    sheet.save(os.path.join(BG_DIR, "fire.png"), "PNG")
    print("Saved fire.png (384x80)")

def draw_32_tile(d, tx, ty, name, idx):
    """Draw a high-detail 32x32 tile at (tx, ty)."""
    ink = PAL['ink']
    
    if name == 'apartment':
        if idx == 0: # Parquet floor
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(130, 85, 55))
            d.line([tx, ty + 15, tx + 31, ty + 15], fill=(95, 60, 35), width=1)
            d.line([tx + 15, ty, tx + 15, ty + 31], fill=(95, 60, 35), width=1)
        elif idx == 1: # Wall / skirting
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(160, 175, 195))
            d.rectangle([tx, ty + 24, tx + 31, ty + 31], fill=(85, 55, 35)) # Baseboard
        elif idx == 2: # Ceiling molding
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(185, 195, 210))
            d.line([tx, ty + 30, tx + 31, ty + 30], fill=(120, 135, 150), width=2)
        elif idx == 3: # Desk
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(50, 58, 70), outline=ink)
            d.rectangle([tx + 4, ty + 4, tx + 27, ty + 22], fill=PAL['panel'], outline=PAL['cyan']) # Monitor
        elif idx == 4: # Chair
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(130, 85, 55)) # floor
            d.ellipse([tx + 4, ty + 4, tx + 27, ty + 27], fill=PAL['red'], outline=ink)
        elif idx == 5: # Carpet rug
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(70, 95, 130), outline=(120, 150, 190), width=2)
        elif idx == 6: # Bed
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(90, 105, 130), outline=ink)
            d.rectangle([tx + 4, ty + 4, tx + 27, ty + 14], fill=PAL['white'], outline=PAL['silver']) # Pillow
        elif idx == 7: # Doorway
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(60, 40, 25))
            d.rectangle([tx + 4, ty + 4, tx + 27, ty + 31], fill=PAL['panel'], outline=PAL['gold'])

    elif name == 'city':
        if idx == 0: # Asphalt road
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(42, 46, 52))
            d.line([tx + 14, ty, tx + 14, ty + 16], fill=PAL['white'], width=3) # White dashed marking
        elif idx == 1: # Concrete sidewalk
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(115, 122, 130), outline=(85, 90, 98))
            d.line([tx, ty + 15, tx + 31, ty + 15], fill=(85, 90, 98))
        elif idx in (2, 3): # Blokowisko facade & windows
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(95, 102, 112), outline=ink)
            d.rectangle([tx + 6, ty + 6, tx + 25, ty + 25], fill=(225, 215, 130) if idx==2 else (35, 42, 50), outline=ink)
        elif idx == 4: # Streetlamp
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(115, 122, 130))
            d.line([tx + 15, ty, tx + 15, ty + 31], fill=PAL['ink'], width=4)
        elif idx == 5: # Green hedge/grass
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=PAL['forest_mid'], outline=PAL['forest_dk'])
        elif idx == 6: # Żabka entrance
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=PAL['zabka_green'])
            d.rectangle([tx + 4, ty + 6, tx + 27, ty + 25], fill=PAL['zabka_yellow'], outline=ink)
        elif idx == 7: # Pedestrian zebra crosswalk
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(42, 46, 52))
            d.rectangle([tx + 4, ty, tx + 12, ty + 31], fill=PAL['white'])
            d.rectangle([tx + 20, ty, tx + 28, ty + 31], fill=PAL['white'])

    elif name == 'garage':
        if idx == 0: # Concrete floor with oil stain
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(48, 52, 60))
            d.ellipse([tx + 8, ty + 10, tx + 24, ty + 22], fill=(22, 25, 30))
        elif idx == 1: # Pillar with hazard stripes
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(80, 85, 95), outline=ink)
            d.polygon([(tx, ty + 8), (tx + 12, ty + 8), (tx + 24, ty + 24), (tx + 12, ty + 24)], fill=PAL['yellow'])
        elif idx == 2: # Pegboard tools
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=PAL['panel'], outline=ink)
            d.line([tx + 8, ty + 6, tx + 8, ty + 24], fill=PAL['silver'], width=2)
            d.line([tx + 18, ty + 6, tx + 18, ty + 24], fill=PAL['silver'], width=2)
        elif idx == 3: # Tire stack
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(48, 52, 60))
            d.ellipse([tx + 2, ty + 6, tx + 29, ty + 25], fill=PAL['ink'], outline=PAL['slate'], width=2)
        elif idx == 4: # Projector fight screen
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=PAL['panel'], outline=PAL['cyan_hi'])
            d.ellipse([tx + 10, ty + 10, tx + 21, ty + 21], fill=PAL['red_hi'])
        elif idx == 5: # Bench press barbell
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(48, 52, 60))
            d.line([tx + 2, ty + 15, tx + 29, ty + 15], fill=PAL['silver'], width=3)
        elif idx == 6: # Beer crate cooler
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(48, 52, 60))
            d.rectangle([tx + 6, ty + 8, tx + 25, ty + 24], fill=PAL['red'], outline=ink)
        elif idx == 7: # Garage shutter gate
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(70, 75, 85), outline=ink)
            for gy in range(ty + 4, ty + 30, 6):
                d.line([tx, gy, tx + 31, gy], fill=PAL['ink'])

    elif name == 'pub':
        if idx == 0: # Mahogany tavern floor
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(65, 35, 20), outline=(45, 22, 12))
            d.line([tx, ty + 15, tx + 31, ty + 15], fill=(45, 22, 12))
        elif idx == 1: # Wainscot wall
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(85, 42, 25), outline=ink)
            d.rectangle([tx + 4, ty + 4, tx + 27, ty + 27], fill=(55, 25, 15))
        elif idx == 2: # Bar counter
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(110, 55, 30), outline=ink)
            d.rectangle([tx + 12, ty + 4, tx + 19, ty + 16], fill=PAL['gold']) # Beer tap
        elif idx == 3: # Bar stool
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(65, 35, 20))
            d.ellipse([tx + 6, ty + 6, tx + 25, ty + 25], fill=PAL['red'], outline=PAL['gold'], width=2)
        elif idx == 4: # Vinyl record crate
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(65, 35, 20))
            d.rectangle([tx + 4, ty + 6, tx + 27, ty + 25], fill=PAL['wood_dk'], outline=PAL['gold'])
        elif idx == 5: # Turntable
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=PAL['wood_mid'], outline=ink)
            d.ellipse([tx + 6, ty + 6, tx + 25, ty + 25], fill=PAL['ink'], outline=PAL['silver'], width=2)
        elif idx == 6: # Booth seat
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(95, 30, 25), outline=ink)
        elif idx == 7: # Dartboard
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(85, 42, 25))
            d.ellipse([tx + 6, ty + 6, tx + 25, ty + 25], fill=PAL['ink'], outline=PAL['red'], width=2)

    elif name == 'alley':
        if idx == 0: # Wet cobblestones
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(42, 45, 55), outline=(28, 30, 38))
            d.line([tx + 6, ty + 10, tx + 24, ty + 10], fill=(70, 80, 100)) # Wet highlight
        elif idx == 1: # Red brick wall
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=PAL['brick_mid'], outline=ink)
            d.line([tx, ty + 15, tx + 31, ty + 15], fill=PAL['brick_dk'])
        elif idx == 2: # Sodium lamp bracket
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=PAL['brick_mid'])
            d.ellipse([tx + 8, ty + 8, tx + 23, ty + 23], fill=PAL['sodium'])
        elif idx == 3: # Trash dumpster
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(42, 45, 55))
            d.rectangle([tx + 4, ty + 6, tx + 27, ty + 26], fill=PAL['steel'], outline=ink)
        elif idx == 4: # Fire escape stairs
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=PAL['brick_mid'])
            d.line([tx, ty + 28, tx + 31, ty + 4], fill=PAL['ink'], width=3)
        elif idx == 5: # Cellar club doors
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(35, 38, 45), outline=PAL['steel'], width=2)
        elif idx == 6: # Wooden pallet
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(42, 45, 55))
            d.rectangle([tx + 4, ty + 8, tx + 27, ty + 24], fill=PAL['wood_mid'], outline=ink)
        elif idx == 7: # Neon arrow
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=PAL['brick_mid'])
            d.polygon([(tx + 6, ty + 15), (tx + 22, ty + 6), (tx + 22, ty + 24)], fill=PAL['cyan_hi'])

    elif name == 'marina':
        if idx == 0: # Wooden pier planks
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(85, 60, 40), outline=(55, 38, 24))
            d.line([tx, ty + 15, tx + 31, ty + 15], fill=(55, 38, 24))
        elif idx == 1: # Rippling lake water
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(18, 42, 75))
            d.line([tx + 4, ty + 10, tx + 26, ty + 10], fill=PAL['cyan'], width=2)
        elif idx == 2: # Mooring pylon
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(85, 60, 40))
            d.ellipse([tx + 8, ty + 8, tx + 23, tx + 23], fill=PAL['wood_dk'], outline=ink)
        elif idx == 3: # Lifebuoy station
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(85, 60, 40))
            d.ellipse([tx + 6, ty + 6, tx + 25, ty + 25], fill=PAL['red_hi'], outline=PAL['white'], width=3)
        elif idx == 4: # Rowing boat
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(18, 42, 75))
            d.ellipse([tx + 4, ty + 8, tx + 27, ty + 24], fill=PAL['wood_mid'], outline=ink)
        elif idx == 5: # Reeds / Cattails
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(18, 42, 75))
            d.line([tx + 10, ty + 28, tx + 10, ty + 4], fill=PAL['olive_hi'], width=2)
            d.line([tx + 20, ty + 28, tx + 20, ty + 8], fill=PAL['olive_hi'], width=2)
        elif idx == 6: # Lantern post
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(85, 60, 40))
            d.ellipse([tx + 10, ty + 6, tx + 21, ty + 18], fill=PAL['yellow_hi'])
        elif idx == 7: # Pier bench
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(85, 60, 40))
            d.rectangle([tx + 4, ty + 10, tx + 27, ty + 22], fill=PAL['wood_dk'], outline=ink)

    elif name == 'forest':
        if idx == 0: # Mossy forest trail
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(45, 32, 22), outline=(32, 22, 14))
            d.point([tx + 8, ty + 12], fill=PAL['forest_mid'])
            d.point([tx + 22, ty + 20], fill=PAL['forest_mid'])
        elif idx == 1: # Dense ancient pine tree trunk
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=PAL['wood_dk'], outline=ink)
            d.rectangle([tx + 4, ty, tx + 27, ty + 31], fill=PAL['forest_dk'])
        elif idx == 2: # Fern / undergrowth
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(45, 32, 22))
            d.polygon([(tx + 6, ty + 26), (tx + 16, ty + 6), (tx + 26, ty + 26)], fill=PAL['forest_hi'])
        elif idx == 3: # Wild brambles
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(45, 32, 22))
            d.ellipse([tx + 6, ty + 8, tx + 25, ty + 24], fill=PAL['forest_mid'])
            d.point([tx + 12, ty + 14], fill=PAL['red'])
            d.point([tx + 18, ty + 16], fill=PAL['red'])
        elif idx == 4: # Campfire stone ring
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(45, 32, 22))
            d.ellipse([tx + 4, ty + 6, tx + 27, ty + 26], fill=(55, 60, 68), outline=ink, width=2)
            d.ellipse([tx + 10, ty + 12, tx + 21, ty + 20], fill=PAL['fire'])
        elif idx == 5: # Split log bench
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(45, 32, 22))
            d.rectangle([tx + 2, ty + 10, tx + 29, ty + 22], fill=PAL['wood_mid'], outline=ink)
        elif idx == 6: # Hammock post
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(45, 32, 22))
            d.line([tx + 15, ty, tx + 15, ty + 31], fill=PAL['wood_dk'], width=4)
        elif idx == 7: # Clearing exit
            d.rectangle([tx, ty, tx + 31, ty + 31], fill=(55, 78, 45), outline=PAL['forest_hi'])

def generate_tilesets():
    print("Generating 32x32 tilesets...")
    sets = ['apartment', 'city', 'garage', 'pub', 'alley', 'marina', 'forest']
    for sname in sets:
        # 8 tiles per row (256x32)
        sheet = Image.new("RGBA", (256, 32), (0, 0, 0, 0))
        d = ImageDraw.Draw(sheet)
        for idx in range(8):
            draw_32_tile(d, idx * 32, 0, sname, idx)
        out_path = os.path.join(TILES_DIR, f"{sname}.png")
        sheet.save(out_path, "PNG")
        print(f"Saved tileset {out_path} ({sheet.size})")

def update_manifest():
    manifest_path = os.path.join(ASSETS, "manifest.json")
    manifest = {
        "resolution": { "width": W, "height": H, "tile": 32 },
        "images": {
            "title_bg": "assets/bg/title.png",
            "campfire_bg": "assets/bg/campfire.png",
            "battle_apartment_bg": "assets/bg/battle_apartment.png",
            "battle_city_bg": "assets/bg/battle_city.png",
            "battle_garage_bg": "assets/bg/battle_garage.png",
            "battle_pub_bg": "assets/bg/battle_pub.png",
            "battle_alley_bg": "assets/bg/battle_alley.png",
            "battle_marina_bg": "assets/bg/battle_marina.png",
            "battle_forest_bg": "assets/bg/battle_forest.png",
            "battle_rift_bg": "assets/bg/battle_rift.png",
            "sunrise_bg": "assets/bg/sunrise.png",
            "analyzer_bg": "assets/bg/analyzer_bg.png",
            "tiles_apartment": "assets/tiles/apartment.png",
            "tiles_city": "assets/tiles/city.png",
            "tiles_garage": "assets/tiles/garage.png",
            "tiles_pub": "assets/tiles/pub.png",
            "tiles_alley": "assets/tiles/alley.png",
            "tiles_marina": "assets/tiles/marina.png",
            "tiles_forest": "assets/tiles/forest.png",
            "thumb_group": "assets/ui/thumb_group.png",
            "thumb_travel": "assets/ui/thumb_travel.png",
            "thumb_funny": "assets/ui/thumb_funny.png",
            "thumb_moments": "assets/ui/thumb_moments.png",
        },
        "spritesheets": {
            "fire": { "path": "assets/bg/fire.png", "frameWidth": 64, "frameHeight": 80 },
            "enemy_bolKregoslupa": { "path": "assets/enemies/bolKregoslupa.png", "frameWidth": 96, "frameHeight": 96 },
            "enemy_slacki": { "path": "assets/enemies/slacki.png", "frameWidth": 96, "frameHeight": 96 },
            "enemy_sasiadSzkodnik": { "path": "assets/enemies/sasiadSzkodnik.png", "frameWidth": 128, "frameHeight": 128 },
            "enemy_autoTuneHipster": { "path": "assets/enemies/autoTuneHipster.png", "frameWidth": 96, "frameHeight": 96 },
            "enemy_drogiePiwo": { "path": "assets/enemies/drogiePiwo.png", "frameWidth": 96, "frameHeight": 96 },
            "enemy_kark": { "path": "assets/enemies/kark.png", "frameWidth": 128, "frameHeight": 128 },
            "enemy_straznik": { "path": "assets/enemies/straznik.png", "frameWidth": 96, "frameHeight": 96 },
            "enemy_panJanusz": { "path": "assets/enemies/panJanusz.png", "frameWidth": 128, "frameHeight": 128 },
            "enemy_kredyt": { "path": "assets/enemies/kredyt.png", "frameWidth": 128, "frameHeight": 128 },
            "enemy_audyt": { "path": "assets/enemies/audyt.png", "frameWidth": 128, "frameHeight": 128 },
            "enemy_rwaKulszowa": { "path": "assets/enemies/rwaKulszowa.png", "frameWidth": 96, "frameHeight": 96 },
        }
    }
    for hid in ['danny', 'alior', 'lisu', 'barti', 'oziem', 'luki']:
        manifest["spritesheets"][f"{hid}_walk"] = { "path": f"assets/sprites/{hid}_walk.png", "frameWidth": 32, "frameHeight": 48 }
        manifest["spritesheets"][f"{hid}_battle"] = { "path": f"assets/sprites/{hid}_battle.png", "frameWidth": 64, "frameHeight": 80 }
        manifest["spritesheets"][f"{hid}_sit"] = { "path": f"assets/sprites/{hid}_sit.png", "frameWidth": 32, "frameHeight": 32 }
        manifest["images"][f"portrait_{hid}_128"] = f"assets/portraits/{hid}_128.png"
        manifest["images"][f"portrait_{hid}_96"] = f"assets/portraits/{hid}_96.png"
        manifest["images"][f"portrait_{hid}_64"] = f"assets/portraits/{hid}_64.png"
        manifest["images"][f"card_{hid}"] = f"assets/cards/{hid}.png"

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print("Updated manifest.json")

def main():
    generate_backgrounds()
    generate_fire()
    generate_tilesets()
    update_manifest()
    print("All HD environments, tilesets, and backgrounds created successfully!")

if __name__ == "__main__":
    main()
