#!/usr/bin/env python3
"""generate_hd_enemies.py - Generate high-detail combat sprites for all 11 enemies.

Dimensions:
- Regular enemies (96x96 per frame, 2 frames = 192x96):
  bolKregoslupa, slacki, autoTuneHipster, drogiePiwo, straznik, rwaKulszowa
- Bosses (128x128 per frame, 2 frames = 256x128):
  sasiadSzkodnik, kark, panJanusz, kredyt, audyt
"""
import os
import math
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "public", "assets", "enemies")
os.makedirs(OUT, exist_ok=True)

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
    'red': (192, 57, 43, 255),
    'red_hi': (235, 87, 87, 255),
    'crimson': (130, 20, 25, 255),
    'green': (95, 200, 90, 255),
    'green_hi': (130, 230, 120, 255),
    'neon_yellow': (225, 245, 30, 255),
    'beer_amber': (215, 140, 30, 255),
    'beer_gold': (245, 190, 50, 255),
    'foam_white': (245, 245, 235, 255),
    'stone_dk': (50, 55, 65, 255),
    'stone_mid': (90, 95, 105, 255),
    'stone_hi': (140, 145, 155, 255),
    'purple': (140, 50, 170, 255),
    'purple_hi': (200, 90, 240, 255),
    'skin_mid': (235, 185, 145, 255),
    'skin_shadow': (195, 140, 100, 255),
    'robe_blue': (55, 75, 105, 255),
    'robe_hi': (80, 110, 150, 255),
    'warden_green': (40, 65, 35, 255),
    'gold': (215, 175, 45, 255),
}

BOSSES = {'sasiadSzkodnik': 128, 'kark': 128, 'panJanusz': 128, 'kredyt': 128, 'audyt': 128}

def draw_bol_kregoslupa(d: ImageDraw.ImageDraw, ox: int, frame: int):
    # 96x96: Glowing anatomical spinal column with red sciatic lightning
    cx = ox + 48
    cy = 48
    ink = PAL['ink']
    
    # Shadow
    d.ellipse([cx - 20, 84, cx + 20, 92], fill=(0, 0, 0, 80))
    
    # Cervical down to lumbar vertebrae (8 segments)
    for i in range(8):
        vy = 16 + i * 8 + (math.sin(i * 0.8 + frame) * 2)
        vw = 18 + int(i * 1.8) # wider towards lumbar
        # Vertebra body
        d.rectangle([cx - vw//2, vy, cx + vw//2, vy + 5], fill=PAL['white'], outline=ink)
        # Intervertebral disc (inflamed red at lower lumbar)
        disc_color = PAL['red_hi'] if i >= 5 else PAL['cyan']
        d.rectangle([cx - vw//3, vy + 5, cx + vw//3, vy + 7], fill=disc_color)
        # Transverse processes (side wings)
        d.line([cx - vw//2, vy + 2, cx - vw//2 - 6, vy + (0 if frame == 0 else -2)], fill=PAL['silver'], width=2)
        d.line([cx + vw//2, vy + 2, cx + vw//2 + 6, vy + (0 if frame == 0 else -2)], fill=PAL['silver'], width=2)

    # Sciatic nerve pain lightning
    spark_c = PAL['red_hi'] if frame == 0 else PAL['yellow_hi']
    d.line([cx - 10, 60, cx - 24, 75, cx - 18, 85], fill=spark_c, width=2)
    d.line([cx + 10, 60, cx + 28, 70, cx + 20, 88], fill=spark_c, width=2)
    if frame == 1:
        d.ellipse([cx - 30, 70, cx - 22, 78], fill=PAL['yellow_hi'])
        d.ellipse([cx + 22, 75, cx + 30, 83], fill=PAL['yellow_hi'])

def draw_slacki(d: ImageDraw.ImageDraw, ox: int, frame: int):
    # 96x96: Swarming cluster of glossy chat notification bubbles
    cx = ox + 48
    cy = 48
    ink = PAL['ink']
    
    # Shadow
    d.ellipse([cx - 24, 82, cx + 24, 90], fill=(0, 0, 0, 70))
    
    # Main big Slack bubble
    bob = 2 if frame == 1 else 0
    bx, by = cx - 4, cy - 6 + bob
    d.rounded_rectangle([bx - 26, by - 22, bx + 26, by + 18], radius=8, fill=PAL['panel'], outline=PAL['cyan'])
    # Highlight
    d.line([bx - 22, by - 18, bx + 22, by - 18], fill=PAL['cyan_hi'])
    
    # Angry digital eyes
    eye_c = PAL['red_hi'] if frame == 1 else PAL['yellow']
    d.rectangle([bx - 14, by - 8, bx - 6, by - 4], fill=eye_c)
    d.rectangle([bx + 6, by - 8, bx + 14, by - 4], fill=eye_c)
    # Digital mouth
    d.line([bx - 10, by + 6, bx + 10, by + 6], fill=PAL['red_hi'], width=2)
    
    # [99+] badge
    d.rounded_rectangle([bx + 12, by - 28, bx + 36, by - 12], radius=4, fill=PAL['red'], outline=PAL['white'])
    d.line([bx + 16, by - 20, bx + 32, by - 20], fill=PAL['white'], width=2) # 99+
    
    # Sub-bubble 1: @channel
    s1x, s1y = cx - 22, cy + 14 - bob
    d.rounded_rectangle([s1x - 14, s1y - 10, s1x + 14, s1y + 10], radius=5, fill=PAL['navy'], outline=PAL['yellow'])
    d.point([s1x - 4, s1y], fill=PAL['yellow_hi'])
    d.point([s1x + 4, s1y], fill=PAL['yellow_hi'])
    
    # Sub-bubble 2: @here
    s2x, s2y = cx + 24, cy + 12 + bob
    d.rounded_rectangle([s2x - 12, s2y - 9, s2x + 12, s2y + 9], radius=5, fill=PAL['steel'], outline=PAL['red_hi'])

def draw_sasiad_szkodnik(d: ImageDraw.ImageDraw, ox: int, frame: int):
    # 128x128 Boss: Grumpy balding neighbor in flannel bathrobe and slippers with broom
    cx = ox + 64
    by = 114
    ink = PAL['ink']
    skin = PAL['skin_mid']
    
    # Shadow
    d.ellipse([cx - 28, by - 6, cx + 28, by + 6], fill=(0, 0, 0, 90))
    
    # Slippers
    d.rectangle([cx - 16, by - 8, cx - 4, by], fill=PAL['grey'], outline=ink)
    d.rectangle([cx + 4, by - 8, cx + 16, by], fill=PAL['grey'], outline=ink)
    
    # Bathrobe body (wide flannel checkered)
    ty = by - 64
    d.rectangle([cx - 24, ty, cx + 24, by - 6], fill=PAL['robe_blue'], outline=ink)
    # Checkered pattern
    for py in range(ty + 6, by - 10, 10):
        d.line([cx - 22, py, cx + 22, py], fill=PAL['robe_hi'], width=2)
    for px in range(cx - 18, cx + 20, 10):
        d.line([px, ty + 2, px, by - 8], fill=PAL['robe_hi'], width=2)
    # Bathrobe belt sash
    d.rectangle([cx - 25, ty + 24, cx + 25, ty + 28], fill=PAL['yellow'], outline=ink)
    
    # Head & Balding hair
    hy = ty - 26
    d.rectangle([cx - 14, hy, cx + 14, hy + 26], fill=skin, outline=ink)
    # Balding side hair puffs
    d.rectangle([cx - 17, hy + 8, cx - 14, hy + 20], fill=PAL['grey'], outline=ink)
    d.rectangle([cx + 14, hy + 8, cx + 17, hy + 20], fill=PAL['grey'], outline=ink)
    # Wrinkles & furrowed brow
    d.line([cx - 8, hy + 6, cx + 8, hy + 6], fill=PAL['skin_shadow'], width=1)
    d.line([cx - 8, hy + 9, cx + 8, hy + 9], fill=PAL['skin_shadow'], width=1)
    # Angled angry eyes
    d.line([cx - 9, hy + 12, cx - 4, hy + 14], fill=ink, width=2)
    d.line([cx + 9, hy + 12, cx + 4, hy + 14], fill=ink, width=2)
    # Big grumpy nose & mouth
    d.rectangle([cx - 3, hy + 14, cx + 3, hy + 18], fill=PAL['skin_shadow'])
    d.line([cx - 7, hy + 22, cx + 7, hy + 20], fill=ink, width=2) # sneer
    
    # Broom in hand (right side)
    broom_x = cx + 32
    broom_y = by - 80 if frame == 1 else by - 70 # raised broom shake
    d.line([broom_x - 12, broom_y + 60, broom_x + 8, broom_y], fill=PAL['orange'], width=4) # pole
    # Bristles
    d.polygon([(broom_x + 6, broom_y - 2), (broom_x + 22, broom_y - 12), (broom_x + 18, broom_y + 12)], fill=PAL['yellow'], outline=ink)

def draw_autotune_hipster(d: ImageDraw.ImageDraw, ox: int, frame: int):
    # 96x96: Flannel hipster with beanie, tortoiseshell glasses, glowing audio visualizer laptop
    cx = ox + 48
    by = 86
    ink = PAL['ink']
    skin = PAL['skin_mid']
    
    d.ellipse([cx - 20, by - 4, cx + 20, by + 4], fill=(0, 0, 0, 80))
    # Legs (skinny jeans)
    d.rectangle([cx - 10, by - 24, cx - 3, by], fill=PAL['panel'], outline=ink)
    d.rectangle([cx + 3, by - 24, cx + 10, by], fill=PAL['panel'], outline=ink)
    
    # Flannel torso
    ty = by - 46
    d.rectangle([cx - 16, ty, cx + 16, by - 22], fill=PAL['red'], outline=ink)
    # Flannel grid
    d.line([cx - 14, ty + 8, cx + 14, ty + 8], fill=PAL['navy'], width=2)
    d.line([cx, ty, cx, by - 24], fill=PAL['navy'], width=2)
    
    # Head & Hipster Beanie
    hy = ty - 20
    d.rectangle([cx - 10, hy, cx + 10, hy + 20], fill=skin, outline=ink)
    # Beanie (mustard yellow)
    d.rectangle([cx - 11, hy - 6, cx + 11, hy + 4], fill=PAL['yellow'], outline=ink)
    d.rectangle([cx - 8, hy - 9, cx + 8, hy - 5], fill=PAL['yellow_hi'])
    # Well-groomed beard
    d.rectangle([cx - 9, hy + 12, cx + 9, hy + 20], fill=PAL['orange'], outline=ink)
    # Round Tortoiseshell Glasses
    d.rectangle([cx - 8, hy + 6, cx - 2, hy + 11], outline=PAL['orange'], fill=PAL['cyan'])
    d.rectangle([cx + 2, hy + 6, cx + 8, hy + 11], outline=PAL['orange'], fill=PAL['cyan'])
    d.line([cx - 2, hy + 8, cx + 2, hy + 8], fill=PAL['orange'])
    
    # Laptop with waveform visualizer
    lx = cx - 18
    ly = ty + 12
    d.rectangle([lx, ly, lx + 20, ly + 14], fill=PAL['silver'], outline=ink)
    # Screen visualizer
    d.rectangle([lx + 2, ly + 2, lx + 18, ly + 12], fill=PAL['ink'])
    wave_c = PAL['cyan_hi'] if frame == 0 else PAL['green_hi']
    for wx in range(lx + 4, lx + 17, 3):
        h = 3 + ((wx * 7 + frame * 5) % 6)
        d.line([wx, ly + 10, wx, ly + 10 - h], fill=wave_c, width=2)

def draw_drogie_piwo(d: ImageDraw.ImageDraw, ox: int, frame: int):
    # 96x96: Artisanal craft beer bottle monster with dripping golden foam & 48 zł tag
    cx = ox + 48
    by = 88
    ink = PAL['ink']
    
    d.ellipse([cx - 22, by - 4, cx + 22, by + 6], fill=(0, 0, 0, 80))
    
    # Amber glass bottle body
    bw = 30
    bh = 46
    bx = cx - bw // 2
    by_top = by - bh
    d.rounded_rectangle([bx, by_top, bx + bw, by], radius=6, fill=PAL['beer_amber'], outline=ink)
    d.rectangle([bx + 4, by_top + 2, bx + 8, by - 4], fill=PAL['beer_gold']) # highlight sheen
    
    # Bottle neck
    nw = 14
    nh = 20
    nx = cx - nw // 2
    ny = by_top - nh
    d.rectangle([nx, ny, nx + nw, by_top + 2], fill=PAL['beer_amber'], outline=ink)
    
    # Dripping golden foam head
    d.ellipse([nx - 4, ny - 10, nx + nw + 4, ny + 4], fill=PAL['foam_white'], outline=ink)
    foam_drip = 6 if frame == 1 else 3
    d.rectangle([nx + 2, ny + 4, nx + 6, ny + 4 + foam_drip], fill=PAL['foam_white'])
    
    # Ornate Craft Label ("48 ZŁ")
    label_y = by_top + 14
    d.rectangle([bx + 2, label_y, bx + bw - 2, label_y + 20], fill=PAL['panel'], outline=PAL['gold'])
    # Hop leaf icon on label
    d.polygon([(cx, label_y + 3), (cx - 4, label_y + 8), (cx + 4, label_y + 8)], fill=PAL['green'])
    # "48 ZŁ"
    d.line([cx - 6, label_y + 14, cx + 6, label_y + 14], fill=PAL['yellow_hi'], width=2)
    
    # Glowing eyes on bottle glass
    eye_c = PAL['red_hi'] if frame == 1 else PAL['yellow_hi']
    d.point([cx - 6, by_top + 8], fill=eye_c)
    d.point([cx + 6, by_top + 8], fill=eye_c)

def draw_kark(d: ImageDraw.ImageDraw, ox: int, frame: int):
    # 128x128 Boss: Massive bouncer in tailored black security bomber, gold badge, shades, earpiece
    cx = ox + 64
    by = 118
    ink = PAL['ink']
    skin = PAL['skin_shadow']
    
    d.ellipse([cx - 36, by - 6, cx + 36, by + 6], fill=(0, 0, 0, 90))
    
    # Massive combat boots & black tactical trousers
    d.rectangle([cx - 24, by - 30, cx - 8, by - 4], fill=PAL['navy'], outline=ink)
    d.rectangle([cx + 8, by - 30, cx + 24, by - 4], fill=PAL['navy'], outline=ink)
    d.rectangle([cx - 26, by - 6, cx - 6, by], fill=PAL['ink'])
    d.rectangle([cx + 6, by - 6, cx + 26, by], fill=PAL['ink'])
    
    # Huge wide torso (Security bomber jacket)
    tw = 64
    th = 48
    tx = cx - tw // 2
    ty = by - 74
    d.rectangle([tx, ty, tx + tw, ty + th], fill=PAL['ink'], outline=PAL['steel'])
    # Zipper line
    d.line([cx, ty, cx, ty + th], fill=PAL['silver'], width=2)
    # Gold SECURITY badge
    d.polygon([(tx + 8, ty + 12), (tx + 16, ty + 12), (tx + 12, ty + 20)], fill=PAL['gold'], outline=ink)
    
    # Massive boulder arms / biceps
    arm_w = 16
    d.rectangle([tx - arm_w + 4, ty + 4, tx + 4, ty + th - 6], fill=PAL['ink'], outline=PAL['steel'])
    d.rectangle([tx + tw - 4, ty + 4, tx + tw + arm_w - 4, ty + th - 6], fill=PAL['ink'], outline=PAL['steel'])
    # Huge fists
    d.rectangle([tx - arm_w + 2, ty + th - 8, tx + 4, ty + th + 6], fill=skin, outline=ink)
    d.rectangle([tx + tw - 4, ty + th - 8, tx + tw + arm_w - 2, ty + th + 6], fill=skin, outline=ink)
    
    # Thick neck & Head
    hy = ty - 26
    d.rectangle([cx - 16, hy, cx + 16, hy + 26], fill=skin, outline=ink)
    # Shaved head / fade
    d.rectangle([cx - 16, hy, cx + 16, hy + 4], fill=PAL['void'])
    # Sunglasses with white shine reflection
    d.rectangle([cx - 14, hy + 8, cx - 2, hy + 14], fill=PAL['void'], outline=PAL['gold'])
    d.rectangle([cx + 2, hy + 8, cx + 14, hy + 14], fill=PAL['void'], outline=PAL['gold'])
    d.line([cx - 12, hy + 9, cx - 6, hy + 13], fill=PAL['white']) # reflection
    d.line([cx + 4, hy + 9, cx + 10, hy + 13], fill=PAL['white'])
    # Coiled radio earpiece
    d.line([cx - 16, hy + 12, cx - 20, hy + 20, cx - 18, hy + 26], fill=PAL['silver'], width=1)
    # Stern mouth
    d.line([cx - 8, hy + 20, cx + 8, hy + 20], fill=ink, width=2)

def draw_straznik(d: ImageDraw.ImageDraw, ox: int, frame: int):
    # 96x96: Municipal guard (Straż Miejska) in neon yellow reflective vest & baton
    cx = ox + 48
    by = 88
    ink = PAL['ink']
    skin = PAL['skin_mid']
    
    d.ellipse([cx - 18, by - 4, cx + 18, by + 4], fill=(0, 0, 0, 80))
    d.rectangle([cx - 10, by - 26, cx - 3, by], fill=PAL['navy'], outline=ink)
    d.rectangle([cx + 3, by - 26, cx + 10, by], fill=PAL['navy'], outline=ink)
    
    # Torso: Neon yellow high-vis vest over navy shirt
    ty = by - 50
    d.rectangle([cx - 16, ty, cx + 16, by - 24], fill=PAL['neon_yellow'], outline=ink)
    # Silver reflective stripes
    d.line([cx - 14, ty + 10, cx + 14, ty + 10], fill=PAL['white'], width=3)
    d.line([cx - 14, ty + 18, cx + 14, ty + 18], fill=PAL['white'], width=3)
    
    # Head & Cap
    hy = ty - 20
    d.rectangle([cx - 9, hy, cx + 9, hy + 20], fill=skin, outline=ink)
    # Checkered Municipal Visor Cap
    d.rectangle([cx - 11, hy - 6, cx + 11, hy + 4], fill=PAL['navy'], outline=ink)
    # Checkered band (white/black)
    for bx in range(cx - 10, cx + 10, 4):
        d.point([bx, hy + 2], fill=PAL['yellow'])
    # Cap visor
    d.line([cx - 12, hy + 4, cx + 12, hy + 4], fill=PAL['ink'], width=2)
    # Mustache & angry expression
    d.point([cx - 4, hy + 8], fill=ink)
    d.point([cx + 4, hy + 8], fill=ink)
    d.rectangle([cx - 6, hy + 12, cx + 6, hy + 15], fill=PAL['grey']) # mustache
    
    # Baton in hand
    d.line([cx + 18, ty + 6, cx + 24, ty + 30], fill=PAL['ink'], width=3)

def draw_pan_janusz(d: ImageDraw.ImageDraw, ox: int, frame: int):
    # 128x128 Boss: Polish Forest Warden (Komendant) in ornate uniform with ticket book & megaphone
    cx = ox + 64
    by = 116
    ink = PAL['ink']
    skin = PAL['skin_mid']
    
    d.ellipse([cx - 32, by - 6, cx + 32, by + 6], fill=(0, 0, 0, 90))
    # Tall leather riding boots & dark olive trousers
    d.rectangle([cx - 20, by - 32, cx - 6, by - 8], fill=PAL['warden_green'], outline=ink)
    d.rectangle([cx + 6, by - 32, cx + 20, by - 8], fill=PAL['warden_green'], outline=ink)
    d.rectangle([cx - 22, by - 8, cx - 4, by], fill=PAL['ink'])
    d.rectangle([cx + 4, by - 8, cx + 22, by], fill=PAL['ink'])
    
    # Formal Forest Warden Tunic
    tw = 52
    th = 46
    tx = cx - tw // 2
    ty = by - 76
    d.rectangle([tx, ty, tx + tw, ty + th], fill=PAL['warden_green'], outline=ink)
    # Gold Pine Oakleaf Epaulets on shoulders
    d.rectangle([tx - 2, ty, tx + 10, ty + 6], fill=PAL['gold'], outline=ink)
    d.rectangle([tx + tw - 10, ty, tx + tw + 2, ty + 6], fill=PAL['gold'], outline=ink)
    # Gold button row
    for by_btn in range(ty + 8, ty + th - 6, 8):
        d.circle((cx, by_btn), 2, fill=PAL['gold'])
        
    # Head & Eagle Cap
    hy = ty - 26
    d.rectangle([cx - 14, hy, cx + 14, hy + 26], fill=skin, outline=ink)
    # Peaked Warden Cap with Eagle
    d.rectangle([cx - 16, hy - 10, cx + 16, hy + 2], fill=PAL['warden_green'], outline=ink)
    d.polygon([(cx - 4, hy - 6), (cx + 4, hy - 6), (cx, hy - 1)], fill=PAL['silver']) # Eagle
    d.line([cx - 18, hy + 2, cx + 18, hy + 2], fill=PAL['ink'], width=3) # Visor
    # Janusz mustache (legendary bushy grey/brown)
    d.rectangle([cx - 12, hy + 13, cx + 12, hy + 19], fill=PAL['grey'], outline=ink)
    d.point([cx - 6, hy + 8], fill=ink)
    d.point([cx + 6, hy + 8], fill=ink)
    
    # Left hand: Red-stamped Penalty Ticket Book ("MANDAT 5000 ZŁ")
    bx_t = tx - 14
    by_t = ty + 12
    d.rectangle([bx_t, by_t, bx_t + 20, by_t + 28], fill=PAL['white'], outline=ink)
    d.rectangle([bx_t + 3, by_t + 8, bx_t + 17, by_t + 18], outline=PAL['red'], fill=PAL['red_hi']) # Stamp
    
    # Right hand: Megaphone
    mx = tx + tw - 2
    my = ty + 14
    d.polygon([(mx, my + 6), (mx + 22, my - 6), (mx + 22, my + 18)], fill=PAL['white'], outline=ink)

def draw_kredyt(d: ImageDraw.ImageDraw, ox: int, frame: int):
    # 128x128 Boss: Monolithic 30-year mortgage stone deed bound in red caution tape
    cx = ox + 64
    by = 118
    ink = PAL['ink']
    
    d.ellipse([cx - 36, by - 6, cx + 36, by + 6], fill=(0, 0, 0, 95))
    
    # Massive Stone Slab
    sw = 68
    sh = 88
    sx = cx - sw // 2
    sy = by - sh - 4
    d.rounded_rectangle([sx, sy, sx + sw, sy + sh], radius=8, fill=PAL['stone_mid'], outline=ink)
    d.rounded_rectangle([sx + 4, sy + 4, sx + sw - 4, sy + sh - 4], radius=6, fill=PAL['stone_dk'])
    
    # Cracked fissures in stone (glowing red)
    fissure_c = PAL['red_hi'] if frame == 1 else PAL['crimson']
    d.line([cx - 10, sy + 10, cx - 18, sy + 35, cx - 12, sy + 60], fill=fissure_c, width=2)
    d.line([cx + 12, sy + 20, cx + 22, sy + 45, cx + 14, sy + 75], fill=fissure_c, width=2)
    
    # Bound in red & white warning tape
    d.line([sx + 2, sy + 22, sx + sw - 2, sy + 46], fill=PAL['red'], width=5)
    d.line([sx + 2, sy + 22, sx + sw - 2, sy + 46], fill=PAL['white'], width=2)
    d.line([sx + sw - 2, sy + 40, sx + 2, sy + 70], fill=PAL['red'], width=5)
    
    # Demonic glowing eyes inside stone
    eye_c = PAL['yellow_hi'] if frame == 1 else PAL['red_hi']
    d.rectangle([cx - 16, sy + 26, cx - 6, sy + 32], fill=eye_c)
    d.rectangle([cx + 6, sy + 26, cx + 16, sy + 32], fill=eye_c)
    # Carved "30 LAT"
    d.line([cx - 16, sy + 58, cx + 16, sy + 58], fill=PAL['yellow'], width=2)

def draw_audyt(d: ImageDraw.ImageDraw, ox: int, frame: int):
    # 128x128 Boss: Corporate robotic spreadsheet monster with paperclip claws & pie chart eyes
    cx = ox + 64
    by = 116
    ink = PAL['ink']
    
    d.ellipse([cx - 32, by - 6, cx + 32, by + 6], fill=(0, 0, 0, 85))
    
    # Spreadsheet Grid Body (Excel Green border + white/slate cells)
    bw = 64
    bh = 72
    bx = cx - bw // 2
    by_top = by - bh - 6
    d.rectangle([bx, by_top, bx + bw, by_top + bh], fill=PAL['panel'], outline=PAL['green_hi'], width=2)
    
    # Grid lines
    for gy in range(by_top + 16, by_top + bh, 14):
        d.line([bx, gy, bx + bw, gy], fill=PAL['green'], width=1)
    for gx in range(bx + 16, bx + bw, 16):
        d.line([gx, by_top, gx, by_top + bh], fill=PAL['green'], width=1)
        
    # Pie chart eyes (blood red / yellow slices)
    d.ellipse([cx - 22, by_top + 18, cx - 8, by_top + 32], fill=PAL['red_hi'], outline=ink)
    d.pieslice([cx - 22, by_top + 18, cx - 8, by_top + 32], 0, 90, fill=PAL['yellow'])
    d.ellipse([cx + 8, by_top + 18, cx + 22, by_top + 32], fill=PAL['red_hi'], outline=ink)
    d.pieslice([cx + 8, by_top + 18, cx + 22, by_top + 32], 0, 90, fill=PAL['yellow'])
    
    # Bar graph jagged teeth
    for tx_b in range(cx - 18, cx + 18, 6):
        h = 4 + (tx_b % 5)
        d.rectangle([tx_b, by_top + 46, tx_b + 4, by_top + 46 + h], fill=PAL['red_hi'])
        
    # Razor Paperclip Claws
    claw_offset = 6 if frame == 1 else 0
    d.line([bx - 12 - claw_offset, by_top + 20, bx - 2, by_top + 36], fill=PAL['silver'], width=3)
    d.line([bx - 14 - claw_offset, by_top + 36, bx - 2, by_top + 48], fill=PAL['silver'], width=3)
    d.line([bx + bw + 12 + claw_offset, by_top + 20, bx + bw + 2, by_top + 36], fill=PAL['silver'], width=3)

def draw_rwa_kulszowa(d: ImageDraw.ImageDraw, ox: int, frame: int):
    # 96x96: Pulsing violet & crimson neural electrical nerve mass with sparks
    cx = ox + 48
    cy = 48
    ink = PAL['ink']
    
    d.ellipse([cx - 22, 80, cx + 22, 88], fill=(0, 0, 0, 70))
    
    # Core nerve ganglion
    pulse = 3 if frame == 1 else 0
    r = 18 + pulse
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=PAL['purple'], outline=PAL['purple_hi'])
    d.ellipse([cx - r + 5, cy - r + 5, cx + r - 5, cy + r - 5], fill=PAL['crimson'])
    
    # Branching electric pain dendrites
    bolt_c = PAL['yellow_hi'] if frame == 1 else PAL['cyan_hi']
    angles = [0.4, 1.2, 2.1, 3.2, 4.0, 5.2]
    for a in angles:
        x1 = cx + math.cos(a) * r
        y1 = cy + math.sin(a) * r
        x2 = cx + math.cos(a + 0.3) * (r + 16)
        y2 = cy + math.sin(a + 0.3) * (r + 16)
        d.line([x1, y1, x2, y2], fill=bolt_c, width=2)
        d.circle((x2, y2), 2, fill=PAL['red_hi'])

ENEMIES = {
    'bolKregoslupa': draw_bol_kregoslupa,
    'slacki': draw_slacki,
    'sasiadSzkodnik': draw_sasiad_szkodnik,
    'autoTuneHipster': draw_autotune_hipster,
    'drogiePiwo': draw_drogie_piwo,
    'kark': draw_kark,
    'straznik': draw_straznik,
    'panJanusz': draw_pan_janusz,
    'kredyt': draw_kredyt,
    'audyt': draw_audyt,
    'rwaKulszowa': draw_rwa_kulszowa,
}

def main():
    print("Generating HD enemy sprites...")
    for eid, draw_fn in ENEMIES.items():
        size = BOSSES.get(eid, 96)
        sheet = Image.new("RGBA", (size * 2, size), (0, 0, 0, 0))
        d = ImageDraw.Draw(sheet)
        
        # Frame 0
        draw_fn(d, 0, 0)
        # Frame 1
        draw_fn(d, size, 1)
        
        out_path = os.path.join(OUT, f"{eid}.png")
        sheet.save(out_path, "PNG")
        print(f"Saved enemy {out_path} ({sheet.size})")

    print("All 11 HD enemy sprites generated successfully!")

if __name__ == "__main__":
    main()
