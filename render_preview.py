"""Render a 6-second EpisodeIntro preview video using Pillow + FFmpeg."""
import math
import subprocess
import struct
import zlib
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FFMPEG = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
OUTPUT = "/home/user/supercode/output/preview_episode_intro.mp4"
W, H = 1920, 1080
FPS = 30
FRAMES = 180  # 6 seconds

BG = (8, 8, 16)
ACCENT = (196, 30, 58)
TEXT = (240, 240, 240)
SUBTEXT = (136, 136, 153)
DIVIDER = (51, 51, 85)

FONT_SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FONT_SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
FONT_SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

Path(OUTPUT).parent.mkdir(parents=True, exist_ok=True)


def ease_out(t: float) -> float:
    return 1 - (1 - t) ** 3


def spring(t: float, damping: float = 14.0) -> float:
    if t <= 0:
        return 0.0
    if t >= 1:
        return 1.0
    return 1 - math.exp(-damping * t) * math.cos(math.pi * t * 2)


def lerp(a, b, t):
    return a + (b - a) * max(0.0, min(1.0, t))


def interp(frame, f0, f1, v0=0.0, v1=1.0):
    if f1 == f0:
        return v1
    t = (frame - f0) / (f1 - f0)
    t = max(0.0, min(1.0, t))
    return v0 + (v1 - v0) * t


def alpha_composite_rect(img, xy, size, color_rgb, opacity):
    if opacity <= 0:
        return
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    a = int(opacity * 255)
    d.rectangle([xy, (xy[0] + size[0], xy[1] + size[1])], fill=(*color_rgb, a))
    img.paste(Image.alpha_composite(img, overlay))


def render_frame(frame: int) -> Image.Image:
    img = Image.new("RGBA", (W, H), (*BG, 255))
    draw = ImageDraw.Draw(img)

    channel_name = "FINALLY SOLVED"
    episode_title = "Jeffrey Epstein"
    subtitle = "The system knew. It looked away."

    # ── Accent bars ─────────────────────────────────────────────────────────
    draw.rectangle([(0, 0), (W, 4)], fill=(*ACCENT, 255))
    draw.rectangle([(0, H - 4), (W, H)], fill=(*ACCENT, 255))

    # ── Phase 1: Channel name (0→30) ────────────────────────────────────────
    ch_opacity = ease_out(interp(frame, 0, 28))
    if ch_opacity > 0:
        font_ch = ImageFont.truetype(FONT_SANS_BOLD, 28)
        text_w = draw.textlength(channel_name, font=font_ch)
        x = (W - text_w) / 2
        y = H // 2 - 160
        r, g, b = ACCENT
        draw.text((x, y), channel_name, font=font_ch,
                  fill=(r, g, b, int(ch_opacity * 255)))

    # ── Phase 2: Divider line (30→70) ───────────────────────────────────────
    line_pct = ease_out(interp(frame, 30, 70))
    if line_pct > 0:
        line_max = 600
        line_w = int(line_pct * line_max)
        lx = (W - line_max) // 2
        ly = H // 2 - 108
        draw.rectangle([(lx, ly), (lx + line_w, ly + 1)], fill=(*DIVIDER, 255))

    # ── Phase 3: Episode title (60→110) ─────────────────────────────────────
    title_t = interp(frame, 60, 100)
    title_sp = spring(title_t, damping=12)
    title_opacity = ease_out(interp(frame, 60, 90))
    if title_opacity > 0:
        font_title = ImageFont.truetype(FONT_SERIF_BOLD, 96)
        text_w = draw.textlength(episode_title, font=font_title)
        x = (W - text_w) / 2
        y_base = H // 2 - 60
        y_offset = lerp(30, 0, title_sp)
        r, g, b = TEXT
        draw.text((x, y_base + y_offset), episode_title, font=font_title,
                  fill=(r, g, b, int(title_opacity * 255)))

    # ── Phase 4: Subtitle (100→130) ─────────────────────────────────────────
    sub_opacity = ease_out(interp(frame, 100, 130))
    if sub_opacity > 0:
        font_sub = ImageFont.truetype(FONT_SANS, 34)
        text_w = draw.textlength(subtitle, font=font_sub)
        x = (W - text_w) / 2
        y = H // 2 + 62
        r, g, b = SUBTEXT
        draw.text((x, y), subtitle, font=font_sub,
                  fill=(r, g, b, int(sub_opacity * 255)))

    # ── Fade out (160→180) ──────────────────────────────────────────────────
    fade_out = interp(frame, 160, 180)
    if fade_out > 0:
        overlay = Image.new("RGBA", (W, H), (*BG, int(fade_out * 255)))
        img = Image.alpha_composite(img, overlay)

    return img.convert("RGB")


def main():
    cmd = [
        FFMPEG, "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{W}x{H}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "pipe:0",
        "-vcodec", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "18",
        OUTPUT,
    ]

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    for f in range(FRAMES):
        frame_img = render_frame(f)
        proc.stdin.write(frame_img.tobytes())
        if f % 30 == 0:
            print(f"  frame {f}/{FRAMES}")

    proc.stdin.close()
    proc.wait()
    print(f"\nDone: {OUTPUT}")


if __name__ == "__main__":
    main()
