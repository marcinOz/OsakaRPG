#!/usr/bin/env python3
"""generate_hd_enemies.py - High-Fidelity Pixel Art Engine for OsakaRPG Enemies & Bosses.
Generates authentic, high-detail pixel art for all 10 enemies/bosses while strictly
preserving 'slacki.png'.

Adheres to OsakaRPG's master Neon-Noir Polish Satire art direction:
- Multi-tier shading ramps (deep dark plum/navy ink shadows, saturated midtones, specular highlights)
- Anti-aliased organic contouring, dithered gradient textures, cloth folds, anatomy
- Contextual atmospheric rim lighting (club neon, phosphor CRT green, beer amber, caution red)
- Exact engine frame dimensions (96x96, 128x128, 144x144) across 2 horizontal frames (rest vs action/breathing).
"""
import os
import math
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "public", "assets", "enemies")
os.makedirs(OUT_DIR, exist_ok=True)

# Master Outline & Shadow Colors
INK = (12, 16, 28, 255)
DARK_PLUM = (28, 16, 26, 255)
SHADOW_TINT = (8, 10, 18, 140)

def save_enemy_sheet(name: str, frame0: Image.Image, frame1: Image.Image, sz: int):
    """Saves a 2-frame horizontal spritesheet (sz*2 x sz)."""
    sheet = Image.new("RGBA", (sz * 2, sz), (0, 0, 0, 0))
    sheet.paste(frame0, (0, 0))
    sheet.paste(frame1, (sz, 0))
    out_path = os.path.join(OUT_DIR, f"{name}.png")
    sheet.save(out_path, "PNG")
    print(f"✓ Generated {name}.png: {sheet.size} ({os.path.getsize(out_path)} bytes)")


# ============================================================================
# 1. BÓL KRĘGOSŁUPA (96x96 x 2 = 192x96)
# Floating anatomical/biomechanical spinal column with herniated glowing ruby
# disc and arcing sciatic nerve lightning.
# ============================================================================
def build_bol_kregoslupa():
    sz = 96
    frames = []
    
    for f in range(2):
        im = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        cx, cy = 48, 48
        
        # Ground / floating contact shadow
        d.ellipse([cx - 22, 84, cx + 22, 92], fill=SHADOW_TINT)
        
        # 8 Vertebral segments from cervical (top) to lumbar/sacrum (bottom)
        # S-curve spine motion
        spine_pts = []
        for i in range(8):
            t = i / 7.0
            # Sinuous curve sway
            sway = math.sin(t * 3.8 + (f * 0.8)) * (3.5 if f == 0 else 5.0)
            compress = -2 if (f == 1 and i >= 5) else 0
            vy = int(14 + i * 8.5 + compress)
            vx = int(cx + sway)
            vw = int(16 + i * 2.2) # widening towards lumbar base
            spine_pts.append((vx, vy, vw, i))
        
        # Draw vertebral bodies
        for vx, vy, vw, idx in spine_pts:
            # Vertebra shadow under
            d.rounded_rectangle([vx - vw//2 - 1, vy - 1, vx + vw//2 + 1, vy + 7], radius=3, fill=INK)
            
            # Bone gradient body (ivory to warm ochre)
            bone_base = (235, 230, 218, 255) if idx < 5 else (245, 235, 215, 255)
            d.rounded_rectangle([vx - vw//2, vy, vx + vw//2, vy + 6], radius=2, fill=bone_base)
            
            # Bone marrow shading & horizontal suture line
            d.line([(vx - vw//2 + 2, vy + 4), (vx + vw//2 - 2, vy + 4)], fill=(185, 175, 155, 255))
            d.line([(vx - vw//2 + 3, vy + 5), (vx + vw//2 - 3, vy + 5)], fill=(145, 135, 120, 255))
            # Bone highlight top rim
            d.line([(vx - vw//2 + 2, vy + 1), (vx + vw//2 - 2, vy + 1)], fill=(255, 255, 250, 255))
            
            # Transverse lateral processes (winged side spikes)
            wing_len = 7 + idx
            wing_y_off = -1 if f == 1 else 0
            # Left wing
            d.polygon([
                (vx - vw//2, vy + 2),
                (vx - vw//2 - wing_len, vy + 1 + wing_y_off),
                (vx - vw//2 - wing_len + 2, vy + 4 + wing_y_off),
                (vx - vw//2, vy + 5)
            ], fill=(210, 205, 190, 255), outline=INK)
            d.line([(vx - vw//2, vy + 2), (vx - vw//2 - wing_len + 1, vy + 2 + wing_y_off)], fill=(255, 255, 255, 255))
            # Right wing
            d.polygon([
                (vx + vw//2, vy + 2),
                (vx + vw//2 + wing_len, vy + 1 + wing_y_off),
                (vx + vw//2 + wing_len - 2, vy + 4 + wing_y_off),
                (vx + vw//2, vy + 5)
            ], fill=(200, 195, 180, 255), outline=INK)
            d.line([(vx + vw//2, vy + 2), (vx + vw//2 + wing_len - 1, vy + 2 + wing_y_off)], fill=(255, 255, 255, 255))
            
            # Intervertebral discs
            if idx < 7:
                ny = vy + 6
                # L4-L5 and L5-S1 are severely inflamed hernia discs!
                if idx >= 4:
                    disc_pulse = 2 if f == 1 else 0
                    disc_w = vw - 2 + disc_pulse
                    # Outer fiery aura
                    d.ellipse([vx - disc_w//2 - 2, ny - 1, vx + disc_w//2 + 2, ny + 5], fill=(255, 30, 60, 160))
                    # Molten red/ruby core
                    d.rounded_rectangle([vx - disc_w//2, ny, vx + disc_w//2, ny + 4], radius=2, fill=(240, 30, 50, 255), outline=DARK_PLUM)
                    # Intense inflammatory hot center
                    d.line([(vx - disc_w//4, ny + 2), (vx + disc_w//4, ny + 2)], fill=(255, 220, 80, 255))
                else:
                    # Healthy cervical/thoracic discs
                    d.rounded_rectangle([vx - vw//3, ny, vx + vw//3, ny + 3], radius=1, fill=(80, 175, 210, 255), outline=INK)
                    d.point((vx, ny + 1), fill=(160, 235, 255, 255))

        # Sciatic nerve electrical pain discharge arcing outward
        sparks = [
            (cx - 14, 62, cx - 34, 76, cx - 26, 88),
            (cx + 14, 62, cx + 36, 72, cx + 28, 86),
            (cx - 8, 45, cx - 28, 40, cx - 22, 32),
            (cx + 8, 45, cx + 30, 48, cx + 38, 42),
        ]
        spark_color = (255, 235, 90, 255) if f == 1 else (255, 50, 80, 255)
        spark_core = (255, 255, 255, 255)
        for x0, y0, x1, y1, x2, y2 in sparks:
            jitter = (3 if f == 1 else -2)
            d.line([(x0, y0), (x1 + jitter, y1), (x2, y2 + jitter)], fill=spark_color, width=2)
            d.line([(x0, y0), (x1 + jitter, y1), (x2, y2 + jitter)], fill=spark_core, width=1)
            d.point((x1 + jitter, y1), fill=(255, 255, 255, 255))
            d.point((x2, y2 + jitter), fill=spark_color)
            
        frames.append(im)
        
    save_enemy_sheet("bolKregoslupa", frames[0], frames[1], sz)


# ============================================================================
# 2. SĄSIAD SZKODNIK (128x128 x 2 = 256x128) - Boss
# Plaid flannel bathrobe, varicose bare legs, kapcie slippers, walrus mustache,
# pointing finger, waving birch broom with anger steam.
# ============================================================================
def build_sasiad_szkodnik():
    sz = 128
    frames = []
    
    for f in range(2):
        im = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        
        # Ground shadow
        d.ellipse([32, 114, 96, 126], fill=SHADOW_TINT)
        
        # Frame animation: Frame 0 scowling ready stance; Frame 1 stomping forward, broom raised
        bob = -2 if f == 1 else 0
        broom_angle = -38 if f == 1 else -20
        
        # 1. Slippers ("Kapcie w kratę")
        # Left slipper
        d.polygon([(36, 115), (56, 115), (58, 124), (34, 124)], fill=(65, 70, 80, 255), outline=INK)
        d.polygon([(38, 116), (54, 116), (56, 121), (36, 121)], fill=(125, 45, 55, 255)) # red plaid felt
        d.line([(38, 118), (54, 118)], fill=(220, 190, 80, 180)) # gold stripe
        # Right slipper (stomping in frame 1)
        step_r = -3 if f == 1 else 0
        d.polygon([(72, 115 + step_r), (92, 115 + step_r), (94, 124 + step_r), (70, 124 + step_r)], fill=(65, 70, 80, 255), outline=INK)
        d.polygon([(74, 116 + step_r), (90, 116 + step_r), (92, 121 + step_r), (72, 121 + step_r)], fill=(125, 45, 55, 255))
        d.line([(74, 118 + step_r), (90, 118 + step_r)], fill=(220, 190, 80, 180))
        
        # 2. Bare hairy legs with knee shading
        # Left leg
        d.rectangle([42, 94 + bob, 50, 116], fill=(225, 175, 140, 255), outline=INK)
        d.line([(43, 98 + bob), (48, 98 + bob)], fill=(195, 140, 110, 255)) # patella crease
        # Varicose vein
        d.line([(45, 102 + bob), (48, 106 + bob), (44, 111 + bob)], fill=(80, 95, 160, 220))
        for hy in range(97, 115, 3): d.point((43, hy + bob), fill=(55, 40, 30, 255))
        # Right leg
        d.rectangle([76, 94 + bob, 84, 116 + step_r], fill=(225, 175, 140, 255), outline=INK)
        d.line([(77, 98 + bob), (82, 98 + bob)], fill=(195, 140, 110, 255))
        for hy in range(98, 114, 3): d.point((83, hy + bob), fill=(55, 40, 30, 255))
        
        # 3. Flannel Bathrobe Body (Rich multi-tone tartan plaid over potbelly)
        robe_pts = [
            (32, 46 + bob), (96, 46 + bob),
            (102, 102 + bob), (26, 102 + bob)
        ]
        d.polygon(robe_pts, fill=(145, 30, 42, 255), outline=INK)
        # Deep shadow underside
        d.polygon([(26, 96 + bob), (102, 96 + bob), (102, 102 + bob), (26, 102 + bob)], fill=(90, 18, 26, 255))
        
        # Tartan cross-weave grid (dark navy vertical/horizontal + mustard threads)
        for gx in range(32, 98, 10):
            d.line([(gx, 46 + bob), (gx - 5, 102 + bob)], fill=(28, 38, 65, 200), width=2)
            d.line([(gx + 3, 46 + bob), (gx - 2, 102 + bob)], fill=(225, 185, 55, 160), width=1)
        for gy in range(52, 102, 10):
            d.line([(28, gy + bob), (100, gy + bob)], fill=(28, 38, 65, 200), width=2)
            d.line([(28, gy + 3 + bob), (100, gy + 3 + bob)], fill=(225, 185, 55, 160), width=1)
            
        # Potbelly volume highlights
        d.ellipse([50, 68 + bob, 82, 92 + bob], fill=(175, 45, 58, 140))
        
        # Ribbed white undershirt showing at neckline
        d.polygon([(52, 46 + bob), (64, 68 + bob), (76, 46 + bob)], fill=(215, 210, 200, 255), outline=INK)
        # Stains on undershirt
        d.ellipse([58, 54 + bob, 63, 58 + bob], fill=(185, 140, 80, 200)) # mustard/beer stain
        
        # Bathrobe lapel collar V
        d.line([(50, 46 + bob), (64, 76 + bob)], fill=(95, 20, 30, 255), width=4)
        d.line([(78, 46 + bob), (64, 76 + bob)], fill=(95, 20, 30, 255), width=4)
        
        # Tied bathrobe belt sash
        d.rectangle([30, 78 + bob, 98, 85 + bob], fill=(95, 20, 30, 255), outline=INK)
        d.polygon([(56, 85 + bob), (64, 98 + bob), (60, 99 + bob), (52, 85 + bob)], fill=(95, 20, 30, 255), outline=INK)
        d.polygon([(62, 85 + bob), (70, 96 + bob), (66, 97 + bob), (58, 85 + bob)], fill=(95, 20, 30, 255), outline=INK)

        # 4. Head, Balding Dome & Expressive Angry Face
        hy = 32 + bob
        # Thick neck
        d.rectangle([56, hy + 8, 72, hy + 18], fill=(225, 175, 140, 255), outline=INK)
        d.line([(57, hy + 16), (71, hy + 16)], fill=(185, 130, 100, 255))
        
        # Head oval
        d.ellipse([46, hy - 14, 82, hy + 14], fill=(235, 185, 150, 255), outline=INK)
        # Specular bald dome sheen
        d.ellipse([52, hy - 13, 74, hy - 6], fill=(255, 225, 205, 255))
        d.ellipse([58, hy - 12, 68, hy - 8], fill=(255, 255, 255, 255))
        # Grey side hair wisps
        for wy in range(hy - 6, hy + 8, 3):
            d.line([(44, wy), (40, wy - 2)], fill=(190, 195, 205, 255), width=2)
            d.line([(84, wy), (88, wy - 2)], fill=(190, 195, 205, 255), width=2)
            
        # Furious furrowed eyebrows (heavy angry diagonal)
        d.line([(50, hy - 2), (60, hy + 2)], fill=(65, 45, 30, 255), width=3)
        d.line([(78, hy - 2), (68, hy + 2)], fill=(65, 45, 30, 255), width=3)
        # Deep brow wrinkles
        d.line([(56, hy - 5), (72, hy - 5)], fill=(190, 135, 105, 255), width=2)
        # Beady bloodshot eyes
        d.rectangle([53, hy + 2, 58, hy + 5], fill=(255, 255, 255, 255), outline=INK)
        d.point((56, hy + 3), fill=(10, 10, 10, 255))
        d.point((54, hy + 3), fill=(255, 60, 60, 255)) # bloodshot vein
        d.rectangle([70, hy + 2, 75, hy + 5], fill=(255, 255, 255, 255), outline=INK)
        d.point((72, hy + 3), fill=(10, 10, 10, 255))
        d.point((74, hy + 3), fill=(255, 60, 60, 255))
        
        # Bulbous red nose
        d.ellipse([60, hy + 4, 68, hy + 10], fill=(235, 115, 105, 255), outline=(175, 65, 60, 255))
        d.point((63, hy + 6), fill=(255, 180, 170, 255)) # nose highlight
        
        # Giant grey/brown walrus mustache
        mustache_pts = [
            (48, hy + 10), (64, hy + 17), (80, hy + 10),
            (76, hy + 8), (64, hy + 10), (52, hy + 8)
        ]
        d.polygon(mustache_pts, fill=(165, 170, 180, 255), outline=INK)
        d.line([(52, hy + 10), (76, hy + 10)], fill=(210, 215, 225, 255))
        
        # Screaming open mouth under mustache with a crooked yellow tooth
        d.ellipse([58, hy + 14, 70, hy + 21], fill=(70, 15, 15, 255), outline=INK)
        d.rectangle([62, hy + 14, 65, hy + 17], fill=(245, 235, 170, 255)) # yellow tooth
        
        # 5. Left Arm: Pointing Accusing Gnarled Finger
        arm_l_pts = [(34, 52 + bob), (16, 64 + bob), (18, 72 + bob), (34, 64 + bob)]
        d.polygon(arm_l_pts, fill=(145, 30, 42, 255), outline=INK)
        # Bare hand & pointing finger
        d.ellipse([10, 64 + bob, 18, 74 + bob], fill=(235, 185, 150, 255), outline=INK)
        d.line([(12, 68 + bob), (2, 65 + bob)], fill=(235, 185, 150, 255), width=3)
        d.point((2, 65 + bob), fill=INK) # fingernail
        
        # 6. Right Arm & Birch Broom ("Miotła brzozowa")
        # Shoulder and upper arm
        arm_rx = 94
        arm_ry = 54 + bob - (4 if f == 1 else 0)
        d.polygon([(88, 50 + bob), (arm_rx + 8, arm_ry), (arm_rx + 4, arm_ry + 10), (86, 62 + bob)], fill=(145, 30, 42, 255), outline=INK)
        # Clenched fist gripping broom handle
        d.ellipse([arm_rx + 4, arm_ry - 4, arm_rx + 16, arm_ry + 8], fill=(235, 185, 150, 255), outline=INK)
        
        # Broom stick calculation
        rad = math.radians(broom_angle)
        sx0 = arm_rx + 10
        sy0 = arm_ry + 2
        slen = 62
        sx1 = sx0 + math.cos(rad) * slen
        sy1 = sy0 + math.sin(rad) * slen
        # Wooden broom pole
        d.line([(sx0 - math.cos(rad) * 18, sy0 - math.sin(rad) * 18), (sx1, sy1)], fill=(125, 80, 45, 255), width=4)
        d.line([(sx0 - math.cos(rad) * 18, sy0 - math.sin(rad) * 18), (sx1, sy1)], fill=(175, 125, 80, 255), width=1) # woodgrain highlight
        
        # Straw bristle head
        bx, by = sx1, sy1
        bristles = [
            (bx, by),
            (bx + 16, by - 16),
            (bx + 28, by - 8),
            (bx + 12, by + 10)
        ]
        d.polygon(bristles, fill=(225, 195, 75, 255), outline=INK)
        # Wire binding
        d.line([(bx + 4, by - 4), (bx + 8, by + 4)], fill=(40, 40, 40, 255), width=3)
        # Bristle texture
        for bidx in range(4):
            d.line([(bx + 4 + bidx * 3, by - 6 + bidx * 2), (bx + 18 + bidx * 3, by - 14 + bidx * 3)], fill=(185, 155, 50, 255))
            
        # Anger steam puffs from ears if frame 1
        if f == 1:
            d.arc([30, hy - 18, 42, hy - 6], 0, 360, fill=(245, 245, 255, 220), width=2)
            d.arc([86, hy - 18, 98, hy - 6], 0, 360, fill=(245, 245, 255, 220), width=2)
            
        frames.append(im)
        
    save_enemy_sheet("sasiadSzkodnik", frames[0], frames[1], sz)


# ============================================================================
# 3. AUTO-TUNE HIPSTER (128x128 x 2 = 256x128)
# Mustard rolled beanie, manicured beard, wire glasses, buffalo plaid flannel,
# selvedge denim, open MacBook with glowing multi-color DAW equalizer visualizer.
# ============================================================================
def build_autotune_hipster():
    sz = 128
    frames = []
    
    for f in range(2):
        im = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        
        # Ground shadow
        d.ellipse([34, 116, 94, 126], fill=SHADOW_TINT)
        
        bob = -2 if f == 1 else 0
        
        # 1. Bar Stool & Cuffed Raw Denim Jeans
        # Wooden stool legs
        d.line([(38, 96), (32, 122)], fill=(110, 65, 35, 255), width=3)
        d.line([(90, 96), (96, 122)], fill=(110, 65, 35, 255), width=3)
        d.line([(48, 102), (48, 122)], fill=(75, 45, 25, 255), width=2)
        d.line([(80, 102), (80, 122)], fill=(75, 45, 25, 255), width=2)
        d.line([(34, 112), (94, 112)], fill=(110, 65, 35, 255), width=2) # stool rung
        
        # Raw denim legs
        d.rectangle([44, 90 + bob, 56, 114], fill=(28, 38, 58, 255), outline=INK)
        d.rectangle([68, 90 + bob, 80, 114], fill=(28, 38, 58, 255), outline=INK)
        # Selvedge double cuff turn-up
        d.rectangle([44, 110, 56, 115], fill=(210, 205, 190, 255), outline=INK)
        d.line([(45, 111), (45, 114)], fill=(225, 45, 55, 255)) # red selvedge stitch!
        d.rectangle([68, 110, 80, 115], fill=(210, 205, 190, 255), outline=INK)
        d.line([(69, 111), (69, 114)], fill=(225, 45, 55, 255))
        
        # Red-Wing style oiled leather heritage boots
        d.polygon([(42, 115), (58, 115), (57, 124), (40, 124)], fill=(135, 60, 28, 255), outline=INK)
        d.line([(40, 124), (57, 124)], fill=(230, 225, 210, 255), width=2) # white vibram wedge sole
        d.polygon([(66, 115), (82, 115), (81, 124), (64, 124)], fill=(135, 60, 28, 255), outline=INK)
        d.line([(64, 124), (81, 124)], fill=(230, 225, 210, 255), width=2)
        
        # 2. Buffalo Plaid Heavy Green/Black Flannel
        d.polygon([
            (34, 46 + bob), (94, 46 + bob),
            (90, 94 + bob), (38, 94 + bob)
        ], fill=(32, 78, 48, 255), outline=INK)
        # Black block checks
        for bx in range(36, 92, 10):
            d.line([(bx, 46 + bob), (bx, 94 + bob)], fill=(16, 26, 18, 220), width=4)
        for by in range(52, 94, 10):
            d.line([(36, by + bob), (92, by + bob)], fill=(16, 26, 18, 220), width=4)
            
        # Vintage synth tee peeking through unbuttoned top
        d.polygon([(58, 46 + bob), (70, 46 + bob), (64, 62 + bob)], fill=(245, 240, 230, 255))
        d.line([(60, 52 + bob), (68, 52 + bob)], fill=(255, 80, 140, 255)) # neon synth wave line
        
        # DJ Studio Monitor Headphones around neck
        d.arc([42, 38 + bob, 86, 62 + bob], 0, 180, fill=(35, 38, 46, 255), width=6)
        d.ellipse([34, 44 + bob, 46, 58 + bob], fill=(55, 60, 72, 255), outline=INK)
        d.ellipse([82, 44 + bob, 94, 58 + bob], fill=(55, 60, 72, 255), outline=INK)
        
        # 3. Head, Mustard Beanie & Groomed Beard
        hy = 32 + bob
        d.rectangle([56, hy + 6, 72, hy + 16], fill=(235, 185, 145, 255), outline=INK)
        d.ellipse([48, hy - 10, 80, hy + 14], fill=(235, 185, 145, 255), outline=INK)
        
        # Rolled Mustard Fisherman Beanie perched on crown
        d.ellipse([46, hy - 18, 82, hy - 4], fill=(225, 160, 25, 255), outline=INK)
        d.rectangle([46, hy - 11, 82, hy - 5], fill=(245, 180, 40, 255), outline=INK) # ribbed cuff
        for rx in range(48, 80, 4): d.line([(rx, hy - 10), (rx, hy - 6)], fill=(185, 125, 15, 255))
        
        # Manicured full hipster beard with gradient
        beard_pts = [
            (48, hy + 2), (54, hy + 18), (74, hy + 18), (80, hy + 2),
            (72, hy + 6), (56, hy + 6)
        ]
        d.polygon(beard_pts, fill=(75, 48, 30, 255), outline=INK)
        d.polygon([(56, hy + 8), (64, hy + 16), (72, hy + 8)], fill=(105, 68, 42, 255)) # beard volume highlight
        
        # Wire-rim round glasses
        d.ellipse([50, hy - 4, 61, hy + 5], fill=(240, 245, 255, 160), outline=(60, 40, 25, 255))
        d.ellipse([67, hy - 4, 78, hy + 5], fill=(240, 245, 255, 160), outline=(60, 40, 25, 255))
        d.line([(61, hy), (67, hy)], fill=(60, 40, 25, 255), width=2)
        # Blue screen reflection glint in glasses
        d.point((53, hy - 1), fill=(100, 220, 255, 255))
        d.point((70, hy - 1), fill=(100, 220, 255, 255))
        d.point((57, hy + 1), fill=(20, 20, 20, 255))
        d.point((74, hy + 1), fill=(20, 20, 20, 255))
        
        # 4. Open Aluminum MacBook with Glowing Neon DAW Equalizer
        # Base keyboard chassis held by hands
        mb_y = 68 + bob
        d.polygon([(30, mb_y + 12), (98, mb_y + 12), (102, mb_y + 24), (26, mb_y + 24)], fill=(195, 200, 210, 255), outline=INK)
        # Trackpad
        d.rectangle([54, mb_y + 17, 74, mb_y + 22], fill=(165, 170, 180, 255), outline=(130, 135, 145, 255))
        # Hands resting on laptop edges
        d.ellipse([24, mb_y + 10, 34, mb_y + 20], fill=(235, 185, 145, 255), outline=INK)
        d.ellipse([94, mb_y + 10, 104, mb_y + 20], fill=(235, 185, 145, 255), outline=INK)
        
        # Screen lid
        d.polygon([(34, mb_y - 12), (94, mb_y - 12), (98, mb_y + 12), (30, mb_y + 12)], fill=(25, 28, 36, 255), outline=INK)
        # Inner screen bezel
        d.rectangle([36, mb_y - 10, 92, mb_y + 10], fill=(12, 14, 22, 255))
        
        # Neon DAW Spectrum Visualizer Bars
        bar_colors = [
            (0, 245, 212, 255),   # Cyan
            (123, 44, 191, 255),  # Violet
            (247, 37, 133, 255),  # Magenta
            (255, 230, 109, 255), # Yellow
            (76, 201, 240, 255),  # Sky blue
        ]
        for bidx in range(9):
            bx = 40 + bidx * 5
            # Dynamic equalizer height variation between frames
            bar_h = ((bidx * 4 + f * 6) % 14) + 3
            col = bar_colors[(bidx + f) % len(bar_colors)]
            d.line([(bx, mb_y + 8), (bx, mb_y + 8 - bar_h)], fill=col, width=2)
            d.point((bx, mb_y + 7 - bar_h), fill=(255, 255, 255, 255)) # peak hold dot
            
        # Audio wave circle FX radiating from laptop if frame 1
        if f == 1:
            d.arc([22, mb_y - 20, 106, mb_y + 20], 180, 360, fill=(0, 245, 212, 180), width=2)
            
        frames.append(im)
        
    save_enemy_sheet("autoTuneHipster", frames[0], frames[1], sz)


# ============================================================================
# 4. ZBYT DROGIE PIWO (128x128 x 2 = 256x128)
# Sentient, haughty craft IPA in a stemmed Belgian Teku glass, glowing amber
# liquid, overflowing foamy monocle face, dangling 48 zł kraft price tag.
# ============================================================================
def build_drogie_piwo():
    sz = 128
    frames = []
    
    for f in range(2):
        im = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        
        # Ground shadow
        d.ellipse([40, 118, 88, 126], fill=SHADOW_TINT)
        
        bob = -2 if f == 1 else 0
        
        # 1. Stemmed Teku Glass Base & Stem
        d.ellipse([46, 114, 82, 122], fill=(225, 238, 245, 120), outline=INK)
        d.ellipse([50, 116, 78, 120], fill=(255, 255, 255, 180)) # base rim highlight
        # Slender glass stem
        d.rectangle([61, 88 + bob, 67, 116], fill=(210, 230, 240, 160), outline=INK)
        d.line([(63, 88 + bob), (63, 115)], fill=(255, 255, 255, 220))
        
        # 2. Teku Chalice Bowl (Angular flared glass)
        chalice_pts = [
            (38, 44 + bob), (90, 44 + bob),
            (96, 72 + bob), (68, 88 + bob),
            (60, 88 + bob), (32, 72 + bob)
        ]
        # Glass backdrop
        d.polygon(chalice_pts, fill=(20, 28, 40, 200), outline=INK)
        
        # Glowing Hazy DDH Amber IPA Liquid Body
        liquid_pts = [
            (40, 52 + bob), (88, 52 + bob),
            (93, 70 + bob), (66, 86 + bob),
            (62, 86 + bob), (35, 70 + bob)
        ]
        d.polygon(liquid_pts, fill=(225, 135, 25, 255))
        # Inner honey-gold core gradient
        d.polygon([
            (46, 56 + bob), (82, 56 + bob),
            (86, 70 + bob), (65, 82 + bob),
            (63, 82 + bob), (42, 70 + bob)
        ], fill=(250, 185, 45, 255))
        
        # Carbonation Effervescence Micro-bubbles
        for bx, by in [(48, 76), (56, 68), (64, 80), (72, 70), (80, 75), (52, 60), (76, 62)]:
            b_shift = -3 if f == 1 else 0
            d.point((bx, by + bob + b_shift), fill=(255, 245, 180, 240))
            d.point((bx + 1, by + bob + b_shift), fill=(255, 255, 255, 200))
            
        # Curved Glass Specular Highlight Sheen
        d.line([(36, 48 + bob), (34, 70 + bob), (61, 87 + bob)], fill=(255, 255, 255, 220), width=2)
        d.line([(92, 48 + bob), (94, 70 + bob)], fill=(255, 255, 255, 140), width=1)
        
        # 3. Dense Creamy Nitro Foam Head & Haughty Aristocrat Face
        # Meringue-like foam overflowing rim
        foam_y = 42 + bob
        # Main dense foam puff
        d.ellipse([34, foam_y - 18, 94, foam_y + 12], fill=(252, 250, 240, 255), outline=INK)
        d.ellipse([42, foam_y - 24, 86, foam_y - 4], fill=(255, 255, 250, 255), outline=INK)
        # Foam drip overflowing down left edge
        d.polygon([(34, foam_y), (38, foam_y + 22), (42, foam_y)], fill=(252, 250, 240, 255), outline=INK)
        
        # Pompous Expressive Facial Features inside the Foam
        fy = foam_y - 6
        # Scowling foam brow
        d.line([(48, fy - 4), (58, fy)], fill=(185, 175, 155, 255), width=2)
        d.line([(80, fy - 4), (70, fy)], fill=(185, 175, 155, 255), width=2)
        
        # Left eye: Golden Monocle!
        d.ellipse([46, fy - 1, 58, fy + 11], fill=(255, 255, 255, 255), outline=(215, 165, 30, 255))
        d.ellipse([47, fy, 57, fy + 10], fill=(245, 245, 255, 200), outline=(215, 165, 30, 255))
        d.point((53, fy + 4), fill=(20, 20, 20, 255)) # pupil
        # Monocle gold chain dangling down glass
        d.line([(58, fy + 6), (62, fy + 16), (58, fy + 26)], fill=(215, 165, 30, 255), width=1)
        
        # Right eye: Half-closed condescending squint
        d.line([(68, fy + 4), (78, fy + 3)], fill=INK, width=2)
        d.point((73, fy + 5), fill=(20, 20, 20, 255))
        
        # Aristocratic Hop-Cone Mustache
        must_pts = [
            (48, fy + 12), (64, fy + 18), (80, fy + 12),
            (74, fy + 10), (64, fy + 13), (54, fy + 10)
        ]
        d.polygon(must_pts, fill=(95, 165, 60, 255), outline=INK) # green hop cones!
        d.point((64, fy + 15), fill=(160, 225, 90, 255))
        
        # 4. Dangling Artisanal Kraft Price Tag ("48 zł / 0.33L")
        # Hemp twine tied around stem
        d.line([(62, 88 + bob), (48, 92 + bob)], fill=(145, 115, 75, 255), width=2)
        # Fluttering kraft paper tag
        tag_angle = 6 if f == 1 else 0
        tag_x0, tag_y0 = 18, 90 + bob + tag_angle
        tag_x1, tag_y1 = 48, 114 + bob + tag_angle
        d.polygon([
            (tag_x0 + 4, tag_y0), (tag_x1, tag_y0),
            (tag_x1, tag_y1), (tag_x0, tag_y1 - 6)
        ], fill=(215, 185, 140, 255), outline=INK)
        # String hole
        d.ellipse([tag_x1 - 6, tag_y0 + 2, tag_x1 - 2, tag_y0 + 6], fill=(60, 45, 30, 255))
        # Price text
        d.text((tag_x0 + 4, tag_y0 + 3), "48zł", fill=(160, 20, 25, 255))
        d.text((tag_x0 + 4, tag_y0 + 12), "0.33L", fill=(40, 35, 30, 255))
        
        # Fizzy hop aroma citrus sparkles if frame 1
        if f == 1:
            d.point((38, foam_y - 26), fill=(255, 220, 80, 255))
            d.point((88, foam_y - 24), fill=(255, 220, 80, 255))
            d.line([(60, foam_y - 28), (64, foam_y - 32)], fill=(255, 240, 140, 255))
            
        frames.append(im)
        
    save_enemy_sheet("drogiePiwo", frames[0], frames[1], sz)


# ============================================================================
# 5. STRAŻNIK MIEJSKI (128x128 x 2 = 256x128)
# High-vis neon chartreuse tactical vest with 3M retroreflective silver stripes,
# checkered crown cap, heavy tonfa baton, glowing citation ticket book.
# ============================================================================
def build_straznik():
    sz = 128
    frames = []
    
    for f in range(2):
        im = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        
        # Ground shadow
        d.ellipse([34, 116, 94, 126], fill=SHADOW_TINT)
        
        bob = -2 if f == 1 else 0
        
        # 1. Dark Navy Patrol Trousers & Heavy Duty Boots
        d.rectangle([46, 92 + bob, 58, 116], fill=(18, 24, 42, 255), outline=INK)
        d.rectangle([70, 92 + bob, 82, 116], fill=(18, 24, 42, 255), outline=INK)
        # Heavy black polished boots
        d.polygon([(42, 115), (60, 115), (59, 125), (40, 125)], fill=(12, 15, 22, 255), outline=INK)
        d.line([(42, 116), (58, 116)], fill=(75, 85, 105, 255)) # leather shine
        d.polygon([(68, 115), (86, 115), (85, 125), (66, 125)], fill=(12, 15, 22, 255), outline=INK)
        d.line([(68, 116), (84, 116)], fill=(75, 85, 105, 255))
        
        # 2. Dark Navy Uniform & Fluorescent Lime High-Vis Tactical Vest
        # Base navy jacket
        d.polygon([(34, 46 + bob), (94, 46 + bob), (90, 94 + bob), (38, 94 + bob)], fill=(18, 24, 42, 255), outline=INK)
        
        # High-Vis Neon Chartreuse Vest
        vest_pts = [(38, 48 + bob), (90, 48 + bob), (86, 92 + bob), (42, 92 + bob)]
        d.polygon(vest_pts, fill=(215, 245, 30, 255), outline=INK)
        # Vest shoulder straps
        d.polygon([(42, 48 + bob), (52, 48 + bob), (50, 68 + bob), (42, 68 + bob)], fill=(195, 225, 25, 255))
        d.polygon([(86, 48 + bob), (76, 48 + bob), (78, 68 + bob), (86, 68 + bob)], fill=(195, 225, 25, 255))
        
        # 3M Retroreflective Silver/White Prismatic Stripes
        d.rectangle([40, 68 + bob, 88, 74 + bob], fill=(235, 245, 255, 255), outline=(150, 170, 190, 255))
        d.rectangle([42, 80 + bob, 86, 86 + bob], fill=(235, 245, 255, 255), outline=(150, 170, 190, 255))
        # Silver micro-prismatic glint
        d.line([(44, 71 + bob), (84, 71 + bob)], fill=(255, 255, 255, 255))
        
        # Duty belt with equipment & radio lapel mic
        d.rectangle([36, 90 + bob, 92, 96 + bob], fill=(14, 16, 22, 255), outline=INK)
        # Shoulder radio mic with coiled black cord
        d.rectangle([42, 52 + bob, 48, 60 + bob], fill=(25, 28, 35, 255), outline=INK)
        d.arc([44, 58 + bob, 52, 74 + bob], 90, 270, fill=(20, 20, 20, 255), width=2)
        
        # 3. Head & Polish Straż Miejska Checkered Cap
        hy = 32 + bob
        d.rectangle([58, hy + 6, 70, hy + 16], fill=(225, 175, 140, 255), outline=INK)
        d.ellipse([50, hy - 8, 78, hy + 14], fill=(225, 175, 140, 255), outline=INK)
        
        # Strict scowling facial features
        d.line([(54, hy + 2), (60, hy + 5)], fill=(65, 45, 30, 255), width=2)
        d.line([(74, hy + 2), (68, hy + 5)], fill=(65, 45, 30, 255), width=2)
        d.point((57, hy + 4), fill=(10, 10, 10, 255))
        d.point((71, hy + 4), fill=(10, 10, 10, 255))
        d.line([(58, hy + 11), (70, hy + 10)], fill=(125, 55, 45, 255), width=2) # clenched jaw
        
        # Peaked Straż Miejska Cap
        d.ellipse([46, hy - 16, 82, hy - 4], fill=(16, 22, 38, 255), outline=INK)
        # Checkered Crown Band (Black and White alternating squares)
        check_w = 6
        for cidx, cx in enumerate(range(48, 80, check_w)):
            col = (255, 255, 255, 255) if cidx % 2 == 0 else (12, 15, 22, 255)
            d.rectangle([cx, hy - 8, cx + check_w, hy - 4], fill=col)
        # Shiny black vinyl visor
        d.polygon([(44, hy - 4), (84, hy - 4), (78, hy + 1), (50, hy + 1)], fill=(10, 12, 18, 255), outline=INK)
        d.line([(48, hy - 3), (80, hy - 3)], fill=(120, 135, 160, 255)) # visor reflection
        
        # 4. Left Hand: Orange Citation Ticket Book ("Mandatownik")
        d.polygon([(36, 56 + bob), (22, 66 + bob), (26, 76 + bob), (38, 64 + bob)], fill=(215, 245, 30, 255), outline=INK)
        # Ticket clipboard
        tb_y = 62 + bob
        d.polygon([(12, tb_y), (30, tb_y - 6), (36, tb_y + 18), (18, tb_y + 24)], fill=(185, 75, 25, 255), outline=INK)
        d.polygon([(14, tb_y + 2), (28, tb_y - 4), (33, tb_y + 16), (19, tb_y + 22)], fill=(255, 250, 240, 255))
        # Orange "MANDAT" header
        d.line([(16, tb_y + 4), (26, tb_y)], fill=(255, 95, 35, 255), width=2)
        # Ballpoint pen in hand
        d.line([(24, tb_y + 8), (30, tb_y + 4)], fill=(30, 80, 210, 255), width=2)
        
        # 5. Right Hand: Heavy Black Rubber Tonfa Baton
        baton_swing = 10 if f == 1 else 0
        d.polygon([(90, 54 + bob), (104, 62 + bob - baton_swing), (106, 70 + bob - baton_swing), (92, 62 + bob)], fill=(215, 245, 30, 255), outline=INK)
        d.ellipse([102, 60 + bob - baton_swing, 110, 68 + bob - baton_swing], fill=(225, 175, 140, 255), outline=INK)
        # Rubber Tonfa
        bx0 = 106
        by0 = 64 + bob - baton_swing
        d.line([(bx0, by0), (bx0 + 16, by0 - 24)], fill=(20, 22, 28, 255), width=5) # long shaft
        d.line([(bx0, by0), (bx0 - 6, by0 + 12)], fill=(20, 22, 28, 255), width=5) # side grip
        d.line([(bx0 + 2, by0 - 2), (bx0 + 14, by0 - 22)], fill=(75, 80, 95, 255), width=1) # rubber sheen
        
        frames.append(im)
        
    save_enemy_sheet("straznik", frames[0], frames[1], sz)


# ============================================================================
# 6. SZEF OCHRONY "KARK" (128x128 x 2 = 256x128) - Boss
# 130kg muscular fortress, monolithic neck, mirrored aviators with club neon
# magenta/cyan reflection, VIP leather bomber jacket, silver chain, crossed arms.
# ============================================================================
def build_kark():
    sz = 128
    frames = []
    
    for f in range(2):
        im = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        
        # Huge ground shadow
        d.ellipse([26, 116, 102, 126], fill=SHADOW_TINT)
        
        bob = -2 if f == 1 else 0
        
        # 1. Heavy Tactical Pants & Steel-Toe Combat Boots
        d.rectangle([38, 92 + bob, 58, 116], fill=(22, 24, 30, 255), outline=INK)
        d.rectangle([70, 92 + bob, 90, 116], fill=(22, 24, 30, 255), outline=INK)
        # Heavy boots
        d.polygon([(34, 114), (60, 114), (58, 125), (32, 125)], fill=(12, 14, 18, 255), outline=INK)
        d.polygon([(68, 114), (94, 114), (92, 125), (66, 125)], fill=(12, 14, 18, 255), outline=INK)
        d.line([(34, 124), (58, 124)], fill=(70, 75, 85, 255), width=2)
        d.line([(68, 124), (92, 124)], fill=(70, 75, 85, 255), width=2)
        
        # 2. Enormous Broad Shoulders & Quilted Leather VIP Bomber Jacket
        jy = 40 + bob
        # Massive torso trapezoid
        d.polygon([(16, jy + 14), (112, jy + 14), (100, 94 + bob), (28, 94 + bob)], fill=(18, 20, 26, 255), outline=INK)
        # Quilted leather shoulder padding
        d.line([(20, jy + 18), (38, jy + 32)], fill=(45, 50, 62, 255), width=2)
        d.line([(108, jy + 18), (90, jy + 32)], fill=(45, 50, 62, 255), width=2)
        # Golden embroidered "VIP OCHRONA" Shield Crest
        d.polygon([(36, jy + 26), (46, jy + 26), (41, jy + 38)], fill=(235, 195, 45, 255), outline=INK)
        d.point((41, jy + 30), fill=(255, 255, 255, 255))
        
        # Tight black compression shirt defining bulging pectorals
        d.line([(50, jy + 30), (78, jy + 30)], fill=(40, 45, 55, 255), width=2) # chest crease
        # Heavy Cuban link silver chain
        d.arc([52, jy + 16, 76, jy + 36], 0, 180, fill=(215, 225, 235, 255), width=3)
        for cx in range(54, 76, 4): d.point((cx, jy + 24), fill=(255, 255, 255, 255))
        
        # 3. Crossed Muscular Forearms with Tribal Tattoos & Carbon Knuckle Gloves
        arm_y = 64 + bob
        d.rectangle([30, arm_y, 98, arm_y + 18], fill=(18, 20, 26, 255), outline=INK)
        # Bare muscular forearms
        d.rectangle([34, arm_y + 2, 54, arm_y + 16], fill=(215, 160, 125, 255), outline=INK)
        d.rectangle([74, arm_y + 2, 94, arm_y + 16], fill=(215, 160, 125, 255), outline=INK)
        # Tribal tattoo linework on left forearm
        d.line([(38, arm_y + 4), (46, arm_y + 12), (52, arm_y + 6)], fill=(35, 45, 55, 255), width=2)
        # Bulging vascularity vein on right forearm
        d.line([(78, arm_y + 6), (84, arm_y + 12)], fill=(175, 115, 90, 255))
        # Carbon-knuckle tactical fingerless gloves clenched together
        d.rectangle([52, arm_y + 4, 76, arm_y + 16], fill=(12, 14, 18, 255), outline=INK)
        for kx in range(56, 74, 5):
            d.ellipse([kx, arm_y + 6, kx + 3, arm_y + 10], fill=(85, 90, 105, 255)) # carbon armor studs
            
        # 4. Monolithic Bull Neck & Shaved Buzzcut Skull
        # Neck wider than head
        d.rectangle([46, jy - 6, 82, jy + 16], fill=(215, 160, 125, 255), outline=INK)
        # Trapezius muscle slope
        d.polygon([(28, jy + 14), (50, jy), (50, jy + 14)], fill=(195, 140, 110, 255))
        d.polygon([(100, jy + 14), (78, jy), (78, jy + 14)], fill=(195, 140, 110, 255))
        
        # Head with squared brutal jaw
        hy = jy - 14
        d.polygon([(46, hy), (82, hy), (76, hy + 24), (52, hy + 24)], fill=(225, 170, 135, 255), outline=INK)
        # Buzzcut scalp stipple fade
        d.ellipse([46, hy - 6, 82, hy + 8], fill=(125, 105, 95, 255))
        # Brow scar
        d.line([(52, hy + 3), (56, hy + 9)], fill=(245, 205, 190, 255), width=2)
        
        # Dark Mirrored Sunglasses reflecting Club Neon (Magenta & Cyan)
        d.polygon([(48, hy + 7), (62, hy + 7), (60, hy + 14), (50, hy + 14)], fill=(10, 12, 16, 255), outline=INK)
        d.polygon([(66, hy + 7), (80, hy + 7), (78, hy + 14), (68, hy + 14)], fill=(10, 12, 16, 255), outline=INK)
        d.line([(62, hy + 9), (66, hy + 9)], fill=(60, 65, 75, 255), width=2) # bridge
        
        # Strobe neon reflection glint across aviator lenses
        d.line([(49, hy + 8), (59, hy + 13)], fill=(255, 0, 127, 255)) # neon magenta
        d.line([(67, hy + 8), (77, hy + 13)], fill=(0, 240, 255, 255)) # neon cyan
        if f == 1:
            # Specular lens spark on frame 1
            d.point((58, hy + 8), fill=(255, 255, 255, 255))
            d.point((76, hy + 8), fill=(255, 255, 255, 255))
            
        # Contemptuous scowling mouth
        d.line([(58, hy + 19), (70, hy + 19)], fill=(130, 80, 70, 255), width=2)
        # Spiral acoustic surveillance earpiece cord
        d.arc([78, hy + 10, 86, hy + 24], 90, 270, fill=(225, 235, 245, 200), width=2)
        
        frames.append(im)
        
    save_enemy_sheet("kark", frames[0], frames[1], sz)


# ============================================================================
# 7. PAN JANUSZ KOMENDANT (144x144 x 2 = 288x144) - Final Boss
# Polish State Forest Service ceremonial greatcoat, golden oak leaf epaulets,
# rogatywka cap with silver eagle, vintage industrial megaphone with acoustic rings.
# ============================================================================
def build_pan_janusz():
    sz = 144
    frames = []
    
    for f in range(2):
        im = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        
        # Ground shadow
        d.ellipse([34, 130, 110, 142], fill=SHADOW_TINT)
        
        bob = -2 if f == 1 else 0
        
        # 1. Dark Green Forestry Trousers & Heavy Field Boots
        d.rectangle([50, 108 + bob, 68, 132], fill=(24, 44, 26, 255), outline=INK)
        d.rectangle([78, 108 + bob, 96, 132], fill=(24, 44, 26, 255), outline=INK)
        # Heavy leather field boots
        d.polygon([(46, 130), (70, 130), (68, 140), (44, 140)], fill=(55, 35, 22, 255), outline=INK)
        d.line([(46, 131), (68, 131)], fill=(115, 85, 60, 255))
        d.polygon([(76, 130), (100, 130), (98, 140), (74, 140)], fill=(55, 35, 22, 255), outline=INK)
        d.line([(76, 131), (98, 131)], fill=(115, 85, 60, 255))
        
        # 2. Ceremonial Pine-Green Wool Greatcoat with Golden Buttons & Epaulets
        jy = 54 + bob
        # Coat mantle
        d.polygon([
            (28, jy), (118, jy),
            (110, 110 + bob), (36, 110 + bob)
        ], fill=(28, 56, 32, 255), outline=INK)
        
        # Scarlet collar tabs & lapels
        d.polygon([(56, jy), (64, jy + 18), (72, jy)], fill=(175, 25, 35, 255), outline=INK)
        d.point((64, jy + 8), fill=(255, 215, 60, 255)) # gold insignia pin
        
        # Double-breasted polished brass buttons
        for by in range(jy + 12, 108, 12):
            d.ellipse([60, by + bob, 65, by + 5 + bob], fill=(245, 205, 50, 255), outline=INK)
            d.ellipse([79, by + bob, 84, by + 5 + bob], fill=(245, 205, 50, 255), outline=INK)
            d.point((61, by + 1 + bob), fill=(255, 255, 255, 255))
            d.point((80, by + 1 + bob), fill=(255, 255, 255, 255))
            
        # Heavy ceremonial gold bullion fringed epaulets on shoulders
        # Left epaulet
        d.polygon([(24, jy - 3), (46, jy - 3), (42, jy + 6), (22, jy + 6)], fill=(240, 205, 55, 255), outline=INK)
        for fx in range(24, 44, 3): d.line([(fx, jy + 6), (fx, jy + 11)], fill=(240, 205, 55, 255)) # gold fringe
        # Right epaulet
        d.polygon([(100, jy - 3), (122, jy - 3), (124, jy + 6), (102, jy + 6)], fill=(240, 205, 55, 255), outline=INK)
        for fx in range(102, 122, 3): d.line([(fx, jy + 6), (fx, jy + 11)], fill=(240, 205, 55, 255))
        
        # Leather service belt & golden buckle
        d.rectangle([34, 102 + bob, 112, 110 + bob], fill=(65, 40, 22, 255), outline=INK)
        d.rectangle([66, 100 + bob, 78, 112 + bob], fill=(240, 205, 55, 255), outline=INK)
        d.point((72, 106 + bob), fill=INK)
        
        # 3. Head & Peaked Polish Rogatywka Cap with Silver Eagle
        hy = 36 + bob
        d.rectangle([64, hy + 8, 80, hy + 18], fill=(225, 175, 140, 255), outline=INK)
        d.ellipse([54, hy - 10, 90, hy + 16], fill=(225, 175, 140, 255), outline=INK)
        
        # Rugged weathered face & stern squint
        d.line([(58, hy - 1), (68, hy + 2)], fill=(95, 100, 110, 255), width=3) # thick grey brows
        d.line([(86, hy - 1), (76, hy + 2)], fill=(95, 100, 110, 255), width=3)
        d.point((64, hy + 4), fill=(10, 10, 10, 255))
        d.point((80, hy + 4), fill=(10, 10, 10, 255))
        d.line([(56, hy + 8), (62, hy + 8)], fill=(185, 130, 100, 255)) # eye bags
        d.line([(82, hy + 8), (88, hy + 8)], fill=(185, 130, 100, 255))
        
        # Sweeping silver-grey walrus mustache
        must_pts = [
            (50, hy + 10), (72, hy + 18), (94, hy + 10),
            (88, hy + 8), (72, hy + 10), (56, hy + 8)
        ]
        d.polygon(must_pts, fill=(185, 190, 198, 255), outline=INK)
        d.line([(54, hy + 11), (90, hy + 11)], fill=(240, 245, 250, 255)) # silver highlights
        
        # Traditional Square Rogatywka Cap
        cap_pts = [(48, hy - 10), (96, hy - 10), (92, hy - 24), (52, hy - 24)]
        d.polygon(cap_pts, fill=(24, 48, 28, 255), outline=INK)
        # Cap dark band with silver Polish Eagle badge
        d.rectangle([(49, hy - 13), (95, hy - 9)], fill=(16, 32, 18, 255))
        # Silver Polish Eagle
        d.polygon([(70, hy - 13), (74, hy - 17), (72, hy - 10)], fill=(255, 255, 255, 255))
        d.point((72, hy - 15), fill=(245, 205, 50, 255)) # golden crown on eagle
        # Stiff black visor
        d.polygon([(46, hy - 8), (98, hy - 8), (92, hy - 4), (52, hy - 4)], fill=(12, 14, 18, 255))
        d.line([(50, hy - 7), (94, hy - 7)], fill=(100, 115, 130, 255))
        
        # 4. Left Arm & Giant Industrial Megaphone
        mega_dy = -6 if f == 1 else 0
        d.polygon([(32, 60 + bob), (18, 70 + bob + mega_dy), (22, 78 + bob + mega_dy), (34, 68 + bob)], fill=(28, 56, 32, 255), outline=INK)
        # Vintage metal megaphone horn
        mx0, my0 = 20, 74 + bob + mega_dy
        horn_pts = [
            (mx0, my0 - 2), (0, my0 - 18),
            (0, my0 + 18), (mx0, my0 + 6)
        ]
        d.polygon(horn_pts, fill=(185, 190, 200, 255), outline=INK)
        d.line([(mx0, my0), (0, my0 - 14)], fill=(240, 245, 255, 255), width=2) # metal highlight
        d.ellipse([-2, my0 - 18, 5, my0 + 18], fill=(70, 75, 85, 255), outline=INK)
        
        # Acoustic sonic pressure rings emitting from megaphone if frame 1
        if f == 1:
            d.arc([-12, my0 - 28, 8, my0 + 28], 90, 270, fill=(255, 230, 60, 255), width=2)
            d.arc([-24, my0 - 38, 12, my0 + 38], 90, 270, fill=(255, 60, 60, 255), width=2)
            
        # 5. Right Arm & Citation Fine Dossier ("Bloczek 5000 zł")
        d.polygon([(112, 60 + bob), (126, 70 + bob), (124, 78 + bob), (110, 68 + bob)], fill=(28, 56, 32, 255), outline=INK)
        # Leather folder with white summons sheets
        d.polygon([(118, 64 + bob), (142, 58 + bob), (144, 82 + bob), (120, 88 + bob)], fill=(115, 35, 25, 255), outline=INK)
        d.polygon([(122, 66 + bob), (139, 61 + bob), (141, 80 + bob), (124, 85 + bob)], fill=(255, 250, 240, 255))
        d.text((124, 68 + bob), "5000", fill=(180, 20, 20, 255))
        
        frames.append(im)
        
    save_enemy_sheet("panJanusz", frames[0], frames[1], sz)


# ============================================================================
# 8. KREDYT NA 30 LAT (144x144 x 2 = 288x144) - Boss Construct
# Neoclassical dark basalt bank temple, crumbling fluted pillars, demonic
# interest-rate red eyes in the vault void, tattered foreclosure tape, orbiting WIBOR runes.
# ============================================================================
def build_kredyt():
    sz = 144
    frames = []
    
    for f in range(2):
        im = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        
        # Ground shadow
        d.ellipse([14, 126, 130, 142], fill=SHADOW_TINT)
        
        # 1. Monument Pedestal Steps
        d.rectangle([18, 116, 126, 134], fill=(48, 52, 62, 255), outline=INK)
        d.rectangle([24, 104, 120, 116], fill=(62, 66, 78, 255), outline=INK)
        d.line([(20, 117), (124, 117)], fill=(110, 115, 130, 255)) # step highlight
        d.line([(26, 105), (118, 105)], fill=(110, 115, 130, 255))
        
        # 2. Dark Basalt Neoclassical Columns (4 pillars)
        col_x = [30, 54, 80, 104]
        for cx in col_x:
            # Pillar body
            d.rectangle([cx, 44, cx + 11, 104], fill=(75, 80, 94, 255), outline=INK)
            # Flute shadows and highlights
            d.line([(cx + 2, 45), (cx + 2, 103)], fill=(130, 136, 150, 255))
            d.line([(cx + 8, 45), (cx + 8, 103)], fill=(40, 44, 52, 255))
            # Corinthian carved capital on top
            d.rectangle([cx - 2, 41, cx + 13, 45], fill=(95, 102, 118, 255), outline=INK)
            
        # 3. Pediment & Temple Roof
        roof_pts = [(20, 42), (124, 42), (72, 14)]
        d.polygon(roof_pts, fill=(68, 72, 85, 255), outline=INK)
        # Inner pediment frieze
        d.polygon([(28, 40), (116, 40), (72, 18)], fill=(86, 92, 108, 255))
        # Tectonic fracture crack running through temple
        crack_c = (255, 40, 60, 255) if f == 1 else (255, 90, 90, 255)
        d.line([(72, 18), (68, 30), (74, 41)], fill=crack_c, width=2)
        if f == 1:
            d.line([(68, 30), (60, 36)], fill=(255, 180, 100, 255), width=2)
            
        # 4. Abyssal Vault Void with Demonic Predatory Red Interest Eyes
        d.rectangle([44, 52, 100, 96], fill=(12, 10, 16, 255))
        # Baleful demonic glowing eyes (WIBOR hike!)
        eye_glow = (255, 30, 45, 255) if f == 0 else (255, 90, 110, 255)
        # Left eye
        d.polygon([(52, 68), (64, 72), (56, 78)], fill=eye_glow)
        d.point((58, 73), fill=(255, 255, 255, 255))
        # Right eye
        d.polygon([(92, 68), (80, 72), (88, 78)], fill=eye_glow)
        d.point((86, 73), fill=(255, 255, 255, 255))
        
        # 5. Tattered Foreclosure Caution Tape Wrapping Columns
        tapes = [56, 74, 92]
        for ty in tapes:
            tshift = 2 if f == 1 else 0
            d.polygon([
                (20, ty - 6 + tshift), (124, ty + 4 + tshift),
                (124, ty + 12 + tshift), (20, ty + 2 + tshift)
            ], fill=(225, 30, 40, 255), outline=INK)
            # White diagonal warning marks
            for tx in range(24, 120, 12):
                d.polygon([
                    (tx, ty - 4 + tshift), (tx + 5, ty - 3 + tshift),
                    (tx + 3, ty + 4 + tshift), (tx - 2, ty + 3 + tshift)
                ], fill=(255, 255, 255, 255))
                
        # 6. Orbiting Financial Runes (WIBOR, %, CHF, PLN)
        rune_dy = 4 if f == 1 else -3
        # Left rune: % in glowing circle
        d.ellipse([12, 32 + rune_dy, 32, 52 + rune_dy], fill=(22, 24, 34, 230), outline=(255, 215, 60, 255))
        d.line([(18, 46 + rune_dy), (26, 38 + rune_dy)], fill=(255, 215, 60, 255), width=2)
        d.point((19, 39 + rune_dy), fill=(255, 215, 60, 255))
        d.point((25, 45 + rune_dy), fill=(255, 215, 60, 255))
        
        # Right rune: zł in glowing red circle
        d.ellipse([112, 30 - rune_dy, 134, 52 - rune_dy], fill=(22, 24, 34, 230), outline=(255, 60, 60, 255))
        d.text((116, 34 - rune_dy), "zł", fill=(255, 80, 80, 255))
        
        frames.append(im)
        
    save_enemy_sheet("kredyt", frames[0], frames[1], sz)


# ============================================================================
# 9. AUDYT KORPORACYJNY (144x144 x 2 = 288x144) - Boss Construct
# Industrial mainframe server rack, curved phosphor CRT monitor, terrifying
# cyclopean red pie chart eye with radar crosshairs, razor paperclip pincers,
# spilling continuous dot-matrix green-bar stationery.
# ============================================================================
def build_audyt():
    sz = 144
    frames = []
    
    for f in range(2):
        im = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        
        # Ground shadow
        d.ellipse([30, 126, 114, 142], fill=SHADOW_TINT)
        
        # 1. Industrial Server Rack Base Pedestal
        d.rectangle([38, 96, 106, 134], fill=(28, 32, 42, 255), outline=INK)
        # Array of blinking server LEDs
        for lx in range(44, 100, 8):
            led_c = (255, 35, 45, 255) if (lx + f * 8) % 16 == 0 else (45, 245, 95, 255)
            d.rectangle([lx, 102, lx + 4, 106], fill=led_c)
            d.rectangle([lx, 112, lx + 4, 116], fill=(0, 200, 255, 255))
            d.rectangle([lx, 122, lx + 4, 126], fill=(255, 215, 50, 255))
            
        # 2. Heavy CRT Monitor Chassis
        d.rounded_rectangle([30, 26, 114, 96], radius=10, fill=(48, 54, 68, 255), outline=INK)
        # CRT Bezel
        d.rectangle([36, 32, 108, 90], fill=(14, 26, 20, 255), outline=(22, 26, 36, 255))
        
        # Phosphor Green Spreadsheet Grid on Screen
        for gx in range(42, 106, 14): d.line([(gx, 34), (gx, 88)], fill=(32, 95, 55, 160))
        for gy in range(40, 88, 11): d.line([(38, gy), (106, gy)], fill=(32, 95, 55, 160))
        
        # Cyclopean Red Pie-Chart Eye with Deficit Slice
        eye_x, eye_y = 72, 61
        d.ellipse([eye_x - 17, eye_y - 17, eye_x + 17, eye_y + 17], fill=(16, 20, 26, 255), outline=(225, 35, 45, 255))
        # Deficit pie slice
        slice_ang = 100 + (35 if f == 1 else 0)
        d.pieslice([eye_x - 15, eye_y - 15, eye_x + 15, eye_y + 15], 0, slice_ang, fill=(245, 45, 55, 255))
        d.pieslice([eye_x - 15, eye_y - 15, eye_x + 15, eye_y + 15], slice_ang, 360, fill=(45, 185, 85, 255))
        # Center pupil crosshair
        d.ellipse([eye_x - 5, eye_y - 5, eye_x + 5, eye_y + 5], fill=(255, 255, 255, 255), outline=INK)
        d.line([(eye_x - 20, eye_y), (eye_x + 20, eye_y)], fill=(255, 80, 80, 180))
        d.line([(eye_x, eye_y - 20), (eye_x, eye_y + 20)], fill=(255, 80, 80, 180))
        
        # Spreadsheet Terror Notices (#REF! and -99%)
        d.text((40, 36), "#REF!", fill=(255, 50, 50, 255))
        d.text((80, 74), "-99%", fill=(255, 50, 50, 255))
        
        # 3. Mechanical Paperclip Pincers Robotic Arms
        pinc_ang = 12 if f == 1 else 0
        # Left steel pincer arm
        d.line([(30, 48), (16, 42), (10, 58)], fill=(130, 140, 155, 255), width=4)
        d.arc([2, 50 + pinc_ang, 20, 72 + pinc_ang], 0, 360, fill=(225, 230, 245, 255), width=3)
        d.line([(10, 68 + pinc_ang), (24, 76 + pinc_ang)], fill=(225, 230, 245, 255), width=3)
        # Right steel pincer arm
        d.line([(114, 48), (128, 42), (134, 58)], fill=(130, 140, 155, 255), width=4)
        d.arc([124, 50 - pinc_ang, 142, 72 - pinc_ang], 0, 360, fill=(225, 230, 245, 255), width=3)
        d.line([(134, 68 - pinc_ang), (120, 76 - pinc_ang)], fill=(225, 230, 245, 255), width=3)
        
        # 4. Spilling Continuous Green-Bar Dot-Matrix Paper Ribbons
        paper_x = 72
        d.polygon([
            (paper_x - 16, 94), (paper_x + 16, 94),
            (paper_x + 20, 128), (paper_x - 12, 128)
        ], fill=(245, 250, 245, 255), outline=INK)
        # Green-bar ledger lines and tractor pinholes
        for py in range(98, 126, 6):
            d.line([(paper_x - 14, py), (paper_x + 16, py)], fill=(175, 225, 185, 255), width=2)
            d.point((paper_x - 14, py), fill=(80, 90, 100, 255))
            d.point((paper_x + 16, py), fill=(80, 90, 100, 255))
            
        frames.append(im)
        
    save_enemy_sheet("audyt", frames[0], frames[1], sz)


# ============================================================================
# 10. RWA KULSZOWA (128x128 x 2 = 256x128)
# Sinuous neural ganglion core, branching violet/magenta dendrites & axons,
# high-voltage synaptic yellow/cyan pain discharges.
# ============================================================================
def build_rwa_kulszowa():
    sz = 128
    frames = []
    
    for f in range(2):
        im = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        cx, cy = 64, 64
        
        # Ground shadow
        d.ellipse([34, 114, 94, 126], fill=SHADOW_TINT)
        
        # 1. Sciatic Nerve Branches / Dendrites Radiating Outward
        branches = [
            (cx, cy, 22, 18, 5),
            (cx, cy, 106, 20, 5),
            (cx, cy, 14, 92, 5),
            (cx, cy, 114, 102, 6),
            (cx, cy, 64, 120, 6),
            (cx, cy, 64, 8, 4),
            (cx, cy, 16, 54, 4),
            (cx, cy, 112, 58, 5),
        ]
        
        for x0, y0, x1, y1, width in branches:
            mx = (x0 + x1) // 2 + (math.sin(x1) * 9)
            my = (y0 + y1) // 2 + (math.cos(y1) * 9)
            # Deep violet outer contour
            d.line([(x0, y0), (mx, my), (x1, y1)], fill=(95, 25, 130, 255), width=width + 2)
            # Radiant fuchsia axon fiber
            d.line([(x0, y0), (mx, my), (x1, y1)], fill=(215, 55, 225, 255), width=max(1, width - 1))
            # Inner white-hot neural core
            d.line([(x0, y0), (mx, my), (x1, y1)], fill=(255, 210, 255, 255), width=1)
            
            # Synaptic terminal clefts
            d.line([(x1, y1), (x1 + 8, y1 - 6)], fill=(245, 75, 195, 255), width=2)
            d.line([(x1, y1), (x1 - 6, y1 + 8)], fill=(245, 75, 195, 255), width=2)
            
            # High-voltage pain sparks at terminal clefts
            spark_col = (255, 235, 70, 255) if f == 1 else (0, 245, 212, 255)
            d.point((int(x1 + 8), int(y1 - 6)), fill=spark_col)
            d.point((int(x1 - 6), int(y1 + 8)), fill=spark_col)
            d.line([(int(x1), int(y1)), (int(x1 + (5 if f==0 else -5)), int(y1 + (5 if f==1 else -5)))], fill=spark_col, width=2)
            
        # 2. Central Neural Ganglion Core Sphere
        pulse_r = -3 if f == 1 else 0
        core_r = 28 + pulse_r
        for r in range(core_r, 0, -1):
            t = r / float(core_r)
            cr = int(50 * t + 245 * (1 - t))
            cg = int(10 * t + 60 * (1 - t))
            cb = int(85 * t + 225 * (1 - t))
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(cr, cg, cb, 255))
            
        # 3. Throbbing Synaptic Veins & Electric Discharge Arcs Across Core
        vein_pts = [(cx - 18, cy - 8), (cx - 4, cy + 5), (cx + 12, cy - 3), (cx + 20, cy + 12)]
        d.line(vein_pts, fill=(255, 120, 210, 255), width=3)
        d.line(vein_pts, fill=(255, 255, 255, 255), width=1)
        
        # Spasm discharge arc
        arc_pts = [
            (cx - 22, cy + 8),
            (cx - 8, cy + 18 if f == 0 else cy + 2),
            (cx + 8, cy + 4 if f == 0 else cy + 16),
            (cx + 24, cy + 6)
        ]
        arc_col = (255, 255, 130, 255) if f == 1 else (0, 245, 212, 255)
        d.line(arc_pts, fill=arc_col, width=2)
        d.point((cx, cy + 10), fill=(255, 255, 255, 255))
        
        frames.append(im)
        
    save_enemy_sheet("rwaKulszowa", frames[0], frames[1], sz)


# ============================================================================
# MASTER GENERATOR
# Generates all 10 enemies/bosses while strictly preserving 'slacki.png'.
# ============================================================================
def build_all_hd_enemies():
    print("==================================================================")
    print("Generating High-Definition Pixel Art for OsakaRPG Enemies/Bosses...")
    print("==================================================================")
    build_bol_kregoslupa()
    build_sasiad_szkodnik()
    build_autotune_hipster()
    build_drogie_piwo()
    build_straznik()
    build_kark()
    build_pan_janusz()
    build_kredyt()
    build_audyt()
    build_rwa_kulszowa()
    print("------------------------------------------------------------------")
    print("Note: 'slacki.png' intentionally left unchanged per user instruction.")
    print("All 10 enemy/boss pixel art sheets successfully rebuilt!")
    print("==================================================================")

if __name__ == "__main__":
    build_all_hd_enemies()
