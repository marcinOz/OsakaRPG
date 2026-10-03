#!/usr/bin/env python3
"""crop_items.py - extract item icons and photo thumbnails from reference.jpg."""
import os
import sys
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pixelize as P

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.path.join(ROOT, "art_src", "reference.jpg")
OUT = os.path.join(ROOT, "public", "assets")

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

def make_items(im, pal, debug=False):
    os.makedirs(os.path.join(OUT, "items"), exist_ok=True)
    q = P.Quantizer(pal)

    for name, (cx, cy) in ITEMS_COORDS.items():
        # Crop 28x28 around the icon
        crop = im.crop((cx - 13, cy - 13, cx + 13, cy + 13)).convert("RGBA")
        px = crop.load()
        w, h = crop.size

        # Remove card background (card bg is dark navy with lum < 45 and r < 35, g < 40, b < 60)
        # Keep bright parts of the icon
        for y in range(h):
            for x in range(w):
                r, g, b, a = px[x, y]
                # Card background check
                if (r < 30 and g < 35 and b < 55) or lum(r, g, b) < 32:
                    px[x, y] = (0, 0, 0, 0)
                else:
                    px[x, y] = (r, g, b, 255)

        # Scale to 24x24
        icon24 = crop.resize((24, 24), Image.BOX)
        p24 = P.binarize_alpha(P.quantize(icon24, q))
        dest = os.path.join(OUT, "items", f"{name}.png")
        p24.save(dest)
        if debug:
            print(f"Saved {dest}")

def make_thumbs(im, pal, debug=False):
    os.makedirs(os.path.join(OUT, "ui"), exist_ok=True)
    q = P.Quantizer(pal)

    for name, (cx, cy) in THUMBS_COORDS.items():
        crop = im.crop((cx - 18, cy - 18, cx + 18, cy + 18)).convert("RGBA")
        thumb40 = crop.resize((40, 40), Image.BOX)
        p40 = P.binarize_alpha(P.quantize(thumb40, q))
        dest = os.path.join(OUT, "ui", f"thumb_{name}.png")
        p40.save(dest)
        if debug:
            print(f"Saved {dest}")

def main():
    im = Image.open(REF).convert("RGB")
    pal = P.load_palette()
    make_items(im, pal, debug=True)
    make_thumbs(im, pal, debug=True)

if __name__ == "__main__":
    main()
