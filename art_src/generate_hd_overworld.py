#!/usr/bin/env python3
"""generate_hd_overworld.py - High-Definition Overworld Pixel Art Generator for OsakaRPG (Phase 1).
Generates:
1. public/assets/maps/apartment_bg.png (1024x576, 32x18 tiles)
2. public/assets/maps/city_bg.png (1280x576, 40x18 tiles)
3. public/assets/maps/zabka_bg.png (1024x576, 32x18 tiles)
4. Updated prop tilesets in public/assets/tiles/:
   - apartment.png
   - city.png
   - zabka.png

Aesthetic Standards:
- Authentic, rich pixel art matching lisu_battle.png and battle backgrounds.
- Multi-tone color ramps with highlights, midtones, shadows, and bevel crevices.
- Textured surfaces (herringbone oak parquet, granite pavers, vinyl wax, asphalt).
- Ambient contact shadows, glowing neon/light sources, diagonal morning sunbeams.
"""

import os
import math
from PIL import Image, ImageDraw

MAPS_DIR = "public/assets/maps"
TILES_DIR = "public/assets/tiles"
os.makedirs(MAPS_DIR, exist_ok=True)
os.makedirs(TILES_DIR, exist_ok=True)

TILE = 32

# Master Palette constants
PAL = {
    'void': (0, 3, 11, 255),
    'ink': (6, 18, 32, 255),
    'navy': (10, 24, 43, 255),
    'panel': (12, 33, 52, 255),
    'panelHi': (16, 45, 59, 255),
    'steel': (32, 61, 84, 255),
    'slate': (46, 59, 77, 255),
    'grey': (94, 111, 122, 255),
    'silver': (151, 160, 166, 255),
    'white': (216, 218, 218, 255),
    'yellow': (232, 216, 74, 255),
    'green': (95, 200, 90, 255),
    'fire': (224, 116, 44, 255),
    'fireHi': (246, 192, 74, 255),
    'red': (192, 57, 43, 255),
    'cyan': (158, 203, 212, 255),
    'cyanHi': (200, 238, 244, 255),
    'zabka_green': (12, 138, 42, 255),
    'zabka_green_hi': (26, 178, 62, 255),
    'zabka_green_dk': (8, 90, 28, 255),
    'zabka_yellow': (244, 212, 48, 255),
}

def draw_v_gradient(draw, y0, y1, c0, c1, x0=0, x1=1024):
    h = max(1, y1 - y0)
    for y in range(y0, y1):
        t = (y - y0) / float(h)
        r = int(c0[0] + (c1[0] - c0[0]) * t)
        g = int(c0[1] + (c1[1] - c0[1]) * t)
        b = int(c0[2] + (c1[2] - c0[2]) * t)
        draw.line([(x0, y), (x1, y)], fill=(r, g, b, 255))

def draw_contact_shadow(draw, cx, cy, rx, ry, alpha=80):
    """Draws a soft ambient contact shadow ellipse under an object."""
    bbox = [cx - rx, cy - ry, cx + rx, cy + ry]
    draw.ellipse(bbox, fill=(10, 14, 22, alpha))
    inner = [cx - rx * 0.65, cy - ry * 0.6, cx + rx * 0.65, cy + ry * 0.6]
    draw.ellipse(inner, fill=(6, 10, 16, int(alpha * 0.8)))

# ============================================================================
# 1. MAP: MIESZKANIE (APARTMENT) - 1024x576 (32x18 tiles)
# ============================================================================
def generate_apartment_bg():
    W = 32 * TILE # 1024
    H = 18 * TILE # 576
    im = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(im)

    # Base background: Herringbone oak parquet across the entire room (rows 2 to 17)
    # Herringbone pattern: 45-degree interlocked oak planks
    parquet_base = (195, 142, 92)
    parquet_mid = (175, 122, 74)
    parquet_hi = (218, 168, 118)
    parquet_sh = (138, 88, 48)
    parquet_crevice = (98, 58, 30)

    # Fill base floor
    draw.rectangle([0, 0, W, H], fill=parquet_base)

    # Render textured parquet with fine wood grain and plank seams
    plank_w = 16
    plank_h = 32
    for y in range(64, H, 16):
        for x in range(0, W, 16):
            direction = ((x // 16) + (y // 16)) % 2
            # Subtle plank tint variation
            noise = ((x * 17 + y * 31) % 19) - 9
            r = min(255, max(0, parquet_mid[0] + noise))
            g = min(255, max(0, parquet_mid[1] + noise // 2))
            b = min(255, max(0, parquet_mid[2] + noise // 3))
            draw.rectangle([x, y, x + 15, y + 15], fill=(r, g, b, 255))

            if direction == 0:
                # Diagonal 45-degree grain highlight
                draw.line([(x + 2, y + 4), (x + 13, y + 4)], fill=parquet_hi)
                draw.line([(x + 1, y + 10), (x + 14, y + 10)], fill=parquet_sh)
                # Outer bevel
                draw.line([(x, y), (x + 15, y)], fill=parquet_hi)
                draw.line([(x, y + 15), (x + 15, y + 15)], fill=parquet_crevice)
                draw.line([(x + 15, y), (x + 15, y + 15)], fill=parquet_crevice)
            else:
                # Vertical grain highlight
                draw.line([(x + 4, y + 2), (x + 4, y + 13)], fill=parquet_hi)
                draw.line([(x + 10, y + 1), (x + 10, y + 14)], fill=parquet_sh)
                draw.line([(x, y), (x, y + 15)], fill=parquet_hi)
                draw.line([(x + 15, y), (x + 15, y + 15)], fill=parquet_crevice)
                draw.line([(x, y + 15), (x + 15, y + 15)], fill=parquet_crevice)

    # Satin sheen reflection bands (subtle horizontal varnish sheen across floor)
    sheen_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sheen_draw = ImageDraw.Draw(sheen_overlay)
    for sy in range(96, H - 48, 48):
        sheen_draw.rectangle([32, sy, W - 32, sy + 8], fill=(255, 240, 210, 16))
        sheen_draw.rectangle([32, sy + 2, W - 32, sy + 6], fill=(255, 245, 220, 22))
    im.alpha_composite(sheen_overlay)
    draw = ImageDraw.Draw(im)

    # -------------------------------------------------------------------------
    # North Plaster Wall (Rows 0 to 1, y = 0..63)
    # -------------------------------------------------------------------------
    # Ceiling Crown Moulding (y = 0..10)
    draw_v_gradient(draw, 0, 10, (238, 235, 228), (210, 204, 194), 0, W)
    draw.line([(0, 10), (W, 10)], fill=(160, 154, 144, 255), width=2)

    # Warm oatmeal plaster wall (y = 11..56)
    draw_v_gradient(draw, 11, 56, (224, 218, 206), (198, 190, 176), 0, W)
    # Plaster texture stippling
    for py in range(12, 55, 3):
        for px in range(0, W, 4):
            if (px * 13 + py * 7) % 11 == 0:
                draw.point((px, py), fill=(182, 174, 160, 255))
            elif (px * 19 + py * 5) % 13 == 0:
                draw.point((px, py), fill=(236, 230, 220, 255))

    # Baseboard (y = 56..63)
    draw.rectangle([0, 56, W, 63], fill=(110, 68, 38, 255))
    draw.line([(0, 56), (W, 56)], fill=(154, 98, 58, 255), width=1)
    draw.line([(0, 63), (W, 63)], fill=(58, 34, 18, 255), width=1)

    # Outer wall borders (x=0..31 is solid west wall, x=1024-32..1024 is east wall, y=576-32 is south wall)
    # West wall (x = 0..31, y = 0..H)
    draw.rectangle([0, 0, 31, H], fill=(185, 176, 162, 255))
    draw.rectangle([0, 0, 12, H], fill=(150, 140, 128, 255))
    draw.line([(31, 0), (31, H)], fill=(120, 110, 98, 255), width=2)
    draw.rectangle([24, 56, 31, H], fill=(110, 68, 38, 255)) # west baseboard

    # East wall (x = W - 32..W, y = 0..H)
    draw.rectangle([W - 32, 0, W, H], fill=(185, 176, 162, 255))
    draw.rectangle([W - 12, 0, W, H], fill=(150, 140, 128, 255))
    draw.line([(W - 32, 0), (W - 32, H)], fill=(120, 110, 98, 255), width=2)
    draw.rectangle([W - 32, 56, W - 24, H], fill=(110, 68, 38, 255)) # east baseboard

    # South Wall / Baseboard (y = H - 32..H)
    draw.rectangle([0, H - 32, W, H], fill=(190, 182, 170, 255))
    draw.rectangle([0, H - 32, W, H - 24], fill=(110, 68, 38, 255)) # south baseboard
    draw.line([(0, H - 32), (W, H - 32)], fill=(65, 38, 20, 255), width=2)

    # -------------------------------------------------------------------------
    # North Double-Hung Window with Venetian Blinds (x = 224..384, y = 8..56)
    # -------------------------------------------------------------------------
    wx0, wy0, wx1, wy1 = 224, 8, 384, 56
    # Outer trim
    draw.rectangle([wx0 - 4, wy0 - 2, wx1 + 4, wy1 + 4], fill=(245, 245, 248, 255), outline=(170, 170, 180, 255))
    # Sky outside window (morning golden sunrise sky)
    draw_v_gradient(draw, wy0, wy1, (90, 140, 210), (250, 215, 140), wx0, wx1)
    # Distant rooftop silhouettes
    draw.polygon([(wx0, wy1), (wx0 + 40, wy1 - 18), (wx0 + 80, wy1 - 12), (wx0 + 130, wy1 - 24), (wx1, wy1 - 10), (wx1, wy1)], fill=(70, 85, 115, 255))
    # Window panes & mullions
    draw.line([(wx0 + (wx1 - wx0)//2, wy0), (wx0 + (wx1 - wx0)//2, wy1)], fill=(245, 245, 250, 255), width=4)
    draw.line([(wx0, wy0 + (wy1 - wy0)//2), (wx1, wy0 + (wy1 - wy0)//2)], fill=(245, 245, 250, 255), width=4)
    # Venetian blinds slats
    for by in range(wy0 + 4, wy1, 5):
        draw.line([(wx0 + 2, by), (wx1 - 2, by)], fill=(235, 238, 245, 180), width=2)
        draw.line([(wx0 + 2, by + 1), (wx1 - 2, by + 1)], fill=(160, 165, 180, 180), width=1)
    # Window sill
    draw.rectangle([wx0 - 8, wy1 - 2, wx1 + 8, wy1 + 6], fill=(240, 240, 245, 255), outline=(140, 140, 150, 255))

    # -------------------------------------------------------------------------
    # Morning Sunbeams Streaming Diagonally Across the Parquet Floor
    # -------------------------------------------------------------------------
    beam_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    beam_draw = ImageDraw.Draw(beam_img)
    # Main wide golden sunbeam
    beam_poly = [
        (wx0 + 10, wy1 + 6),
        (wx1 - 10, wy1 + 6),
        (wx1 + 280, H - 80),
        (wx0 + 120, H - 80)
    ]
    beam_draw.polygon(beam_poly, fill=(255, 242, 190, 52))
    # Core brighter center beam
    beam_core = [
        (wx0 + 50, wy1 + 6),
        (wx1 - 50, wy1 + 6),
        (wx1 + 180, H - 120),
        (wx0 + 170, H - 120)
    ]
    beam_draw.polygon(beam_core, fill=(255, 248, 215, 68))
    # Venetian blind shadow stripes through the beam
    for offset in range(30, 420, 28):
        beam_draw.line([(wx0 + offset, wy1 + 6), (wx0 + offset + 260, H - 80)], fill=(180, 140, 80, 16), width=6)
    # Floating sunlit dust motes
    for dx, dy in [(280, 120), (310, 160), (340, 220), (410, 280), (460, 340), (510, 260), (380, 310), (440, 190)]:
        beam_draw.ellipse([dx - 2, dy - 2, dx + 2, dy + 2], fill=(255, 255, 230, 160))

    im.alpha_composite(beam_img)
    draw = ImageDraw.Draw(im)

    # -------------------------------------------------------------------------
    # Architectural Partition Wall dividing Bedroom / Foyer (x = 11 tiles = 352px)
    # -------------------------------------------------------------------------
    # Divider wall at x = 352, runs y = 0..352 (with open archway at y = 160..224)
    part_x = 11 * TILE
    # Upper partition wall (y = 0..160)
    draw.rectangle([part_x, 0, part_x + 12, 160], fill=(205, 198, 186, 255), outline=(130, 120, 110, 255))
    draw.line([(part_x, 56), (part_x + 12, 56)], fill=(110, 68, 38, 255), width=4)
    # Lower partition wall (y = 224..352)
    draw.rectangle([part_x, 224, part_x + 12, 352], fill=(205, 198, 186, 255), outline=(130, 120, 110, 255))
    draw.line([(part_x, 346), (part_x + 12, 346)], fill=(110, 68, 38, 255), width=6)
    # Wall running along y = 11 (352px) from x = 0 to part_x (bedroom south wall)
    draw.rectangle([0, 11 * TILE, part_x, 11 * TILE + 16], fill=(195, 188, 176, 255), outline=(120, 110, 100, 255))
    draw.rectangle([0, 11 * TILE + 10, part_x, 11 * TILE + 16], fill=(110, 68, 38, 255)) # baseboard

    # -------------------------------------------------------------------------
    # Entryway Front Door & Doormat at (x: 10, y: 11) -> (320, 352)
    # -------------------------------------------------------------------------
    ed_x = 10 * TILE
    ed_y = 11 * TILE
    # Heavy solid oak front door frame
    draw.rectangle([ed_x - 2, ed_y - 2, ed_x + 34, ed_y + 34], fill=(95, 55, 30, 255), outline=(50, 28, 14, 255))
    # Coir entryway doormat on the floor in front of the door
    draw_contact_shadow(draw, ed_x + 16, ed_y + 16, 20, 14, alpha=110)
    draw.rounded_rectangle([ed_x + 2, ed_y + 4, ed_x + 30, ed_y + 28], radius=3, fill=(180, 130, 75, 255), outline=(75, 45, 20, 255), width=2)
    draw.text((ed_x + 6, ed_y + 11), "HOME", fill=(245, 225, 175, 255))
    # Brass door threshold
    draw.line([(ed_x, ed_y + 1), (ed_x + 32, ed_y + 1)], fill=(225, 190, 80, 255), width=2)
    # Wall coat rack at x = 9, y = 11
    cr_x = 9 * TILE
    draw.rectangle([cr_x + 4, ed_y + 2, cr_x + 28, ed_y + 10], fill=(130, 80, 45, 255), outline=(70, 40, 20, 255))
    # Hanging jacket silhouette
    draw.polygon([(cr_x + 8, ed_y + 10), (cr_x + 18, ed_y + 10), (cr_x + 22, ed_y + 26), (cr_x + 6, ed_y + 26)], fill=(45, 58, 72, 255))

    # -------------------------------------------------------------------------
    # Battlestation: Dual-Monitor Desk at (3, 2), Chair at (3, 3)
    # -------------------------------------------------------------------------
    desk_x = 3 * TILE
    desk_y = 2 * TILE
    draw_contact_shadow(draw, desk_x + 16, desk_y + 28, 22, 10, alpha=140)
    # Desk wood surface
    draw.rectangle([desk_x + 2, desk_y + 10, desk_x + 30, desk_y + 30], fill=(42, 46, 56, 255), outline=(18, 20, 26, 255), width=2)
    draw.line([(desk_x + 3, desk_y + 11), (desk_x + 29, desk_y + 11)], fill=(75, 82, 98, 255))
    # Glowing Dual Ultrawide Monitors
    # Monitor 1 (Left: IDE / VS Code)
    draw.rectangle([desk_x + 2, desk_y - 2, desk_x + 15, desk_y + 12], fill=(18, 22, 30, 255), outline=(6, 8, 12, 255))
    draw.rectangle([desk_x + 4, desk_y, desk_x + 13, desk_y + 10], fill=(24, 32, 48, 255))
    # Code syntax lines (cyan, yellow, green)
    draw.line([(desk_x + 5, desk_y + 2), (desk_x + 10, desk_y + 2)], fill=(90, 210, 245, 255))
    draw.line([(desk_x + 6, desk_y + 4), (desk_x + 12, desk_y + 4)], fill=(245, 220, 80, 255))
    draw.line([(desk_x + 5, desk_y + 6), (desk_x + 11, desk_y + 6)], fill=(120, 240, 140, 255))
    draw.line([(desk_x + 6, desk_y + 8), (desk_x + 9, desk_y + 8)], fill=(245, 110, 140, 255))
    # Monitor 2 (Right: Slack / Terminal with active red badges)
    draw.rectangle([desk_x + 16, desk_y - 2, desk_x + 29, desk_y + 12], fill=(18, 22, 30, 255), outline=(6, 8, 12, 255))
    draw.rectangle([desk_x + 18, desk_y, desk_x + 27, desk_y + 10], fill=(38, 18, 38, 255)) # Slack aubergine sidebar
    draw.rectangle([desk_x + 22, desk_y, desk_x + 27, desk_y + 10], fill=(28, 32, 42, 255)) # chat body
    draw.line([(desk_x + 23, desk_y + 3), (desk_x + 26, desk_y + 3)], fill=(220, 225, 235, 255))
    draw.line([(desk_x + 23, desk_y + 6), (desk_x + 26, desk_y + 6)], fill=(220, 225, 235, 255))
    # Glowing Red Unread Notification Badge!
    draw.ellipse([desk_x + 26, desk_y - 1, desk_x + 29, desk_y + 2], fill=(245, 45, 55, 255))
    # Cyan LED desk glow reflection
    draw.line([(desk_x + 4, desk_y + 13), (desk_x + 28, desk_y + 13)], fill=(80, 210, 255, 120))

    # Gaming Chair at (3, 3) -> (96, 96)
    chair_x = 3 * TILE
    chair_y = 3 * TILE
    draw_contact_shadow(draw, chair_x + 16, chair_y + 24, 14, 8, alpha=120)
    # Chair seat & lumbar support
    draw.rounded_rectangle([chair_x + 8, chair_y + 6, chair_x + 24, chair_y + 22], radius=3, fill=(26, 28, 36, 255), outline=(12, 14, 18, 255))
    draw.line([(chair_x + 11, chair_y + 8), (chair_x + 21, chair_y + 8)], fill=(225, 42, 48, 255), width=2) # red racing stripe
    draw.line([(chair_x + 11, chair_y + 16), (chair_x + 21, chair_y + 16)], fill=(225, 42, 48, 255), width=2)
    # Five-point caster wheels
    draw.line([(chair_x + 8, chair_y + 24), (chair_x + 24, chair_y + 24)], fill=(45, 50, 60, 255), width=2)

    # -------------------------------------------------------------------------
    # Platform Bed with Crumpled Slate-Blue Duvet at (6, 5) and (7, 5)
    # -------------------------------------------------------------------------
    bed_x = 6 * TILE
    bed_y = 5 * TILE
    draw_contact_shadow(draw, bed_x + 32, bed_y + 22, 36, 16, alpha=130)
    # Dark oiled walnut low platform frame
    draw.rectangle([bed_x + 2, bed_y - 8, bed_x + 62, bed_y + 26], fill=(78, 48, 30, 255), outline=(42, 24, 14, 255), width=2)
    draw.line([(bed_x + 3, bed_y - 7), (bed_x + 61, bed_y - 7)], fill=(120, 78, 48, 255))
    # Two plump soft white pillows
    draw.rounded_rectangle([bed_x + 6, bed_y - 6, bed_x + 28, bed_y + 6], radius=3, fill=(245, 246, 250, 255), outline=(180, 185, 195, 255))
    draw.line([(bed_x + 10, bed_y - 2), (bed_x + 24, bed_y - 2)], fill=(210, 215, 225, 255))
    draw.rounded_rectangle([bed_x + 34, bed_y - 6, bed_x + 56, bed_y + 6], radius=3, fill=(245, 246, 250, 255), outline=(180, 185, 195, 255))
    draw.line([(bed_x + 38, bed_y - 2), (bed_x + 52, bed_y - 2)], fill=(210, 215, 225, 255))
    # Crumpled slate-blue duvet with realistic fabric folds
    draw.rounded_rectangle([bed_x + 4, bed_y + 4, bed_x + 60, bed_y + 24], radius=3, fill=(78, 108, 144, 255), outline=(42, 64, 92, 255))
    # Duvet fold highlights & crevice shadows
    draw.line([(bed_x + 8, bed_y + 8), (bed_x + 26, bed_y + 14)], fill=(118, 152, 195, 255), width=2)
    draw.line([(bed_x + 28, bed_y + 14), (bed_x + 52, bed_y + 8)], fill=(118, 152, 195, 255), width=2)
    draw.line([(bed_x + 12, bed_y + 18), (bed_x + 46, bed_y + 22)], fill=(48, 70, 98, 255), width=2)

    # -------------------------------------------------------------------------
    # Monstera Plant in Terracotta Pot at (8, 2) -> (256, 64)
    # -------------------------------------------------------------------------
    mon_x = 8 * TILE
    mon_y = 2 * TILE
    draw_contact_shadow(draw, mon_x + 16, mon_y + 28, 12, 6, alpha=130)
    # Terracotta Pot
    draw.polygon([(mon_x + 9, mon_y + 16), (mon_x + 23, mon_y + 16), (mon_x + 21, mon_y + 28), (mon_x + 11, mon_y + 28)], fill=(195, 85, 48, 255), outline=(110, 42, 22, 255))
    draw.line([(mon_x + 8, mon_y + 16), (mon_x + 24, mon_y + 16)], fill=(235, 115, 75, 255), width=2)
    # Lush split monstera leaves
    leaves = [
        (mon_x + 16, mon_y + 4, 7, 5),
        (mon_x + 8, mon_y + 10, 6, 4),
        (mon_x + 24, mon_y + 8, 6, 4),
        (mon_x + 11, mon_y + 14, 5, 4),
        (mon_x + 21, mon_y + 14, 5, 4),
    ]
    for lx, ly, rx, ry in leaves:
        draw.ellipse([lx - rx, ly - ry, lx + rx, ly + ry], fill=(42, 138, 58, 255), outline=(18, 72, 28, 255))
        draw.line([(lx, ly - ry + 1), (lx, ly + ry - 1)], fill=(85, 195, 105, 255))

    # -------------------------------------------------------------------------
    # Kitchenette along North-East (x = 16..24 tiles, y = 1..2)
    # -------------------------------------------------------------------------
    kit_x = 16 * TILE
    kit_y = 1 * TILE
    # Refrigerator at (16, 2)
    rf_x = 16 * TILE
    rf_y = 2 * TILE
    draw_contact_shadow(draw, rf_x + 16, rf_y + 28, 16, 8, alpha=130)
    draw.rectangle([rf_x + 4, rf_y - 12, rf_x + 28, rf_y + 28], fill=(210, 215, 222, 255), outline=(140, 145, 155, 255), width=2)
    draw.line([(rf_x + 6, rf_y + 4), (rf_x + 26, rf_y + 4)], fill=(140, 145, 155, 255)) # door split
    draw.rectangle([rf_x + 7, rf_y - 4, rf_x + 9, rf_y + 2], fill=(90, 95, 105, 255)) # handle top
    draw.rectangle([rf_x + 7, rf_y + 6, rf_x + 9, rf_y + 14], fill=(90, 95, 105, 255)) # handle bottom

    # Kitchen Counter & Cabinets (x = 17..23 tiles, y = 2)
    cnt_x0 = 17 * TILE
    cnt_x1 = 24 * TILE
    draw_contact_shadow(draw, (cnt_x0 + cnt_x1)//2, 2 * TILE + 28, (cnt_x1 - cnt_x0)//2, 8, alpha=110)
    # Base cabinets
    draw.rectangle([cnt_x0, 2 * TILE + 4, cnt_x1, 2 * TILE + 28], fill=(52, 58, 68, 255), outline=(26, 30, 36, 255))
    # Quartz white countertop
    draw.rectangle([cnt_x0 - 2, 2 * TILE + 2, cnt_x1 + 2, 2 * TILE + 10], fill=(238, 240, 244, 255), outline=(170, 175, 185, 255))
    # Sink at (19, 2)
    sink_x = 19 * TILE
    draw.rectangle([sink_x + 4, 2 * TILE + 4, sink_x + 24, 2 * TILE + 9], fill=(130, 140, 155, 255), outline=(80, 85, 95, 255))
    draw.line([(sink_x + 14, 2 * TILE + 2), (sink_x + 14, 2 * TILE + 5)], fill=(200, 205, 215, 255), width=2) # faucet
    # Espresso Coffee Machine at (22, 2)
    esp_x = 22 * TILE
    draw.rectangle([esp_x + 6, 2 * TILE - 4, esp_x + 24, 2 * TILE + 8], fill=(30, 34, 42, 255), outline=(12, 14, 18, 255))
    draw.rectangle([esp_x + 9, 2 * TILE - 2, esp_x + 14, 2 * TILE + 1], fill=(235, 60, 40, 255)) # blinking display!
    draw.rectangle([esp_x + 11, 2 * TILE + 4, esp_x + 19, 2 * TILE + 8], fill=(240, 240, 245, 255)) # cup

    # -------------------------------------------------------------------------
    # Living Room Lounge (x = 18..28 tiles, y = 8..15)
    # -------------------------------------------------------------------------
    # Oval wool area rug
    rug_x = 23 * TILE
    rug_y = 11 * TILE
    draw.ellipse([rug_x - 120, rug_y - 60, rug_x + 120, rug_y + 60], fill=(62, 85, 105, 255), outline=(95, 125, 150, 255), width=2)
    draw.ellipse([rug_x - 100, rug_y - 45, rug_x + 100, rug_y + 45], fill=(72, 98, 120, 255))

    # Scandinavian Sofa at (20..24, 8)
    sofa_x = 20 * TILE
    sofa_y = 8 * TILE
    draw_contact_shadow(draw, sofa_x + 64, sofa_y + 26, 68, 14, alpha=130)
    draw.rounded_rectangle([sofa_x, sofa_y - 2, sofa_x + 128, sofa_y + 26], radius=4, fill=(135, 115, 95, 255), outline=(78, 64, 52, 255), width=2)
    # Cushions
    draw.rounded_rectangle([sofa_x + 6, sofa_y + 4, sofa_x + 44, sofa_y + 22], radius=3, fill=(165, 142, 118, 255))
    draw.rounded_rectangle([sofa_x + 46, sofa_y + 4, sofa_x + 84, sofa_y + 22], radius=3, fill=(165, 142, 118, 255))
    draw.rounded_rectangle([sofa_x + 86, sofa_y + 4, sofa_x + 122, sofa_y + 22], radius=3, fill=(165, 142, 118, 255))

    # TV Credenza & Retro CRT with Pegasus Console at (27..29, 10..11)
    tv_x = 27 * TILE
    tv_y = 10 * TILE
    draw_contact_shadow(draw, tv_x + 32, tv_y + 28, 36, 12, alpha=130)
    # Wooden credenza
    draw.rectangle([tv_x, tv_y + 4, tv_x + 64, tv_y + 28], fill=(95, 60, 36, 255), outline=(50, 30, 16, 255), width=2)
    # CRT Television (Sony Trinitron retro curved screen)
    draw.rounded_rectangle([tv_x + 6, tv_y - 14, tv_x + 42, tv_y + 6], radius=3, fill=(35, 38, 45, 255), outline=(15, 18, 22, 255))
    draw.rounded_rectangle([tv_x + 9, tv_y - 11, tv_x + 39, tv_y + 3], radius=2, fill=(48, 65, 85, 255))
    draw.line([(tv_x + 12, tv_y - 8), (tv_x + 22, tv_y + 1)], fill=(120, 155, 195, 140), width=2) # glass reflection
    # Pegasus / Famicom console beside CRT
    draw.rectangle([tv_x + 46, tv_y - 2, tv_x + 60, tv_y + 6], fill=(225, 220, 205, 255), outline=(140, 135, 120, 255))
    draw.rectangle([tv_x + 50, tv_y - 5, tv_x + 56, tv_y - 1], fill=(235, 190, 40, 255)) # yellow cartridge!

    # Save Apartment Map
    out_path = os.path.join(MAPS_DIR, "apartment_bg.png")
    im.save(out_path, "PNG")
    print(f"Generated {out_path}: {im.size} (32x18 tiles)")


# ============================================================================
# 2. MAP: PORANNE MIASTO (CITY) - 1280x576 (40x18 tiles)
# ============================================================================
def generate_city_bg():
    W = 40 * TILE # 1280
    H = 18 * TILE # 576
    im = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(im)

    # -------------------------------------------------------------------------
    # Sky: Early Morning Sunrise over Warsaw / Osaka (y = 0..96)
    # -------------------------------------------------------------------------
    draw_v_gradient(draw, 0, 96, (42, 48, 75), (235, 165, 130), 0, W)
    # Distant hazy skyline & morning clouds
    cloud_img = Image.new("RGBA", (W, 96), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cloud_img)
    for cx in range(40, W, 180):
        cd.ellipse([cx, 30, cx + 140, 65], fill=(245, 195, 160, 60))
        cd.ellipse([cx + 20, 20, cx + 110, 50], fill=(255, 225, 185, 75))
    im.alpha_composite(cloud_img)
    draw = ImageDraw.Draw(im)

    # -------------------------------------------------------------------------
    # Historic Brick Tenements (Kamienice) Facades (Rows 1 to 3, y = 32..96)
    # -------------------------------------------------------------------------
    # Brick building base across entire width
    brick_main = (162, 70, 54)
    brick_hi = (195, 95, 74)
    brick_sh = (118, 45, 34)
    mortar = (210, 198, 185)

    draw.rectangle([0, 32, W, 96], fill=brick_main)
    # Individual detailed bricks & mortar joints
    for by in range(32, 96, 6):
        draw.line([(0, by), (W, by)], fill=mortar, width=1)
        shift = (by % 12) // 6 * 8
        for bx in range(shift, W, 16):
            draw.line([(bx, by), (bx, by + 6)], fill=mortar, width=1)
            # Brick highlight & shadow
            draw.point((bx + 3, by + 2), fill=brick_hi)
            draw.point((bx + 11, by + 4), fill=brick_sh)

    # Architectural Stucco Cornice & Roofline Parapet (y = 28..36)
    draw.rectangle([0, 28, W, 36], fill=(235, 230, 222, 255), outline=(155, 145, 135, 255))
    # Dentil cornice pattern
    for dx in range(0, W, 8):
        draw.rectangle([dx, 33, dx + 4, 36], fill=(160, 150, 140, 255))

    # Upper Tenement Windows with stone lintels and warm dawn reflections
    for wx in range(32, W - 64, 48):
        if 96 <= wx <= 240:
            continue # Żabka storefront area
        if wx >= 1152:
            continue # Garage shutter area
        # Stone lintel
        draw.rectangle([wx - 2, 42, wx + 26, 46], fill=(235, 230, 220, 255), outline=(150, 145, 135, 255))
        # Window frame & glass
        is_lit = ((wx // 48) % 3 == 0)
        glass_col = (255, 225, 110, 255) if is_lit else (52, 68, 92, 255)
        draw.rectangle([wx, 46, wx + 24, 76], fill=glass_col, outline=(35, 25, 20, 255), width=2)
        draw.line([(wx + 12, 46), (wx + 12, 76)], fill=(35, 25, 20, 255), width=2)
        draw.line([(wx, 61), (wx + 24, 61)], fill=(35, 25, 20, 255), width=2)
        if not is_lit:
            draw.line([(wx + 2, 48), (wx + 10, 72)], fill=(140, 175, 215, 140), width=2) # sky reflection

    # -------------------------------------------------------------------------
    # Żabka Storefront Facade (Columns 3 to 7, x = 96..256, y = 32..96)
    # -------------------------------------------------------------------------
    zx0 = 3 * TILE # 96
    zx1 = 8 * TILE # 256
    # Deep storefront recess
    draw.rectangle([zx0, 32, zx1, 96], fill=(28, 34, 42, 255))
    # Iconic Żabka Green Brand Awning / Signboard (y = 42..68)
    draw.rectangle([zx0 + 4, 42, zx1 - 4, 68], fill=PAL['zabka_green'], outline=PAL['zabka_green_hi'], width=2)
    draw.line([(zx0 + 4, 68), (zx1 - 4, 68)], fill=PAL['zabka_green_dk'], width=2)
    # Żabka Yellow Smiling Frog Arc Logo
    logo_cx = (zx0 + zx1) // 2 - 14
    draw.arc([logo_cx - 16, 44, logo_cx + 16, 64], 0, 180, fill=PAL['zabka_yellow'], width=3)
    draw.ellipse([logo_cx - 8, 48, logo_cx - 4, 52], fill=PAL['zabka_yellow'])
    draw.ellipse([logo_cx + 4, 48, logo_cx + 8, 52], fill=PAL['zabka_yellow'])
    draw.text((logo_cx + 18, 48), "żabka", fill=(255, 255, 255, 255))
    # Glowing Neon "24/7" badge
    draw.rounded_rectangle([zx1 - 38, 46, zx1 - 10, 64], radius=2, fill=(16, 45, 24, 255), outline=PAL['zabka_yellow'], width=2)
    draw.text((zx1 - 34, 48), "24/7", fill=PAL['zabka_yellow'])

    # Large Plate Glass Display Windows at (4, 2) and (6, 2)
    for dwx in [4 * TILE, 6 * TILE]:
        draw.rectangle([dwx + 2, 70, dwx + 30, 96], fill=(16, 75, 95, 255), outline=(10, 48, 25, 255), width=2)
        draw.line([(dwx + 4, 72), (dwx + 16, 94)], fill=(180, 240, 255, 140), width=2)
        # Inside neon icons (hot dog & coffee silhouettes)
        if dwx == 4 * TILE:
            draw.rounded_rectangle([dwx + 8, 76, dwx + 24, 84], radius=3, fill=(235, 95, 45, 255)) # neon hot dog!
        else:
            draw.rectangle([dwx + 10, 76, dwx + 22, 88], fill=(245, 215, 120, 255)) # neon coffee cup!

    # Automatic Sliding Glass Entrance Doors at (5, 3) -> (160, 96)
    ed_x = 5 * TILE # 160
    draw.rectangle([ed_x + 2, 68, ed_x + 30, 96], fill=(22, 145, 54, 255), outline=(8, 65, 22, 255), width=2)
    # Glass sliding panels with reflections
    draw.rectangle([ed_x + 4, 70, ed_x + 14, 95], fill=(150, 220, 238, 200), outline=(10, 70, 26, 255))
    draw.rectangle([ed_x + 18, 70, ed_x + 28, 95], fill=(150, 220, 238, 200), outline=(10, 70, 26, 255))
    # Green welcome doormat in front of doors (at row 3, y = 96..127)
    draw.rounded_rectangle([ed_x + 3, 98, ed_x + 29, 114], radius=3, fill=PAL['zabka_green'], outline=PAL['zabka_green_dk'], width=2)
    draw.text((ed_x + 6, 101), "WEJŚCIE", fill=PAL['zabka_yellow'])

    # -------------------------------------------------------------------------
    # Industrial Garage Roll-up Shutter on Far Right (Columns 36 to 39, x = 1152..1279)
    # -------------------------------------------------------------------------
    gx0 = 36 * TILE
    gx1 = W
    draw.rectangle([gx0, 32, gx1, 160], fill=(42, 46, 54, 255))
    # Concrete structural lintel
    draw.rectangle([gx0 + 4, 40, gx1 - 4, 60], fill=(160, 165, 175, 255), outline=(90, 95, 105, 255), width=2)
    # Yellow and Black Hazard Warning Stripes!
    for hx in range(gx0 + 6, gx1 - 6, 16):
        draw.polygon([(hx, 60), (hx + 10, 40), (hx + 16, 40), (hx + 6, 60)], fill=(245, 215, 40, 255))
    # Corrugated steel roll-up door (slats)
    draw.rectangle([gx0 + 8, 60, gx1 - 8, 155], fill=(68, 75, 88, 255), outline=(32, 36, 44, 255), width=2)
    for sy in range(64, 154, 6):
        draw.line([(gx0 + 10, sy), (gx1 - 10, sy)], fill=(95, 105, 120, 255), width=2)
        draw.line([(gx0 + 10, sy + 2), (gx1 - 10, sy + 2)], fill=(45, 50, 60, 255), width=1)
    # Digital security keypad & heavy padlock hasp at (38, 5) -> (1216, 160)
    draw.rectangle([gx0 + 48, 110, gx0 + 58, 126], fill=(25, 28, 35, 255), outline=(235, 60, 40, 255)) # keypad with red LED

    # -------------------------------------------------------------------------
    # Sidewalk: Granite Flagstone Pavers & Tactile Paving (Rows 3 to 6, y = 96..223)
    # -------------------------------------------------------------------------
    sidewalk_base = (168, 174, 184)
    sidewalk_hi = (205, 210, 220)
    sidewalk_sh = (124, 130, 140)
    sidewalk_joint = (95, 100, 110)

    draw.rectangle([0, 96, W, 223], fill=sidewalk_base)
    # 60x60cm rectangular granite slabs
    for fy in range(96, 192, 16):
        draw.line([(0, fy), (W, fy)], fill=sidewalk_joint, width=1)
        shift = ((fy // 16) % 2) * 16
        for fx in range(shift, W, 32):
            draw.line([(fx, fy), (fx, fy + 16)], fill=sidewalk_joint, width=1)
            # Granite stipple & bevel highlight
            draw.line([(fx + 1, fy + 1), (fx + 31, fy + 1)], fill=sidewalk_hi)
            draw.point((fx + 5, fy + 6), fill=(140, 145, 155, 255))
            draw.point((fx + 19, fy + 11), fill=(190, 195, 205, 255))

    # Yellow tactile paving strip (row 5 bottom, y = 180..192)
    tactile_y = 180
    draw.rectangle([0, tactile_y, W, tactile_y + 12], fill=(225, 205, 55, 255), outline=(160, 140, 30, 255))
    # Raised tactile paving studs / ribs
    for tx in range(0, W, 8):
        draw.line([(tx + 2, tactile_y + 2), (tx + 2, tactile_y + 10)], fill=(255, 238, 110, 255), width=2)
        draw.line([(tx + 4, tactile_y + 2), (tx + 4, tactile_y + 10)], fill=(180, 155, 30, 255), width=1)

    # Chiseled Granite Curb transition separating sidewalk from road (y = 192..208)
    draw.rectangle([0, 192, W, 204], fill=(210, 215, 224, 255), outline=(135, 140, 150, 255))
    draw.line([(0, 192), (W, 192)], fill=(245, 248, 252, 255), width=1)
    draw.line([(0, 204), (W, 204)], fill=(75, 80, 90, 255), width=2) # drop shadow into road

    # -------------------------------------------------------------------------
    # Roadway: Dark Asphalt Road & White Markings (Rows 7 to 17, y = 208..576)
    # -------------------------------------------------------------------------
    asphalt_base = (46, 50, 58)
    asphalt_hi = (62, 66, 76)
    asphalt_sh = (32, 35, 42)
    draw.rectangle([0, 208, W, H], fill=asphalt_base)

    # Multi-tone aggregate gravel noise
    for ay in range(208, H, 4):
        for ax in range(0, W, 4):
            val = (ax * 17 + ay * 31) % 13
            if val == 0:
                draw.point((ax + 1, ay + 1), fill=asphalt_hi)
            elif val == 7:
                draw.point((ax + 2, ay + 2), fill=asphalt_sh)

    # Dashed White Center Lane Line (y = 370..378)
    for dx in range(16, W, 48):
        if 512 <= dx <= 704:
            continue # crosswalk area
        draw.rectangle([dx, 372, dx + 28, 376], fill=(242, 245, 250, 255), outline=(180, 185, 195, 255))

    # Broad Zebra Crosswalk (Pasy) at Columns 16 to 21 (x = 512..704, y = 208..540)
    for zx in range(512, 704, 32):
        draw.rectangle([zx + 4, 212, zx + 24, 540], fill=(240, 244, 250, 255), outline=(190, 195, 205, 255))
        # Realistic tire scuff rubber marks
        draw.line([(zx + 8, 310), (zx + 18, 330)], fill=(70, 75, 85, 160), width=3)
        draw.line([(zx + 10, 420), (zx + 20, 450)], fill=(70, 75, 85, 160), width=3)

    # Outer Bottom Roadway Barrier / Solid Curb (y = H - 32..H)
    draw.rectangle([0, H - 32, W, H], fill=(85, 90, 100, 255), outline=(45, 48, 55, 255))
    draw.line([(0, H - 32), (W, H - 32)], fill=(125, 130, 140, 255), width=2)

    # -------------------------------------------------------------------------
    # Street Furniture & Interactables:
    # -------------------------------------------------------------------------
    # Latarnia (Ornate Wrought Iron Streetlamp) at (10, 4) -> (320, 128)
    # Second streetlamp at (24, 4), Third at (34, 4)
    for lx in [10 * TILE, 24 * TILE, 34 * TILE]:
        ly = 4 * TILE
        # Warm sodium cast light puddle on pavement
        draw_contact_shadow(draw, lx + 16, ly + 28, 28, 14, alpha=90)
        light_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(light_img)
        ld.ellipse([lx - 32, ly - 16, lx + 64, ly + 64], fill=(255, 215, 80, 55))
        ld.ellipse([lx - 16, ly - 4, lx + 48, ly + 52], fill=(255, 230, 120, 70))
        im.alpha_composite(light_img)
        draw = ImageDraw.Draw(im)
        # Cast Iron Post
        draw.line([(lx + 16, ly - 36), (lx + 16, ly + 28)], fill=(22, 26, 34, 255), width=4)
        draw.ellipse([lx + 11, ly + 24, lx + 21, ly + 30], fill=(22, 26, 34, 255)) # base
        # Curved bracket & lantern housing
        draw.polygon([(lx + 9, ly - 36), (lx + 23, ly - 36), (lx + 20, ly - 20), (lx + 12, ly - 20)], fill=(22, 26, 34, 255))
        draw.rectangle([lx + 12, ly - 32, lx + 20, ly - 22], fill=(255, 245, 140, 255)) # glowing bulb

    # Park Bench with Sąsiadka at (8, 4) -> (256, 128)
    bx = 8 * TILE
    by = 4 * TILE
    draw_contact_shadow(draw, bx + 16, by + 26, 20, 8, alpha=130)
    # Wooden bench slats & cast iron frame
    draw.rectangle([bx + 4, by + 12, bx + 28, by + 24], fill=(138, 85, 45, 255), outline=(55, 30, 15, 255), width=2)
    draw.line([(bx + 5, by + 16), (bx + 27, by + 16)], fill=(175, 110, 65, 255))
    # Sąsiadka w berecie sitting on bench
    draw.ellipse([bx + 12, by + 2, bx + 20, by + 10], fill=(160, 45, 75, 255)) # beret bordowy
    draw.ellipse([bx + 13, by + 6, bx + 19, by + 12], fill=(234, 184, 144, 255)) # face
    draw.rectangle([bx + 11, by + 12, bx + 21, by + 22], fill=(95, 80, 105, 255)) # floral coat
    draw.rectangle([bx + 22, by + 16, bx + 27, by + 24], fill=(185, 145, 95, 255)) # wicker basket

    # City Pigeon (Gołąb) at (12, 5) -> (384, 160)
    px = 12 * TILE
    py = 5 * TILE
    draw_contact_shadow(draw, px + 16, py + 22, 8, 4, alpha=110)
    draw.ellipse([px + 10, py + 12, px + 22, py + 20], fill=(115, 125, 138, 255)) # body
    draw.ellipse([px + 18, py + 10, px + 24, py + 16], fill=(70, 120, 100, 255)) # iridescent head
    draw.point((px + 24, py + 13), fill=(245, 160, 40, 255)) # beak

    # Jogger (Biegacz) at (14, 4) -> (448, 128)
    jx = 14 * TILE
    jy = 4 * TILE
    draw_contact_shadow(draw, jx + 16, jy + 26, 10, 5, alpha=110)
    draw.ellipse([jx + 12, jy + 2, jx + 20, jy + 10], fill=(234, 184, 144, 255)) # head
    draw.rectangle([jx + 11, jy + 10, jx + 21, jy + 20], fill=(235, 245, 50, 255)) # neon yellow lycra!
    draw.rectangle([jx + 12, jy + 20, jx + 20, jy + 26], fill=(25, 28, 35, 255)) # black shorts

    # Save City Map
    out_path = os.path.join(MAPS_DIR, "city_bg.png")
    im.save(out_path, "PNG")
    print(f"Generated {out_path}: {im.size} (40x18 tiles)")


# ============================================================================
# 3. MAP: ŻABKA INTERIOR - 1024x576 (32x18 tiles)
# ============================================================================
def generate_zabka_bg():
    W = 32 * TILE # 1024
    H = 18 * TILE # 576
    im = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(im)

    # -------------------------------------------------------------------------
    # Floor: High-Gloss Supermarket Vinyl Tiles (Checkerboard Off-White & Cool Grey)
    # -------------------------------------------------------------------------
    tile_w = 32
    for ty in range(0, H, tile_w):
        for tx in range(0, W, tile_w):
            is_alt = ((tx // tile_w) + (ty // tile_w)) % 2 == 1
            col = (218, 224, 234, 255) if is_alt else (240, 243, 248, 255)
            draw.rectangle([tx, ty, tx + tile_w - 1, ty + tile_w - 1], fill=col)
            # Fine tile grout lines
            draw.line([(tx, ty), (tx + tile_w - 1, ty)], fill=(195, 202, 212, 255))
            draw.line([(tx, ty), (tx, ty + tile_w - 1)], fill=(195, 202, 212, 255))

    # Specular reflections of ceiling fluorescent luminaires on polished wax!
    fluor_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fluor_overlay)
    # 4 rows of fluorescent ceiling light reflections
    for ly in [110, 230, 350, 470]:
        for lx in range(48, W - 48, 128):
            fd.rectangle([lx, ly, lx + 72, ly + 14], fill=(255, 255, 255, 42))
            fd.rectangle([lx + 6, ly + 3, lx + 66, ly + 11], fill=(255, 255, 255, 75))
            fd.rectangle([lx + 16, ly + 5, lx + 56, ly + 9], fill=(255, 255, 255, 115))
    im.alpha_composite(fluor_overlay)
    draw = ImageDraw.Draw(im)

    # -------------------------------------------------------------------------
    # North Perimeter: Green Brand Wall Fascia & Shelving Vault (Rows 0 to 1)
    # -------------------------------------------------------------------------
    # Żabka Brand Green upper wall fascia (y = 0..16)
    draw.rectangle([0, 0, W, 16], fill=PAL['zabka_green'], outline=PAL['zabka_green_dk'], width=2)
    # Yellow stripe & logo
    draw.line([(0, 16), (W, 16)], fill=PAL['zabka_yellow'], width=2)
    for lx in range(64, W, 192):
        draw.arc([lx, 2, lx + 16, 14], 0, 180, fill=PAL['zabka_yellow'], width=2)

    # -------------------------------------------------------------------------
    # Wall Snack Shelves at x = 1..4 tiles (y = 0..63) -> (2, 0) is interactable!
    # -------------------------------------------------------------------------
    sx0 = 1 * TILE
    sx1 = 5 * TILE
    draw.rectangle([sx0, 16, sx1, 63], fill=(52, 58, 68, 255), outline=(26, 30, 36, 255))
    # Shelves
    for sy in [28, 42, 56]:
        draw.line([(sx0, sy), (sx1, sy)], fill=(185, 190, 200, 255), width=2)
    # Lays / Crunchips colorful packets (top shelf)
    chips_colors = [(235, 45, 45), (45, 130, 240), (245, 215, 35), (55, 200, 75), (235, 115, 35)]
    for ci, cx in enumerate(range(sx0 + 6, sx1 - 10, 14)):
        ccol = chips_colors[ci % len(chips_colors)]
        draw.rectangle([cx, 18, cx + 10, 26], fill=ccol)
    # Tarczyński Kabanosy & Jerky (mid shelf)
    for cx in range(sx0 + 6, sx1 - 10, 18):
        draw.rectangle([cx, 31, cx + 14, 40], fill=(168, 42, 32, 255))
        draw.line([(cx + 2, 33), (cx + 12, 33)], fill=(245, 215, 50, 255))
    # Chocolate bars & Prince Polo (bottom shelf)
    for cx in range(sx0 + 4, sx1 - 6, 10):
        draw.rectangle([cx, 45, cx + 7, 54], fill=(215, 135, 40, 255))

    # -------------------------------------------------------------------------
    # Walk-in Cold Beverage Wall at x = 7..24 tiles (y = 16..63) -> (8, 0) interactable!
    # -------------------------------------------------------------------------
    bx0 = 7 * TILE
    bx1 = 25 * TILE
    # Cold 6500K bright ice-blue interior
    draw.rectangle([bx0, 16, bx1, 63], fill=(16, 78, 125, 255), outline=(180, 225, 245, 255), width=2)
    # Double-pane glass cooler doors with aluminum mullions
    for dx in range(bx0, bx1, 48):
        draw.line([(dx, 16), (dx, 63)], fill=(210, 235, 250, 255), width=3)
        draw.line([(dx + 38, 28), (dx + 38, 52)], fill=(240, 245, 255, 255), width=2) # handle
        # Diagonal cold reflection streak across glass
        draw.line([(dx + 6, 18), (dx + 32, 60)], fill=(255, 255, 255, 90), width=2)
    # Colorful beverage cans on illuminated glass shelves
    for sy in [28, 44]:
        draw.line([(bx0, sy), (bx1, sy)], fill=(215, 240, 255, 255), width=1)
    # Shelf 1: Monster Energy, Oshee, Red Bull
    can_palette = [
        (45, 225, 65),  # Monster Green
        (245, 245, 250), # Monster White Zero
        (35, 150, 245),  # Oshee Blue
        (245, 130, 30),  # Oshee Orange
        (225, 35, 45),   # Coca-Cola Red
        (45, 95, 225),   # Pepsi Blue
        (245, 215, 40),  # Red Bull Gold
    ]
    for ci, cx in enumerate(range(bx0 + 8, bx1 - 12, 10)):
        cc = can_palette[ci % len(can_palette)]
        draw.rectangle([cx, 19, cx + 6, 27], fill=cc)
    # Shelf 2: Craft Beers & Lagers (Tyskie, Namysłów, Pinta)
    beer_palette = [(180, 40, 40), (225, 185, 40), (35, 125, 55), (145, 45, 165), (235, 90, 35)]
    for ci, cx in enumerate(range(bx0 + 8, bx1 - 12, 10)):
        bc = beer_palette[ci % len(beer_palette)]
        draw.rectangle([cx, 33, cx + 6, 43], fill=bc)

    # Right wall: Bakery & Pastry display (x = 25..31 tiles, y = 16..63)
    rx0 = 25 * TILE
    rx1 = 31 * TILE
    draw.rectangle([rx0, 16, rx1, 63], fill=(62, 54, 46, 255), outline=(32, 28, 24, 255))
    for sy in [30, 46]:
        draw.line([(rx0, sy), (rx1, sy)], fill=(195, 165, 125, 255), width=2)
    for bx in range(rx0 + 8, rx1 - 8, 16):
        draw.ellipse([bx, 20, bx + 12, 28], fill=(225, 165, 85, 255)) # fresh croissants!
        draw.ellipse([bx, 34, bx + 12, 44], fill=(195, 135, 65, 255)) # baguettes!

    # -------------------------------------------------------------------------
    # Checkout Counter (Row 2, y = 64..95)
    # -------------------------------------------------------------------------
    cnt_x0 = 3 * TILE # 96
    cnt_x1 = 7 * TILE # 224
    draw_contact_shadow(draw, (cnt_x0 + cnt_x1)//2, 96, (cnt_x1 - cnt_x0)//2, 10, alpha=130)
    # Counter body with green Żabka brand front kickplate
    draw.rectangle([cnt_x0, 68, cnt_x1, 95], fill=(228, 232, 238, 255), outline=(32, 38, 46, 255), width=2)
    draw.rectangle([cnt_x0 + 4, 76, cnt_x1 - 4, 92], fill=PAL['zabka_green'], outline=PAL['zabka_green_dk'], width=2)

    # Espresso Coffee Machine at (3, 2) -> (96, 64)
    esp_x = 3 * TILE
    draw.rectangle([esp_x + 6, 52, esp_x + 28, 72], fill=(28, 32, 40, 255), outline=(12, 14, 18, 255), width=2)
    draw.rectangle([esp_x + 9, 55, esp_x + 18, 60], fill=(235, 65, 45, 255)) # touchscreen
    draw.rectangle([esp_x + 12, 64, esp_x + 22, 71], fill=PAL['zabka_green']) # green paper cup

    # Steaming Hot Dog Roller Grill at (4, 2) -> (128, 64)
    grill_x = 4 * TILE
    draw.rectangle([grill_x + 4, 54, grill_x + 28, 72], fill=(175, 180, 190, 255), outline=(45, 50, 60, 255), width=2)
    # Polished heated rollers with sizzling sausages!
    for ry in [58, 62, 66]:
        draw.line([(grill_x + 6, ry), (grill_x + 26, ry)], fill=(195, 68, 42, 255), width=3) # sausages
        draw.line([(grill_x + 7, ry - 1), (grill_x + 25, ry - 1)], fill=(245, 140, 95, 255), width=1) # sizzle highlight
    # Squeeze bottles of sauces
    draw.rectangle([grill_x + 2, 60, grill_x + 5, 71], fill=(235, 45, 45, 255)) # ketchup
    draw.rectangle([grill_x + 27, 60, grill_x + 30, 71], fill=(245, 225, 65, 255)) # mustard

    # Cashier & POS Terminal at (5, 2) -> (160, 64)
    pos_x = 5 * TILE
    # Kasjer w zielonym fartuchu standing behind counter
    draw.ellipse([pos_x + 12, 38, pos_x + 20, 46], fill=(234, 184, 144, 255)) # head
    draw.rectangle([pos_x + 10, 46, pos_x + 22, 64], fill=PAL['zabka_green']) # polo shirt
    draw.ellipse([pos_x + 13, 50, pos_x + 19, 54], fill=PAL['zabka_yellow']) # name tag!
    # POS Touchscreen cash register
    draw.rectangle([pos_x + 6, 50, pos_x + 22, 68], fill=(24, 28, 36, 255), outline=(8, 10, 14, 255), width=2)
    draw.rectangle([pos_x + 8, 52, pos_x + 20, 64], fill=(65, 195, 245, 255)) # glowing POS screen
    # PIN Pad terminal
    draw.rectangle([pos_x + 24, 62, pos_x + 30, 72], fill=(42, 46, 56, 255))
    draw.point((pos_x + 27, 65), fill=(95, 245, 120, 255)) # green accept LED

    # -------------------------------------------------------------------------
    # Retail Gondola Aisles (Rows 4..5 and 8..9)
    # -------------------------------------------------------------------------
    # Gondolas at x = 8..14 and x = 18..24 (Rows 4..5 and Rows 8..9)
    def draw_gondola(gx0, gy0, gx1, gy1, theme='chips'):
        draw_contact_shadow(draw, (gx0 + gx1)//2, gy1 + 4, (gx1 - gx0)//2, 8, alpha=130)
        draw.rectangle([gx0, gy0, gx1, gy1], fill=(62, 68, 78, 255), outline=(28, 32, 38, 255), width=2)
        # Shelves with products
        mid_y = (gy0 + gy1)//2
        draw.line([(gx0, mid_y), (gx1, mid_y)], fill=(180, 185, 195, 255), width=2)
        if theme == 'chips':
            for px in range(gx0 + 6, gx1 - 6, 12):
                draw.rectangle([px, gy0 + 4, px + 8, mid_y - 2], fill=(235, 65, 45, 255))
                draw.rectangle([px, mid_y + 4, px + 8, gy1 - 2], fill=(45, 135, 235, 255))
        elif theme == 'drinks':
            for px in range(gx0 + 6, gx1 - 6, 10):
                draw.rectangle([px, gy0 + 3, px + 6, mid_y - 2], fill=(245, 145, 35, 255))
                draw.rectangle([px, mid_y + 3, px + 6, gy1 - 2], fill=(55, 195, 85, 255))

    draw_gondola(8 * TILE, 4 * TILE, 15 * TILE, 5 * TILE + 20, theme='chips')
    draw_gondola(18 * TILE, 4 * TILE, 25 * TILE, 5 * TILE + 20, theme='drinks')
    draw_gondola(8 * TILE, 8 * TILE, 15 * TILE, 9 * TILE + 20, theme='drinks')
    draw_gondola(18 * TILE, 8 * TILE, 25 * TILE, 9 * TILE + 20, theme='chips')

    # Ice Cream Chest Freezer at x = 27..30 tiles, y = 6..8
    fz_x0 = 27 * TILE
    fz_y0 = 6 * TILE
    fz_x1 = 31 * TILE
    fz_y1 = 9 * TILE
    draw_contact_shadow(draw, (fz_x0 + fz_x1)//2, fz_y1 + 4, (fz_x1 - fz_x0)//2, 10, alpha=130)
    draw.rounded_rectangle([fz_x0, fz_y0, fz_x1, fz_y1], radius=4, fill=(235, 238, 245, 255), outline=(130, 135, 145, 255), width=2)
    # Curved glass sliding lid
    draw.rectangle([fz_x0 + 4, fz_y0 + 6, fz_x1 - 4, fz_y1 - 6], fill=(160, 215, 240, 220), outline=(50, 95, 130, 255))
    draw.line([(fz_x0 + 8, fz_y0 + 8), (fz_x1 - 12, fz_y1 - 8)], fill=(255, 255, 255, 180), width=3) # glass reflection

    # -------------------------------------------------------------------------
    # Entrance / Exit Doors & "DO ZOBACZENIA" Welcome Mat at (5, 7) and (5, 16)
    # -------------------------------------------------------------------------
    # Green embossed carpet welcome mat at (5, 7) -> (160, 224)
    mat_x = 5 * TILE
    mat_y = 7 * TILE
    draw_contact_shadow(draw, mat_x + 16, mat_y + 16, 24, 16, alpha=110)
    draw.rounded_rectangle([mat_x - 4, mat_y + 2, mat_x + 36, mat_y + 30], radius=3, fill=PAL['zabka_green'], outline=PAL['zabka_green_dk'], width=2)
    draw.arc([mat_x + 6, mat_y + 6, mat_x + 26, mat_y + 22], 0, 180, fill=PAL['zabka_yellow'], width=2)
    draw.text((mat_x + 4, mat_y + 18), "EXIT", fill=PAL['zabka_yellow'])

    # Also south entrance at (5, 16) / (5, 17)
    smat_y = 16 * TILE
    draw_contact_shadow(draw, mat_x + 16, smat_y + 16, 24, 16, alpha=110)
    draw.rounded_rectangle([mat_x - 4, smat_y + 2, mat_x + 36, smat_y + 30], radius=3, fill=PAL['zabka_green'], outline=PAL['zabka_green_dk'], width=2)
    draw.text((mat_x + 2, smat_y + 10), "DO ZOBACZENIA", fill=(255, 255, 255, 255))

    # Outer wall borders
    draw.rectangle([0, 0, 16, H], fill=(42, 48, 56, 255)) # west wall
    draw.rectangle([W - 16, 0, W, H], fill=(42, 48, 56, 255)) # east wall
    draw.rectangle([0, H - 16, W, H], fill=(42, 48, 56, 255)) # south wall

    # Save Żabka Map
    out_path = os.path.join(MAPS_DIR, "zabka_bg.png")
    im.save(out_path, "PNG")
    print(f"Generated {out_path}: {im.size} (32x18 tiles)")


# ============================================================================
# 4. UPDATED TILESETS (32x32 Tiles per sheet)
# ============================================================================
def save_tileset(name, tiles):
    sheet = Image.new("RGBA", (len(tiles) * 32, 32), (0, 0, 0, 0))
    for i, t in enumerate(tiles):
        sheet.paste(t, (i * 32, 0))
    path = os.path.join(TILES_DIR, f"{name}.png")
    sheet.save(path, "PNG")
    print(f"Generated {name}.png: {sheet.size} ({len(tiles)} tiles)")

def build_apartment_tileset():
    tiles = []
    # Tile 0: Herringbone oak parquet floor
    t0 = Image.new("RGBA", (32, 32), (195, 142, 92, 255))
    d0 = ImageDraw.Draw(t0)
    for y in range(0, 32, 16):
        for x in range(0, 32, 16):
            direction = ((x // 16) + (y // 16)) % 2
            d0.rectangle([x, y, x + 15, y + 15], fill=(182, 130, 80, 255))
            if direction == 0:
                d0.line([(x + 2, y + 4), (x + 13, y + 4)], fill=(218, 168, 118, 255))
                d0.line([(x, y + 15), (x + 15, y + 15)], fill=(110, 68, 38, 255))
            else:
                d0.line([(x + 4, y + 2), (x + 4, y + 13)], fill=(218, 168, 118, 255))
                d0.line([(x + 15, y), (x + 15, y + 15)], fill=(110, 68, 38, 255))
    tiles.append(t0)

    # Tile 1: Plaster wall with wooden baseboard
    t1 = Image.new("RGBA", (32, 32), (218, 212, 202, 255))
    d1 = ImageDraw.Draw(t1)
    d1.rectangle([0, 24, 32, 32], fill=(110, 68, 38, 255), outline=(70, 40, 20, 255))
    d1.line([(0, 25), (32, 25)], fill=(154, 98, 58, 255))
    tiles.append(t1)

    # Tile 2: Ceiling Moulding
    t2 = Image.new("RGBA", (32, 32), (218, 212, 202, 255))
    d2 = ImageDraw.Draw(t2)
    d2.rectangle([0, 0, 32, 10], fill=(238, 235, 228, 255), outline=(160, 154, 144, 255))
    tiles.append(t2)

    # Tile 3: Dual-monitor Battlestation Desk
    t3 = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d3 = ImageDraw.Draw(t3)
    d3.rectangle([2, 10, 30, 30], fill=(42, 46, 56, 255), outline=(18, 20, 26, 255), width=2)
    # Screen 1 (IDE)
    d3.rectangle([2, 0, 15, 12], fill=(18, 22, 30, 255), outline=(6, 8, 12, 255))
    d3.rectangle([4, 2, 13, 10], fill=(24, 32, 48, 255))
    d3.line([(5, 4), (10, 4)], fill=(90, 210, 245, 255))
    # Screen 2 (Slack)
    d3.rectangle([16, 0, 29, 12], fill=(18, 22, 30, 255), outline=(6, 8, 12, 255))
    d3.rectangle([18, 2, 27, 10], fill=(38, 18, 38, 255))
    d3.ellipse([26, 0, 29, 3], fill=(245, 45, 55, 255)) # red badge
    tiles.append(t3)

    # Tile 4: Gaming Chair
    t4 = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d4 = ImageDraw.Draw(t4)
    d4.rounded_rectangle([8, 4, 24, 22], radius=3, fill=(26, 28, 36, 255), outline=(12, 14, 18, 255))
    d4.line([(11, 7), (21, 7)], fill=(225, 42, 48, 255), width=2)
    d4.line([(8, 24), (24, 24)], fill=(45, 50, 60, 255), width=2)
    tiles.append(t4)

    # Tile 5: Cozy Bed
    t5 = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d5 = ImageDraw.Draw(t5)
    d5.rectangle([2, 0, 30, 28], fill=(78, 48, 30, 255), outline=(42, 24, 14, 255))
    d5.rounded_rectangle([4, 2, 14, 12], radius=2, fill=(245, 246, 250, 255), outline=(180, 185, 195, 255))
    d5.rounded_rectangle([12, 8, 28, 26], radius=3, fill=(78, 108, 144, 255), outline=(42, 64, 92, 255))
    d5.line([(15, 12), (24, 18)], fill=(118, 152, 195, 255), width=2)
    tiles.append(t5)

    # Tile 6: Terracotta Monstera Plant
    t6 = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d6 = ImageDraw.Draw(t6)
    d6.polygon([(9, 16), (23, 16), (21, 28), (11, 28)], fill=(195, 85, 48, 255), outline=(110, 42, 22, 255))
    d6.ellipse([9, 2, 23, 14], fill=(42, 138, 58, 255), outline=(18, 72, 28, 255))
    d6.line([(16, 3), (16, 15)], fill=(85, 195, 105, 255))
    tiles.append(t6)

    # Tile 7: Entryway Coir Doormat / Exit
    t7 = t0.copy()
    d7 = ImageDraw.Draw(t7)
    d7.rounded_rectangle([3, 4, 29, 28], radius=3, fill=(180, 130, 75, 255), outline=(75, 45, 20, 255), width=2)
    d7.text((7, 10), "HOME", fill=(245, 225, 175, 255))
    tiles.append(t7)

    save_tileset("apartment", tiles)

def build_city_tileset():
    tiles = []
    # Tile 0: Asphalt Road with dashed center line
    t0 = Image.new("RGBA", (32, 32), (46, 50, 58, 255))
    d0 = ImageDraw.Draw(t0)
    for y in range(0, 32, 4):
        for x in range(0, 32, 4):
            if (x * 7 + y * 13) % 5 == 0:
                d0.point((x + 1, y + 1), fill=(62, 66, 76, 255))
    d0.line([(14, 8), (18, 8)], fill=(242, 245, 250, 255), width=2)
    d0.line([(14, 24), (18, 24)], fill=(242, 245, 250, 255), width=2)
    tiles.append(t0)

    # Tile 1: Granite Sidewalk Pavers
    t1 = Image.new("RGBA", (32, 32), (168, 174, 184, 255))
    d1 = ImageDraw.Draw(t1)
    for y in range(0, 32, 16):
        d1.line([(0, y), (32, y)], fill=(95, 100, 110, 255))
        for x in range((y % 32), 32, 32):
            d1.line([(x, y), (x, y + 16)], fill=(95, 100, 110, 255))
            d1.line([(x + 1, y + 1), (x + 31, y + 1)], fill=(205, 210, 220, 255))
    tiles.append(t1)

    # Tile 2: Brick Tenement Wall
    t2 = Image.new("RGBA", (32, 32), (162, 70, 54, 255))
    d2 = ImageDraw.Draw(t2)
    for y in range(0, 32, 6):
        d2.line([(0, y), (32, y)], fill=(210, 198, 185, 255))
        for x in range((y % 12), 32, 12):
            d2.line([(x, y), (x, y + 6)], fill=(210, 198, 185, 255))
    tiles.append(t2)

    # Tile 3: Tenement Window with Warm Glow
    t3 = t2.copy()
    d3 = ImageDraw.Draw(t3)
    d3.rectangle([6, 4, 26, 26], fill=(255, 225, 110, 255), outline=(35, 25, 20, 255), width=2)
    d3.line([(16, 4), (16, 26)], fill=(35, 25, 20, 255), width=2)
    d3.line([(6, 15), (26, 15)], fill=(35, 25, 20, 255), width=2)
    tiles.append(t3)

    # Tile 4: Granite Curb transition
    t4 = Image.new("RGBA", (32, 32), (46, 50, 58, 255))
    d4 = ImageDraw.Draw(t4)
    d4.rectangle([0, 0, 32, 16], fill=(168, 174, 184, 255))
    d4.rectangle([0, 16, 32, 24], fill=(210, 215, 224, 255), outline=(135, 140, 150, 255))
    tiles.append(t4)

    # Tile 5: Żabka Store Neon Signboard Awning
    t5 = t2.copy()
    d5 = ImageDraw.Draw(t5)
    d5.rectangle([1, 4, 31, 20], fill=PAL['zabka_green'], outline=PAL['zabka_green_hi'], width=2)
    d5.arc([9, 6, 23, 18], 0, 180, fill=PAL['zabka_yellow'], width=2)
    tiles.append(t5)

    # Tile 6: Automatic Sliding Entrance Door
    t6 = t1.copy()
    d6 = ImageDraw.Draw(t6)
    d6.rectangle([3, 0, 29, 28], fill=(22, 145, 54, 255), outline=(8, 65, 22, 255), width=2)
    d6.rectangle([5, 2, 14, 25], fill=(150, 220, 238, 200))
    d6.rectangle([18, 2, 27, 25], fill=(150, 220, 238, 200))
    d6.rounded_rectangle([4, 26, 28, 31], radius=2, fill=PAL['zabka_green'], outline=PAL['zabka_green_dk'])
    tiles.append(t6)

    # Tile 7: Żabka Showcase Display Window
    t7 = t2.copy()
    d7 = ImageDraw.Draw(t7)
    d7.rectangle([3, 2, 29, 28], fill=(16, 75, 95, 255), outline=(10, 48, 25, 255), width=2)
    d7.rounded_rectangle([9, 8, 23, 14], radius=3, fill=(235, 95, 45, 255)) # neon hot dog!
    tiles.append(t7)

    # Tile 8: Cast-iron Streetlamp (Upright Prop)
    t8 = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d8 = ImageDraw.Draw(t8)
    d8.line([(16, 4), (16, 30)], fill=(22, 26, 34, 255), width=3)
    d8.ellipse([11, 26, 21, 31], fill=(22, 26, 34, 255))
    d8.polygon([(11, 4), (21, 4), (18, 0), (14, 0)], fill=(22, 26, 34, 255))
    d8.rectangle([13, 3, 19, 7], fill=(255, 245, 140, 255))
    tiles.append(t8)

    # Tile 9: Crosswalk White Stripes
    t9 = t0.copy()
    d9 = ImageDraw.Draw(t9)
    for x in range(2, 32, 8):
        d9.rectangle([x, 4, x + 4, 28], fill=(240, 244, 250, 255))
    tiles.append(t9)

    # Tile 10: Garage Shutter
    t10 = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d10 = ImageDraw.Draw(t10)
    d10.rectangle([2, 4, 30, 30], fill=(68, 75, 88, 255), outline=(32, 36, 44, 255), width=2)
    for sy in range(8, 30, 5):
        d10.line([(4, sy), (28, sy)], fill=(95, 105, 120, 255), width=2)
    tiles.append(t10)

    save_tileset("city", tiles)

def build_zabka_tileset():
    tiles = []
    # Tile 0: Glossy checkerboard vinyl floor
    t0 = Image.new("RGBA", (32, 32), (240, 243, 248, 255))
    d0 = ImageDraw.Draw(t0)
    d0.rectangle([0, 0, 15, 15], fill=(218, 224, 234, 255))
    d0.rectangle([16, 16, 31, 31], fill=(218, 224, 234, 255))
    d0.rectangle([0, 0, 31, 31], outline=(195, 202, 212, 255))
    tiles.append(t0)

    # Tile 1: Beverage refrigerator back wall
    t1 = Image.new("RGBA", (32, 32), (16, 78, 125, 255))
    d1 = ImageDraw.Draw(t1)
    d1.rectangle([2, 1, 29, 31], fill=(16, 78, 125, 255), outline=(180, 225, 245, 255), width=2)
    # Cans
    cans = [(6, (45, 225, 65)), (12, (225, 35, 45)), (18, (35, 150, 245)), (24, (245, 215, 40))]
    for cx, ccol in cans:
        d1.rectangle([cx, 5, cx + 4, 12], fill=ccol)
    d1.line([(4, 14), (27, 14)], fill=(215, 240, 255, 255))
    for cx, ccol in cans:
        d1.rectangle([cx, 16, cx + 4, 24], fill=ccol)
    tiles.append(t1)

    # Tile 2: Wall Snack Shelves
    t2 = Image.new("RGBA", (32, 32), (52, 58, 68, 255))
    d2 = ImageDraw.Draw(t2)
    d2.rectangle([2, 0, 29, 31], fill=(52, 58, 68, 255), outline=(26, 30, 36, 255))
    for sy in [8, 18, 26]:
        d2.line([(3, sy), (28, sy)], fill=(185, 190, 200, 255), width=2)
    # Chips & snacks
    for px, pcol in [(5, (235, 45, 45)), (12, (45, 130, 240)), (19, (245, 215, 35)), (24, (55, 200, 75))]:
        d2.rectangle([px, 2, px + 4, 7], fill=pcol)
    tiles.append(t2)

    # Tile 3: Cash register counter with POS
    t3 = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d3 = ImageDraw.Draw(t3)
    d3.rectangle([2, 10, 30, 30], fill=(228, 232, 238, 255), outline=(32, 38, 46, 255), width=2)
    d3.rectangle([4, 16, 28, 26], fill=PAL['zabka_green'])
    d3.rectangle([6, 2, 17, 12], fill=(24, 28, 36, 255), outline=(8, 10, 14, 255))
    d3.rectangle([8, 4, 15, 10], fill=(65, 195, 245, 255)) # POS screen
    tiles.append(t3)

    # Tile 4: Hot dog roller grill & coffee machine
    t4 = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d4 = ImageDraw.Draw(t4)
    d4.rectangle([2, 10, 30, 30], fill=(228, 232, 238, 255), outline=(32, 38, 46, 255), width=2)
    d4.rectangle([4, 4, 16, 12], fill=(175, 180, 190, 255), outline=(45, 50, 60, 255))
    for ry in [6, 8, 10]:
        d4.line([(5, ry), (15, ry)], fill=(195, 68, 42, 255), width=2)
    d4.rectangle([18, 2, 28, 12], fill=(28, 32, 40, 255))
    tiles.append(t4)

    # Tile 5: Entrance / Exit Doormat "DO ZOBACZENIA"
    t5 = t0.copy()
    d5 = ImageDraw.Draw(t5)
    d5.rounded_rectangle([3, 4, 29, 28], radius=3, fill=PAL['zabka_green'], outline=PAL['zabka_green_dk'], width=2)
    d5.arc([11, 8, 21, 18], 0, 180, fill=PAL['zabka_yellow'], width=2)
    d5.text((7, 18), "EXIT", fill=PAL['zabka_yellow'])
    tiles.append(t5)

    # Tile 6: Center Promo Gondola
    t6 = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d6 = ImageDraw.Draw(t6)
    d6.rectangle([2, 6, 30, 28], fill=(62, 68, 78, 255), outline=(28, 32, 38, 255), width=2)
    d6.line([(3, 16), (29, 16)], fill=(180, 185, 195, 255), width=2)
    tiles.append(t6)

    # Tile 7: Brand Green Wall
    t7 = Image.new("RGBA", (32, 32), PAL['zabka_green'])
    d7 = ImageDraw.Draw(t7)
    d7.line([(0, 31), (32, 31)], fill=PAL['zabka_yellow'], width=2)
    tiles.append(t7)

    save_tileset("zabka", tiles)


# ============================================================================
# PHASE 2 MAPS & TILESETS
# ============================================================================

# ============================================================================
# 4. MAP: GARAŻ (DANNY'S GARAGE / UFC HQ) - 1024x576 (32x18 tiles)
# ============================================================================
def generate_garage_bg():
    W = 32 * TILE # 1024
    H = 18 * TILE # 576
    im = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(im)

    # 1. Base floor: Industrial concrete slab across rows 2..17 (y = 64..576)
    concrete_base = (76, 80, 86)
    draw.rectangle([0, 64, W, H], fill=concrete_base)
    # Stippled aggregate texture & fine noise
    for y in range(64, H, 4):
        for x in range(0, W, 4):
            val = (x * 19 + y * 37) % 17
            if val == 0:
                draw.point((x + 1, y + 1), fill=(95, 100, 108, 255))
            elif val == 8:
                draw.point((x + 2, y + 2), fill=(58, 62, 68, 255))
    # Expansion joints grid (every 64px) with dark crevice and light bevel
    for gx in range(0, W, 64):
        draw.line([(gx, 64), (gx, H)], fill=(45, 48, 52, 255), width=1)
        draw.line([(gx + 1, 64), (gx + 1, H)], fill=(105, 110, 118, 255), width=1)
    for gy in range(64, H, 64):
        draw.line([(0, gy), (W, gy)], fill=(45, 48, 52, 255), width=1)
        draw.line([(0, gy + 1), (W, gy + 1)], fill=(105, 110, 118, 255), width=1)
    # Concrete cracks (fracture lines)
    cracks = [
        [(180, 280), (195, 292), (210, 290), (225, 305), (240, 310)],
        [(680, 380), (695, 395), (715, 390), (730, 410)],
        [(410, 180), (425, 190), (440, 185), (460, 200)]
    ]
    for pts in cracks:
        for i in range(len(pts) - 1):
            draw.line([pts[i], pts[i+1]], fill=(38, 40, 44, 255), width=2)
            draw.line([(pts[i][0] + 1, pts[i][1] + 1), (pts[i+1][0] + 1, pts[i+1][1] + 1)], fill=(115, 120, 128, 255), width=1)

    # 2. Rubber gym puzzle mats in sparring / wrestling zone (cols 4..11 = x: 128..384, rows 4..9 = y: 128..320)
    for my in range(128, 320, 32):
        for mx in range(128, 384, 32):
            is_crimson = ((mx // 32) + (my // 32)) % 2 == 1
            mat_fill = (142, 38, 44, 255) if is_crimson else (32, 35, 40, 255)
            mat_hi = (175, 52, 58, 255) if is_crimson else (48, 52, 60, 255)
            mat_sh = (105, 26, 30, 255) if is_crimson else (20, 22, 26, 255)
            draw.rectangle([mx, my, mx + 31, my + 31], fill=mat_fill)
            # Puzzle seams & bevel border
            draw.line([(mx, my), (mx + 31, my)], fill=mat_hi)
            draw.line([(mx, my), (mx, my + 31)], fill=mat_hi)
            draw.line([(mx + 31, my), (mx + 31, my + 31)], fill=mat_sh)
            draw.line([(mx, my + 31), (mx + 31, my + 31)], fill=mat_sh)
            # Diamond-plate / crosshatch textured ribs
            for rx in range(mx + 4, mx + 28, 8):
                draw.line([(rx, my + 6), (rx + 4, my + 10)], fill=mat_hi, width=2)
                draw.line([(rx, my + 20), (rx + 4, my + 24)], fill=mat_hi, width=2)

    # 3. Oil slicks & tire skid marks
    oil_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(oil_img)
    # Large oil puddle at x: 450..560, y: 320..400
    od.ellipse([450, 320, 560, 400], fill=(24, 26, 30, 230))
    od.arc([460, 328, 550, 392], 20, 220, fill=(160, 40, 180, 180), width=3) # magenta
    od.arc([465, 332, 545, 388], 50, 260, fill=(30, 190, 220, 180), width=3) # cyan
    od.arc([470, 336, 540, 384], 80, 300, fill=(230, 205, 40, 180), width=2) # gold
    # Smaller oil slick near workbench at x: 200..260, y: 360..400
    od.ellipse([200, 360, 260, 400], fill=(28, 30, 34, 220))
    od.arc([208, 366, 252, 394], 30, 240, fill=(50, 200, 180, 160), width=2)
    # Tire skid marks
    od.arc([680, 240, 920, 500], 190, 270, fill=(28, 30, 34, 150), width=8)
    od.arc([700, 260, 940, 520], 190, 270, fill=(28, 30, 34, 150), width=8)
    im.alpha_composite(oil_img)
    draw = ImageDraw.Draw(im)

    # 4. North Cinder Block Wall (rows 0 to 1, y = 0..63)
    # Overhead steel beam (y = 0..12)
    draw_v_gradient(draw, 0, 12, (52, 56, 64), (36, 40, 46), 0, W)
    draw.line([(0, 12), (W, 12)], fill=(24, 26, 30, 255), width=2)
    # Rivets along beam
    for rx in range(16, W, 32):
        draw.ellipse([rx - 2, 4, rx + 2, 8], fill=(95, 100, 110, 255), outline=(25, 28, 32, 255))
    # Cinder block wall (y = 12..60)
    cb_col = (148, 152, 160)
    draw.rectangle([0, 12, W, 60], fill=cb_col)
    # Cinder blocks: rows of 16px high, alternating 32px wide
    for cby in range(12, 60, 16):
        draw.line([(0, cby), (W, cby)], fill=(85, 90, 98, 255), width=2)
        shift = ((cby - 12) // 16) * 16
        for cbx in range(shift, W, 32):
            draw.line([(cbx, cby), (cbx, cby + 16)], fill=(85, 90, 98, 255), width=2)
            # Stippling texture on block
            draw.point((cbx + 8, cby + 4), fill=(180, 185, 195, 255))
            draw.point((cbx + 22, cby + 10), fill=(110, 115, 122, 255))
    # Steel protective baseboard (y = 60..64)
    draw.rectangle([0, 60, W, 64], fill=(55, 58, 65, 255), outline=(32, 34, 38, 255))

    # 5. Wall Tool Pegboard & Red Tool Chest at (4, 2) -> (x: 100..164, y: 16..96)
    # Perforated pegboard
    draw.rectangle([98, 14, 164, 58], fill=(70, 75, 82, 255), outline=(42, 45, 50, 255), width=2)
    for py in range(20, 56, 6):
        for px in range(104, 160, 6):
            draw.point((px, py), fill=(28, 30, 34, 255))
    # Pegboard hung tools
    # Wrenches
    draw.line([(108, 22), (108, 48)], fill=(210, 215, 225, 255), width=3)
    draw.ellipse([106, 20, 110, 24], fill=(210, 215, 225, 255))
    draw.line([(116, 26), (116, 46)], fill=(210, 215, 225, 255), width=2)
    # Claw hammer
    draw.line([(126, 26), (126, 50)], fill=(160, 110, 65, 255), width=2)
    draw.rectangle([122, 22, 130, 26], fill=(190, 195, 205, 255))
    # Screwdrivers with red handles
    draw.rectangle([136, 20, 139, 30], fill=(225, 45, 45, 255))
    draw.line([(137, 30), (137, 46)], fill=(200, 205, 215, 255), width=2)
    draw.rectangle([144, 24, 147, 32], fill=(245, 205, 30, 255))
    draw.line([(145, 32), (145, 44)], fill=(200, 205, 215, 255), width=2)
    # Handsaw
    draw.polygon([(150, 22), (160, 34), (150, 48)], fill=(185, 190, 200, 255))

    # Red Tool Chest at (4, 2) -> (x = 110..156, y = 56..94)
    draw_contact_shadow(draw, 133, 94, 26, 8, alpha=140)
    draw.rectangle([110, 56, 156, 92], fill=(195, 35, 30, 255), outline=(105, 18, 16, 255), width=2)
    draw.line([(111, 57), (155, 57)], fill=(240, 75, 70, 255))
    # 5 drawers with chrome handles
    for dy in range(62, 90, 6):
        draw.line([(112, dy), (154, dy)], fill=(120, 20, 18, 255), width=1)
        draw.line([(118, dy - 2), (148, dy - 2)], fill=(235, 240, 250, 255), width=2)
    # Caster wheels
    draw.rectangle([114, 91, 118, 95], fill=(30, 32, 36, 255))
    draw.rectangle([148, 91, 152, 95], fill=(30, 32, 36, 255))

    # 6. Hanging Punching Bag at (6, 2..3) -> (x: 192, y: 30..106)
    draw_contact_shadow(draw, 192, 108, 14, 6, alpha=130)
    # Steel ceiling chains
    draw.line([(192, 12), (188, 34)], fill=(180, 185, 195, 255), width=2)
    draw.line([(192, 12), (196, 34)], fill=(180, 185, 195, 255), width=2)
    # Heavy leather punching bag
    draw.rounded_rectangle([182, 34, 202, 102], radius=5, fill=(65, 42, 32, 255), outline=(32, 20, 15, 255), width=2)
    draw.line([(184, 38), (184, 98)], fill=(110, 75, 60, 255), width=2)
    draw.rectangle([183, 56, 201, 66], fill=(180, 35, 30, 255))
    draw.text((185, 57), "UFC", fill=(255, 255, 255, 255))

    # Stacked tires at (3, 2) -> (x: 80..106, y: 64..94)
    draw_contact_shadow(draw, 93, 94, 18, 6, alpha=130)
    for ty in [82, 72, 62]:
        draw.ellipse([80, ty, 106, ty + 12], fill=(30, 33, 38, 255), outline=(15, 16, 20, 255), width=2)
        draw.ellipse([86, ty + 2, 100, ty + 10], fill=(60, 65, 75, 255))
        draw.ellipse([90, ty + 4, 96, ty + 8], fill=(20, 22, 26, 255))

    # 7. Ceiling Digital Projector & UFC 300 Fight Wall Projection at (8, 2) -> (x: 236..336, y: 8..62)
    draw.rectangle([276, 6, 296, 14], fill=(28, 30, 36, 255), outline=(12, 14, 18, 255))
    draw.point((279, 10), fill=(60, 190, 255, 255))
    # Projector light beam
    beam_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beam_layer)
    bd.polygon([(286, 14), (232, 60), (340, 60)], fill=(200, 235, 255, 45))
    im.alpha_composite(beam_layer)
    draw = ImageDraw.Draw(im)

    # Wall Projection Screen at (8, 2) -> (x = 236..336, y = 16..58)
    draw.rectangle([236, 16, 336, 58], fill=(16, 24, 40, 255), outline=(65, 140, 210, 255), width=2)
    # Octagon cage canvas
    draw.polygon([(256, 22), (316, 22), (330, 48), (242, 48)], fill=(32, 42, 58, 255), outline=(80, 105, 135, 255))
    draw.text((268, 24), "UFC 300", fill=(245, 220, 50, 255))
    # Fighters in octagon
    draw.ellipse([272, 32, 278, 38], fill=(234, 184, 144, 255))
    draw.rectangle([270, 38, 280, 46], fill=(215, 40, 40, 255))
    draw.line([(280, 36), (292, 34)], fill=(234, 184, 144, 255), width=2)
    draw.ellipse([294, 30, 300, 36], fill=(234, 184, 144, 255))
    draw.rectangle([292, 36, 302, 46], fill=(40, 100, 220, 255))
    # Ambient projection glow
    proj_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pg = ImageDraw.Draw(proj_glow)
    pg.ellipse([220, 4, 352, 70], fill=(80, 170, 255, 35))
    im.alpha_composite(proj_glow)
    draw = ImageDraw.Draw(im)

    # 8. Beer Fridge at (14, 2) -> (x: 436..476, y = 28..92)
    draw_contact_shadow(draw, 456, 94, 24, 8, alpha=130)
    draw.rectangle([436, 28, 476, 92], fill=(32, 36, 44, 255), outline=(16, 18, 22, 255), width=2)
    draw.rectangle([440, 32, 472, 84], fill=(16, 75, 120, 255), outline=(140, 210, 245, 255))
    beer_cans = [(443, (225, 45, 45)), (449, (245, 205, 35)), (455, (45, 175, 75)), (461, (215, 120, 35)), (467, (50, 130, 230))]
    for sy in [46, 62, 78]:
        draw.line([(441, sy), (471, sy)], fill=(185, 225, 250, 255), width=1)
        for bx, bcol in beer_cans:
            draw.rectangle([bx, sy - 9, bx + 4, sy], fill=bcol)
    draw.line([(444, 34), (466, 82)], fill=(255, 255, 255, 95), width=2)
    draw.rectangle([440, 85, 472, 90], fill=(20, 22, 28, 255))
    for vy in range(86, 90, 2):
        draw.line([(442, vy), (470, vy)], fill=(50, 55, 65, 255))

    # 9. Heavy Metal Exit Door to Pub at (16..17, 6) -> (x: 512..576, y: 172..224)
    draw_contact_shadow(draw, 544, 224, 36, 8, alpha=120)
    draw.rectangle([512, 172, 576, 224], fill=(52, 56, 64, 255), outline=(24, 26, 30, 255), width=2)
    draw.rectangle([515, 175, 542, 222], fill=(68, 74, 85, 255), outline=(35, 38, 44, 255))
    draw.rectangle([545, 175, 573, 222], fill=(68, 74, 85, 255), outline=(35, 38, 44, 255))
    draw.line([(518, 200), (539, 200)], fill=(215, 220, 230, 255), width=3)
    draw.line([(548, 200), (569, 200)], fill=(215, 220, 230, 255), width=3)
    # Hazard threshold
    for hx in range(512, 576, 12):
        draw.polygon([(hx, 232), (hx + 6, 224), (hx + 12, 224), (hx + 6, 232)], fill=(245, 215, 35, 255))
    # Green Emergency Exit Sign
    draw.rectangle([530, 156, 558, 170], fill=(12, 145, 45, 255), outline=(160, 255, 180, 255), width=2)
    draw.text((534, 158), "EXIT", fill=(255, 255, 255, 255))
    sign_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sg = ImageDraw.Draw(sign_glow)
    sg.ellipse([516, 146, 572, 180], fill=(45, 225, 75, 40))
    im.alpha_composite(sign_glow)
    draw = ImageDraw.Draw(im)

    # 10. Beat-up Leather Sofa at (20..23, 6..7) -> (x: 640..740, y: 176..224)
    draw_contact_shadow(draw, 690, 224, 54, 12, alpha=130)
    draw.rounded_rectangle([640, 176, 740, 222], radius=4, fill=(120, 72, 42, 255), outline=(60, 34, 18, 255), width=2)
    draw.line([(644, 192), (736, 192)], fill=(75, 42, 22, 255), width=2)
    draw.rounded_rectangle([646, 194, 674, 218], radius=2, fill=(145, 88, 52, 255), outline=(85, 48, 26, 255))
    draw.rounded_rectangle([676, 194, 704, 218], radius=2, fill=(145, 88, 52, 255), outline=(85, 48, 26, 255))
    draw.rounded_rectangle([706, 194, 734, 218], radius=2, fill=(145, 88, 52, 255), outline=(85, 48, 26, 255))
    # Silver duct tape patch
    draw.rectangle([642, 186, 650, 196], fill=(195, 200, 208, 255), outline=(130, 135, 142, 255))
    draw.line([(644, 188), (648, 194)], fill=(230, 235, 242, 255))

    # 11. Barbell & Bumper Plates on floor at (7, 4) -> (x: 210..260, y: 120..136)
    draw_contact_shadow(draw, 235, 130, 28, 5, alpha=110)
    draw.line([(212, 128), (258, 128)], fill=(210, 215, 225, 255), width=3)
    draw.ellipse([210, 120, 218, 136], fill=(28, 30, 35, 255), outline=(10, 12, 15, 255), width=2)
    draw.ellipse([252, 120, 260, 136], fill=(28, 30, 35, 255), outline=(10, 12, 15, 255), width=2)

    # 12. Ceiling Fluorescent Tube Luminaires
    fluor_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fld = ImageDraw.Draw(fluor_layer)
    for fx in [160, 480, 800]:
        draw.rectangle([fx - 32, 6, fx + 32, 12], fill=(65, 70, 78, 255), outline=(28, 30, 34, 255))
        draw.rectangle([fx - 30, 8, fx + 30, 11], fill=(245, 252, 255, 255))
        fld.polygon([(fx - 24, 12), (fx + 24, 12), (fx + 120, 340), (fx - 120, 340)], fill=(235, 248, 255, 18))
    im.alpha_composite(fluor_layer)
    draw = ImageDraw.Draw(im)

    # Perimeter solid borders
    draw.rectangle([0, 0, 16, H], fill=(42, 45, 52, 255))
    draw.rectangle([W - 16, 0, W, H], fill=(42, 45, 52, 255))
    draw.rectangle([0, H - 16, W, H], fill=(42, 45, 52, 255))

    out_path = os.path.join(MAPS_DIR, "garage_bg.png")
    im.save(out_path, "PNG")
    print(f"Generated {out_path}: {im.size} (32x18 tiles)")


# ============================================================================
# 5. MAP: PUB "CZARNY KRĄŻEK" - 1024x576 (32x18 tiles)
# ============================================================================
def generate_pub_bg():
    W = 32 * TILE # 1024
    H = 18 * TILE # 576
    im = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(im)

    # 1. Base floor: Aged dark mahogany floorboards across rows 2..17 (y = 64..576)
    mahogany_base = (88, 40, 22)
    draw.rectangle([0, 64, W, H], fill=mahogany_base)
    for py in range(64, H, 8):
        draw.line([(0, py), (W, py)], fill=(48, 20, 10, 255), width=1)
        shift = ((py - 64) // 8 % 3) * 24
        for px in range(shift, W, 48):
            draw.line([(px, py), (px, py + 8)], fill=(48, 20, 10, 255), width=1)
            draw.line([(px + 2, py + 2), (px + 44, py + 2)], fill=(125, 62, 34, 255))
            draw.line([(px + 6, py + 5), (px + 38, py + 5)], fill=(65, 28, 14, 255))
            draw.point((px + 2, py + 4), fill=(35, 16, 8, 255))
            draw.point((px + 45, py + 4), fill=(35, 16, 8, 255))

    # Amber pendant light reflections on varnished mahogany floor
    sheen_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sheen_layer)
    for lx in [160, 280, 400, 600, 750, 900]:
        for ly in [180, 320, 460]:
            sd.ellipse([lx - 40, ly - 20, lx + 40, ly + 20], fill=(255, 185, 60, 25))
            sd.ellipse([lx - 20, ly - 10, lx + 20, ly + 10], fill=(255, 210, 90, 40))
    im.alpha_composite(sheen_layer)
    draw = ImageDraw.Draw(im)

    # 2. North Wall (rows 0 to 1, y = 0..63)
    draw.rectangle([0, 0, W, 42], fill=(115, 45, 34, 255))
    for by in range(0, 42, 6):
        draw.line([(0, by), (W, by)], fill=(60, 24, 18, 255), width=1)
        shift = (by // 6 % 2) * 8
        for bx in range(shift, W, 16):
            draw.line([(bx, by), (bx, by + 6)], fill=(60, 24, 18, 255), width=1)
            draw.point((bx + 3, by + 2), fill=(145, 62, 48, 255))
    # Acoustic wall diffusers
    for ax in [40, 650]:
        draw.rectangle([ax, 8, ax + 56, 38], fill=(95, 52, 28, 255), outline=(48, 24, 12, 255), width=2)
        for dy in range(12, 36, 6):
            for dx in range(ax + 4, ax + 52, 8):
                h_val = ((dx * 7 + dy * 13) % 4) * 2
                draw.rectangle([dx, dy, dx + 6, dy + 4], fill=(135 + h_val * 15, 75 + h_val * 8, 40 + h_val * 5, 255), outline=(40, 20, 10, 255))
    draw.rectangle([0, 42, W, 64], fill=(58, 26, 14, 255), outline=(32, 14, 8, 255))
    draw.line([(0, 42), (W, 42)], fill=(110, 55, 28, 255), width=2)

    # 3. Backlit Liquor Bottle Shelves behind the bar (x = 128..400, y = 6..60)
    draw.rectangle([128, 6, 400, 60], fill=(22, 12, 18, 255), outline=(75, 36, 18, 255), width=2)
    bottle_palette = [
        (235, 165, 35),  # Amber whiskey
        (35, 195, 95),   # Emerald absinthe
        (215, 35, 55),   # Ruby Campari
        (65, 165, 235),  # Sapphire gin
        (240, 215, 120), # Golden rum
        (230, 235, 245), # Clear vodka
    ]
    for si, sy in enumerate([20, 36, 52]):
        draw.line([(130, sy + 6), (398, sy + 6)], fill=(255, 225, 160, 220), width=2)
        for bi, bx in enumerate(range(134, 394, 8)):
            bcol = bottle_palette[(bi + si * 2) % len(bottle_palette)]
            draw.rectangle([bx + 1, sy - 12, bx + 3, sy - 8], fill=(200, 210, 220, 255))
            draw.rectangle([bx, sy - 8, bx + 4, sy + 4], fill=bcol)
            draw.point((bx + 1, sy - 6), fill=(255, 255, 255, 220))

    bottle_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bgd = ImageDraw.Draw(bottle_glow)
    bgd.ellipse([120, 0, 408, 66], fill=(245, 160, 40, 40))
    im.alpha_composite(bottle_glow)
    draw = ImageDraw.Draw(im)

    # 4. Curved Teak Bar Counter (rows 2..3, x = 120..400, y = 64..118)
    draw_contact_shadow(draw, 260, 118, 145, 14, alpha=140)
    draw.rectangle([128, 76, 392, 114], fill=(62, 28, 16, 255), outline=(32, 14, 8, 255))
    for fx in range(132, 388, 4):
        draw.line([(fx, 78), (fx, 112)], fill=(44, 20, 10, 255))
    draw.rounded_rectangle([120, 64, 400, 80], radius=6, fill=(162, 92, 48, 255), outline=(85, 45, 22, 255), width=2)
    draw.line([(124, 66), (396, 66)], fill=(215, 138, 82, 255), width=2)
    # Brass footrail
    draw.line([(124, 112), (396, 112)], fill=(225, 185, 55, 255), width=3)
    draw.line([(124, 111), (396, 111)], fill=(255, 235, 140, 255), width=1)
    for sx in range(144, 380, 48):
        draw.rectangle([sx - 2, 108, sx + 2, 116], fill=(195, 155, 40, 255))

    # 4 Velvet-Padded Bar Stools
    for stx in [156, 216, 306, 366]:
        draw_contact_shadow(draw, stx, 128, 12, 6, alpha=130)
        draw.line([(stx - 7, 98), (stx - 9, 126)], fill=(48, 22, 12, 255), width=2)
        draw.line([(stx + 7, 98), (stx + 9, 126)], fill=(48, 22, 12, 255), width=2)
        draw.line([(stx - 8, 114), (stx + 8, 114)], fill=(185, 150, 45, 255))
        draw.ellipse([stx - 10, 92, stx + 10, 104], fill=(155, 26, 38, 255), outline=(80, 12, 20, 255), width=2)
        draw.ellipse([stx - 7, 94, stx + 7, 100], fill=(195, 42, 58, 255))

    # Triple Brass Draft Beer Font at (8, 3) -> (x: 256, y: 56..80)
    draw.rectangle([250, 60, 262, 78], fill=(225, 185, 55, 255), outline=(135, 105, 25, 255), width=2)
    for ti, tx in enumerate([252, 256, 260]):
        draw.line([(tx, 52), (tx, 60)], fill=(30, 25, 25, 255), width=2)
        draw.ellipse([tx - 1, 50, tx + 1, 54], fill=(180, 30, 30) if ti == 1 else (240, 200, 40))
    draw.rectangle([246, 78, 266, 82], fill=(185, 190, 200, 255), outline=(95, 100, 110, 255))

    # 5. DJ Booth & Dual Technics Turntables at (10, 2..3) -> (x: 310..386, y: 56..82)
    draw.rectangle([342, 60, 356, 76], fill=(28, 30, 35, 255), outline=(12, 14, 18, 255))
    draw.line([(346, 63), (346, 72)], fill=(45, 215, 65, 255))
    draw.line([(346, 63), (346, 66)], fill=(245, 45, 45, 255))
    draw.line([(352, 63), (352, 72)], fill=(45, 215, 65, 255))
    draw.line([(352, 63), (352, 66)], fill=(245, 45, 45, 255))
    draw.rectangle([345, 73, 353, 75], fill=(215, 220, 230, 255))
    # Turntable 1
    draw.rectangle([314, 60, 340, 76], fill=(190, 195, 205, 255), outline=(50, 55, 65, 255))
    draw.ellipse([317, 61, 335, 75], fill=(20, 22, 26, 255))
    draw.point((317, 63), fill=(45, 160, 255, 255))
    draw.line([(336, 62), (333, 70)], fill=(225, 230, 240, 255))
    # Turntable 2
    draw.rectangle([358, 60, 384, 76], fill=(190, 195, 205, 255), outline=(50, 55, 65, 255))
    draw.ellipse([361, 61, 379, 75], fill=(20, 22, 26, 255))
    draw.point((361, 63), fill=(45, 160, 255, 255))
    draw.line([(380, 62), (377, 70)], fill=(225, 230, 240, 255))

    # 6. Massive Crates of Vinyl Records at (14, 2) -> (x: 440..500, y: 38..92)
    draw_contact_shadow(draw, 470, 94, 32, 8, alpha=130)
    draw.rectangle([440, 52, 500, 92], fill=(110, 62, 34, 255), outline=(55, 30, 16, 255), width=2)
    draw.line([(470, 52), (470, 92)], fill=(55, 30, 16, 255), width=2)
    spine_colors = [(225, 45, 45), (45, 120, 230), (245, 215, 35), (240, 240, 245), (35, 35, 40), (55, 195, 75), (225, 115, 35), (175, 45, 185)]
    for ci, cx in enumerate(range(444, 468, 3)):
        draw.line([(cx, 38), (cx, 68)], fill=spine_colors[ci % len(spine_colors)], width=2)
    for ci, cx in enumerate(range(474, 498, 3)):
        draw.line([(cx, 38), (cx, 68)], fill=spine_colors[(ci + 3) % len(spine_colors)], width=2)
    draw.rectangle([456, 12, 484, 36], fill=(30, 20, 15, 255), outline=(195, 160, 55, 255), width=2)
    draw.ellipse([460, 16, 480, 32], fill=(235, 195, 55, 255), outline=(145, 115, 30, 255))
    draw.ellipse([467, 21, 473, 27], fill=(195, 45, 45, 255))

    # 7. Heavy Pub Exit Door to Alley at (16..17, 6) -> (x: 512..576, y: 172..224)
    draw_contact_shadow(draw, 544, 224, 36, 8, alpha=120)
    draw.rectangle([512, 172, 576, 224], fill=(55, 28, 16, 255), outline=(28, 14, 8, 255), width=2)
    draw.rectangle([518, 178, 540, 218], fill=(78, 38, 22, 255), outline=(38, 18, 10, 255))
    draw.rectangle([548, 178, 570, 218], fill=(78, 38, 22, 255), outline=(38, 18, 10, 255))
    draw.rectangle([516, 216, 572, 222], fill=(215, 175, 45, 255))
    draw.rectangle([538, 196, 542, 204], fill=(235, 195, 55, 255))
    draw.rectangle([530, 156, 558, 170], fill=(12, 145, 45, 255), outline=(160, 255, 180, 255), width=2)
    draw.text((534, 158), "EXIT", fill=(255, 255, 255, 255))

    # 8. Cozy Lounge Area with Persian Tavern Rug & Tables (x = 600..960, y = 160..520)
    rug_x0, rug_y0, rug_x1, rug_y1 = 620, 220, 940, 480
    draw.rectangle([rug_x0, rug_y0, rug_x1, rug_y1], fill=(115, 28, 36, 255), outline=(215, 175, 75, 255), width=3)
    draw.rectangle([rug_x0 + 12, rug_y0 + 12, rug_x1 - 12, rug_y1 - 12], fill=(42, 28, 54, 255), outline=(215, 175, 75, 255), width=2)
    draw.ellipse([(rug_x0 + rug_x1)//2 - 40, (rug_y0 + rug_y1)//2 - 30, (rug_x0 + rug_x1)//2 + 40, (rug_y0 + rug_y1)//2 + 30], fill=(135, 35, 45, 255), outline=(225, 195, 85, 255), width=2)

    for tx, ty in [(700, 280), (840, 400)]:
        draw_contact_shadow(draw, tx, ty + 24, 28, 10, alpha=130)
        draw.ellipse([tx - 26, ty - 12, tx + 26, ty + 12], fill=(135, 68, 36, 255), outline=(65, 30, 15, 255), width=2)
        draw.ellipse([tx - 22, ty - 10, tx + 22, ty + 8], fill=(162, 85, 45, 255))
        draw.ellipse([tx - 4, ty - 4, tx + 4, ty + 2], fill=(215, 175, 45, 255))
        draw.ellipse([tx - 2, ty - 10, tx + 2, ty - 4], fill=(255, 215, 80, 255))
        draw.rectangle([tx + 8, ty - 6, tx + 14, ty + 2], fill=(235, 185, 45, 255), outline=(145, 105, 25, 255))

    # 9. Warm Hanging Edison Bulbs
    bulb_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bld = ImageDraw.Draw(bulb_layer)
    edisons = [(180, 36), (280, 28), (380, 36), (620, 30), (760, 24), (880, 32)]
    for bx, by in edisons:
        draw.line([(bx, 0), (bx, by)], fill=(22, 18, 16, 255), width=2)
        draw.rectangle([bx - 3, by, bx + 3, by + 4], fill=(195, 155, 45, 255))
        draw.ellipse([bx - 5, by + 4, bx + 5, by + 16], fill=(255, 205, 75, 255), outline=(180, 105, 25, 255))
        draw.point((bx, by + 10), fill=(255, 250, 200, 255))
        bld.ellipse([bx - 60, by - 10, bx + 60, by + 110], fill=(255, 175, 40, 35))
        bld.ellipse([bx - 30, by, bx + 30, by + 70], fill=(255, 210, 80, 50))
    im.alpha_composite(bulb_layer)
    draw = ImageDraw.Draw(im)

    # Perimeter solid borders
    draw.rectangle([0, 0, 16, H], fill=(32, 14, 8, 255))
    draw.rectangle([W - 16, 0, W, H], fill=(32, 14, 8, 255))
    draw.rectangle([0, H - 16, W, H], fill=(32, 14, 8, 255))

    out_path = os.path.join(MAPS_DIR, "pub_bg.png")
    im.save(out_path, "PNG")
    print(f"Generated {out_path}: {im.size} (32x18 tiles)")


# ============================================================================
# 6. MAP: ZAUŁKI STARÓWKI (ALLEY) - 1280x576 (40x18 tiles)
# ============================================================================
def generate_alley_bg():
    W = 40 * TILE # 1280
    H = 18 * TILE # 576
    im = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(im)

    # 1. Rainy night sky (rows 0..1, y = 0..32)
    draw_v_gradient(draw, 0, 32, (18, 22, 34), (36, 42, 54), 0, W)

    # 2. Historic Weathered Red Brick Tenement Facade (rows 1..2, y = 24..96)
    brick_main = (142, 56, 44)
    brick_hi = (175, 75, 62)
    brick_sh = (105, 38, 30)
    mortar = (72, 42, 36)
    draw.rectangle([0, 24, W, 96], fill=brick_main)
    for by in range(24, 96, 6):
        draw.line([(0, by), (W, by)], fill=mortar, width=1)
        shift = ((by - 24) // 6 % 2) * 8
        for bx in range(shift, W, 16):
            draw.line([(bx, by), (bx, by + 6)], fill=mortar, width=1)
            draw.point((bx + 3, by + 2), fill=brick_hi)
            draw.point((bx + 11, by + 4), fill=brick_sh)

    # Architectural Stone Cornice at roofline (y = 20..26)
    draw.rectangle([0, 20, W, 26], fill=(95, 100, 110, 255), outline=(55, 58, 65, 255))

    # Cast-Iron Fire Escapes at x = 200..280 and x = 860..940 (y = 26..96)
    for fx in [200, 860]:
        draw.rectangle([fx, 45, fx + 80, 52], fill=(28, 32, 38, 255), outline=(15, 18, 22, 255))
        draw.rectangle([fx, 78, fx + 80, 85], fill=(28, 32, 38, 255), outline=(15, 18, 22, 255))
        draw.line([(fx, 36), (fx + 80, 36)], fill=(28, 32, 38, 255), width=2)
        draw.line([(fx, 69), (fx + 80, 69)], fill=(28, 32, 38, 255), width=2)
        for rx in range(fx + 6, fx + 80, 12):
            draw.line([(rx, 36), (rx, 45)], fill=(28, 32, 38, 255), width=1)
            draw.line([(rx, 69), (rx, 78)], fill=(28, 32, 38, 255), width=1)
        draw.line([(fx + 12, 45), (fx + 12, 94)], fill=(35, 38, 46, 255), width=2)
        draw.line([(fx + 24, 45), (fx + 24, 94)], fill=(35, 38, 46, 255), width=2)
        for ly in range(50, 94, 7):
            draw.line([(fx + 12, ly), (fx + 24, ly)], fill=(35, 38, 46, 255), width=2)

    # Peeling concert / event posters on brick wall
    posters = [
        (60, 48, (245, 220, 90)),
        (150, 52, (225, 65, 45)),
        (480, 46, (60, 180, 240)),
        (650, 50, (230, 235, 245)),
        (780, 48, (235, 120, 40)),
        (1020, 52, (245, 220, 90))
    ]
    for px, py, pcol in posters:
        draw.rectangle([px, py, px + 22, py + 30], fill=pcol, outline=(35, 25, 20, 255))
        draw.polygon([(px + 16, py + 30), (px + 22, py + 24), (px + 16, py + 24)], fill=brick_main)
        for ty in range(py + 6, py + 26, 5):
            draw.line([(px + 3, ty), (px + 19, ty)], fill=(35, 35, 40, 255), width=1)

    # Graffiti Murals
    draw.text((382, 47), "OSAKA", fill=(215, 35, 110, 255))
    draw.text((380, 45), "OSAKA", fill=(60, 235, 255, 255))
    draw.text((702, 50), "THE PACK", fill=(245, 140, 30, 255))
    draw.text((700, 48), "THE PACK", fill=(255, 235, 60, 255))

    # Upper Tenement Windows with rain streaks
    for wx in range(32, W - 64, 56):
        if 200 <= wx <= 280 or 860 <= wx <= 940: continue
        draw.rectangle([wx - 2, 42, wx + 26, 46], fill=(160, 165, 175, 255), outline=(90, 95, 105, 255))
        draw.rectangle([wx, 46, wx + 24, 76], fill=(28, 36, 48, 255), outline=(22, 26, 34, 255), width=2)
        draw.line([(wx + 3, 48), (wx + 10, 72)], fill=(110, 150, 195, 120), width=2)

    # Storm Drainage Gutter along tenement base (y = 96..106)
    draw.rectangle([0, 96, W, 104], fill=(42, 45, 52, 255), outline=(26, 28, 34, 255))
    for gx in range(48, W, 128):
        draw.rectangle([gx, 97, gx + 28, 103], fill=(22, 24, 28, 255), outline=(65, 70, 80, 255))
        for gy in range(gx + 3, gx + 26, 4):
            draw.line([(gy, 98), (gy, 102)], fill=(12, 14, 18, 255))

    # 3. Ground: Wet River-Stone Cobblestones across rows 3..17 (y = 104..576)
    cobble_base = (56, 60, 68)
    draw.rectangle([0, 104, W, H], fill=cobble_base)
    for cy in range(104, H, 12):
        draw.line([(0, cy), (W, cy)], fill=(32, 34, 40, 255), width=1)
        shift = ((cy - 104) // 12 % 2) * 12
        for cx in range(shift, W, 24):
            draw.line([(cx, cy), (cx, cy + 12)], fill=(32, 34, 40, 255), width=1)
            draw.line([(cx + 2, cy + 2), (cx + 22, cy + 2)], fill=(78, 84, 96, 255))
            draw.line([(cx + 2, cy + 10), (cx + 22, cy + 10)], fill=(40, 42, 48, 255))
            if (cx * 13 + cy * 7) % 19 == 0:
                draw.point((cx + 8, cy + 3), fill=(185, 205, 225, 200))

    # 4. Large Reflective Rain Puddles Mirroring Light and Sky
    puddle_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(puddle_layer)
    puddles = [
        (160, 180, 260, 240),
        (330, 150, 450, 220),
        (540, 300, 680, 380),
        (740, 200, 880, 280),
        (960, 340, 1100, 420),
        (1140, 180, 1240, 250)
    ]
    for px0, py0, px1, py1 in puddles:
        pd.ellipse([px0, py0, px1, py1], fill=(28, 38, 54, 210), outline=(60, 85, 115, 180), width=2)
        mid_y = (py0 + py1) // 2
        pd.line([(px0 + 20, mid_y), (px1 - 20, mid_y)], fill=(120, 160, 210, 90), width=3)
        pd.line([(px0 + 35, mid_y + 8), (px1 - 35, mid_y + 8)], fill=(100, 140, 190, 70), width=2)
    im.alpha_composite(puddle_layer)
    draw = ImageDraw.Draw(im)

    # 5. Green Industrial Dumpster & Lisu NPC Zone at (10, 3..4) -> (x: 300..370, y: 100..164)
    draw_contact_shadow(draw, 335, 164, 42, 12, alpha=150)
    draw.polygon([(304, 114), (366, 114), (360, 160), (310, 160)], fill=(45, 78, 52, 255), outline=(18, 32, 22, 255), width=2)
    draw.line([(316, 116), (316, 142)], fill=(145, 65, 30, 255), width=2)
    draw.line([(334, 116), (334, 152)], fill=(145, 65, 30, 255), width=2)
    draw.line([(352, 116), (352, 138)], fill=(145, 65, 30, 255), width=2)
    draw.polygon([(300, 102), (370, 102), (366, 114), (304, 114)], fill=(26, 30, 32, 255), outline=(10, 12, 14, 255))
    draw.line([(302, 104), (340, 92)], fill=(38, 42, 46, 255), width=3)
    draw.text((322, 132), "MPO", fill=(210, 220, 225, 200))
    draw.ellipse([308, 156, 316, 164], fill=(30, 32, 38, 255), outline=(10, 12, 15, 255))
    draw.ellipse([354, 156, 362, 164], fill=(30, 32, 38, 255), outline=(10, 12, 15, 255))
    draw.rectangle([366, 146, 380, 160], fill=(215, 185, 145, 255), outline=(130, 95, 60, 255))
    draw.polygon([(372, 138), (388, 148), (382, 160), (368, 156)], fill=(28, 30, 35, 255))

    # 6. Wooden Cargo Crates & Euro-Pallets at (3, 4) -> (x: 88..136, y: 118..162) and (20, 4) -> (x: 624..674, y: 118..162)
    for cx0, cy0 in [(88, 118), (624, 118)]:
        draw_contact_shadow(draw, cx0 + 24, cy0 + 44, 28, 10, alpha=130)
        draw.rectangle([cx0 - 4, cy0 + 34, cx0 + 52, cy0 + 44], fill=(130, 88, 50, 255), outline=(65, 42, 22, 255))
        draw.rectangle([cx0, cy0, cx0 + 48, cy0 + 36], fill=(162, 112, 65, 255), outline=(78, 50, 26, 255), width=2)
        draw.line([(cx0, cy0), (cx0 + 48, cy0 + 36)], fill=(95, 62, 34, 255), width=2)
        draw.line([(cx0 + 48, cy0), (cx0, cy0 + 36)], fill=(95, 62, 34, 255), width=2)
        draw.line([(cx0 + 6, cy0), (cx0 + 6, cy0 + 36)], fill=(55, 60, 68, 255), width=2)
        draw.line([(cx0 + 42, cy0), (cx0 + 42, cy0 + 36)], fill=(55, 60, 68, 255), width=2)

    # 7. Ornate Victorian Cast-Iron Streetlamps & Sodium Light Cones at cols 5, 13, 24, 35
    lamp_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lamp_layer)
    lamps = [5 * TILE, 13 * TILE, 24 * TILE, 35 * TILE]
    for lx in lamps:
        ly = 3 * TILE + 16
        draw.line([(lx + 16, ly - 48), (lx + 16, ly + 20)], fill=(22, 26, 32, 255), width=4)
        draw.ellipse([lx + 10, ly + 14, lx + 22, ly + 22], fill=(22, 26, 32, 255))
        draw.polygon([(lx + 9, ly - 48), (lx + 23, ly - 48), (lx + 20, ly - 32), (lx + 12, ly - 32)], fill=(22, 26, 32, 255))
        draw.rectangle([lx + 12, ly - 44, lx + 20, ly - 34], fill=(255, 240, 140, 255))
        ld.polygon([(lx + 16, ly - 34), (lx - 70, ly + 90), (lx + 102, ly + 90)], fill=(255, 205, 65, 40))
        ld.ellipse([lx - 60, ly + 50, lx + 92, ly + 120], fill=(255, 215, 80, 55))
        ld.ellipse([lx - 30, ly + 65, lx + 62, ly + 105], fill=(255, 235, 120, 75))
    im.alpha_composite(lamp_layer)
    draw = ImageDraw.Draw(im)

    # 8. Romanesque Stone Archway Exit to Marina at right end (cols 37..39 = x: 1184..1280, y: 96..240)
    ax0 = 37 * TILE
    ax1 = W
    draw.rectangle([ax0, 96, ax1, 240], fill=(95, 90, 85, 255), outline=(50, 48, 45, 255), width=2)
    for ay in range(96, 240, 16):
        draw.line([(ax0, ay), (ax1, ay)], fill=(45, 42, 40, 255), width=2)
        shift = (ay // 16 % 2) * 24
        for bx in range(ax0 + shift, ax1, 32):
            draw.line([(bx, ay), (bx, ay + 16)], fill=(45, 42, 40, 255), width=1)
    draw.chord([1200, 120, 1264, 224], 180, 360, fill=(16, 24, 38, 255), outline=(135, 130, 125, 255), width=3)
    draw.rectangle([1200, 172, 1264, 224], fill=(16, 24, 38, 255))
    draw.ellipse([1216, 170, 1248, 190], fill=(255, 205, 80, 60))
    draw.line([(1204, 200), (1260, 200)], fill=(40, 85, 125, 200), width=2)
    draw.line([(1208, 212), (1256, 212)], fill=(65, 120, 165, 180), width=1)

    # Also archway at (16..17, 5..6) -> (x: 512..576, y: 120..224)
    draw.rectangle([512, 120, 576, 224], fill=(95, 90, 85, 255), outline=(50, 48, 45, 255))
    draw.chord([520, 130, 568, 210], 180, 360, fill=(16, 24, 38, 255), outline=(135, 130, 125, 255), width=2)
    draw.rectangle([520, 170, 568, 220], fill=(16, 24, 38, 255))

    # Perimeter solid borders
    draw.rectangle([0, 0, 16, H], fill=(35, 38, 44, 255))
    draw.rectangle([0, H - 16, W, H], fill=(35, 38, 44, 255))

    out_path = os.path.join(MAPS_DIR, "alley_bg.png")
    im.save(out_path, "PNG")
    print(f"Generated {out_path}: {im.size} (40x18 tiles)")


# ============================================================================
# 7. MAP: PRZYSTAŃ MARINA (PIER) - 1280x576 (40x18 tiles)
# ============================================================================
def generate_marina_bg():
    W = 40 * TILE # 1280
    H = 18 * TILE # 576
    im = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(im)

    # 1. Deep sapphire lake water filling entire canvas
    water_base = (20, 38, 62)
    draw.rectangle([0, 0, W, H], fill=water_base)

    # Undulating water wave ripples
    for wy in range(4, H, 6):
        shift = (wy * 17) % 32
        for wx in range(shift, W, 48):
            draw.arc([wx, wy, wx + 28, wy + 8], 180, 360, fill=(45, 85, 135, 200), width=1)
            draw.line([(wx + 8, wy + 1), (wx + 20, wy + 1)], fill=(95, 165, 225, 180))

    # Moonlight reflection path streaming vertically down lake (x: 560..720)
    moon_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(moon_layer)
    for my in range(0, H, 8):
        m_w = int(30 + math.sin(my * 0.05) * 20 + (my / float(H)) * 40)
        md.ellipse([640 - m_w, my, 640 + m_w, my + 6], fill=(210, 240, 255, 32))
        md.ellipse([640 - m_w // 2, my + 1, 640 + m_w // 2, my + 4], fill=(240, 250, 255, 55))
    im.alpha_composite(moon_layer)
    draw = ImageDraw.Draw(im)

    # Distant northern shoreline with dark pine forest silhouette (y = 0..48)
    draw_v_gradient(draw, 0, 48, (12, 18, 30), (22, 38, 58), 0, W)
    for px in range(0, W, 12):
        tree_h = 16 + ((px * 13) % 24)
        draw.polygon([(px, 48), (px + 6, 48 - tree_h), (px + 12, 48)], fill=(10, 16, 26, 255))
    for mx in range(0, W, 96):
        draw.ellipse([mx, 40, mx + 140, 54], fill=(160, 200, 230, 30))

    # 2. Weathered Cedar Boardwalk Pier Decking (rows 3 to 7, y = 96..256, cols 1..38 = x: 32..1248)
    pier_x0 = 32
    pier_x1 = W - 32
    draw_contact_shadow(draw, (pier_x0 + pier_x1)//2, 260, (pier_x1 - pier_x0)//2, 12, alpha=150)
    draw.rectangle([pier_x0, 224, pier_x1, 248], fill=(68, 45, 28, 255), outline=(32, 20, 12, 255))
    # Pilings extending into water with algae
    for px in range(pier_x0 + 16, pier_x1, 64):
        draw.rectangle([px, 224, px + 12, 272], fill=(48, 32, 20, 255), outline=(22, 14, 8, 255))
        draw.rectangle([px, 254, px + 12, 264], fill=(30, 80, 45, 255))

    # Cedar boardwalk decking planks (y = 96..224)
    pier_base = (132, 98, 70)
    draw.rectangle([pier_x0, 96, pier_x1, 224], fill=pier_base)
    for py in range(96, 224, 8):
        draw.line([(pier_x0, py), (pier_x1, py)], fill=(75, 52, 34, 255), width=1)
        shift = ((py - 96) // 8 % 4) * 32
        for px in range(pier_x0 + shift, pier_x1, 64):
            draw.line([(px, py), (px, py + 8)], fill=(75, 52, 34, 255), width=1)
            draw.line([(px + 2, py + 1), (px + 62, py + 1)], fill=(168, 128, 95, 255))
            draw.line([(px + 4, py + 5), (px + 58, py + 5)], fill=(108, 78, 52, 255))
            draw.point((px + 3, py + 4), fill=(32, 26, 24, 255))
            draw.point((px + 61, py + 4), fill=(32, 26, 24, 255))

    # 3. Heavy Timber Safety Railing with Brass Post Caps along North Pier Edge (row 3, y = 96..118)
    draw.line([(pier_x0, 100), (pier_x1, 100)], fill=(85, 56, 36, 255), width=3)
    draw.line([(pier_x0, 110), (pier_x1, 110)], fill=(85, 56, 36, 255), width=3)
    draw.line([(pier_x0, 99), (pier_x1, 99)], fill=(145, 105, 75, 255), width=1)
    for rx in range(pier_x0 + 16, pier_x1, 64):
        draw.rectangle([rx - 3, 96, rx + 3, 120], fill=(75, 48, 30, 255), outline=(38, 22, 14, 255))
        draw.rectangle([rx - 4, 94, rx + 4, 98], fill=(225, 185, 55, 255), outline=(135, 105, 25, 255))
        draw.point((rx - 1, 95), fill=(255, 245, 160, 255))

    # 4. Mooring Bollards & Coiled Manila Dock Ropes along pier edge
    for bx in [pier_x0 + 80, pier_x0 + 280, pier_x0 + 580, pier_x0 + 880]:
        draw_contact_shadow(draw, bx, 226, 12, 6, alpha=130)
        draw.rectangle([bx - 4, 206, bx + 4, 224], fill=(42, 45, 52, 255), outline=(18, 20, 24, 255), width=2)
        draw.ellipse([bx - 7, 202, bx + 7, 210], fill=(55, 60, 70, 255), outline=(18, 20, 24, 255))
        draw.ellipse([bx - 10, 216, bx + 10, 226], fill=(195, 160, 105, 255), outline=(125, 95, 55, 255), width=2)

    # 5. Emergency Lifebuoy Station at (6, 3) -> (x: 192, y: 96..124)
    draw.rectangle([184, 94, 206, 122], fill=(240, 242, 245, 255), outline=(160, 165, 175, 255), width=2)
    draw.line([(195, 96), (195, 120)], fill=(215, 40, 45, 255), width=2)
    draw.ellipse([186, 98, 204, 118], fill=(245, 245, 250, 255), outline=(32, 24, 20, 255), width=2)
    draw.ellipse([191, 103, 199, 113], fill=(184, 130, 90, 255))
    draw.pieslice([186, 98, 204, 118], 45, 135, fill=(225, 40, 45, 255))
    draw.pieslice([186, 98, 204, 118], 225, 315, fill=(225, 40, 45, 255))
    draw.ellipse([191, 103, 199, 113], fill=(184, 130, 90, 255), outline=(32, 24, 20, 255))

    # 6. Nautical Hurricane Lanterns at (11, 3) -> (x: 352, y: 94) and (25, 3) -> (x: 800, y: 94)
    lantern_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lnd = ImageDraw.Draw(lantern_layer)
    for lx in [352, 800]:
        draw.line([(lx, 94), (lx, 104)], fill=(195, 155, 45, 255), width=2)
        draw.polygon([(lx - 5, 104), (lx + 5, 104), (lx + 3, 98), (lx - 3, 98)], fill=(195, 155, 45, 255))
        draw.rectangle([lx - 3, 104, lx + 3, 112], fill=(255, 235, 130, 255), outline=(135, 100, 25, 255))
        lnd.ellipse([lx - 50, 80, lx + 50, 160], fill=(255, 195, 60, 45))
        lnd.ellipse([lx - 25, 95, lx + 25, 140], fill=(255, 225, 90, 65))
    im.alpha_composite(lantern_layer)
    draw = ImageDraw.Draw(im)

    # 7. Łuki's Wooden Rescue Motorboat at (14..16, 4..6) -> (x: 440..540, y: 140..220)
    draw_contact_shadow(draw, 490, 185, 54, 24, alpha=140)
    draw.polygon([(444, 180), (470, 155), (534, 155), (538, 205), (470, 205)], fill=(240, 244, 250, 255), outline=(60, 70, 85, 255), width=2)
    draw.line([(448, 180), (472, 157), (534, 157)], fill=(245, 105, 25, 255), width=3)
    draw.line([(448, 180), (472, 203), (534, 203)], fill=(245, 105, 25, 255), width=3)
    draw.polygon([(474, 163), (526, 163), (526, 197), (474, 197)], fill=(115, 62, 34, 255), outline=(55, 28, 14, 255))
    draw.rectangle([480, 168, 492, 192], fill=(155, 88, 48, 255))
    draw.rectangle([508, 168, 520, 192], fill=(155, 88, 48, 255))
    draw.line([(494, 172), (494, 188)], fill=(180, 220, 240, 200), width=2)
    draw.ellipse([496, 176, 502, 184], outline=(20, 22, 26, 255), width=2)
    # Outboard motor
    draw.rectangle([536, 174, 548, 188], fill=(28, 30, 36, 255), outline=(12, 14, 18, 255))
    draw.line([(548, 181), (552, 181)], fill=(210, 215, 225, 255), width=2)
    draw.polygon([(552, 177), (554, 181), (552, 185)], fill=(210, 215, 225, 255))
    draw.line([(450, 180), (432, 206)], fill=(245, 215, 45, 255), width=2)

    # Perimeter water boundaries
    draw.rectangle([0, 0, 16, H], fill=(16, 28, 45, 255))
    draw.rectangle([W - 16, 0, W, H], fill=(16, 28, 45, 255))

    out_path = os.path.join(MAPS_DIR, "marina_bg.png")
    im.save(out_path, "PNG")
    print(f"Generated {out_path}: {im.size} (40x18 tiles)")


# ============================================================================
# 8. MAP: LEŚNE OBOZOWISKO (FOREST) - 1280x576 (40x18 tiles)
# ============================================================================
def generate_forest_bg():
    W = 40 * TILE # 1280
    H = 18 * TILE # 576
    im = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(im)

    # 1. Base organic forest floor (rows 2 to 17, y = 64..576)
    forest_base = (55, 68, 38)
    draw.rectangle([0, 0, W, H], fill=forest_base)
    for y in range(0, H, 4):
        for x in range(0, W, 4):
            val = (x * 23 + y * 41) % 13
            if val == 0:
                draw.line([(x, y), (x + 3, y + 2)], fill=(115, 72, 36, 255))
            elif val == 5:
                draw.point((x + 1, y + 1), fill=(78, 142, 52, 255))
            elif val == 9:
                draw.point((x + 2, y + 2), fill=(40, 48, 28, 255))

    # Winding beaten-dirt path across clearing
    for px in range(64, W - 64, 4):
        py_mid = int(160 + math.sin(px * 0.01) * 20)
        draw.ellipse([px - 8, py_mid - 12, px + 8, py_mid + 12], fill=(95, 72, 45, 180))
        draw.ellipse([px - 4, py_mid - 6, px + 4, py_mid + 6], fill=(115, 88, 55, 140))

    # Gnarled ancient tree roots
    roots = [
        [(140, 180), (170, 195), (200, 190), (230, 210)],
        [(360, 150), (390, 165), (420, 160), (450, 175)],
        [(720, 220), (750, 240), (790, 235), (830, 255)],
        [(960, 160), (990, 180), (1030, 175), (1070, 195)]
    ]
    for rpts in roots:
        for i in range(len(rpts) - 1):
            draw.line([rpts[i], rpts[i+1]], fill=(52, 32, 18, 255), width=4)
            draw.line([(rpts[i][0] + 1, rpts[i][1] + 1), (rpts[i+1][0] + 1, rpts[i+1][1] + 1)], fill=(92, 58, 34, 255), width=2)

    # Velvety green moss mounds
    moss_mounds = [(120, 240, 36, 18), (240, 320, 42, 20), (500, 260, 48, 22), (760, 340, 52, 24), (1040, 280, 44, 20)]
    for mx, my, mrx, mry in moss_mounds:
        draw.ellipse([mx - mrx, my - mry, mx + mrx, my + mry], fill=(62, 125, 42, 255), outline=(35, 75, 25, 255))
        draw.ellipse([mx - mrx + 6, my - mry + 4, mx + mrx - 6, my + mry - 4], fill=(85, 155, 58, 255))

    # Wild mushrooms
    mushrooms = [
        (130, 235, 'red'), (136, 240, 'red'), (250, 315, 'brown'), (510, 255, 'red'),
        (770, 335, 'brown'), (1050, 275, 'red'), (880, 210, 'red')
    ]
    for mx, my, mtype in mushrooms:
        draw.line([(mx, my + 3), (mx, my + 7)], fill=(235, 235, 225, 255), width=2)
        if mtype == 'red':
            draw.ellipse([mx - 4, my - 2, mx + 4, my + 3], fill=(215, 38, 32, 255))
            draw.point((mx - 2, my), fill=(255, 255, 255, 255))
            draw.point((mx + 2, my), fill=(255, 255, 255, 255))
        else:
            draw.ellipse([mx - 5, my - 2, mx + 5, my + 3], fill=(135, 82, 42, 255))

    # 2. Impassable Ancient Pine Wall
    for tx in range(0, W, 48):
        tw = 28 + ((tx * 7) % 16)
        draw.rectangle([tx, 0, tx + tw, 96], fill=(58, 36, 22, 255), outline=(28, 16, 10, 255), width=2)
        for bx in range(tx + 4, tx + tw - 4, 6):
            draw.line([(bx, 0), (bx, 96)], fill=(38, 22, 14, 255), width=2)
            draw.line([(bx + 2, 0), (bx + 2, 96)], fill=(95, 62, 38, 255), width=1)
        draw.polygon([(tx, 60), (tx + 10, 60), (tx + 8, 92), (tx, 94)], fill=(65, 120, 42, 255))

    for cx in range(0, W, 32):
        for cy in range(0, 60, 16):
            draw.ellipse([cx - 24, cy - 16, cx + 24, cy + 16], fill=(26, 58, 30, 255))
            draw.ellipse([cx - 16, cy - 10, cx + 16, cy + 10], fill=(42, 88, 48, 255))

    draw.rectangle([0, 480, W, H], fill=(24, 46, 26, 255))
    for tx in range(0, W, 56):
        draw.rectangle([tx, 480, tx + 36, H], fill=(52, 32, 20, 255), outline=(24, 14, 8, 255), width=2)
        draw.ellipse([tx - 20, 460, tx + 56, 510], fill=(28, 62, 32, 255))

    draw.rectangle([0, 0, 48, H], fill=(22, 42, 24, 255))
    draw.rectangle([W - 48, 0, W, H], fill=(22, 42, 24, 255))

    # 3. Dappled Moonlight Beams
    moon_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    mnd = ImageDraw.Draw(moon_img)
    beams = [(220, 50, 360, 420), (520, 40, 680, 440), (840, 45, 1020, 430)]
    for bx0, by0, bx1, by1 in beams:
        mnd.polygon([(bx0, by0), (bx0 + 60, by0), (bx1 + 120, by1), (bx1, by1)], fill=(185, 215, 245, 32))
        mnd.polygon([(bx0 + 20, by0), (bx0 + 40, by0), (bx1 + 80, by1), (bx1 + 40, by1)], fill=(215, 235, 255, 48))
    for dx, dy in [(280, 200), (340, 280), (580, 220), (640, 310), (900, 240), (960, 320)]:
        mnd.ellipse([dx - 2, dy - 2, dx + 2, dy + 2], fill=(240, 250, 255, 160))
    im.alpha_composite(moon_img)
    draw = ImageDraw.Draw(im)

    # 4. Stone Campfire Ring & Burning Embers at (9, 5) -> (x: 288, y: 160)
    fire_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fgd = ImageDraw.Draw(fire_glow)
    fgd.ellipse([288 - 90, 160 - 50, 288 + 90, 160 + 50], fill=(255, 120, 25, 55))
    fgd.ellipse([288 - 50, 160 - 30, 288 + 50, 160 + 30], fill=(255, 185, 45, 80))
    im.alpha_composite(fire_glow)
    draw = ImageDraw.Draw(im)

    draw_contact_shadow(draw, 288, 172, 38, 16, alpha=150)
    draw.ellipse([262, 146, 314, 174], fill=(32, 20, 16, 255), outline=(18, 10, 8, 255))
    for ang in range(0, 360, 30):
        rad = math.radians(ang)
        sx = int(288 + math.cos(rad) * 24)
        sy = int(160 + math.sin(rad) * 13)
        draw.ellipse([sx - 6, sy - 5, sx + 6, sy + 5], fill=(110, 115, 122, 255), outline=(50, 52, 56, 255))
        draw.ellipse([sx - 4, sy - 4, sx + 2, sy + 1], fill=(155, 160, 170, 255))
    draw.ellipse([274, 153, 302, 167], fill=(235, 75, 20, 255))
    draw.ellipse([280, 156, 296, 164], fill=(255, 195, 40, 255))
    draw.line([(276, 162), (300, 154)], fill=(65, 38, 22, 255), width=3)
    draw.line([(278, 154), (298, 162)], fill=(65, 38, 22, 255), width=3)
    draw.polygon([(282, 160), (288, 136), (294, 160)], fill=(255, 165, 30, 255))
    draw.polygon([(285, 160), (288, 142), (291, 160)], fill=(255, 240, 120, 255))
    smoke_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    smd = ImageDraw.Draw(smoke_layer)
    smd.arc([282, 110, 298, 138], 90, 270, fill=(200, 215, 230, 60), width=3)
    smd.arc([286, 80, 304, 112], 270, 90, fill=(200, 215, 230, 45), width=4)
    smd.arc([282, 50, 310, 84], 90, 270, fill=(200, 215, 230, 30), width=5)
    im.alpha_composite(smoke_layer)
    draw = ImageDraw.Draw(im)

    # 5. Split Log Benches around campfire
    for bx, by in [(224, 160), (352, 160)]:
        draw_contact_shadow(draw, bx, by + 12, 22, 8, alpha=130)
        draw.rectangle([bx - 18, by - 6, bx + 18, by + 6], fill=(168, 125, 78, 255), outline=(78, 48, 24, 255), width=2)
        draw.line([(bx - 16, by - 4), (bx + 16, by - 4)], fill=(215, 175, 125, 255))
        draw.rectangle([bx - 16, by + 6, bx - 10, by + 12], fill=(68, 42, 22, 255))
        draw.rectangle([bx + 10, by + 6, bx + 16, by + 12], fill=(68, 42, 22, 255))

    # 6. Ripstop Camping Hammocks at (5, 3) -> (x: 160, y: 96) and (13, 3) -> (x: 416, y: 96)
    draw_contact_shadow(draw, 160, 128, 28, 8, alpha=110)
    draw.line([(132, 92), (142, 102)], fill=(28, 30, 35, 255), width=2)
    draw.line([(188, 92), (178, 102)], fill=(28, 30, 35, 255), width=2)
    draw.ellipse([140, 100, 144, 104], fill=(215, 220, 230, 255))
    draw.ellipse([176, 100, 180, 104], fill=(215, 220, 230, 255))
    draw.chord([140, 96, 180, 124], 0, 180, fill=(235, 110, 30, 255), outline=(135, 50, 12, 255), width=2)
    draw.arc([144, 100, 176, 120], 0, 180, fill=(255, 165, 60, 255), width=2)

    draw_contact_shadow(draw, 416, 128, 28, 8, alpha=110)
    draw.line([(388, 92), (398, 102)], fill=(28, 30, 35, 255), width=2)
    draw.line([(444, 92), (434, 102)], fill=(28, 30, 35, 255), width=2)
    draw.ellipse([396, 100, 400, 104], fill=(215, 220, 230, 255))
    draw.ellipse([432, 100, 436, 104], fill=(215, 220, 230, 255))
    draw.chord([396, 96, 436, 124], 0, 180, fill=(45, 115, 60, 255), outline=(22, 60, 30, 255), width=2)
    draw.arc([400, 100, 432, 120], 0, 180, fill=(75, 165, 95, 255), width=2)

    # 7. Bushcraft Gear
    draw_contact_shadow(draw, 260, 202, 12, 5, alpha=130)
    draw.ellipse([252, 188, 268, 196], fill=(155, 115, 75, 255), outline=(68, 42, 22, 255))
    draw.rectangle([252, 192, 268, 202], fill=(78, 48, 26, 255), outline=(38, 20, 10, 255))
    draw.line([(260, 184), (260, 192)], fill=(195, 200, 210, 255), width=3)
    draw.line([(260, 184), (272, 172)], fill=(165, 115, 65, 255), width=2)

    draw_contact_shadow(draw, 320, 192, 10, 4, alpha=120)
    draw.rounded_rectangle([314, 174, 326, 190], radius=2, fill=(65, 88, 52, 255), outline=(32, 45, 25, 255))
    draw.line([(316, 178), (324, 178)], fill=(145, 105, 55, 255))
    draw.rectangle([328, 184, 332, 190], fill=(60, 120, 180, 255))

    out_path = os.path.join(MAPS_DIR, "forest_bg.png")
    im.save(out_path, "PNG")
    print(f"Generated {out_path}: {im.size} (40x18 tiles)")


# ============================================================================
# PHASE 2 TILESET BUILDERS
# ============================================================================
def build_garage_tileset():
    tiles = []
    # Tile 0: Stained concrete with iridescent oil slick
    t0 = Image.new("RGBA", (32, 32), (76, 80, 86, 255))
    d0 = ImageDraw.Draw(t0)
    for y in range(0, 32, 4):
        for x in range(0, 32, 4):
            if (x * 7 + y * 13) % 5 == 0:
                d0.point((x + 1, y + 1), fill=(95, 100, 108, 255))
    d0.line([(0, 31), (32, 31)], fill=(45, 48, 52, 255))
    d0.line([(31, 0), (31, 32)], fill=(45, 48, 52, 255))
    # Iridescent oil slick
    d0.ellipse([8, 8, 24, 22], fill=(28, 30, 34, 230))
    d0.arc([10, 10, 22, 20], 30, 210, fill=(160, 40, 180, 180), width=2)
    d0.arc([11, 11, 21, 19], 60, 240, fill=(30, 190, 220, 180), width=2)
    tiles.append(t0)

    # Tile 1: Cinder block wall with conduit pipe
    t1 = Image.new("RGBA", (32, 32), (148, 152, 160, 255))
    d1 = ImageDraw.Draw(t1)
    d1.line([(0, 16), (32, 16)], fill=(85, 90, 98, 255), width=2)
    d1.line([(16, 0), (16, 16)], fill=(85, 90, 98, 255), width=2)
    d1.line([(0, 16), (0, 32)], fill=(85, 90, 98, 255), width=2)
    d1.line([(0, 28), (32, 28)], fill=(185, 190, 200, 255), width=2)
    d1.rectangle([14, 25, 18, 31], fill=(90, 95, 105, 255))
    tiles.append(t1)

    # Tile 2: Concrete ceiling with fluorescent light fixture
    t2 = t1.copy()
    d2 = ImageDraw.Draw(t2)
    d2.rectangle([4, 4, 28, 12], fill=(65, 70, 78, 255), outline=(25, 28, 32, 255))
    d2.rectangle([6, 6, 26, 10], fill=(245, 252, 255, 255))
    tiles.append(t2)

    # Tile 3: Stacked tires (transparent background)
    t3 = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d3 = ImageDraw.Draw(t3)
    for ty in [18, 10, 2]:
        d3.ellipse([6, ty, 26, ty + 10], fill=(28, 30, 35, 255), outline=(12, 14, 18, 255))
        d3.ellipse([10, ty + 2, 22, ty + 8], fill=(55, 60, 68, 255))
        d3.ellipse([13, ty + 3, 19, ty + 7], fill=(16, 18, 22, 255))
    tiles.append(t3)

    # Tile 4: Red industrial tool chest (transparent background)
    t4 = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d4 = ImageDraw.Draw(t4)
    d4.rectangle([4, 4, 28, 28], fill=(195, 35, 30, 255), outline=(105, 18, 16, 255), width=2)
    d4.line([(5, 5), (27, 5)], fill=(240, 75, 70, 255))
    for dy in range(10, 26, 5):
        d4.line([(6, dy), (26, dy)], fill=(120, 20, 18, 255))
        d4.line([(10, dy - 2), (22, dy - 2)], fill=(235, 240, 250, 255), width=2)
    tiles.append(t4)

    # Tile 5: Beer fridge with cold cans (transparent background)
    t5 = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d5 = ImageDraw.Draw(t5)
    d5.rectangle([4, 2, 28, 30], fill=(32, 36, 44, 255), outline=(16, 18, 22, 255), width=2)
    d5.rectangle([6, 4, 26, 26], fill=(16, 75, 120, 255), outline=(140, 210, 245, 255))
    for sy in [12, 18, 24]:
        d5.line([(7, sy), (25, sy)], fill=(185, 225, 250, 255))
        for bx, bcol in [(9, (225, 45, 45)), (14, (245, 205, 35)), (19, (45, 175, 75)), (23, (50, 130, 230))]:
            d5.rectangle([bx - 1, sy - 4, bx + 1, sy], fill=bcol)
    d5.line([(8, 4), (22, 25)], fill=(255, 255, 255, 110), width=2)
    tiles.append(t5)

    # Tile 6: Projector screen displaying UFC fight (transparent background)
    t6 = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d6 = ImageDraw.Draw(t6)
    d6.rectangle([2, 4, 30, 28], fill=(16, 24, 40, 255), outline=(65, 140, 210, 255), width=2)
    d6.polygon([(6, 8), (26, 8), (28, 24), (4, 24)], outline=(80, 105, 135, 255))
    d6.text((7, 6), "UFC", fill=(245, 220, 50, 255))
    d6.point((12, 16), fill=(215, 40, 40, 255))
    d6.point((20, 16), fill=(40, 100, 220, 255))
    tiles.append(t6)

    # Tile 7: Heavy metal exit door with green emergency exit sign
    t7 = t0.copy()
    d7 = ImageDraw.Draw(t7)
    d7.rectangle([4, 2, 28, 30], fill=(68, 74, 85, 255), outline=(35, 38, 44, 255), width=2)
    d7.line([(6, 16), (26, 16)], fill=(215, 220, 230, 255), width=2)
    d7.rectangle([10, 4, 22, 10], fill=(12, 145, 45, 255), outline=(160, 255, 180, 255))
    d7.text((11, 4), "EXIT", fill=(255, 255, 255, 255))
    tiles.append(t7)

    save_tileset("garage", tiles)


def build_pub_tileset():
    tiles = []
    # Tile 0: Mahogany floorboards with amber reflection
    t0 = Image.new("RGBA", (32, 32), (88, 40, 22, 255))
    d0 = ImageDraw.Draw(t0)
    for y in range(0, 32, 8):
        d0.line([(0, y), (32, y)], fill=(48, 20, 10, 255))
        for x in range((y % 16), 32, 16):
            d0.line([(x, y), (x, y + 8)], fill=(48, 20, 10, 255))
            d0.line([(x + 2, y + 2), (x + 14, y + 2)], fill=(125, 62, 34, 255))
    tiles.append(t0)

    # Tile 1: Dark wood panel wall
    t1 = Image.new("RGBA", (32, 32), (62, 28, 16, 255))
    d1 = ImageDraw.Draw(t1)
    for x in range(0, 32, 8):
        d1.rectangle([x + 1, 2, x + 7, 28], fill=(82, 38, 20, 255), outline=(38, 16, 10, 255))
    tiles.append(t1)

    # Tile 2: Ceiling with amber hanging lamp
    t2 = t1.copy()
    d2 = ImageDraw.Draw(t2)
    d2.line([(16, 0), (16, 10)], fill=(22, 18, 16, 255), width=2)
    d2.ellipse([11, 10, 21, 22], fill=(255, 185, 55, 240), outline=(180, 105, 25, 255))
    d2.point((16, 16), fill=(255, 250, 200, 255))
    tiles.append(t2)

    # Tile 3: Bar counter with brass footrail
    t3 = t0.copy()
    d3 = ImageDraw.Draw(t3)
    d3.rectangle([0, 6, 32, 24], fill=(162, 92, 48, 255), outline=(62, 28, 16, 255))
    d3.line([(0, 7), (32, 7)], fill=(215, 138, 82, 255), width=2)
    d3.line([(0, 27), (32, 27)], fill=(225, 185, 55, 255), width=3)
    d3.line([(0, 26), (32, 26)], fill=(255, 235, 140, 255), width=1)
    tiles.append(t3)

    # Tile 4: Brass draft beer taps (transparent background)
    t4 = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d4 = ImageDraw.Draw(t4)
    d4.rectangle([10, 4, 22, 24], fill=(225, 185, 55, 255), outline=(135, 105, 25, 255), width=2)
    d4.line([(13, 0), (13, 6)], fill=(25, 25, 25, 255), width=2)
    d4.line([(19, 0), (19, 6)], fill=(25, 25, 25, 255), width=2)
    d4.ellipse([12, -1, 14, 2], fill=(180, 30, 30, 255))
    d4.ellipse([18, -1, 20, 2], fill=(240, 200, 40, 255))
    tiles.append(t4)

    # Tile 5: Shelves packed with vinyl records (transparent background)
    t5 = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d5 = ImageDraw.Draw(t5)
    d5.rectangle([2, 2, 30, 30], fill=(110, 62, 34, 255), outline=(55, 30, 16, 255), width=2)
    for sy in [12, 24]:
        d5.line([(4, sy), (28, sy)], fill=(55, 30, 16, 255), width=2)
        vcols = [(225, 45, 45), (45, 120, 230), (245, 215, 35), (240, 240, 245), (55, 195, 75), (225, 115, 35)]
        for vi, vx in enumerate(range(5, 27, 4)):
            d5.line([(vx, sy - 8), (vx, sy - 1)], fill=vcols[vi % len(vcols)], width=3)
    tiles.append(t5)

    # Tile 6: Dual turntables DJ setup (transparent background)
    t6 = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d6 = ImageDraw.Draw(t6)
    d6.rectangle([2, 4, 15, 20], fill=(190, 195, 205, 255), outline=(50, 55, 65, 255))
    d6.ellipse([4, 6, 13, 18], fill=(20, 22, 26, 255))
    d6.point((5, 7), fill=(45, 160, 255, 255))
    d6.rectangle([17, 4, 30, 20], fill=(190, 195, 205, 255), outline=(50, 55, 65, 255))
    d6.ellipse([19, 6, 28, 18], fill=(20, 22, 26, 255))
    d6.point((20, 7), fill=(45, 160, 255, 255))
    d6.rectangle([14, 8, 18, 22], fill=(28, 30, 35, 255))
    d6.point((16, 12), fill=(45, 215, 65, 255))
    tiles.append(t6)

    # Tile 7: Pub Exit door
    t7 = t0.copy()
    d7 = ImageDraw.Draw(t7)
    d7.rectangle([4, 2, 28, 30], fill=(55, 28, 16, 255), outline=(28, 14, 8, 255), width=2)
    d7.rectangle([8, 6, 24, 14], fill=(12, 145, 45, 255), outline=(160, 255, 180, 255))
    d7.text((10, 7), "EXIT", fill=(255, 255, 255, 255))
    tiles.append(t7)

    save_tileset("pub", tiles)


def build_alley_tileset():
    tiles = []
    # Tile 0: Wet cobblestones with rain puddle
    t0 = Image.new("RGBA", (32, 32), (56, 60, 68, 255))
    d0 = ImageDraw.Draw(t0)
    for y in range(0, 32, 8):
        d0.line([(0, y), (32, y)], fill=(32, 34, 40, 255))
        for x in range((y % 16), 32, 16):
            d0.line([(x, y), (x, y + 8)], fill=(32, 34, 40, 255))
            d0.line([(x + 2, y + 2), (x + 14, y + 2)], fill=(78, 84, 96, 255))
    # Puddle
    d0.ellipse([8, 10, 24, 22], fill=(28, 38, 54, 220), outline=(60, 85, 115, 200))
    d0.line([(11, 15), (21, 15)], fill=(120, 160, 210, 140))
    tiles.append(t0)

    # Tile 1: Aged red brick wall with graffiti
    t1 = Image.new("RGBA", (32, 32), (142, 56, 44, 255))
    d1 = ImageDraw.Draw(t1)
    for y in range(0, 32, 6):
        d1.line([(0, y), (32, y)], fill=(72, 42, 36, 255))
        for x in range((y % 12), 32, 12):
            d1.line([(x, y), (x, y + 6)], fill=(72, 42, 36, 255))
    d1.line([(6, 14), (12, 22), (18, 14)], fill=(60, 235, 255, 240), width=2)
    tiles.append(t1)

    # Tile 2: Brick wall cornice & fire escape ladder (transparent background)
    t2 = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d2 = ImageDraw.Draw(t2)
    d2.rectangle([0, 0, 32, 8], fill=(95, 100, 110, 255), outline=(55, 58, 65, 255))
    d2.line([(10, 8), (10, 32)], fill=(28, 32, 38, 255), width=2)
    d2.line([(22, 8), (22, 32)], fill=(28, 32, 38, 255), width=2)
    for ly in range(12, 32, 6):
        d2.line([(10, ly), (22, ly)], fill=(28, 32, 38, 255), width=2)
    tiles.append(t2)

    # Tile 3: Green industrial dumpster (transparent background)
    t3 = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d3 = ImageDraw.Draw(t3)
    d3.polygon([(3, 10), (29, 10), (27, 28), (5, 28)], fill=(45, 78, 52, 255), outline=(18, 32, 22, 255), width=2)
    d3.line([(8, 14), (8, 24)], fill=(145, 65, 30, 255), width=2)
    d3.polygon([(2, 7), (30, 7), (28, 11), (4, 11)], fill=(26, 30, 32, 255))
    tiles.append(t3)

    # Tile 4: Cast-iron streetlamp with sodium glow (transparent background)
    t4 = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d4 = ImageDraw.Draw(t4)
    d4.ellipse([4, 0, 28, 22], fill=(255, 205, 65, 90))
    d4.line([(16, 6), (16, 28)], fill=(22, 26, 32, 255), width=3)
    d4.polygon([(11, 6), (21, 6), (18, 0), (14, 0)], fill=(22, 26, 32, 255))
    d4.rectangle([13, 4, 19, 7], fill=(255, 240, 140, 255))
    tiles.append(t4)

    # Tile 5: Stacked wooden cargo crates (transparent background)
    t5 = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d5 = ImageDraw.Draw(t5)
    d5.rectangle([4, 6, 28, 28], fill=(162, 112, 65, 255), outline=(78, 50, 26, 255), width=2)
    d5.line([(4, 6), (28, 28)], fill=(95, 62, 34, 255), width=2)
    d5.line([(28, 6), (4, 28)], fill=(95, 62, 34, 255), width=2)
    tiles.append(t5)

    # Tile 6: Drainage gutter with iron grate
    t6 = t0.copy()
    d6 = ImageDraw.Draw(t6)
    d6.rectangle([4, 6, 28, 26], fill=(22, 24, 28, 255), outline=(65, 70, 80, 255))
    for gx in range(6, 28, 4):
        d6.line([(gx, 8), (gx, 24)], fill=(12, 14, 18, 255), width=2)
    tiles.append(t6)

    # Tile 7: Romanesque stone archway exit
    t7 = t0.copy()
    d7 = ImageDraw.Draw(t7)
    d7.ellipse([2, 0, 30, 30], fill=(16, 24, 38, 255), outline=(135, 130, 125, 255), width=2)
    tiles.append(t7)

    save_tileset("alley", tiles)


def build_marina_tileset():
    tiles = []
    # Tile 0: Weathered cedar pier boardwalk with iron nails
    t0 = Image.new("RGBA", (32, 32), (132, 98, 70, 255))
    d0 = ImageDraw.Draw(t0)
    for y in range(0, 32, 8):
        d0.line([(0, y), (32, y)], fill=(75, 52, 34, 255))
        d0.line([(0, y + 1), (32, y + 1)], fill=(168, 128, 95, 255))
        d0.point((4, y + 4), fill=(32, 26, 24, 255))
        d0.point((28, y + 4), fill=(32, 26, 24, 255))
    tiles.append(t0)

    # Tile 1: Deep sapphire lake water with ripples
    t1 = Image.new("RGBA", (32, 32), (20, 38, 62, 255))
    d1 = ImageDraw.Draw(t1)
    for y in range(2, 32, 6):
        d1.arc([(y % 8), y, 20 + (y % 8), y + 6], 180, 360, fill=(45, 85, 135, 220), width=1)
        d1.line([(2 + (y % 12), y + 1), (8 + (y % 12), y + 1)], fill=(95, 165, 225, 180))
    tiles.append(t1)

    # Tile 2: Pier edge with bumper beam & water
    t2 = t1.copy()
    d2 = ImageDraw.Draw(t2)
    d2.rectangle([0, 0, 32, 16], fill=(132, 98, 70, 255), outline=(32, 20, 12, 255))
    d2.rectangle([0, 16, 32, 22], fill=(68, 45, 28, 255), outline=(22, 14, 8, 255))
    tiles.append(t2)

    # Tile 3: Mooring bollard with rope (transparent background)
    t3 = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d3 = ImageDraw.Draw(t3)
    d3.rectangle([11, 8, 21, 26], fill=(42, 45, 52, 255), outline=(18, 20, 24, 255), width=2)
    d3.ellipse([8, 4, 24, 12], fill=(55, 60, 70, 255), outline=(18, 20, 24, 255))
    d3.ellipse([6, 16, 26, 26], outline=(195, 160, 105, 255), width=3)
    tiles.append(t3)

    # Tile 4: Wall rack with red-and-white lifebuoy (transparent background)
    t4 = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d4 = ImageDraw.Draw(t4)
    d4.ellipse([5, 5, 27, 27], fill=(245, 245, 250, 255), outline=(32, 24, 20, 255), width=2)
    d4.ellipse([11, 11, 21, 21], fill=(0, 0, 0, 0))
    d4.pieslice([5, 5, 27, 27], 45, 135, fill=(225, 40, 45, 255))
    d4.pieslice([5, 5, 27, 27], 225, 315, fill=(225, 40, 45, 255))
    tiles.append(t4)

    # Tile 5: Moored rescue motorboat with orange stripe (transparent background)
    t5 = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d5 = ImageDraw.Draw(t5)
    d5.polygon([(4, 16), (28, 6), (28, 26)], fill=(240, 244, 250, 255), outline=(60, 70, 85, 255), width=2)
    d5.polygon([(7, 16), (26, 9), (26, 23)], fill=(115, 62, 34, 255))
    d5.line([(10, 13), (10, 19)], fill=(245, 105, 25, 255), width=3)
    tiles.append(t5)

    # Tile 6: Pier railing with brass post caps (transparent background)
    t6 = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d6 = ImageDraw.Draw(t6)
    d6.line([(0, 6), (32, 6)], fill=(85, 56, 36, 255), width=3)
    d6.line([(0, 16), (32, 16)], fill=(85, 56, 36, 255), width=3)
    for px in [6, 26]:
        d6.rectangle([px - 2, 4, px + 2, 28], fill=(75, 48, 30, 255), outline=(38, 22, 14, 255))
        d6.rectangle([px - 3, 2, px + 3, 6], fill=(225, 185, 55, 255), outline=(135, 105, 25, 255))
    tiles.append(t6)

    # Tile 7: Nautical hurricane lantern on pier post (transparent background)
    t7 = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d7 = ImageDraw.Draw(t7)
    d7.ellipse([4, 0, 28, 24], fill=(255, 195, 60, 90))
    d7.rectangle([13, 10, 19, 28], fill=(75, 48, 30, 255))
    d7.polygon([(11, 10), (21, 10), (19, 4), (13, 4)], fill=(195, 155, 45, 255))
    d7.rectangle([13, 7, 19, 10], fill=(255, 235, 130, 255))
    tiles.append(t7)

    save_tileset("marina", tiles)


def build_forest_tileset():
    tiles = []
    # Tile 0: Pine needle forest floor with moss and mushrooms
    t0 = Image.new("RGBA", (32, 32), (55, 68, 38, 255))
    d0 = ImageDraw.Draw(t0)
    for y in range(0, 32, 4):
        for x in range(0, 32, 4):
            if (x * 3 + y * 7) % 4 == 0:
                d0.line([(x, y), (x + 3, y + 2)], fill=(115, 72, 36, 255))
            elif (x * 5 + y * 11) % 6 == 0:
                d0.point((x + 1, y + 1), fill=(78, 142, 52, 255))
    d0.ellipse([14, 18, 18, 22], fill=(215, 38, 32, 255))
    d0.point((15, 19), fill=(255, 255, 255, 255))
    d0.line([(16, 22), (16, 26)], fill=(235, 235, 225, 255), width=2)
    tiles.append(t0)

    # Tile 1: Dirt trail path with exposed tree roots
    t1 = Image.new("RGBA", (32, 32), (105, 80, 50, 255))
    d1 = ImageDraw.Draw(t1)
    for y in range(0, 32, 6):
        d1.point((y, y), fill=(75, 52, 30, 255))
        d1.point((31 - y, y), fill=(138, 108, 72, 255))
    d1.arc([4, 6, 28, 26], 30, 210, fill=(62, 38, 20, 255), width=3)
    tiles.append(t1)

    # Tile 2: Ancient gnarled pine tree trunk with deep bark
    t2 = t0.copy()
    d2 = ImageDraw.Draw(t2)
    d2.rectangle([4, 0, 28, 32], fill=(58, 36, 22, 255), outline=(28, 16, 10, 255), width=2)
    for bx in range(8, 28, 5):
        d2.line([(bx, 0), (bx, 32)], fill=(38, 22, 14, 255), width=2)
        d2.line([(bx + 2, 0), (bx + 2, 32)], fill=(95, 62, 38, 255), width=1)
    d2.polygon([(4, 18), (10, 18), (8, 28), (4, 30)], fill=(65, 120, 42, 255))
    tiles.append(t2)

    # Tile 3: Dense pine needle canopy top with dappled sunbeams
    t3 = Image.new("RGBA", (32, 32), (26, 58, 30, 255))
    d3 = ImageDraw.Draw(t3)
    for cy in range(0, 32, 8):
        for cx in range(0, 32, 8):
            d3.ellipse([cx, cy, cx + 10, cy + 8], fill=(42, 88, 48, 255))
            d3.point((cx + 5, cy + 4), fill=(75, 145, 70, 255))
    d3.line([(4, 0), (28, 32)], fill=(215, 235, 255, 90), width=3)
    tiles.append(t3)

    # Tile 4: Mossy granite boulder (transparent background)
    t4 = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d4 = ImageDraw.Draw(t4)
    d4.ellipse([4, 8, 28, 28], fill=(110, 115, 125, 255), outline=(45, 48, 55, 255), width=2)
    d4.line([(6, 12), (24, 12)], fill=(160, 168, 180, 255), width=2)
    d4.polygon([(10, 8), (20, 8), (18, 16), (8, 14)], fill=(65, 125, 45, 255))
    tiles.append(t4)

    # Tile 5: Stone campfire ring with glowing embers (transparent background)
    t5 = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d5 = ImageDraw.Draw(t5)
    d5.ellipse([4, 6, 28, 26], fill=(32, 20, 16, 255), outline=(18, 10, 8, 255))
    for ang in range(0, 360, 45):
        rad = math.radians(ang)
        sx = int(16 + math.cos(rad) * 10)
        sy = int(16 + math.sin(rad) * 8)
        d5.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=(110, 115, 122, 255), outline=(50, 52, 56, 255))
    d5.ellipse([11, 12, 21, 20], fill=(235, 75, 20, 255))
    d5.point((16, 16), fill=(255, 195, 40, 255))
    tiles.append(t5)

    # Tile 6: Ripstop nylon camping hammock (transparent background)
    t6 = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d6 = ImageDraw.Draw(t6)
    d6.line([(2, 10), (8, 16)], fill=(28, 30, 35, 255), width=2)
    d6.line([(30, 10), (24, 16)], fill=(28, 30, 35, 255), width=2)
    d6.arc([6, 12, 26, 26], 0, 180, fill=(235, 110, 30, 255), width=5)
    d6.arc([8, 14, 24, 24], 0, 180, fill=(75, 165, 95, 255), width=3)
    tiles.append(t6)

    # Tile 7: Forest trail exit with ferns
    t7 = t1.copy()
    d7 = ImageDraw.Draw(t7)
    d7.polygon([(2, 24), (12, 10), (14, 26)], fill=(55, 125, 45, 255))
    d7.polygon([(30, 24), (20, 10), (18, 26)], fill=(55, 125, 45, 255))
    tiles.append(t7)

    save_tileset("forest", tiles)


if __name__ == '__main__':
    print("=== Generating All 8 HD Overworld Maps & Tilesets (Phase 1 & Phase 2) ===")
    generate_apartment_bg()
    generate_city_bg()
    generate_zabka_bg()
    generate_garage_bg()
    generate_pub_bg()
    generate_alley_bg()
    generate_marina_bg()
    generate_forest_bg()

    build_apartment_tileset()
    build_city_tileset()
    build_zabka_tileset()
    build_garage_tileset()
    build_pub_tileset()
    build_alley_tileset()
    build_marina_tileset()
    build_forest_tileset()
    print("=== Full HD Overworld Generation Complete! ===")
