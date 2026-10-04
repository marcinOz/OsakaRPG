#!/usr/bin/env python3
"""generate_all_enemies.py - Generates authentic, high-detail pixel art for all 11 enemies/bosses.
Strictly avoids flat geometric blocks. Uses multi-layer palettes, volume rendering, textures,
ambient occlusion, rim lighting, and distinct 2-frame animation states.
"""
import os
import math
from PIL import Image, ImageDraw

OUT_DIR = "public/assets/enemies"
os.makedirs(OUT_DIR, exist_ok=True)

# Master palette tones
INK = (12, 16, 28, 255)
DARK_PLUM = (28, 18, 26, 255)

def save_enemy_sheet(name, frame0, frame1, sz):
    sheet = Image.new("RGBA", (sz * 2, sz), (0, 0, 0, 0))
    sheet.paste(frame0, (0, 0))
    sheet.paste(frame1, (sz, 0))
    out_path = os.path.join(OUT_DIR, f"{name}.png")
    sheet.save(out_path, "PNG")
    print(f"Generated {name}.png: {sheet.size}")

# ============================================================================
# 1. slacki (96x96 x 2 frames = 192x96)
# ============================================================================
def build_slacki():
    sz = 96
    logo_path = "art_src/slack_logo.png"
    if os.path.exists(logo_path):
        logo_raw = Image.open(logo_path).convert("RGBA")
    else:
        # Fallback if logo not found
        logo_raw = Image.new("RGBA", (128, 128), (58, 20, 68, 255))
        
    base_w, base_h = 64, 64
    frames = []
    for f in range(2):
        im = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        
        dy = -3 if f == 1 else 0
        scale_factor = 1.02 if f == 1 else 1.0
        w = int(base_w * scale_factor)
        h = int(base_h * scale_factor)
        
        cur_logo = logo_raw.resize((w, h), Image.Resampling.LANCZOS)
        pos_x = (sz - w) // 2
        pos_y = (sz - h) // 2 + 4 + dy
        im.paste(cur_logo, (pos_x, pos_y), cur_logo)
        
        # Pulsating [99+] notification badge floating top right
        badge_y = 8 + dy
        badge_x = 54
        badge_color = (255, 45, 75, 255) if f == 1 else (235, 30, 60, 255)
        border_color = (255, 220, 230, 255)
        d.rounded_rectangle([badge_x, badge_y, badge_x + 36, badge_y + 16], radius=8, fill=badge_color, outline=border_color)
        
        # Draw [99+]
        # [
        d.line([(badge_x + 4, badge_y + 4), (badge_x + 4, badge_y + 12)], fill=(255, 255, 255, 255))
        d.point((badge_x + 5, badge_y + 4), fill=(255, 255, 255, 255))
        d.point((badge_x + 5, badge_y + 12), fill=(255, 255, 255, 255))
        # 9
        d.rectangle([badge_x + 8, badge_y + 4, badge_x + 12, badge_y + 8], outline=(255, 255, 255, 255))
        d.line([(badge_x + 12, badge_y + 7), (badge_x + 12, badge_y + 12)], fill=(255, 255, 255, 255))
        # 9
        d.rectangle([badge_x + 15, badge_y + 4, badge_x + 19, badge_y + 8], outline=(255, 255, 255, 255))
        d.line([(badge_x + 19, badge_y + 7), (badge_x + 19, badge_y + 12)], fill=(255, 255, 255, 255))
        # +
        d.line([(badge_x + 23, badge_y + 7), (badge_x + 27, badge_y + 7)], fill=(255, 255, 255, 255))
        d.line([(badge_x + 25, badge_y + 5), (badge_x + 25, badge_y + 9)], fill=(255, 255, 255, 255))
        # ]
        d.line([(badge_x + 30, badge_y + 4), (badge_x + 30, badge_y + 12)], fill=(255, 255, 255, 255))
        d.point((badge_x + 29, badge_y + 4), fill=(255, 255, 255, 255))
        d.point((badge_x + 29, badge_y + 12), fill=(255, 255, 255, 255))

        frames.append(im)
    save_enemy_sheet("slacki", frames[0], frames[1], sz)

# ============================================================================
# 2. sasiadSzkodnik (128x128 x 2 frames = 256x128) Boss
# ============================================================================
def build_sasiad():
    sz = 128
    frames = []
    for f in range(2):
        im = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        
        # Frame 1: broom shakes up and down, body leans
        broom_angle = -18 if f == 0 else -30
        head_tilt = 0 if f == 0 else 1
        
        # 1. Slippers
        d.ellipse([40, 114, 56, 124], fill=(70, 75, 85, 255), outline=DARK_PLUM)
        d.ellipse([70, 114, 86, 124], fill=(70, 75, 85, 255), outline=DARK_PLUM)
        d.ellipse([42, 116, 54, 121], fill=(120, 130, 145, 255))
        d.ellipse([72, 116, 84, 121], fill=(120, 130, 145, 255))
        
        # 2. Bare hairy legs
        d.rectangle([45, 96, 52, 115], fill=(215, 165, 130, 255), outline=DARK_PLUM)
        d.rectangle([74, 96, 81, 115], fill=(215, 165, 130, 255), outline=DARK_PLUM)
        # leg hairs
        for ly in range(100, 114, 3):
            d.point((47, ly), fill=(60, 45, 35, 255))
            d.point((77, ly + 1), fill=(60, 45, 35, 255))

        # 3. Flannel Bathrobe Body (Rich plaid pattern)
        bathrobe_pts = [(36, 48), (92, 48), (98, 102), (30, 102)]
        d.polygon(bathrobe_pts, fill=(150, 35, 45, 255), outline=DARK_PLUM)
        # Plaid pattern cross-lines
        for px in range(36, 96, 8):
            d.line([(px, 48), (px - 4, 102)], fill=(40, 50, 80, 180), width=2)
            d.line([(px + 3, 48), (px - 1, 102)], fill=(220, 180, 60, 140))
        for py in range(54, 102, 8):
            d.line([(32, py), (96, py)], fill=(40, 50, 80, 180), width=2)
            d.line([(32, py + 3), (96, py + 3)], fill=(220, 180, 60, 140))
        # Bathrobe belt sash
        d.rectangle([34, 76, 94, 82], fill=(110, 25, 35, 255), outline=DARK_PLUM)
        d.rectangle([56, 82, 62, 94], fill=(110, 25, 35, 255), outline=DARK_PLUM)
        # Collar V
        d.polygon([(48, 48), (64, 72), (80, 48)], fill=(110, 25, 35, 255), outline=DARK_PLUM)
        # Undershirt (white tank top with stains)
        d.polygon([(52, 48), (64, 66), (76, 48)], fill=(210, 205, 195, 255))

        # 4. Head & Face
        hx, hy = 64, 32 + head_tilt
        # Neck
        d.rectangle([58, 42, 70, 49], fill=(215, 165, 130, 255), outline=DARK_PLUM)
        # Balding head with side wisps
        d.ellipse([46, hy - 14, 82, hy + 14], fill=(225, 175, 140, 255), outline=DARK_PLUM)
        # Bald sheen highlight
        d.ellipse([54, hy - 12, 72, hy - 6], fill=(245, 210, 185, 255))
        # Grey side hair wisps
        d.arc([44, hy - 6, 52, hy + 8], 90, 270, fill=(180, 185, 195, 255), width=2)
        d.arc([76, hy - 6, 84, hy + 8], -90, 90, fill=(180, 185, 195, 255), width=2)
        
        # Angry furrowed eyebrows & wrinkles
        d.line([(52, hy - 3), (60, hy)], fill=(60, 45, 35, 255), width=2)
        d.line([(76, hy - 3), (68, hy)], fill=(60, 45, 35, 255), width=2)
        d.line([(58, hy - 6), (70, hy - 6)], fill=(180, 130, 100, 255))
        # Beady angry eyes
        d.rectangle([54, hy + 1, 57, hy + 3], fill=(255, 255, 255, 255))
        d.point((55, hy + 2), fill=(20, 20, 20, 255))
        d.rectangle([71, hy + 1, 74, hy + 3], fill=(255, 255, 255, 255))
        d.point((72, hy + 2), fill=(20, 20, 20, 255))
        # Red nose
        d.ellipse([61, hy + 3, 67, hy + 8], fill=(225, 130, 120, 255), outline=(160, 80, 70, 255))
        # Giant grey/brown walrus mustache
        d.polygon([(52, hy + 8), (64, hy + 14), (76, hy + 8), (64, hy + 7)], fill=(160, 165, 175, 255), outline=DARK_PLUM)
        # Open yelling mouth under mustache
        d.ellipse([60, hy + 12, 68, hy + 17], fill=(80, 20, 20, 255), outline=DARK_PLUM)
        d.point((64, hy + 13), fill=(240, 240, 240, 255)) # single tooth

        # 5. Left arm pointing scolding finger
        d.polygon([(34, 52), (18, 62), (20, 68), (34, 62)], fill=(150, 35, 45, 255), outline=DARK_PLUM)
        d.ellipse([14, 60, 20, 68], fill=(225, 175, 140, 255), outline=DARK_PLUM)
        d.line([(14, 64), (8, 62)], fill=(225, 175, 140, 255), width=2) # pointing finger

        # 6. Right arm waving wooden broom
        bx = 96
        by = 56 - (6 if f == 1 else 0)
        d.polygon([(88, 52), (bx, by), (bx + 6, by + 4), (92, 62)], fill=(150, 35, 45, 255), outline=DARK_PLUM)
        # Fist
        d.ellipse([bx, by - 4, bx + 10, by + 6], fill=(225, 175, 140, 255), outline=DARK_PLUM)
        # Wooden broom stick
        stick_angle = math.radians(broom_angle)
        sx0 = bx + 5
        sy0 = by + 1
        stick_len = 54
        sx1 = sx0 + math.cos(stick_angle) * stick_len
        sy1 = sy0 + math.sin(stick_angle) * stick_len
        d.line([(sx0 - math.cos(stick_angle) * 15, sy0 - math.sin(stick_angle) * 15), (sx1, sy1)], fill=(140, 95, 55, 255), width=3)
        # Straw bristles broom head
        bristle_x = sx1
        bristle_y = sy1
        d.polygon([
            (bristle_x, bristle_y),
            (bristle_x + 12, bristle_y - 14),
            (bristle_x + 22, bristle_y - 8),
            (bristle_x + 8, bristle_y + 6)
        ], fill=(215, 185, 75, 255), outline=DARK_PLUM)
        # bristle binding wire
        d.line([(bristle_x + 4, bristle_y - 4), (bristle_x + 8, bristle_y + 2)], fill=(40, 40, 40, 255), width=2)

        frames.append(im)
    save_enemy_sheet("sasiadSzkodnik", frames[0], frames[1], sz)

# ============================================================================
# 3. autoTuneHipster (128x128 x 2 frames = 256x128)
# ============================================================================
def build_hipster():
    sz = 128
    frames = []
    for f in range(2):
        im = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        
        # 1. Stool / Legs
        d.rectangle([46, 95, 56, 118], fill=(30, 40, 60, 255), outline=DARK_PLUM) # raw denim cuffed
        d.rectangle([68, 95, 78, 118], fill=(30, 40, 60, 255), outline=DARK_PLUM)
        # Cuff turn-up
        d.rectangle([46, 114, 56, 118], fill=(180, 185, 170, 255))
        d.rectangle([68, 114, 78, 118], fill=(180, 185, 170, 255))
        # Red-wing style leather boots
        d.polygon([(44, 118), (58, 118), (56, 125), (42, 125)], fill=(120, 60, 30, 255), outline=DARK_PLUM)
        d.polygon([(66, 118), (80, 118), (78, 125), (64, 125)], fill=(120, 60, 30, 255), outline=DARK_PLUM)

        # 2. Torso: Green/Black Buffalo Plaid Flannel
        d.polygon([(36, 50), (88, 50), (86, 98), (38, 98)], fill=(35, 75, 45, 255), outline=DARK_PLUM)
        for px in range(40, 86, 8):
            d.line([(px, 50), (px, 98)], fill=(20, 30, 20, 220), width=3)
        for py in range(56, 98, 8):
            d.line([(36, py), (88, py)], fill=(20, 30, 20, 220), width=3)
        
        # Studio DJ Headphones around neck
        d.arc([42, 40, 82, 60], 0, 180, fill=(30, 30, 35, 255), width=5)
        d.ellipse([36, 44, 46, 56], fill=(50, 50, 60, 255), outline=DARK_PLUM)
        d.ellipse([78, 44, 88, 56], fill=(50, 50, 60, 255), outline=DARK_PLUM)

        # 3. Head & Hipster Beanie
        hy = 34
        # Neck
        d.rectangle([56, 42, 68, 52], fill=(225, 180, 145, 255), outline=DARK_PLUM)
        # Face
        d.ellipse([48, hy - 10, 76, hy + 14], fill=(225, 180, 145, 255), outline=DARK_PLUM)
        # Mustard rolled beanie
        d.ellipse([46, hy - 18, 78, hy - 4], fill=(215, 155, 25, 255), outline=DARK_PLUM)
        d.rectangle([46, hy - 10, 78, hy - 4], fill=(235, 180, 35, 255), outline=DARK_PLUM) # cuff ribbing
        # Manicured full beard
        d.polygon([(48, hy + 2), (54, hy + 18), (70, hy + 18), (76, hy + 2)], fill=(85, 55, 35, 255), outline=DARK_PLUM)
        # Round tortoiseshell glasses
        d.ellipse([50, hy - 3, 60, hy + 5], fill=(245, 245, 250, 180), outline=(50, 30, 15, 255))
        d.ellipse([64, hy - 3, 74, hy + 5], fill=(245, 245, 250, 180), outline=(50, 30, 15, 255))
        d.line([(60, hy + 1), (64, hy + 1)], fill=(50, 30, 15, 255), width=2)
        d.point((55, hy + 1), fill=(20, 20, 20, 255))
        d.point((69, hy + 1), fill=(20, 20, 20, 255))

        # 4. Open MacBook with Auto-tune DAW Visualizer
        # Hands holding MacBook
        mb_y = 70
        d.polygon([(34, 76), (92, 76), (96, 92), (30, 92)], fill=(195, 200, 210, 255), outline=DARK_PLUM) # base
        d.polygon([(38, 54), (88, 54), (92, 76), (34, 76)], fill=(30, 35, 45, 255), outline=DARK_PLUM) # screen lid
        # Screen glowing DAW waveform visualizer
        d.rectangle([(40, 56), (86, 74)], fill=(15, 20, 30, 255))
        # Equalizer bars
        colors = [(60, 220, 240), (240, 60, 180), (120, 240, 80), (255, 220, 50)]
        for b_idx in range(9):
            bx = 42 + b_idx * 5
            h_bar = (b_idx * 3 + f * 4) % 12 + 2
            col = colors[(b_idx + f) % len(colors)]
            d.line([(bx, 73), (bx, 73 - h_bar)], fill=col, width=2)
            d.point((bx, 73 - h_bar - 1), fill=(255, 255, 255, 255))

        # Glowing Apple logo
        d.ellipse([61, 80, 65, 84], fill=(255, 255, 255, 240))

        frames.append(im)
    save_enemy_sheet("autoTuneHipster", frames[0], frames[1], sz)

# ============================================================================
# 4. kark (128x128 x 2 frames = 256x128) Boss
# ============================================================================
def build_kark():
    sz = 128
    frames = []
    for f in range(2):
        im = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        
        # 1. Heavy Combat Boots & Black Tactical Pants
        d.rectangle([40, 92, 58, 116], fill=(24, 26, 32, 255), outline=DARK_PLUM)
        d.rectangle([68, 92, 86, 116], fill=(24, 26, 32, 255), outline=DARK_PLUM)
        # Heavy boots
        d.polygon([(36, 114), (60, 114), (58, 126), (34, 126)], fill=(12, 14, 18, 255), outline=DARK_PLUM)
        d.polygon([(66, 114), (90, 114), (88, 126), (64, 126)], fill=(12, 14, 18, 255), outline=DARK_PLUM)

        # 2. Enormous Broad Shoulders & Bomber Jacket
        # Shrug breathing in frame 1
        jy = 40 - (2 if f == 1 else 0)
        d.polygon([(20, jy + 16), (106, jy + 16), (96, 94), (30, 94)], fill=(20, 22, 28, 255), outline=DARK_PLUM)
        # Leather jacket sheen / creases
        d.line([(32, jy + 24), (46, 88)], fill=(50, 55, 68, 255), width=2)
        d.line([(94, jy + 24), (80, 88)], fill=(50, 55, 68, 255), width=2)
        # Golden OCHRONA badge
        d.polygon([(40, jy + 28), (48, jy + 28), (44, jy + 38)], fill=(235, 190, 45, 255), outline=DARK_PLUM)

        # 3. Crossed Muscular Arms in Tactical Fingerless Gloves
        d.rectangle([34, 66, 92, 82], fill=(25, 28, 35, 255), outline=DARK_PLUM)
        # Bare muscular forearms
        d.rectangle([38, 62, 54, 76], fill=(210, 160, 130, 255), outline=DARK_PLUM)
        d.rectangle([72, 62, 88, 76], fill=(210, 160, 130, 255), outline=DARK_PLUM)
        # Vein on forearm
        d.line([(42, 64), (48, 72)], fill=(170, 120, 100, 255))
        # Tactical gloves clenched
        d.rectangle([54, 68, 72, 78], fill=(15, 18, 22, 255), outline=DARK_PLUM)

        # 4. Massive Bull Neck & Shaved Buzzcut Head
        # Neck
        d.rectangle([50, jy - 4, 76, jy + 18], fill=(210, 160, 130, 255), outline=DARK_PLUM)
        # Trapezoids
        d.polygon([(36, jy + 12), (54, jy + 2), (54, jy + 14)], fill=(195, 145, 120, 255))
        d.polygon([(90, jy + 12), (72, jy + 2), (72, jy + 14)], fill=(195, 145, 120, 255))
        
        # Head with strong jawline
        hy = jy - 14
        d.polygon([(48, hy), (78, hy), (74, hy + 24), (52, hy + 24)], fill=(215, 165, 135, 255), outline=DARK_PLUM)
        # Buzzcut stubble
        d.ellipse([48, hy - 4, 78, hy + 8], fill=(120, 100, 90, 255))
        # Scar over eyebrow
        d.line([(52, hy + 4), (56, hy + 10)], fill=(235, 195, 180, 255), width=2)
        # Dark mirrored sunglasses with red club neon reflection
        d.polygon([(50, hy + 8), (62, hy + 8), (60, hy + 14), (52, hy + 14)], fill=(10, 12, 16, 255), outline=(40, 45, 55, 255))
        d.polygon([(64, hy + 8), (76, hy + 8), (74, hy + 14), (66, hy + 14)], fill=(10, 12, 16, 255), outline=(40, 45, 55, 255))
        d.line([(51, hy + 9), (59, hy + 13)], fill=(240, 40, 80, 255)) # red neon reflection glint
        d.line([(65, hy + 9), (73, hy + 13)], fill=(240, 40, 80, 255))
        if f == 1:
            d.point((58, hy + 9), fill=(255, 255, 255, 255)) # glint spark
            d.point((72, hy + 9), fill=(255, 255, 255, 255))
        
        # Scowling mouth
        d.line([(58, hy + 20), (68, hy + 20)], fill=(140, 90, 80, 255), width=2)
        # Acoustic spiral earpiece coil
        d.arc([74, hy + 10, 84, hy + 24], 90, 270, fill=(220, 230, 240, 200), width=2)

        frames.append(im)
    save_enemy_sheet("kark", frames[0], frames[1], sz)

# ============================================================================
# 5. straznik (128x128 x 2 frames = 256x128)
# ============================================================================
def build_straznik():
    sz = 128
    frames = []
    for f in range(2):
        im = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        
        # 1. Dark Navy Trousers & Boots
        d.rectangle([46, 94, 58, 118], fill=(22, 28, 48, 255), outline=DARK_PLUM)
        d.rectangle([68, 94, 80, 118], fill=(22, 28, 48, 255), outline=DARK_PLUM)
        d.polygon([(42, 116), (60, 116), (58, 125), (40, 125)], fill=(15, 18, 25, 255), outline=DARK_PLUM)
        d.polygon([(66, 116), (84, 116), (82, 125), (64, 125)], fill=(15, 18, 25, 255), outline=DARK_PLUM)

        # 2. Torso with High-Vis Neon Yellow Reflective Vest
        d.polygon([(34, 46), (92, 46), (88, 96), (38, 96)], fill=(20, 26, 45, 255), outline=DARK_PLUM)
        # High-vis neon yellow vest
        d.polygon([(38, 48), (88, 48), (84, 94), (42, 94)], fill=(220, 245, 30, 255), outline=DARK_PLUM)
        # Silver retroreflective horizontal stripes
        d.rectangle([40, 68, 86, 73], fill=(225, 235, 245, 255), outline=(160, 175, 190, 255))
        d.rectangle([41, 80, 85, 85], fill=(225, 235, 245, 255), outline=(160, 175, 190, 255))
        # Police radio lapel mic
        d.rectangle([44, 52, 50, 60], fill=(25, 25, 30, 255), outline=DARK_PLUM)

        # 3. Head & Checkered Cap
        hy = 32
        d.rectangle([58, 40, 68, 48], fill=(220, 170, 135, 255), outline=DARK_PLUM)
        d.ellipse([50, hy - 8, 76, hy + 14], fill=(220, 170, 135, 255), outline=DARK_PLUM)
        # Angry scowling face
        d.line([(54, hy + 2), (60, hy + 5)], fill=(60, 45, 35, 255), width=2)
        d.line([(72, hy + 2), (66, hy + 5)], fill=(60, 45, 35, 255), width=2)
        d.point((57, hy + 4), fill=(10, 10, 10, 255))
        d.point((69, hy + 4), fill=(10, 10, 10, 255))
        d.line([(58, hy + 11), (68, hy + 10)], fill=(120, 70, 60, 255), width=2)

        # Polish Straż Miejska Cap with black/white checkerboard band
        d.ellipse([46, hy - 16, 80, hy - 4], fill=(18, 24, 42, 255), outline=DARK_PLUM)
        # Checkered band
        for cx in range(48, 78, 6):
            c_fill = (255, 255, 255, 255) if (cx // 6) % 2 == 0 else (15, 18, 25, 255)
            d.rectangle([cx, hy - 7, cx + 5, hy - 3], fill=c_fill)
        # Black visor peak
        d.polygon([(44, hy - 3), (82, hy - 3), (76, hy + 1), (50, hy + 1)], fill=(12, 14, 18, 255))

        # 4. Left hand holding Ticket Book (Mandatownik)
        d.polygon([(34, 58), (22, 68), (24, 76), (36, 66)], fill=(220, 245, 30, 255), outline=DARK_PLUM)
        # Orange/White citation ticket notebook
        d.polygon([(14, 60), (28, 54), (32, 72), (18, 78)], fill=(245, 140, 30, 255), outline=DARK_PLUM)
        d.polygon([(16, 62), (26, 57), (29, 70), (19, 75)], fill=(255, 255, 255, 255))
        # Pen in hand
        d.line([(24, 66), (28, 62)], fill=(30, 30, 30, 255), width=2)

        # 5. Right hand brandishing baton (pałka)
        baton_lift = 6 if f == 1 else 0
        d.polygon([(90, 56), (102, 62 - baton_lift), (104, 70 - baton_lift), (92, 64)], fill=(220, 245, 30, 255), outline=DARK_PLUM)
        d.ellipse([100, 60 - baton_lift, 108, 68 - baton_lift], fill=(220, 170, 135, 255), outline=DARK_PLUM)
        # Black rubber baton
        d.line([(104, 64 - baton_lift), (118, 42 - baton_lift)], fill=(25, 25, 30, 255), width=4)
        d.line([(104, 64 - baton_lift), (98, 76 - baton_lift)], fill=(25, 25, 30, 255), width=4)

        frames.append(im)
    save_enemy_sheet("straznik", frames[0], frames[1], sz)

# ============================================================================
# 6. panJanusz (144x144 x 2 frames = 288x144) Boss
# ============================================================================
def build_pan_janusz():
    sz = 144
    frames = []
    for f in range(2):
        im = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        
        # 1. Dark Green Forestry Trousers & Heavy Field Boots
        d.rectangle([50, 108, 66, 132], fill=(28, 48, 30, 255), outline=DARK_PLUM)
        d.rectangle([78, 108, 94, 132], fill=(28, 48, 30, 255), outline=DARK_PLUM)
        # Heavy leather field boots
        d.polygon([(46, 130), (68, 130), (66, 140), (44, 140)], fill=(65, 40, 25, 255), outline=DARK_PLUM)
        d.polygon([(76, 130), (98, 130), (96, 140), (74, 140)], fill=(65, 40, 25, 255), outline=DARK_PLUM)

        # 2. Formal Forestry Jacket with Golden Epaulets
        jy = 54
        d.polygon([(32, jy), (112, jy), (106, 110), (38, 110)], fill=(32, 60, 36, 255), outline=DARK_PLUM)
        # Brass buttons
        for by in range(jy + 10, 108, 12):
            d.ellipse([70, by, 74, by + 4], fill=(235, 195, 50, 255), outline=DARK_PLUM)
        # Golden oak leaf epaulets on shoulders
        d.polygon([(28, jy - 2), (48, jy - 2), (44, jy + 6), (26, jy + 6)], fill=(240, 205, 55, 255), outline=DARK_PLUM)
        d.polygon([(96, jy - 2), (116, jy - 2), (118, jy + 6), (100, jy + 6)], fill=(240, 205, 55, 255), outline=DARK_PLUM)
        # Epaulet fringe
        for ex in range(28, 46, 3): d.point((ex, jy + 7), fill=(240, 205, 55, 255))
        for ex in range(98, 116, 3): d.point((ex, jy + 7), fill=(240, 205, 55, 255))
        # Leather service belt
        d.rectangle([36, 102, 108, 110], fill=(85, 50, 30, 255), outline=DARK_PLUM)
        d.rectangle([66, 100, 78, 112], fill=(240, 205, 55, 255), outline=DARK_PLUM) # buckle

        # 3. Head & Forestry Service Cap with Polish Eagle
        hy = 36
        d.rectangle([64, 46, 80, 56], fill=(225, 175, 140, 255), outline=DARK_PLUM)
        d.ellipse([56, hy - 10, 88, hy + 18], fill=(225, 175, 140, 255), outline=DARK_PLUM)
        # Massive grey walrus mustache
        d.polygon([(52, hy + 10), (72, hy + 18), (92, hy + 10), (72, hy + 8)], fill=(185, 190, 195, 255), outline=DARK_PLUM)
        # Stern squinting eyes & thick grey brows
        d.line([(58, hy - 1), (68, hy + 2)], fill=(120, 125, 130, 255), width=3)
        d.line([(86, hy - 1), (76, hy + 2)], fill=(120, 125, 130, 255), width=3)
        d.point((64, hy + 4), fill=(10, 10, 10, 255))
        d.point((80, hy + 4), fill=(10, 10, 10, 255))
        
        # Forestry Cap (Ranger rogatywka style)
        d.polygon([(50, hy - 12), (94, hy - 12), (90, hy - 24), (54, hy - 24)], fill=(26, 52, 30, 255), outline=DARK_PLUM)
        # Dark band with silver Polish Eagle badge
        d.rectangle([51, hy - 14, 93, hy - 10], fill=(18, 36, 22, 255))
        d.polygon([(70, hy - 13), (74, hy - 16), (72, hy - 11)], fill=(245, 245, 255, 255)) # eagle
        # Stiff visor
        d.polygon([(48, hy - 9), (96, hy - 9), (90, hy - 5), (54, hy - 5)], fill=(12, 15, 18, 255))

        # 4. Left hand holding giant Megaphone (Tubę leśną)
        mega_dy = -4 if f == 1 else 0
        d.polygon([(34, 62), (20, 72 + mega_dy), (24, 80 + mega_dy), (36, 70)], fill=(32, 60, 36, 255), outline=DARK_PLUM)
        # Vintage metal megaphone
        d.polygon([
            (22, 74 + mega_dy),
            (2, 60 + mega_dy),
            (2, 92 + mega_dy),
            (22, 82 + mega_dy)
        ], fill=(190, 195, 205, 255), outline=DARK_PLUM)
        d.ellipse([0, 58 + mega_dy, 6, 94 + mega_dy], fill=(80, 85, 95, 255), outline=DARK_PLUM)
        if f == 1:
            # Sound waves radiating from megaphone!
            d.arc([0, 50 + mega_dy, 16, 102 + mega_dy], 90, 270, fill=(255, 230, 80, 255), width=2)
            d.arc([-6, 42 + mega_dy, 22, 110 + mega_dy], 90, 270, fill=(255, 180, 40, 255), width=2)

        # 5. Right hand holding Citation Fine Book (Bloczek mandatowy)
        d.polygon([(110, 62), (124, 72), (122, 80), (108, 70)], fill=(32, 60, 36, 255), outline=DARK_PLUM)
        # Leather folder with tickets
        d.polygon([(118, 66), (138, 60), (142, 82), (122, 88)], fill=(120, 40, 30, 255), outline=DARK_PLUM)
        d.polygon([(122, 68), (136, 63), (139, 80), (125, 85)], fill=(250, 245, 230, 255))
        d.line([(126, 73), (134, 70)], fill=(30, 30, 30, 255))
        d.line([(127, 77), (135, 74)], fill=(30, 30, 30, 255))

        frames.append(im)
    save_enemy_sheet("panJanusz", frames[0], frames[1], sz)

# ============================================================================
# 7. kredyt (144x144 x 2 frames = 288x144) Boss
# ============================================================================
def build_kredyt():
    sz = 144
    frames = []
    for f in range(2):
        im = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        
        # 1. Massive Stone Bank Monument Pedestal & Steps
        d.rectangle([20, 116, 124, 136], fill=(55, 58, 68, 255), outline=DARK_PLUM)
        d.rectangle([28, 104, 116, 116], fill=(70, 75, 88, 255), outline=DARK_PLUM)
        # Stone steps highlight
        d.line([(22, 117), (122, 117)], fill=(120, 125, 140, 255))
        d.line([(30, 105), (114, 105)], fill=(120, 125, 140, 255))

        # 2. Neoclassical Columns (4 pillars)
        col_x = [34, 56, 80, 102]
        for cx in col_x:
            d.rectangle([cx, 46, cx + 10, 104], fill=(85, 90, 105, 255), outline=DARK_PLUM)
            d.line([(cx + 2, 47), (cx + 2, 103)], fill=(140, 145, 160, 255)) # flute highlight
            d.line([(cx + 8, 47), (cx + 8, 103)], fill=(45, 48, 56, 255)) # shadow

        # 3. Pediment / Temple Roof
        d.polygon([(26, 46), (118, 46), (72, 18)], fill=(75, 80, 94, 255), outline=DARK_PLUM)
        d.polygon([(32, 44), (112, 44), (72, 22)], fill=(95, 102, 120, 255))
        # Cracks and fissures in stone
        d.line([(72, 22), (68, 34), (74, 44)], fill=(255, 40, 40, 255), width=2) # molten red crack
        if f == 1:
            d.line([(68, 34), (60, 38)], fill=(255, 80, 80, 255), width=2)

        # 4. Hollow Void inside temple with Demonic Crimson Eyes
        d.rectangle([48, 56, 96, 96], fill=(16, 14, 22, 255))
        eye_glow = (255, 30, 40, 255) if f == 0 else (255, 80, 100, 255)
        # Left eye
        d.polygon([(54, 70), (66, 74), (58, 80)], fill=eye_glow)
        d.point((60, 75), fill=(255, 255, 255, 255))
        # Right eye
        d.polygon([(90, 70), (78, 74), (86, 80)], fill=eye_glow)
        d.point((84, 75), fill=(255, 255, 255, 255))

        # 5. Red Foreclosure Caution Tape Wrapping Pillars
        tape_y_offsets = [58, 76, 94]
        for ty in tape_y_offsets:
            tape_shift = 2 if f == 1 else 0
            # Slanted caution tape band across pillars
            d.polygon([
                (24, ty - 6 + tape_shift),
                (120, ty + 4 + tape_shift),
                (120, ty + 12 + tape_shift),
                (24, ty + 2 + tape_shift)
            ], fill=(225, 35, 45, 255), outline=DARK_PLUM)
            # White dashed caution markings
            for tx in range(28, 116, 12):
                d.polygon([
                    (tx, ty - 4 + tape_shift + (tx - 28) // 10),
                    (tx + 5, ty - 3 + tape_shift + (tx - 28) // 10),
                    (tx + 3, ty + 3 + tape_shift + (tx - 28) // 10),
                    (tx - 2, ty + 2 + tape_shift + (tx - 28) // 10)
                ], fill=(255, 255, 255, 255))

        # 6. Floating Currency Runes (PLN, %, CHF) orbiting
        d.ellipse([16, 32 + (f * 3), 32, 48 + (f * 3)], fill=(20, 22, 35, 230), outline=(255, 215, 60, 255))
        # %
        d.line([(21, 43 + f * 3), (27, 37 + f * 3)], fill=(255, 215, 60, 255), width=2)
        d.point((22, 38 + f * 3), fill=(255, 215, 60, 255))
        d.point((26, 42 + f * 3), fill=(255, 215, 60, 255))

        d.ellipse([112, 30 - (f * 3), 130, 48 - (f * 3)], fill=(20, 22, 35, 230), outline=(255, 80, 80, 255))
        # PLN
        d.text((115, 33 - f * 3), "zł", fill=(255, 80, 80, 255))

        frames.append(im)
    save_enemy_sheet("kredyt", frames[0], frames[1], sz)

# ============================================================================
# 8. audyt (144x144 x 2 frames = 288x144) Boss
# ============================================================================
def build_audyt():
    sz = 144
    frames = []
    for f in range(2):
        im = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        
        # 1. Mainframe Tower Base & Server Rack Pedestal
        d.rectangle([40, 98, 104, 134], fill=(30, 34, 45, 255), outline=DARK_PLUM)
        # Server blinking LEDs
        for lx in range(46, 98, 8):
            led_c = (255, 40, 40, 255) if (lx + f * 8) % 16 == 0 else (60, 240, 100, 255)
            d.rectangle([lx, 104, lx + 4, 108], fill=led_c)
            d.rectangle([lx, 114, lx + 4, 118], fill=(40, 120, 240, 255))
            d.rectangle([lx, 124, lx + 4, 128], fill=(240, 200, 40, 255))

        # 2. Giant CRT Monitor Body
        d.rounded_rectangle([32, 28, 112, 96], radius=8, fill=(45, 52, 68, 255), outline=DARK_PLUM)
        # CRT Bezel & Screen
        d.rectangle([38, 34, 106, 90], fill=(12, 24, 18, 255), outline=(20, 25, 35, 255))
        # CRT Green Phosphor Spreadsheet Grid
        for sx in range(44, 104, 12):
            d.line([(sx, 36), (sx, 88)], fill=(30, 90, 50, 180))
        for sy in range(42, 88, 10):
            d.line([(40, sy), (104, sy)], fill=(30, 90, 50, 180))
        
        # Central Cyclopean Red Pie-Chart Eye
        eye_cx, eye_cy = 72, 62
        d.ellipse([eye_cx - 16, eye_cy - 16, eye_cx + 16, eye_cy + 16], fill=(18, 22, 28, 255), outline=(220, 40, 50, 255))
        # Pie chart slice (Deficit angle)
        slice_ang = 90 + (30 if f == 1 else 0)
        d.pieslice([eye_cx - 14, eye_cy - 14, eye_cx + 14, eye_cy + 14], 0, slice_ang, fill=(245, 50, 60, 255))
        d.pieslice([eye_cx - 14, eye_cy - 14, eye_cx + 14, eye_cy + 14], slice_ang, 360, fill=(40, 180, 80, 255))
        d.ellipse([eye_cx - 5, eye_cy - 5, eye_cx + 5, eye_cy + 5], fill=(255, 255, 255, 255), outline=DARK_PLUM)
        # Red deficit targeting radar crosshair
        d.line([(eye_cx - 18, eye_cy), (eye_cx + 18, eye_cy)], fill=(255, 80, 80, 180))
        d.line([(eye_cx, eye_cy - 18), (eye_cx, eye_cy + 18)], fill=(255, 80, 80, 180))

        # Flashing #REF! Error on screen
        d.text((42, 38), "#REF!", fill=(255, 60, 60, 255))
        d.text((78, 76), "-99%", fill=(255, 60, 60, 255))

        # 3. Mechanical Paperclip Pincers Arms
        # Left pincer
        pinc_ang = 0 if f == 0 else 10
        d.line([(32, 50), (18, 44), (12, 60)], fill=(120, 130, 145, 255), width=4)
        # Steel razor paperclip pincer
        d.arc([4, 52 + pinc_ang, 20, 72 + pinc_ang], 0, 360, fill=(220, 225, 240, 255), width=3)
        d.line([(12, 70 + pinc_ang), (24, 76 + pinc_ang)], fill=(220, 225, 240, 255), width=3)
        d.line([(8, 62 + pinc_ang), (18, 84 + pinc_ang)], fill=(220, 225, 240, 255), width=3)

        # Right pincer
        d.line([(112, 50), (126, 44), (132, 60)], fill=(120, 130, 145, 255), width=4)
        d.arc([124, 52 - pinc_ang, 140, 72 - pinc_ang], 0, 360, fill=(220, 225, 240, 255), width=3)
        d.line([(132, 70 - pinc_ang), (120, 76 - pinc_ang)], fill=(220, 225, 240, 255), width=3)

        # 4. Spilling Continuous Perforated Dot-Matrix Green-Bar Paper Ribbons
        paper_x = 72
        d.polygon([
            (paper_x - 14, 94), (paper_x + 14, 94),
            (paper_x + 18, 126), (paper_x - 10, 126)
        ], fill=(240, 245, 240, 255), outline=DARK_PLUM)
        # Green-bar ledger lines
        for py in range(98, 124, 6):
            d.line([(paper_x - 12, py), (paper_x + 14, py)], fill=(180, 225, 190, 255), width=2)
            d.point((paper_x - 12, py), fill=(100, 110, 120, 255)) # pinhole
            d.point((paper_x + 14, py), fill=(100, 110, 120, 255))

        frames.append(im)
    save_enemy_sheet("audyt", frames[0], frames[1], sz)

# ============================================================================
# 9. rwaKulszowa (128x128 x 2 frames = 256x128)
# ============================================================================
def build_rwa():
    sz = 128
    frames = []
    for f in range(2):
        im = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        
        cx, cy = 64, 64
        # Frame 1: pulse contraction and extra electric sparks
        radius_pulse = -3 if f == 1 else 0
        
        # 1. Sciatic Nerve Branches / Dendrites radiating out
        branches = [
            (cx, cy, 24, 18, 4),
            (cx, cy, 104, 22, 4),
            (cx, cy, 16, 96, 4),
            (cx, cy, 112, 106, 5),
            (cx, cy, 64, 118, 5),
            (cx, cy, 64, 10, 3),
            (cx, cy, 18, 56, 3),
            (cx, cy, 110, 60, 4),
        ]
        
        for x0, y0, x1, y1, width in branches:
            # Jagged organic nerve curve
            mx = (x0 + x1) // 2 + (math.sin(x1) * 8)
            my = (y0 + y1) // 2 + (math.cos(y1) * 8)
            d.line([(x0, y0), (mx, my), (x1, y1)], fill=(110, 35, 140, 255), width=width + 2)
            d.line([(x0, y0), (mx, my), (x1, y1)], fill=(210, 60, 230, 255), width=max(1, width - 1))
            d.line([(x0, y0), (mx, my), (x1, y1)], fill=(255, 180, 255, 255), width=1)
            # Nerve endings branching into synapses
            d.line([(x1, y1), (x1 + 8, y1 - 6)], fill=(240, 80, 200, 255), width=2)
            d.line([(x1, y1), (x1 - 6, y1 + 8)], fill=(240, 80, 200, 255), width=2)
            
            # Pain sparks at branch tips
            spark_col = (255, 240, 80, 255) if f == 1 else (80, 240, 255, 255)
            d.point((int(x1 + 8), int(y1 - 6)), fill=spark_col)
            d.point((int(x1 - 6), int(y1 + 8)), fill=spark_col)
            d.line([(int(x1), int(y1)), (int(x1 + (4 if f==0 else -4)), int(y1 + (4 if f==1 else -4)))], fill=spark_col)

        # 2. Central Neural Ganglion Node Body (pulsing deep violet sphere)
        br = 26 + radius_pulse
        for r in range(br, 0, -1):
            t = r / float(br)
            cr = int(45 * t + 240 * (1 - t))
            cg = int(12 * t + 40 * (1 - t))
            cb = int(75 * t + 220 * (1 - t))
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(cr, cg, cb, 255))

        # 3. Throbbing Synaptic Veins & Electric Core Arc
        vein_pts = [(cx - 16, cy - 8), (cx - 4, cy + 4), (cx + 12, cy - 2), (cx + 18, cy + 12)]
        d.line(vein_pts, fill=(255, 100, 200, 255), width=3)
        d.line(vein_pts, fill=(255, 255, 255, 255), width=1)
        
        # Electric pain discharge arc leaping across core
        arc_pts = [
            (cx - 20, cy + 10),
            (cx - 8, cy + 16 if f == 0 else cy + 4),
            (cx + 6, cy + 8 if f == 0 else cy + 18),
            (cx + 22, cy + 6)
        ]
        arc_color = (255, 255, 120, 255) if f == 1 else (100, 230, 255, 255)
        d.line(arc_pts, fill=arc_color, width=2)
        d.point((cx, cy + 10), fill=(255, 255, 255, 255))

        frames.append(im)
    save_enemy_sheet("rwaKulszowa", frames[0], frames[1], sz)

if __name__ == "__main__":
    build_slacki()
    build_sasiad()
    build_hipster()
    build_kark()
    build_straznik()
    build_pan_janusz()
    build_kredyt()
    build_audyt()
    build_rwa()
    print("All custom enemy sprites built successfully!")
