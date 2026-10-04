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

if __name__ == '__main__':
    print("=== Generating Phase 1 HD Overworld Maps & Tilesets ===")
    generate_apartment_bg()
    generate_city_bg()
    generate_zabka_bg()
    build_apartment_tileset()
    build_city_tileset()
    build_zabka_tileset()
    print("=== Generation Complete! ===")
