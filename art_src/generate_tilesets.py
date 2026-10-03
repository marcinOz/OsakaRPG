#!/usr/bin/env python3
"""generate_tilesets.py - High-Detail 32x32 Overworld Tilesets (8 tiles x 32px = 256x32 RGBA).
Generates authentic pixel art tilesets for:
1. apartment.png
2. city.png
3. garage.png
4. pub.png
5. alley.png
6. marina.png
7. forest.png
"""
import os
import math
from PIL import Image, ImageDraw

OUT_DIR = "public/assets/tiles"
os.makedirs(OUT_DIR, exist_ok=True)

DARK_PLUM = (24, 16, 22, 255)

def save_tileset(name, tiles):
    sheet = Image.new("RGBA", (256, 32), (0, 0, 0, 0))
    for i, t in enumerate(tiles):
        sheet.paste(t, (i * 32, 0))
    path = os.path.join(OUT_DIR, f"{name}.png")
    sheet.save(path, "PNG")
    print(f"Generated {name}.png: {sheet.size}")

# ============================================================================
# 1. APARTMENT TILESET
# ============================================================================
def build_apartment():
    tiles = []
    # Tile 0: Parquet wood floor planks with fine grain and varnish highlight
    t0 = Image.new("RGBA", (32, 32), (185, 125, 75, 255))
    d0 = ImageDraw.Draw(t0)
    for y in range(0, 32, 8):
        d0.line([(0, y), (32, y)], fill=(130, 80, 45, 255))
        # Alternating wood planks
        for x in range((y % 16), 32, 16):
            d0.line([(x, y), (x, y + 8)], fill=(130, 80, 45, 255))
            # Plank wood grain highlight
            d0.line([(x + 2, y + 2), (x + 14, y + 2)], fill=(215, 155, 95, 180))
            d0.line([(x + 4, y + 5), (x + 12, y + 5)], fill=(160, 105, 60, 180))
    tiles.append(t0)

    # Tile 1: Apartment wall (cream plaster with wooden baseboard)
    t1 = Image.new("RGBA", (32, 32), (210, 205, 195, 255))
    d1 = ImageDraw.Draw(t1)
    # Subtle wallpaper pinstripes
    for x in range(4, 32, 8):
        d1.line([(x, 0), (x, 24)], fill=(195, 190, 180, 255))
    # Baseboard at bottom
    d1.rectangle([0, 24, 32, 32], fill=(120, 75, 45, 255), outline=(80, 45, 25, 255))
    d1.line([(0, 25), (32, 25)], fill=(160, 105, 65, 255))
    tiles.append(t1)

    # Tile 2: Wall top & ceiling moulding
    t2 = Image.new("RGBA", (32, 32), (210, 205, 195, 255))
    d2 = ImageDraw.Draw(t2)
    d2.rectangle([0, 0, 32, 8], fill=(235, 235, 230, 255), outline=(160, 160, 160, 255))
    d2.line([(0, 8), (32, 8)], fill=(140, 135, 130, 255))
    tiles.append(t2)

    # Tile 3: Dual-monitor gaming desk
    t3 = t0.copy()
    d3 = ImageDraw.Draw(t3)
    # Desk surface
    d3.rectangle([2, 12, 30, 30], fill=(65, 45, 35, 255), outline=DARK_PLUM)
    d3.line([(2, 13), (30, 13)], fill=(110, 80, 65, 255))
    # Dual glowing monitors
    d3.rectangle([3, 2, 16, 14], fill=(20, 25, 35, 255), outline=DARK_PLUM)
    d3.rectangle([5, 4, 14, 12], fill=(60, 140, 220, 255)) # screen 1
    d3.rectangle([16, 2, 29, 14], fill=(20, 25, 35, 255), outline=DARK_PLUM)
    d3.rectangle([18, 4, 27, 12], fill=(80, 220, 140, 255)) # screen 2
    tiles.append(t3)

    # Tile 4: Gaming chair / desk lower part
    t4 = t0.copy()
    d4 = ImageDraw.Draw(t4)
    # Gaming chair
    d4.rectangle([8, 4, 24, 24], fill=(30, 32, 40, 255), outline=DARK_PLUM)
    d4.line([(10, 6), (22, 6)], fill=(225, 40, 50, 255), width=2) # red racing stripe
    d4.line([(10, 14), (22, 14)], fill=(225, 40, 50, 255), width=2)
    # Caster wheels
    d4.line([(8, 26), (24, 26)], fill=(50, 55, 65, 255), width=2)
    tiles.append(t4)

    # Tile 5: Cozy bed with blanket
    t5 = t0.copy()
    d5 = ImageDraw.Draw(t5)
    # Bed frame
    d5.rectangle([2, 4, 30, 28], fill=(130, 85, 55, 255), outline=DARK_PLUM)
    # Soft pillow
    d5.rounded_rectangle([4, 6, 14, 16], radius=3, fill=(245, 245, 250, 255), outline=(180, 185, 195, 255))
    # Crumpled duvet blanket
    d5.rounded_rectangle([12, 6, 28, 26], radius=3, fill=(90, 130, 180, 255), outline=(50, 80, 120, 255))
    d5.line([(16, 12), (24, 18)], fill=(130, 175, 225, 255), width=2) # fold highlight
    tiles.append(t5)

    # Tile 6: Monstera plant in terracotta pot
    t6 = t0.copy()
    d6 = ImageDraw.Draw(t6)
    # Terracotta pot
    d6.polygon([(10, 18), (22, 18), (20, 30), (12, 30)], fill=(195, 85, 50, 255), outline=DARK_PLUM)
    d6.line([(9, 18), (23, 18)], fill=(225, 115, 75, 255), width=2)
    # Lush split monstera leaves
    leaves = [(16, 6), (8, 12), (24, 10), (12, 16), (20, 16)]
    for lx, ly in leaves:
        d6.ellipse([lx - 5, ly - 4, lx + 5, ly + 4], fill=(45, 135, 60, 255), outline=(20, 70, 30, 255))
        d6.point((lx, ly), fill=(80, 185, 95, 255))
    tiles.append(t6)

    # Tile 7: Entryway doormat / exit
    t7 = t0.copy()
    d7 = ImageDraw.Draw(t7)
    d7.rounded_rectangle([4, 6, 28, 26], radius=2, fill=(160, 110, 60, 255), outline=DARK_PLUM)
    d7.text((8, 11), "EXIT", fill=(240, 210, 150, 255))
    tiles.append(t7)

    save_tileset("apartment", tiles)

# ============================================================================
# 2. CITY TILESET
# ============================================================================
def build_city():
    tiles = []
    # Tile 0: Dark asphalt road with lane markings
    t0 = Image.new("RGBA", (32, 32), (48, 52, 60, 255))
    d0 = ImageDraw.Draw(t0)
    # Subtle asphalt gravel grain
    for y in range(0, 32, 4):
        for x in range(0, 32, 4):
            if (x * 7 + y * 13) % 5 == 0:
                d0.point((x + 1, y + 1), fill=(65, 70, 80, 255))
            elif (x * 11 + y * 3) % 7 == 0:
                d0.point((x + 2, y + 2), fill=(35, 38, 44, 255))
    # Dashed center line
    d0.line([(14, 8), (18, 8)], fill=(240, 240, 245, 255), width=2)
    d0.line([(14, 24), (18, 24)], fill=(240, 240, 245, 255), width=2)
    tiles.append(t0)

    # Tile 1: Sidewalk pavers
    t1 = Image.new("RGBA", (32, 32), (160, 165, 175, 255))
    d1 = ImageDraw.Draw(t1)
    for y in range(0, 32, 8):
        d1.line([(0, y), (32, y)], fill=(110, 115, 125, 255))
        for x in range((y % 16), 32, 16):
            d1.line([(x, y), (x, y + 8)], fill=(110, 115, 125, 255))
            d1.line([(x + 1, y + 1), (x + 15, y + 1)], fill=(195, 200, 210, 255))
    tiles.append(t1)

    # Tile 2: Tenement brick building wall
    t2 = Image.new("RGBA", (32, 32), (150, 65, 50, 255))
    d2 = ImageDraw.Draw(t2)
    for y in range(0, 32, 6):
        d2.line([(0, y), (32, y)], fill=(80, 35, 25, 255))
        for x in range((y % 12), 32, 12):
            d2.line([(x, y), (x, y + 6)], fill=(80, 35, 25, 255))
            d2.point((x + 3, y + 2), fill=(185, 95, 75, 255))
    tiles.append(t2)

    # Tile 3: Tenement window with warm interior glow
    t3 = t2.copy()
    d3 = ImageDraw.Draw(t3)
    d3.rectangle([6, 4, 26, 26], fill=(255, 220, 100, 255), outline=(40, 20, 15, 255))
    d3.line([(16, 4), (16, 26)], fill=(40, 20, 15, 255), width=2)
    d3.line([(6, 15), (26, 15)], fill=(40, 20, 15, 255), width=2)
    # Curtain silhouette
    d3.polygon([(6, 4), (12, 4), (6, 16)], fill=(180, 80, 50, 255))
    tiles.append(t3)

    # Tile 4: Concrete curb transition
    t4 = Image.new("RGBA", (32, 32), (48, 52, 60, 255)) # road top
    d4 = ImageDraw.Draw(t4)
    d4.rectangle([0, 0, 32, 14], fill=(160, 165, 175, 255)) # sidewalk
    d4.rectangle([0, 14, 32, 20], fill=(195, 200, 210, 255), outline=(100, 105, 115, 255)) # granite curb
    tiles.append(t4)

    # Tile 5: Żabka store green neon sign & shop window
    t5 = t2.copy()
    d5 = ImageDraw.Draw(t5)
    # Bright green neon signboard
    d5.rectangle([2, 4, 30, 16], fill=(15, 140, 45, 255), outline=(220, 255, 200, 255))
    # Żabka frog smile logo
    d5.arc([10, 6, 22, 14], 0, 180, fill=(240, 255, 220, 255), width=2)
    d5.point((12, 8), fill=(240, 255, 220, 255))
    d5.point((20, 8), fill=(240, 255, 220, 255))
    # Shop window
    d5.rectangle([4, 18, 28, 30], fill=(180, 235, 210, 200), outline=(20, 50, 30, 255))
    tiles.append(t5)

    # Tile 6: Cast-iron streetlamp with warm sodium glow
    t6 = t1.copy()
    d6 = ImageDraw.Draw(t6)
    # Warm glow halo
    d6.ellipse([4, 0, 28, 24], fill=(255, 210, 80, 80))
    # Cast iron post
    d6.line([(16, 8), (16, 30)], fill=(25, 28, 35, 255), width=3)
    d6.ellipse([12, 28, 20, 31], fill=(25, 28, 35, 255)) # base
    # Lamp head
    d6.polygon([(11, 8), (21, 8), (18, 2), (14, 2)], fill=(25, 28, 35, 255))
    d6.rectangle([13, 5, 19, 8], fill=(255, 240, 120, 255))
    tiles.append(t6)

    # Tile 7: Crosswalk / exit transition
    t7 = t0.copy()
    d7 = ImageDraw.Draw(t7)
    for x in range(2, 32, 8):
        d7.rectangle([x, 4, x + 4, 28], fill=(245, 245, 250, 255))
    tiles.append(t7)

    save_tileset("city", tiles)

# ============================================================================
# 3. GARAGE TILESET
# ============================================================================
def build_garage():
    tiles = []
    # Tile 0: Stained concrete with oil slick
    t0 = Image.new("RGBA", (32, 32), (85, 90, 95, 255))
    d0 = ImageDraw.Draw(t0)
    # Expansion joints
    d0.line([(0, 31), (32, 31)], fill=(55, 58, 62, 255))
    d0.line([(31, 0), (31, 32)], fill=(55, 58, 62, 255))
    # Rainbow iridescent oil slick
    d0.ellipse([8, 8, 24, 22], fill=(45, 45, 50, 240))
    d0.arc([10, 10, 22, 20], 30, 210, fill=(120, 50, 160, 200), width=2)
    d0.arc([11, 11, 21, 19], 60, 240, fill=(40, 160, 180, 200), width=2)
    tiles.append(t0)

    # Tile 1: Concrete wall with electrical conduit pipe
    t1 = Image.new("RGBA", (32, 32), (110, 115, 120, 255))
    d1 = ImageDraw.Draw(t1)
    # Stains
    d1.line([(0, 30), (32, 30)], fill=(65, 70, 75, 255), width=2)
    # Metal conduit pipe
    d1.line([(0, 12), (32, 12)], fill=(160, 165, 170, 255), width=3)
    d1.line([(0, 11), (32, 11)], fill=(210, 215, 220, 255), width=1)
    d1.rectangle([14, 8, 18, 16], fill=(90, 95, 100, 255)) # junction box
    tiles.append(t1)

    # Tile 2: Concrete ceiling with fluorescent light fixture
    t2 = t1.copy()
    d2 = ImageDraw.Draw(t2)
    d2.rectangle([4, 4, 28, 12], fill=(70, 75, 80, 255), outline=DARK_PLUM)
    d2.rectangle([6, 6, 26, 10], fill=(240, 250, 255, 255)) # tube
    tiles.append(t2)

    # Tile 3: Stacked tires
    t3 = t0.copy()
    d3 = ImageDraw.Draw(t3)
    for ty in [18, 10, 2]:
        d3.ellipse([6, ty, 26, ty + 10], fill=(25, 28, 32, 255), outline=DARK_PLUM)
        d3.ellipse([10, ty + 2, 22, ty + 8], fill=(50, 55, 62, 255))
        d3.ellipse([13, ty + 3, 19, ty + 7], fill=(15, 18, 20, 255))
    tiles.append(t3)

    # Tile 4: Red industrial tool chest
    t4 = t0.copy()
    d4 = ImageDraw.Draw(t4)
    d4.rectangle([4, 6, 28, 28], fill=(185, 35, 30, 255), outline=DARK_PLUM)
    for dy in range(10, 26, 5):
        d4.line([(6, dy), (26, dy)], fill=(120, 20, 20, 255))
        d4.line([(12, dy - 2), (20, dy - 2)], fill=(225, 225, 235, 255)) # handle
    tiles.append(t4)

    # Tile 5: Beer fridge with glowing glass door
    t5 = t0.copy()
    d5 = ImageDraw.Draw(t5)
    d5.rectangle([4, 4, 28, 28], fill=(35, 40, 48, 255), outline=DARK_PLUM)
    d5.rectangle([6, 6, 26, 26], fill=(80, 180, 220, 180), outline=(20, 25, 30, 255))
    # Beer cans on shelves
    for sy in [12, 18, 24]:
        d5.line([(7, sy), (25, sy)], fill=(180, 190, 200, 255))
        for bx in [9, 14, 19, 23]:
            d5.rectangle([bx - 1, sy - 4, bx + 1, sy], fill=(220, 40, 40, 255))
    tiles.append(t5)

    # Tile 6: Projector screen displaying UFC fight
    t6 = t1.copy()
    d6 = ImageDraw.Draw(t6)
    d6.rectangle([2, 4, 30, 26], fill=(220, 235, 250, 255), outline=DARK_PLUM)
    # Octagon cage lines
    d6.polygon([(8, 8), (24, 8), (28, 22), (4, 22)], outline=(60, 80, 100, 255))
    # 2 fighters pixelated
    d6.point((12, 14), fill=(210, 60, 60, 255))
    d6.point((20, 14), fill=(60, 100, 210, 255))
    tiles.append(t6)

    # Tile 7: Garage exit door
    t7 = t0.copy()
    d7 = ImageDraw.Draw(t7)
    d7.rectangle([4, 2, 28, 30], fill=(70, 75, 85, 255), outline=DARK_PLUM)
    for gy in range(4, 28, 4):
        d7.line([(6, gy), (26, gy)], fill=(45, 50, 58, 255))
    tiles.append(t7)

    save_tileset("garage", tiles)

# ============================================================================
# 4. PUB TILESET
# ============================================================================
def build_pub():
    tiles = []
    # Tile 0: Mahogany floorboards with amber reflection
    t0 = Image.new("RGBA", (32, 32), (95, 45, 25, 255))
    d0 = ImageDraw.Draw(t0)
    for y in range(0, 32, 8):
        d0.line([(0, y), (32, y)], fill=(60, 25, 12, 255))
        for x in range((y % 16), 32, 16):
            d0.line([(x, y), (x, y + 8)], fill=(60, 25, 12, 255))
            d0.line([(x + 2, y + 2), (x + 14, y + 2)], fill=(145, 75, 40, 220))
    tiles.append(t0)

    # Tile 1: Dark wood panel wall
    t1 = Image.new("RGBA", (32, 32), (65, 30, 18, 255))
    d1 = ImageDraw.Draw(t1)
    for x in range(0, 32, 8):
        d1.rectangle([x + 1, 2, x + 7, 28], fill=(85, 40, 22, 255), outline=(40, 18, 10, 255))
    tiles.append(t1)

    # Tile 2: Ceiling with amber hanging lamp
    t2 = t1.copy()
    d2 = ImageDraw.Draw(t2)
    d2.line([(16, 0), (16, 12)], fill=(30, 20, 15, 255), width=2)
    d2.ellipse([10, 12, 22, 24], fill=(255, 180, 40, 240), outline=(120, 50, 15, 255))
    d2.ellipse([13, 15, 19, 21], fill=(255, 245, 180, 255))
    tiles.append(t2)

    # Tile 3: Bar counter with brass footrail
    t3 = t0.copy()
    d3 = ImageDraw.Draw(t3)
    d3.rectangle([0, 6, 32, 24], fill=(120, 55, 30, 255), outline=DARK_PLUM)
    d3.line([(0, 7), (32, 7)], fill=(175, 95, 55, 255), width=2) # bar top highlight
    # Brass footrail at bottom
    d3.line([(0, 27), (32, 27)], fill=(225, 190, 55, 255), width=3)
    d3.line([(0, 26), (32, 26)], fill=(255, 235, 140, 255), width=1)
    tiles.append(t3)

    # Tile 4: Brass draft beer taps
    t4 = t3.copy()
    d4 = ImageDraw.Draw(t4)
    # Draft beer tower
    d4.rectangle([10, 0, 22, 12], fill=(215, 175, 45, 255), outline=DARK_PLUM)
    # 2 Tap handles
    d4.line([(13, 0), (13, 6)], fill=(25, 25, 25, 255), width=2)
    d4.line([(19, 0), (19, 6)], fill=(25, 25, 25, 255), width=2)
    tiles.append(t4)

    # Tile 5: Shelves packed with vinyl records
    t5 = t1.copy()
    d5 = ImageDraw.Draw(t5)
    for sy in [10, 22]:
        d5.line([(0, sy), (32, sy)], fill=(120, 60, 30, 255), width=2)
        # Colorful vinyl record sleeves stacked vertically
        colors = [(220, 60, 60), (60, 140, 220), (230, 200, 50), (60, 200, 100), (220, 120, 40), (180, 80, 200)]
        for vx in range(2, 30, 4):
            c = colors[(vx // 4) % len(colors)]
            d5.line([(vx, sy - 8), (vx, sy - 1)], fill=c, width=3)
    tiles.append(t5)

    # Tile 6: Dual turntables
    t6 = t3.copy()
    d6 = ImageDraw.Draw(t6)
    # Turntable 1
    d6.rectangle([2, 4, 15, 18], fill=(30, 32, 38, 255), outline=DARK_PLUM)
    d6.ellipse([4, 6, 13, 15], fill=(15, 16, 20, 255), outline=(80, 85, 95, 255))
    # Turntable 2
    d6.rectangle([17, 4, 30, 18], fill=(30, 32, 38, 255), outline=DARK_PLUM)
    d6.ellipse([19, 6, 28, 15], fill=(15, 16, 20, 255), outline=(80, 85, 95, 255))
    # Blue needle target light
    d6.point((6, 7), fill=(60, 180, 255, 255))
    d6.point((21, 7), fill=(60, 180, 255, 255))
    tiles.append(t6)

    # Tile 7: Pub Exit
    t7 = t0.copy()
    d7 = ImageDraw.Draw(t7)
    d7.rectangle([4, 2, 28, 28], fill=(45, 22, 14, 255), outline=DARK_PLUM)
    d7.rectangle([8, 6, 24, 14], fill=(20, 160, 60, 255), outline=(180, 255, 200, 255))
    d7.text((10, 8), "EXIT", fill=(255, 255, 255, 255))
    tiles.append(t7)

    save_tileset("pub", tiles)

# ============================================================================
# 5. ALLEY TILESET
# ============================================================================
def build_alley():
    tiles = []
    # Tile 0: Wet cobblestones with puddle reflection
    t0 = Image.new("RGBA", (32, 32), (60, 62, 70, 255))
    d0 = ImageDraw.Draw(t0)
    for y in range(0, 32, 8):
        d0.line([(0, y), (32, y)], fill=(35, 36, 42, 255))
        for x in range((y % 16), 32, 16):
            d0.line([(x, y), (x, y + 8)], fill=(35, 36, 42, 255))
            d0.line([(x + 2, y + 2), (x + 14, y + 2)], fill=(85, 90, 100, 255))
    # Rain puddle
    d0.ellipse([8, 10, 24, 22], fill=(40, 55, 75, 230), outline=(80, 110, 140, 255))
    d0.line([(11, 14), (21, 14)], fill=(140, 180, 220, 200)) # sky reflection
    tiles.append(t0)

    # Tile 1: Aged red brick wall with subtle graffiti tag
    t1 = Image.new("RGBA", (32, 32), (135, 55, 45, 255))
    d1 = ImageDraw.Draw(t1)
    for y in range(0, 32, 6):
        d1.line([(0, y), (32, y)], fill=(75, 30, 25, 255))
        for x in range((y % 12), 32, 12):
            d1.line([(x, y), (x, y + 6)], fill=(75, 30, 25, 255))
    # Graffiti tag
    d1.line([(6, 14), (12, 22), (18, 14)], fill=(60, 220, 240, 240), width=2)
    tiles.append(t1)

    # Tile 2: Brick wall cornice & fire escape ladder
    t2 = t1.copy()
    d2 = ImageDraw.Draw(t2)
    d2.rectangle([0, 0, 32, 8], fill=(95, 100, 110, 255), outline=DARK_PLUM)
    # Iron fire escape ladder
    d2.line([(10, 8), (10, 32)], fill=(30, 32, 36, 255), width=2)
    d2.line([(22, 8), (22, 32)], fill=(30, 32, 36, 255), width=2)
    for ly in range(12, 32, 6):
        d2.line([(10, ly), (22, ly)], fill=(30, 32, 36, 255), width=2)
    tiles.append(t2)

    # Tile 3: Steel industrial dumpster
    t3 = t0.copy()
    d3 = ImageDraw.Draw(t3)
    d3.polygon([(3, 10), (29, 10), (27, 28), (5, 28)], fill=(75, 95, 75, 255), outline=DARK_PLUM)
    # Rust patches
    d3.polygon([(5, 18), (12, 18), (10, 24), (5, 22)], fill=(140, 70, 35, 255))
    # Slanted plastic lid
    d3.polygon([(2, 8), (30, 8), (28, 12), (4, 12)], fill=(35, 45, 40, 255), outline=DARK_PLUM)
    tiles.append(t3)

    # Tile 4: Cast iron streetlamp with warm sodium glow
    t4 = t0.copy()
    d4 = ImageDraw.Draw(t4)
    d4.ellipse([4, 0, 28, 24], fill=(255, 180, 40, 80)) # glow
    d4.line([(16, 6), (16, 28)], fill=(30, 32, 38, 255), width=3)
    d4.polygon([(12, 6), (20, 6), (18, 0), (14, 0)], fill=(30, 32, 38, 255))
    d4.rectangle([13, 4, 19, 7], fill=(255, 220, 80, 255))
    tiles.append(t4)

    # Tile 5: Stacked wooden cargo crates
    t5 = t0.copy()
    d5 = ImageDraw.Draw(t5)
    d5.rectangle([4, 8, 28, 28], fill=(150, 100, 55, 255), outline=DARK_PLUM)
    d5.line([(4, 8), (28, 28)], fill=(95, 60, 30, 255), width=2)
    d5.line([(28, 8), (4, 28)], fill=(95, 60, 30, 255), width=2)
    tiles.append(t5)

    # Tile 6: Drainage gutter with iron grate
    t6 = t0.copy()
    d6 = ImageDraw.Draw(t6)
    d6.rectangle([4, 6, 28, 26], fill=(25, 28, 35, 255), outline=(70, 75, 85, 255))
    for gx in range(6, 28, 4):
        d6.line([(gx, 8), (gx, 24)], fill=(90, 95, 105, 255), width=2)
    tiles.append(t6)

    # Tile 7: Brick archway exit
    t7 = t0.copy()
    d7 = ImageDraw.Draw(t7)
    d7.ellipse([2, 0, 30, 30], fill=(15, 18, 24, 255), outline=(135, 55, 45, 255))
    tiles.append(t7)

    save_tileset("alley", tiles)

# ============================================================================
# 6. MARINA TILESET
# ============================================================================
def build_marina():
    tiles = []
    # Tile 0: Weathered wooden pier boardwalk with iron nails
    t0 = Image.new("RGBA", (32, 32), (135, 95, 65, 255))
    d0 = ImageDraw.Draw(t0)
    for y in range(0, 32, 8):
        d0.line([(0, y), (32, y)], fill=(80, 52, 32, 255))
        d0.line([(0, y + 1), (32, y + 1)], fill=(175, 130, 95, 220)) # edge highlight
        # Iron nails
        d0.point((4, y + 4), fill=(35, 30, 28, 255))
        d0.point((28, y + 4), fill=(35, 30, 28, 255))
    tiles.append(t0)

    # Tile 1: Deep translucent lake water with ripples
    t1 = Image.new("RGBA", (32, 32), (32, 58, 88, 255))
    d1 = ImageDraw.Draw(t1)
    for y in range(2, 32, 6):
        d1.arc([(y % 8), y, 20 + (y % 8), y + 6], 180, 360, fill=(65, 115, 165, 220), width=1)
        d1.line([(2 + (y % 12), y + 1), (8 + (y % 12), y + 1)], fill=(130, 195, 240, 180))
    tiles.append(t1)

    # Tile 2: Pier edge with bumper beam & water
    t2 = t1.copy()
    d2 = ImageDraw.Draw(t2)
    # Pier wood top
    d2.rectangle([0, 0, 32, 16], fill=(135, 95, 65, 255), outline=DARK_PLUM)
    d2.rectangle([0, 16, 32, 22], fill=(90, 60, 40, 255), outline=DARK_PLUM) # dark side fascia
    tiles.append(t2)

    # Tile 3: Vertical mooring bollard post with coiled rope
    t3 = t0.copy()
    d3 = ImageDraw.Draw(t3)
    # Post
    d3.rectangle([10, 4, 22, 24], fill=(95, 65, 42, 255), outline=DARK_PLUM)
    d3.line([(12, 4), (12, 24)], fill=(155, 115, 80, 255))
    # Coiled rope around post
    d3.ellipse([6, 14, 26, 22], outline=(205, 175, 115, 255), width=3)
    tiles.append(t3)

    # Tile 4: Wall rack with red-and-white lifebuoy
    t4 = t0.copy()
    d4 = ImageDraw.Draw(t4)
    # Circular lifebuoy
    d4.ellipse([6, 6, 26, 26], fill=(245, 245, 250, 255), outline=DARK_PLUM)
    d4.ellipse([11, 11, 21, 21], fill=(135, 95, 65, 255), outline=DARK_PLUM) # center hole
    # Red quarters
    d4.pieslice([6, 6, 26, 26], 45, 135, fill=(225, 40, 45, 255))
    d4.pieslice([6, 6, 26, 26], 225, 315, fill=(225, 40, 45, 255))
    d4.ellipse([11, 11, 21, 21], fill=(135, 95, 65, 255), outline=DARK_PLUM)
    tiles.append(t4)

    # Tile 5: Moored wooden rescue rowboat
    t5 = t1.copy()
    d5 = ImageDraw.Draw(t5)
    d5.polygon([(4, 16), (28, 6), (28, 26)], fill=(160, 115, 75, 255), outline=DARK_PLUM)
    d5.polygon([(7, 16), (26, 9), (26, 23)], fill=(85, 55, 35, 255))
    # Orange rescue stripe
    d5.line([(12, 13), (12, 19)], fill=(245, 110, 25, 255), width=2)
    tiles.append(t5)

    # Tile 6: Pier railing with brass post caps
    t6 = t0.copy()
    d6 = ImageDraw.Draw(t6)
    # Horizontal wooden rails
    d6.line([(0, 6), (32, 6)], fill=(110, 75, 50, 255), width=3)
    d6.line([(0, 16), (32, 16)], fill=(110, 75, 50, 255), width=3)
    # Vertical posts with brass caps
    for px in [6, 26]:
        d6.rectangle([px - 2, 4, px + 2, 28], fill=(95, 65, 42, 255), outline=DARK_PLUM)
        d6.ellipse([px - 3, 2, px + 3, 6], fill=(225, 195, 60, 255), outline=DARK_PLUM)
    tiles.append(t6)

    # Tile 7: Nautical hurricane lantern on pier post
    t7 = t0.copy()
    d7 = ImageDraw.Draw(t7)
    d7.ellipse([4, 0, 28, 24], fill=(255, 200, 60, 80)) # golden ripple glow
    d7.rectangle([13, 10, 19, 28], fill=(85, 55, 35, 255), outline=DARK_PLUM)
    # Brass lantern
    d7.polygon([(11, 10), (21, 10), (19, 4), (13, 4)], fill=(205, 165, 45, 255), outline=DARK_PLUM)
    d7.rectangle([13, 7, 19, 10], fill=(255, 240, 120, 255))
    tiles.append(t7)

    save_tileset("marina", tiles)

# ============================================================================
# 7. FOREST TILESET
# ============================================================================
def build_forest():
    tiles = []
    # Tile 0: Pine needle forest floor with moss and mushrooms
    t0 = Image.new("RGBA", (32, 32), (65, 78, 45, 255))
    d0 = ImageDraw.Draw(t0)
    # Pine needles scattered
    for y in range(0, 32, 4):
        for x in range(0, 32, 4):
            if (x * 3 + y * 7) % 4 == 0:
                d0.line([(x, y), (x + 3, y + 2)], fill=(120, 80, 40, 255))
            elif (x * 5 + y * 11) % 6 == 0:
                d0.point((x + 1, y + 1), fill=(95, 145, 60, 255)) # vibrant moss patch
    # Tiny forest mushroom
    d0.ellipse([14, 18, 18, 22], fill=(210, 45, 40, 255))
    d0.line([(16, 22), (16, 26)], fill=(240, 240, 230, 255), width=2)
    tiles.append(t0)

    # Tile 1: Dirt trail path with exposed tree roots
    t1 = Image.new("RGBA", (32, 32), (110, 85, 55, 255))
    d1 = ImageDraw.Draw(t1)
    # Dirt pebbles
    for y in range(0, 32, 6):
        d1.point((y, y), fill=(80, 55, 32, 255))
        d1.point((31 - y, y), fill=(145, 115, 80, 255))
    # Gnarled root curving across
    d1.arc([4, 6, 28, 26], 30, 210, fill=(75, 48, 25, 255), width=3)
    tiles.append(t1)

    # Tile 2: Ancient gnarled pine tree trunk with deep bark
    t2 = t0.copy()
    d2 = ImageDraw.Draw(t2)
    d2.rectangle([4, 0, 28, 32], fill=(68, 44, 28, 255), outline=DARK_PLUM)
    # Deep bark grooves
    for bx in range(8, 28, 5):
        d2.line([(bx, 0), (bx, 32)], fill=(40, 24, 14, 255), width=2)
        d2.line([(bx + 2, 0), (bx + 2, 32)], fill=(105, 72, 48, 255), width=1)
    # Green moss clinging to bark
    d2.polygon([(4, 18), (10, 18), (8, 28), (4, 30)], fill=(75, 130, 50, 255))
    tiles.append(t2)

    # Tile 3: Dense pine needle canopy top with dappled sunbeams
    t3 = Image.new("RGBA", (32, 32), (32, 68, 36, 255))
    d3 = ImageDraw.Draw(t3)
    # Overlapping needle clusters
    for cy in range(0, 32, 8):
        for cx in range(0, 32, 8):
            d3.ellipse([cx, cy, cx + 10, cy + 8], fill=(45, 95, 48, 255))
            d3.point((cx + 5, cy + 4), fill=(80, 150, 75, 255))
    # Dappled sunbeam
    d3.line([(4, 0), (28, 32)], fill=(255, 255, 180, 90), width=3)
    tiles.append(t3)

    # Tile 4: Mossy granite boulder
    t4 = t0.copy()
    d4 = ImageDraw.Draw(t4)
    d4.ellipse([4, 8, 28, 28], fill=(110, 115, 125, 255), outline=DARK_PLUM)
    d4.line([(6, 12), (24, 12)], fill=(160, 168, 180, 255), width=2) # highlight
    # Moss patch on rock
    d4.polygon([(10, 8), (20, 8), (18, 16), (8, 14)], fill=(75, 135, 55, 255))
    tiles.append(t4)

    # Tile 5: Stone campfire ring with glowing embers
    t5 = t0.copy()
    d5 = ImageDraw.Draw(t5)
    # Ring of stones
    d5.ellipse([4, 6, 28, 26], fill=(45, 25, 18, 255), outline=DARK_PLUM)
    for ang in range(0, 360, 45):
        rad = math.radians(ang)
        sx = int(16 + math.cos(rad) * 10)
        sy = int(16 + math.sin(rad) * 8)
        d5.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=(125, 130, 140, 255), outline=DARK_PLUM)
    # Glowing ember bed
    d5.ellipse([11, 12, 21, 20], fill=(240, 80, 20, 255))
    d5.point((16, 16), fill=(255, 220, 80, 255))
    tiles.append(t5)

    # Tile 6: Ripstop nylon camping hammock strung between trees
    t6 = t0.copy()
    d6 = ImageDraw.Draw(t6)
    # Tree trunks on sides
    d6.rectangle([0, 0, 4, 32], fill=(68, 44, 28, 255))
    d6.rectangle([28, 0, 32, 32], fill=(68, 44, 28, 255))
    # Suspension ropes
    d6.line([(4, 12), (8, 16)], fill=(200, 200, 200, 255))
    d6.line([(28, 12), (24, 16)], fill=(200, 200, 200, 255))
    # Green/Orange curved hammock body
    d6.arc([6, 12, 26, 26], 0, 180, fill=(245, 120, 30, 255), width=5)
    d6.arc([8, 14, 24, 24], 0, 180, fill=(75, 150, 60, 255), width=3)
    tiles.append(t6)

    # Tile 7: Forest trail exit with ferns
    t7 = t1.copy()
    d7 = ImageDraw.Draw(t7)
    # Fern fronds
    d7.polygon([(2, 24), (12, 10), (14, 26)], fill=(55, 125, 45, 255))
    d7.polygon([(30, 24), (20, 10), (18, 26)], fill=(55, 125, 45, 255))
    tiles.append(t7)

    save_tileset("forest", tiles)

def build_all():
    build_apartment()
    build_city()
    build_garage()
    build_pub()
    build_alley()
    build_marina()
    build_forest()
    print("All 7 tilesets generated successfully!")

if __name__ == "__main__":
    build_all()
