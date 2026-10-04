#!/usr/bin/env python3
"""process_lisu_sprites.py - Extract, refine, and generate high-definition pixel art
sprites, portraits, and cards for Lisu ("The Swift Scout") in OsakaRPG.

Conforms to engine specifications:
- lisu_walk.png: 128x192 RGBA (4 columns x 4 rows, 32x48 per frame)
  Rows: 0=Down, 1=Left, 2=Right, 3=Up
  Cols: 4-frame walk cycle
- lisu_battle.png: 512x80 RGBA (8 frames horizontal, 64x80 per frame)
  0=Idle, 1=Ready, 2=Windup, 3=Attack, 4=Skill, 5=Hurt, 6=KO, 7=Victory
- lisu_sit.png: 64x32 RGBA (2 frames horizontal, 32x32 per frame)
  0=Seated/Crouched, 1=Seated breath
- Portraits: lisu_{128,96,64}.png, avatar_lisu.png (32x32)
- Hero Card: card_lisu -> cards/lisu.png (307x182)
"""
import os
import sys
from collections import deque
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT, "art_src", "heroes", "lisu")
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
    # Grey background in walk_source.png is (137, 137, 137)
    return abs(r - 137) <= 18 and abs(g - 137) <= 18 and abs(b - 137) <= 18

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
        if is_bg_pixel := is_walk_bg(*cell.getpixel((cw - 1, y))[:3]): visited.add((cw - 1, y)); q.append((cw - 1, y))

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
                # Defringe gray border residue
                if abs(r - 137) <= 8 and abs(g - 137) <= 8 and abs(b - 137) <= 8:
                    continue
                fg.putpixel((x, y), (r, g, b, 255))

    bbox = fg.getbbox()
    return fg.crop(bbox) if bbox else fg

def build_walk_sheet():
    src_path = os.path.join(SRC_DIR, "walk_source.png")
    im = Image.open(src_path).convert("RGB")

    xs = [7, 175, 344, 514, 683, 851, 1018]
    ys = [36, 285, 556]

    # Pre-extract cells:
    # Row 0: c0=down idle, c1=down step L, c3=profile 1, c4=profile 2, c5=profile 3
    # Row 1: c0=up idle, c3=up step L, c4=up step R
    r0_c0 = extract_walk_cell(im, xs[0] + 4, ys[0] + 4, xs[1] - 4, ys[1] - 4)
    r0_c1 = extract_walk_cell(im, xs[1] + 4, ys[0] + 4, xs[2] - 4, ys[1] - 4)
    r0_c3 = extract_walk_cell(im, xs[3] + 4, ys[0] + 4, xs[4] - 4, ys[1] - 4)
    r0_c4 = extract_walk_cell(im, xs[4] + 4, ys[0] + 4, xs[5] - 4, ys[1] - 4)
    r0_c5 = extract_walk_cell(im, xs[5] + 4, ys[0] + 4, xs[6] - 4, ys[1] - 4)

    r1_c0 = extract_walk_cell(im, xs[0] + 4, ys[1] + 4, xs[1] - 4, ys[2] - 4)
    r1_c3 = extract_walk_cell(im, xs[3] + 4, ys[1] + 4, xs[4] - 4, ys[2] - 4)
    r1_c4 = extract_walk_cell(im, xs[4] + 4, ys[1] + 4, xs[5] - 4, ys[2] - 4)

    # 4 frames per direction:
    # Down: [idle, step_left, idle, step_right]
    down_frames = [
        r0_c0,
        r0_c1,
        r0_c0,
        r0_c1.transpose(Image.FLIP_LEFT_RIGHT)
    ]

    # Right: profile walk sequence [c3, c4, c5, c4]
    right_frames = [
        r0_c3,
        r0_c4,
        r0_c5,
        r0_c4
    ]

    # Left: flipped right frames
    left_frames = [f.transpose(Image.FLIP_LEFT_RIGHT) for f in right_frames]

    # Up: back walk sequence [idle, step_L, idle, step_R]
    up_frames = [
        r1_c0,
        r1_c3,
        r1_c0,
        r1_c4
    ]

    # Game row ordering: 0=Down, 1=Left, 2=Right, 3=Up
    cycle_rows = [down_frames, left_frames, right_frames, up_frames]

    sheet = Image.new("RGBA", (128, 192), (0, 0, 0, 0))
    fw, fh = 32, 48
    target_char_h = 41.0
    ground_y = 45

    for r_idx, row_frames in enumerate(cycle_rows):
        for c_idx, fg in enumerate(row_frames):
            orig_w, orig_h = fg.size
            scale = target_char_h / float(orig_h)
            sw = max(1, round(orig_w * scale))
            sh = max(1, round(orig_h * scale))
            sc = fg.resize((sw, sh), Image.Resampling.LANCZOS)

            # Center spine (mean x of head/upper body)
            top = max(1, int(sc.height * 0.4))
            xs_body = [x for y in range(top) for x in range(sc.width) if sc.getpixel((x, y))[3] > 0]
            spine = sum(xs_body) / len(xs_body) if xs_body else sc.width / 2.0

            dx = c_idx * fw + 16 - round(spine)
            dy = r_idx * fh + ground_y - sh
            sheet.paste(sc, (dx, dy), sc)

    out_path = os.path.join(SPRITES_DIR, "lisu_walk.png")
    sheet.save(out_path, "PNG")
    print(f"Generated {out_path}: {sheet.size}")


# ==============================================================================
# 2. BATTLE SHEET GENERATOR
# ==============================================================================
def is_battle_bg(r, g, b):
    # Slate-blue background
    if abs(r - 39) <= 14 and abs(g - 58) <= 14 and abs(b - 72) <= 14:
        return True
    # Dark border lines or badge background
    if r < 32 and g < 48 and b < 62:
        return True
    return False

def extract_battle_cell(im, idx):
    x0 = int(round(3 + idx * (1018.0 / 8.0)))
    x1 = int(round(3 + (idx + 1) * (1018.0 / 8.0)))
    # Add safety inset to avoid outer box borders
    cell = im.crop((x0 + 3, 22, x1 - 3, 118))
    cw, ch = cell.size
    visited = set()
    q = deque()

    for x in range(cw):
        if is_battle_bg(*cell.getpixel((x, 0))[:3]): visited.add((x, 0)); q.append((x, 0))
        if is_battle_bg(*cell.getpixel((x, ch - 1))[:3]): visited.add((x, ch - 1)); q.append((x, ch - 1))
    for y in range(ch):
        if is_battle_bg(*cell.getpixel((0, y))[:3]): visited.add((0, y)); q.append((0, y))
        if is_battle_bg(*cell.getpixel((cw - 1, y))[:3]): visited.add((cw - 1, y)); q.append((cw - 1, y))

    while q:
        cx, cy = q.popleft()
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < cw and 0 <= ny < ch and (nx, ny) not in visited:
                if is_battle_bg(*cell.getpixel((nx, ny))[:3]):
                    visited.add((nx, ny))
                    q.append((nx, ny))

    fg = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    for y in range(ch):
        for x in range(cw):
            if (x, y) not in visited:
                # Strip frame badge in top-left
                if x < 15 and y < 15:
                    continue
                # Strip border lines along edges
                if x >= cw - 2 or y >= ch - 2:
                    continue
                fg.putpixel((x, y), cell.getpixel((x, y)))

    bbox = fg.getbbox()
    return fg.crop(bbox) if bbox else fg

def build_battle_sheet():
    src_path = os.path.join(SRC_DIR, "battle_source.png")
    im = Image.open(src_path).convert("RGBA")

    # 8 animation states:
    # 0: Idle stand
    # 1: Ready / Guard (unmasked stance)
    # 2: Windup (sprint surge)
    # 3: Attack (dagger slash with arc FX)
    # 4: Skill (smoke grenade throw)
    # 5: Hurt (recoil)
    # 6: KO (flat on back)
    # 7: Victory (treasure chest aloft)
    raw_frames = [extract_battle_cell(im, i) for i in range(8)]

    sheet = Image.new("RGBA", (512, 80), (0, 0, 0, 0))
    frame_w, frame_h = 64, 80
    ground_y = 75

    for out_idx in range(8):
        char_crop = raw_frames[out_idx]
        orig_w, orig_h = char_crop.size

        if out_idx == 6:  # KO frame (horizontal on ground)
            target_w = min(60, orig_w)
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
            if new_w > frame_w - 2:
                new_w = frame_w - 2
                new_h = max(1, int(round(orig_h * (new_w / float(orig_w)))))

            scaled = char_crop.resize((new_w, new_h), Image.Resampling.LANCZOS)
            dst_x = out_idx * frame_w + (frame_w - new_w) // 2
            dst_y = ground_y - new_h

        sheet.paste(scaled, (dst_x, dst_y), scaled)

    out_path = os.path.join(SPRITES_DIR, "lisu_battle.png")
    sheet.save(out_path, "PNG")
    print(f"Generated {out_path}: {sheet.size}")


# ==============================================================================
# 3. CAMPFIRE SIT SHEET GENERATOR
# ==============================================================================
def is_crouch_bg(r, g, b):
    # Slate-blue grid background in crouch_source.png
    diff = max(r, g, b) - min(r, g, b)
    if diff <= 32 and b >= r and b >= g - 2 and r < 140 and g < 155 and b < 165:
        return True
    return False

def extract_crouch_sprite():
    src_path = os.path.join(SRC_DIR, "crouch_source.png")
    im = Image.open(src_path).convert("RGBA")

    # Frame 1: Crouch Idle (left half of sheet)
    cell = im.crop((20, 115, 450, 520))
    cw, ch = cell.size
    visited = set()
    q = deque()

    for x in range(cw):
        if is_crouch_bg(*cell.getpixel((x, 0))[:3]): visited.add((x, 0)); q.append((x, 0))
        if is_crouch_bg(*cell.getpixel((x, ch - 1))[:3]): visited.add((x, ch - 1)); q.append((x, ch - 1))
    for y in range(ch):
        if is_crouch_bg(*cell.getpixel((0, y))[:3]): visited.add((0, y)); q.append((0, y))
        if is_crouch_bg(*cell.getpixel((cw - 1, y))[:3]): visited.add((cw - 1, y)); q.append((cw - 1, y))

    while q:
        cx, cy = q.popleft()
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < cw and 0 <= ny < ch and (nx, ny) not in visited:
                if is_crouch_bg(*cell.getpixel((nx, ny))[:3]):
                    visited.add((nx, ny))
                    q.append((nx, ny))

    fg = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    for y in range(ch):
        for x in range(cw):
            if (x, y) not in visited:
                fg.putpixel((x, y), cell.getpixel((x, y)))

    bbox = fg.getbbox()
    return fg.crop(bbox) if bbox else fg

def build_sit_sheet():
    crouch_clean = extract_crouch_sprite()

    # Lisu sits on the left side of the campfire in CampfireScene.ts:
    # { id: 'lisu', x: GAME_W / 2 - 165, y: 425 }, and spr.setFlipX(true) is called.
    # Therefore, saving facing LEFT ensures flipping in-game makes him face RIGHT toward fire!
    # In crouch_source.png, Lisu is already facing left (slightly front-3/4 left).
    lisu_left = crouch_clean

    target_h = 28
    scale = target_h / float(lisu_left.height)
    new_w = max(1, int(round(lisu_left.width * scale)))
    new_h = target_h
    if new_w > 30:
        new_w = 30

    frame0 = lisu_left.resize((new_w, new_h), Image.Resampling.LANCZOS)
    # Frame 1: breathing (subtle 1px upward offset)
    frame1 = frame0.copy()

    sheet = Image.new("RGBA", (64, 32), (0, 0, 0, 0))
    # Frame 0
    sheet.paste(frame0, (16 - new_w // 2, 30 - new_h), frame0)
    # Frame 1 with 1px breathing bob
    sheet.paste(frame1, (32 + (16 - new_w // 2), 29 - new_h), frame1)

    out_path = os.path.join(SPRITES_DIR, "lisu_sit.png")
    sheet.save(out_path, "PNG")
    print(f"Generated {out_path}: {sheet.size}")


# ==============================================================================
# 4. PORTRAITS, AVATAR & HERO CARD GENERATOR
# ==============================================================================
def build_portraits():
    src_path = os.path.join(SRC_DIR, "crouch_source.png")
    im = Image.open(src_path).convert("RGBA")

    # Crop bust from Frame 1: cowl hood, piercing eyes, mask, binoculars, shoulders
    bust = im.crop((150, 120, 360, 340))
    bw, bh = bust.size

    visited = set()
    q = deque()
    for x in range(bw):
        if is_crouch_bg(*bust.getpixel((x, 0))[:3]): visited.add((x, 0)); q.append((x, 0))
        if is_crouch_bg(*bust.getpixel((x, bh - 1))[:3]): visited.add((x, bh - 1)); q.append((x, bh - 1))
    for y in range(ch := bh):
        if is_crouch_bg(*bust.getpixel((0, y))[:3]): visited.add((0, y)); q.append((0, y))
        if is_crouch_bg(*bust.getpixel((bw - 1, y))[:3]): visited.add((cw := bw, y)); q.append((bw - 1, y))

    while q:
        cx, cy = q.popleft()
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < bw and 0 <= ny < bh and (nx, ny) not in visited:
                if is_crouch_bg(*bust.getpixel((nx, ny))[:3]):
                    visited.add((nx, ny))
                    q.append((nx, ny))

    bust_clean = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    for y in range(bh):
        for x in range(bw):
            if (x, y) not in visited:
                bust_clean.putpixel((x, y), bust.getpixel((x, y)))

    bbox = bust_clean.getbbox()
    if bbox:
        bust_clean = bust_clean.crop(bbox)

    # Composite on dark navy panel background matching all hero portraits
    NAVY = (16, 28, 44)

    for sz in [128, 96, 64]:
        p_canvas = Image.new("RGB", (sz, sz), NAVY)
        target_bh = int(sz * 0.90)
        scale = target_bh / float(bust_clean.height)
        tb_w = int(round(bust_clean.width * scale))
        tb_h = target_bh
        scaled_bust = bust_clean.resize((tb_w, tb_h), Image.Resampling.LANCZOS)
        p_canvas.paste(scaled_bust, ((sz - tb_w) // 2, sz - tb_h), scaled_bust)

        out_path = os.path.join(PORTRAITS_DIR, f"lisu_{sz}.png")
        p_canvas.save(out_path, "PNG")
        print(f"Generated {out_path}: {p_canvas.size}")

    # Avatar 32x32 (phone chat UI)
    avatar = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    av_bust = bust_clean.resize((26, 30), Image.Resampling.LANCZOS)
    avatar.paste(av_bust, (3, 2), av_bust)
    av_path = os.path.join(UI_DIR, "avatar_lisu.png")
    avatar.save(av_path, "PNG")
    print(f"Generated {av_path}: {avatar.size}")

    # Hero Card (307x182) for Analyzer
    # Action scene crop of Lisu crouching on tactical grid
    card_crop = im.crop((40, 110, 460, 505)).convert("RGB")
    card = card_crop.resize((307, 182), Image.Resampling.LANCZOS)
    card_path = os.path.join(CARDS_DIR, "lisu.png")
    card.save(card_path, "PNG")
    print(f"Generated {card_path}: {card.size}")


if __name__ == "__main__":
    print("Building high-detail Lisu assets...")
    build_walk_sheet()
    build_battle_sheet()
    build_sit_sheet()
    build_portraits()
    print("All Lisu assets generated successfully!")
