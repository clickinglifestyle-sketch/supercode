"""25-second cinematic cold open — Jeffrey Epstein / Finally Solved.
2.39:1 letterbox · film grain · vignette · slow dramatic reveals."""
import math, subprocess
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FFMPEG = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
OUTPUT = "/home/user/supercode/output/epstein_cinematic_25s.mp4"
W, H   = 1920, 1080
FPS    = 30
TOTAL  = 750   # 25 s

F_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
F_SANS  = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
F_BOLD  = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# 2.39:1 letterbox
BAR_H = 136
AY    = BAR_H              # active top
AH    = H - BAR_H * 2     # active height ≈ 808 px
ACY   = AY + AH // 2      # active center y

BLACK  = (0,   0,   0)
WHITE  = (240, 240, 240)
ACCENT = (196,  30,  58)
DIM    = (120, 120, 130)

Path(OUTPUT).parent.mkdir(parents=True, exist_ok=True)

rng = np.random.default_rng()


# ── post-processing ───────────────────────────────────────────────────────────

def make_vignette():
    y = np.linspace(-1, 1, H)[:, None]
    x = np.linspace(-1, 1, W)[None, :]
    d = np.sqrt(x**2 + (y * 1.6)**2)   # wider than tall
    v = np.clip(d ** 2.2 * 0.72, 0, 1).astype(np.float32)
    return v  # 0 = no darkening, 1 = full black

VIGNETTE = make_vignette()


def post(img: Image.Image, grain: float = 0.035) -> Image.Image:
    arr = np.array(img, dtype=np.float32)

    # Vignette
    vig = VIGNETTE[:, :, None]
    arr = arr * (1 - vig)

    # Film grain
    noise = rng.normal(0, grain * 255, arr.shape)
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)

    result = Image.fromarray(arr)

    # Letterbox bars
    draw = ImageDraw.Draw(result)
    draw.rectangle([(0, 0), (W, BAR_H)],          fill=BLACK)
    draw.rectangle([(0, H - BAR_H), (W, H)],      fill=BLACK)

    return result


# ── helpers ───────────────────────────────────────────────────────────────────

def lf(path, sz): return ImageFont.truetype(path, sz)
def clamp(v): return max(0.0, min(1.0, v))
def it(fr, f0, f1, v0=0.0, v1=1.0):
    return v0 + (v1 - v0) * clamp((fr - f0) / max(f1 - f0, 1))
def eo(t): t = clamp(t); return 1 - (1 - t) ** 3
def ei(t): t = clamp(t); return t ** 2


def cx_text(draw, text, font, y, color, alpha, tracking=0):
    """Draw centered text with alpha."""
    if alpha <= 0:
        return
    a = int(clamp(alpha) * 255)
    if tracking == 0:
        w = draw.textlength(text, font=font)
        draw.text(((W - w) / 2, y), text, font=font, fill=(*color, a))
    else:
        # Spaced out tracking
        chars = list(text)
        total_w = sum(draw.textlength(c, font=font) for c in chars) + tracking * (len(chars) - 1)
        x = (W - total_w) / 2
        for c in chars:
            draw.text((x, y), c, font=font, fill=(*color, a))
            x += draw.textlength(c, font=font) + tracking


def draw_line(draw, y, width, color, alpha):
    if alpha <= 0:
        return
    a = int(clamp(alpha) * 255)
    x0 = (W - width) // 2
    draw.rectangle([(x0, y), (x0 + width, y + 1)], fill=(*color, a))


# ── beat renderers ────────────────────────────────────────────────────────────
# Each receives local frame (lf) and an RGBA Image; returns modified image.

def beat1(lf, img):
    """0-180 (6 s): 'For 15 years, he operated in plain sight.'"""
    draw = ImageDraw.Draw(img)
    font = lf_font(F_SERIF, 68)

    fi = eo(it(lf, 25, 65))
    fo = ei(it(lf, 130, 168))
    a  = fi * (1 - fo)

    line1 = "For 15 years,"
    line2 = "he operated in plain sight."

    yo = (1 - fi) * 16
    cx_text(draw, line1, font, ACY - 58 + yo, WHITE, a)
    cx_text(draw, line2, font, ACY + 18 + yo, WHITE, a)
    return img


def beat2(lf, img):
    """180-360 (6 s): red line + 'With the full knowledge of those in power.'"""
    draw = ImageDraw.Draw(img)

    t_line = eo(it(lf, 15, 50))
    t_text = eo(it(lf, 40, 80))
    fo     = ei(it(lf, 130, 168))
    a_text = t_text * (1 - fo)
    a_line = t_line * (1 - fo)

    line_w = int(t_line * 480)
    draw_line(draw, ACY - 62, line_w, ACCENT, a_line)

    font = lf_font(F_SERIF, 64)
    yo   = (1 - t_text) * 14
    cx_text(draw, "With the full knowledge", font, ACY - 30 + yo, WHITE, a_text)
    cx_text(draw, "of those in power.",      font, ACY + 48 + yo, WHITE, a_text)
    return img


def beat3(lf, img):
    """360-510 (5 s): 'JEFFREY EPSTEIN' — cinematic title."""
    draw = ImageDraw.Draw(img)

    t_name = eo(it(lf, 10, 55))
    fo     = ei(it(lf, 110, 148))

    font_big = lf_font(F_SERIF, 148)
    font_sub = lf_font(F_SANS,   32)

    a_name = t_name * (1 - fo)

    yo = (1 - t_name) * 20
    cx_text(draw, "JEFFREY EPSTEIN", font_big, ACY - 96 + yo, WHITE, a_name, tracking=6)

    # Fine rule under name
    t_rule = eo(it(lf, 42, 72))
    a_rule = t_rule * (1 - fo)
    rule_w = int(t_rule * 680)
    draw_line(draw, ACY + 72, rule_w, DIM, a_rule * 0.5)

    # Subtitle
    t_sub = eo(it(lf, 58, 90))
    a_sub = t_sub * (1 - fo)
    cx_text(draw, "FINANCIER   ·   1953 – 2019", font_sub, ACY + 92, DIM, a_sub, tracking=3)

    return img


def beat4(lf, img):
    """510-630 (4 s): 'Trafficker. Untouchable. Protected.'"""
    draw = ImageDraw.Draw(img)

    font = lf_font(F_SERIF, 82)
    words = [
        ("Trafficker.",  0,  WHITE),
        ("Untouchable.", 22, WHITE),
        ("Protected.",   44, ACCENT),
    ]
    fo = ei(it(lf, 90, 118))

    total_h = len(words) * 106
    y = ACY - total_h // 2 + 10

    for word, start, color in words:
        t  = eo(it(lf, start, start + 30))
        a  = t * (1 - fo)
        yo = (1 - t) * 18
        cx_text(draw, word, font, y + yo, color, a)
        y += 106

    return img


def beat5(lf, img):
    """630-720 (3 s): 'UNTIL NOW.' — red, huge."""
    draw = ImageDraw.Draw(img)

    t_in = eo(it(lf,  8, 38))
    fo   = ei(it(lf, 70, 90))
    a    = t_in * (1 - fo)

    font = lf_font(F_SERIF, 172)
    yo   = (1 - t_in) * 24
    cx_text(draw, "UNTIL NOW.", font, ACY - 104 + yo, ACCENT, a)

    return img


def beat6(lf, img):
    """720-750 (1 s): 'FINALLY SOLVED' brand + fade to black."""
    draw = ImageDraw.Draw(img)

    t_in = eo(it(lf, 0, 18))
    fo   = ei(it(lf, 18, 30))
    a    = t_in * (1 - fo)

    font_ch  = lf_font(F_BOLD, 30)
    font_tag = lf_font(F_BOLD, 22)

    cx_text(draw, "FINALLY SOLVED", font_ch, ACY - 28, ACCENT, a, tracking=4)
    cx_text(draw, "THE SYSTEM KNEW", font_tag, ACY + 28, DIM, a * 0.7, tracking=2)

    return img


# Font cache to avoid re-loading every frame
_font_cache: dict = {}
def lf_font(path, sz):
    key = (path, sz)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, sz)
    return _font_cache[key]


# ── schedule ──────────────────────────────────────────────────────────────────

SCHEDULE = [
    (0,   180, beat1),
    (180, 180, beat2),
    (360, 150, beat3),
    (510, 120, beat4),
    (630,  90, beat5),
    (720,  30, beat6),
]
FADE = 22


def render_frame(frame: int) -> Image.Image:
    img  = Image.new("RGBA", (W, H), (*BLACK, 255))

    for start, dur, fn in SCHEDULE:
        if start <= frame < start + dur:
            lf_val = frame - start

            img = fn(lf_val, img)

            # Scene crossfade
            fi    = 1 - eo(clamp(lf_val / FADE))
            fo    = eo(clamp((lf_val - (dur - FADE)) / FADE))
            alpha = max(fi, fo)
            if alpha > 0:
                ov = Image.new("RGBA", img.size, (*BLACK, int(alpha * 255)))
                img = Image.alpha_composite(img, ov)
            break

    img = post(img.convert("RGB"))
    return img


def main():
    print(f"Rendering {TOTAL} frames (25s) cinematic at {W}×{H}…")
    cmd = [
        FFMPEG, "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{W}x{H}", "-pix_fmt", "rgb24",
        "-r", str(FPS), "-i", "pipe:0",
        "-vcodec", "libx264", "-pix_fmt", "yuv420p",
        "-crf", "26", OUTPUT,
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
