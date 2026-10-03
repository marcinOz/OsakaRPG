#!/usr/bin/env python3
"""extract_pixel_perfect.py - Extract pixel-perfect uncompressed assets from art_src/reference.jpg

Drops all 16-bit / 48-color constraints.
Extracts:
1. public/assets/bg/analyzer_bg.png (1024x576, reference padded with authentic navy bezel at bottom)
2. public/assets/cards/{id}.png (~307x182 native resolution hero cards)
3. public/assets/portraits/{id}_{128,96,64}.png (full fidelity portraits)
4. public/assets/items/{name}.png (32x32 clean item icons with alpha)
5. public/assets/ui/thumb_{group,travel,funny,moments}.png (uncompressed photo thumbnails)
"""
import os
import sys
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.path.join(ROOT, "art_src", "reference.jpg")
ASSETS = os.path.join(ROOT, "public", "assets")

CARDS_COORDS = {
    "danny": (37, 173, 344, 355),
    "alior": (364, 173, 671, 355),
    "lisu":  (691, 173, 998, 355),
    "barti": (37, 363, 344, 545),
    "oziem": (364, 363, 671, 545),
    "luki":  (691, 363, 998, 545),
}

ITEMS_COORDS = {
    'shield': (168, 256), 'gauntlets': (227, 256), 'shaker': (291, 256),
    'controller': (494, 256), 'cartridge': (557, 256), 'goggles': (612, 256),
    'binoculars': (821, 256), 'fox': (880, 256), 'sneakers': (937, 256),
    'vinyl': (168, 447), 'turntable': (230, 447), 'speaker': (293, 447),
    'rope': (494, 447), 'multitool': (556, 447), 'campfire': (623, 447),
    'divingGoggles': (821, 447), 'lifebuoy': (882, 447), 'backpack': (941, 447),
}

THUMBS_COORDS = {
    'group': (756, 92),
    'travel': (820, 92),
    'funny': (884, 92),
    'moments': (948, 92),
}

def lum(r, g, b):
    return 0.299 * r + 0.587 * g + 0.114 * b

def extract_analyzer_bg(ref_im):
    """Pads the 1024x559 reference image to 1024x576 with matching navy bezel."""
    os.makedirs(os.path.join(ASSETS, "bg"), exist_ok=True)
    w, h = ref_im.size # 1024, 559
    target_w, target_h = 1024, 576
    bg = Image.new("RGB", (target_w, target_h), (47, 66, 92))
    bg.paste(ref_im, (0, 0))
    
    # Replicate bottom rows with gradient matching the bottom bezel
    ref_px = ref_im.load()
    bg_px = bg.load()
    for y in range(h, target_h):
        for x in range(target_w):
            # Take color from row h - 1, slight darkening towards the very bottom
            r, g, b = ref_px[x, h - 1]
            factor = 1.0 - (y - h) / (target_h - h) * 0.15
            bg_px[x, y] = (int(r * factor), int(g * factor), int(b * factor))
            
    out_path = os.path.join(ASSETS, "bg", "analyzer_bg.png")
    bg.save(out_path, "PNG", optimize=True)
    print(f"Saved {out_path} ({bg.size})")

def extract_cards(ref_im):
    """Extracts the 6 cards at native resolution."""
    cards_dir = os.path.join(ASSETS, "cards")
    os.makedirs(cards_dir, exist_ok=True)
    for name, (x0, y0, x1, y1) in CARDS_COORDS.items():
        card = ref_im.crop((x0, y0, x1, y1))
        out_path = os.path.join(cards_dir, f"{name}.png")
        card.save(out_path, "PNG", optimize=True)
        print(f"Saved card {out_path} ({card.size})")

def inner_box(im, x0, y0, w=100, h=116):
    """Locates the inner portrait rectangle."""
    px = im.load()
    ys = range(y0 + 20, y0 + h - 20, 4)
    xs = range(x0 + 20, x0 + w - 20, 4)
    right = max(x for x in range(x0 + w - 10, x0 + w + 6) if sum(lum(*px[x, y]) > 150 for y in ys) > len(ys) * 0.6)
    bottom = max(y for y in range(y0 + h - 12, y0 + h + 6) if sum(lum(*px[x, y]) > 150 for x in xs) > len(xs) * 0.6)
    
    def scan(start, step, fixed_axis, positions, limit=8):
        res = []
        for pos in positions:
            for k in range(1, limit):
                c = start + step * k
                p = px[c, pos] if fixed_axis == "y" else px[pos, c]
                if lum(*p) < 40:
                    res.append(c)
                    break
        res.sort()
        return res[len(res) // 2] if res else None

    l = scan(x0, 1, "y", ys) + 1
    r = scan(right, -1, "y", ys)
    t = scan(y0, 1, "x", xs) + 1
    b = scan(bottom, -1, "x", xs)
    return l, t, r, b

def extract_portraits(ref_im):
    """Extracts 128x128, 96x96, and 64x64 uncompressed portraits."""
    portraits_dir = os.path.join(ASSETS, "portraits")
    os.makedirs(portraits_dir, exist_ok=True)
    
    for name, (x0, y0, _, _) in CARDS_COORDS.items():
        l, t, r, b = inner_box(ref_im, x0, y0)
        iw, ih = r - l, b - t
        # Clean 96x96 base
        crop = ref_im.crop((l, t, r, min(b, t + 96)))
        canvas = Image.new("RGB", (96, 96))
        padl = (96 - iw) // 2
        canvas.paste(crop, (padl, 0))
        cp = canvas.load()
        for y in range(96):
            for x in range(padl):
                cp[x, y] = cp[padl, y]
            for x in range(padl + iw, 96):
                cp[x, y] = cp[padl + iw - 1, y]
        
        # Subtle cleanup filter to remove JPEG noise while preserving pixel edges
        clean96 = canvas.filter(ImageFilter.MedianFilter(3))
        
        # 96x96
        p96_path = os.path.join(portraits_dir, f"{name}_96.png")
        clean96.save(p96_path, "PNG")
        
        # 128x128 (resampled cleanly with slight unsharp mask)
        p128 = clean96.resize((128, 128), Image.Resampling.LANCZOS)
        p128 = p128.filter(ImageFilter.UnsharpMask(radius=1.2, percent=130, threshold=2))
        p128_path = os.path.join(portraits_dir, f"{name}_128.png")
        p128.save(p128_path, "PNG")
        
        # 64x64 (clean downscale)
        p64 = clean96.resize((64, 64), Image.Resampling.BILINEAR)
        p64_path = os.path.join(portraits_dir, f"{name}_64.png")
        p64.save(p64_path, "PNG")
        print(f"Extracted portraits for {name}: 128, 96, 64")

def extract_items(ref_im):
    """Extracts 32x32 uncompressed item icons with alpha transparency."""
    items_dir = os.path.join(ASSETS, "items")
    os.makedirs(items_dir, exist_ok=True)
    
    for name, (cx, cy) in ITEMS_COORDS.items():
        # Crop 28x28 around icon
        crop = ref_im.crop((cx - 14, cy - 14, cx + 14, cy + 14)).convert("RGBA")
        px = crop.load()
        w, h = crop.size
        
        # Remove dark navy background (r < 32, g < 36, b < 56, lum < 35)
        for y in range(h):
            for x in range(w):
                r, g, b, a = px[x, y]
                l = lum(r, g, b)
                if (r < 35 and g < 40 and b < 58) or l < 32:
                    px[x, y] = (0, 0, 0, 0)
                elif l < 48 and (b > r + 15):
                    # Soft edge blend
                    alpha = int(255 * (l - 32) / 16)
                    px[x, y] = (r, g, b, max(0, min(255, alpha)))
                else:
                    px[x, y] = (r, g, b, 255)
        
        # Resize cleanly to 32x32 centered
        icon32 = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
        crop_scaled = crop.resize((28, 28), Image.Resampling.NEAREST)
        icon32.paste(crop_scaled, (2, 2), crop_scaled)
        
        out_path = os.path.join(items_dir, f"{name}.png")
        icon32.save(out_path, "PNG")
        print(f"Saved item icon {out_path}")

def extract_thumbs(ref_im):
    """Extracts 40x40 uncompressed photo thumbnails."""
    ui_dir = os.path.join(ASSETS, "ui")
    os.makedirs(ui_dir, exist_ok=True)
    
    for name, (cx, cy) in THUMBS_COORDS.items():
        crop = ref_im.crop((cx - 18, cy - 18, cx + 18, cy + 18)).convert("RGBA")
        thumb = crop.resize((40, 40), Image.Resampling.LANCZOS)
        out_path = os.path.join(ui_dir, f"thumb_{name}.png")
        thumb.save(out_path, "PNG")
        print(f"Saved thumbnail {out_path}")

def main():
    print("Opening reference image:", REF)
    ref_im = Image.open(REF).convert("RGB")
    print("Reference size:", ref_im.size)
    
    extract_analyzer_bg(ref_im)
    extract_cards(ref_im)
    extract_portraits(ref_im)
    extract_items(ref_im)
    extract_thumbs(ref_im)
    print("Pixel-perfect extraction completed successfully!")

if __name__ == "__main__":
    main()
