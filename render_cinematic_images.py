"""Generate cinematic scene images — architectural silhouettes, environments, dramatic lighting."""
import math, numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = Path("/home/user/supercode/output/cinematic")
OUT.mkdir(parents=True, exist_ok=True)
W, H = 1920, 1080
rng  = np.random.default_rng(99)

F_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
F_SANS  = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
F_BOLD  = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def font(p, s): return ImageFont.truetype(p, s)

# ── shared utilities ──────────────────────────────────────────────────────────

def glow_np(arr, fx, fy, fr, col, intensity):
    px, py = fx*W, fy*H
    r = fr * min(W, H)
    y = np.arange(H)[:,None].astype(np.float32)
    x = np.arange(W)[None,:].astype(np.float32)
    d = np.sqrt((x-px)**2 + (y-py)**2)
    mask = np.clip(1 - d/r, 0, 1)[:,:,None] ** 1.6
    return arr + mask * np.array(col, dtype=np.float32) * intensity

def vignette(arr, strength=0.7):
    y = np.linspace(-1,1,H)[:,None]
    x = np.linspace(-1,1,W)[None,:]
    d = np.sqrt(x**2 + (y*1.4)**2)
    v = np.clip(d**2.2 * strength, 0, 1)[:,:,None]
    return arr * (1-v)

def grain(arr, intensity=0.022):
    return arr + rng.normal(0, intensity*255, arr.shape)

def finalize(arr):
    arr = vignette(arr)
    arr = grain(arr)
    return np.clip(arr, 0, 255).astype(np.uint8)

def cx(draw, text, fn, y, col, alpha=255):
    w = draw.textlength(text, font=fn)
    draw.text(((W-w)/2, y), text, font=fn, fill=(*col, alpha))

def save(img, name, label):
    img.convert("RGB").save(OUT/name, quality=95)
    print(f"✓ {label}")


# ── Image 1: Night city skyline ───────────────────────────────────────────────
print("Rendering city skyline…")
# Sky gradient — deep blue to near-black
sky = np.zeros((H, W, 3), dtype=np.float32)
for row in range(H):
    t = row / H
    sky[row] = np.array([4+t*6, 6+t*10, 18+t*28]) * (1-t*0.4)

# Distant city glow on horizon
sky = glow_np(sky, 0.5, 0.72, 0.55, (30, 50, 120), 0.55)
sky = glow_np(sky, 0.3, 0.75, 0.30, (20, 35,  90), 0.35)
sky = glow_np(sky, 0.7, 0.74, 0.28, (15, 25,  70), 0.28)

img = Image.fromarray(finalize(sky)).convert("RGBA")
draw = ImageDraw.Draw(img)

# Draw city buildings as silhouettes
horizon = int(H * 0.60)
rs = np.random.RandomState(42)

buildings = []
x = -40
while x < W + 40:
    w = rs.randint(30, 110)
    h = rs.randint(60, 340)
    buildings.append((x, horizon - h, x + w, horizon))
    x += w + rs.randint(0, 12)

# Back layer (shorter, lighter grey)
for bx0, by0, bx1, by1 in buildings:
    bx0b, bx1b = bx0+4, bx1-4
    by0b = by0 + rs.randint(40, 140)
    by0b = min(by0b, horizon - 20)
    draw.rectangle([(bx0b, by0b), (bx1b, by1)], fill=(12, 14, 22, 255))

# Front layer silhouettes
for bx0, by0, bx1, by1 in buildings:
    draw.rectangle([(bx0, by0), (bx1, by1)], fill=(5, 6, 10, 255))
    # Lit windows
    ww, wh = 4, 5
    for wy in range(by0 + 8, by1 - 10, 14):
        for wx in range(bx0 + 5, bx1 - 5, 10):
            if rs.random() < 0.38:
                brightness = rs.randint(140, 255)
                warmth     = rs.randint(0, 60)
                draw.rectangle(
                    [(wx, wy), (wx+ww, wy+wh)],
                    fill=(brightness, brightness-warmth//2, max(0,brightness-warmth), 255)
                )

# Ground / street
draw.rectangle([(0, horizon), (W, H)], fill=(3, 3, 6, 255))

# Street glow — orange sodium lamps
arr2 = np.array(img, dtype=np.float32)
for lx in range(80, W, 180):
    arr2 = glow_np(arr2[:,:,:3], lx/W, 0.62, 0.06, (180, 90, 20), 0.45)
    arr2_full = np.concatenate([arr2, np.full((H,W,1),255,dtype=np.float32)], axis=2)
    arr2 = arr2_full[:,:,:3]

arr2 = grain(arr2, 0.025)
arr2 = np.clip(arr2, 0, 255).astype(np.uint8)
img2 = Image.fromarray(arr2).convert("RGBA")
draw2 = ImageDraw.Draw(img2)
draw2.rectangle([(0,0),(W,4)], fill=(196,30,58,255))
draw2.rectangle([(0,H-4),(W,H)], fill=(196,30,58,255))
cx(draw2, "FINALLY SOLVED", font(F_BOLD, 42), H-90, (196,30,58), 220)
save(img2, "01_city_night.jpg", "City night skyline")


# ── Image 2: Courthouse / institution ────────────────────────────────────────
print("Rendering courthouse…")
arr = np.zeros((H, W, 3), dtype=np.float32)
# Sky — overcast grey-blue
for row in range(H):
    t = row / H
    arr[row] = np.array([8+t*4, 8+t*5, 14+t*8])

arr = glow_np(arr, 0.5, 0.0, 0.80, (30, 25, 50), 0.35)
arr = glow_np(arr, 0.5, 0.5, 0.90, (20, 15, 35), 0.20)

img = Image.fromarray(finalize(arr)).convert("RGBA")
draw = ImageDraw.Draw(img)

# Steps
step_y = int(H * 0.78)
for i in range(6):
    sy = step_y + i * 18
    sx = int(W*0.12) - i*28
    draw.rectangle([(sx, sy), (W-sx, sy+18)], fill=(14, 12, 18, 255))

# Main building body
body_top = int(H * 0.28)
body_l   = int(W * 0.14)
body_r   = int(W * 0.86)
draw.rectangle([(body_l, body_top), (body_r, step_y)], fill=(10, 9, 15, 255))

# Triangular pediment
pediment_pts = [(body_l-20, body_top), (W//2, int(H*0.10)), (body_r+20, body_top)]
draw.polygon(pediment_pts, fill=(8, 7, 12, 255))

# Columns
col_count = 10
col_w = 28
col_gap = (body_r - body_l) // col_count
for i in range(col_count + 1):
    cx_pos = body_l + i * col_gap
    draw.rectangle([(cx_pos-col_w//2, body_top-10), (cx_pos+col_w//2, step_y)],
                   fill=(16, 14, 22, 255))
    # Column highlight
    draw.rectangle([(cx_pos-col_w//2, body_top-10), (cx_pos-col_w//2+3, step_y)],
                   fill=(24, 20, 32, 255))

# Windows — tall arched
for i in range(7):
    wx = body_l + 60 + i * ((body_r - body_l - 120) // 7)
    wy = int(H * 0.42)
    ww2, wh2 = 38, 90
    draw.rectangle([(wx, wy), (wx+ww2, wy+wh2)], fill=(6, 5, 9, 255))
    draw.rectangle([(wx+2, wy+2), (wx+ww2-2, wy+wh2-2)], fill=(18, 14, 28, 200))

# Overlay glow from behind building
arr3 = np.array(img, dtype=np.float32)[:,:,:3]
arr3 = glow_np(arr3, 0.5, 0.22, 0.30, (100, 80, 160), 0.18)
arr3 = grain(arr3, 0.020)
arr3 = vignette(arr3, 0.80)
arr3 = np.clip(arr3, 0, 255).astype(np.uint8)
img3 = Image.fromarray(arr3).convert("RGBA")
draw3 = ImageDraw.Draw(img3)
draw3.rectangle([(0,0),(W,4)], fill=(196,30,58,255))
draw3.rectangle([(0,H-4),(W,H)], fill=(196,30,58,255))
cx(draw3, "THE SYSTEM KNEW", font(F_SERIF, 64), int(H*0.82), (196,30,58), 230)
cx(draw3, "JEFFREY EPSTEIN", font(F_BOLD, 28), int(H*0.87)+50, (160,150,155), 180)
save(img3, "02_courthouse.jpg", "Courthouse silhouette")


# ── Image 3: Redacted document ────────────────────────────────────────────────
print("Rendering redacted document…")
arr = np.zeros((H, W, 3), dtype=np.float32)
arr[:] = np.array([6, 5, 8])
arr = glow_np(arr, 0.5, 0.5, 0.70, (15, 10, 20), 0.30)

img = Image.fromarray(finalize(arr)).convert("RGBA")
draw = ImageDraw.Draw(img)

# Document card
dw, dh = 900, 640
dx, dy = (W-dw)//2, (H-dh)//2
draw.rectangle([(dx, dy), (dx+dw, dy+dh)], fill=(18, 16, 22, 240))
draw.rectangle([(dx, dy), (dx+dw, dy+dh)], outline=(40, 35, 50, 255), width=1)

# Document header
draw.rectangle([(dx+30, dy+30), (dx+dw-30, dy+80)], fill=(30, 25, 38, 255))
fn_doc = font(F_BOLD, 22)
fn_sm  = font(F_SANS, 16)
draw.text((dx+50, dy+44), "UNITED STATES DISTRICT COURT — SOUTHERN DISTRICT OF FLORIDA",
          font=fn_doc, fill=(150, 140, 155, 255))
draw.text((dx+50, dy+72), "CASE NO. 08-80736-CIV",
          font=fn_sm, fill=(100, 92, 108, 200))

# Text lines (some redacted)
line_y = dy + 120
lines = [
    ("The Government agrees that it shall not prosecute", False),
    ("EPSTEIN for any federal crimes                   ", False),
    ("that he has committed or might have committed", False),
    ("in connection with                              ", False),
    ("██████████████████████████████████████", True),
    ("                                               ", False),
    ("This agreement shall be binding upon all", False),
    ("█████████████ and all █████████ of", True),
    ("the United States of America.", False),
    ("                              ", False),
    ("██████████████████████████████████████████████", True),
    ("██████████████████████████", True),
]
fn_line = font(F_SANS, 20)
for line, redacted in lines:
    col = (50, 45, 55, 255) if not redacted else (8, 6, 10, 255)
    bg_col = None if not redacted else (8, 6, 10, 255)
    if redacted:
        tw = draw.textlength(line, font=fn_line)
        draw.rectangle([(dx+50, line_y-2), (dx+50+int(tw), line_y+22)], fill=(8,6,10,255))
    draw.text((dx+50, line_y), line, font=fn_line, fill=col)
    line_y += 32

# Stamp — CONFIDENTIAL
stamp_fn = font(F_BOLD, 52)
stamp_txt = "NON-PROSECUTION AGREEMENT"
sw = draw.textlength(stamp_txt, font=stamp_fn)
draw.text((dx+(dw-sw)//2, dy+dh-90), stamp_txt, font=stamp_fn, fill=(196,30,58, 80))

arr4 = np.array(img, dtype=np.float32)[:,:,:3]
arr4 = grain(arr4, 0.018)
arr4 = vignette(arr4, 0.75)
arr4 = np.clip(arr4, 0, 255).astype(np.uint8)
img4 = Image.fromarray(arr4).convert("RGBA")
draw4 = ImageDraw.Draw(img4)
draw4.rectangle([(0,0),(W,4)], fill=(196,30,58,255))
draw4.rectangle([(0,H-4),(W,H)], fill=(196,30,58,255))
cx(draw4, "SEALED. CLASSIFIED. BURIED.", font(F_SERIF, 52), H-120, (196,30,58), 220)
save(img4, "03_redacted_document.jpg", "Redacted document")


# ── Image 4: Person in shadows / backlit silhouette ──────────────────────────
print("Rendering silhouette portrait…")
arr = np.zeros((H, W, 3), dtype=np.float32)
arr[:] = np.array([3, 2, 4])
# Background light source — strong backlight
arr = glow_np(arr, 0.5, 0.42, 0.50, (255, 240, 200), 0.55)
arr = glow_np(arr, 0.5, 0.42, 0.28, (255, 255, 255), 0.35)
arr = glow_np(arr, 0.5, 0.42, 0.15, (255, 255, 255), 0.50)
# Color fringes
arr = glow_np(arr, 0.28, 0.5, 0.30, (20, 40, 120), 0.22)
arr = glow_np(arr, 0.72, 0.5, 0.30, (120, 20, 20), 0.22)

img = Image.fromarray(finalize(arr)).convert("RGBA")
draw = ImageDraw.Draw(img)

# Draw silhouette — head + shoulders
cx_s, cy_s = W//2, int(H*0.48)
# Head
r_head = 80
draw.ellipse([(cx_s-r_head, cy_s-r_head-30), (cx_s+r_head, cy_s+r_head-30)],
             fill=(2, 1, 3, 255))
# Neck
draw.rectangle([(cx_s-28, cy_s+46), (cx_s+28, cy_s+90)], fill=(2,1,3,255))
# Shoulders — suit shape
shoulder_pts = [
    (cx_s-280, H),
    (cx_s-280, cy_s+130),
    (cx_s-160, cy_s+88),
    (cx_s-45,  cy_s+90),
    (cx_s+45,  cy_s+90),
    (cx_s+160, cy_s+88),
    (cx_s+280, cy_s+130),
    (cx_s+280, H),
]
draw.polygon(shoulder_pts, fill=(2,1,3,255))
# Suit lapels (slightly lighter)
draw.polygon([
    (cx_s-45, cy_s+90), (cx_s-28, cy_s+55),
    (cx_s,    cy_s+120), (cx_s+28, cy_s+55),
    (cx_s+45, cy_s+90), (cx_s, cy_s+140)
], fill=(5,3,6,255))

# Rim light edges on silhouette
arr5 = np.array(img, dtype=np.float32)[:,:,:3]
arr5 = glow_np(arr5, 0.5, 0.42, 0.55, (255, 235, 190), 0.40)
arr5 = grain(arr5, 0.022)
arr5 = vignette(arr5, 0.72)
arr5 = np.clip(arr5, 0, 255).astype(np.uint8)
img5 = Image.fromarray(arr5).convert("RGBA")
draw5 = ImageDraw.Draw(img5)
draw5.rectangle([(0,0),(W,4)],   fill=(196,30,58,255))
draw5.rectangle([(0,H-4),(W,H)], fill=(196,30,58,255))
cx(draw5, "JEFFREY EPSTEIN", font(F_SERIF, 72), int(H*0.80), (240,240,240), 230)
cx(draw5, "FINANCIER  ·  TRAFFICKER  ·  PROTECTED", font(F_BOLD, 26), int(H*0.87), (196,30,58), 200)
save(img5, "04_silhouette_portrait.jpg", "Silhouette portrait")


# ── Image 5: Prison bars ─────────────────────────────────────────────────────
print("Rendering prison bars…")
arr = np.zeros((H, W, 3), dtype=np.float32)
arr[:] = np.array([4, 3, 5])
arr = glow_np(arr, 0.5, 0.5,  0.65, (180, 120, 40),  0.28)
arr = glow_np(arr, 0.5, 1.1,  0.55, (100,  60, 15),  0.40)
arr = glow_np(arr, 0.5, -0.1, 0.40, ( 20,  15, 35),  0.20)

img = Image.fromarray(finalize(arr)).convert("RGBA")
draw = ImageDraw.Draw(img)

# Horizontal bars top and bottom
draw.rectangle([(0, int(H*0.08)), (W, int(H*0.08)+18)], fill=(8,7,10,240))
draw.rectangle([(0, int(H*0.92)), (W, int(H*0.92)+18)], fill=(8,7,10,240))

# Vertical bars
bar_w   = 22
spacing = 95
for bx in range(0, W + spacing, spacing):
    # Shadow side
    draw.rectangle([(bx, 0), (bx+bar_w, H)], fill=(6, 5, 8, 230))
    # Highlight edge
    draw.rectangle([(bx, 0), (bx+3, H)], fill=(22, 18, 28, 200))
    draw.rectangle([(bx+bar_w-3, 0), (bx+bar_w, H)], fill=(14, 11, 18, 160))

arr6 = np.array(img, dtype=np.float32)[:,:,:3]
arr6 = grain(arr6, 0.026)
arr6 = vignette(arr6, 0.78)
arr6 = np.clip(arr6, 0, 255).astype(np.uint8)
img6 = Image.fromarray(arr6).convert("RGBA")
draw6 = ImageDraw.Draw(img6)
draw6.rectangle([(0,0),(W,4)],   fill=(196,30,58,255))
draw6.rectangle([(0,H-4),(W,H)], fill=(196,30,58,255))
cx(draw6, "13 MONTHS.", font(F_SERIF, 110), int(H*0.39), (240,240,240), 240)
cx(draw6, "Work release. Six days a week.", font(F_SANS, 36), int(H*0.58), (180,170,170), 200)
save(img6, "05_prison_bars.jpg", "Prison bars")


print(f"\nAll cinematic images saved to {OUT}/")
