#!/usr/bin/env python3
"""generate_chronicle_sprites.py - Generate procedural pixel-art sprite sheets for KRONIKA:
- spinning_vinyl_deck (4 frames, 48x26 per frame): rotating Technics vinyl label & sheen.
- birds_v_formation (6 frames, 48x24 per frame): flapping bird V-formation silhouette.
- shooting_star_anim (6 frames, 64x32 per frame): luminous streak shooting across sky.
- alley_cat (6 frames, 32x20 per frame): prowling black cat walk cycle.
- ufc_screen_fight (6 frames, 96x70 per frame): retro blue broadcast screen MMA fighters.
"""
import math
import os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "public", "assets", "chronicle", "sprites")
os.makedirs(OUT_DIR, exist_ok=True)


def generate_spinning_vinyl():
    """4 frames of 48x26 rotating vinyl record with red label and light sheen."""
    fw, fh = 48, 26
    nframes = 4
    sheet = Image.new("RGBA", (fw * nframes, fh), (0, 0, 0, 0))

    for f in range(nframes):
        img = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Outer vinyl disc (perspective ellipse)
        draw.ellipse([2, 1, fw - 3, fh - 2], fill=(18, 18, 22, 255), outline=(35, 35, 42, 255))
        # Concentric groove lines
        draw.ellipse([6, 3, fw - 7, fh - 4], outline=(28, 28, 34, 255))
        draw.ellipse([11, 5, fw - 12, fh - 6], outline=(24, 24, 30, 255))

        # Center label (classic red turntable label)
        draw.ellipse([16, 7, fw - 17, fh - 8], fill=(190, 45, 45, 255), outline=(230, 80, 80, 255))

        # Center spindle hole
        draw.ellipse([22, 11, 25, 14], fill=(12, 12, 14, 255))

        # Rotating white label notch / text notch
        angle = (f / nframes) * math.pi * 2
        nx = int(23.5 + math.cos(angle) * 5)
        ny = int(12.5 + math.sin(angle) * 3)
        draw.point((nx, ny), fill=(255, 240, 240, 255))

        # Light sheen / vinyl gloss reflection across diagonal
        for d in range(-2, 3):
            sx = int(fw * 0.35 + d * 2 + (f % 2))
            draw.line([(sx, 3), (sx + 8, fh - 4)], fill=(70, 70, 85, 90))

        sheet.paste(img, (f * fw, 0))

    sheet.save(os.path.join(OUT_DIR, "spinning_vinyl_deck.png"))
    print("[OK] Generated spinning_vinyl_deck.png")


def generate_birds_v_formation():
    """6 frames of 48x24 distant bird silhouettes flapping in V-formation."""
    fw, fh = 48, 24
    nframes = 6
    sheet = Image.new("RGBA", (fw * nframes, fh), (0, 0, 0, 0))

    # Positions of 5 birds in V-formation (rel to center)
    birds = [
        (24, 4),   # lead bird
        (16, 10),  # left 1
        (8, 16),   # left 2
        (32, 10),  # right 1
        (40, 16)   # right 2
    ]

    for f in range(nframes):
        img = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Flap phase: 0=wings up, 1=level, 2=down, 3=down, 4=level, 5=up
        wing_y_offsets = [-2, 0, 2, 2, 0, -2]
        wy = wing_y_offsets[f]

        for bx, by in birds:
            # Bird center body
            draw.point((bx, by), fill=(40, 30, 48, 240))
            # Left wing
            draw.line([(bx - 3, by + wy), (bx, by)], fill=(30, 22, 38, 255))
            # Right wing
            draw.line([(bx, by), (bx + 3, by + wy)], fill=(30, 22, 38, 255))

        sheet.paste(img, (f * fw, 0))

    sheet.save(os.path.join(OUT_DIR, "birds_v_formation.png"))
    print("[OK] Generated birds_v_formation.png")


def generate_shooting_star():
    """6 frames of 64x32 shooting star streak traveling across frame."""
    fw, fh = 64, 32
    nframes = 6
    sheet = Image.new("RGBA", (fw * nframes, fh), (0, 0, 0, 0))

    for f in range(nframes):
        img = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Head moves from top-right to bottom-left
        progress = f / (nframes - 1)
        hx = int(54 - progress * 40)
        hy = int(6 + progress * 18)

        # Luminous head
        draw.point((hx, hy), fill=(255, 255, 255, 255))
        draw.point((hx + 1, hy), fill=(220, 245, 255, 220))
        draw.point((hx, hy + 1), fill=(200, 240, 255, 200))

        # Tail length grows then fades
        tail_len = int(12 + math.sin(progress * math.pi) * 16)
        for t in range(1, tail_len):
            tx = hx + int(t * 1.5)
            ty = hy - int(t * 0.7)
            alpha = int(255 * (1.0 - t / tail_len) * (1.0 - progress * 0.4))
            draw.point((tx, ty), fill=(180, 220, 255, max(0, min(255, alpha))))

        sheet.paste(img, (f * fw, 0))

    sheet.save(os.path.join(OUT_DIR, "shooting_star_anim.png"))
    print("[OK] Generated shooting_star_anim.png")


def generate_alley_cat():
    """6 frames of 32x20 pixel silhouette cat walk cycle."""
    fw, fh = 32, 20
    nframes = 6
    sheet = Image.new("RGBA", (fw * nframes, fh), (0, 0, 0, 0))

    for f in range(nframes):
        img = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Body: sleek black cat with glowing yellow eyes
        bx, by = 14, 11
        draw.ellipse([bx - 6, by - 3, bx + 6, by + 3], fill=(16, 18, 24, 255))

        # Head & ears
        hx, hy = bx - 7, by - 2
        draw.ellipse([hx - 3, hy - 3, hx + 3, hy + 3], fill=(16, 18, 24, 255))
        draw.polygon([(hx - 2, hy - 4), (hx - 4, hy - 7), (hx, hy - 4)], fill=(16, 18, 24, 255))
        draw.polygon([(hx + 1, hy - 4), (hx + 3, hy - 7), (hx - 1, hy - 4)], fill=(16, 18, 24, 255))

        # Glowing green/yellow eye
        draw.point((hx - 2, hy - 1), fill=(180, 255, 80, 255))

        # Tail curved upward
        tail_wave = math.sin((f / nframes) * math.pi * 2) * 2
        draw.line([(bx + 5, by), (bx + 9, by - 4 + tail_wave), (bx + 8, by - 8 + tail_wave)], fill=(16, 18, 24, 255), width=1)

        # 4 legs walking cycle
        leg_offsets = [
            (-2, 2, 2, -2),
            (-1, 1, 1, -1),
            (0, 0, 0, 0),
            (2, -2, -2, 2),
            (1, -1, -1, 1),
            (0, 0, 0, 0)
        ]
        lo = leg_offsets[f]
        # Front-left, front-right, back-left, back-right
        draw.line([(bx - 4, by + 2), (bx - 4 + lo[0], by + 7)], fill=(16, 18, 24, 255))
        draw.line([(bx - 2, by + 2), (bx - 2 + lo[1], by + 7)], fill=(22, 25, 34, 255))
        draw.line([(bx + 3, by + 2), (bx + 3 + lo[2], by + 7)], fill=(16, 18, 24, 255))
        draw.line([(bx + 5, by + 2), (bx + 5 + lo[3], by + 7)], fill=(22, 25, 34, 255))

        sheet.paste(img, (f * fw, 0))

    sheet.save(os.path.join(OUT_DIR, "alley_cat.png"))
    print("[OK] Generated alley_cat.png")


def generate_ufc_fight():
    """6 frames of 96x70 retro pixel MMA broadcast in octagon."""
    fw, fh = 96, 70
    nframes = 6
    sheet = Image.new("RGBA", (fw * nframes, fh), (0, 0, 0, 0))

    for f in range(nframes):
        img = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Octagon cage canvas floor (cyan/grey broadcast tint)
        draw.polygon([(20, 20), (76, 20), (90, 52), (76, 66), (20, 66), (6, 52)], fill=(28, 48, 64, 230), outline=(80, 160, 210, 255))
        # Center red canvas UFC logo
        draw.ellipse([42, 38, 54, 46], fill=(160, 40, 40, 180))

        # Octagon wire fence posts
        for px, py in [(20, 20), (76, 20), (90, 52), (76, 66), (20, 66), (6, 52)]:
            draw.line([(px, py - 12), (px, py)], fill=(90, 170, 220, 200))

        # Fighter 1 (left, trunks red/black)
        f1_x = 40 + int(math.sin(f * 1.1) * 3)
        f1_y = 38
        draw.ellipse([f1_x - 3, f1_y - 8, f1_x + 3, f1_y - 3], fill=(230, 180, 140, 255)) # Head
        draw.rectangle([f1_x - 4, f1_y - 2, f1_x + 4, f1_y + 6], fill=(210, 150, 110, 255)) # Torso
        draw.rectangle([f1_x - 4, f1_y + 7, f1_x + 4, f1_y + 11], fill=(180, 30, 30, 255)) # Shorts
        # Punching arm
        punch = 4 if f in [1, 4] else 1
        draw.line([(f1_x + 3, f1_y), (f1_x + 7 + punch, f1_y - 1)], fill=(210, 150, 110, 255), width=2)

        # Fighter 2 (right, trunks blue/black)
        f2_x = 56 - int(math.cos(f * 1.1) * 2)
        f2_y = 38
        draw.ellipse([f2_x - 3, f2_y - 8, f2_x + 3, f2_y - 3], fill=(220, 170, 130, 255)) # Head
        draw.rectangle([f2_x - 4, f2_y - 2, f2_x + 4, f2_y + 6], fill=(200, 140, 100, 255)) # Torso
        draw.rectangle([f2_x - 4, f2_y + 7, f2_x + 4, f2_y + 11], fill=(30, 50, 180, 255)) # Shorts
        # Guard / counter
        guard = 3 if f in [2, 5] else 0
        draw.line([(f2_x - 3, f2_y), (f2_x - 6 - guard, f2_y - 2)], fill=(200, 140, 100, 255), width=2)

        # Scanlines / broadcast flicker overlay
        for y in range(0, fh, 3):
            draw.line([(0, y), (fw, y)], fill=(120, 210, 255, 25))

        sheet.paste(img, (f * fw, 0))

    sheet.save(os.path.join(OUT_DIR, "ufc_screen_fight.png"))
    print("[OK] Generated ufc_screen_fight.png")


def main():
    generate_spinning_vinyl()
    generate_birds_v_formation()
    generate_shooting_star()
    generate_alley_cat()
    generate_ufc_fight()
    print("\nAll procedural chronicle sprite sheets generated successfully!")


if __name__ == "__main__":
    main()
