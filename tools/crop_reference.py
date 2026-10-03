#!/usr/bin/env python3
"""crop_reference.py - extract canonical portraits, item icons and photo
thumbnails from art_src/reference.jpg (Friend Pack Analyzer screen).

  python3 tools/crop_reference.py [--debug]

Portrait boxes are located by scanning for the bright cyan card frame and the
dark 1px line just inside it, so the crop is pixel-exact.  The portraits are
kept at 1:1 source resolution (the reference art is ~native at 96px), JPEG
noise is cleaned with a small median filter, then palette-locked.
"""
from __future__ import annotations

import argparse
import os
import sys

from PIL import Image, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pixelize as P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.path.join(ROOT, "art_src", "reference.jpg")
OUT = os.path.join(ROOT, "public", "assets")

# outer-frame top-left of each portrait box (found with art_src/scratch/find_bounds.py)
CARDS = {
    "danny": (37, 173), "alior": (364, 173), "lisu": (691, 173),
    "barti": (37, 363), "oziem": (364, 363), "luki": (691, 363),
}
# item icon centres (x, y) and source box half-size in the reference
ITEMS = {
    "shield": ("danny", 0), "gauntlets": ("danny", 1), "shaker": ("danny", 2),
    "controller": ("alior", 0), "cartridge": ("alior", 1), "goggles": ("alior", 2),
    "binoculars": ("lisu", 0), "fox": ("lisu", 1), "sneakers": ("lisu", 2),
    "vinyl": ("barti", 0), "turntable": ("barti", 1), "speaker": ("barti", 2),
    "rope": ("oziem", 0), "multitool": ("oziem", 1), "campfire": ("oziem", 2),
    "divingGoggles": ("luki", 0), "lifebuoy": ("luki", 1), "backpack": ("luki", 2),
}
THUMBS = ["group", "travel", "funny", "moments"]


def lum(p):
    return 0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]


def inner_box(im, x0, y0, w=100, h=116):
    """Return (l, t, r, b) exclusive inner portrait area for the frame at x0,y0."""
    px = im.load()

    def scan(start, step, fixed_axis, positions, limit=8):
        res = []
        for pos in positions:
            for k in range(1, limit):
                c = start + step * k
                p = px[c, pos] if fixed_axis == "y" else px[pos, c]
                if lum(p) < 40:  # dark inner line
                    res.append(c)
                    break
        res.sort()
        return res[len(res) // 2] if res else None

    ys = range(y0 + 20, y0 + h - 20, 4)
    xs = range(x0 + 20, x0 + w - 20, 4)
    # find right/bottom bright frame first
    right = max(x for x in range(x0 + w - 10, x0 + w + 6) if sum(lum(px[x, y]) > 150 for y in ys) > len(ys) * 0.6)
    bottom = max(y for y in range(y0 + h - 12, y0 + h + 6) if sum(lum(px[x, y]) > 150 for x in xs) > len(xs) * 0.6)
    l = scan(x0, 1, "y", ys) + 1
    r = scan(right, -1, "y", ys)
    t = scan(y0, 1, "x", xs) + 1
    b = scan(bottom, -1, "x", xs)
    return l, t, r, b


def clean(img, size_filter=3):
    return img.filter(ImageFilter.MedianFilter(size_filter))


def make_portraits(im, pal, debug=False):
    q = P.Quantizer(pal)
    os.makedirs(os.path.join(OUT, "portraits"), exist_ok=True)
    boxes = {}
    for k, (x0, y0) in CARDS.items():
        l, t, r, b = inner_box(im, x0, y0)
        boxes[k] = (l, t, r, b)
        iw, ih = r - l, b - t
        # 96x96: 1:1 crop, width padded by edge replication, top aligned
        top = t
        crop = im.crop((l, top, r, min(b, top + 96)))
        canvas = Image.new("RGB", (96, 96))
        padl = (96 - iw) // 2
        canvas.paste(crop, (padl, 0))
        cp = canvas.load()
        for y in range(96):
            for x in range(padl):
                cp[x, y] = cp[padl, y]
            for x in range(padl + iw, 96):
                cp[x, y] = cp[padl + iw - 1, y]
        src96 = clean(canvas)
        p96 = P.quantize(src96.convert("RGBA"), q)
        p96 = P.binarize_alpha(p96)
        p96.save(os.path.join(OUT, "portraits", f"{k}_96.png"))
        # 64x64: area downscale from the cleaned 96 source
        sq = src96.resize((64, 64), Image.BOX)
        p64 = P.binarize_alpha(P.quantize(sq.convert("RGBA"), q))
        p64.save(os.path.join(OUT, "portraits", f"{k}_64.png"))
        if debug:
            print(k, "inner", (l, t, r, b), "size", (iw, ih))
    return boxes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--debug", action="store_true")
    ap.add_argument("--only", choices=["portraits", "items", "thumbs"])
    a = ap.parse_args()
    im = Image.open(REF).convert("RGB")
    pal = P.load_palette()
    if a.only in (None, "portraits"):
        make_portraits(im, pal, a.debug)
    if a.only in (None, "items"):
        import crop_items
        crop_items.make_items(im, pal, a.debug)
    if a.only in (None, "thumbs"):
        import crop_items
        crop_items.make_thumbs(im, pal, a.debug)


if __name__ == "__main__":
    main()
