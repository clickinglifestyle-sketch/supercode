"""Render a 30-second Jeffrey Epstein short-form video."""
import math
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FFMPEG = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
OUTPUT = "/home/user/supercode/output/epstein_30s.mp4"
W, H = 1080, 1920  # 9:16 vertical for Shorts
FPS = 30
TOTAL = 900  # 30 seconds

FONT_SERIF      = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FONT_SANS       = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
FONT_SANS_BOLD  = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

BG      = (8, 8, 16)
ACCENT  = (196, 30, 58)
TEXT    = (240, 240, 240)
SUBTEXT = (136, 136, 153)
DIM     = (40, 40, 70)

Path(OUTPUT).parent.mkdir(parents=True, exist_ok=True)


def lf(path, size):
    return ImageFont.truetype(path, size)


def clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, v))


def interp(frame, f0, f1, v0=0.0, v1=1.0):
    t = clamp((frame - f0) / max(f1 - f0, 1))
    return v0 + (v1 - v0) * t


def ease_out(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_in_out(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def spring(t, damping=12):
    t = clamp(t)
    if t == 0:
        return 0.0
    return 1 - math.exp(-damping * t) * math.cos(math.pi * t * 2.5)


def alpha_blit(base, color_rgb, alpha, x, y, w, h):
    if alpha <= 0:
        return
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(overlay).rectangle([(x, y), (x + w, y + h)], fill=(*color_rgb, int(alpha * 255)))
    return Image.alpha_composite(base, overlay)


def centered_text(draw, text, font, cy, color, img_w=W):
    w = draw.textlength(text, font=font)
    draw.text(((img_w - w) / 2, cy), text, font=font, fill=color)


def channel_bug(draw, opacity):
    """Top-left channel name bug."""
    font = lf(FONT_SANS_BOLD, 28)
    a = int(clamp(opacity) * 255)
    draw.text((44, 60), "FINALLY SOLVED", font=font, fill=(*ACCENT, a))
    draw.rectangle([(34, 56), (38, 96)], fill=(*ACCENT, a))


# ── Scene renderers ───────────────────────────────────────────────────────────

def scene_hook(f, img, draw):
    """0-150: 'He was the most protected predator...' word by word."""
    lines = [
        "He was the most",
        "protected predator",
        "in American history.",
    ]
    font = lf(FONT_SERIF, 88)
    total_h = len(lines) * 110
    start_y = H // 2 - total_h // 2 - 40

    for i, line in enumerate(lines):
        t = ease_out(interp(f, i * 18, i * 18 + 35))
        a = int(t * 255)
        ty = interp(f, i * 18, i * 18 + 35, start_y + i * 110 + 28, start_y + i * 110)
        lw = draw.textlength(line, font=font)
        draw.text(((W - lw) / 2, ty), line, font=font, fill=(*TEXT, a))

    channel_bug(draw, ease_out(interp(f, 0, 20)))

    # Bottom accent bar
    draw.rectangle([(0, H - 6), (W, H)], fill=(*ACCENT, 255))


def scene_intro(f, img, draw):
    """150-300: Jeffrey Epstein data graphic."""
    t_bg   = ease_out(interp(f, 0, 20))
    t_ch   = ease_out(interp(f, 8, 30))
    t_name = spring(interp(f, 20, 60), damping=10)
    t_sub  = ease_out(interp(f, 50, 75))
    t_tag  = ease_out(interp(f, 65, 85))

    draw.rectangle([(0, 0), (W, 6)], fill=(*ACCENT, 255))
    draw.rectangle([(0, H - 6), (W, H)], fill=(*ACCENT, 255))

    # Channel name
    font_ch = lf(FONT_SANS_BOLD, 26)
    a_ch = int(t_ch * 255)
    draw.text((44, 80), "FINALLY SOLVED", font=font_ch, fill=(*ACCENT, a_ch))

    # Divider line grows
    line_w = int(t_ch * (W - 88))
    draw.rectangle([(44, 122), (44 + line_w, 124)], fill=(*DIM, 255))

    # Name
    font_name = lf(FONT_SERIF, 110)
    name = "Jeffrey"
    nw = draw.textlength(name, font=font_name)
    y_off = int((1 - t_name) * 40)
    a_name = int(t_name * 255)
    draw.text(((W - nw) / 2, H // 2 - 200 + y_off), name, font=font_name, fill=(*TEXT, a_name))

    font_name2 = lf(FONT_SERIF, 110)
    name2 = "Epstein"
    nw2 = draw.textlength(name2, font=font_name2)
    t_name2 = spring(interp(f, 28, 68), damping=10)
    y_off2 = int((1 - t_name2) * 40)
    draw.text(((W - nw2) / 2, H // 2 - 70 + y_off2), name2, font=font_name2,
              fill=(*TEXT, int(t_name2 * 255)))

    # Sub
    font_sub = lf(FONT_SANS, 36)
    sub = "1953  ·  Financier  ·  New York"
    sw = draw.textlength(sub, font=font_sub)
    draw.text(((W - sw) / 2, H // 2 + 90), sub, font=font_sub,
              fill=(*SUBTEXT, int(t_sub * 255)))

    # Tag
    font_tag = lf(FONT_SANS_BOLD, 24)
    tag = "THE SYSTEM KNEW"
    tw2 = draw.textlength(tag, font=font_tag)
    pad = 18
    tx = (W - tw2 - pad * 2) / 2
    a_tag = int(t_tag * 255)
    draw.rectangle([(tx - 2, H // 2 + 160), (tx + tw2 + pad * 2 + 2, H // 2 + 200)],
                   fill=(*ACCENT, int(t_tag * 50)))
    draw.rectangle([(tx - 2, H // 2 + 160), (tx + tw2 + pad * 2 + 2, H // 2 + 200)],
                   outline=(*ACCENT, int(t_tag * 100)), width=1)
    draw.text((tx + pad, H // 2 + 165), tag, font=font_tag, fill=(*ACCENT, a_tag))


def scene_deal(f, img, draw):
    """300-450: The sweetheart deal — impact card."""
    t_bg    = ease_out(interp(f, 0, 15))
    t_label = ease_out(interp(f, 10, 30))
    t_big   = spring(interp(f, 20, 55), damping=9)
    t_sub   = ease_out(interp(f, 50, 75))
    t_desc  = ease_out(interp(f, 70, 95))

    # Red-tinted background
    overlay = Image.new("RGBA", img.size, (30, 4, 8, int(t_bg * 200)))
    img.paste(Image.alpha_composite(img, overlay))
    draw = ImageDraw.Draw(img)

    draw.rectangle([(0, 0), (W, 6)], fill=(*ACCENT, 255))
    draw.rectangle([(0, H - 6), (W, H)], fill=(*ACCENT, 255))

    channel_bug(draw, t_label)

    font_label = lf(FONT_SANS_BOLD, 32)
    label = "THE DEAL"
    lw = draw.textlength(label, font=font_label)
    draw.text(((W - lw) / 2, H // 2 - 340), label, font=font_label,
              fill=(*SUBTEXT, int(t_label * 255)))

    # Big number
    font_big = lf(FONT_SERIF, 260)
    big = "13"
    bw = draw.textlength(big, font=font_big)
    y_off = int((1 - t_big) * 60)
    draw.text(((W - bw) / 2, H // 2 - 240 + y_off), big, font=font_big,
              fill=(*ACCENT, int(t_big * 255)))

    font_sub = lf(FONT_SERIF, 72)
    sub = "MONTHS"
    sw = draw.textlength(sub, font=font_sub)
    draw.text(((W - sw) / 2, H // 2 + 80), sub, font=font_sub,
              fill=(*TEXT, int(t_sub * 255)))

    font_desc = lf(FONT_SANS, 34)
    lines = ["Work release 6 days/week.", "Victims were never notified."]
    y = H // 2 + 200
    for line in lines:
        lw2 = draw.textlength(line, font=font_desc)
        draw.text(((W - lw2) / 2, y), line, font=font_desc,
                  fill=(*SUBTEXT, int(t_desc * 255)))
        y += 50


def scene_failure(f, img, draw):
    """450-600: Institutional failure — three staggered lines."""
    t_title = ease_out(interp(f, 0, 25))
    lines_data = [
        ("The FBI knew.", 20, ACCENT),
        ("The DOJ signed off.", 38, TEXT),
        ("Acosta buried it.", 56, TEXT),
    ]

    draw.rectangle([(0, 0), (6, H)], fill=(*ACCENT, 255))
    draw.rectangle([(W - 6, 0), (W, H)], fill=(*ACCENT, 255))
    draw.rectangle([(0, 0), (W, 6)], fill=(*ACCENT, 255))
    draw.rectangle([(0, H - 6), (W, H)], fill=(*ACCENT, 255))

    channel_bug(draw, t_title)

    font_title = lf(FONT_SANS_BOLD, 32)
    title = "INSTITUTIONAL FAILURE"
    tw2 = draw.textlength(title, font=font_title)
    draw.text(((W - tw2) / 2, H // 2 - 360), title, font=font_title,
              fill=(*SUBTEXT, int(t_title * 255)))
    draw.rectangle([((W - 300) // 2, H // 2 - 305), ((W + 300) // 2, H // 2 - 304)],
                   fill=(*DIM, 255))

    font_line = lf(FONT_SERIF, 80)
    start_y = H // 2 - 260
    for i, (line, start_f, color) in enumerate(lines_data):
        t = spring(interp(f, start_f, start_f + 28), damping=11)
        lw2 = draw.textlength(line, font=font_line)
        x_off = int((1 - t) * -60)
        draw.text(((W - lw2) / 2 + x_off, start_y + i * 160), line, font=font_line,
                  fill=(*color, int(t * 255)))

    # Bottom footnote
    t_note = ease_out(interp(f, 85, 110))
    font_note = lf(FONT_SANS, 28)
    note = "— U.S. Attorney Alexander Acosta, 2008"
    nw = draw.textlength(note, font=font_note)
    draw.text(((W - nw) / 2, H // 2 + 260), note, font=font_note,
              fill=(*SUBTEXT, int(t_note * 255)))


def scene_death(f, img, draw):
    """600-780: Dead in his cell — alarm card."""
    t_flash = ease_out(interp(f, 0, 8))

    # Red flash on cut
    if f < 8:
        flash_overlay = Image.new("RGBA", img.size, (*ACCENT, int(t_flash * 180)))
        img.paste(Image.alpha_composite(img, flash_overlay))
        draw = ImageDraw.Draw(img)

    overlay2 = Image.new("RGBA", img.size, (28, 4, 4, 220))
    img.paste(Image.alpha_composite(img, overlay2))
    draw = ImageDraw.Draw(img)

    draw.rectangle([(0, 0), (W, 6)], fill=(*ACCENT, 255))
    draw.rectangle([(0, H - 6), (W, H)], fill=(*ACCENT, 255))

    t_date  = ease_out(interp(f, 10, 30))
    t_dead  = spring(interp(f, 15, 50), damping=9)
    t_cell  = spring(interp(f, 25, 60), damping=9)
    t_lines = ease_out(interp(f, 55, 85))

    font_date = lf(FONT_SANS_BOLD, 30)
    date_txt = "AUGUST 10, 2019  ·  6:30 AM"
    dw = draw.textlength(date_txt, font=font_date)
    draw.text(((W - dw) / 2, H // 2 - 420), date_txt, font=font_date,
              fill=(*SUBTEXT, int(t_date * 255)))

    font_big = lf(FONT_SERIF, 148)
    for i, (word, t_word) in enumerate([("DEAD", t_dead), ("IN HIS", spring(interp(f, 28, 63), 9)), ("CELL.", spring(interp(f, 38, 73), 9))]):
        ww = draw.textlength(word, font=font_big)
        y_off = int((1 - t_word) * 40)
        draw.text(((W - ww) / 2, H // 2 - 280 + i * 160 + y_off), word, font=font_big,
                  fill=(*TEXT, int(t_word * 255)))

    font_detail = lf(FONT_SANS, 32)
    details = ["Guards were asleep.", "Security cameras failed.", "Files remain sealed."]
    y = H // 2 + 210
    for detail in details:
        dw2 = draw.textlength(detail, font=font_detail)
        draw.text(((W - dw2) / 2, y), detail, font=font_detail,
                  fill=(*SUBTEXT, int(t_lines * 255)))
        y += 50

    channel_bug(draw, t_date)


def scene_question(f, img, draw):
    """780-900: The question + CTA."""
    t_in   = ease_out(interp(f, 0, 25))
    t_q1   = spring(interp(f, 15, 50), damping=11)
    t_q2   = spring(interp(f, 28, 63), damping=11)
    t_q3   = spring(interp(f, 40, 75), damping=11)
    t_cta  = ease_out(interp(f, 70, 95))
    t_out  = ease_in_out(interp(f, 95, 120))

    draw.rectangle([(0, 0), (W, 6)], fill=(*ACCENT, 255))
    draw.rectangle([(0, H - 6), (W, H)], fill=(*ACCENT, 255))

    channel_bug(draw, t_in)

    # Divider line
    lw = int(t_in * 500)
    draw.rectangle([((W - lw) // 2, H // 2 - 360), ((W + lw) // 2, H // 2 - 359)], fill=(*DIM, 255))

    font_q = lf(FONT_SERIF, 82)
    q_lines = [("Was it", t_q1), ("suicide?", t_q2), ("Or did the", spring(interp(f, 48, 80), 11))]
    y = H // 2 - 320
    for line, t in q_lines:
        lw2 = draw.textlength(line, font=font_q)
        y_off = int((1 - t) * 35)
        draw.text(((W - lw2) / 2, y + y_off), line, font=font_q, fill=(*TEXT, int(t * 255)))
        y += 110

    font_q2 = lf(FONT_SERIF, 72)
    last_lines = [("system protect", spring(interp(f, 58, 88), 11)), ("itself?", t_q3)]
    for line, t in last_lines:
        lw3 = draw.textlength(line, font=font_q2)
        y_off = int((1 - t) * 35)
        draw.text(((W - lw3) / 2, y + y_off), line, font=font_q2, fill=(*ACCENT, int(t * 255)))
        y += 100

    # CTA
    font_cta = lf(FONT_SANS_BOLD, 30)
    cta = "Follow for the full breakdown ↓"
    cw = draw.textlength(cta, font=font_cta)
    draw.text(((W - cw) / 2, H - 160), cta, font=font_cta,
              fill=(*TEXT, int(t_cta * 255)))

    # Fade to black at end
    if t_out > 0:
        fade = Image.new("RGBA", img.size, (*BG, int(t_out * 255)))
        img.paste(Image.alpha_composite(img, fade))


# Scene schedule: (start_frame, duration, render_fn)
SCHEDULE = [
    (0,   150, scene_hook),
    (150, 150, scene_intro),
    (300, 150, scene_deal),
    (450, 150, scene_failure),
    (600, 180, scene_death),
    (780, 120, scene_question),
]
FADE = 18


def render_frame(frame: int) -> Image.Image:
    img = Image.new("RGBA", (W, H), (*BG, 255))
    draw = ImageDraw.Draw(img)

    # Find current scene
    for start, dur, fn in SCHEDULE:
        if start <= frame < start + dur:
            local = frame - start
            fn(local, img, draw)

            # Crossfade overlay at scene boundaries
            fade_in_alpha  = 1 - ease_out(clamp(local / FADE))
            fade_out_alpha = ease_out(clamp((local - (dur - FADE)) / FADE))
            alpha = max(fade_in_alpha, fade_out_alpha)
            if alpha > 0:
                fade_img = Image.new("RGBA", img.size, (*BG, int(alpha * 255)))
                img = Image.alpha_composite(img, fade_img)
            break

    return img.convert("RGB")


def main():
    print(f"Rendering {TOTAL} frames (30s) at {W}×{H} (9:16 vertical)…")
    cmd = [
        FFMPEG, "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{W}x{H}", "-pix_fmt", "rgb24",
        "-r", str(FPS), "-i", "pipe:0",
        "-vcodec", "libx264", "-pix_fmt", "yuv420p",
        "-crf", "16", OUTPUT,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    for f in range(TOTAL):
        proc.stdin.write(render_frame(f).tobytes())
        if f % 150 == 0:
            print(f"  {f // FPS}s / 30s")
    proc.stdin.close()
    proc.wait()
    print(f"\nDone → {OUTPUT}")


if __name__ == "__main__":
    main()
