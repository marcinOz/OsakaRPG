#!/usr/bin/env python3
"""generate_hd_sprites.py - Generate high-detail pixel art sprites for all 6 heroes.

Dimensions:
- Walk sheets: 32x48 per frame (4 columns x 4 rows = 128x192)
  Rows: 0=Down, 1=Left, 2=Right, 3=Up
  Columns: 0=Step L, 1=Neutral, 2=Step R, 3=Neutral Bob
- Battle sheets: 64x80 per frame (6 frames horizontal = 384x80)
  0=Idle, 1=Windup, 2=Attack, 3=Skill, 4=Hurt, 5=KO
- Sit sheets: 32x32 per frame (2 frames horizontal = 64x32)
  0=Seated, 1=Seated Breath/Nod
"""
import os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "public", "assets", "sprites")
os.makedirs(OUT, exist_ok=True)

# Master Color Palette (16/32-bit rich tones)
PAL = {
    'void': (0, 3, 11, 255),
    'ink': (6, 18, 32, 255),
    'navy': (10, 24, 43, 255),
    'panel': (12, 33, 52, 255),
    'panel_hi': (16, 45, 59, 255),
    'steel': (32, 61, 84, 255),
    'slate': (46, 59, 77, 255),
    'grey': (94, 111, 122, 255),
    'silver': (151, 160, 166, 255),
    'cyan': (158, 203, 212, 255),
    'cyan_hi': (200, 238, 244, 255),
    'white': (235, 240, 245, 255),
    'yellow': (232, 216, 74, 255),
    'yellow_hi': (255, 245, 120, 255),
    'orange': (224, 116, 44, 255),
    'red': (192, 57, 43, 255),
    'red_hi': (235, 87, 87, 255),
    'green': (95, 200, 90, 255),
    'green_hi': (130, 230, 120, 255),
    'forest': (45, 75, 45, 255),
    'denim': (63, 107, 143, 255),
    'denim_hi': (95, 145, 190, 255),
    'denim_dk': (35, 65, 95, 255),
    'olive': (75, 90, 48, 255),
    'olive_dk': (45, 58, 30, 255),
    'olive_hi': (110, 130, 70, 255),
    'leather': (95, 55, 30, 255),
    'leather_dk': (60, 35, 20, 255),
    
    # Skin Ramps
    'skin_hi': (255, 225, 200, 255),
    'skin_mid': (235, 185, 145, 255),
    'skin_shadow': (195, 140, 100, 255),
    'skin_dark': (150, 100, 70, 255),
    
    # Hair / Beard Ramps
    'hair_black': (20, 18, 24, 255),
    'hair_brown_dk': (45, 28, 20, 255),
    'hair_brown': (85, 50, 32, 255),
    'hair_brown_hi': (125, 80, 50, 255),
    'hair_quiff': (140, 95, 60, 255),
    
    # Gear
    'grey_tank': (80, 85, 95, 255),
    'grey_tank_hi': (115, 120, 135, 255),
    'hoodie_dark': (25, 30, 42, 255),
    'lifevest_orange': (245, 100, 25, 255),
    'lifevest_hi': (255, 145, 60, 255),
}

HEROES = ['danny', 'alior', 'lisu', 'barti', 'oziem', 'luki']

def create_walk_sheet(hid: str) -> Image.Image:
    """Creates a 4 cols x 4 rows walk sheet (128 x 192)."""
    fw, fh = 32, 48
    sheet = Image.new("RGBA", (fw * 4, fh * 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(sheet)

    dirs = ['down', 'left', 'right', 'up']
    for r, direction in enumerate(dirs):
        for c in range(4):
            ox = c * fw
            oy = r * fh
            # c=0: step left, c=1: neutral, c=2: step right, c=3: neutral bob
            bob = 1 if c in (0, 2) else 0
            leg_phase = -1 if c == 0 else (1 if c == 2 else 0)
            draw_walk_frame(d, ox, oy, hid, direction, leg_phase, bob)
    return sheet

def draw_walk_frame(d: ImageDraw.ImageDraw, ox: int, oy: int, hid: str, dir_name: str, leg_phase: int, bob: int):
    ink = PAL['ink']
    skin = PAL['skin_mid']
    skin_s = PAL['skin_shadow']
    
    # Center is at ox + 16, baseY at oy + 44
    cx = ox + 16
    by = oy + 44 + bob
    
    # 1. Legs & Shoes
    leg_l_x = cx - 5 + (leg_phase * 2 if dir_name in ('down', 'up') else 0)
    leg_r_x = cx + 2 - (leg_phase * 2 if dir_name in ('down', 'up') else 0)
    leg_w = 4
    leg_h = 10
    
    pants_color = PAL['navy']
    shoes_color = PAL['slate']
    if hid == 'danny':
        pants_color = PAL['ink']
        shoes_color = PAL['red']
    elif hid == 'alior':
        pants_color = PAL['navy']
        shoes_color = PAL['green']
    elif hid == 'lisu':
        pants_color = PAL['olive_dk']
        shoes_color = PAL['red_hi'] # signature red sneakers!
    elif hid == 'barti':
        pants_color = PAL['denim_dk']
        shoes_color = PAL['white']
    elif hid == 'oziem':
        pants_color = PAL['olive_dk']
        shoes_color = PAL['leather']
    elif hid == 'luki':
        pants_color = PAL['panel']
        shoes_color = PAL['cyan']

    if dir_name in ('left', 'right'):
        # Side profile legs
        dx = -leg_phase * 3 if dir_name == 'right' else leg_phase * 3
        d.rectangle([cx - 3 + dx, by - leg_h, cx + 3 + dx, by - 3], fill=pants_color, outline=ink)
        d.rectangle([cx - 4 + dx, by - 3, cx + 4 + dx, by], fill=shoes_color, outline=ink)
    else:
        # Legs
        d.rectangle([leg_l_x, by - leg_h, leg_l_x + leg_w, by - 3], fill=pants_color, outline=ink)
        d.rectangle([leg_r_x, by - leg_h, leg_r_x + leg_w, by - 3], fill=pants_color, outline=ink)
        # Shoes
        d.rectangle([leg_l_x - 1, by - 3, leg_l_x + leg_w + 1, by], fill=shoes_color, outline=ink)
        d.rectangle([leg_r_x - 1, by - 3, leg_r_x + leg_w + 1, by], fill=shoes_color, outline=ink)

    # 2. Torso & Clothing
    torso_y = by - 24
    torso_w = 14
    torso_h = 15
    tx = cx - 7
    
    if hid == 'danny':
        # Danny: grey muscle tank, bare muscular arms
        d.rectangle([tx, torso_y, tx + torso_w, torso_y + torso_h], fill=PAL['grey_tank'], outline=ink)
        d.rectangle([tx + 3, torso_y + 2, tx + torso_w - 3, torso_y + 6], fill=PAL['grey_tank_hi'])
        # Bare muscular arms
        arm_l = tx - 4
        arm_r = tx + torso_w
        d.rectangle([arm_l, torso_y + 2, arm_l + 3, torso_y + torso_h - 2], fill=skin, outline=ink)
        d.rectangle([arm_r, torso_y + 2, arm_r + 3, torso_y + torso_h - 2], fill=skin, outline=ink)
        # Shaker bottle in right hand
        if dir_name != 'up':
            d.rectangle([arm_r + 1, torso_y + torso_h - 6, arm_r + 5, torso_y + torso_h + 1], fill=PAL['cyan'], outline=ink)
            d.rectangle([arm_r + 2, torso_y + torso_h - 8, arm_r + 4, torso_y + torso_h - 6], fill=PAL['red_hi'])
            
    elif hid == 'alior':
        # Alior: dark hoodie with green 1-UP pixel logo
        d.rectangle([tx - 2, torso_y, tx + torso_w + 2, torso_y + torso_h], fill=PAL['hoodie_dark'], outline=ink)
        # 1-UP logo
        if dir_name != 'up':
            d.rectangle([cx - 2, torso_y + 4, cx + 2, torso_y + 8], fill=PAL['green'])
            d.point([cx, torso_y + 3], fill=PAL['green_hi'])
        # Gamepad in hands
        if dir_name != 'up':
            d.rectangle([cx - 4, torso_y + torso_h - 4, cx + 4, torso_y + torso_h], fill=PAL['slate'], outline=ink)
            d.point([cx - 2, torso_y + torso_h - 2], fill=PAL['red_hi'])
            d.point([cx + 2, torso_y + torso_h - 2], fill=PAL['green'])

    elif hid == 'lisu':
        # Lisu: tactical green/olive vest with binoculars
        d.rectangle([tx, torso_y, tx + torso_w, torso_y + torso_h], fill=PAL['olive'], outline=ink)
        d.rectangle([tx + 2, torso_y + 2, tx + 6, torso_y + 8], fill=PAL['olive_hi'])
        d.rectangle([tx + 8, torso_y + 2, tx + 12, torso_y + 8], fill=PAL['olive_hi'])
        # Binoculars neck strap
        if dir_name != 'up':
            d.line([cx - 3, torso_y, cx - 2, torso_y + 6], fill=PAL['ink'])
            d.line([cx + 3, torso_y, cx + 2, torso_y + 6], fill=PAL['ink'])
            d.rectangle([cx - 3, torso_y + 6, cx + 3, torso_y + 10], fill=PAL['slate'], outline=ink)
            d.point([cx - 2, torso_y + 9], fill=PAL['cyan'])
            d.point([cx + 2, torso_y + 9], fill=PAL['cyan'])

    elif hid == 'barti':
        # Barti: blue denim jacket with fleece collar & headphones
        d.rectangle([tx - 1, torso_y, tx + torso_w + 1, torso_y + torso_h], fill=PAL['denim'], outline=ink)
        d.rectangle([tx + 3, torso_y, tx + torso_w - 3, torso_y + torso_h], fill=PAL['white']) # white tee
        d.rectangle([tx, torso_y, tx + 3, torso_y + torso_h], fill=PAL['denim_dk'])
        d.rectangle([tx + torso_w - 2, torso_y, tx + torso_w + 1, torso_y + torso_h], fill=PAL['denim_dk'])
        # DJ Headphones around neck
        d.rectangle([cx - 5, torso_y - 2, cx + 5, torso_y + 2], fill=PAL['slate'], outline=ink)
        d.point([cx - 5, torso_y], fill=PAL['silver'])
        d.point([cx + 5, torso_y], fill=PAL['silver'])

    elif hid == 'oziem':
        # Oziem: tactical bushcraft field jacket with pockets & tinderbox
        d.rectangle([tx - 1, torso_y, tx + torso_w + 1, torso_y + torso_h], fill=PAL['olive'], outline=ink)
        d.rectangle([tx + 1, torso_y + 2, tx + 5, torso_y + 6], fill=PAL['olive_dk'])
        d.rectangle([tx + 8, torso_y + 2, tx + 12, torso_y + 6], fill=PAL['olive_dk'])
        d.rectangle([tx + 1, torso_y + 8, tx + 5, torso_y + 13], fill=PAL['leather']) # holster
        # Belt
        d.rectangle([tx, torso_y + torso_h - 3, tx + torso_w, torso_y + torso_h], fill=PAL['leather_dk'])
        d.point([cx, torso_y + torso_h - 2], fill=PAL['yellow'])

    elif hid == 'luki':
        # Łuki: bright orange life vest over navy wetsuit + rescue lifebuoy
        d.rectangle([tx - 1, torso_y, tx + torso_w + 1, torso_y + torso_h], fill=PAL['lifevest_orange'], outline=ink)
        d.rectangle([tx + 2, torso_y + 2, tx + 5, torso_y + torso_h - 2], fill=PAL['lifevest_hi'])
        d.rectangle([tx + 8, torso_y + 2, tx + 11, torso_y + torso_h - 2], fill=PAL['lifevest_hi'])
        # Lifebuoy strap diagonal
        if dir_name != 'up':
            d.line([tx, torso_y + 2, tx + torso_w, torso_y + torso_h - 2], fill=PAL['white'], width=2)
            # Torpedo float / lifebuoy on side
            d.ellipse([tx + torso_w, torso_y + 4, tx + torso_w + 6, torso_y + 14], fill=PAL['red_hi'], outline=ink)

    # 3. Head & Likeness
    head_w = 12
    head_h = 13
    hx = cx - 6
    hy = torso_y - head_h + 1
    
    # Head base
    d.rectangle([hx, hy, hx + head_w, hy + head_h], fill=skin, outline=ink)
    
    if hid == 'danny':
        # Buzzcut hair & full trimmed beard
        d.rectangle([hx, hy, hx + head_w, hy + 3], fill=PAL['hair_black'])
        if dir_name != 'up':
            # Beard & jawline
            d.rectangle([hx, hy + 7, hx + head_w, hy + head_h], fill=PAL['hair_black'])
            d.rectangle([hx + 2, hy + 4, hx + 4, hy + 6], fill=skin) # cheeks
            d.rectangle([hx + 7, hy + 4, hx + 9, hy + 6], fill=skin)
            # Eyes
            d.point([hx + 3, hy + 4], fill=ink)
            d.point([hx + 8, hy + 4], fill=ink)
    elif hid == 'alior':
        # Bald with shine + beard + headset
        d.point([hx + 3, hy + 1], fill=PAL['skin_hi']) # bald sheen
        # Gaming headset headband
        d.line([hx - 1, hy + 1, hx + head_w + 1, hy + 1], fill=PAL['green_hi'])
        d.rectangle([hx - 2, hy + 3, hx, hy + 7], fill=PAL['green'], outline=ink) # earcups
        d.rectangle([hx + head_w, hy + 3, hx + head_w + 2, hy + 7], fill=PAL['green'], outline=ink)
        if dir_name != 'up':
            # Beard
            d.rectangle([hx + 1, hy + 7, hx + head_w - 1, hy + head_h], fill=PAL['hair_brown_dk'])
            # Mic boom
            d.line([hx, hy + 6, hx + 3, hy + 9], fill=PAL['silver'])
            # Eyes
            d.point([hx + 3, hy + 4], fill=ink)
            d.point([hx + 8, hy + 4], fill=ink)
    elif hid == 'lisu':
        # Ninja cowl & mask
        d.rectangle([hx, hy, hx + head_w, hy + head_h], fill=PAL['olive_dk'], outline=ink)
        if dir_name != 'up':
            # Eye opening slit
            d.rectangle([hx + 2, hy + 3, hx + head_w - 2, hy + 6], fill=skin)
            d.point([hx + 3, hy + 4], fill=ink)
            d.point([hx + 8, hy + 4], fill=ink)
    elif hid == 'barti':
        # Big stylish quiff / pompadour hair
        d.rectangle([hx - 1, hy - 3, hx + head_w + 1, hy + 3], fill=PAL['hair_quiff'])
        d.rectangle([hx + 2, hy - 4, hx + head_w, hy - 1], fill=PAL['hair_brown_hi'])
        if dir_name != 'up':
            d.point([hx + 3, hy + 5], fill=ink)
            d.point([hx + 8, hy + 5], fill=ink)
            d.line([hx + 4, hy + 8, hx + 7, hy + 8], fill=PAL['skin_shadow']) # clean shaven smile
    elif hid == 'oziem':
        # Full outdoorsman beard & tousled hair
        d.rectangle([hx, hy, hx + head_w, hy + 4], fill=PAL['hair_brown_dk'])
        d.point([hx + 1, hy - 1], fill=PAL['hair_brown'])
        d.point([hx + head_w - 2, hy - 1], fill=PAL['hair_brown'])
        if dir_name != 'up':
            d.rectangle([hx, hy + 6, hx + head_w, hy + head_h + 1], fill=PAL['hair_brown_dk']) # thick beard
            d.point([hx + 3, hy + 4], fill=ink)
            d.point([hx + 8, hy + 4], fill=ink)
    elif hid == 'luki':
        # Wavy hair & diving goggles on forehead
        d.rectangle([hx, hy, hx + head_w, hy + 4], fill=PAL['hair_black'])
        # Diving goggles perched on forehead
        d.rectangle([hx + 1, hy + 1, hx + head_w - 1, hy + 4], fill=PAL['cyan'], outline=ink)
        d.point([hx + 3, hy + 2], fill=PAL['cyan_hi'])
        d.point([hx + 8, hy + 2], fill=PAL['cyan_hi'])
        if dir_name != 'up':
            d.point([hx + 3, hy + 6], fill=ink)
            d.point([hx + 8, hy + 6], fill=ink)
            d.line([hx + 4, hy + 9, hx + 7, hy + 9], fill=skin_s)

def create_battle_sheet(hid: str) -> Image.Image:
    """Creates a 6 frames horizontal battle sheet (384 x 80).
    Frames: 0=Idle, 1=Windup, 2=Attack, 3=Skill, 4=Hurt, 5=KO
    """
    fw, fh = 64, 80
    sheet = Image.new("RGBA", (fw * 6, fh), (0, 0, 0, 0))
    d = ImageDraw.Draw(sheet)

    for frame_idx in range(6):
        ox = frame_idx * fw
        draw_battle_frame(d, ox, 0, hid, frame_idx)
    return sheet

def draw_battle_frame(d: ImageDraw.ImageDraw, ox: int, oy: int, hid: str, frame: int):
    # Scale: character is around 40-50px tall, positioned centered at ox + 32, baseY = oy + 70
    cx = ox + 32
    by = oy + 72
    ink = PAL['ink']
    skin = PAL['skin_mid']
    
    # State offsets
    lunge = 6 if frame == 2 else (3 if frame == 1 else 0)
    recoil = -6 if frame == 4 else 0
    drop = 18 if frame == 5 else 0
    bx = cx - lunge + recoil
    cy = by + drop

    if frame == 5:
        # KO: collapsed/kneeling
        d.ellipse([bx - 18, cy - 8, bx + 18, cy], fill=(0, 0, 0, 80)) # shadow
        d.rectangle([bx - 14, cy - 12, bx + 14, cy - 2], fill=PAL['navy'], outline=ink)
        d.rectangle([bx - 12, cy - 18, bx + 6, cy - 8], fill=PAL['panel'], outline=ink)
        d.rectangle([bx - 8, cy - 26, bx + 4, cy - 18], fill=skin, outline=ink)
        return

    # Shadow
    d.ellipse([bx - 14, by - 4, bx + 14, by + 4], fill=(0, 0, 0, 80))

    # Legs
    d.rectangle([bx - 9, cy - 22, bx - 3, cy - 2], fill=PAL['navy'], outline=ink)
    d.rectangle([bx + 3, cy - 22, bx + 9, cy - 2], fill=PAL['navy'], outline=ink)
    # Shoes
    shoe_color = PAL['red_hi'] if hid == 'lisu' else PAL['slate']
    d.rectangle([bx - 11, cy - 4, bx - 2, cy], fill=shoe_color, outline=ink)
    d.rectangle([bx + 1, cy - 4, bx + 10, cy], fill=shoe_color, outline=ink)

    # Torso & Arms
    tw, th = 20, 24
    tx = bx - 10
    ty = cy - 44
    
    # Specific outfits
    if hid == 'danny':
        d.rectangle([tx, ty, tx + tw, ty + th], fill=PAL['grey_tank'], outline=ink)
        # Muscular arms
        d.rectangle([tx - 6, ty + 2, tx, ty + th - 4], fill=skin, outline=ink)
        d.rectangle([tx + tw, ty + 2, tx + tw + 6, ty + th - 4], fill=skin, outline=ink)
        if frame == 2:
            # Massive punch / shaker slam
            d.line([bx, ty + 6, bx - 24, ty + 12], fill=PAL['white'], width=4)
            d.rectangle([bx - 28, ty + 8, bx - 18, ty + 22], fill=PAL['cyan_hi'], outline=ink)
    elif hid == 'alior':
        d.rectangle([tx - 2, ty, tx + tw + 2, ty + th], fill=PAL['hoodie_dark'], outline=ink)
        d.rectangle([bx - 4, ty + 4, bx + 4, ty + 12], fill=PAL['green']) # 1-UP logo
        if frame == 3: # Skill cast: green code matrix
            for k in range(5):
                d.point([bx - 10 + k * 5, ty - 10 - k * 3], fill=PAL['green_hi'])
    elif hid == 'lisu':
        d.rectangle([tx, ty, tx + tw, ty + th], fill=PAL['olive'], outline=ink)
        # Tactical straps
        d.line([tx, ty + 4, tx + tw, ty + th - 4], fill=PAL['ink'], width=2)
        if frame == 2:
            # Ninja flash strike
            d.line([bx + 10, cy - 10, bx - 26, cy - 25], fill=PAL['red_hi'], width=3)
    elif hid == 'barti':
        d.rectangle([tx, ty, tx + tw, ty + th], fill=PAL['denim'], outline=ink)
        d.rectangle([bx - 4, ty + 4, bx + 4, ty + th - 2], fill=PAL['white'])
        # Headphones
        d.rectangle([bx - 8, ty - 4, bx + 8, ty + 2], fill=PAL['silver'], outline=ink)
        if frame == 3: # Bass drop soundwave rings
            d.ellipse([bx - 30, ty - 10, bx + 30, ty + 30], outline=PAL['cyan_hi'])
    elif hid == 'oziem':
        d.rectangle([tx - 2, ty, tx + tw + 2, ty + th], fill=PAL['olive'], outline=ink)
        d.rectangle([tx - 4, ty + 6, tx, ty + 16], fill=PAL['leather'])
        if frame == 3: # Campfire kindle flame burst
            d.polygon([(bx - 8, ty + 10), (bx - 18, ty - 12), (bx - 2, ty - 4)], fill=PAL['orange'])
    elif hid == 'luki':
        d.rectangle([tx - 1, ty, tx + tw + 1, ty + th], fill=PAL['lifevest_orange'], outline=ink)
        d.ellipse([bx + 10, ty + 2, bx + 22, ty + 20], fill=PAL['red_hi'], outline=ink) # lifebuoy

    # Head
    hw, hh = 16, 18
    hx = bx - 8
    hy = ty - hh + 2
    d.rectangle([hx, hy, hx + hw, hy + hh], fill=skin, outline=ink)
    
    # Hair & Face
    if hid == 'danny':
        d.rectangle([hx, hy, hx + hw, hy + 4], fill=PAL['hair_black'])
        d.rectangle([hx, hy + 10, hx + hw, hy + hh], fill=PAL['hair_black']) # beard
    elif hid == 'alior':
        d.line([hx - 2, hy + 2, hx + hw + 2, hy + 2], fill=PAL['green'])
        d.rectangle([hx + 1, hy + 9, hx + hw - 1, hy + hh], fill=PAL['hair_brown_dk'])
    elif hid == 'lisu':
        d.rectangle([hx, hy, hx + hw, hy + hh], fill=PAL['olive_dk'], outline=ink)
        d.rectangle([hx + 3, hy + 5, hx + hw - 3, hy + 9], fill=skin)
    elif hid == 'barti':
        d.rectangle([hx - 2, hy - 4, hx + hw + 2, hy + 4], fill=PAL['hair_quiff'])
    elif hid == 'oziem':
        d.rectangle([hx, hy, hx + hw, hy + 5], fill=PAL['hair_brown_dk'])
        d.rectangle([hx, hy + 8, hx + hw, hy + hh + 2], fill=PAL['hair_brown_dk'])
    elif hid == 'luki':
        d.rectangle([hx, hy, hx + hw, hy + 5], fill=PAL['hair_black'])
        d.rectangle([hx + 2, hy + 1, hx + hw - 2, hy + 5], fill=PAL['cyan'], outline=ink)

    # Eyes
    eye_y = hy + 7
    d.point([hx + 4, eye_y], fill=ink)
    d.point([hx + 10, eye_y], fill=ink)

def create_sit_sheet(hid: str) -> Image.Image:
    """Creates a 2 frames horizontal sit sheet (64 x 32)."""
    fw, fh = 32, 32
    sheet = Image.new("RGBA", (fw * 2, fh), (0, 0, 0, 0))
    d = ImageDraw.Draw(sheet)

    for frame in (0, 1):
        ox = frame * fw
        cx = ox + 16
        by = 28 + (1 if frame == 1 else 0)
        ink = PAL['ink']
        skin = PAL['skin_mid']
        
        # Shadow & Log
        d.ellipse([cx - 12, by - 2, cx + 12, by + 4], fill=(0, 0, 0, 90))
        
        # Crossed legs
        d.rectangle([cx - 10, by - 8, cx + 10, by - 2], fill=PAL['navy'], outline=ink)
        # Shoes
        shoe_color = PAL['red_hi'] if hid == 'lisu' else PAL['slate']
        d.rectangle([cx - 11, by - 4, cx - 7, by], fill=shoe_color)
        d.rectangle([cx + 7, by - 4, cx + 11, by], fill=shoe_color)
        
        # Torso
        torso_y = by - 18
        if hid == 'danny':
            d.rectangle([cx - 6, torso_y, cx + 6, torso_y + 10], fill=PAL['grey_tank'], outline=ink)
        elif hid == 'alior':
            d.rectangle([cx - 7, torso_y, cx + 7, torso_y + 10], fill=PAL['hoodie_dark'], outline=ink)
        elif hid == 'lisu':
            d.rectangle([cx - 6, torso_y, cx + 6, torso_y + 10], fill=PAL['olive'], outline=ink)
        elif hid == 'barti':
            d.rectangle([cx - 6, torso_y, cx + 6, torso_y + 10], fill=PAL['denim'], outline=ink)
        elif hid == 'oziem':
            d.rectangle([cx - 6, torso_y, cx + 6, torso_y + 10], fill=PAL['olive'], outline=ink)
        elif hid == 'luki':
            d.rectangle([cx - 6, torso_y, cx + 6, torso_y + 10], fill=PAL['lifevest_orange'], outline=ink)

        # Head
        hy = torso_y - 10
        d.rectangle([cx - 5, hy, cx + 5, hy + 10], fill=skin, outline=ink)
        
        # Hair / Beard
        if hid == 'danny':
            d.rectangle([cx - 5, hy, cx + 5, hy + 3], fill=PAL['hair_black'])
            d.rectangle([cx - 5, hy + 6, cx + 5, hy + 10], fill=PAL['hair_black'])
        elif hid == 'alior':
            d.line([cx - 6, hy + 1, cx + 6, hy + 1], fill=PAL['green'])
            d.rectangle([cx - 4, hy + 6, cx + 4, hy + 10], fill=PAL['hair_brown_dk'])
        elif hid == 'lisu':
            d.rectangle([cx - 5, hy, cx + 5, hy + 10], fill=PAL['olive_dk'], outline=ink)
            d.rectangle([cx - 3, hy + 3, cx + 3, hy + 6], fill=skin)
        elif hid == 'barti':
            d.rectangle([cx - 6, hy - 3, cx + 6, hy + 3], fill=PAL['hair_quiff'])
        elif hid == 'oziem':
            d.rectangle([cx - 5, hy, cx + 5, hy + 3], fill=PAL['hair_brown_dk'])
            d.rectangle([cx - 5, hy + 5, cx + 5, hy + 11], fill=PAL['hair_brown_dk'])
        elif hid == 'luki':
            d.rectangle([cx - 5, hy, cx + 5, hy + 3], fill=PAL['hair_black'])
            d.rectangle([cx - 3, hy + 1, cx + 3, hy + 3], fill=PAL['cyan'])

        # Eye blink in frame 1
        eye_color = PAL['skin_shadow'] if frame == 1 else ink
        d.point([cx - 2, hy + 4], fill=eye_color)
        d.point([cx + 2, hy + 4], fill=eye_color)

    return sheet

def main():
    print("Generating HD hero spritesheets...")
    for hid in HEROES:
        # Walk: 32x48
        walk = create_walk_sheet(hid)
        walk_path = os.path.join(OUT, f"{hid}_walk.png")
        walk.save(walk_path, "PNG")
        print(f"Saved {walk_path} ({walk.size})")

        # Battle: 64x80
        battle = create_battle_sheet(hid)
        battle_path = os.path.join(OUT, f"{hid}_battle.png")
        battle.save(battle_path, "PNG")
        print(f"Saved {battle_path} ({battle.size})")

        # Sit: 32x32
        sit = create_sit_sheet(hid)
        sit_path = os.path.join(OUT, f"{hid}_sit.png")
        sit.save(sit_path, "PNG")
        print(f"Saved {sit_path} ({sit.size})")

    print("Hero sprites generated successfully!")

if __name__ == "__main__":
    main()
