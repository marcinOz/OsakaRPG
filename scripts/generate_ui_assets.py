import os
import math
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

UI_DIR = 'public/assets/ui'
FX_DIR = 'public/assets/fx'
PORTRAITS_DIR = 'public/assets/portraits'

os.makedirs(UI_DIR, exist_ok=True)
os.makedirs(FX_DIR, exist_ok=True)

# Select best system font for crisp pixel / UI rendering
FONT_PATHS = [
    '/System/Library/Fonts/Menlo.ttc',
    '/System/Library/Fonts/SFNSMono.ttf',
    '/System/Library/Fonts/Monaco.ttf',
    '/System/Library/Fonts/Geneva.ttf'
]
FONT_MAIN = None
for p in FONT_PATHS:
    if os.path.exists(p):
        FONT_MAIN = p
        break

def get_font(size, bold=False):
    if FONT_MAIN:
        try:
            return ImageFont.truetype(FONT_MAIN, size)
        except Exception:
            pass
    return ImageFont.load_default()

# -------------------------------------------------------------
# 1. HERO AVATAR CHIPS & GROUP CHAT ICON
# -------------------------------------------------------------
def generate_avatars():
    names = ['danny', 'alior', 'lisu', 'barti', 'oziem', 'luki']
    for name in names:
        src = f'{PORTRAITS_DIR}/{name}_64.png'
        if not os.path.exists(src):
            continue
        im = Image.open(src).convert('RGBA')
        # Center-head crop
        head = im.crop((4, 2, 60, 58)).resize((32, 32), Image.Resampling.LANCZOS)
        
        mask = Image.new('L', (32, 32), 0)
        d = ImageDraw.Draw(mask)
        d.ellipse((1, 1, 30, 30), fill=255)
        
        out = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
        out.paste(head, (0, 0), mask)
        
        d_out = ImageDraw.Draw(out)
        d_out.ellipse((0, 0, 31, 31), outline=(18, 140, 126, 255), width=1) # WhatsApp teal outline
        out.save(f'{UI_DIR}/avatar_{name}.png')
        print(f'Generated: {UI_DIR}/avatar_{name}.png')
    
    # Generate group avatar chip (32x32)
    grp = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    d_grp = ImageDraw.Draw(grp)
    # Circle background in deep teal
    d_grp.ellipse((0, 0, 31, 31), fill=(0, 92, 75, 255), outline=(0, 168, 132, 255), width=1)
    
    # Campfire / Pack flame icon in the center
    flame_coords = [
        (16, 6), (18, 9), (21, 13), (22, 18), (20, 22), (18, 24),
        (14, 24), (12, 22), (10, 18), (11, 13), (14, 9)
    ]
    d_grp.polygon(flame_coords, fill=(224, 116, 44, 255))
    inner_flame = [
        (16, 11), (18, 14), (19, 18), (17, 22), (15, 22), (13, 18), (14, 14)
    ]
    d_grp.polygon(inner_flame, fill=(246, 192, 74, 255))
    core_flame = [(16, 15), (17, 18), (16, 21), (15, 18)]
    d_grp.polygon(core_flame, fill=(255, 255, 220, 255))
    # Two crossed logs at the base
    d_grp.line([(10, 23), (22, 27)], fill=(90, 50, 30, 255), width=2)
    d_grp.line([(22, 23), (10, 27)], fill=(110, 65, 40, 255), width=2)
    
    grp.save(f'{UI_DIR}/avatar_group.png')
    print(f'Generated: {UI_DIR}/avatar_group.png')

# -------------------------------------------------------------
# 2. AUTHENTIC WHATSAPP SMARTPHONE MODAL (400x540 RGBA)
# -------------------------------------------------------------
def draw_whatsapp_doodles(draw, area):
    """Draw subtle authentic WhatsApp dark-mode doodle icons."""
    x0, y0, x1, y1 = area
    color = (19, 32, 40, 255) # Subtle low contrast doodle on (11, 20, 26)
    
    # Pre-defined mini doodle functions
    def doodle_bubble(x, y):
        draw.rounded_rectangle((x, y, x + 14, y + 10), radius=3, outline=color, width=1)
        draw.polygon([(x + 2, y + 10), (x + 5, y + 10), (x + 1, y + 13)], fill=color)

    def doodle_coffee(x, y):
        draw.rectangle((x, y + 3, x + 10, y + 11), outline=color, width=1)
        draw.arc((x + 8, y + 4, x + 13, y + 9), start=270, end=90, fill=color, width=1)
        draw.line([(x + 3, y), (x + 3, y + 2)], fill=color, width=1)
        draw.line([(x + 7, y), (x + 7, y + 2)], fill=color, width=1)

    def doodle_music(x, y):
        draw.ellipse((x, y + 8, x + 5, y + 12), fill=color)
        draw.line([(x + 4, y + 1), (x + 4, y + 10)], fill=color, width=1)
        draw.line([(x + 4, y + 1), (x + 10, y + 3)], fill=color, width=2)
        draw.ellipse((x + 8, y + 9, x + 13, y + 13), fill=color)
        draw.line([(x + 12, y + 3), (x + 12, y + 11)], fill=color, width=1)

    def doodle_heart(x, y):
        draw.polygon([(x+5, y+2), (x+8, y), (x+11, y+2), (x+11, y+5), (x+5, y+11), (x, y+5), (x, y+2), (x+3, y)], outline=color)

    def doodle_star(x, y):
        draw.line([(x+5, y), (x+5, y+10)], fill=color, width=1)
        draw.line([(x, y+5), (x+10, y+5)], fill=color, width=1)
        draw.line([(x+2, y+2), (x+8, y+8)], fill=color, width=1)
        draw.line([(x+8, y+2), (x+2, y+8)], fill=color, width=1)

    def doodle_gamepad(x, y):
        draw.rounded_rectangle((x, y, x + 14, y + 8), radius=2, outline=color, width=1)
        draw.line([(x + 3, y + 2), (x + 3, y + 6)], fill=color, width=1)
        draw.line([(x + 1, y + 4), (x + 5, y + 4)], fill=color, width=1)
        draw.point((x + 10, y + 3), fill=color)
        draw.point((x + 12, y + 5), fill=color)

    def doodle_flame(x, y):
        draw.polygon([(x+5, y), (x+8, y+4), (x+9, y+8), (x+6, y+11), (x+3, y+11), (x+1, y+8), (x+2, y+4)], outline=color)

    def doodle_car(x, y):
        draw.polygon([(x+2, y+4), (x+5, y), (x+11, y), (x+14, y+4), (x+15, y+7), (x, y+7)], outline=color)
        draw.ellipse((x+3, y+6, x+6, y+9), fill=color)
        draw.ellipse((x+10, y+6, x+13, y+9), fill=color)

    def doodle_clock(x, y):
        draw.ellipse((x, y, x + 10, y + 10), outline=color, width=1)
        draw.line([(x+5, y+5), (x+5, y+2)], fill=color, width=1)
        draw.line([(x+5, y+5), (x+8, y+5)], fill=color, width=1)

    def doodle_tree(x, y):
        draw.polygon([(x+5, y), (x+9, y+6), (x+7, y+6), (x+10, y+10), (x+1, y+10), (x+4, y+6), (x+2, y+6)], outline=color)
        draw.line([(x+5, y+10), (x+5, y+12)], fill=color, width=1)

    doodles = [
        doodle_bubble, doodle_coffee, doodle_music, doodle_heart,
        doodle_star, doodle_gamepad, doodle_flame, doodle_car,
        doodle_clock, doodle_tree
    ]
    
    # Use deterministic seed for neat consistent wallpaper pattern
    rng = random.Random(42)
    step_x = 36
    step_y = 34
    
    cols = (x1 - x0) // step_x
    rows = (y1 - y0) // step_y
    
    for r in range(rows):
        for c in range(cols):
            dx = x0 + 10 + c * step_x + ((r % 2) * 16) + rng.randint(-3, 3)
            dy = y0 + 10 + r * step_y + rng.randint(-3, 3)
            if dx + 16 < x1 and dy + 16 < y1:
                fn = doodles[(r * cols + c) % len(doodles)]
                fn(dx, dy)

def generate_phone_frame():
    w, h = 400, 540
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 1. Phone Outer Body / Chassis
    # Matte titanium/slate chassis with bevel
    draw.rounded_rectangle((2, 2, 397, 537), radius=30, fill=(20, 23, 27, 255), outline=(48, 54, 62, 255), width=2)
    draw.rounded_rectangle((4, 4, 395, 535), radius=28, fill=(16, 18, 22, 255))
    
    # Outer highlights & shadows
    # Top speaker slit
    draw.rounded_rectangle((175, 7, 225, 11), radius=2, fill=(35, 39, 46, 255), outline=(22, 25, 30, 255), width=1)
    
    # 2. Inner Screen (372 x 506)
    scr_x0, scr_y0, scr_x1, scr_y1 = 14, 16, 386, 524
    screen_rect = (scr_x0, scr_y0, scr_x1, scr_y1)
    draw.rounded_rectangle(screen_rect, radius=18, fill=(11, 20, 26, 255))
    
    # 3. Status Bar (y: 16 .. 38)
    draw.rectangle((scr_x0, scr_y0, scr_x1, 38), fill=(31, 44, 52, 255))
    # Punch-hole camera (centered at x=200, y=27)
    draw.ellipse((196, 23, 204, 31), fill=(9, 10, 13, 255), outline=(28, 34, 42, 255), width=1)
    draw.point((198, 25), fill=(40, 80, 140, 255)) # Camera lens reflection
    
    font_status = get_font(10)
    # Time
    draw.text((28, 22), "08:14", fill=(233, 237, 239, 255), font=font_status)
    
    # Cellular Signal (4 bars)
    sig_x = 312
    for i in range(4):
        h_bar = 3 + i * 2
        draw.line([(sig_x + i * 4, 31), (sig_x + i * 4, 31 - h_bar)], fill=(233, 237, 239, 255), width=2)
        
    # Wi-Fi icon
    wifi_x = 338
    draw.arc((wifi_x, 21, wifi_x + 10, 31), start=210, end=330, fill=(233, 237, 239, 255), width=1)
    draw.arc((wifi_x + 2, 24, wifi_x + 8, 30), start=210, end=330, fill=(233, 237, 239, 255), width=1)
    draw.point((wifi_x + 5, 29), fill=(233, 237, 239, 255))
    
    # Battery icon (358..376)
    draw.rounded_rectangle((356, 22, 374, 31), radius=2, outline=(233, 237, 239, 255), width=1)
    draw.line([(375, 24), (375, 29)], fill=(233, 237, 239, 255), width=1)
    # 90% Battery fill
    draw.rectangle((358, 24, 371, 29), fill=(37, 211, 102, 255))
    
    # 4. WhatsApp Header (y: 38 .. 94)
    draw.rectangle((scr_x0, 38, scr_x1, 94), fill=(31, 44, 52, 255))
    # Bottom divider line
    draw.line([(scr_x0, 94), (scr_x1, 94)], fill=(24, 34, 41, 255), width=1)
    
    # Back chevron <
    draw.line([(24, 65), (28, 60)], fill=(174, 196, 181, 255), width=2)
    draw.line([(24, 65), (28, 70)], fill=(174, 196, 181, 255), width=2)
    
    # Circular Group Avatar (34x34) at (36, 48)
    grp_avatar = Image.open(f'{UI_DIR}/avatar_group.png').resize((34, 34), Image.Resampling.LANCZOS)
    img.paste(grp_avatar, (36, 48), grp_avatar)
    
    # Header Titles
    font_title = get_font(12, bold=True)
    font_sub = get_font(9)
    draw.text((78, 51), "EKIPA 36+ [REUNION NIGHT]", fill=(233, 237, 239, 255), font=font_title)
    draw.text((78, 69), "Danny, Alior, Lisu, Barti, Oziem, Łuki", fill=(134, 150, 160, 255), font=font_sub)
    
    # Header icons: Video, Phone, Menu
    # Video icon
    draw.rounded_rectangle((318, 59, 331, 71), radius=2, outline=(174, 196, 181, 255), width=1)
    draw.polygon([(331, 62), (336, 59), (336, 71), (331, 68)], fill=(174, 196, 181, 255))
    # Phone icon
    draw.arc((346, 59, 356, 71), start=120, end=300, fill=(174, 196, 181, 255), width=2)
    # 3-dots Menu ⋮
    draw.ellipse((370, 58, 372, 60), fill=(174, 196, 181, 255))
    draw.ellipse((370, 64, 372, 66), fill=(174, 196, 181, 255))
    draw.ellipse((370, 70, 372, 72), fill=(174, 196, 181, 255))
    
    # 5. WhatsApp Doodle Wallpaper Background (y: 95 .. 472)
    draw_whatsapp_doodles(draw, (scr_x0, 95, scr_x1, 472))
    
    # 6. Bottom Input & Action Bar (y: 472 .. 524)
    draw.rectangle((scr_x0, 472, scr_x1, scr_y1 - 10), fill=(31, 44, 52, 255))
    # Bottom curved screen boundary
    draw.rounded_rectangle((scr_x0, 472, scr_x1, scr_y1), radius=16, fill=(31, 44, 52, 255))
    draw.line([(scr_x0, 472), (scr_x1, 472)], fill=(24, 34, 41, 255), width=1)
    
    # Input Pill Box
    input_box = (22, 482, 268, 514)
    draw.rounded_rectangle(input_box, radius=16, fill=(42, 57, 66, 255), outline=(55, 66, 72, 255), width=1)
    
    # Smiley icon inside pill
    draw.ellipse((32, 491, 44, 503), outline=(134, 150, 160, 255), width=1)
    draw.point((35, 495), fill=(134, 150, 160, 255))
    draw.point((41, 495), fill=(134, 150, 160, 255))
    draw.arc((35, 496, 41, 501), start=0, end=180, fill=(134, 150, 160, 255), width=1)
    
    # Placeholder text
    draw.text((50, 493), "Wiadomość...", fill=(134, 150, 160, 255), font=get_font(10))
    
    # Paperclip icon inside pill
    draw.line([(230, 494), (236, 500)], fill=(134, 150, 160, 255), width=1)
    draw.arc((234, 498, 238, 504), start=0, end=180, fill=(134, 150, 160, 255), width=1)
    # Camera icon inside pill
    draw.rounded_rectangle((246, 492, 258, 502), radius=1, outline=(134, 150, 160, 255), width=1)
    draw.ellipse((249, 494, 255, 500), outline=(134, 150, 160, 255), width=1)
    
    # Action Button "[Z] DALEJ ▶" (WhatsApp Emerald Green)
    act_box = (276, 482, 378, 514)
    draw.rounded_rectangle(act_box, radius=16, fill=(0, 168, 132, 255), outline=(0, 196, 154, 255), width=1)
    # Subtle button highlight on upper half
    draw.rounded_rectangle((278, 483, 376, 497), radius=14, fill=(0, 185, 145, 255))
    
    font_btn = get_font(10, bold=True)
    draw.text((292, 493), "[Z] DALEJ ▶", fill=(255, 255, 255, 255), font=font_btn)
    
    # Save phone frame
    img.save(f'{UI_DIR}/phone_frame.png')
    print(f'Generated: {UI_DIR}/phone_frame.png (400x540 RGBA)')

# -------------------------------------------------------------
# 3. SPEECH BUBBLES (INCOMING & OUTGOING)
# -------------------------------------------------------------
def generate_speech_bubbles():
    # Incoming message bubble (Dark Slate #202C33)
    w_b, h_b = 280, 56
    b_in = Image.new('RGBA', (w_b, h_b), (0, 0, 0, 0))
    d_in = ImageDraw.Draw(b_in)
    
    # Main bubble
    d_in.rounded_rectangle((8, 0, w_b - 1, h_b - 1), radius=8, fill=(32, 44, 51, 255), outline=(42, 57, 66, 255), width=1)
    # Left tail
    d_in.polygon([(0, 6), (8, 0), (8, 14)], fill=(32, 44, 51, 255))
    d_in.line([(0, 6), (8, 0)], fill=(42, 57, 66, 255), width=1)
    d_in.line([(0, 6), (8, 14)], fill=(42, 57, 66, 255), width=1)
    b_in.save(f'{UI_DIR}/chat_bubble_in.png')
    print(f'Generated: {UI_DIR}/chat_bubble_in.png')
    
    # Outgoing message bubble (Dark Emerald #005C4B)
    b_out = Image.new('RGBA', (w_b, h_b), (0, 0, 0, 0))
    d_out = ImageDraw.Draw(b_out)
    
    # Main bubble
    d_out.rounded_rectangle((0, 0, w_b - 9, h_b - 1), radius=8, fill=(0, 92, 75, 255), outline=(0, 122, 101, 255), width=1)
    # Right tail
    d_out.polygon([(w_b - 1, 6), (w_b - 9, 0), (w_b - 9, 14)], fill=(0, 92, 75, 255))
    d_out.line([(w_b - 1, 6), (w_b - 9, 0)], fill=(0, 122, 101, 255), width=1)
    d_out.line([(w_b - 1, 6), (w_b - 9, 14)], fill=(0, 122, 101, 255), width=1)
    
    # Double checkmarks (Blue ticks #53BDEB) in bottom right
    tick_x, tick_y = w_b - 28, h_b - 12
    # First tick
    d_out.line([(tick_x, tick_y + 3), (tick_x + 3, tick_y + 6)], fill=(83, 189, 235, 255), width=1)
    d_out.line([(tick_x + 3, tick_y + 6), (tick_x + 8, tick_y)], fill=(83, 189, 235, 255), width=1)
    # Second tick
    d_out.line([(tick_x + 4, tick_y + 3), (tick_x + 7, tick_y + 6)], fill=(83, 189, 235, 255), width=1)
    d_out.line([(tick_x + 7, tick_y + 6), (tick_x + 12, tick_y)], fill=(83, 189, 235, 255), width=1)
    
    b_out.save(f'{UI_DIR}/chat_bubble_out.png')
    print(f'Generated: {UI_DIR}/chat_bubble_out.png')

def draw_pixel_badge_text(draw, x, y, text, color):
    GLYPHS = {
        'W': ['101', '101', '111', '111', '101'],
        'Y': ['101', '101', '010', '010', '010'],
        'J': ['001', '001', '001', '101', '010'],
        'Ś': ['111', '100', '111', '001', '111'],
        'C': ['111', '100', '100', '100', '111'],
        'I': ['111', '010', '010', '010', '111'],
        'E': ['111', '100', '110', '100', '111'],
        'B': ['110', '101', '110', '101', '110'],
        'L': ['100', '100', '100', '100', '111'],
        'O': ['010', '101', '101', '101', '010'],
        'K': ['101', '110', '100', '110', '101'],
        'A': ['010', '101', '111', '101', '101'],
        'D': ['110', '101', '101', '101', '110'],
    }
    cx = x
    for ch in text:
        if ch in GLYPHS:
            if ch == 'Ś':
                draw.point((cx + 1, y - 1), fill=color)
            for row_idx, row in enumerate(GLYPHS[ch]):
                for col_idx, bit in enumerate(row):
                    if bit == '1':
                        draw.point((cx + col_idx, y + row_idx), fill=color)
            cx += 4

# -------------------------------------------------------------
# 4. ANIMATED GLOWING EXIT BEACON (exit_beacon.png & exit_locked.png)
# -------------------------------------------------------------
def generate_exit_beacons():
    # 4 frames side-by-side: 128x48 RGBA (each frame 32x48)
    w_sheet, h_sheet = 128, 48
    beacon_img = Image.new('RGBA', (w_sheet, h_sheet), (0, 0, 0, 0))
    d_b = ImageDraw.Draw(beacon_img)
    
    locked_img = Image.new('RGBA', (w_sheet, h_sheet), (0, 0, 0, 0))
    d_l = ImageDraw.Draw(locked_img)
    
    # Offsets for bobbing arrow: [0, -2, 0, 2]
    bob_offsets = [0, -2, 0, 2]
    
    for f in range(4):
        x_base = f * 32
        bob = bob_offsets[f]
        
        # -----------------------------
        # A. UNLOCKED BEACON (exit_beacon.png)
        # -----------------------------
        # 1. Badge "WYJŚCIE" (y: 2..10)
        badge_rect = (x_base + 1, 2, x_base + 30, 10)
        d_b.rounded_rectangle(badge_rect, radius=2, fill=(6, 18, 32, 240), outline=(0, 240, 255, 255), width=1)
        draw_pixel_badge_text(d_b, x_base + 3, 4, "WYJŚCIE", (200, 238, 244, 255))
        
        # 2. Glowing Vertical Beacon Light Pillar (translucent cyan)
        light_overlay = Image.new('RGBA', (32, 48), (0, 0, 0, 0))
        d_lo = ImageDraw.Draw(light_overlay)
        # Vertical gradient cone
        cone_pts = [(16, 14 + bob), (28, 42), (4, 42)]
        alpha_cone = 25 + (f % 2) * 15
        d_lo.polygon(cone_pts, fill=(0, 240, 255, alpha_cone))
        beacon_img.paste(light_overlay, (x_base, 0), light_overlay)
        
        # 3. Ground Beacon Ring (ellipse at center x=16, y=41)
        rx = 11 + (f % 2)
        ry = 4.5 + (f % 2) * 0.5
        d_b.ellipse((x_base + 16 - rx, 41 - ry, x_base + 16 + rx, 41 + ry), outline=(0, 168, 255, 180), width=1)
        d_b.ellipse((x_base + 16 - 7, 41 - 2.5, x_base + 16 + 7, 41 + 2.5), outline=(0, 240, 255, 255), width=1)
        d_b.point((x_base + 16, 41), fill=(255, 255, 255, 255))
        d_b.point((x_base + 15, 41), fill=(200, 238, 244, 255))
        d_b.point((x_base + 17, 41), fill=(200, 238, 244, 255))
        
        # 4. Floating Neon Chevron / Arrow
        arr_y = 16 + bob
        arrow_poly = [
            (x_base + 16, arr_y + 11), # bottom tip
            (x_base + 9, arr_y + 4),   # left wing
            (x_base + 13, arr_y + 4),  # left notch
            (x_base + 13, arr_y),      # top-left shaft
            (x_base + 19, arr_y),      # top-right shaft
            (x_base + 19, arr_y + 4),  # right notch
            (x_base + 23, arr_y + 4)   # right wing
        ]
        # Gold/cyan glowing neon
        d_b.polygon(arrow_poly, fill=(255, 230, 0, 255), outline=(0, 240, 255, 255))
        inner_shaft = [(x_base + 15, arr_y + 2), (x_base + 17, arr_y + 2), (x_base + 17, arr_y + 7), (x_base + 16, arr_y + 9), (x_base + 15, arr_y + 7)]
        d_b.polygon(inner_shaft, fill=(255, 255, 255, 255))
        
        # Floating sparkles
        if f in [1, 2]:
            d_b.point((x_base + 7, arr_y + 2), fill=(0, 240, 255, 255))
            d_b.point((x_base + 25, arr_y + 6), fill=(255, 230, 0, 255))
            d_b.point((x_base + 16, arr_y - 2), fill=(255, 255, 255, 255))
            
        # -----------------------------
        # B. LOCKED BEACON (exit_locked.png)
        # -----------------------------
        # 1. Badge "BLOKADA" (y: 2..10)
        badge_l_rect = (x_base + 1, 2, x_base + 30, 10)
        d_l.rounded_rectangle(badge_l_rect, radius=2, fill=(32, 6, 12, 240), outline=(255, 42, 85, 255), width=1)
        draw_pixel_badge_text(d_l, x_base + 3, 4, "BLOKADA", (255, 208, 216, 255))
        
        # 2. Glowing Red Cone Overlay
        red_overlay = Image.new('RGBA', (32, 48), (0, 0, 0, 0))
        d_ro = ImageDraw.Draw(red_overlay)
        d_ro.polygon(cone_pts, fill=(255, 42, 85, alpha_cone))
        locked_img.paste(red_overlay, (x_base, 0), red_overlay)
        
        # 3. Ground Red Warning Ring
        d_l.ellipse((x_base + 16 - rx, 41 - ry, x_base + 16 + rx, 41 + ry), outline=(192, 57, 43, 180), width=1)
        d_l.ellipse((x_base + 16 - 7, 41 - 2.5, x_base + 16 + 7, 41 + 2.5), outline=(255, 42, 85, 255), width=1)
        # Hazard X on ground
        d_l.line([(x_base + 12, 40), (x_base + 20, 42)], fill=(255, 42, 85, 220), width=1)
        d_l.line([(x_base + 20, 40), (x_base + 12, 42)], fill=(255, 42, 85, 220), width=1)
        
        # 4. Floating Padlock Icon at y: 16..29 + bob
        lock_y = 16 + bob
        # Shackle (silver metallic)
        d_l.arc((x_base + 12, lock_y - 2, x_base + 20, lock_y + 8), start=180, end=0, fill=(220, 225, 230, 255), width=2)
        # Lock Body (crimson with gold highlight)
        d_l.rounded_rectangle((x_base + 10, lock_y + 3, x_base + 22, lock_y + 13), radius=2, fill=(192, 57, 43, 255), outline=(255, 42, 85, 255), width=1)
        # Keyhole
        d_l.ellipse((x_base + 15, lock_y + 5, x_base + 17, lock_y + 7), fill=(20, 5, 8, 255))
        d_l.line([(x_base + 16, lock_y + 7), (x_base + 16, lock_y + 10)], fill=(20, 5, 8, 255), width=1)
        
        # Red warning pulse aura
        if f in [1, 2]:
            d_l.ellipse((x_base + 8, lock_y - 4, x_base + 24, lock_y + 15), outline=(255, 42, 85, 120), width=1)
            
    beacon_img.save(f'{FX_DIR}/exit_beacon.png')
    print(f'Generated: {FX_DIR}/exit_beacon.png (128x48 RGBA, 4 frames)')
    
    locked_img.save(f'{FX_DIR}/exit_locked.png')
    print(f'Generated: {FX_DIR}/exit_locked.png (128x48 RGBA, 4 frames)')

# -------------------------------------------------------------
# 5. ACTION KEYS LEGEND BADGES (keycaps.png & keys_legend.png)
# -------------------------------------------------------------
def draw_keycap(draw, x, y, w, h, label, font, gold=False):
    """Draw a 3D retro beveled mechanical arcade keycap."""
    # Colors
    bg = (46, 59, 77, 255) if not gold else (90, 70, 20, 255)
    hi = (94, 111, 122, 255) if not gold else (180, 145, 40, 255)
    shadow = (10, 24, 43, 255) if not gold else (40, 30, 10, 255)
    text_color = (200, 238, 244, 255) if not gold else (255, 230, 74, 255)
    
    # Outer base shadow
    draw.rounded_rectangle((x, y, x + w - 1, y + h - 1), radius=3, fill=shadow)
    # Beveled top face
    draw.rounded_rectangle((x, y, x + w - 1, y + h - 3), radius=3, fill=bg, outline=hi, width=1)
    # Bottom lip shadow
    draw.line([(x + 2, y + h - 2), (x + w - 3, y + h - 2)], fill=shadow, width=1)
    
    # Label
    bbox = font.getbbox(label)
    lw = bbox[2] - bbox[0]
    lh = bbox[3] - bbox[1]
    tx = x + (w - lw) // 2
    ty = y + (h - 3 - lh) // 2
    draw.text((tx, ty - 1), label, fill=text_color, font=font)

def generate_keycaps():
    # Sheet containing individual keycaps: 256x96 RGBA
    w_sheet, h_sheet = 256, 96
    sheet = Image.new('RGBA', (w_sheet, h_sheet), (0, 0, 0, 0))
    d = ImageDraw.Draw(sheet)
    
    font_key = get_font(9, bold=True)
    font_lg = get_font(8, bold=True)
    
    # Row 1 (y: 4): [WASD], [W], [A], [S], [D], [Z], [X], [M]
    draw_keycap(d, 4, 4, 44, 20, "WASD", font_key, gold=True)
    draw_keycap(d, 52, 4, 20, 20, "W", font_key)
    draw_keycap(d, 76, 4, 20, 20, "A", font_key)
    draw_keycap(d, 100, 4, 20, 20, "S", font_key)
    draw_keycap(d, 124, 4, 20, 20, "D", font_key)
    draw_keycap(d, 148, 4, 20, 20, "Z", font_key, gold=True)
    draw_keycap(d, 172, 4, 20, 20, "X", font_key)
    draw_keycap(d, 196, 4, 20, 20, "M", font_key)
    draw_keycap(d, 220, 4, 28, 20, "TAB", font_lg)
    
    # Row 2 (y: 28): [ENTER], [SPACJA], [ESC], [1], [2], [3]
    draw_keycap(d, 4, 28, 44, 20, "ENTER", font_lg, gold=True)
    draw_keycap(d, 52, 28, 54, 20, "SPACJA", font_lg, gold=True)
    draw_keycap(d, 110, 28, 28, 20, "ESC", font_lg)
    draw_keycap(d, 142, 28, 20, 20, "1", font_key, gold=True)
    draw_keycap(d, 166, 28, 20, 20, "2", font_key, gold=True)
    draw_keycap(d, 190, 28, 20, 20, "3", font_key, gold=True)
    
    # Row 3 (y: 52): Arrows [▲], [▼], [◄], [►], [E]
    draw_keycap(d, 4, 52, 20, 20, "▲", font_key)
    draw_keycap(d, 28, 52, 20, 20, "▼", font_key)
    draw_keycap(d, 52, 52, 20, 20, "◄", font_key)
    draw_keycap(d, 76, 52, 20, 20, "►", font_key)
    draw_keycap(d, 100, 52, 20, 20, "E", font_key)
    
    sheet.save(f'{UI_DIR}/keycaps.png')
    print(f'Generated: {UI_DIR}/keycaps.png (256x96 RGBA)')

def generate_keys_legend_panels():
    # Pre-composed ready-to-use HUD bars for scenes
    # Width: 560, Height: 84 (3 strips of 28px height: Overworld, Battle, Campfire)
    w, h = 560, 84
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    
    font_key = get_font(9, bold=True)
    font_lbl = get_font(9)
    
    bars = [
        ("overworld", 0),
        ("battle", 28),
        ("campfire", 56)
    ]
    
    for bar_type, y_start in bars:
        # Semi-transparent dark slate HUD backdrop with cyan border
        d.rounded_rectangle((0, y_start + 2, w - 1, y_start + 25), radius=4, fill=(12, 33, 52, 220), outline=(32, 61, 84, 255), width=1)
        
        if bar_type == "overworld":
            cx = 10
            # [WASD]
            draw_keycap(d, cx, y_start + 4, 38, 18, "WASD", font_key, gold=True)
            cx += 42
            d.text((cx, y_start + 7), "Ruch", fill=(216, 218, 218, 255), font=font_lbl)
            cx += 42
            
            d.text((cx, y_start + 7), "|", fill=(94, 111, 122, 255), font=font_lbl)
            cx += 14
            
            # [Z] [ENTER]
            draw_keycap(d, cx, y_start + 4, 18, 18, "Z", font_key, gold=True)
            cx += 22
            draw_keycap(d, cx, y_start + 4, 40, 18, "ENTER", font_key, gold=True)
            cx += 44
            d.text((cx, y_start + 7), "Interakcja / Akcja", fill=(216, 218, 218, 255), font=font_lbl)
            cx += 124
            
            d.text((cx, y_start + 7), "|", fill=(94, 111, 122, 255), font=font_lbl)
            cx += 14
            
            # [M] [TAB]
            draw_keycap(d, cx, y_start + 4, 18, 18, "M", font_key)
            cx += 22
            draw_keycap(d, cx, y_start + 4, 28, 18, "TAB", font_key)
            cx += 32
            d.text((cx, y_start + 7), "Menu / Ekwipunek", fill=(216, 218, 218, 255), font=font_lbl)

        elif bar_type == "battle":
            cx = 10
            # [W] [S]
            draw_keycap(d, cx, y_start + 4, 18, 18, "W", font_key, gold=True)
            cx += 22
            draw_keycap(d, cx, y_start + 4, 18, 18, "S", font_key, gold=True)
            cx += 22
            lbl_choice = "Wybór: Atak / Umiejętność"
            d.text((cx, y_start + 7), lbl_choice, fill=(216, 218, 218, 255), font=font_lbl)
            bbox = font_lbl.getbbox(lbl_choice)
            cx += (bbox[2] - bbox[0]) + 12
            
            d.text((cx, y_start + 7), "|", fill=(94, 111, 122, 255), font=font_lbl)
            cx += 14
            
            # [Z] [SPACJA]
            draw_keycap(d, cx, y_start + 4, 18, 18, "Z", font_key, gold=True)
            cx += 22
            draw_keycap(d, cx, y_start + 4, 48, 18, "SPACJA", font_key, gold=True)
            cx += 52
            lbl_confirm = "Zatwierdź"
            d.text((cx, y_start + 7), lbl_confirm, fill=(216, 218, 218, 255), font=font_lbl)
            bbox_c = font_lbl.getbbox(lbl_confirm)
            cx += (bbox_c[2] - bbox_c[0]) + 12
            
            d.text((cx, y_start + 7), "|", fill=(94, 111, 122, 255), font=font_lbl)
            cx += 14
            
            # [X] [ESC]
            draw_keycap(d, cx, y_start + 4, 18, 18, "X", font_key)
            cx += 22
            draw_keycap(d, cx, y_start + 4, 28, 18, "ESC", font_key)
            cx += 32
            d.text((cx, y_start + 7), "Wstecz", fill=(216, 218, 218, 255), font=font_lbl)

        elif bar_type == "campfire":
            cx = 10
            # [1]
            draw_keycap(d, cx, y_start + 4, 18, 18, "1", font_key, gold=True)
            cx += 22
            d.text((cx, y_start + 7), "Dorzuć do ognia", fill=(216, 218, 218, 255), font=font_lbl)
            cx += 105
            
            d.text((cx, y_start + 7), "|", fill=(94, 111, 122, 255), font=font_lbl)
            cx += 14
            
            # [2]
            draw_keycap(d, cx, y_start + 4, 18, 18, "2", font_key, gold=True)
            cx += 22
            d.text((cx, y_start + 7), "Klasyk O.S.T.R.", fill=(216, 218, 218, 255), font=font_lbl)
            cx += 100
            
            d.text((cx, y_start + 7), "|", fill=(94, 111, 122, 255), font=font_lbl)
            cx += 14
            
            # [3]
            draw_keycap(d, cx, y_start + 4, 18, 18, "3", font_key, gold=True)
            cx += 22
            d.text((cx, y_start + 7), "Toast za ekipę 36+!", fill=(216, 218, 218, 255), font=font_lbl)

    img.save(f'{UI_DIR}/keys_legend.png')
    print(f'Generated: {UI_DIR}/keys_legend.png (560x84 RGBA)')

if __name__ == '__main__':
    print("=== Generating Pixel Art UI & FX Assets ===")
    generate_avatars()
    generate_phone_frame()
    generate_speech_bubbles()
    generate_exit_beacons()
    generate_keycaps()
    generate_keys_legend_panels()
    print("=== All Assets Successfully Generated ===")
