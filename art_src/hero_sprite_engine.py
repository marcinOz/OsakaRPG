#!/usr/bin/env python3
"""hero_sprite_engine.py - High-Detail Pixel Art Generator for all 6 Heroes.
Generates:
1. {hid}_walk.png: 128x192 px (4 directions: down, left, right, up; 4 walk frames of 32x48)
2. {hid}_battle.png: 512x80 px (8 animation states: idle0, idle1, windup, attack, skill, hurt, ko, victory; frame 64x80)
3. {hid}_sit.png: 64x32 px (2 breathing frames of 32x32)

Full artistic likeness from art_src/reference.jpg:
- Danny: Muscular gym build, beard, tank, athletic shorts, shaker
- Alior: Bald sheen, green headset + mic, 1-UP hoodie, controller
- Lisu: Olive cowl + mask, binoculars, red high-top sneakers
- Barti: Brown quiff pompadour, denim jacket over tee, headphones, vinyl record
- Oziem: Bushcraft beard & jacket, multi-tool holster, tinderbox
- Łuki: Wavy hair, diving goggles on forehead, orange rescue vest, lifebuoy
"""
import os
import math
from PIL import Image, ImageDraw

OUT_DIR = "public/assets/sprites"
os.makedirs(OUT_DIR, exist_ok=True)

DARK_PLUM = (24, 16, 22, 255)

# Palettes per hero
HERO_CONFIGS = {
    'danny': {
        'skin': (232, 178, 138), 'skin_sh': (178, 126, 92), 'skin_hi': (250, 206, 172),
        'hair': (32, 22, 20), 'hair_sh': (18, 12, 10), 'beard': (38, 26, 22),
        'top': (46, 52, 60), 'top_sh': (28, 32, 38), 'top_hi': (70, 78, 90),
        'bottom': (22, 24, 28), 'bottom_sh': (12, 14, 18),
        'shoes': (45, 48, 54), 'shoe_sole': (180, 185, 190),
        'accent': (80, 235, 100), # Neon shaker
    },
    'alior': {
        'skin': (226, 172, 132), 'skin_sh': (174, 120, 86), 'skin_hi': (248, 204, 168),
        'hair': (226, 172, 132), 'hair_sh': (174, 120, 86), 'beard': (42, 30, 24),
        'top': (28, 34, 52), 'top_sh': (18, 22, 35), 'top_hi': (45, 54, 78), # 1-UP hoodie
        'bottom': (40, 44, 54), 'bottom_sh': (24, 28, 36),
        'shoes': (55, 60, 68), 'shoe_sole': (170, 175, 180),
        'accent': (60, 220, 70), # Lime headset & controller
    },
    'lisu': {
        'skin': (234, 184, 144), 'skin_sh': (180, 130, 94), 'skin_hi': (250, 210, 176),
        'hair': (52, 70, 40), 'hair_sh': (34, 46, 26), 'beard': (25, 28, 30), # mask
        'top': (56, 74, 44), 'top_sh': (36, 48, 28), 'top_hi': (82, 106, 64), # olive cowl
        'bottom': (32, 38, 44), 'bottom_sh': (18, 22, 26),
        'shoes': (225, 35, 45), 'shoe_sole': (245, 248, 250), # Red sneakers
        'accent': (20, 20, 22), # Binoculars
    },
    'barti': {
        'skin': (238, 188, 148), 'skin_sh': (184, 134, 98), 'skin_hi': (252, 212, 178),
        'hair': (105, 68, 42), 'hair_sh': (65, 40, 24), 'hair_hi': (145, 95, 60), # Pompadour
        'beard': None,
        'top': (65, 110, 155), 'top_sh': (38, 70, 105), 'top_hi': (95, 150, 205), # Denim
        'bottom': (30, 42, 65), 'bottom_sh': (16, 25, 42),
        'shoes': (235, 238, 242), 'shoe_sole': (180, 185, 190),
        'accent': (22, 22, 24), # Vinyl record
    },
    'oziem': {
        'skin': (222, 168, 128), 'skin_sh': (172, 118, 84), 'skin_hi': (246, 200, 164),
        'hair': (75, 48, 32), 'hair_sh': (45, 28, 18), 'hair_hi': (108, 70, 48),
        'beard': (70, 45, 30),
        'top': (60, 80, 45), 'top_sh': (38, 52, 28), 'top_hi': (88, 115, 68), # Bushcraft jacket
        'bottom': (90, 72, 50), 'bottom_sh': (58, 45, 30),
        'shoes': (48, 32, 20), 'shoe_sole': (30, 20, 12),
        'accent': (190, 195, 205), # Multi-tool
    },
    'luki': {
        'skin': (228, 174, 134), 'skin_sh': (176, 124, 88), 'skin_hi': (248, 204, 168),
        'hair': (32, 26, 28), 'hair_sh': (18, 14, 16), 'hair_hi': (55, 46, 50), # Wavy
        'beard': None,
        'top': (245, 110, 25), 'top_sh': (185, 70, 15), 'top_hi': (255, 150, 60), # Orange vest
        'bottom': (28, 42, 65), 'bottom_sh': (16, 25, 40),
        'shoes': (25, 30, 40), 'shoe_sole': (50, 60, 75),
        'accent': (225, 35, 40), # Lifebuoy
    },
}

# ============================================================================
# WALK SPRITE ENGINE (32x48 frame, 4 directions x 4 frames = 128x192)
# ============================================================================
def render_walk_frame(hid, direction, frame_idx):
    """direction: 0=down, 1=left, 2=right, 3=up. frame_idx: 0..3."""
    cfg = HERO_CONFIGS[hid]
    im = Image.new("RGBA", (32, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    # Walk cycle leg offset
    # 0: idle, 1: step left, 2: idle, 3: step right
    leg_l = 0
    leg_r = 0
    bob = 0
    if frame_idx == 1:
        leg_l = -2
        leg_r = 2
        bob = -1
    elif frame_idx == 3:
        leg_l = 2
        leg_r = -2
        bob = -1

    # Shadow under character
    d.ellipse([8, 43, 24, 47], fill=(10, 12, 18, 120))

    # Center x
    cx = 16

    # 1. LEGS & SHOES
    if direction in (0, 3): # Down or Up
        # Left leg
        ly_l = 32 + bob + leg_l
        d.rectangle([10, 30 + bob, 15, ly_l + 8], fill=cfg['bottom'], outline=DARK_PLUM)
        d.polygon([(9, ly_l + 8), (15, ly_l + 8), (15, ly_l + 12), (9, ly_l + 12)], fill=cfg['shoes'], outline=DARK_PLUM)
        d.line([(9, ly_l + 12), (15, ly_l + 12)], fill=cfg['shoe_sole'])
        # Right leg
        ly_r = 32 + bob + leg_r
        d.rectangle([17, 30 + bob, 22, ly_r + 8], fill=cfg['bottom'], outline=DARK_PLUM)
        d.polygon([(17, ly_r + 8), (23, ly_r + 8), (23, ly_r + 12), (17, ly_r + 12)], fill=cfg['shoes'], outline=DARK_PLUM)
        d.line([(17, ly_r + 12), (23, ly_r + 12)], fill=cfg['shoe_sole'])
    elif direction == 1: # Left
        ly = 32 + bob
        # Back leg
        d.rectangle([cx - 2 - leg_r, ly, cx + 3 - leg_r, ly + 8], fill=cfg['bottom_sh'], outline=DARK_PLUM)
        d.polygon([(cx - 4 - leg_r, ly + 8), (cx + 3 - leg_r, ly + 8), (cx + 3 - leg_r, ly + 12), (cx - 4 - leg_r, ly + 12)], fill=cfg['shoes'], outline=DARK_PLUM)
        # Front leg
        d.rectangle([cx - 3 + leg_l, ly, cx + 2 + leg_l, ly + 8], fill=cfg['bottom'], outline=DARK_PLUM)
        d.polygon([(cx - 5 + leg_l, ly + 8), (cx + 2 + leg_l, ly + 8), (cx + 2 + leg_l, ly + 12), (cx - 5 + leg_l, ly + 12)], fill=cfg['shoes'], outline=DARK_PLUM)
    else: # Right
        ly = 32 + bob
        # Back leg
        d.rectangle([cx - 3 - leg_r, ly, cx + 2 - leg_r, ly + 8], fill=cfg['bottom_sh'], outline=DARK_PLUM)
        d.polygon([(cx - 3 - leg_r, ly + 8), (cx + 4 - leg_r, ly + 8), (cx + 4 - leg_r, ly + 12), (cx - 3 - leg_r, ly + 12)], fill=cfg['shoes'], outline=DARK_PLUM)
        # Front leg
        d.rectangle([cx - 2 + leg_l, ly, cx + 3 + leg_l, ly + 8], fill=cfg['bottom'], outline=DARK_PLUM)
        d.polygon([(cx - 2 + leg_l, ly + 8), (cx + 5 + leg_l, ly + 8), (cx + 5 + leg_l, ly + 12), (cx - 2 + leg_l, ly + 12)], fill=cfg['shoes'], outline=DARK_PLUM)

    # 2. TORSO & APPAREL
    ty = 18 + bob
    d.polygon([(9, ty), (23, ty), (22, ty + 14), (10, ty + 14)], fill=cfg['top'], outline=DARK_PLUM)
    # Highlights / Shadows
    d.line([(10, ty + 1), (10, ty + 13)], fill=cfg['top_hi'])
    d.line([(22, ty + 1), (22, ty + 13)], fill=cfg['top_sh'])

    # Specific hero apparel details
    if hid == 'danny':
        # Tank top muscular arms (bare skin)
        d.rectangle([7, ty + 2, 9, ty + 11], fill=cfg['skin'], outline=DARK_PLUM)
        d.rectangle([23, ty + 2, 25, ty + 11], fill=cfg['skin'], outline=DARK_PLUM)
        # Tank white trim
        d.line([(11, ty), (21, ty)], fill=(230, 235, 240, 255))
    elif hid == 'alior':
        # 1-UP lime logo on chest
        if direction == 0:
            d.rectangle([14, ty + 5, 18, ty + 9], fill=cfg['accent'], outline=DARK_PLUM)
    elif hid == 'lisu':
        # Binoculars around neck
        if direction == 0:
            d.line([(12, ty + 2), (15, ty + 8)], fill=DARK_PLUM)
            d.line([(20, ty + 2), (17, ty + 8)], fill=DARK_PLUM)
            d.rectangle([14, ty + 7, 18, ty + 11], fill=(20, 22, 24), outline=DARK_PLUM)
            d.point((15, ty + 10), fill=(80, 200, 240))
            d.point((17, ty + 10), fill=(80, 200, 240))
    elif hid == 'barti':
        # Open denim jacket over white tee
        if direction == 0:
            d.polygon([(14, ty), (18, ty), (17, ty + 13), (15, ty + 13)], fill=(245, 245, 245), outline=DARK_PLUM)
    elif hid == 'oziem':
        # Pockets & belt holster
        d.rectangle([11, ty + 5, 14, ty + 8], fill=cfg['top_hi'], outline=DARK_PLUM)
        d.rectangle([18, ty + 5, 21, ty + 8], fill=cfg['top_hi'], outline=DARK_PLUM)
        d.rectangle([21, ty + 10, 24, ty + 14], fill=(70, 48, 25), outline=DARK_PLUM) # holster
    elif hid == 'luki':
        # Orange rescue life vest with reflective silver tape
        d.polygon([(9, ty), (23, ty), (22, ty + 13), (10, ty + 13)], fill=(245, 110, 25), outline=DARK_PLUM)
        d.line([(10, ty + 7), (22, ty + 7)], fill=(245, 248, 255), width=2) # silver tape

    # 3. HEAD & FACE
    hy = 10 + bob
    # Head base
    d.polygon([(10, hy - 4), (22, hy - 4), (21, hy + 8), (11, hy + 8)], fill=cfg['skin'], outline=DARK_PLUM)
    
    if direction == 0: # Down (facing forward)
        # Eyes
        d.point((13, hy + 2), fill=DARK_PLUM)
        d.point((19, hy + 2), fill=DARK_PLUM)
        # Hair / Beard
        if hid == 'danny':
            # Crew cut
            d.rectangle([10, hy - 6, 22, hy - 2], fill=cfg['hair'], outline=DARK_PLUM)
            # Full beard
            d.polygon([(11, hy + 4), (21, hy + 4), (20, hy + 9), (12, hy + 9)], fill=cfg['beard'], outline=DARK_PLUM)
        elif hid == 'alior':
            # Bald sheen
            d.ellipse([10, hy - 7, 22, hy - 1], fill=cfg['skin_hi'])
            # Green gaming headset
            d.arc([8, hy - 6, 24, hy + 4], 180, 360, fill=cfg['accent'], width=2)
            d.rectangle([8, hy, 10, hy + 4], fill=cfg['accent'], outline=DARK_PLUM)
            d.rectangle([22, hy, 24, hy + 4], fill=cfg['accent'], outline=DARK_PLUM)
            d.line([(10, hy + 3), (13, hy + 5)], fill=cfg['accent']) # boom mic
            # Beard
            d.polygon([(12, hy + 4), (20, hy + 4), (19, hy + 9), (13, hy + 9)], fill=cfg['beard'], outline=DARK_PLUM)
        elif hid == 'lisu':
            # Olive ninja cowl
            d.polygon([(9, hy - 6), (23, hy - 6), (23, hy + 2), (9, hy + 2)], fill=cfg['top'], outline=DARK_PLUM)
            # Black face mask
            d.rectangle([11, hy + 3, 21, hy + 8], fill=(25, 28, 30), outline=DARK_PLUM)
        elif hid == 'barti':
            # Brown quiff pompadour
            d.polygon([(9, hy - 8), (16, hy - 10), (23, hy - 6), (23, hy - 2), (9, hy - 2)], fill=cfg['hair'], outline=DARK_PLUM)
            d.line([(11, hy - 6), (19, hy - 4)], fill=cfg['hair_hi'])
            # Headset around neck
            d.arc([9, hy + 6, 23, hy + 12], 0, 180, fill=(40, 45, 55), width=2)
        elif hid == 'oziem':
            # Tousled hair & full beard
            d.polygon([(9, hy - 6), (23, hy - 7), (23, hy - 1), (9, hy - 1)], fill=cfg['hair'], outline=DARK_PLUM)
            d.polygon([(11, hy + 3), (21, hy + 3), (20, hy + 10), (12, hy + 10)], fill=cfg['beard'], outline=DARK_PLUM)
        elif hid == 'luki':
            # Wavy hair & diving goggles on forehead
            d.polygon([(9, hy - 6), (23, hy - 6), (23, hy - 2), (9, hy - 2)], fill=cfg['hair'], outline=DARK_PLUM)
            # Aqua goggles on forehead
            d.rectangle([11, hy - 3, 21, hy], fill=(60, 220, 240), outline=DARK_PLUM)
    elif direction == 1: # Left
        d.point((11, hy + 2), fill=DARK_PLUM)
        if hid == 'alior':
            d.rectangle([13, hy, 16, hy + 4], fill=cfg['accent'], outline=DARK_PLUM)
            d.line([(13, hy + 3), (11, hy + 5)], fill=cfg['accent'])
        elif hid == 'lisu':
            d.rectangle([9, hy + 3, 16, hy + 8], fill=(25, 28, 30), outline=DARK_PLUM)
    elif direction == 2: # Right
        d.point((21, hy + 2), fill=DARK_PLUM)
        if hid == 'alior':
            d.rectangle([16, hy, 19, hy + 4], fill=cfg['accent'], outline=DARK_PLUM)
        elif hid == 'lisu':
            d.rectangle([16, hy + 3, 23, hy + 8], fill=(25, 28, 30), outline=DARK_PLUM)
    else: # Up (facing back)
        # Hair covers head
        d.polygon([(9, hy - 6), (23, hy - 6), (23, hy + 5), (9, hy + 5)], fill=cfg['hair'], outline=DARK_PLUM)
        if hid == 'alior':
            d.ellipse([10, hy - 7, 22, hy + 4], fill=cfg['skin'], outline=DARK_PLUM)
            d.arc([8, hy - 6, 24, hy + 4], 180, 360, fill=cfg['accent'], width=2)
        elif hid == 'luki':
            # Goggle strap behind head
            d.line([(10, hy), (22, hy)], fill=(20, 20, 20), width=2)

    return im

def build_walk_sheet(hid):
    """4 directions x 4 walk frames = 128x192 px."""
    sheet = Image.new("RGBA", (128, 192), (0, 0, 0, 0))
    for direction in range(4): # 0=down, 1=left, 2=right, 3=up
        for f in range(4):
            frame = render_walk_frame(hid, direction, f)
            sheet.paste(frame, (f * 32, direction * 48))
    sheet.save(os.path.join(OUT_DIR, f"{hid}_walk.png"), "PNG")
    print(f"Generated {hid}_walk.png: {sheet.size}")

# ============================================================================
# BATTLE SPRITE ENGINE (64x80 frame, 8 states = 512x80 px)
# ============================================================================
def render_battle_frame(hid, state_idx):
    """state_idx: 0=idle0, 1=idle1, 2=windup, 3=attack, 4=skill, 5=hurt, 6=ko, 7=victory."""
    cfg = HERO_CONFIGS[hid]
    im = Image.new("RGBA", (64, 80), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    cx = 32
    by = 48 # base torso y

    # Pose dynamics based on state
    bob = 0
    arm_l_state = 'idle'
    arm_r_state = 'idle'
    head_shift_x = 0
    head_shift_y = 0

    if state_idx == 1: # idle breathing
        bob = -1
    elif state_idx == 2: # windup
        bob = 2
        arm_l_state = 'back'
        arm_r_state = 'ready'
        head_shift_x = -2
    elif state_idx == 3: # attack
        bob = 0
        arm_l_state = 'strike'
        arm_r_state = 'swing'
        head_shift_x = 4
    elif state_idx == 4: # skill
        bob = -2
        arm_l_state = 'raise'
        arm_r_state = 'raise'
    elif state_idx == 5: # hurt
        bob = -2
        head_shift_x = -4
        head_shift_y = -2
        arm_l_state = 'recoil'
        arm_r_state = 'recoil'
    elif state_idx == 6: # ko
        # Lying flat on ground
        d.ellipse([14, 68, 50, 78], fill=(10, 12, 18, 120)) # shadow
        # Body horizontal
        d.polygon([(16, 66), (46, 66), (44, 74), (18, 74)], fill=cfg['top'], outline=DARK_PLUM)
        d.polygon([(36, 68), (56, 68), (54, 76), (36, 76)], fill=cfg['bottom'], outline=DARK_PLUM)
        # Head
        d.ellipse([10, 64, 22, 74], fill=cfg['skin'], outline=DARK_PLUM)
        d.polygon([(10, 64), (18, 62), (20, 70), (10, 70)], fill=cfg['hair'], outline=DARK_PLUM)
        d.line([(12, 69), (16, 69)], fill=DARK_PLUM) # closed eye
        return im
    elif state_idx == 7: # victory
        bob = -2
        arm_l_state = 'victory'
        arm_r_state = 'victory'

    # Shadow under character
    d.ellipse([cx - 16, 70, cx + 16, 78], fill=(10, 12, 18, 130))

    # 1. LEGS & COMBAT STANCE
    leg_y = by + 18 + bob
    # Left combat leg (forward)
    d.polygon([(cx - 12, by + 12), (cx - 14, leg_y), (cx - 6, leg_y), (cx - 4, by + 12)], fill=cfg['bottom'], outline=DARK_PLUM)
    d.polygon([(cx - 16, leg_y), (cx - 5, leg_y), (cx - 5, leg_y + 8), (cx - 16, leg_y + 8)], fill=cfg['shoes'], outline=DARK_PLUM)
    d.line([(cx - 16, leg_y + 8), (cx - 5, leg_y + 8)], fill=cfg['shoe_sole'])

    # Right combat leg (back braced)
    d.polygon([(cx + 4, by + 12), (cx + 10, leg_y - 2), (cx + 18, leg_y - 2), (cx + 12, by + 12)], fill=cfg['bottom_sh'], outline=DARK_PLUM)
    d.polygon([(cx + 8, leg_y - 2), (cx + 20, leg_y - 2), (cx + 20, leg_y + 6), (cx + 8, leg_y + 6)], fill=cfg['shoes'], outline=DARK_PLUM)
    d.line([(cx + 8, leg_y + 6), (cx + 20, leg_y + 6)], fill=cfg['shoe_sole'])

    # 2. TORSO & COMBAT STANCE
    ty = by + bob
    d.polygon([(cx - 12, ty - 12), (cx + 12, ty - 12), (cx + 10, ty + 14), (cx - 10, ty + 14)], fill=cfg['top'], outline=DARK_PLUM)
    # Shading
    d.line([(cx - 11, ty - 11), (cx - 9, ty + 13)], fill=cfg['top_hi'], width=2)
    d.line([(cx + 11, ty - 11), (cx + 9, ty + 13)], fill=cfg['top_sh'], width=2)

    # Hero unique chest details
    if hid == 'danny':
        # Muscular chest volume
        d.line([(cx - 8, ty - 2), (cx + 8, ty - 2)], fill=cfg['top_sh'])
    elif hid == 'alior':
        # 1-UP logo
        d.rectangle([cx - 4, ty - 4, cx + 4, ty + 4], fill=cfg['accent'], outline=DARK_PLUM)
    elif hid == 'barti':
        # Denim jacket open over tee
        d.polygon([(cx - 4, ty - 12), (cx + 4, ty - 12), (cx + 2, ty + 12), (cx - 2, ty + 12)], fill=(245, 245, 245), outline=DARK_PLUM)
    elif hid == 'luki':
        # High vis orange vest
        d.line([(cx - 10, ty), (cx + 10, ty)], fill=(245, 248, 255), width=3)

    # 3. ARMS & WEAPON / SIGNATURE ACCESSORIES
    if arm_l_state == 'strike':
        # Lunging strike arm
        d.line([(cx - 8, ty - 4), (cx - 26, ty - 2)], fill=cfg['top_hi'], width=5)
        d.ellipse([cx - 30, ty - 6, cx - 22, ty + 2], fill=cfg['skin'], outline=DARK_PLUM)
        # Attack slash FX
        d.arc([cx - 36, ty - 18, cx - 18, ty + 14], 120, 240, fill=(255, 255, 200, 240), width=3)
    elif arm_l_state == 'raise' or arm_l_state == 'victory':
        # Triumphant raised arm holding signature item
        d.line([(cx - 8, ty - 4), (cx - 18, ty - 24)], fill=cfg['top_hi'], width=5)
        d.ellipse([cx - 22, ty - 28, cx - 14, ty - 20], fill=cfg['skin'], outline=DARK_PLUM)
        # Render signature item held aloft!
        ix, iy = cx - 18, ty - 32
        if hid == 'danny':
            # Shaker bottle
            d.rectangle([ix - 3, iy - 6, ix + 3, iy + 4], fill=cfg['accent'], outline=DARK_PLUM)
        elif hid == 'alior':
            # Gamepad
            d.rounded_rectangle([ix - 6, iy - 4, ix + 6, iy + 4], radius=3, fill=(30, 30, 35), outline=cfg['accent'])
        elif hid == 'lisu':
            # Binoculars
            d.rectangle([ix - 4, iy - 4, ix + 4, iy + 4], fill=(25, 28, 30), outline=DARK_PLUM)
        elif hid == 'barti':
            # Vinyl Record
            d.ellipse([ix - 8, iy - 8, ix + 8, iy + 8], fill=(20, 20, 22), outline=DARK_PLUM)
            d.ellipse([ix - 3, iy - 3, ix + 3, iy + 3], fill=(225, 40, 40))
        elif hid == 'oziem':
            # Multi-tool blade
            d.polygon([(ix - 2, iy + 4), (ix + 2, iy + 4), (ix, iy - 10)], fill=(220, 225, 235), outline=DARK_PLUM)
        elif hid == 'luki':
            # Lifebuoy
            d.ellipse([ix - 9, iy - 9, ix + 9, iy + 9], outline=(225, 35, 40), width=4)
        
        # Skill energy particles if state 4
        if state_idx == 4:
            d.arc([cx - 28, ty - 38, cx - 8, ty - 18], 0, 360, fill=(255, 230, 80, 200), width=2)
    else:
        # Idle / ready combat guard arms
        d.polygon([(cx - 8, ty - 6), (cx - 18, ty + 2), (cx - 14, ty + 8), (cx - 6, ty)], fill=cfg['top_hi'], outline=DARK_PLUM)
        d.ellipse([cx - 20, ty, cx - 12, ty + 8], fill=cfg['skin'], outline=DARK_PLUM)
        # Held item in ready stance
        if hid == 'danny':
            d.rectangle([cx - 22, ty - 2, cx - 16, ty + 8], fill=cfg['accent'], outline=DARK_PLUM)
        elif hid == 'alior':
            d.rectangle([cx - 22, ty - 1, cx - 14, ty + 6], fill=(30, 30, 35), outline=cfg['accent'])
        elif hid == 'lisu':
            d.rectangle([cx - 20, ty - 1, cx - 14, ty + 7], fill=(20, 22, 24), outline=DARK_PLUM)
        elif hid == 'barti':
            d.ellipse([cx - 22, ty - 2, cx - 12, ty + 8], fill=(20, 20, 22), outline=DARK_PLUM)
        elif hid == 'oziem':
            d.rectangle([cx - 20, ty, cx - 14, ty + 8], fill=(200, 205, 215), outline=DARK_PLUM)
        elif hid == 'luki':
            d.ellipse([cx - 24, ty - 2, cx - 10, ty + 12], outline=(225, 35, 40), width=3)

    # 4. HEAD & EXPRESSION
    hx = cx + head_shift_x
    hy = by - 22 + bob + head_shift_y
    # Head volume
    d.polygon([(hx - 10, hy - 8), (hx + 8, hy - 8), (hx + 6, hy + 10), (hx - 8, hy + 10)], fill=cfg['skin'], outline=DARK_PLUM)
    # Facial expression
    eye_x = hx - 4
    eye_y = hy + 1
    if state_idx == 5: # hurt
        d.line([(eye_x - 3, eye_y - 2), (eye_x + 1, eye_y + 2)], fill=DARK_PLUM, width=2)
        d.line([(eye_x - 3, eye_y + 2), (eye_x + 1, eye_y - 2)], fill=DARK_PLUM, width=2)
    elif state_idx == 7: # victory smile
        d.arc([eye_x - 2, eye_y - 2, eye_x + 2, eye_y + 2], 180, 360, fill=DARK_PLUM, width=2)
        d.arc([hx - 4, hy + 4, hx + 2, hy + 8], 0, 180, fill=DARK_PLUM, width=2)
    else: # combat focus
        d.line([(eye_x - 2, eye_y), (eye_x + 2, eye_y)], fill=DARK_PLUM, width=2)
        d.line([(eye_x - 3, eye_y - 3), (eye_x + 3, eye_y - 1)], fill=cfg['hair_sh'], width=2) # brow

    # Specific headgear & hair
    if hid == 'danny':
        d.rectangle([hx - 10, hy - 11, hx + 8, hy - 6], fill=cfg['hair'], outline=DARK_PLUM)
        d.polygon([(hx - 8, hy + 4), (hx + 6, hy + 4), (hx + 5, hy + 11), (hx - 7, hy + 11)], fill=cfg['beard'], outline=DARK_PLUM)
    elif hid == 'alior':
        d.ellipse([hx - 9, hy - 12, hx + 7, hy - 5], fill=cfg['skin_hi']) # bald sheen
        d.arc([hx - 10, hy - 9, hx + 8, hy + 4], 160, 360, fill=cfg['accent'], width=3) # headset
        d.rectangle([hx - 11, hy, hx - 8, hy + 5], fill=cfg['accent'], outline=DARK_PLUM)
        d.line([(hx - 8, hy + 3), (hx - 4, hy + 5)], fill=cfg['accent'], width=2) # mic
        d.polygon([(hx - 7, hy + 5), (hx + 5, hy + 5), (hx + 4, hy + 11), (hx - 6, hy + 11)], fill=cfg['beard'], outline=DARK_PLUM)
    elif hid == 'lisu':
        d.polygon([(hx - 11, hy - 11), (hx + 9, hy - 11), (hx + 8, hy), (hx - 10, hy)], fill=cfg['top'], outline=DARK_PLUM)
        d.rectangle([hx - 8, hy + 3, hx + 6, hy + 10], fill=(25, 28, 30), outline=DARK_PLUM) # mask
    elif hid == 'barti':
        d.polygon([(hx - 10, hy - 14), (hx - 2, hy - 17), (hx + 9, hy - 9), (hx + 8, hy - 4), (hx - 10, hy - 4)], fill=cfg['hair'], outline=DARK_PLUM)
        d.line([(hx - 7, hy - 11), (hx + 3, hy - 8)], fill=cfg['hair_hi'], width=2)
    elif hid == 'oziem':
        d.polygon([(hx - 11, hy - 11), (hx + 9, hy - 12), (hx + 8, hy - 4), (hx - 10, hy - 4)], fill=cfg['hair'], outline=DARK_PLUM)
        d.polygon([(hx - 8, hy + 3), (hx + 6, hy + 3), (hx + 5, hy + 12), (hx - 7, hy + 12)], fill=cfg['beard'], outline=DARK_PLUM)
    elif hid == 'luki':
        d.polygon([(hx - 10, hy - 11), (hx + 8, hy - 11), (hx + 8, hy - 5), (hx - 10, hy - 5)], fill=cfg['hair'], outline=DARK_PLUM)
        d.rectangle([hx - 8, hy - 6, hx + 6, hy - 2], fill=(60, 220, 240), outline=DARK_PLUM) # goggles

    return im

def build_battle_sheet(hid):
    """8 animation states: idle0, idle1, windup, attack, skill, hurt, ko, victory = 512x80 px."""
    sheet = Image.new("RGBA", (512, 80), (0, 0, 0, 0))
    for s in range(8):
        frame = render_battle_frame(hid, s)
        sheet.paste(frame, (s * 64, 0))
    sheet.save(os.path.join(OUT_DIR, f"{hid}_battle.png"), "PNG")
    print(f"Generated {hid}_battle.png: {sheet.size}")

# ============================================================================
# CAMPFIRE SIT SPRITE ENGINE (32x32 frame, 2 frames = 64x32 px)
# ============================================================================
def render_sit_frame(hid, f_idx):
    """2 idle breathing frames around campfire."""
    cfg = HERO_CONFIGS[hid]
    im = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    bob = -1 if f_idx == 1 else 0
    cx = 16

    # Log / Ground contact shadow
    d.ellipse([6, 26, 26, 31], fill=(10, 12, 18, 140))

    # Folded / Crossed legs on log
    d.ellipse([7, 22, 25, 29], fill=cfg['bottom'], outline=DARK_PLUM)
    d.ellipse([9, 23, 14, 28], fill=cfg['shoes'], outline=DARK_PLUM)
    d.ellipse([18, 23, 23, 28], fill=cfg['shoes'], outline=DARK_PLUM)

    # Torso
    ty = 13 + bob
    d.polygon([(10, ty), (22, ty), (21, ty + 10), (11, ty + 10)], fill=cfg['top'], outline=DARK_PLUM)
    # Warm campfire orange glow highlight on front of torso
    d.line([(11, ty + 2), (11, ty + 9)], fill=(245, 160, 50, 180))

    # Head
    hy = 7 + bob
    d.polygon([(11, hy - 4), (21, hy - 4), (20, hy + 5), (12, hy + 5)], fill=cfg['skin'], outline=DARK_PLUM)
    # Eyes looking down at campfire
    d.point((14, hy + 2), fill=DARK_PLUM)
    d.point((18, hy + 2), fill=DARK_PLUM)
    # Warm glow on face
    d.point((13, hy + 3), fill=(245, 170, 60))
    d.point((19, hy + 3), fill=(245, 170, 60))

    # Hero unique head details
    if hid == 'danny':
        d.rectangle([11, hy - 6, 21, hy - 3], fill=cfg['hair'], outline=DARK_PLUM)
        d.polygon([(12, hy + 3), (20, hy + 3), (19, hy + 6), (13, hy + 6)], fill=cfg['beard'], outline=DARK_PLUM)
    elif hid == 'alior':
        d.ellipse([11, hy - 6, 21, hy - 2], fill=cfg['skin_hi'])
        d.arc([9, hy - 5, 23, hy + 2], 180, 360, fill=cfg['accent'], width=2)
        d.polygon([(13, hy + 3), (19, hy + 3), (18, hy + 6), (14, hy + 6)], fill=cfg['beard'], outline=DARK_PLUM)
    elif hid == 'lisu':
        d.polygon([(10, hy - 6), (22, hy - 6), (22, hy), (10, hy)], fill=cfg['top'], outline=DARK_PLUM)
        d.rectangle([12, hy + 2, 20, hy + 6], fill=(25, 28, 30), outline=DARK_PLUM)
    elif hid == 'barti':
        d.polygon([(10, hy - 8), (16, hy - 9), (22, hy - 5), (22, hy - 2), (10, hy - 2)], fill=cfg['hair'], outline=DARK_PLUM)
    elif hid == 'oziem':
        d.polygon([(10, hy - 6), (22, hy - 6), (22, hy - 2), (10, hy - 2)], fill=cfg['hair'], outline=DARK_PLUM)
        d.polygon([(12, hy + 2), (20, hy + 2), (19, hy + 7), (13, hy + 7)], fill=cfg['beard'], outline=DARK_PLUM)
    elif hid == 'luki':
        d.polygon([(10, hy - 6), (22, hy - 6), (22, hy - 2), (10, hy - 2)], fill=cfg['hair'], outline=DARK_PLUM)
        d.rectangle([12, hy - 3, 20, hy - 1], fill=(60, 220, 240), outline=DARK_PLUM)

    return im

def build_sit_sheet(hid):
    """2 idle breathing frames = 64x32 px."""
    sheet = Image.new("RGBA", (64, 32), (0, 0, 0, 0))
    for f in range(2):
        frame = render_sit_frame(hid, f)
        sheet.paste(frame, (f * 32, 0))
    sheet.save(os.path.join(OUT_DIR, f"{hid}_sit.png"), "PNG")
    print(f"Generated {hid}_sit.png: {sheet.size}")

def build_all():
    for hid in ['danny', 'alior', 'lisu', 'barti', 'oziem', 'luki']:
        build_walk_sheet(hid)
        build_battle_sheet(hid)
        build_sit_sheet(hid)
    print("All 6 heroes generated successfully across walk, battle, and sit sheets!")

if __name__ == "__main__":
    build_all()
