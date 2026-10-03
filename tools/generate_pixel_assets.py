#!/usr/bin/env python3
"""generate_pixel_assets.py - creates high-detail 16-bit pixel art assets for THE PACK:
1. Walk sprites (16x24, 3 cols x 4 rows = 48x96) for all 6 heroes
2. Battle sprites (32x40, 8 frames = 256x40) for all 6 heroes
3. Seated campfire sprites (24x24, 2 frames = 48x24) for all 6 heroes
4. Enemy sprites (48x48 x 2 frames = 96x48) for bolKregoslupa and slacki
5. Animated campfire fire (32x40 x 6 frames = 192x40)
6. Skill FX sheets (32x32 x 6 frames = 192x32)
7. Tilesets (16x16 tiles + JSON) for apartment, city, and forest
8. Backgrounds (480x270) for title, battle_apartment, battle_city, battle_forest, campfire
9. public/assets/manifest.json
"""
import json
import math
import os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "public", "assets")
os.makedirs(os.path.join(ASSETS, "sprites"), exist_ok=True)
os.makedirs(os.path.join(ASSETS, "enemies"), exist_ok=True)
os.makedirs(os.path.join(ASSETS, "bg"), exist_ok=True)
os.makedirs(os.path.join(ASSETS, "tiles"), exist_ok=True)
os.makedirs(os.path.join(ASSETS, "fx"), exist_ok=True)

# Colors from palette
VOID = (0x00, 0x03, 0x0B, 255)
INK = (0x06, 0x12, 0x20, 255)
NAVY = (0x0A, 0x18, 0x2B, 255)
PANEL = (0x0C, 0x21, 0x34, 255)
PANEL_HI = (0x10, 0x2D, 0x3B, 255)
STEEL = (0x20, 0x3D, 0x54, 255)
SLATE = (0x2E, 0x3B, 0x4D, 255)
TEAL = (0x40, 0x6A, 0x6A, 255)
GREY = (0x5E, 0x6F, 0x7A, 255)
SILVER = (0x97, 0xA0, 0xA6, 255)
CYAN = (0x9E, 0xCB, 0xD4, 255)
WHITE = (0xD8, 0xDA, 0xDA, 255)
DARK_BROWN = (0x4F, 0x41, 0x41, 255)
PLUM = (0x1B, 0x13, 0x19, 255)
YELLOW = (0xE8, 0xD8, 0x4A, 255)
GREEN = (0x5F, 0xC8, 0x5A, 255)
FIRE = (0xE0, 0x74, 0x2C, 255)
FIRE_HI = (0xF6, 0xC0, 0x4A, 255)
RED = (0xC0, 0x39, 0x2B, 255)
DENIM = (0x3F, 0x6B, 0x8F, 255)

# Skin tones
SKIN_LIGHT = (0xF0, 0xC8, 0xA0, 255)
SKIN_MID = (0xD9, 0xA0, 0x66, 255)
SKIN_DARK = (0xA8, 0x6B, 0x4C, 255)
BEARD_BROWN = (0x6E, 0x44, 0x30, 255)
HAIR_DARK = (0x2A, 0x1A, 0x14, 255)

# Character visual palettes
CHAR_PALETTES = {
    'danny': {
        'skin': SKIN_MID, 'hair': HAIR_DARK, 'beard': BEARD_BROWN,
        'shirt': (0x20, 0x3D, 0x54, 255), 'pants': (0x0C, 0x21, 0x34, 255), 'shoes': (0x4F, 0x41, 0x41, 255),
        'accent': FIRE
    },
    'alior': {
        'skin': SKIN_MID, 'hair': SKIN_MID, 'beard': BEARD_BROWN,
        'shirt': (0x1E, 0x28, 0x44, 255), 'pants': (0x0A, 0x18, 0x2B, 255), 'shoes': (0x5E, 0x6F, 0x7A, 255),
        'accent': GREEN
    },
    'lisu': {
        'skin': SKIN_LIGHT, 'hair': (0x4B, 0x5A, 0x30, 255), 'beard': (0x4B, 0x5A, 0x30, 255),
        'shirt': (0x4B, 0x5A, 0x30, 255), 'pants': (0x2F, 0x3A, 0x24, 255), 'shoes': RED,
        'accent': RED
    },
    'barti': {
        'skin': SKIN_LIGHT, 'hair': (0x7A, 0x62, 0x48, 255), 'beard': None,
        'shirt': DENIM, 'pants': (0x1E, 0x28, 0x44, 255), 'shoes': (0xD8, 0xDA, 0xDA, 255),
        'accent': (0x5F, 0xC8, 0x5A, 255)
    },
    'oziem': {
        'skin': SKIN_MID, 'hair': (0x4A, 0x2E, 0x22, 255), 'beard': (0x4A, 0x2E, 0x22, 255),
        'shirt': (0x4B, 0x5A, 0x30, 255), 'pants': (0x5C, 0x46, 0x30, 255), 'shoes': (0x2A, 0x1A, 0x14, 255),
        'accent': TEAL
    },
    'luki': {
        'skin': SKIN_MID, 'hair': HAIR_DARK, 'beard': None,
        'shirt': (0xE0, 0x74, 0x2C, 255), 'pants': (0x20, 0x3D, 0x54, 255), 'shoes': (0x0C, 0x21, 0x34, 255),
        'accent': CYAN
    },
}

def draw_hero_walk_frame(d, fx, fy, hid, direction, step):
    """Draw one 16x24 character frame. Direction: 0=down, 1=left, 2=right, 3=up. Step: 0=L, 1=idle, 2=R."""
    cp = CHAR_PALETTES[hid]
    outline = PLUM

    # Head (y=2..9, x=4..11)
    head_x = fx + 4
    head_y = fy + 2
    # Outline
    d.rectangle([head_x - 1, head_y - 1, head_x + 7, head_y + 7], fill=outline)
    # Face base
    d.rectangle([head_x, head_y, head_x + 6, head_y + 6], fill=cp['skin'])

    # Hair / Hood / Beard
    if hid == 'lisu':
        # Green hood
        d.rectangle([head_x, head_y, head_x + 6, head_y + 2], fill=cp['shirt'])
        d.rectangle([head_x, head_y + 4, head_x + 6, head_y + 6], fill=cp['shirt']) # mask
        if direction != 3:
            # Ninja eyes
            d.rectangle([head_x + 1, head_y + 3, head_x + 5, head_y + 3], fill=PLUM)
    elif hid == 'alior':
        # Bald top + beard + headset
        if cp['beard'] and direction != 3:
            d.rectangle([head_x + 1, head_y + 4, head_x + 5, head_y + 6], fill=cp['beard'])
        # Headset band
        d.line([head_x, head_y, head_x + 6, head_y], fill=GREEN)
        d.point([head_x, head_y + 2], fill=GREEN)
        d.point([head_x + 6, head_y + 2], fill=GREEN)
    else:
        # Hair top
        d.rectangle([head_x, head_y, head_x + 6, head_y + 2], fill=cp['hair'])
        if cp['beard'] and direction != 3:
            d.rectangle([head_x + 1, head_y + 4, head_x + 5, head_y + 6], fill=cp['beard'])

    # Eyes for forward / side view
    if direction == 0 and hid != 'lisu':
        d.point([head_x + 2, head_y + 3], fill=PLUM)
        d.point([head_x + 4, head_y + 3], fill=PLUM)
    elif direction == 1 and hid != 'lisu':
        d.point([head_x + 1, head_y + 3], fill=PLUM)
    elif direction == 2 and hid != 'lisu':
        d.point([head_x + 5, head_y + 3], fill=PLUM)

    # Torso (y=10..16, x=3..12)
    body_x = fx + 3
    body_y = fy + 9
    d.rectangle([body_x - 1, body_y - 1, body_x + 9, body_y + 7], fill=outline)
    d.rectangle([body_x, body_y, body_x + 8, body_y + 6], fill=cp['shirt'])

    # Torso details: life vest for Luki, muscle cut for Danny, denim collar for Barti
    if hid == 'luki':
        d.rectangle([body_x + 1, body_y + 1, body_x + 3, body_y + 5], fill=FIRE)
        d.rectangle([body_x + 5, body_y + 1, body_x + 7, body_y + 5], fill=FIRE)
    elif hid == 'danny':
        # Bare arms on sides
        d.rectangle([body_x, body_y + 1, body_x + 1, body_y + 5], fill=cp['skin'])
        d.rectangle([body_x + 7, body_y + 1, body_x + 8, body_y + 5], fill=cp['skin'])

    # Legs (y=16..22)
    leg_y = fy + 16
    leg1_x = fx + 4
    leg2_x = fx + 8
    # Step offsets
    offset1 = 0
    offset2 = 0
    if step == 0:
        offset1 = -1
        offset2 = 1
    elif step == 2:
        offset1 = 1
        offset2 = -1

    # Draw legs & pants
    d.rectangle([leg1_x - 1, leg_y - 1, leg1_x + 2, leg_y + 5 + offset1], fill=outline)
    d.rectangle([leg2_x - 1, leg_y - 1, leg2_x + 2, leg_y + 5 + offset2], fill=outline)
    d.rectangle([leg1_x, leg_y, leg1_x + 1, leg_y + 4 + offset1], fill=cp['pants'])
    d.rectangle([leg2_x, leg_y, leg2_x + 1, leg_y + 4 + offset2], fill=cp['pants'])

    # Shoes
    d.rectangle([leg1_x, leg_y + 4 + offset1, leg1_x + 2, leg_y + 5 + offset1], fill=cp['shoes'])
    d.rectangle([leg2_x - 1, leg_y + 4 + offset2, leg2_x + 1, leg_y + 5 + offset2], fill=cp['shoes'])

def make_hero_walk_sheets():
    for hid in CHAR_PALETTES.keys():
        img = Image.new("RGBA", (48, 96), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        # 4 rows (down, left, right, up) x 3 cols (step0, idle, step1)
        for row in range(4):
            for col in range(3):
                draw_hero_walk_frame(d, col * 16, row * 24, hid, direction=row, step=col)
        dest = os.path.join(ASSETS, "sprites", f"{hid}_walk.png")
        img.save(dest)
        print(f"Generated {dest}")

def make_hero_battle_sheets():
    # 8 frames 32x40 = 256x40: idle0, idle1, attack0, attack1, attack2, skill0, hurt, ko
    for hid in CHAR_PALETTES.keys():
        img = Image.new("RGBA", (256, 40), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        cp = CHAR_PALETTES[hid]
        outline = PLUM

        for f in range(8):
            fx = f * 32
            fy = 4
            # Hero facing left towards enemies
            bob = 1 if f == 1 else (2 if f in (2, 3) else 0)
            if f == 7: # KO pose on ground
                d.rectangle([fx + 4, fy + 24, fx + 26, fy + 32], fill=outline)
                d.rectangle([fx + 5, fy + 25, fx + 25, fy + 31], fill=cp['shirt'])
                d.rectangle([fx + 20, fy + 22, fx + 26, fy + 28], fill=cp['skin'])
                continue

            # Head
            hx = fx + 10 - (2 if f in (2, 3, 5) else 0)
            hy = fy + 4 + bob
            d.rectangle([hx - 1, hy - 1, hx + 11, hy + 11], fill=outline)
            d.rectangle([hx, hy, hx + 10, hy + 10], fill=cp['skin'])
            # Hair / Beard
            if hid != 'alior':
                d.rectangle([hx, hy, hx + 10, hy + 3], fill=cp['hair'])
            if cp['beard']:
                d.rectangle([hx, hy + 6, hx + 6, hy + 10], fill=cp['beard'])
            # Eye facing left
            d.point([hx + 2, hy + 5], fill=PLUM)

            # Torso
            bx = fx + 8 - (3 if f in (2, 3, 5) else 0)
            by = fy + 14 + bob
            d.rectangle([bx - 1, by - 1, bx + 13, by + 13], fill=outline)
            d.rectangle([bx, by, bx + 12, by + 12], fill=cp['shirt'])

            # Attack swing weapon / effect
            if f == 3: # attack peak
                d.rectangle([bx - 8, by + 2, bx - 2, by + 6], fill=WHITE)
                d.line([bx - 8, by + 4, bx - 2, by + 4], fill=CYAN)
            elif f == 5: # skill pose
                d.rectangle([bx - 6, by - 4, bx, by + 2], fill=YELLOW)

            # Legs
            lx = fx + 10
            ly = fy + 26
            d.rectangle([lx - 1, ly - 1, lx + 11, ly + 10], fill=outline)
            d.rectangle([lx, ly, lx + 4, ly + 9], fill=cp['pants'])
            d.rectangle([lx + 6, ly, lx + 10, ly + 9], fill=cp['pants'])
            d.rectangle([lx - 1, ly + 7, lx + 4, ly + 9], fill=cp['shoes'])
            d.rectangle([lx + 5, ly + 7, lx + 10, ly + 9], fill=cp['shoes'])

        dest = os.path.join(ASSETS, "sprites", f"{hid}_battle.png")
        img.save(dest)
        print(f"Generated {dest}")

def make_hero_sit_sprites():
    # 24x24 x 2 frames = 48x24
    for hid in CHAR_PALETTES.keys():
        img = Image.new("RGBA", (48, 24), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        cp = CHAR_PALETTES[hid]
        outline = PLUM

        for f in range(2):
            fx = f * 24
            bob = 1 if f == 1 else 0
            # Seated posture
            d.rectangle([fx + 7, 3 + bob, fx + 16, 11 + bob], fill=outline)
            d.rectangle([fx + 8, 4 + bob, fx + 15, 10 + bob], fill=cp['skin'])
            if hid != 'alior':
                d.rectangle([fx + 8, 4 + bob, fx + 15, 6 + bob], fill=cp['hair'])
            if cp['beard']:
                d.rectangle([fx + 9, 8 + bob, fx + 14, 10 + bob], fill=cp['beard'])

            # Body leaning forward toward fire
            d.rectangle([fx + 6, 12 + bob, fx + 17, 18 + bob], fill=outline)
            d.rectangle([fx + 7, 13 + bob, fx + 16, 17 + bob], fill=cp['shirt'])
            # Crossed/seated legs
            d.rectangle([fx + 5, 18, fx + 18, 22], fill=cp['pants'])
            d.rectangle([fx + 6, 21, fx + 10, 23], fill=cp['shoes'])

        dest = os.path.join(ASSETS, "sprites", f"{hid}_sit.png")
        img.save(dest)
        print(f"Generated {dest}")

def make_enemies():
    # bolKregoslupa: glowing angry spine creature 48x48 x 2 frames = 96x48
    img = Image.new("RGBA", (96, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for f in range(2):
        fx = f * 48
        bob = math.sin(f * 3.14) * 2
        cx, cy = fx + 24, 24 + int(bob)
        # Vertebrae bones
        for i in range(5):
            vy = cy - 14 + i * 7
            w = 8 + int(math.sin(i * 0.8) * 6)
            d.rectangle([cx - w, vy - 2, cx + w, vy + 2], fill=PLUM)
            d.rectangle([cx - w + 1, vy - 1, cx + w - 1, vy + 1], fill=WHITE)
            # Glowing red nerve/pain spikes
            d.point([cx - w - 2, vy], fill=RED)
            d.point([cx + w + 2, vy], fill=RED)
        # Menacing glowing eyes at the top skull/cervical
        d.point([cx - 4, cy - 12], fill=RED)
        d.point([cx + 4, cy - 12], fill=RED)
        d.point([cx - 3, cy - 12], fill=YELLOW)
        d.point([cx + 3, cy - 12], fill=YELLOW)
    img.save(os.path.join(ASSETS, "enemies", "bolKregoslupa.png"))

    # slacki: floating chat-bubble monster with unread badges
    img = Image.new("RGBA", (96, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for f in range(2):
        fx = f * 48
        bob = math.cos(f * 3.14) * 2
        cx, cy = fx + 24, 24 + int(bob)
        # Big chat bubble
        d.rectangle([cx - 16, cy - 12, cx + 16, cy + 10], fill=PLUM)
        d.rectangle([cx - 15, cy - 11, cx + 15, cy + 9], fill=WHITE)
        # Bubble tail
        d.polygon([(cx - 8, cy + 9), (cx - 14, cy + 15), (cx - 3, cy + 9)], fill=WHITE)
        # Slack hashtag / dots inside
        d.rectangle([cx - 8, cy - 3, cx + 8, cy - 1], fill=TEAL)
        d.rectangle([cx - 8, cy + 2, cx + 4, cy + 4], fill=GREY)
        # Angry eyes
        d.rectangle([cx - 10, cy - 7, cx - 6, cy - 5], fill=RED)
        d.rectangle([cx + 6, cy - 7, cx + 10, cy - 5], fill=RED)
        # Red unread badge in top right "+99"
        d.ellipse([cx + 8, cy - 18, cx + 22, cy - 6], fill=RED)
        d.point([cx + 14, cy - 12], fill=WHITE)
        d.point([cx + 15, cy - 12], fill=WHITE)
    img.save(os.path.join(ASSETS, "enemies", "slacki.png"))
    print("Generated enemy sprites")

def make_fire_animation():
    # 32x40 x 6 frames = 192x40
    img = Image.new("RGBA", (192, 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for f in range(6):
        fx = f * 32
        # Stone circle & logs at base (y=30..38)
        d.rectangle([fx + 4, 32, fx + 28, 36], fill=DARK_BROWN)
        d.rectangle([fx + 8, 34, fx + 24, 38], fill=PLUM)
        # Flickering fire flames
        h = 20 + int(math.sin(f * 1.05) * 5)
        # Outer red flame
        d.polygon([(fx + 8, 32), (fx + 16, 32 - h), (fx + 24, 32)], fill=RED)
        # Middle orange flame
        d.polygon([(fx + 10, 32), (fx + 16, 34 - h), (fx + 22, 32)], fill=FIRE)
        # Inner yellow/white core
        d.polygon([(fx + 12, 32), (fx + 16, 36 - h), (fx + 20, 32)], fill=FIRE_HI)
        d.polygon([(fx + 14, 32), (fx + 16, 38 - h), (fx + 18, 32)], fill=WHITE)
        # Flying ember spark
        d.point([fx + 14 + (f * 3) % 7, 10 + (f * 5) % 12], fill=FIRE_HI)
    img.save(os.path.join(ASSETS, "bg", "fire.png"))
    print("Generated fire.png")

def make_fx_sheets():
    # 32x32 x 6 frames = 192x32
    fx_list = ['shield', 'glitch', 'smoke', 'bass', 'leaves', 'splash', 'hit']
    for name in fx_list:
        img = Image.new("RGBA", (192, 32), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        for f in range(6):
            fx = f * 32
            cx, cy = fx + 16, 16
            progress = (f + 1) / 6.0
            r = int(progress * 13)

            if name == 'shield':
                # Expanding cyan barrier shield
                d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=CYAN, width=2)
                d.point([cx, cy], fill=WHITE)
            elif name == 'glitch':
                # Digital matrix glitch lines
                for line_i in range(4):
                    ly = cy - 8 + line_i * 5
                    shift = int(math.sin(f + line_i) * 6)
                    d.line([cx - 10 + shift, ly, cx + 10 + shift, ly], fill=GREEN, width=1)
            elif name == 'smoke':
                # Puff of grey smoke clouds
                for p in range(5):
                    ang = p * 1.25 + f * 0.2
                    px = cx + int(math.cos(ang) * (r * 0.8))
                    py = cy + int(math.sin(ang) * (r * 0.8))
                    d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=GREY)
            elif name == 'bass':
                # Sound wave ripples
                d.arc([cx - r, cy - r, cx + r, cy + r], start=0, end=360, fill=YELLOW, width=2)
            elif name == 'leaves':
                # Whirling green survival leaves
                for l in range(4):
                    ang = l * 1.57 + f * 0.8
                    lx = cx + int(math.cos(ang) * r)
                    ly = cy + int(math.sin(ang) * r)
                    d.rectangle([lx - 2, ly - 2, lx + 2, ly + 2], fill=GREEN)
            elif name == 'splash':
                # Blue water splashes
                d.arc([cx - r, cy - r, cx + r, cy + r], start=180, end=360, fill=CYAN, width=2)
            elif name == 'hit':
                # Yellow star burst
                d.line([cx - r, cy - r, cx + r, cy + r], fill=YELLOW, width=2)
                d.line([cx - r, cy + r, cx + r, cy - r], fill=WHITE, width=2)
        img.save(os.path.join(ASSETS, "fx", f"{name}.png"))
    print("Generated skill FX sheets")

def make_tilesets():
    # 16x16 tiles per set. 8 tiles per row = 128px wide.
    # Apartment
    apt = Image.new("RGBA", (128, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(apt)
    # 0: wood floor
    d.rectangle([0, 0, 15, 15], fill=(0x5C, 0x46, 0x30, 255))
    d.line([0, 7, 15, 7], fill=(0x3A, 0x2A, 0x1E, 255))
    # 1: wallpaper wall
    d.rectangle([16, 0, 31, 15], fill=NAVY)
    d.line([16, 15, 31, 15], fill=STEEL)
    # 2: wall top
    d.rectangle([32, 0, 47, 15], fill=INK)
    # 3: bed pillow/head
    d.rectangle([48, 0, 63, 15], fill=WHITE)
    # 4: bed blanket
    d.rectangle([64, 0, 79, 15], fill=DENIM)
    # 5: rug
    d.rectangle([80, 0, 95, 15], fill=TEAL)
    d.rectangle([82, 2, 93, 13], fill=CYAN)
    # 6: desk PC
    d.rectangle([96, 0, 111, 15], fill=DARK_BROWN)
    d.rectangle([100, 3, 107, 10], fill=CYAN)
    # 7: door
    d.rectangle([112, 0, 127, 15], fill=(0x7A, 0x62, 0x48, 255))
    d.point([124, 8], fill=YELLOW)
    apt.save(os.path.join(ASSETS, "tiles", "apartment.png"))

    # City (blokowisko)
    city = Image.new("RGBA", (128, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(city)
    # 0: asphalt road
    d.rectangle([0, 0, 15, 15], fill=(0x2E, 0x3B, 0x4D, 255))
    # 1: sidewalk pavement
    d.rectangle([16, 0, 31, 15], fill=(0x5E, 0x6F, 0x7A, 255))
    d.rectangle([17, 1, 30, 14], outline=(0x81, 0x79, 0x7A, 255))
    # 2: block wall concrete
    d.rectangle([32, 0, 47, 15], fill=(0x81, 0x79, 0x7A, 255))
    # 3: block window
    d.rectangle([48, 0, 63, 15], fill=(0x81, 0x79, 0x7A, 255))
    d.rectangle([51, 3, 60, 12], fill=CYAN)
    # 4: grass lawn
    d.rectangle([64, 0, 79, 15], fill=(0x2F, 0x3A, 0x24, 255))
    d.point([68, 6], fill=(0x6F, 0x7F, 0x3E, 255))
    d.point([74, 11], fill=(0x6F, 0x7F, 0x3E, 255))
    # 5: Żabka green kiosk
    d.rectangle([80, 0, 95, 15], fill=GREEN)
    d.rectangle([82, 3, 93, 10], fill=WHITE)
    # 6: bench
    d.rectangle([96, 0, 111, 15], fill=(0x5E, 0x6F, 0x7A, 255))
    d.rectangle([98, 5, 109, 10], fill=DARK_BROWN)
    # 7: garage door
    d.rectangle([112, 0, 127, 15], fill=STEEL)
    for gy in range(2, 14, 3):
        d.line([112, gy, 127, gy], fill=PANEL_HI)
    city.save(os.path.join(ASSETS, "tiles", "city.png"))

    # Forest night
    forest = Image.new("RGBA", (128, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(forest)
    # 0: dark forest grass
    d.rectangle([0, 0, 15, 15], fill=(0x1F, 0x2A, 0x1C, 255))
    # 1: dirt path
    d.rectangle([16, 0, 31, 15], fill=(0x3A, 0x2A, 0x1E, 255))
    # 2: tree trunk
    d.rectangle([32, 0, 47, 15], fill=(0x1F, 0x2A, 0x1C, 255))
    d.rectangle([37, 0, 42, 15], fill=(0x4A, 0x2E, 0x22, 255))
    # 3: tree canopy dark green
    d.rectangle([48, 0, 63, 15], fill=(0x2E, 0x4A, 0x2A, 255))
    # 4: water lake
    d.rectangle([64, 0, 79, 15], fill=PANEL)
    d.line([64, 4, 79, 4], fill=CYAN)
    # 5: stone/rock
    d.rectangle([80, 0, 95, 15], fill=(0x1F, 0x2A, 0x1C, 255))
    d.ellipse([82, 4, 93, 12], fill=GREY)
    # 6: wooden log seat
    d.rectangle([96, 0, 111, 15], fill=(0x1F, 0x2A, 0x1C, 255))
    d.rectangle([97, 6, 110, 11], fill=(0x5C, 0x46, 0x30, 255))
    # 7: hammock strap
    d.rectangle([112, 0, 127, 15], fill=(0x1F, 0x2A, 0x1C, 255))
    d.line([112, 4, 127, 11], fill=YELLOW)
    forest.save(os.path.join(ASSETS, "tiles", "forest.png"))
    print("Generated tilesets")

def make_backgrounds():
    # 480x270 backgrounds
    # Title: night forest with distant campfire glow and lake
    title = Image.new("RGBA", (480, 270), VOID)
    d = ImageDraw.Draw(title)
    # Sky gradient
    for y in range(160):
        c = (int(0x06 + y * 0.05), int(0x12 + y * 0.08), int(0x20 + y * 0.12), 255)
        d.line([0, y, 479, y], fill=c)
    # Distant lake horizon (y=160..210)
    for y in range(160, 210):
        d.line([0, y, 479, y], fill=NAVY)
    # Distant tree silhouettes
    for tx in range(0, 480, 12):
        th = 20 + int(math.sin(tx * 0.05) * 15)
        d.polygon([(tx, 160), (tx + 6, 160 - th), (tx + 12, 160)], fill=INK)
    # Foreground clearing & subtle amber fire glow in distance
    d.rectangle([0, 210, 479, 269], fill=(0x10, 0x1B, 0x14, 255))
    d.ellipse([210, 180, 270, 240], fill=(0x4A, 0x28, 0x12, 120))
    title.save(os.path.join(ASSETS, "bg", "title.png"))

    # Campfire scene (Ch.7 background clearing, hammocks between trees, fire pit)
    camp = Image.new("RGBA", (480, 270), VOID)
    d = ImageDraw.Draw(camp)
    # Deep midnight sky with stars
    d.rectangle([0, 0, 479, 140], fill=INK)
    for sx, sy in [(50, 30), (120, 20), (220, 40), (330, 25), (410, 35), (280, 15)]:
        d.point([sx, sy], fill=WHITE)
    # Dense forest ground
    d.rectangle([0, 140, 479, 269], fill=(0x15, 0x22, 0x18, 255))
    # Tree trunks on sides
    d.rectangle([30, 60, 60, 250], fill=(0x3A, 0x2A, 0x1E, 255))
    d.rectangle([420, 60, 450, 250], fill=(0x3A, 0x2A, 0x1E, 255))
    # Hammocks tied between trees
    d.arc([60, 110, 200, 170], start=0, end=180, fill=DENIM, width=3)
    d.arc([280, 110, 420, 170], start=0, end=180, fill=GREEN, width=3)
    # Campfire pit center ground (x=240, y=190)
    d.ellipse([210, 180, 270, 210], fill=(0x30, 0x20, 0x15, 255))
    camp.save(os.path.join(ASSETS, "bg", "campfire.png"))

    # Battle backgrounds
    for name, wall_col, floor_col in [
        ('battle_apartment', (0x10, 0x2D, 0x3B, 255), (0x5C, 0x46, 0x30, 255)),
        ('battle_city', (0x40, 0x6A, 0x6A, 255), (0x2E, 0x3B, 0x4D, 255)),
        ('battle_forest', INK, (0x1F, 0x2A, 0x1C, 255)),
    ]:
        bimg = Image.new("RGBA", (480, 270), wall_col)
        bd = ImageDraw.Draw(bimg)
        bd.rectangle([0, 170, 479, 269], fill=floor_col)
        bd.line([0, 170, 479, 170], fill=PLUM, width=2)
        bimg.save(os.path.join(ASSETS, "bg", f"{name}.png"))
    print("Generated backgrounds")

def make_manifest():
    manifest = {
        "images": {
            "title_bg": "assets/bg/title.png",
            "campfire_bg": "assets/bg/campfire.png",
            "battle_apartment_bg": "assets/bg/battle_apartment.png",
            "battle_city_bg": "assets/bg/battle_city.png",
            "battle_forest_bg": "assets/bg/battle_forest.png",
            "thumb_group": "assets/ui/thumb_group.png",
            "thumb_travel": "assets/ui/thumb_travel.png",
            "thumb_funny": "assets/ui/thumb_funny.png",
            "thumb_moments": "assets/ui/thumb_moments.png",
        },
        "portraits": {},
        "items": {},
        "spritesheets": {
            "fire": {"path": "assets/bg/fire.png", "frameWidth": 32, "frameHeight": 40},
            "enemy_bolKregoslupa": {"path": "assets/enemies/bolKregoslupa.png", "frameWidth": 48, "frameHeight": 48},
            "enemy_slacki": {"path": "assets/enemies/slacki.png", "frameWidth": 48, "frameHeight": 48},
        },
        "fonts": {
            "pixel": {"png": "assets/fonts/pixel.png", "fnt": "assets/fonts/pixel.fnt"},
            "pixel_big": {"png": "assets/fonts/pixel_big.png", "fnt": "assets/fonts/pixel_big.fnt"},
        }
    }

    # Heroes
    for hid in CHAR_PALETTES.keys():
        manifest["portraits"][f"portrait_{hid}_96"] = f"assets/portraits/{hid}_96.png"
        manifest["portraits"][f"portrait_{hid}_64"] = f"assets/portraits/{hid}_64.png"
        manifest["spritesheets"][f"{hid}_walk"] = {"path": f"assets/sprites/{hid}_walk.png", "frameWidth": 16, "frameHeight": 24}
        manifest["spritesheets"][f"{hid}_battle"] = {"path": f"assets/sprites/{hid}_battle.png", "frameWidth": 32, "frameHeight": 40}
        manifest["spritesheets"][f"{hid}_sit"] = {"path": f"assets/sprites/{hid}_sit.png", "frameWidth": 24, "frameHeight": 24}

    # Items
    item_names = [
        'shield', 'gauntlets', 'shaker', 'controller', 'cartridge', 'goggles',
        'binoculars', 'fox', 'sneakers', 'vinyl', 'turntable', 'speaker',
        'rope', 'multitool', 'campfire', 'divingGoggles', 'lifebuoy', 'backpack'
    ]
    for iname in item_names:
        manifest["items"][f"item_{iname}"] = f"assets/items/{iname}.png"

    # FX
    for fx_name in ['shield', 'glitch', 'smoke', 'bass', 'leaves', 'splash', 'hit']:
        manifest["spritesheets"][f"fx_{fx_name}"] = {"path": f"assets/fx/{fx_name}.png", "frameWidth": 32, "frameHeight": 32}

    # Tiles
    for tname in ['apartment', 'city', 'forest']:
        manifest["images"][f"tiles_{tname}"] = f"assets/tiles/{tname}.png"

    dest = os.path.join(ASSETS, "manifest.json")
    with open(dest, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"Saved {dest}")

if __name__ == "__main__":
    make_hero_walk_sheets()
    make_hero_battle_sheets()
    make_hero_sit_sprites()
    make_enemies()
    make_fire_animation()
    make_fx_sheets()
    make_tilesets()
    make_backgrounds()
    make_manifest()
