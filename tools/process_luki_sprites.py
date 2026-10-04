#!/usr/bin/env python3
"""process_luki_sprites.py - Build Łuki's high-detail sprites, portraits and card.

Same engine contract as process_daniel_sprites.py:
- luki_walk.png   128x192 (4x4 of 32x48)   rows: 0=Down 1=Left 2=Right 3=Up
- luki_battle.png 512x80  (8x 64x80)       Idle, Idle2, Windup, Attack, Skill, Hurt, KO, Victory
- luki_sit.png    64x32   (2x 32x32)       faces LEFT (CampfireScene does not flip Łuki)
- luki_{128,96,64}.png, avatar_luki.png (32x32), cards/luki.png (307x182)

Source note: in the walk sheet BOTH profile rows face LEFT. Right row = mirrored copy.

Usage: python3 tools/process_luki_sprites.py [--debug]
"""
import os
import sys
from collections import deque
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT, "art_src", "heroes", "luki")
SPRITES_DIR = os.path.join(ROOT, "public", "assets", "sprites")
PORTRAITS_DIR = os.path.join(ROOT, "public", "assets", "portraits")
UI_DIR = os.path.join(ROOT, "public", "assets", "ui")
CARDS_DIR = os.path.join(ROOT, "public", "assets", "cards")
SCRATCH_DIR = os.path.join(ROOT, "art_src", "scratch")
NAVY = (16, 28, 44)


# ------------------------------------------------------------------ helpers
def flood_cutout(img, is_bg, seeds_all_border=True):
    """Return RGBA with border-connected background removed."""
    img = img.convert("RGB")
    w, h = img.size
    px = img.load()
    bg = [[False] * w for _ in range(h)]
    q = deque()

    def seed(x, y):
        if not bg[y][x] and is_bg(*px[x, y]):
            bg[y][x] = True
            q.append((x, y))

    for x in range(w):
        seed(x, 0)
        seed(x, h - 1)
    for y in range(h):
        seed(0, y)
        seed(w - 1, y)
    while q:
        x, y = q.popleft()
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and not bg[ny][nx] and is_bg(*px[nx, ny]):
                bg[ny][nx] = True
                q.append((nx, ny))
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    op = out.load()
    for y in range(h):
        for x in range(w):
            if not bg[y][x]:
                r, g, b = px[x, y]
                op[x, y] = (r, g, b, 255)
    return out


def components(img, min_px=1):
    """8-connected components of opaque pixels -> list of (pixels list)."""
    w, h = img.size
    a = img.getchannel("A").load()
    seen = [[False] * w for _ in range(h)]
    comps = []
    for y in range(h):
        for x in range(w):
            if a[x, y] and not seen[y][x]:
                seen[y][x] = True
                stack = [(x, y)]
                pts = []
                while stack:
                    cx, cy = stack.pop()
                    pts.append((cx, cy))
                    for dx in (-1, 0, 1):
                        for dy in (-1, 0, 1):
                            nx, ny = cx + dx, cy + dy
                            if 0 <= nx < w and 0 <= ny < h and a[nx, ny] and not seen[ny][nx]:
                                seen[ny][nx] = True
                                stack.append((nx, ny))
                if len(pts) >= min_px:
                    comps.append(pts)
    return comps


def keep_largest(img):
    comps = components(img)
    if not comps:
        return img
    big = max(comps, key=len)
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    src, dst = img.load(), out.load()
    for x, y in big:
        dst[x, y] = src[x, y]
    return out


def crisp_resize(img, size):
    """LANCZOS resize (premultiplied by Pillow) then binarize alpha for a crisp pixel edge."""
    r = img.resize(size, Image.Resampling.LANCZOS)
    a = r.getchannel("A").point(lambda v: 255 if v >= 110 else 0)
    r.putalpha(a)
    return r


def trim(img):
    bb = img.getbbox()
    return img.crop(bb) if bb else img


# --------------------------------------------------------------------- walk
def walk_bg(r, g, b):
    if b >= 50 and (b - r) >= 24 and (b - g) >= 6:
        return True
    # cyan glow in the top-right of the sheet
    if g > 110 and b > 120 and r < 110 and (g - r) > 15 and b >= g:
        return True
    return False


def build_walk_sheet(debug=False):
    im = Image.open(os.path.join(SRC_DIR, "walk_source.png")).convert("RGB")
    col_x = [0, 256, 512, 768, 1024]
    row_y = [66, 301, 529, 765, 1024]
    PAD = 6

    frames = {}
    for r in range(4):
        for c in range(4):
            cell = im.crop((col_x[c] + PAD, row_y[r] + PAD, col_x[c + 1] - PAD, row_y[r + 1] - PAD))
            fg = keep_largest(flood_cutout(cell, walk_bg))
            frames[(r, c)] = trim(fg)

    # Source rows: 0 down, 1 left-facing, 2 left-facing (ALSO left!), 3 up.
    # Game rows: 0 down, 1 left, 2 right (= mirrored source row 2), 3 up.
    plan = [(0, False), (1, False), (2, True), (3, False)]

    heights = sorted(f.height for f in frames.values())
    scale = 42.0 / heights[len(heights) // 2]
    sheet = Image.new("RGBA", (128, 192), (0, 0, 0, 0))
    fw, fh, ground_y = 32, 48, 46

    for out_row, (src_row, mirror) in enumerate(plan):
        for c in range(4):
            fg = frames[(src_row, c)]
            if mirror:
                fg = fg.transpose(Image.FLIP_LEFT_RIGHT)
            sw, sh = max(1, round(fg.width * scale)), max(1, round(fg.height * scale))
            sc = crisp_resize(fg, (sw, sh))
            # align by spine (opaque mean x of top 40%)
            top = max(1, int(sc.height * 0.4))
            a = sc.getchannel("A").load()
            xs = [x for y in range(top) for x in range(sc.width) if a[x, y]]
            spine = sum(xs) / len(xs) if xs else sc.width / 2
            dx = c * fw + 16 - round(spine)
            dx = max(c * fw, min(dx, c * fw + fw - sc.width))
            dy = out_row * fh + ground_y - sh
            sheet.paste(sc, (dx, dy), sc)

    out = os.path.join(SPRITES_DIR, "luki_walk.png")
    sheet.save(out)
    print("Generated", out, sheet.size)


# ------------------------------------------------------------------- battle
def build_battle_sheet():
    im = Image.open(os.path.join(SRC_DIR, "battle_source.png")).convert("RGB")
    bgc = im.getpixel((5, 200))

    def is_bg(r, g, b):
        return abs(r - bgc[0]) + abs(g - bgc[1]) + abs(b - bgc[2]) < 40

    # restrict to the art band (excludes title and captions)
    band = im.crop((0, 95, im.width, 345))
    cut = flood_cutout(band, is_bg)
    comps = [c for c in components(cut) if len(c) >= 25]

    # pose anchors (centroid x) in source order; KO is separated by low y
    centers = {"idle": 75, "windup": 170, "attack": 305, "skill": 535, "hurt": 720, "victory": 950}
    groups = {k: [] for k in list(centers) + ["ko"]}
    for pts in comps:
        cx = sum(p[0] for p in pts) / len(pts)
        cy = sum(p[1] for p in pts) / len(pts)
        if cx > 740 and cx < 900 and cy > 190:   # lying figure + its buoy (band-relative y)
            key = "ko"
        else:
            key = min(centers, key=lambda k: abs(centers[k] - cx))
        groups[key].append(pts)

    poses = {}
    for key, glist in groups.items():
        layer = Image.new("RGBA", cut.size, (0, 0, 0, 0))
        src, dst = cut.load(), layer.load()
        for pts in glist:
            for x, y in pts:
                dst[x, y] = src[x, y]
        poses[key] = trim(layer)
        print(" pose", key, poses[key].size)

    standing = ["idle", "windup", "attack", "hurt"]
    base = 72.0 / max(poses[k].height for k in standing)

    def scaled(key, extra_h=0):
        p = poses[key]
        s = base
        if key == "victory":
            s = min(base, 76.0 / p.height)
        if p.width * s > 62:
            s = 62.0 / p.width
        if p.height * s > 76:
            s = 76.0 / p.height
        return crisp_resize(p, (max(1, round(p.width * s)), max(1, round(p.height * s) + extra_h)))

    order = ["idle", "idle2", "windup", "attack", "skill", "hurt", "ko", "victory"]
    sheet = Image.new("RGBA", (512, 80), (0, 0, 0, 0))
    ground_y = 77
    for i, key in enumerate(order):
        sp = scaled("idle", 1) if key == "idle2" else scaled(key)
        dx = i * 64 + (64 - sp.width) // 2
        dy = ground_y - sp.height
        sheet.paste(sp, (dx, max(0, dy)), sp)

    out = os.path.join(SPRITES_DIR, "luki_battle.png")
    sheet.save(out)
    print("Generated", out, sheet.size)


# ----------------------------------------------------------------- campfire
def camp_cut(box):
    im = Image.open(os.path.join(SRC_DIR, "campfire_source.png")).convert("RGB")
    bgc = im.getpixel((20, 20))

    def is_bg(r, g, b):
        # background + soft ground shadow (all very dark, low saturation)
        return max(r, g, b) < 52 and (max(r, g, b) - min(r, g, b)) < 22

    return keep_largest(flood_cutout(im.crop(box), is_bg))


def build_sit_sheet():
    # Right figure (reclining) already faces LEFT, which is what CampfireScene expects for Łuki.
    fig = trim(camp_cut((550, 295, 965, 675)))
    s = min(30.0 / fig.width, 28.0 / fig.height)
    f0 = crisp_resize(fig, (max(1, round(fig.width * s)), max(1, round(fig.height * s))))
    sheet = Image.new("RGBA", (64, 32), (0, 0, 0, 0))
    sheet.paste(f0, (16 - f0.width // 2, 30 - f0.height), f0)
    sheet.paste(f0, (32 + 16 - f0.width // 2, 29 - f0.height), f0)
    out = os.path.join(SPRITES_DIR, "luki_sit.png")
    sheet.save(out)
    print("Generated", out, sheet.size)


def build_portraits():
    bust = camp_cut((165, 295, 335, 465))
    for sz in (128, 96, 64):
        canvas = Image.new("RGB", (sz, sz), NAVY)
        th = int(sz * 0.92)
        sc = bust.resize((round(bust.width * th / bust.height), th), Image.Resampling.LANCZOS)
        canvas.paste(sc, ((sz - sc.width) // 2, sz - th), sc)
        p = os.path.join(PORTRAITS_DIR, f"luki_{sz}.png")
        canvas.save(p)
        print("Generated", p)

    av = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    a = bust.resize((28, 28), Image.Resampling.LANCZOS)
    av.paste(a, (2, 4), a)
    ap = os.path.join(UI_DIR, "avatar_luki.png")
    av.save(ap)
    print("Generated", ap)

    im = Image.open(os.path.join(SRC_DIR, "campfire_source.png")).convert("RGB")
    card = im.crop((110, 250, 960, 754)).resize((307, 182), Image.Resampling.LANCZOS)
    cp = os.path.join(CARDS_DIR, "luki.png")
    card.save(cp)
    print("Generated", cp, card.size)


if __name__ == "__main__":
    for d in (SPRITES_DIR, PORTRAITS_DIR, UI_DIR, CARDS_DIR, SCRATCH_DIR):
        os.makedirs(d, exist_ok=True)
    build_walk_sheet()
    build_battle_sheet()
    build_sit_sheet()
    build_portraits()
    print("Łuki assets done.")
