"""25-second cinematic with rich generated backgrounds — Epstein / Finally Solved.
Atmospheric gradients · light glows · floating particles · chromatic aberration."""
import math, subprocess
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FFMPEG = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
OUTPUT = "/home/user/supercode/output/epstein_cinematic_v2.mp4"
W, H   = 1920, 1080
FPS    = 30
TOTAL  = 750

F_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
F_SANS  = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
F_BOLD  = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

BAR_H  = 136
AY     = BAR_H
AH     = H - BAR_H * 2
ACY    = AY + AH // 2

Path(OUTPUT).parent.mkdir(parents=True, exist_ok=True)
_font_cache: dict = {}
rng = np.random.default_rng(42)


def font(path, sz):
    k = (path, sz)
    if k not in _font_cache:
        _font_cache[k] = ImageFont.truetype(path, sz)
    return _font_cache[k]


def clamp(v): return max(0.0, min(1.0, v))
def it(fr, f0, f1, v0=0.0, v1=1.0):
    return v0 + (v1-v0)*clamp((fr-f0)/max(f1-f0,1))
def eo(t): t=clamp(t); return 1-(1-t)**3
def ei(t): t=clamp(t); return t**2


# ── background generators (all return float32 H×W×3 arrays 0-255) ────────────

def radial(center_col, edge_col, power=2.0, cx=0.5, cy=0.5):
    y = np.linspace(-1, 1, H)[:, None] * (H/W)
    x = np.linspace(-1, 1, W)[None, :]
    d = np.sqrt((x - (cx-0.5)*2)**2 + (y - (cy-0.5)*2*(H/W))**2)
    t = np.clip(d / 1.4, 0, 1)[:, :, None] ** power
    c0 = np.array(center_col, dtype=np.float32)
    c1 = np.array(edge_col,   dtype=np.float32)
    return c0*(1-t) + c1*t


def linear(top_col, bot_col):
    t = np.linspace(0, 1, H)[:, None, None]
    c0 = np.array(top_col, dtype=np.float32)
    c1 = np.array(bot_col, dtype=np.float32)
    return (c0*(1-t) + c1*t) * np.ones((1, W, 1))


def glow(arr, fx, fy, fr, col, intensity):
    h, w = arr.shape[:2]
    px, py = fx*w, fy*h
    r = fr * min(w, h)
    y = np.arange(h)[:, None].astype(np.float32)
    x = np.arange(w)[None, :].astype(np.float32)
    d = np.sqrt((x-px)**2 + (y-py)**2)
    mask = np.clip(1 - d/r, 0, 1)[:, :, None] ** 1.8
    c = np.array(col, dtype=np.float32)
    return arr + mask * c * intensity


def particles(arr, seed, n, col, t_anim, size=2.5, intensity=0.7):
    rs = np.random.RandomState(seed)
    h, w = arr.shape[:2]
    px = rs.uniform(0, w, n)
    py = rs.uniform(0, h, n)
    speeds = rs.uniform(18, 55, n)
    py = (py - t_anim * speeds) % h
    alphas = rs.uniform(0.15, 0.55, n)
    sizes  = rs.uniform(1.2, size, n)

    out = arr.copy()
    c = np.array(col, dtype=np.float32)
    for i in range(n):
        ix, iy = int(px[i]), int(py[i])
        r = int(sizes[i] * 4) + 1
        x0, x1 = max(0, ix-r), min(w, ix+r)
        y0, y1 = max(0, iy-r), min(h, iy+r)
        yy, xx = np.ogrid[y0:y1, x0:x1]
        d = np.sqrt((xx-px[i])**2 + (yy-py[i])**2)
        mask = np.clip(1 - d/sizes[i], 0, 1)[:, :, None] ** 1.5
        out[y0:y1, x0:x1] += mask * c * alphas[i] * intensity * 255
    return out


def diagonal_lines(arr, spacing=90, opacity=0.055):
    out = arr.copy()
    h, w = arr.shape[:2]
    y = np.arange(h)[:, None]
    x = np.arange(w)[None, :]
    mask = ((x + y) % spacing < 1).astype(np.float32)[:, :, None]
    return out + mask * 255 * opacity


def horizontal_lines(arr, spacing=6, opacity=0.04):
    out = arr.copy()
    mask = (np.arange(H) % spacing == 0).astype(np.float32)[:, None, None]
    return out + mask * 255 * opacity


def noise_layer(arr, scale=8, intensity=0.08, seed=0):
    rs = np.random.RandomState(seed)
    small = rs.random((H//scale, W//scale)).astype(np.float32)
    noise_img = Image.fromarray((small * 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
    noise = np.array(noise_img)[:, :, None].astype(np.float32) / 255
    return arr + noise * 255 * intensity


def chromatic(arr, shift=3):
    """Subtle RGB channel separation."""
    out = arr.copy()
    out[:, shift:,  0] = arr[:, :-shift, 0]   # R shifts right
    out[:, :-shift, 2] = arr[:, shift:,  2]   # B shifts left
    return out


def film_grain(arr, intensity=0.028):
    noise = rng.normal(0, intensity*255, arr.shape)
    return np.clip(arr + noise, 0, 255)


def vignette(arr, strength=0.65):
    y = np.linspace(-1, 1, H)[:, None]
    x = np.linspace(-1, 1, W)[None, :]
    d = np.sqrt(x**2 + (y*1.5)**2)
    v = np.clip(d**2.4 * strength, 0, 1)[:, :, None]
    return arr * (1 - v)


def letterbox(img: Image.Image) -> Image.Image:
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0,0),(W,BAR_H)],     fill=(0,0,0))
    draw.rectangle([(0,H-BAR_H),(W,H)],   fill=(0,0,0))
    return img


# ── per-scene background builders ────────────────────────────────────────────

def bg_scene1(t):
    """Dark navy, amber light leak, golden dust particles drifting up."""
    arr = radial((6, 10, 24), (2, 2, 6), power=1.8)
    arr = glow(arr, 0.12, 0.18, 0.42, (160, 65, 8), 0.28 + t*0.08)
    arr = glow(arr, 0.85, 0.75, 0.38, (8, 20, 60), 0.22)
    arr = glow(arr, 0.5,  0.9,  0.55, (15, 8,  35), 0.30)
    arr = particles(arr, seed=1, n=55, col=(210, 145, 50), t_anim=t*60, size=2.8, intensity=0.55)
    arr = particles(arr, seed=7, n=25, col=(255, 200, 100), t_anim=t*35, size=1.6, intensity=0.35)
    arr = noise_layer(arr, scale=6, intensity=0.06, seed=1)
    arr = horizontal_lines(arr, spacing=5, opacity=0.025)
    return arr


def bg_scene2(t):
    """Deep blood-red radial, dark geometry, menacing."""
    arr = radial((18, 3, 3), (55, 6, 6), power=2.2)
    arr = glow(arr, 0.5,  0.5,  0.7,  (90, 8, 8),   0.55 + t*0.12)
    arr = glow(arr, 0.15, 0.3,  0.35, (140, 15, 15), 0.30)
    arr = glow(arr, 0.82, 0.65, 0.32, (60, 5, 5),    0.22)
    arr = diagonal_lines(arr, spacing=100, opacity=0.04)
    arr = noise_layer(arr, scale=5, intensity=0.07, seed=2)
    arr = particles(arr, seed=3, n=20, col=(220, 30, 30), t_anim=t*25, size=2.0, intensity=0.3)
    return arr


def bg_scene3(t):
    """Cinematic backlit — silver-white central bloom, silhouette feel."""
    arr = radial((22, 20, 20), (2, 2, 2), power=3.5)
    bloom_intensity = 0.38 + math.sin(t * math.pi * 0.4) * 0.06
    arr = glow(arr, 0.5,  0.5,  0.55, (255, 250, 240), bloom_intensity)
    arr = glow(arr, 0.5,  0.42, 0.28, (255, 255, 255), 0.18 + t*0.05)
    arr = glow(arr, 0.5,  0.7,  0.40, (180, 100, 40),  0.12)
    # Subtle lens flare streaks
    arr = glow(arr, 0.18, 0.48, 0.12, (255, 240, 200), 0.18)
    arr = glow(arr, 0.78, 0.52, 0.10, (200, 220, 255), 0.14)
    arr = noise_layer(arr, scale=4, intensity=0.05, seed=3)
    arr = horizontal_lines(arr, spacing=4, opacity=0.03)
    return arr


def bg_scene4(t):
    """Red interrogation light flooding from right, dark charcoal left."""
    base = linear((8, 6, 6), (4, 4, 12))
    arr  = np.array(base)
    arr  = glow(arr, 1.05, 0.5,  0.65, (190, 20, 10),  0.70 + t*0.10)
    arr  = glow(arr, 0.05, 0.5,  0.40, (10,  15, 40),  0.25)
    arr  = glow(arr, 0.5,  0.05, 0.45, (20,  10, 8),   0.18)
    arr  = glow(arr, 0.5,  0.98, 0.45, (8,   8,  18),  0.18)
    arr  = diagonal_lines(arr, spacing=80, opacity=0.035)
    arr  = particles(arr, seed=9, n=18, col=(255, 80, 40), t_anim=t*40, size=1.8, intensity=0.28)
    arr  = noise_layer(arr, scale=5, intensity=0.07, seed=4)
    return arr


def bg_scene5(t):
    """Explosive red radial burst — alarm, warning, danger."""
    pulse = 0.5 + math.sin(t * math.pi * 3.0) * 0.18
    arr = radial((220, 12, 12), (8, 2, 2), power=0.9)
    arr = glow(arr, 0.5, 0.5, 0.9, (255, 40, 20), 0.9 * pulse)
    arr = glow(arr, 0.5, 0.5, 0.4, (255, 180, 60), 0.5 * pulse)
    arr = glow(arr, 0.5, 0.5, 0.2, (255, 255, 200), 0.25 * pulse)
    arr = particles(arr, seed=5, n=35, col=(255, 150, 50), t_anim=t*80, size=2.2, intensity=0.45)
    arr = diagonal_lines(arr, spacing=70, opacity=0.06)
    arr = noise_layer(arr, scale=4, intensity=0.09, seed=5)
    return arr


def bg_scene6(t):
    """Brand fade — deep black with crimson glow blooming in."""
    arr = radial((6, 4, 4), (1, 1, 1), power=2.5)
    arr = glow(arr, 0.5, 0.5, 0.5, (150, 15, 15), 0.30 * t)
    arr = noise_layer(arr, scale=6, intensity=0.04, seed=6)
    return arr


BG_FNS = [bg_scene1, bg_scene2, bg_scene3, bg_scene4, bg_scene5, bg_scene6]


def build_bg(scene_idx, t):
    arr = BG_FNS[scene_idx](t)
    arr = vignette(arr, strength=0.60)
    arr = film_grain(arr, intensity=0.030)
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, "RGB").convert("RGBA")


# ── text rendering ────────────────────────────────────────────────────────────

def cx(draw, text, fn, y, col, alpha, tracking=0):
    if alpha <= 0: return
    a = int(clamp(alpha)*255)
    if tracking == 0:
        w = draw.textlength(text, font=fn)
        draw.text(((W-w)/2, y), text, font=fn, fill=(*col, a))
    else:
        chars = list(text)
        total = sum(draw.textlength(c, font=fn) for c in chars) + tracking*(len(chars)-1)
        x = (W - total) / 2
        for c in chars:
            draw.text((x, y), c, font=fn, fill=(*col, a))
            x += draw.textlength(c, font=fn) + tracking


def hline(draw, y, w, col, alpha):
    if alpha <= 0: return
    x0 = (W-w)//2
    draw.rectangle([(x0, y),(x0+w, y+1)], fill=(*col, int(clamp(alpha)*255)))


WHITE  = (240, 240, 240)
ACCENT = (196,  30,  58)
DIM    = (150, 140, 135)
SILVER = (200, 200, 210)


def text_scene1(lf, draw):
    fi = eo(it(lf, 25, 65));  fo = ei(it(lf, 130, 168));  a = fi*(1-fo)
    fn = font(F_SERIF, 68)
    yo = (1-fi)*16
    cx(draw, "For 15 years,",                  fn, ACY - 56 + yo, WHITE,  a)
    cx(draw, "he operated in plain sight.",    fn, ACY + 20 + yo, WHITE,  a)


def text_scene2(lf, draw):
    tl = eo(it(lf, 12, 46));  tt = eo(it(lf, 38, 76));  fo = ei(it(lf, 130, 168))
    a_l = tl*(1-fo);  a_t = tt*(1-fo)
    lw = int(tl * 460)
    hline(draw, ACY - 64, lw, ACCENT, a_l)
    fn = font(F_SERIF, 64)
    yo = (1-tt)*14
    cx(draw, "With the full knowledge",        fn, ACY - 30 + yo, WHITE,  a_t)
    cx(draw, "of those in power.",             fn, ACY + 48 + yo, WHITE,  a_t)


def text_scene3(lf, draw):
    tn = eo(it(lf, 10, 52));  fo = ei(it(lf, 108, 148))
    a_n = tn*(1-fo)
    yo  = (1-tn)*22
    fn  = font(F_SERIF, 148)
    cx(draw, "JEFFREY EPSTEIN", fn, ACY - 94 + yo, WHITE, a_n, tracking=5)
    tr = eo(it(lf, 40, 70));   a_r = tr*(1-fo)
    hline(draw, ACY + 68, int(tr*680), SILVER, a_r*0.4)
    ts = eo(it(lf, 55, 88));   a_s = ts*(1-fo)
    cx(draw, "FINANCIER   ·   1953 – 2019", font(F_SANS, 30), ACY + 88, DIM, a_s, tracking=3)


def text_scene4(lf, draw):
    fo = ei(it(lf, 92, 118))
    words = [("Trafficker.",  0,  WHITE), ("Untouchable.", 20, WHITE), ("Protected.", 40, ACCENT)]
    total_h = len(words) * 108
    y = ACY - total_h//2 + 10
    for word, start, col in words:
        t  = eo(it(lf, start, start+28))
        a  = t*(1-fo)
        yo = (1-t)*18
        cx(draw, word, font(F_SERIF, 82), y+yo, col, a)
        y += 108


def text_scene5(lf, draw):
    ti = eo(it(lf, 6, 36));  fo = ei(it(lf, 68, 88))
    a  = ti*(1-fo)
    yo = (1-ti)*26
    cx(draw, "UNTIL NOW.", font(F_SERIF, 172), ACY - 106 + yo, WHITE, a)


def text_scene6(lf, draw):
    ti = eo(it(lf, 0, 18));  fo = ei(it(lf, 18, 30));  a = ti*(1-fo)
    cx(draw, "FINALLY SOLVED",  font(F_BOLD, 30),  ACY - 26, ACCENT, a, tracking=4)
    cx(draw, "THE SYSTEM KNEW", font(F_BOLD, 22),  ACY + 28, DIM,    a*0.7, tracking=2)


TEXT_FNS = [text_scene1, text_scene2, text_scene3, text_scene4, text_scene5, text_scene6]


# ── schedule & render ─────────────────────────────────────────────────────────

SCHEDULE = [
    (0,   180),
    (180, 180),
    (360, 150),
    (510, 120),
    (630,  90),
    (720,  30),
]
FADE = 22


def render_frame(frame: int) -> Image.Image:
    for idx, (start, dur) in enumerate(SCHEDULE):
        if start <= frame < start + dur:
            lf_val = frame - start
            t_norm = lf_val / dur

            bg   = build_bg(idx, t_norm)
            draw = ImageDraw.Draw(bg)
            TEXT_FNS[idx](lf_val, draw)

            # Chromatic aberration — subtle on most scenes, strong on scene 5
            shift = 4 if idx == 4 else 2
            arr = np.array(bg.convert("RGB"), dtype=np.float32)
            arr_ca = arr.copy()
            arr_ca[:, shift:,  0] = arr[:, :-shift, 0]
            arr_ca[:, :-shift, 2] = arr[:, shift:,  2]
            bg = Image.fromarray(np.clip(arr_ca, 0, 255).astype(np.uint8)).convert("RGBA")
            draw = ImageDraw.Draw(bg)

            # Crossfade
            fi    = 1 - eo(clamp(lf_val / FADE))
            fo    = eo(clamp((lf_val - (dur - FADE)) / FADE))
            alpha = max(fi, fo)
            if alpha > 0:
                ov = Image.new("RGBA", bg.size, (0, 0, 0, int(alpha*255)))
                bg = Image.alpha_composite(bg, ov)

            letterbox(bg)
            return bg.convert("RGB")

    return Image.new("RGB", (W, H), (0, 0, 0))


def main():
    print(f"Rendering {TOTAL} frames (25s) cinematic v2 at {W}×{H}…")
    cmd = [
        FFMPEG, "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{W}x{H}", "-pix_fmt", "rgb24",
        "-r", str(FPS), "-i", "pipe:0",
        "-vcodec", "libx264", "-pix_fmt", "yuv420p",
        "-crf", "22", OUTPUT,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    for fr in range(TOTAL):
        proc.stdin.write(render_frame(fr).tobytes())
        if fr % 150 == 0:
            print(f"  {fr // FPS}s / 25s")
    proc.stdin.close()
    proc.wait()
    print(f"\nDone → {OUTPUT}")


if __name__ == "__main__":
    main()
