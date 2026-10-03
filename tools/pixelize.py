#!/usr/bin/env python3
"""pixelize.py - turn hi-res / AI-generated art into palette-locked pixel art.

Usage
-----
  pixelize.py IN OUT --size WxH [--key magenta|auto|none] [--dither none|ordered]
              [--outline] [--outline-mode inner|outer] [--method mean|mode]
              [--crop x,y,w,h] [--fit] [--palette tools/palette.json]
  pixelize.py --verify public/assets [--palette tools/palette.json]

Pipeline: key background -> alpha, area downscale to the target grid,
quantize to the master palette (no dither for sprites, Bayer 4x4 ordered
dither for backgrounds), optional 1px dark outline, orphan pixel removal.
Output alpha is strictly 0 or 255.

Pure Pillow (no numpy) so it runs anywhere Pillow does.  The functions are
importable (crop_reference.py / build_*.py reuse them).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PALETTE = os.path.join(HERE, "palette.json")
OUTLINE_COLOR = (0x1B, 0x13, 0x19)  # warm near-black from the palette

BAYER4 = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


# --------------------------------------------------------------- palette
def hex2rgb(h: str):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def load_palette(path: str = DEFAULT_PALETTE):
    with open(path) as f:
        data = json.load(f)
    return [hex2rgb(c) for c in data["colors"]]


class Quantizer:
    """Nearest-colour lookup using the 'redmean' perceptual RGB distance."""

    def __init__(self, palette, subset=None):
        self.pal = list(subset if subset else palette)
        self.cache = {}

    def nearest(self, c):
        c = c[:3]
        r = self.cache.get(c)
        if r is not None:
            return r
        best, bd = None, 1e18
        r1, g1, b1 = c
        for p in self.pal:
            rm = (r1 + p[0]) / 2
            dr, dg, db = r1 - p[0], g1 - p[1], b1 - p[2]
            d = (2 + rm / 256) * dr * dr + 4 * dg * dg + (2 + (255 - rm) / 256) * db * db
            if d < bd:
                bd, best = d, p
        self.cache[c] = best
        return best


# --------------------------------------------------------------- keying
def _is_magenta(p, tol=90):
    r, g, b = p[:3]
    return r > 255 - tol - 40 and b > 255 - tol - 40 and g < tol and abs(r - b) < 90


def key_background(img: Image.Image, mode: str = "magenta", tol: int = 48) -> Image.Image:
    """Return RGBA with the background made fully transparent."""
    img = img.convert("RGBA")
    if mode in (None, "none"):
        return img
    w, h = img.size
    px = img.load()
    if mode == "magenta":
        for y in range(h):
            for x in range(w):
                if _is_magenta(px[x, y]):
                    px[x, y] = (0, 0, 0, 0)
        return img
    # auto: flood fill from the border with the median border colour
    border = [px[x, 0] for x in range(w)] + [px[x, h - 1] for x in range(w)]
    border += [px[0, y] for y in range(h)] + [px[w - 1, y] for y in range(h)]
    bg = tuple(sorted(c[i] for c in border)[len(border) // 2] for i in range(3))

    def close(p):
        return p[3] > 0 and abs(p[0] - bg[0]) + abs(p[1] - bg[1]) + abs(p[2] - bg[2]) <= tol * 3

    seen = bytearray(w * h)
    stack = []
    for x in range(w):
        stack += [(x, 0), (x, h - 1)]
    for y in range(h):
        stack += [(0, y), (w - 1, y)]
    while stack:
        x, y = stack.pop()
        i = y * w + x
        if seen[i]:
            continue
        seen[i] = 1
        if not close(px[x, y]):
            continue
        px[x, y] = (0, 0, 0, 0)
        if x > 0:
            stack.append((x - 1, y))
        if x < w - 1:
            stack.append((x + 1, y))
        if y > 0:
            stack.append((x, y - 1))
        if y < h - 1:
            stack.append((x, y + 1))
    return img


# --------------------------------------------------------------- geometry
def opaque_bbox(img: Image.Image):
    return img.getchannel("A").point(lambda a: 255 if a > 127 else 0).getbbox()


def fit_into(img: Image.Image, w: int, h: int, anchor: str = "bottom", pad: int = 0) -> Image.Image:
    """Crop to opaque bbox and scale (keeping aspect) onto a w*h*k canvas.

    Returns a hi-res RGBA image whose size is an integer multiple of (w, h)
    so the subsequent area downscale lands on a clean grid."""
    bb = opaque_bbox(img)
    if bb:
        img = img.crop(bb)
    iw, ih = img.size
    k = max(1, int(max(iw / max(1, w - 2 * pad), ih / max(1, h - 2 * pad)) + 0.999))
    cw, ch = w * k, h * k
    s = min((cw - 2 * pad * k) / iw, (ch - 2 * pad * k) / ih)
    nw, nh = max(1, int(iw * s)), max(1, int(ih * s))
    img = img.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    ox = (cw - nw) // 2
    oy = (ch - nh) // 2 if anchor == "center" else ch - nh - pad * k
    canvas.paste(img, (ox, oy), img)
    return canvas


def downscale(img: Image.Image, w: int, h: int, method: str = "mean", alpha_thresh: float = 0.5,
              quant: Quantizer | None = None) -> Image.Image:
    """Area downscale to w*h. Alpha becomes binary (coverage >= alpha_thresh)."""
    img = img.convert("RGBA")
    sw, sh = img.size
    if (sw, sh) == (w, h):
        out = img.copy()
    elif method == "mean":
        out = img.convert("RGBa").resize((w, h), Image.BOX).convert("RGBA")
    else:  # mode: majority palette colour of opaque source pixels in each cell
        q = quant
        src = img.load()
        out = Image.new("RGBA", (w, h))
        op = out.load()
        for ty in range(h):
            y0, y1 = ty * sh // h, max(ty * sh // h + 1, (ty + 1) * sh // h)
            for tx in range(w):
                x0, x1 = tx * sw // w, max(tx * sw // w + 1, (tx + 1) * sw // w)
                cnt = Counter()
                tot = 0
                for yy in range(y0, y1):
                    for xx in range(x0, x1):
                        p = src[xx, yy]
                        tot += 1
                        if p[3] > 127:
                            cnt[q.nearest(p) if q else p[:3]] += 1
                n = sum(cnt.values())
                if n == 0 or n / tot < alpha_thresh:
                    op[tx, ty] = (0, 0, 0, 0)
                else:
                    c = cnt.most_common(1)[0][0]
                    op[tx, ty] = (c[0], c[1], c[2], int(255 * n / tot))
    a = out.getchannel("A").point(lambda v: 255 if v >= int(255 * alpha_thresh) else 0)
    out.putalpha(a)
    return out


# --------------------------------------------------------------- colour
def quantize(img: Image.Image, quant: Quantizer, dither: str = "none", spread: float = 28.0) -> Image.Image:
    img = img.convert("RGBA")
    w, h = img.size
    px = img.load()
    for y in range(h):
        for x in range(w):
            p = px[x, y]
            if p[3] < 128:
                px[x, y] = (0, 0, 0, 0)
                continue
            if dither == "ordered":
                t = (BAYER4[y & 3][x & 3] + 0.5) / 16 - 0.5
                d = t * spread
                c = (max(0, min(255, int(p[0] + d))), max(0, min(255, int(p[1] + d))),
                     max(0, min(255, int(p[2] + d))))
            else:
                c = p[:3]
            n = quant.nearest(c)
            px[x, y] = (n[0], n[1], n[2], 255)
    return img


def luma(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def add_outline(img: Image.Image, color=OUTLINE_COLOR, mode: str = "inner", dark_keep: float = 48) -> Image.Image:
    """1px dark outline. inner: recolour opaque edge pixels (keeps silhouette
    size); outer: paint transparent pixels touching the sprite."""
    img = img.copy()
    w, h = img.size
    src = img.copy().load()
    px = img.load()
    for y in range(h):
        for x in range(w):
            p = src[x, y]
            nb = []
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                xx, yy = x + dx, y + dy
                nb.append(src[xx, yy][3] if 0 <= xx < w and 0 <= yy < h else 0)
            if mode == "inner":
                if p[3] and min(nb) == 0 and luma(p) > dark_keep:
                    px[x, y] = color + (255,)
            else:
                if not p[3] and max(nb) > 0:
                    px[x, y] = color + (255,)
    return img


def remove_orphans(img: Image.Image, min_neighbours: int = 1) -> Image.Image:
    """Drop opaque pixels with fewer than min_neighbours opaque 8-neighbours,
    and fill 1px transparent pin-holes fully enclosed by opaque pixels."""
    img = img.copy()
    w, h = img.size
    src = img.copy().load()
    px = img.load()
    for y in range(h):
        for x in range(w):
            n = 0
            cols = Counter()
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dx == dy == 0:
                        continue
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < w and 0 <= yy < h and src[xx, yy][3]:
                        n += 1
                        if dx == 0 or dy == 0:
                            cols[src[xx, yy]] += 1
            if src[x, y][3] and n < min_neighbours:
                px[x, y] = (0, 0, 0, 0)
            elif not src[x, y][3] and n == 8 and cols:
                px[x, y] = cols.most_common(1)[0][0]
    return img


def binarize_alpha(img: Image.Image) -> Image.Image:
    img = img.convert("RGBA")
    a = img.getchannel("A").point(lambda v: 255 if v >= 128 else 0)
    img.putalpha(a)
    px = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            if px[x, y][3] == 0:
                px[x, y] = (0, 0, 0, 0)
    return img


def pixelize(img: Image.Image, size, key="magenta", dither="none", outline=False, outline_mode="inner",
             method="mean", palette=None, fit=False, alpha_thresh=0.5, orphans=True, spread=28.0):
    pal = palette or load_palette()
    q = Quantizer(pal)
    img = key_background(img, key)
    w, h = size
    if fit:
        img = fit_into(img, w, h)
    img = downscale(img, w, h, method=method, alpha_thresh=alpha_thresh, quant=q)
    img = quantize(img, q, dither=dither, spread=spread)
    if orphans:
        img = remove_orphans(img)
    if outline:
        img = add_outline(img, mode=outline_mode)
    return binarize_alpha(img)


# --------------------------------------------------------------- verify
def verify(root: str, palette) -> int:
    pal = set(palette)
    bad = 0
    count = 0
    for dp, _, files in os.walk(root):
        for fn in sorted(files):
            if not fn.lower().endswith(".png"):
                continue
            path = os.path.join(dp, fn)
            count += 1
            im = Image.open(path).convert("RGBA")
            errs = Counter()
            for p in im.getdata():
                if p[3] == 0:
                    continue
                if p[3] != 255:
                    errs["semi-alpha"] += 1
                elif p[:3] not in pal:
                    errs["#%02x%02x%02x" % p[:3]] += 1
            if errs:
                bad += 1
                print("FAIL", path, dict(errs.most_common(6)))
    print(f"verified {count} PNGs, {bad} failing")
    return 1 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inp", nargs="?")
    ap.add_argument("out", nargs="?")
    ap.add_argument("--size", help="WxH target grid")
    ap.add_argument("--key", default="magenta", choices=["magenta", "auto", "none"])
    ap.add_argument("--dither", default="none", choices=["none", "ordered"])
    ap.add_argument("--spread", type=float, default=28.0, help="ordered dither strength")
    ap.add_argument("--outline", action="store_true")
    ap.add_argument("--outline-mode", default="inner", choices=["inner", "outer"])
    ap.add_argument("--method", default="mean", choices=["mean", "mode"])
    ap.add_argument("--crop", help="x,y,w,h crop applied first")
    ap.add_argument("--fit", action="store_true", help="fit opaque bbox into the target keeping aspect")
    ap.add_argument("--alpha", type=float, default=0.5, help="coverage threshold for opaque cells")
    ap.add_argument("--palette", default=DEFAULT_PALETTE)
    ap.add_argument("--verify", metavar="DIR")
    a = ap.parse_args(argv)
    pal = load_palette(a.palette)
    if a.verify:
        return verify(a.verify, pal)
    if not (a.inp and a.out and a.size):
        ap.error("IN OUT --size required")
    w, h = (int(v) for v in a.size.lower().split("x"))
    img = Image.open(a.inp)
    if a.crop:
        x, y, cw, ch = (int(v) for v in a.crop.split(","))
        img = img.crop((x, y, x + cw, y + ch))
    out = pixelize(img, (w, h), key=a.key, dither=a.dither, outline=a.outline, outline_mode=a.outline_mode,
                   method=a.method, palette=pal, fit=a.fit, alpha_thresh=a.alpha, spread=a.spread)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    out.save(a.out)
    print("wrote", a.out, out.size)
    return 0


if __name__ == "__main__":
    sys.exit(main())
