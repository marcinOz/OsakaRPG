#!/usr/bin/env python3
"""process_daniel_sprites.py - Extract, refine, and generate high-definition pixel art
sprites, portraits, and cards for Daniel ("Danny") in OsakaRPG.

Conforms to engine specifications:
- danny_walk.png: 128x192 RGBA (4 columns x 4 rows, 32x48 per frame)
  Rows: 0=Down, 1=Left, 2=Right, 3=Up
  Cols: 4-frame walk cycle
- danny_battle.png: 512x80 RGBA (8 frames horizontal, 64x80 per frame)
  0=Idle, 1=Idle breath/guard, 2=Windup, 3=Attack, 4=Skill, 5=Hurt, 6=KO, 7=Victory
- danny_sit.png: 64x32 RGBA (2 frames horizontal, 32x32 per frame)
  0=Seated, 1=Seated breath
- Portraits: danny_{128,96,64}.png, avatar_danny.png (32x32)
- Hero Card: card_danny.png (307x182)
"""
import os
import sys
from collections import deque
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT, "art_src", "heroes", "danny")
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
    # Blue grid background has prominent blue and green relative to red
    if b >= 48 and (b - r) >= 26 and (b - g) >= 8:
        return True
    if r < 35 and g < 60 and b < 90 and b > r + 15:
        return True
    return False

def extract_walk_cell(im, x0, y0, x1, y1):
    cell = im.crop((x0, y0, x1, y1))
    cw, ch = cell.size
    visited = set()
    q = deque()

    def is_walk_bg(r, g, b):
        # Grid-blue background only; the dark navy trousers (b < 55) must be kept.
        if b >= 55 and (b - r) >= 28 and (b - g) >= 8: return True
        # Cyan rim-light halo around the character in the source sheet
        if g > 115 and b > 125 and r < 105 and (g - r) > 15 and b > g: return True
        return False

    # Flood fill from perimeter
    for x in range(cw):
        if is_walk_bg(*cell.getpixel((x, 0))[:3]): visited.add((x, 0)); q.append((x, 0))
        if is_walk_bg(*cell.getpixel((x, ch-1))[:3]): visited.add((x, ch-1)); q.append((x, ch-1))
    for y in range(ch):
        if is_walk_bg(*cell.getpixel((0, y))[:3]): visited.add((0, y)); q.append((0, y))
        if is_walk_bg(*cell.getpixel((cw-1, y))[:3]): visited.add((cw-1, y)); q.append((cw-1, y))

    while q:
        cx, cy = q.popleft()
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < cw and 0 <= ny < ch and (nx, ny) not in visited:
                if is_bg_pixel := is_walk_bg(*cell.getpixel((nx, ny))[:3]):
                    visited.add((nx, ny))
                    q.append((nx, ny))

    # Mask foreground
    fg = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    for y in range(ch):
        for x in range(cw):
            if (x, y) not in visited:
                r, g, b = cell.getpixel((x, y))[:3]
                r, g, b = cell.getpixel((x, y))[:3]
                fg.putpixel((x, y), (r, g, b, 255))
    return fg

def build_walk_sheet():
    src_path = os.path.join(SRC_DIR, "walk_source.jpg")
    im = Image.open(src_path).convert("RGB")

    # NOTE: in the source sheet the row captioned "LEFT PROFILE" actually faces
    # image-RIGHT and "RIGHT PROFILE" faces image-LEFT. The game needs
    # row 1 = faces left, row 2 = faces right, so they are swapped here.
    ROWS = {
        'down':  (86, 275),
        'right': (326, 515),   # source "LEFT PROFILE" (faces right)
        'left':  (562, 764),   # source "RIGHT PROFILE" (faces left)
        'up':    (811, 1005),
    }
    order = ['down', 'left', 'right', 'up']  # game rows 0..3

    sheet = Image.new("RGBA", (128, 192), (0, 0, 0, 0))
    fw, fh = 32, 48
    scale = 42.0 / 185.0
    ground_y = 45

    for r_idx, name in enumerate(order):
        y0, y1 = ROWS[name]
        for c in range(4):
            fg = extract_walk_cell(im, c * 171, y0, (c + 1) * 171, y1)
            bbox = fg.getbbox()
            fg = fg.crop(bbox)  # tight crop; feet at bottom edge
            # spine = mean x of head/torso (top 40% of the sprite)
            top = int(fg.height * 0.4)
            xs = [x for y in range(top) for x in range(fg.width) if fg.getpixel((x, y))[3] > 0]
            spine = sum(xs) / len(xs) if xs else fg.width / 2.0
            sw, sh = max(1, round(fg.width * scale)), max(1, round(fg.height * scale))
            sc = fg.resize((sw, sh), Image.Resampling.LANCZOS)
            dx = c * fw + 16 - round(spine * scale)
            dy = r_idx * fh + ground_y - sh
            sheet.paste(sc, (dx, dy), sc)

    out_path = os.path.join(SPRITES_DIR, "danny_walk.png")
    sheet.save(out_path, "PNG")
    print(f"Generated {out_path}: {sheet.size}")


# ==============================================================================
# 2. BATTLE SHEET GENERATOR
# ==============================================================================
def is_bat_bg(r, g, b):
    # Dark slate background
    if r < 40 and g < 45 and b < 55:
        return True
    # Faint dashed grid lines
    if r < 90 and g < 95 and b < 110 and abs(r - g) < 15 and abs(g - b) < 20:
        return True
    return False

def extract_battle_cell(im, idx):
    # Each frame is 128 wide; crop inside borders to avoid vertical dividing lines
    w, h = im.size
    x0 = idx * 128 + 2
    x1 = (idx + 1) * 128 - 2
    cell = im.crop((x0, 0, x1, h))
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
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
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
                # defringe
                if r < 50 and g < 55 and b < 65:
                    continue
                fg.putpixel((x, y), (r, g, b, 255))

    bbox = fg.getbbox()
    if bbox:
        return fg.crop(bbox)
    return fg

def build_battle_sheet():
    src_path = os.path.join(SRC_DIR, "battle_source.png")
    im = Image.open(src_path).convert("RGBA")

    # 8 frames:
    # 0: Idle stand
    # 1: Idle breath / Guard
    # 2: Windup (Guard)
    # 3: Attack (Punch)
    # 4: Skill (Hex Shield Barrier)
    # 5: Hurt (Recoil)
    # 6: KO (Flat on floor)
    # 7: Victory (Double Bicep flex)
    sheet = Image.new("RGBA", (512, 80), (0, 0, 0, 0))

    frame_w, frame_h = 64, 80
    ground_y = 75 # feet baseline

    # Frame mapping from raw source indexes:
    # Source frames:
    # 0 = Idle stand
    # 1 = Guard
    # 2 = Punch
    # 3 = Shield
    # 4 = Hurt
    # 5 = KO
    # 6 = Victory
    # 7 = Defeat
    raw_frames = [extract_battle_cell(im, i) for i in range(8)]

    # We map to the engine's 8 frames:
    # idx 0: raw 0 (Idle)
    # idx 1: raw 1 (Idle ready / Guard subtle)
    # idx 2: raw 1 (Windup guard)
    # idx 3: raw 2 (Punch attack)
    # idx 4: raw 3 (Shield skill)
    # idx 5: raw 4 (Hurt)
    # idx 6: raw 5 (KO flat on ground)
    # idx 7: raw 6 (Victory flex)
    mapped_source_indices = [0, 1, 1, 2, 3, 4, 5, 6]

    for out_idx, src_idx in enumerate(mapped_source_indices):
        char_crop = raw_frames[src_idx]
        orig_w, orig_h = char_crop.size

        if src_idx == 5: # KO frame (horizontal on ground)
            target_w = min(60, orig_w)
            scale = target_w / float(orig_w)
            new_w = target_w
            new_h = max(1, int(round(orig_h * scale)))
            scaled = char_crop.resize((new_w, new_h), Image.Resampling.LANCZOS)
            dst_x = out_idx * frame_w + (frame_w - new_w) // 2
            dst_y = ground_y - new_h
        else:
            # Standing combat pose
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

    out_path = os.path.join(SPRITES_DIR, "danny_battle.png")
    sheet.save(out_path, "PNG")
    print(f"Generated {out_path}: {sheet.size}")


# ==============================================================================
# 3. CAMPFIRE SIT SHEET GENERATOR
# ==============================================================================
def is_camp_bg(r, g, b):
    # Light grey grid background
    diff = max(abs(r - g), abs(g - b), abs(r - b))
    return r > 165 and g > 165 and b > 165 and diff < 15

def build_sit_sheet():
    src_path = os.path.join(SRC_DIR, "campfire_source.png")
    im = Image.open(src_path).convert("RGBA")

    # Crop panel 0 containing Danny sitting on log holding shaker
    # Daniel's body is roughly x in [70, 320], y in [100, 480]
    cell = im.crop((70, 100, 320, 480))
    cw, ch = cell.size
    visited = set()
    q = deque()

    for x in range(cw):
        if is_camp_bg(*cell.getpixel((x, 0))[:3]): visited.add((x, 0)); q.append((x, 0))
        if is_camp_bg(*cell.getpixel((x, ch-1))[:3]): visited.add((x, ch-1)); q.append((x, ch-1))
    for y in range(ch):
        if is_camp_bg(*cell.getpixel((0, y))[:3]): visited.add((0, y)); q.append((0, y))
        if is_camp_bg(*cell.getpixel((cw-1, y))[:3]): visited.add((cw-1, y)); q.append((cw-1, y))

    while q:
        cx, cy = q.popleft()
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < cw and 0 <= ny < ch and (nx, ny) not in visited:
                if is_camp_bg(*cell.getpixel((nx, ny))[:3]):
                    visited.add((nx, ny))
                    q.append((nx, ny))

    fg = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    for y in range(ch):
        for x in range(cw):
            if (x, y) not in visited:
                fg.putpixel((x, y), cell.getpixel((x, y)))

    bbox = fg.getbbox()
    danny_sit = fg.crop(bbox) if bbox else fg

    # Danny in campfire_source faces right.
    # CampfireScene.ts applies spr.setFlipX(true) to Danny, so saving facing LEFT ensures
    # flipping makes him face right toward the fire!
    danny_left = danny_sit.transpose(Image.FLIP_LEFT_RIGHT)

    # Scale to 32x32 per frame (total 64x32)
    # Character seated height is ~28px
    target_h = 28
    scale = target_h / float(danny_left.height)
    new_w = max(1, int(round(danny_left.width * scale)))
    new_h = target_h
    if new_w > 30: new_w = 30

    frame0 = danny_left.resize((new_w, new_h), Image.Resampling.LANCZOS)

    # Frame 1: breathing (subtle 1px upward shift of chest/head)
    frame1 = frame0.copy()

    sheet = Image.new("RGBA", (64, 32), (0, 0, 0, 0))
    # Place frame 0
    sheet.paste(frame0, (16 - new_w // 2, 30 - new_h), frame0)
    # Place frame 1 with subtle breathing bob (-1px)
    sheet.paste(frame1, (32 + (16 - new_w // 2), 29 - new_h), frame1)

    out_path = os.path.join(SPRITES_DIR, "danny_sit.png")
    sheet.save(out_path, "PNG")
    print(f"Generated {out_path}: {sheet.size}")


# ==============================================================================
# 4. PORTRAITS, AVATAR & HERO CARD GENERATOR
# ==============================================================================
def build_portraits():
    # We take the high-detail bust crop from campfire_source (very clean, front-3/4 face with beard, haircut & vest)
    src_path = os.path.join(SRC_DIR, "campfire_source.png")
    im = Image.open(src_path).convert("RGBA")

    # Crop head and shoulders of Danny
    # Danny's bust in campfire_source: x in [110, 240], y in [80, 230]
    bust = im.crop((110, 80, 240, 230))
    bw, bh = bust.size

    # Isolate from light grey background
    visited = set()
    q = deque()
    for x in range(bw):
        if is_camp_bg(*bust.getpixel((x, 0))[:3]): visited.add((x, 0)); q.append((x, 0))
        if is_camp_bg(*bust.getpixel((x, bh-1))[:3]): visited.add((x, bh-1)); q.append((x, bh-1))
    for y in range(bh):
        if is_camp_bg(*bust.getpixel((0, y))[:3]): visited.add((0, y)); q.append((0, y))
        if is_camp_bg(*bust.getpixel((bw-1, y))[:3]): visited.add((bw-1, y)); q.append((bw-1, y))

    while q:
        cx, cy = q.popleft()
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < bw and 0 <= ny < bh and (nx, ny) not in visited:
                if is_camp_bg(*bust.getpixel((nx, ny))[:3]):
                    visited.add((nx, ny))
                    q.append((nx, ny))

    bust_clean = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    for y in range(bh):
        for x in range(bw):
            if (x, y) not in visited:
                bust_clean.putpixel((x, y), bust.getpixel((x, y)))

    # Composite on dark navy panel background matching other hero portraits
    # Navy background: (12, 33, 52)
    NAVY = (16, 28, 44)

    for sz in [128, 96, 64]:
        p_canvas = Image.new("RGB", (sz, sz), NAVY)
        # Scale bust to fill ~85% of portrait
        target_bh = int(sz * 0.90)
        scale = target_bh / float(bh)
        tb_w = int(round(bw * scale))
        tb_h = target_bh
        scaled_bust = bust_clean.resize((tb_w, tb_h), Image.Resampling.LANCZOS)
        p_canvas.paste(scaled_bust, ((sz - tb_w) // 2, sz - tb_h), scaled_bust)

        out_path = os.path.join(PORTRAITS_DIR, f"danny_{sz}.png")
        p_canvas.save(out_path, "PNG")
        print(f"Generated {out_path}: {p_canvas.size}")

    # Avatar 32x32 (phone chat UI)
    avatar = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    av_bust = bust_clean.resize((28, 30), Image.Resampling.LANCZOS)
    avatar.paste(av_bust, (2, 2), av_bust)
    av_path = os.path.join(UI_DIR, "avatar_danny.png")
    avatar.save(av_path, "PNG")
    print(f"Generated {av_path}: {avatar.size}")

    # Hero Card (307x182) for Analyzer
    # Take the campfire scene crop with Daniel seated holding shaker
    camp_crop = im.crop((30, 70, 480, 520))
    card = Image.new("RGB", (307, 182), NAVY)
    # Fit scene into card
    card_scene = camp_crop.resize((307, 182), Image.Resampling.LANCZOS)
    card.paste(card_scene, (0, 0))
    card_path = os.path.join(CARDS_DIR, "danny.png")
    card.save(card_path, "PNG")
    print(f"Generated {card_path}: {card.size}")


if __name__ == "__main__":
    print("Building high-detail Daniel assets...")
    build_walk_sheet()
    build_battle_sheet()
    build_sit_sheet()
    build_portraits()
    print("All Daniel assets generated successfully!")
