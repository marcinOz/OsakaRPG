#!/usr/bin/env python3
"""process_oziem_sprites.py - Extract, refine, and generate high-definition pixel art
sprites, portraits, and cards for Oziem ("The Bushcraft Expert") in OsakaRPG.

Conforms to engine specifications:
- oziem_walk.png: 128x192 RGBA (4 columns x 4 rows, 32x48 per frame)
  Rows: 0=Down, 1=Left, 2=Right, 3=Up
  Cols: 4-frame walk cycle
- oziem_battle.png: 512x80 RGBA (8 frames horizontal, 64x80 per frame)
  0=Idle, 1=Idle ready/breath, 2=Windup, 3=Attack, 4=Skill (Herbal Medicine), 5=Hurt, 6=KO, 7=Victory
- oziem_sit.png: 64x32 RGBA (2 frames horizontal, 32x32 per frame)
  0=Seated, 1=Seated breath (facing left toward campfire)
- Portraits: oziem_{128,96,64}.png, avatar_oziem.png (32x32)
- Hero Card: card_oziem -> cards/oziem.png (307x182)
"""
import os
import sys
from collections import deque
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT, "art_src", "heroes", "oziem")
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
    # Dark cell borders
    if r < 20 and g < 40 and b < 55:
        return True
    # Blue/teal grid and world map background
    if b >= 40 and (b - r) >= 12 and (g - r) >= 8:
        return True
    if g >= 40 and (g - r) >= 15:
        return True
    if r < 40 and g < 60 and b < 70 and (b - r) > 10:
        return True
    return False

def extract_walk_cell(im, x0, y0, x1, y1):
    cell = im.crop((x0, y0, x1, y1))
    cw, ch = cell.size
    visited = set()
    q = deque()

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

    fg = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    for y in range(ch):
        for x in range(cw):
            if (x, y) not in visited:
                r, g, b = cell.getpixel((x, y))[:3]
                if not is_walk_bg(r, g, b):
                    # Filter out top-left corner label text (e.g., 'LEFT', 'RIGHT', 'BACK')
                    if x < 45 and y < 30 and (b > 60 or g > 60):
                        continue
                    fg.putpixel((x, y), (r, g, b, 255))

    bbox = fg.getbbox()
    return fg.crop(bbox) if bbox else fg

def build_walk_sheet():
    src_path = os.path.join(SRC_DIR, "walk_source.png")
    im = Image.open(src_path).convert("RGBA")

    cols = [24, 186, 349, 513, 677, 841, 1001]
    rows = [43, 204, 372, 540]

    # Pre-extract all frames for each row
    front_raw = [extract_walk_cell(im, cols[c] + 2, rows[0] + 2, cols[c + 1] - 2, rows[1] - 2) for c in range(6)]
    left_raw = [extract_walk_cell(im, cols[c] + 2, rows[1] + 2, cols[c + 1] - 2, rows[2] - 2) for c in range(3)]
    right_raw = [extract_walk_cell(im, cols[c] + 2, rows[1] + 2, cols[c + 1] - 2, rows[2] - 2) for c in range(3, 6)]
    back_raw = [extract_walk_cell(im, cols[c] + 2, rows[2] + 2, cols[c + 1] - 2, rows[3] - 2) for c in range(6)]

    # Assemble 4-frame walk cycles:
    # Down: [step_L, idle/passing, step_R, idle/passing]
    down_frames = [front_raw[1], front_raw[0], front_raw[4], front_raw[0]]
    # Left: ping-pong loop [0, 1, 2, 1]
    left_frames = [left_raw[0], left_raw[1], left_raw[2], left_raw[1]]
    # Right: ping-pong loop [0, 1, 2, 1]
    right_frames = [right_raw[0], right_raw[1], right_raw[2], right_raw[1]]
    # Up: [step_L, idle/passing, step_R, idle/passing]
    up_frames = [back_raw[1], back_raw[0], back_raw[4], back_raw[0]]

    order = [down_frames, left_frames, right_frames, up_frames]

    sheet = Image.new("RGBA", (128, 192), (0, 0, 0, 0))
    fw, fh = 32, 48
    scale = 42.0 / 150.0  # Scale ~150px source character down to ~42px height in 48px box
    ground_y = 45

    for r_idx, frames in enumerate(order):
        for c_idx, fg in enumerate(frames):
            top = int(fg.height * 0.4)
            xs = [x for y in range(top) for x in range(fg.width) if fg.getpixel((x, y))[3] > 0]
            spine = sum(xs) / len(xs) if xs else fg.width / 2.0
            sw = max(1, round(fg.width * scale))
            sh = max(1, round(fg.height * scale))
            sc = fg.resize((sw, sh), Image.Resampling.LANCZOS)
            dx = c_idx * fw + 16 - round(spine * scale)
            dy = r_idx * fh + ground_y - sh
            sheet.paste(sc, (dx, dy), sc)

    out_path = os.path.join(SPRITES_DIR, "oziem_walk.png")
    sheet.save(out_path, "PNG")
    print(f"Generated {out_path}: {sheet.size}")


# ==============================================================================
# 2. BATTLE SHEET GENERATOR
# ==============================================================================
def is_bat_bg(r, g, b):
    # Dark cell borders
    if r < 15 and g < 25 and b < 40:
        return True
    # Grid lines and background
    if b >= 45 and (b - r) >= 15 and (g - r) >= 8:
        return True
    if r < 30 and g < 55 and b < 75:
        return True
    if abs(r - 35) < 15 and abs(g - 65) < 20 and abs(b - 80) < 20:
        return True
    return False

def extract_battle_cell(im, idx):
    x0 = idx * 128 + 2
    x1 = (idx + 1) * 128 - 2
    y0 = 34
    y1 = 296
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
                if not is_bat_bg(r, g, b):
                    fg.putpixel((x, y), (r, g, b, 255))

    bbox = fg.getbbox()
    return fg.crop(bbox) if bbox else fg

def build_battle_sheet():
    src_path = os.path.join(SRC_DIR, "battle_source.png")
    im = Image.open(src_path).convert("RGBA")

    raw_frames = [extract_battle_cell(im, i) for i in range(8)]
    # raw_frames:
    # 0 = IDLE 1 (Loop frame 1)
    # 1 = IDLE 2 (Ready stance)
    # 2 = ATK PRE (Two-handed high branch windup)
    # 3 = ATK STRIKE (Slash arc)
    # 4 = ATK RECV
    # 5 = HERBS (Kneeling with mortar & pestle - Bushcraft Healing Skill!)
    # 6 = HURT (Pain recoil & red aura)
    # 7 = VICTORY (Staff raised high)

    # Derive KO frame from Hurt pose:
    # Rotated horizontally, collapsed on ground baseline, darkened slightly
    hurt_raw = raw_frames[6]
    ko_rot = hurt_raw.rotate(80, expand=True, resample=Image.Resampling.BILINEAR)
    ko_crop = ko_rot.crop(ko_rot.getbbox())
    enhancer = ImageEnhance.Brightness(ko_crop)
    ko_dark = enhancer.enhance(0.75)

    # Engine 8-state mapping:
    # 0: Idle0, 1: Idle1, 2: Windup, 3: Attack, 4: Skill, 5: Hurt, 6: KO, 7: Victory
    mapped_frames = [
        ("idle0", raw_frames[0]),
        ("idle1", raw_frames[1]),
        ("windup", raw_frames[2]),
        ("attack", raw_frames[3]),
        ("skill", raw_frames[5]),
        ("hurt", raw_frames[6]),
        ("ko", ko_dark),
        ("victory", raw_frames[7]),
    ]

    sheet = Image.new("RGBA", (512, 80), (0, 0, 0, 0))
    frame_w, frame_h = 64, 80
    ground_y = 75

    for out_idx, (name, char_crop) in enumerate(mapped_frames):
        orig_w, orig_h = char_crop.size

        if name == "ko":
            target_w = min(60, orig_w)
            scale = target_w / float(orig_w)
            new_w = target_w
            new_h = max(1, int(round(orig_h * scale)))
            scaled = char_crop.resize((new_w, new_h), Image.Resampling.LANCZOS)
            dst_x = out_idx * frame_w + (frame_w - new_w) // 2
            dst_y = ground_y - new_h
        elif name == "skill":
            # Kneeling pose scaled proportionally to standard 72px standing height
            target_char_h = 56
            scale = target_char_h / float(orig_h)
            new_h = target_char_h
            new_w = max(1, int(round(orig_w * scale)))
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

    out_path = os.path.join(SPRITES_DIR, "oziem_battle.png")
    sheet.save(out_path, "PNG")
    print(f"Generated {out_path}: {sheet.size}")


# ==============================================================================
# 3. CAMPFIRE SIT SHEET GENERATOR
# ==============================================================================
def is_sit_bg(r, g, b):
    # Dark ambient night
    if r < 18 and g < 28 and b < 38:
        return True
    if r < 10 and g < 10 and b < 10:
        return True
    return False

def build_sit_sheet():
    src_path = os.path.join(SRC_DIR, "campfire_source.png")
    im = Image.open(src_path).convert("RGBA")

    # In Panel 2, Oziem sits on the log looking forward-left toward the campfire
    # CampfireScene.ts has flipX: false for right-side heroes (including Oziem),
    # so facing left naturally looks right into the fire!
    cell = im.crop((650, 80, 920, 505))
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
                if not is_sit_bg(r, g, b):
                    fg.putpixel((x, y), (r, g, b, 255))

    bbox = fg.getbbox()
    oziem_sit = fg.crop(bbox) if bbox else fg

    # Target height 28px inside 32x32 frame
    target_h = 28
    scale = target_h / float(oziem_sit.height)
    new_w = max(1, int(round(oziem_sit.width * scale)))
    new_h = target_h
    if new_w > 30:
        new_w = 30

    frame0 = oziem_sit.resize((new_w, new_h), Image.Resampling.LANCZOS)
    # Frame 1: breathing bob (1px upward shift)
    frame1 = frame0.copy()

    sheet = Image.new("RGBA", (64, 32), (0, 0, 0, 0))
    # Frame 0
    sheet.paste(frame0, (16 - new_w // 2, 30 - new_h), frame0)
    # Frame 1 with 1px breathing bob
    sheet.paste(frame1, (32 + (16 - new_w // 2), 29 - new_h), frame1)

    out_path = os.path.join(SPRITES_DIR, "oziem_sit.png")
    sheet.save(out_path, "PNG")
    print(f"Generated {out_path}: {sheet.size}")


# ==============================================================================
# 4. PORTRAITS, AVATAR & HERO CARD GENERATOR
# ==============================================================================
def build_portraits():
    src_path = os.path.join(SRC_DIR, "campfire_source.png")
    im = Image.open(src_path).convert("RGBA")

    # High-detail bust crop from Panel 2
    bust_crop = im.crop((680, 80, 885, 330))
    bw, bh = bust_crop.size

    visited = set()
    q = deque()
    for x in range(bw):
        if is_sit_bg(*bust_crop.getpixel((x, 0))[:3]): visited.add((x, 0)); q.append((x, 0))
        if is_sit_bg(*bust_crop.getpixel((x, bh - 1))[:3]): visited.add((x, bh - 1)); q.append((x, bh - 1))
    for y in range(bh):
        if is_sit_bg(*bust_crop.getpixel((0, y))[:3]): visited.add((0, y)); q.append((0, y))
        if is_sit_bg(*bust_crop.getpixel((bw - 1, y))[:3]): visited.add((bw - 1, y)); q.append((bw - 1, y))

    while q:
        cx, cy = q.popleft()
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < bw and 0 <= ny < bh and (nx, ny) not in visited:
                if is_sit_bg(*bust_crop.getpixel((nx, ny))[:3]):
                    visited.add((nx, ny))
                    q.append((nx, ny))

    bust_clean = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    for y in range(bh):
        for x in range(bw):
            if (x, y) not in visited:
                r, g, b = bust_crop.getpixel((x, y))[:3]
                if not is_sit_bg(r, g, b):
                    bust_clean.putpixel((x, y), (r, g, b, 255))

    bbox = bust_clean.getbbox()
    bust = bust_clean.crop(bbox) if bbox else bust_clean

    # Composite on dark navy panel background matching all hero portraits
    NAVY = (16, 28, 44)

    for sz in [128, 96, 64]:
        p_canvas = Image.new("RGB", (sz, sz), NAVY)
        target_bh = int(sz * 0.90)
        scale = target_bh / float(bust.height)
        tb_w = int(round(bust.width * scale))
        tb_h = target_bh
        scaled_bust = bust.resize((tb_w, tb_h), Image.Resampling.LANCZOS)
        p_canvas.paste(scaled_bust, ((sz - tb_w) // 2, sz - tb_h), scaled_bust)

        out_path = os.path.join(PORTRAITS_DIR, f"oziem_{sz}.png")
        p_canvas.save(out_path, "PNG")
        print(f"Generated {out_path}: {p_canvas.size}")

    # Avatar 32x32 for phone messenger UI
    avatar = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    av_bust = bust.resize((26, 29), Image.Resampling.LANCZOS)
    avatar.paste(av_bust, (3, 2), av_bust)
    av_path = os.path.join(UI_DIR, "avatar_oziem.png")
    avatar.save(av_path, "PNG")
    print(f"Generated {av_path}: {avatar.size}")

    # Hero Card (307x182) for Analyzer Scene
    # Full campfire scene with fire, whittling survivor, backpack, rope, and multitool
    sim = Image.open(src_path).convert("RGB")
    card_crop = sim.crop((15, 60, 505, 525))
    card = card_crop.resize((307, 182), Image.Resampling.LANCZOS)
    card_path = os.path.join(CARDS_DIR, "oziem.png")
    card.save(card_path, "PNG")
    print(f"Generated {card_path}: {card.size}")


if __name__ == "__main__":
    print("Building high-detail Oziem assets...")
    build_walk_sheet()
    build_battle_sheet()
    build_sit_sheet()
    build_portraits()
    print("All Oziem assets generated successfully!")
