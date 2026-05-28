"""2D flat editorial illustration — observer vs the world's pace."""
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = Path("/home/user/supercode/output/cinematic")
OUT.mkdir(parents=True, exist_ok=True)
W, H = 1920, 1080

F_SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
F_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

rng = np.random.default_rng(7)

# ── Palette ───────────────────────────────────────────────────────────────────
WALL        = (232, 213, 182)   # warm beige
WALL_FAR    = (218, 198, 162)   # slightly darker far wall
FLOOR       = (185, 158, 118)   # warm tan floor
FLOOR_DARK  = (160, 134,  96)   # floor shadow
CEILING     = (210, 196, 170)   # muted ceiling
WIN_LIGHT   = (255, 242, 195)   # window warm glow
WIN_FRAME   = ( 62,  42,  22)   # dark wood frame
TABLE       = ( 92,  58,  28)   # dark wood table
CHAIR       = (120,  82,  42)   # chair brown
CHAIR_LIGHT = (145, 102,  58)
BG_FIG      = (148, 108,  68)   # background figure mid-tone
BG_FIG_D    = (110,  76,  42)   # background figure dark
MOTION_LINE = (200, 158,  90)   # motion streak amber
FG_JACKET   = ( 52,  36,  22)   # foreground jacket dark
FG_SKIN     = (210, 165, 120)   # foreground skin
FG_HAIR     = ( 38,  26,  14)   # hair
FG_SHIRT    = (235, 220, 195)   # shirt cream
FG_SHADOW   = ( 38,  28,  16)   # deep shadow
PLANT       = ( 52,  80,  42)
PLANT_LIGHT = ( 72, 108,  58)
AMBER_GLOW  = (255, 185,  60)   # window ambient
WHITE_BD    = (240, 232, 215)   # whiteboard
TEXT_HINT   = (180, 168, 148)   # muted text on whiteboard


def grain(img, intensity=0.018):
    arr = np.array(img, dtype=np.float32)
    noise = rng.normal(0, intensity*255, arr.shape[:2])[:,:,None]
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


# ── Build scene in layers ─────────────────────────────────────────────────────

# Layer 1 — Environment
env = Image.new("RGBA", (W, H), (*WALL, 255))
ed  = ImageDraw.Draw(env)

# Ceiling
ed.rectangle([(0,0),(W, 120)], fill=(*CEILING, 255))
ed.rectangle([(0,118),(W,122)], fill=(*WIN_FRAME, 80))

# Far wall (behind the action — slightly recessed tone)
horizon = 340
ed.rectangle([(0, 120), (W, horizon)], fill=(*WALL_FAR, 255))
ed.rectangle([(0, horizon-2),(W, horizon+1)], fill=(*FLOOR_DARK, 120))

# Floor — with subtle perspective lines
ed.rectangle([(0, horizon), (W, H)], fill=(*FLOOR, 255))
vp_x, vp_y = W//2, horizon
for x in range(-W, W*2, 120):
    ed.line([(vp_x, vp_y), (x, H)], fill=(*FLOOR_DARK, 35), width=1)

# ── Windows — left wall (light source) ───────────────────────────────────────
for wx in [60, 230, 400]:
    ww, wh = 130, 400
    wy = 135
    # Glow behind window
    for i in range(12, 0, -1):
        alpha = int(i * 6)
        ed.rectangle([(wx-i*4, wy-i*3), (wx+ww+i*4, wy+wh+i*3)],
                     fill=(*AMBER_GLOW, alpha))
    ed.rectangle([(wx, wy), (wx+ww, wy+wh)], fill=(*WIN_LIGHT, 255))
    # Frame
    ed.rectangle([(wx-6, wy-6), (wx+ww+6, wy+wh+6)], outline=(*WIN_FRAME, 255), width=6)
    # Cross pane
    mid_x = wx + ww//2
    mid_y = wy + wh//2
    ed.rectangle([(mid_x-3, wy), (mid_x+3, wy+wh)], fill=(*WIN_FRAME, 255))
    ed.rectangle([(wx, mid_y-3), (wx+ww, mid_y+3)],  fill=(*WIN_FRAME, 255))

# Window light spill on floor
for i in range(20, 0, -1):
    alpha = int(i * 4)
    ed.polygon([(60, horizon+10), (530, horizon+10), (800, H), (-200, H)],
               fill=(*WIN_LIGHT, alpha))

# ── Whiteboard — right side ───────────────────────────────────────────────────
wb_x, wb_y, wb_w, wb_h = W-440, 145, 380, 300
ed.rectangle([(wb_x-8, wb_y-8),(wb_x+wb_w+8, wb_y+wb_h+8)], fill=(*WIN_FRAME, 255))
ed.rectangle([(wb_x, wb_y),(wb_x+wb_w, wb_y+wb_h)], fill=(*WHITE_BD, 255))
# Scribbled content
fn_wb = ImageFont.truetype(F_SANS, 18)
for i, line in enumerate(["Q3 STRATEGY", "─────────────", "• Growth targets",
                           "• Key markets ███", "• Timeline →", "ACTION ITEMS"]):
    ed.text((wb_x+18, wb_y+20+i*38), line, font=fn_wb, fill=(*TEXT_HINT, 200))
ed.rectangle([(wb_x+18, wb_y+wb_h-40),(wb_x+wb_w-18, wb_y+wb_h-38)],
             fill=(*TEXT_HINT, 120))

# Whiteboard tray
ed.rectangle([(wb_x, wb_y+wb_h),(wb_x+wb_w, wb_y+wb_h+14)], fill=(*WIN_FRAME, 255))

# ── Conference table ──────────────────────────────────────────────────────────
tx, ty, tw, th = 520, horizon-40, 880, 55
# Table top
ed.ellipse([(tx, ty-22),(tx+tw, ty+22)], fill=(*TABLE, 255))
ed.rectangle([(tx, ty-8),(tx+tw, ty+th)], fill=(*TABLE, 255))
# Table front edge
ed.ellipse([(tx, ty+th-22),(tx+tw, ty+th+22)], fill=(*WIN_FRAME, 255))
# Leg shadows
for lx in [tx+60, tx+tw-60]:
    ed.rectangle([(lx-8, ty+th), (lx+8, ty+th+160)], fill=(*WIN_FRAME, 220))

# Chairs along table (back row — perspective)
for cx_c in range(tx+80, tx+tw-40, 130):
    chy = ty - 62
    chw, chh = 56, 50
    ed.rectangle([(cx_c-chw//2, chy),(cx_c+chw//2, chy+chh)],  fill=(*CHAIR, 255))
    ed.rectangle([(cx_c-chw//2, chy-32),(cx_c+chw//2, chy)],   fill=(*CHAIR_LIGHT, 255))
    ed.rectangle([(cx_c-6, chy+chh),(cx_c+6, chy+chh+30)],     fill=(*CHAIR, 200))

# Plants — corners
for px_p, py_p in [(W-90, horizon+20), (90, horizon+20)]:
    pot_w = 52
    ed.rectangle([(px_p-pot_w//2, py_p+60),(px_p+pot_w//2, py_p+110)],
                 fill=(90, 65, 35, 255))
    for i in range(8):
        angle = i * 45
        lx = px_p + int(32*np.cos(np.radians(angle)))
        ly = py_p + int(32*np.sin(np.radians(angle))) + 30
        ed.ellipse([(lx-16,ly-10),(lx+16,ly+10)], fill=(*PLANT_LIGHT,220))
    ed.ellipse([(px_p-22, py_p+8),(px_p+22, py_p+52)], fill=(*PLANT, 255))


# Layer 2 — Background figures (drawn separately, then blurred)
fig_layer = Image.new("RGBA", (W, H), (0,0,0,0))
fd = ImageDraw.Draw(fig_layer)

def draw_bg_figure(d, x, y, scale=1.0, tilt=0, arms_up=False, leaning=False, color=BG_FIG, dark=BG_FIG_D):
    """Draw a simple flat cartoon figure."""
    s = scale
    # Head
    d.ellipse([(x-int(18*s), y-int(18*s)),(x+int(18*s), y+int(18*s))],
              fill=(*color, 255))
    # Body
    bx0, bx1 = x-int(16*s), x+int(16*s)
    body_h = int(52*s)
    if leaning:
        bx0 -= int(10*s); bx1 -= int(10*s)
    d.rectangle([(bx0, y+int(18*s)),(bx1, y+int(18*s)+body_h)], fill=(*dark, 255))
    # Legs
    for lx in [bx0+int(6*s), bx1-int(6*s)]:
        d.rectangle([(lx-int(6*s), y+int(18*s)+body_h),
                     (lx+int(6*s), y+int(18*s)+body_h+int(44*s))],
                    fill=(*color, 255))
    # Arms
    if arms_up:
        d.line([(x, y+int(24*s)), (x-int(36*s), y+int(2*s))],  fill=(*dark, 255), width=int(8*s))
        d.line([(x, y+int(24*s)), (x+int(36*s), y-int(8*s))],  fill=(*dark, 255), width=int(8*s))
    elif leaning:
        d.line([(x, y+int(24*s)), (x-int(30*s), y+int(36*s))], fill=(*dark, 255), width=int(8*s))
        d.line([(x, y+int(24*s)), (x+int(28*s), y+int(30*s))], fill=(*dark, 255), width=int(8*s))
    else:
        d.line([(x, y+int(24*s)), (x-int(28*s), y+int(44*s))], fill=(*dark, 255), width=int(8*s))
        d.line([(x, y+int(24*s)), (x+int(30*s), y+int(38*s))], fill=(*dark, 255), width=int(8*s))

# Motion streaks
def motion_streak(d, x, y, w, h, col=MOTION_LINE):
    d.rectangle([(x, y),(x+w, y+h)], fill=(*col, 40))

# Background figures — various poses, positions
configs = [
    (680,  270, 0.90, False, True,  False),
    (820,  255, 0.85, False, False, True),
    (970,  260, 0.92, False, True,  False),
    (1110, 265, 0.88, False, False, False),
    (1260, 258, 0.86, False, True,  True),
    (740,  270, 0.78, False, False, False),
    (1060, 262, 0.80, False, True,  False),
]
for bx, by, sc, tilt, arms, lean in configs:
    draw_bg_figure(fd, bx, by, scale=sc, tilt=tilt, arms_up=arms, leaning=lean)
    # Motion streaks around active figures
    if arms:
        motion_streak(fd, bx-60, by-10, 50, 8)
        motion_streak(fd, bx+20, by-18, 40, 6)

# Seated figures at table
for sx in [620, 760, 920, 1080, 1220]:
    sy = horizon - 38
    sc = 0.75
    fd.ellipse([(sx-14, sy-14),(sx+14, sy+14)], fill=(*BG_FIG, 255))
    fd.rectangle([(sx-13, sy+13),(sx+13, sy+13+38)], fill=(*BG_FIG_D, 255))
    # Arm reaching forward
    fd.line([(sx, sy+20),(sx+35, sy+10)], fill=(*BG_FIG_D, 255), width=7)

# Apply blur to background figures
fig_blurred = fig_layer.filter(ImageFilter.GaussianBlur(radius=3.2))


# Layer 3 — Foreground observer: spiky-hair cartoon character in yellow hoodie
HOODIE      = (242, 178,  18)   # bright yellow
HOODIE_D    = (198, 140,   8)   # hoodie shadow
HOODIE_S    = (255, 215,  80)   # hoodie highlight
FACE_W      = (250, 248, 242)   # white face
HAIR_B      = ( 20,  16,  12)   # black spiky hair
EYE_B       = ( 18,  14,  10)   # eye black
HAND_W      = (245, 240, 230)   # white glove/hand

fg_layer = Image.new("RGBA", (W, H), (0,0,0,0))
fgd = ImageDraw.Draw(fg_layer)

obs_x, obs_y = W//2 - 180, 220
s = 1.72

# ── Drop shadow ───────────────────────────────────────────────────────────────
for i in range(14, 0, -1):
    fgd.ellipse([(obs_x-int(55*s)+i*3, obs_y+int(175*s)),
                 (obs_x+int(55*s)-i*3, obs_y+int(190*s))],
                fill=(120, 85, 30, int(i*4)))

# ── Shoes ─────────────────────────────────────────────────────────────────────
for sx_s, flip in [(obs_x-int(20*s), -1), (obs_x+int(10*s), 1)]:
    fgd.ellipse([(sx_s-int(14*s), obs_y+int(164*s)),
                 (sx_s+int(22*s), obs_y+int(178*s))],
                fill=(30, 24, 18, 255))

# ── Legs (dark jeans) ─────────────────────────────────────────────────────────
for lx in [obs_x-int(18*s), obs_x+int(6*s)]:
    fgd.rectangle([(lx-int(14*s), obs_y+int(106*s)),
                   (lx+int(14*s), obs_y+int(166*s))],
                  fill=(40, 34, 52, 255))
    # Seam highlight
    fgd.rectangle([(lx-int(2*s), obs_y+int(106*s)),
                   (lx+int(2*s), obs_y+int(164*s))],
                  fill=(55, 48, 68, 200))

# ── Hoodie body ───────────────────────────────────────────────────────────────
hoodie_pts = [
    (obs_x-int(42*s), obs_y+int(44*s)),
    (obs_x+int(42*s), obs_y+int(44*s)),
    (obs_x+int(50*s), obs_y+int(108*s)),
    (obs_x-int(50*s), obs_y+int(108*s)),
]
fgd.polygon(hoodie_pts, fill=(*HOODIE, 255))
# Hoodie highlight stripe
fgd.polygon([
    (obs_x-int(10*s), obs_y+int(44*s)),
    (obs_x+int(10*s), obs_y+int(44*s)),
    (obs_x+int(14*s), obs_y+int(108*s)),
    (obs_x-int(14*s), obs_y+int(108*s)),
], fill=(*HOODIE_S, 120))
# Pocket pouch
fgd.rectangle([(obs_x-int(28*s), obs_y+int(82*s)),
               (obs_x+int(28*s), obs_y+int(106*s))],
              fill=(*HOODIE_D, 200))
fgd.rectangle([(obs_x-int(2*s), obs_y+int(82*s)),
               (obs_x+int(2*s), obs_y+int(106*s))],
              fill=(*HOODIE_D, 255))

# ── Hood (behind head) ────────────────────────────────────────────────────────
fgd.ellipse([(obs_x-int(48*s), obs_y-int(32*s)),
             (obs_x+int(48*s), obs_y+int(48*s))],
            fill=(*HOODIE_D, 255))

# ── Left arm — raised, hand to chin ──────────────────────────────────────────
# Upper arm
arm_pts_l = [
    (obs_x-int(42*s), obs_y+int(50*s)),
    (obs_x-int(24*s), obs_y+int(50*s)),
    (obs_x-int(10*s), obs_y+int(90*s)),
    (obs_x-int(30*s), obs_y+int(90*s)),
]
fgd.polygon(arm_pts_l, fill=(*HOODIE, 255))
# Forearm bent upward toward chin
forearm_pts = [
    (obs_x-int(30*s), obs_y+int(90*s)),
    (obs_x-int(10*s), obs_y+int(90*s)),
    (obs_x+int(2*s),  obs_y+int(52*s)),
    (obs_x-int(18*s), obs_y+int(50*s)),
]
fgd.polygon(forearm_pts, fill=(*HOODIE, 255))
# Cuff
fgd.ellipse([(obs_x-int(8*s), obs_y+int(44*s)),
             (obs_x+int(12*s), obs_y+int(62*s))],
            fill=(*HOODIE_D, 255))
# Hand at chin
fgd.ellipse([(obs_x-int(6*s), obs_y+int(36*s)),
             (obs_x+int(16*s), obs_y+int(56*s))],
            fill=(*HAND_W, 255))
# Finger suggestion
fgd.ellipse([(obs_x+int(4*s), obs_y+int(30*s)),
             (obs_x+int(14*s), obs_y+int(44*s))],
            fill=(*HAND_W, 255))

# ── Right arm — relaxed at side ───────────────────────────────────────────────
arm_pts_r = [
    (obs_x+int(24*s), obs_y+int(50*s)),
    (obs_x+int(44*s), obs_y+int(50*s)),
    (obs_x+int(50*s), obs_y+int(96*s)),
    (obs_x+int(28*s), obs_y+int(96*s)),
]
fgd.polygon(arm_pts_r, fill=(*HOODIE, 255))

# ── Neck ──────────────────────────────────────────────────────────────────────
fgd.rectangle([(obs_x-int(10*s), obs_y+int(20*s)),
               (obs_x+int(10*s), obs_y+int(46*s))],
              fill=(*FACE_W, 255))

# ── Head — large round white face ────────────────────────────────────────────
head_r = int(34*s)
# Face (white oval)
fgd.ellipse([(obs_x-head_r, obs_y-head_r+int(4*s)),
             (obs_x+head_r, obs_y+head_r+int(4*s))],
            fill=(*FACE_W, 255))

# Subtle chin shadow
fgd.ellipse([(obs_x-int(20*s), obs_y+int(24*s)),
             (obs_x+int(20*s), obs_y+int(38*s))],
            fill=(220, 215, 205, 100))

# ── Eyes — large cartoon dots ────────────────────────────────────────────────
eye_r = int(9*s)
for ex, ey in [(obs_x-int(12*s), obs_y-int(6*s)), (obs_x+int(12*s), obs_y-int(6*s))]:
    # White of eye (slightly)
    fgd.ellipse([(ex-eye_r, ey-eye_r),(ex+eye_r, ey+eye_r)], fill=(*EYE_B, 255))
    # Shine
    fgd.ellipse([(ex+int(3*s), ey-int(4*s)),(ex+int(6*s), ey-int(1*s))],
                fill=(255, 255, 255, 220))

# ── Mouth — small, slight curve (thinking expression) ────────────────────────
mx, my = obs_x+int(4*s), obs_y+int(12*s)
fgd.line([(mx-int(6*s), my),(mx+int(6*s), my-int(2*s))],
         fill=(*EYE_B, 180), width=int(3*s))

# ── Spiky hair ────────────────────────────────────────────────────────────────
# Base hair mass
fgd.ellipse([(obs_x-head_r-int(4*s), obs_y-head_r-int(6*s)),
             (obs_x+head_r+int(4*s), obs_y+int(8*s))],
            fill=(*HAIR_B, 255))
# Spikes — multiple triangular points
spikes = [
    # (tip_x_offset, tip_y_offset, base_width, angle_offset)
    (-int(34*s), -int(62*s), int(22*s)),
    (-int(18*s), -int(74*s), int(20*s)),
    (  int(2*s), -int(78*s), int(22*s)),
    ( int(20*s), -int(72*s), int(20*s)),
    ( int(36*s), -int(60*s), int(18*s)),
    (-int(46*s), -int(44*s), int(16*s)),
    ( int(46*s), -int(42*s), int(16*s)),
    (-int(52*s), -int(24*s), int(14*s)),
]
for dx_s, dy_s, bw in spikes:
    tip_x = obs_x + dx_s
    tip_y = obs_y + dy_s
    base_cx = obs_x + int(dx_s * 0.3)
    base_cy = obs_y - int(8*s)
    fgd.polygon([
        (tip_x, tip_y),
        (base_cx - bw//2, base_cy),
        (base_cx + bw//2, base_cy),
    ], fill=(*HAIR_B, 255))


# ── Compose all layers ────────────────────────────────────────────────────────
final = env.convert("RGBA")
final = Image.alpha_composite(final, fig_blurred)
final = Image.alpha_composite(final, fg_layer)

# Warm amber atmosphere overlay
atmo = Image.new("RGBA", (W, H), (0,0,0,0))
atmo_d = ImageDraw.Draw(atmo)
# Window light wash across left portion
for i in range(30, 0, -1):
    alpha = int(i * 2.2)
    atmo_d.rectangle([(0, 0),(int(W * 0.45) + i*12, H)], fill=(*WIN_LIGHT, alpha))
final = Image.alpha_composite(final, atmo)

# Depth haze — background slightly lighter/warmer
haze = Image.new("RGBA", (W, H), (0,0,0,0))
haze_d = ImageDraw.Draw(haze)
for row in range(H):
    if row < horizon:
        alpha = int((1 - row/horizon) * 28)
        haze_d.rectangle([(0,row),(W,row+1)], fill=(*WALL_FAR, alpha))
final = Image.alpha_composite(final, haze)

# Grain + slight vignette
final_np = np.array(final.convert("RGB"), dtype=np.float32)
# Soft vignette
y_v = np.linspace(-1,1,H)[:,None]; x_v = np.linspace(-1,1,W)[None,:]
vig = np.clip((x_v**2 + (y_v*1.3)**2)**1.6 * 0.40, 0, 1)[:,:,None]
final_np = final_np * (1-vig)
# Grain
noise = rng.normal(0, 0.015*255, final_np.shape)
final_np = np.clip(final_np + noise, 0, 255).astype(np.uint8)

result = Image.fromarray(final_np)

# Label
draw_f = ImageDraw.Draw(result)
fn_label = ImageFont.truetype(F_BOLD, 20)
draw_f.text((30, H-50), "[ INSERT CHARACTER REFERENCE ]  ← foreground observer",
            font=fn_label, fill=(196, 30, 58, 200))

result.save(OUT/"editorial_observer.jpg", quality=95)
print(f"✓ Saved → {OUT}/editorial_observer.jpg")
