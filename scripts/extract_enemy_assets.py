#!/usr/bin/env python3
"""extract_enemy_assets.py - Extracts all 11 enemy spritesheets from the pixel art showcase graphic.
Removes card framing, borders, F1/F2 watermarks, and background fill to create clean transparent RGBA spritesheets.
"""
import os
from collections import deque
from PIL import Image

SRC_GRAPHIC = "/Users/marcin.oziemski/.gemini/antigravity/brain/80bbfb60-6c92-4378-b508-764f59af633e/.user_uploaded/media_1791111593124.png"
OUT_DIR = "public/assets/enemies"

os.makedirs(OUT_DIR, exist_ok=True)

ENEMY_CONFIGS = [
    {
        'id': 'bolKregoslupa',
        'target_sz': 96,
        'f1_box': (18, 39, 135, 155),
        'f2_box': (148, 39, 265, 155),
        'has_watermark': False,
    },
    {
        'id': 'slacki',
        'target_sz': 96,
        'f1_box': (305, 39, 423, 155),
        'f2_box': (436, 39, 554, 155),
        'has_watermark': False,
    },
    {
        'id': 'sasiadSzkodnik',
        'target_sz': 128,
        'f1_box': (18, 209, 135, 326),
        'f2_box': (148, 209, 265, 326),
        'has_watermark': False,
    },
    {
        'id': 'autoTuneHipster',
        'target_sz': 128,
        'f1_box': (305, 209, 423, 326),
        'f2_box': (436, 209, 554, 326),
        'has_watermark': False,
    },
    {
        'id': 'drogiePiwo',
        'target_sz': 128,
        'f1_box': (18, 381, 135, 497),
        'f2_box': (149, 381, 265, 497),
        'has_watermark': True,
    },
    {
        'id': 'straznik',
        'target_sz': 128,
        'f1_box': (305, 381, 423, 497),
        'f2_box': (436, 381, 554, 497),
        'has_watermark': True,
    },
    {
        'id': 'kark',
        'target_sz': 128,
        'f1_box': (18, 552, 135, 669),
        'f2_box': (149, 552, 265, 669),
        'has_watermark': True,
    },
    {
        'id': 'rwaKulszowa',
        'target_sz': 128,
        'f1_box': (305, 552, 423, 669),
        'f2_box': (436, 552, 554, 669),
        'has_watermark': True,
    },
    {
        'id': 'panJanusz',
        'target_sz': 144,
        'f1_box': (18, 724, 135, 849),
        'f2_box': (149, 724, 265, 849),
        'has_watermark': True,
    },
    {
        'id': 'kredyt',
        'target_sz': 144,
        'f1_box': (305, 724, 423, 849),
        'f2_box': (436, 724, 554, 849),
        'has_watermark': True,
    },
    {
        'id': 'audyt',
        'target_sz': 144,
        # Using Pair B (Box 2 & Box 3) with active matrix scanlines + error CRT & robot claw
        'f1_box': (305, 900, 423, 1012),
        'f2_box': (436, 900, 554, 1012),
        'has_watermark': True,
    }
]

def is_bg_or_border(c):
    r, g, b = c[:3]
    # Background dark teal fill
    if r <= 22 and 22 <= g <= 50 and 26 <= b <= 56:
        return True
    # Border line teal
    if abs(r - 57) < 30 and abs(g - 92) < 30 and abs(b - 98) < 30:
        return True
    return False

def extract_frame(raw_crop, has_watermark):
    crop = raw_crop.copy()
    w, h = crop.size
    pix = crop.load()

    # Clear F1/F2 watermark badges in top-left
    if has_watermark:
        for y in range(min(16, h)):
            for x in range(min(18, w)):
                pix[x, y] = (8, 35, 42, 255)

    # 4-boundary flood fill
    mask = [[False] * w for _ in range(h)]
    q = deque()
    for x in range(w):
        if is_bg_or_border(pix[x, 0]):
            mask[0][x] = True
            q.append((x, 0))
        if is_bg_or_border(pix[x, h - 1]):
            mask[h - 1][x] = True
            q.append((x, h - 1))
    for y in range(h):
        if is_bg_or_border(pix[0, y]):
            mask[y][0] = True
            q.append((0, y))
        if is_bg_or_border(pix[w - 1, y]):
            mask[y][w - 1] = True
            q.append((w - 1, y))

    while q:
        cx, cy = q.popleft()
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < w and 0 <= ny < h and not mask[ny][nx]:
                if is_bg_or_border(pix[nx, ny]):
                    mask[ny][nx] = True
                    q.append((nx, ny))

    res = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    res_pix = res.load()
    for y in range(h):
        for x in range(w):
            if not mask[y][x]:
                res_pix[x, y] = pix[x, y]

    return res

def process_all():
    print(f"Loading master graphic from: {SRC_GRAPHIC}")
    src = Image.open(SRC_GRAPHIC).convert('RGBA')

    for cfg in ENEMY_CONFIGS:
        eid = cfg['id']
        sz = cfg['target_sz']

        f1_raw = src.crop(cfg['f1_box'])
        f2_raw = src.crop(cfg['f2_box'])

        f1_clean = extract_frame(f1_raw, cfg['has_watermark'])
        f2_clean = extract_frame(f2_raw, cfg['has_watermark'])

        sheet = Image.new('RGBA', (sz * 2, sz), (0, 0, 0, 0))

        if sz == 96:
            # Scale down slightly to fit 96x96 canvas with 4px margin
            scale = 88.0 / max(f1_clean.height, f1_clean.width, f2_clean.height, f2_clean.width)
            f1_w, f1_h = int(f1_clean.width * scale), int(f1_clean.height * scale)
            f2_w, f2_h = int(f2_clean.width * scale), int(f2_clean.height * scale)
            f1_s = f1_clean.resize((f1_w, f1_h), Image.Resampling.LANCZOS)
            f2_s = f2_clean.resize((f2_w, f2_h), Image.Resampling.LANCZOS)
            ox1 = (sz - f1_w) // 2
            oy1 = (sz - f1_h) // 2
            ox2 = (sz - f2_w) // 2
            oy2 = (sz - f2_h) // 2
            sheet.paste(f1_s, (ox1, oy1), f1_s)
            sheet.paste(f2_s, (sz + ox2, oy2), f2_s)
        else:
            # 1:1 Native pixel art centered horizontally and vertically
            ox1 = (sz - f1_clean.width) // 2
            oy1 = (sz - f1_clean.height) // 2
            ox2 = (sz - f2_clean.width) // 2
            oy2 = (sz - f2_clean.height) // 2
            sheet.paste(f1_clean, (ox1, oy1), f1_clean)
            sheet.paste(f2_clean, (sz + ox2, oy2), f2_clean)

        out_path = os.path.join(OUT_DIR, f"{eid}.png")
        sheet.save(out_path, "PNG")

        b0 = sheet.crop((0, 0, sz, sz)).getbbox()
        b1 = sheet.crop((sz, 0, sz * 2, sz)).getbbox()
        file_size = os.path.getsize(out_path)
        print(f"Generated {eid}.png: {sheet.size} | Frame0: {b0} | Frame1: {b1} | {file_size} bytes")

if __name__ == '__main__':
    process_all()
