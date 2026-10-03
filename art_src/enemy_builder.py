import os
from collections import deque
from PIL import Image

def process_enemy_sprite(src_img_path, enemy_name, target_sz=128, out_dir='public/assets/enemies'):
    im = Image.open(src_img_path).convert('RGBA')
    w, h = im.size
    pixels = im.load()

    # Determine background color threshold from the 4 corners
    corner_colors = [pixels[0, 0], pixels[w-1, 0], pixels[0, h-1], pixels[w-1, h-1]]
    # Typically solid black (r,g,b < 30) or solid white or solid color
    avg_r = sum(c[0] for c in corner_colors) / 4.0
    avg_g = sum(c[1] for c in corner_colors) / 4.0
    avg_b = sum(c[2] for c in corner_colors) / 4.0

    is_dark_bg = (avg_r + avg_g + avg_b) / 3.0 < 50

    def is_bg_pixel(c):
        if is_dark_bg:
            return c[0] < 28 and c[1] < 28 and c[2] < 28
        else:
            dr = abs(c[0] - avg_r)
            dg = abs(c[1] - avg_g)
            db = abs(c[2] - avg_b)
            return (dr + dg + db) < 35

    # Flood fill outer background
    bg_mask = [[False]*w for _ in range(h)]
    q = deque()
    for x in range(w):
        if is_bg_pixel(pixels[x, 0]):
            bg_mask[0][x] = True; q.append((x, 0))
        if is_bg_pixel(pixels[x, h-1]):
            bg_mask[h-1][x] = True; q.append((x, h-1))
    for y in range(h):
        if is_bg_pixel(pixels[0, y]):
            bg_mask[y][0] = True; q.append((0, y))
        if is_bg_pixel(pixels[w-1, y]):
            bg_mask[y][w-1] = True; q.append((w-1, y))

    while q:
        cx, cy = q.popleft()
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < w and 0 <= ny < h and not bg_mask[ny][nx]:
                if is_bg_pixel(pixels[nx, ny]):
                    bg_mask[ny][nx] = True
                    q.append((nx, ny))

    min_x, max_x = w, 0
    min_y, max_y = h, 0
    found_any = False
    for y in range(h):
        for x in range(w):
            if bg_mask[y][x]:
                pixels[x, y] = (0, 0, 0, 0)
            else:
                c = pixels[x, y]
                if is_dark_bg:
                    brightness = max(c[0], c[1], c[2])
                    if brightness < 32:
                        alpha = int(255 * (brightness / 32.0))
                        pixels[x, y] = (c[0], c[1], c[2], alpha)
                found_any = True
                min_x = min(min_x, x)
                max_x = max(max_x, x)
                min_y = min(min_y, y)
                max_y = max(max_y, y)

    if not found_any or min_x >= max_x or min_y >= max_y:
        print(f"Warning: no foreground found in {src_img_path}")
        return None

    cropped = im.crop((min_x, min_y, max_x + 1, max_y + 1))
    padding = 8 if target_sz >= 128 else 6
    max_dim = target_sz - padding * 2
    scale = max_dim / max(cropped.width, cropped.height)
    new_w, new_h = max(4, int(cropped.width * scale)), max(4, int(cropped.height * scale))
    scaled = cropped.resize((new_w, new_h), Image.Resampling.LANCZOS)

    # Frame 0: rest
    frame0 = Image.new('RGBA', (target_sz, target_sz), (0, 0, 0, 0))
    ox = (target_sz - new_w) // 2
    oy = target_sz - padding - new_h
    frame0.paste(scaled, (ox, oy), scaled)

    # Frame 1: breathing animation (subtle squish / stretch)
    squash_w = min(target_sz - 4, new_w + 3)
    squash_h = max(4, new_h - 2)
    frame1_scaled = cropped.resize((squash_w, squash_h), Image.Resampling.LANCZOS)
    frame1 = Image.new('RGBA', (target_sz, target_sz), (0, 0, 0, 0))
    ox1 = (target_sz - squash_w) // 2
    oy1 = target_sz - padding - squash_h
    frame1.paste(frame1_scaled, (ox1, oy1), frame1_scaled)

    # 2-frame horizontal spritesheet
    sheet = Image.new('RGBA', (target_sz * 2, target_sz), (0, 0, 0, 0))
    sheet.paste(frame0, (0, 0))
    sheet.paste(frame1, (target_sz, 0))

    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, f"{enemy_name}.png")
    sheet.save(out_file, 'PNG')
    print(f"Saved {enemy_name}.png: ({sheet.width}, {sheet.height})")
    return out_file
