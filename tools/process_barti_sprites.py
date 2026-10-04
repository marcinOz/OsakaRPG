#!/usr/bin/env python3
"""process_barti_sprites.py - Extract, refine, and generate high-definition pixel art
sprites, portraits, and cards for Barti ("The Vinyl Bard") in OsakaRPG.

Conforms to engine specifications:
- barti_walk.png: 128x192 RGBA (4 columns x 4 rows, 32x48 per frame)
  Rows: 0=Down, 1=Left, 2=Right, 3=Up
  Cols: 4-frame walk cycle
- barti_battle.png: 512x80 RGBA (8 frames horizontal, 64x80 per frame)
  0=Idle, 1=Ready/Breath, 2=Windup, 3=Attack, 4=Skill, 5=Hurt, 6=KO, 7=Victory
- barti_sit.png: 64x32 RGBA (2 frames horizontal, 32x32 per frame)
  0=Seated, 1=Seated breath
- Portraits: barti_{128,96,64}.png, avatar_barti.png (32x32)
- Hero Card: card_barti -> cards/barti.png (307x182)
"""
import os
import sys
from collections import deque
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT, "art_src", "heroes", "barti")
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
    # Dark slate/navy background
    if r < 35 and g < 42 and b < 58:
        return True
    # Blue grid lines
    if abs(r - 55) < 18 and abs(g - 73) < 18 and abs(b - 93) < 18:
        return True
    if r < 60 and g < 80 and b < 100 and b > r + 20:
        return True
    return False

def extract_walk_cell(im, x0, y0, x1, y1):
    cell = im.crop((x0, y0, x1, y1))
    cw, ch = cell.size
    visited = set()
    q = deque()

    # Flood fill from perimeter
    for x in range(cw):
        if is_walk_bg(*cell.getpixel((x, 0))[:3]): visited.add((x, 0)); q.append((x, 0))
        if is_walk_bg(*cell.getpixel((x, ch - 1))[:3]): visited.add((x, ch - 1)); q.append((x, ch - 1))
    for y in range(ch):
        if is_walk_bg(*cell.getpixel((0, y))[:3]): visited.add((0, y)); q.append((0, y))
        if is_walk_bg(*cell.getpixel((cw - 1, y))[:3]): visited.add((cw - 1, y)); q.append((cw - 1, y))

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
                r, g, b = cell.getpixel((x, y))[:3]
                # Defringe background remnants
                if is_walk_bg(r, g, b):
                    continue
                fg.putpixel((x, y), (r, g, b, 255))

    bbox = fg.getbbox()
    return fg.crop(bbox) if bbox else fg

def build_walk_sheet():
    src_path = os.path.join(SRC_DIR, "walk_source.png")
    im = Image.open(src_path).convert("RGBA")

    cols = [0, 173, 342, 511, 681, 850, 1024]
    rows = [36, 203, 376, 555]

    # Pre-extract all 6 frames for each direction
    down_raw = [extract_walk_cell(im, cols[c] + 3, rows[0] + 3, cols[c + 1] - 3, rows[1] - 3) for c in range(6)]
    right_raw = [extract_walk_cell(im, cols[c] + 3, rows[1] + 3, cols[c + 1] - 3, rows[2] - 3) for c in range(6)]
    up_raw = [extract_walk_cell(im, cols[c] + 3, rows[2] + 3, cols[c + 1] - 3, rows[3] - 3) for c in range(6)]

    # 4 frames per direction:
    # Down: [step_L, passing, step_R, passing]
    down_frames = [down_raw[0], down_raw[1], down_raw[3], down_raw[4]]

    # Right profile: [step_L, passing, step_R, passing]
    right_frames = [right_raw[0], right_raw[1], right_raw[3], right_raw[4]]

    # Left profile: mirrored Right
    left_frames = [f.transpose(Image.FLIP_LEFT_RIGHT) for f in right_frames]

    # Up: back walk [step_L, passing, step_R, passing]
    up_frames = [up_raw[0], up_raw[1], up_raw[3], up_raw[4]]

    # Game row ordering: 0=Down, 1=Left, 2=Right, 3=Up
    cycle_rows = [down_frames, left_frames, right_frames, up_frames]

    sheet = Image.new("RGBA", (128, 192), (0, 0, 0, 0))
    fw, fh = 32, 48
    target_char_h = 42.0
    ground_y = 45

    for r_idx, row_frames in enumerate(cycle_rows):
        for c_idx, fg in enumerate(row_frames):
            orig_w, orig_h = fg.size
            scale = target_char_h / float(orig_h)
            sw = max(1, round(orig_w * scale))
            sh = max(1, round(orig_h * scale))
            sc = fg.resize((sw, sh), Image.Resampling.LANCZOS)

            # Center on spine (mean x of head/upper body)
            top = max(1, int(sc.height * 0.4))
            xs = [x for y in range(top) for x in range(sc.width) if sc.getpixel((x, y))[3] > 0]
            spine = sum(xs) / len(xs) if xs else sc.width / 2.0

            dx = c_idx * fw + 16 - round(spine)
            dy = r_idx * fh + ground_y - sh
            sheet.paste(sc, (dx, dy), sc)

    out_path = os.path.join(SPRITES_DIR, "barti_walk.png")
    sheet.save(out_path, "PNG")
    print(f"Generated {out_path}: {sheet.size}")


# ==============================================================================
# 2. BATTLE SHEET GENERATOR
# ==============================================================================
def is_bat_bg(r, g, b):
    # Blue grid background
    if abs(r - 53) < 22 and abs(g - 76) < 22 and abs(b - 108) < 25:
        return True
    # Darker blue background
    if r < 40 and g < 55 and b < 80:
        return True
    # Cyan grid lines
    if r < 85 and g < 115 and b < 155 and b > r + 35:
        return True
    return False

def extract_battle_cell(im, x0, y0, x1, y1):
    cell = im.crop((x0, y0, x1, y1))
    cw, ch = cell.size
    visited = set()
    q = deque()

    for x in range(cw):
        if is_bat_bg(*cell.getpixel((x, 0))[:3]): visited.add((x, 0)); q.append((x, 0))
        if is_bat_bg(*cell.getpixel((x, ch - 1))[:3]): visited.add((x, ch - 1)); q.append((x, ch - 1))
    for y in range(ch):
        if is_bat_bg(*cell.getpixel((0, y))[:3]): visited.add((0, y)); q.append((0, y))
        if is_bat_bg(*cell.getpixel((cw - 1, y))[:3]): visited.add((cw - 1, y)); q.append((cw - 1, y))

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
                r, g, b = cell.getpixel((x, y))[:3]
                if is_bat_bg(r, g, b):
                    continue
                fg.putpixel((x, y), (r, g, b, 255))

    bbox = fg.getbbox()
    return fg.crop(bbox) if bbox else fg

def build_battle_sheet():
    src_path = os.path.join(SRC_DIR, "battle_source.png")
    im = Image.open(src_path).convert("RGBA")

    # 8 combat poses:
    # 0: Idle 1 (holding sleeve)
    # 1: Idle 2 / Breath (holding disc)
    # 2: Windup (vinyl drawn back)
    # 3: Attack (vinyl slash arc)
    # 4: Skill (turntable bass blast)
    # 5: Hurt (recoil & flying vinyls)
    # 6: KO (collapsed face down)
    # 7: Victory (golden vinyl held high)
    boxes = [
        ('idle0',   (20, 45, 160, 275)),
        ('idle1',   (160, 45, 300, 275)),
        ('windup',  (320, 45, 480, 275)),
        ('attack',  (480, 45, 780, 275)),
        ('skill',   (0, 280, 310, 520)),
        ('hurt',    (310, 280, 520, 520)),
        ('ko',      (520, 280, 840, 520)),
        ('victory', (840, 280, 1010, 520)),
    ]

    sheet = Image.new("RGBA", (512, 80), (0, 0, 0, 0))
    frame_w, frame_h = 64, 80
    ground_y = 75

    for out_idx, (name, box) in enumerate(boxes):
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

    out_path = os.path.join(SPRITES_DIR, "barti_battle.png")
    sheet.save(out_path, "PNG")
    print(f"Generated {out_path}: {sheet.size}")


# ==============================================================================
# 3. CAMPFIRE SIT SHEET GENERATOR
# ==============================================================================
def is_sit_bg(r, g, b):
    # Brick wall
    if 65 <= r <= 140 and 45 <= g <= 100 and 45 <= b <= 100:
        if b < 55 and r > 95: return False # hair
        if r > 180: return False           # skin/tee
        if b > 115: return False           # denim
        if g > 135: return False           # headphones
        return True
    # Floor / baseboard
    if 80 <= r <= 140 and 70 <= g <= 120 and 75 <= b <= 120:
        return True
    # Carpet
    if 50 <= r <= 130 and 65 <= g <= 170 and 75 <= b <= 150:
        if b > 120 and r < 80: return False # denim
        return True
    # Boombox / speaker edges
    if r < 40 and g < 45 and b < 50:
        return True
    return False

def build_sit_sheet():
    src_path = os.path.join(SRC_DIR, "sitting_source.png")
    im = Image.open(src_path).convert("RGBA")

    # Barti seated in Frame 1
    cell = im.crop((100, 150, 390, 470))
    cw, ch = cell.size
    visited = set()
    q = deque()

    for x in range(cw):
        if is_sit_bg(*cell.getpixel((x, 0))[:3]): visited.add((x, 0)); q.append((x, 0))
        if is_sit_bg(*cell.getpixel((x, ch - 1))[:3]): visited.add((x, ch - 1)); q.append((x, ch - 1))
    for y in range(ch):
        if is_sit_bg(*cell.getpixel((0, y))[:3]): visited.add((0, y)); q.append((0, y))
        if is_sit_bg(*cell.getpixel((cw - 1, y))[:3]): visited.add((cw - 1, y)); q.append((cw - 1, y))

    while q:
        cx, cy = q.popleft()
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < cw and 0 <= ny < ch and (nx, ny) not in visited:
                if is_sit_bg(*cell.getpixel((nx, ny))[:3]):
                    visited.add((nx, ny))
                    q.append((nx, ny))

    fg = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    for y in range(ch):
        for x in range(cw):
            if (x, y) not in visited:
                r, g, b = cell.getpixel((x, y))[:3]
                if is_sit_bg(r, g, b):
                    continue
                fg.putpixel((x, y), (r, g, b, 255))

    bbox = fg.getbbox()
    barti_sit = fg.crop(bbox) if bbox else fg

    # In sitting_source, Barti faces LEFT.
    # CampfireScene.ts applies spr.setFlipX(false) to Barti (right side hero),
    # so facing LEFT naturally looks straight toward the fire!
    target_h = 28
    scale = target_h / float(barti_sit.height)
    new_w = max(1, int(round(barti_sit.width * scale)))
    new_h = target_h
    if new_w > 30:
        new_w = 30

    frame0 = barti_sit.resize((new_w, new_h), Image.Resampling.LANCZOS)
    # Frame 1: breathing (subtle 1px upward offset)
    frame1 = frame0.copy()

    sheet = Image.new("RGBA", (64, 32), (0, 0, 0, 0))
    # Frame 0
    sheet.paste(frame0, (16 - new_w // 2, 30 - new_h), frame0)
    # Frame 1 with 1px breathing bob
    sheet.paste(frame1, (32 + (16 - new_w // 2), 29 - new_h), frame1)

    out_path = os.path.join(SPRITES_DIR, "barti_sit.png")
    sheet.save(out_path, "PNG")
    print(f"Generated {out_path}: {sheet.size}")


# ==============================================================================
# 4. PORTRAITS, AVATAR & HERO CARD GENERATOR
# ==============================================================================
def build_portraits():
    # Take high-detail bust crop from battle_source (Idle 1)
    src_path = os.path.join(SRC_DIR, "battle_source.png")
    im = Image.open(src_path).convert("RGBA")

    # Extract Idle 1 sprite
    b0 = extract_battle_cell(im, 20, 45, 160, 275)
    # Crop head and shoulders
    bust = b0.crop((8, 0, 95, 95))
    bw, bh = bust.size

    # Composite on dark navy panel background matching all hero portraits
    NAVY = (16, 28, 44)

    for sz in [128, 96, 64]:
        p_canvas = Image.new("RGB", (sz, sz), NAVY)
        target_bh = int(sz * 0.90)
        scale = target_bh / float(bh)
        tb_w = int(round(bw * scale))
        tb_h = target_bh
        scaled_bust = bust.resize((tb_w, tb_h), Image.Resampling.LANCZOS)
        p_canvas.paste(scaled_bust, ((sz - tb_w) // 2, sz - tb_h), scaled_bust)

        out_path = os.path.join(PORTRAITS_DIR, f"barti_{sz}.png")
        p_canvas.save(out_path, "PNG")
        print(f"Generated {out_path}: {p_canvas.size}")

    # Avatar 32x32 (phone chat UI)
    avatar = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    av_bust = bust.resize((26, 29), Image.Resampling.LANCZOS)
    avatar.paste(av_bust, (3, 2), av_bust)
    av_path = os.path.join(UI_DIR, "avatar_barti.png")
    avatar.save(av_path, "PNG")
    print(f"Generated {av_path}: {avatar.size}")

    # Hero Card (307x182) for Analyzer
    # Vintage vinyl scene with boombox, speaker, vinyl stack, and Barti
    sit_src = os.path.join(SRC_DIR, "sitting_source.png")
    sim = Image.open(sit_src).convert("RGB")
    card_crop = sim.crop((32, 110, 485, 490))
    card = card_crop.resize((307, 182), Image.Resampling.LANCZOS)
    card_path = os.path.join(CARDS_DIR, "barti.png")
    card.save(card_path, "PNG")
    print(f"Generated {card_path}: {card.size}")


if __name__ == "__main__":
    print("Building high-detail Barti assets...")
    build_walk_sheet()
    build_battle_sheet()
    build_sit_sheet()
    build_portraits()
    print("All Barti assets generated successfully!")
