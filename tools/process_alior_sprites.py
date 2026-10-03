#!/usr/bin/env python3
"""process_alior_sprites.py - Extract, refine, and generate high-definition pixel art
sprites, portraits, and cards for Alior ("KRZYSZTOF K.") in OsakaRPG.

Conforms to engine specifications:
- alior_walk.png: 128x192 RGBA (4 columns x 4 rows, 32x48 per frame)
  Rows: 0=Down, 1=Left, 2=Right, 3=Up
  Cols: 4-frame walk cycle
- alior_battle.png: 512x80 RGBA (8 frames horizontal, 64x80 per frame)
  0=Idle, 1=Ready, 2=Windup, 3=Attack, 4=Skill, 5=Hurt, 6=KO, 7=Victory
- alior_sit.png: 64x32 RGBA (2 frames horizontal, 32x32 per frame)
  0=Seated, 1=Seated breath
- Portraits: alior_{128,96,64}.png, avatar_alior.png (32x32)
- Hero Card: card_alior -> cards/alior.png (307x182)
"""
import os
import sys
from collections import deque
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT, "art_src", "heroes", "alior")
SPRITES_DIR = os.path.join(ROOT, "public", "assets", "sprites")
PORTRAITS_DIR = os.path.join(ROOT, "public", "assets", "portraits")
UI_DIR = os.path.join(ROOT, "public", "assets", "ui")
CARDS_DIR = os.path.join(ROOT, "public", "assets", "cards")

os.makedirs(SPRITES_DIR, exist_ok=True)
os.makedirs(PORTRAITS_DIR, exist_ok=True)
os.makedirs(UI_DIR, exist_ok=True)
os.makedirs(CARDS_DIR, exist_ok=True)


# ==============================================================================
# 1. WALK CYCLE SHEET GENERATOR
# ==============================================================================
def is_walk_bg(r, g, b):
    # Grey background in walk_source.png is (80, 80, 80)
    return abs(r - 80) <= 8 and abs(g - 80) <= 8 and abs(b - 80) <= 8

def extract_walk_cell(im, x0, y0, x1, y1):
    # Add safety margin around cell
    x0, y0 = max(0, x0 - 4), max(0, y0 - 4)
    x1, y1 = min(im.width, x1 + 4), min(im.height, y1 + 4)
    cell = im.crop((x0, y0, x1, y1))
    cw, ch = cell.size
    visited = set()
    q = deque()

    # Flood fill from perimeter
    for x in range(cw):
        if is_walk_bg(*cell.getpixel((x, 0))[:3]): visited.add((x, 0)); q.append((x, 0))
        if is_walk_bg(*cell.getpixel((x, ch-1))[:3]): visited.add((x, ch-1)); q.append((x, ch-1))
    for y in range(ch):
        if is_walk_bg(*cell.getpixel((0, y))[:3]): visited.add((0, y)); q.append((0, y))
        if is_walk_bg(*cell.getpixel((cw-1, y))[:3]): visited.add((cw-1, y)); q.append((cw-1, y))

    while q:
        cx, cy = q.popleft()
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < cw and 0 <= ny < ch and (nx, ny) not in visited:
                if is_walk_bg(*cell.getpixel((nx, ny))[:3]):
                    visited.add((nx, ny))
                    q.append((nx, ny))

    # Mask foreground
    fg = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    for y in range(ch):
        for x in range(cw):
            if (x, y) not in visited:
                fg.putpixel((x, y), cell.getpixel((x, y)))

    bbox = fg.getbbox()
    return fg.crop(bbox) if bbox else fg

def build_walk_sheet():
    src_path = os.path.join(SRC_DIR, "walk_source.png")
    im = Image.open(src_path).convert("RGBA")

    # Directions: 0=Down, 1=Left, 2=Right, 3=Up
    # In walk_source:
    # Row 0: cols 0..3 (Down), cols 4..7 (Up)
    # Row 1: cols 0..3 (Right), cols 4..7 (Left)
    dirs = {
        'down':  ([(25, 114), (154, 242), (280, 369), (405, 494)], (9, 188)),
        'left':  ([(566, 631), (690, 759), (810, 873), (930, 994)], (201, 376)),
        'right': ([(37, 102), (162, 230), (288, 357), (414, 482)], (201, 376)),
        'up':    ([(550, 637), (678, 762), (794, 882), (920, 1007)], (9, 188)),
    }
    order = ['down', 'left', 'right', 'up']  # Game rows 0..3

    sheet = Image.new("RGBA", (128, 192), (0, 0, 0, 0))
    fw, fh = 32, 48
    scale = 42.0 / 182.0
    ground_y = 45

    for r_idx, dname in enumerate(order):
        cols, (y0, y1) = dirs[dname]
        for c_idx, (x0, x1) in enumerate(cols):
            fg = extract_walk_cell(im, x0, y0, x1, y1)
            # Find horizontal spine (mean x of head/upper body)
            top = max(1, int(fg.height * 0.4))
            xs = [x for y in range(top) for x in range(fg.width) if fg.getpixel((x, y))[3] > 0]
            spine = sum(xs) / len(xs) if xs else fg.width / 2.0

            sw = max(1, round(fg.width * scale))
            sh = max(1, round(fg.height * scale))
            sc = fg.resize((sw, sh), Image.Resampling.LANCZOS)

            dx = c_idx * fw + 16 - round(spine * scale)
            dy = r_idx * fh + ground_y - sh
            sheet.paste(sc, (dx, dy), sc)

    out_path = os.path.join(SPRITES_DIR, "alior_walk.png")
    sheet.save(out_path, "PNG")
    print(f"Generated {out_path}: {sheet.size}")


# ==============================================================================
# 2. BATTLE SHEET GENERATOR
# ==============================================================================
def is_bat_bg(r, g, b):
    # Light grey background in battle_source.png is (184, 189, 192)
    return abs(r - 184) <= 15 and abs(g - 189) <= 15 and abs(b - 192) <= 15

def extract_battle_cell(im, x0, y0, x1, y1):
    cell = im.crop((x0, y0, x1, y1))
    cw, ch = cell.size
    visited = set()
    q = deque()

    for x in range(cw):
        if is_bat_bg(*cell.getpixel((x, 0))[:3]): visited.add((x, 0)); q.append((x, 0))
        if is_bat_bg(*cell.getpixel((x, ch-1))[:3]): visited.add((x, ch-1)); q.append((x, ch-1))
    for y in range(ch):
        if is_bat_bg(*cell.getpixel((0, y))[:3]): visited.add((0, y)); q.append((0, y))
        if is_bat_bg(*cell.getpixel((cw-1, y))[:3]): visited.add((cw-1, y)); q.append((cw-1, y))

    while q:
        cx, cy = q.popleft()
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < cw and 0 <= ny < ch and (nx, ny) not in visited:
                if is_bat_bg(*cell.getpixel((nx, ny))[:3]):
                    visited.add((nx, ny))
                    q.append((nx, ny))

    fg = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    for y in range(ch):
        for x in range(cw):
            if (x, y) not in visited:
                r, g, b, a = cell.getpixel((x, y))
                # Defringe border background remnants
                if abs(r - 184) <= 8 and abs(g - 189) <= 8 and abs(b - 192) <= 8:
                    continue
                fg.putpixel((x, y), (r, g, b, 255))

    bbox = fg.getbbox()
    return fg.crop(bbox) if bbox else fg

def build_battle_sheet():
    src_path = os.path.join(SRC_DIR, "battle_source.png")
    im = Image.open(src_path).convert("RGBA")

    # 8 animation states:
    # 0: Idle
    # 1: Ready
    # 2: Windup
    # 3: Attack
    # 4: Skill
    # 5: Hurt
    # 6: KO
    # 7: Victory
    poses = [
        ('idle', (39, 49, 153, 251)),
        ('ready', (36, 284, 202, 514)),
        ('windup', (193, 49, 325, 251)),
        ('attack', (378, 49, 626, 251)),
        ('skill', (664, 49, 861, 251)),
        ('hurt', (275, 284, 399, 514)),
        ('ko', (444, 284, 810, 514)),
        ('victory', (827, 284, 1007, 514)),
    ]

    sheet = Image.new("RGBA", (512, 80), (0, 0, 0, 0))
    frame_w, frame_h = 64, 80
    ground_y = 75

    for out_idx, (name, box) in enumerate(poses):
        char_crop = extract_battle_cell(im, *box)
        orig_w, orig_h = char_crop.size

        if name == 'ko':
            target_w = 60
            scale = target_w / float(orig_w)
            new_w = target_w
            new_h = max(1, int(round(orig_h * scale)))
            scaled = char_crop.resize((new_w, new_h), Image.Resampling.LANCZOS)
            dst_x = out_idx * frame_w + (frame_w - new_w) // 2
            dst_y = ground_y - new_h
        else:
            target_char_h = 72
            scale = target_char_h / float(orig_h)
            new_h = target_char_h
            new_w = max(1, int(round(orig_w * scale)))
            if new_w > frame_w - 4:
                new_w = frame_w - 4
                new_h = max(1, int(round(orig_h * (new_w / float(orig_w)))))

            scaled = char_crop.resize((new_w, new_h), Image.Resampling.LANCZOS)
            dst_x = out_idx * frame_w + (frame_w - new_w) // 2
            dst_y = ground_y - new_h

        sheet.paste(scaled, (dst_x, dst_y), scaled)

    out_path = os.path.join(SPRITES_DIR, "alior_battle.png")
    sheet.save(out_path, "PNG")
    print(f"Generated {out_path}: {sheet.size}")


# ==============================================================================
# 3. CAMPFIRE SIT SHEET GENERATOR
# ==============================================================================
def is_gaming_bg(r, g, b):
    # Dark slate background in gaming_source.png
    return r <= 33 and g <= 35 and b <= 47

def build_sit_sheet():
    src_path = os.path.join(SRC_DIR, "gaming_source.png")
    im = Image.open(src_path).convert("RGBA")

    # Crop Frame 1: Alior seated in gaming chair with handheld console
    cell = im.crop((40, 70, 480, 520))
    cw, ch = cell.size
    visited = set()
    q = deque()

    for x in range(cw):
        if is_gaming_bg(*cell.getpixel((x, 0))[:3]): visited.add((x, 0)); q.append((x, 0))
        if is_gaming_bg(*cell.getpixel((x, ch-1))[:3]): visited.add((x, ch-1)); q.append((x, ch-1))
    for y in range(ch):
        if is_gaming_bg(*cell.getpixel((0, y))[:3]): visited.add((0, y)); q.append((0, y))
        if is_gaming_bg(*cell.getpixel((cw-1, y))[:3]): visited.add((cw-1, y)); q.append((cw-1, y))

    while q:
        cx, cy = q.popleft()
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < cw and 0 <= ny < ch and (nx, ny) not in visited:
                if is_gaming_bg(*cell.getpixel((nx, ny))[:3]):
                    visited.add((nx, ny))
                    q.append((nx, ny))

    fg = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    for y in range(ch):
        for x in range(cw):
            if (x, y) not in visited:
                fg.putpixel((x, y), cell.getpixel((x, y)))

    bbox = fg.getbbox()
    alior_sit = fg.crop(bbox) if bbox else fg

    # Alior in gaming_source faces right.
    # CampfireScene.ts applies spr.setFlipX(true) to Alior (left side hero),
    # so saving facing LEFT ensures flipping in-game makes him face right toward the campfire!
    alior_left = alior_sit.transpose(Image.FLIP_LEFT_RIGHT)

    # Scale to 32x32 per frame (total 64x32)
    target_h = 28
    scale = target_h / float(alior_left.height)
    new_w = max(1, int(round(alior_left.width * scale)))
    new_h = target_h
    if new_w > 30:
        new_w = 30

    frame0 = alior_left.resize((new_w, new_h), Image.Resampling.LANCZOS)
    # Frame 1: breathing (subtle 1px upward offset)
    frame1 = frame0.copy()

    sheet = Image.new("RGBA", (64, 32), (0, 0, 0, 0))
    # Place frame 0
    sheet.paste(frame0, (16 - new_w // 2, 30 - new_h), frame0)
    # Place frame 1 with subtle breathing bob (-1px)
    sheet.paste(frame1, (32 + (16 - new_w // 2), 29 - new_h), frame1)

    out_path = os.path.join(SPRITES_DIR, "alior_sit.png")
    sheet.save(out_path, "PNG")
    print(f"Generated {out_path}: {sheet.size}")


# ==============================================================================
# 4. PORTRAITS, AVATAR & HERO CARD GENERATOR
# ==============================================================================
def build_portraits():
    src_path = os.path.join(SRC_DIR, "gaming_source.png")
    im = Image.open(src_path).convert("RGBA")

    # Crop bust from Frame 1: Head, headset, beard, shoulders, upper chest
    bust = im.crop((145, 90, 345, 350))
    bw, bh = bust.size

    visited = set()
    q = deque()
    for x in range(bw):
        if is_gaming_bg(*bust.getpixel((x, 0))[:3]): visited.add((x, 0)); q.append((x, 0))
        if is_gaming_bg(*bust.getpixel((x, bh-1))[:3]): visited.add((x, bh-1)); q.append((x, bh-1))
    for y in range(bh):
        if is_gaming_bg(*bust.getpixel((0, y))[:3]): visited.add((0, y)); q.append((0, y))
        if is_gaming_bg(*bust.getpixel((bw-1, y))[:3]): visited.add((bw-1, y)); q.append((bw-1, y))

    while q:
        cx, cy = q.popleft()
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < bw and 0 <= ny < bh and (nx, ny) not in visited:
                if is_gaming_bg(*bust.getpixel((nx, ny))[:3]):
                    visited.add((nx, ny))
                    q.append((nx, ny))

    bust_clean = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    for y in range(bh):
        for x in range(bw):
            if (x, y) not in visited:
                bust_clean.putpixel((x, y), bust.getpixel((x, y)))

    # Composite on dark navy panel background matching all hero portraits
    NAVY = (16, 28, 44)

    for sz in [128, 96, 64]:
        p_canvas = Image.new("RGB", (sz, sz), NAVY)
        # Scale bust to fill ~90% of portrait height
        target_bh = int(sz * 0.90)
        scale = target_bh / float(bh)
        tb_w = int(round(bw * scale))
        tb_h = target_bh
        scaled_bust = bust_clean.resize((tb_w, tb_h), Image.Resampling.LANCZOS)
        p_canvas.paste(scaled_bust, ((sz - tb_w) // 2, sz - tb_h), scaled_bust)

        out_path = os.path.join(PORTRAITS_DIR, f"alior_{sz}.png")
        p_canvas.save(out_path, "PNG")
        print(f"Generated {out_path}: {p_canvas.size}")

    # Avatar 32x32 (phone chat UI)
    avatar = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    av_bust = bust_clean.resize((26, 30), Image.Resampling.LANCZOS)
    avatar.paste(av_bust, (3, 2), av_bust)
    av_path = os.path.join(UI_DIR, "avatar_alior.png")
    avatar.save(av_path, "PNG")
    print(f"Generated {av_path}: {avatar.size}")

    # Hero Card (307x182) for Analyzer
    # Action scene crop of Alior in his gamer cockpit
    card_crop = im.crop((50, 85, 470, 334)).convert("RGB")
    card = card_crop.resize((307, 182), Image.Resampling.LANCZOS)
    card_path = os.path.join(CARDS_DIR, "alior.png")
    card.save(card_path, "PNG")
    print(f"Generated {card_path}: {card.size}")


if __name__ == "__main__":
    print("Building high-detail Alior assets...")
    build_walk_sheet()
    build_battle_sheet()
    build_sit_sheet()
    build_portraits()
    print("All Alior assets generated successfully!")
