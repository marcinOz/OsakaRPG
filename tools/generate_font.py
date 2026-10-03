#!/usr/bin/env python3
"""generate_font.py - generate crisp 16-bit pixel fonts with full Polish diacritics.
Produces public/assets/fonts/pixel.png + pixel.fnt and pixel_big.png + pixel_big.fnt
in standard BMFont text format supported natively by Phaser 3 BitmapText.
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "public", "assets", "fonts")
os.makedirs(OUT, exist_ok=True)

CHARS = (
    " !\"#$%&'()*+,-./0123456789:;<=>?@"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`"
    "abcdefghijklmnopqrstuvwxyz{|}~"
    "ąćęłńóśźżĄĆĘŁŃÓŚŹŻ▶✓•►★"
)

def build_font(name, font_size, line_height, scale=1):
    tex_w, tex_h = 256 * scale, 256 * scale
    img = Image.new("RGBA", (tex_w, tex_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Use a system monospace font or basic bitmap rasterizer
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Courier.dfont", font_size)
    except:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", font_size)
        except:
            font = ImageFont.load_default()

    cur_x = 2
    cur_y = 2
    max_h = 0
    char_records = []

    for ch in CHARS:
        code = ord(ch)
        bbox = draw.textbbox((0, 0), ch, font=font)
        gw = max(4 * scale, bbox[2] - bbox[0] + 1 * scale)
        gh = max(font_size + 2 * scale, bbox[3] - bbox[1] + 1 * scale)

        if cur_x + gw + 2 >= tex_w:
            cur_x = 2
            cur_y += max_h + 2
            max_h = 0

        # Draw glyph in pure white
        draw.text((cur_x - bbox[0], cur_y - bbox[1]), ch, font=font, fill=(255, 255, 255, 255))

        char_records.append({
            'id': code,
            'x': cur_x,
            'y': cur_y,
            'width': gw,
            'height': gh,
            'xoffset': 0,
            'yoffset': 0,
            'xadvance': gw + 1 * scale,
        })

        cur_x += gw + 2
        if gh > max_h:
            max_h = gh

    # Save PNG
    png_path = os.path.join(OUT, f"{name}.png")
    img.save(png_path)

    # Write BMFont .fnt
    fnt_path = os.path.join(OUT, f"{name}.fnt")
    with open(fnt_path, "w", encoding="utf-8") as f:
        f.write(f'info face="{name}" size={font_size} bold=0 italic=0 charset="" unicode=1 stretchH=100 smooth=0 aa=1 padding=0,0,0,0 spacing=1,1\n')
        f.write(f'common lineHeight={line_height} base={font_size} scaleW={tex_w} scaleH={tex_h} pages=1 packed=0\n')
        f.write(f'page id=0 file="{name}.png"\n')
        f.write(f'chars count={len(char_records)}\n')
        for r in char_records:
            f.write(f'char id={r["id"]} x={r["x"]} y={r["y"]} width={r["width"]} height={r["height"]} xoffset={r["xoffset"]} yoffset={r["yoffset"]} xadvance={r["xadvance"]} page=0 chnl=15\n')

    print(f"Generated {png_path} and {fnt_path} ({len(char_records)} chars)")

if __name__ == "__main__":
    build_font("pixel", font_size=10, line_height=12, scale=1)
    build_font("pixel_big", font_size=18, line_height=20, scale=1)
