"""Render a 60-second storyboard animatic for a Jeffrey Epstein YouTube Short."""
import math
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FFMPEG = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
OUTPUT = "/home/user/supercode/output/storyboard_jeffrey_epstein.mp4"
W, H = 1920, 1080
FPS = 30

FONT_SANS       = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
FONT_SANS_BOLD  = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SERIF      = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

BG       = (8, 8, 16)
PANEL_BG = (14, 14, 28)
ACCENT   = (196, 30, 58)
TEXT     = (240, 240, 240)
SUBTEXT  = (136, 136, 153)
DIVIDER  = (40, 40, 70)
CARD_BG  = (20, 20, 40)

SCENES = [
    {
        "number": 1,
        "timecode": "0:00 – 0:08",
        "title": "COLD OPEN / HOOK",
        "shot_type": "Text Reveal",
        "vo": '"He was the most protected predator\nin American history."',
        "notes": "No music. Silence before\nthe hook drop. White text\non pure black.",
        "preview_type": "hook",
        "preview_text": "He was the most\nprotected predator\nin American history.",
    },
    {
        "number": 2,
        "timecode": "0:08 – 0:16",
        "title": "SUBJECT INTRO",
        "shot_type": "Data Graphic",
        "vo": '"Jeffrey Epstein. Financier.\nConnected to presidents, princes,\nand billionaires."',
        "notes": "DataGraphic composition.\nPass case props. Accent\ncolor: crimson.",
        "preview_type": "data",
        "preview_text": "Jeffrey Epstein\n1953 – 2019\nFinancier · The System Knew",
    },
    {
        "number": 3,
        "timecode": "0:16 – 0:24",
        "title": "THE FIRST ARREST",
        "shot_type": "Timeline Card",
        "vo": '"2005. Palm Beach Police.\nOver 30 underage victims\nalready identified."',
        "notes": "CaseTimeline composition.\nEvent type: arrest.\nRed dot marker.",
        "preview_type": "timeline",
        "preview_text": "2005\nArrested — Palm Beach\n30+ victims identified",
    },
    {
        "number": 4,
        "timecode": "0:24 – 0:32",
        "title": "THE SWEETHEART DEAL",
        "shot_type": "Impact Card",
        "vo": '"13 months. Work release\n6 days a week. Victims were\nnever notified."',
        "notes": "Full-screen impact text.\nLarge red '13 MONTHS'.\nHard cut in.",
        "preview_type": "impact",
        "preview_text": "13\nMONTHS",
    },
    {
        "number": 5,
        "timecode": "0:32 – 0:40",
        "title": "THE INSTITUTIONAL FAILURE",
        "shot_type": "Failure Graphic",
        "vo": '"The FBI knew.\nThe DOJ signed off.\nAlexander Acosta buried it."',
        "notes": "DataGraphic — failure_type:\nInstitutional Failure.\nStagger each name in.",
        "preview_type": "failure",
        "preview_text": "The FBI knew.\nThe DOJ signed off.\nAcosta buried it.",
    },
    {
        "number": 6,
        "timecode": "0:40 – 0:48",
        "title": "SECOND ARREST — 2019",
        "shot_type": "Timeline Card",
        "vo": '"2019. Arrested again.\nFederal charges. 45 counts.\nThis time, no deal."',
        "notes": "CaseTimeline — second event.\nBlue dot: discovery type.\nCut from previous red.",
        "preview_type": "timeline",
        "preview_text": "2019\nArrested — Federal charges\n45 counts. No deal.",
    },
    {
        "number": 7,
        "timecode": "0:48 – 0:56",
        "title": "THE DEATH",
        "shot_type": "Alarm Card",
        "vo": '"Six weeks later —\ndead in his cell. Guards asleep.\nCameras failed. Files sealed."',
        "notes": "Red flash frame on cut.\nLarge white text on red.\nHard silence on last line.",
        "preview_type": "alarm",
        "preview_text": "DEAD\nIN HIS CELL\nAug 10, 2019",
    },
    {
        "number": 8,
        "timecode": "0:56 – 1:00",
        "title": "QUESTION / CTA",
        "shot_type": "Closing Card",
        "vo": '"Was it suicide —\nor did the system protect\nitself one last time?"',
        "notes": "EpisodeIntro composition.\nFade to channel branding.\nSubscribe hook end card.",
        "preview_type": "cta",
        "preview_text": "FINALLY SOLVED\n\nWas it suicide —\nor did the system\nprotect itself?",
    },
]

SCENE_DURATION = {1: 240, 2: 240, 3: 240, 4: 240, 5: 240, 6: 240, 7: 240, 8: 120}
FADE_FRAMES = 18
TOTAL_FRAMES = sum(SCENE_DURATION.values())

Path(OUTPUT).parent.mkdir(parents=True, exist_ok=True)


def ease_out(t):
    return 1 - (1 - max(0.0, min(1.0, t))) ** 3


def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def wrap_text(text, font, draw, max_width):
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        current = []
        for word in words:
            test = " ".join(current + [word])
            if draw.textlength(test, font=font) <= max_width:
                current.append(word)
            else:
                if current:
                    lines.append(" ".join(current))
                current = [word]
        lines.append(" ".join(current) if current else "")
    return lines


def draw_preview_box(draw, scene, bx, by, bw, bh):
    """Draw the left-side scene visual preview."""
    draw.rectangle([(bx, by), (bx + bw, by + bh)], fill=CARD_BG)
    draw.rectangle([(bx, by), (bx + bw, by + bh)], outline=DIVIDER, width=1)

    pt = scene["preview_type"]
    txt = scene["preview_text"]
    cx, cy = bx + bw // 2, by + bh // 2

    if pt == "hook":
        font = load_font(FONT_SERIF, 42)
        lines = txt.split("\n")
        total_h = len(lines) * 54
        y = cy - total_h // 2
        for line in lines:
            w = draw.textlength(line, font=font)
            draw.text((cx - w / 2, y), line, font=font, fill=TEXT)
            y += 54

    elif pt == "data":
        # Accent bar top
        draw.rectangle([(bx, by), (bx + bw, by + 4)], fill=ACCENT)
        font_label = load_font(FONT_SANS_BOLD, 18)
        font_name = load_font(FONT_SERIF, 52)
        font_sub = load_font(FONT_SANS, 22)
        parts = txt.split("\n")
        draw.text((bx + 30, by + 20), "FINALLY SOLVED", font=font_label, fill=ACCENT)
        name_w = draw.textlength(parts[0], font=font_name)
        draw.text((cx - name_w / 2, cy - 50), parts[0], font=font_name, fill=TEXT)
        if len(parts) > 1:
            sub_w = draw.textlength(parts[1], font=font_sub)
            draw.text((cx - sub_w / 2, cy + 20), parts[1], font=font_sub, fill=SUBTEXT)
        if len(parts) > 2:
            tag_w = draw.textlength(parts[2], font=font_sub)
            draw.text((cx - tag_w / 2, cy + 56), parts[2], font=font_sub, fill=ACCENT)

    elif pt == "timeline":
        draw.rectangle([(bx, by), (bx + bw, by + 4)], fill=ACCENT)
        draw.rectangle([(bx + 60, by + 30), (bx + 62, by + bh - 20)], fill=DIVIDER)
        dot_x, dot_y = bx + 54, cy - 10
        draw.ellipse([(dot_x - 8, dot_y - 8), (dot_x + 8, dot_y + 8)], fill=ACCENT)
        font_date = load_font(FONT_SANS_BOLD, 30)
        font_desc = load_font(FONT_SANS, 22)
        parts = txt.split("\n")
        draw.text((bx + 90, dot_y - 30), parts[0], font=font_date, fill=TEXT)
        y_off = dot_y + 10
        for line in parts[1:]:
            draw.text((bx + 90, y_off), line, font=font_desc, fill=SUBTEXT)
            y_off += 30

    elif pt == "impact":
        draw.rectangle([(bx, by), (bx + bw, by + bh)], fill=(30, 5, 10))
        parts = txt.split("\n")
        font_big = load_font(FONT_SERIF, 130)
        font_sub = load_font(FONT_SERIF, 52)
        w = draw.textlength(parts[0], font=font_big)
        draw.text((cx - w / 2, cy - 110), parts[0], font=font_big, fill=ACCENT)
        if len(parts) > 1:
            w2 = draw.textlength(parts[1], font=font_sub)
            draw.text((cx - w2 / 2, cy + 50), parts[1], font=font_sub, fill=TEXT)

    elif pt == "failure":
        draw.rectangle([(bx, by), (bx + bw, by + bh)], fill=(12, 8, 8))
        font = load_font(FONT_SANS_BOLD, 30)
        lines = txt.split("\n")
        total_h = len(lines) * 48
        y = cy - total_h // 2
        for line in lines:
            draw.rectangle([(bx + 30, y - 4), (bx + 38, y + 34)], fill=ACCENT)
            draw.text((bx + 54, y), line, font=font, fill=TEXT)
            y += 48

    elif pt == "alarm":
        draw.rectangle([(bx, by), (bx + bw, by + bh)], fill=(28, 4, 4))
        parts = txt.split("\n")
        font_alarm = load_font(FONT_SERIF, 100)
        font_sub   = load_font(FONT_SANS_BOLD, 28)
        w = draw.textlength(parts[0], font=font_alarm)
        draw.text((cx - w / 2, cy - 110), parts[0], font=font_alarm, fill=TEXT)
        if len(parts) > 1:
            w2 = draw.textlength(parts[1], font=font_alarm)
            draw.text((cx - w2 / 2, cy + 0), parts[1], font=font_alarm, fill=TEXT)
        if len(parts) > 2:
            w3 = draw.textlength(parts[2], font=font_sub)
            draw.text((cx - w3 / 2, cy + 120), parts[2], font=font_sub, fill=ACCENT)

    elif pt == "cta":
        draw.rectangle([(bx, by), (bx + bw, by + bh)], fill=CARD_BG)
        draw.rectangle([(bx, by), (bx + bw, by + 4)], fill=ACCENT)
        draw.rectangle([(bx, by + bh - 4), (bx + bw, by + bh)], fill=ACCENT)
        parts = txt.split("\n")
        font_ch = load_font(FONT_SANS_BOLD, 22)
        font_q  = load_font(FONT_SERIF, 32)
        draw.text((bx + 24, by + 20), parts[0], font=font_ch, fill=ACCENT)
        y = cy - 60
        for line in parts[2:]:
            if line:
                w = draw.textlength(line, font=font_q)
                draw.text((cx - w / 2, y), line, font=font_q, fill=TEXT)
            y += 44


def render_frame(frame: int) -> Image.Image:
    # Determine which scene and local frame
    scene_idx = 0
    local_frame = frame
    for i, scene in enumerate(SCENES):
        dur = SCENE_DURATION[scene["number"]]
        if local_frame < dur:
            scene_idx = i
            break
        local_frame -= dur

    scene = SCENES[scene_idx]
    dur = SCENE_DURATION[scene["number"]]

    # Compute crossfade opacity
    fade_in  = ease_out(min(local_frame / FADE_FRAMES, 1.0))
    fade_out = ease_out(min((dur - local_frame) / FADE_FRAMES, 1.0))
    opacity  = min(fade_in, fade_out)

    img = Image.new("RGBA", (W, H), (*BG, 255))
    draw = ImageDraw.Draw(img)

    # ── Header bar ────────────────────────────────────────────────────────
    draw.rectangle([(0, 0), (W, 56)], fill=(*PANEL_BG, 255))
    draw.rectangle([(0, 56), (W, 57)], fill=(*DIVIDER, 255))
    draw.rectangle([(0, 0), (5, 56)], fill=(*ACCENT, 255))

    font_header = load_font(FONT_SANS_BOLD, 20)
    font_small  = load_font(FONT_SANS, 18)
    draw.text((20, 18), "FINALLY SOLVED  ·  STORYBOARD", font=font_header, fill=(*SUBTEXT, 255))
    scene_label = f"SCENE {scene['number']} of {len(SCENES)}   {scene['timecode']}"
    sw = draw.textlength(scene_label, font=font_small)
    draw.text((W - sw - 24, 19), scene_label, font=font_small, fill=(*SUBTEXT, 255))

    # ── Main content area ─────────────────────────────────────────────────
    content_y = 72
    content_h = H - content_y - 70
    pad = 24

    # Left: visual preview (58% width)
    preview_w = int(W * 0.58)
    preview_h = content_h
    bx, by = pad, content_y
    bw, bh = preview_w - pad * 2, preview_h - pad

    draw_preview_box(draw, scene, bx, by, bw, bh)

    # Right: metadata panel
    rx = preview_w + pad
    ry = content_y
    rw = W - rx - pad
    rh = content_h - pad

    # Scene title
    font_title = load_font(FONT_SANS_BOLD, 26)
    draw.rectangle([(rx, ry), (rx + rw, ry + 2)], fill=(*ACCENT, 255))
    draw.text((rx, ry + 10), scene["title"], font=font_title, fill=(*TEXT, 255))

    # Shot type badge
    font_badge = load_font(FONT_SANS_BOLD, 16)
    badge_text = f"  {scene['shot_type']}  "
    bw2 = draw.textlength(badge_text, font=font_badge)
    draw.rectangle([(rx, ry + 46), (rx + bw2 + 4, ry + 70)], fill=(*ACCENT, int(0.2 * 255)))
    draw.rectangle([(rx, ry + 46), (rx + bw2 + 4, ry + 70)], outline=(*ACCENT, int(0.4 * 255)), width=1)
    draw.text((rx + 2, ry + 50), badge_text, font=font_badge, fill=(*ACCENT, 255))

    # VO label + text
    font_label = load_font(FONT_SANS_BOLD, 17)
    font_vo    = load_font(FONT_SERIF, 22)
    font_notes = load_font(FONT_SANS, 18)

    vo_y = ry + 88
    draw.text((rx, vo_y), "VOICEOVER", font=font_label, fill=(*SUBTEXT, 255))
    vo_y += 26
    draw.rectangle([(rx, vo_y), (rx + rw, vo_y + 1)], fill=(*DIVIDER, 255))
    vo_y += 10
    for line in scene["vo"].split("\n"):
        draw.text((rx, vo_y), line, font=font_vo, fill=(*TEXT, 255))
        vo_y += 30
    vo_y += 16

    # Production notes
    draw.text((rx, vo_y), "PRODUCTION NOTES", font=font_label, fill=(*SUBTEXT, 255))
    vo_y += 26
    draw.rectangle([(rx, vo_y), (rx + rw, vo_y + 1)], fill=(*DIVIDER, 255))
    vo_y += 10
    for line in scene["notes"].split("\n"):
        draw.text((rx, vo_y), line, font=font_notes, fill=(*SUBTEXT, 255))
        vo_y += 26

    # ── Bottom bar: scene title + progress ────────────────────────────────
    bar_y = H - 60
    draw.rectangle([(0, bar_y), (W, H)], fill=(*PANEL_BG, 255))
    draw.rectangle([(0, bar_y), (W, bar_y + 1)], fill=(*DIVIDER, 255))

    font_scene_title = load_font(FONT_SANS_BOLD, 22)
    draw.text((24, bar_y + 18), scene["title"], font=font_scene_title, fill=(*TEXT, 255))

    # Progress bar
    prog_total = TOTAL_FRAMES
    prog_pct = frame / prog_total
    pb_x, pb_y, pb_w, pb_h = W - 360, bar_y + 24, 330, 12
    draw.rectangle([(pb_x, pb_y), (pb_x + pb_w, pb_y + pb_h)], fill=(*DIVIDER, 255))
    draw.rectangle([(pb_x, pb_y), (pb_x + int(pb_w * prog_pct), pb_y + pb_h)], fill=(*ACCENT, 255))

    # Timecode
    total_sec = frame / FPS
    m, s = divmod(int(total_sec), 60)
    tc = f"{m}:{s:02d}"
    font_tc = load_font(FONT_SANS, 18)
    tw = draw.textlength(tc, font=font_tc)
    draw.text((pb_x - tw - 12, bar_y + 20), tc, font=font_tc, fill=(*SUBTEXT, 255))

    # Apply fade
    if opacity < 1.0:
        fade_overlay = Image.new("RGBA", (W, H), (*BG, int((1 - opacity) * 255)))
        img = Image.alpha_composite(img, fade_overlay)

    return img.convert("RGB")


def main():
    print(f"Rendering {TOTAL_FRAMES} frames ({TOTAL_FRAMES / FPS:.0f}s) at {W}×{H}...")
    cmd = [
        FFMPEG, "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{W}x{H}", "-pix_fmt", "rgb24",
        "-r", str(FPS), "-i", "pipe:0",
        "-vcodec", "libx264", "-pix_fmt", "yuv420p",
        "-crf", "18", OUTPUT,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)

    for f in range(TOTAL_FRAMES):
        proc.stdin.write(render_frame(f).tobytes())
        if f % 60 == 0:
            sec = f / FPS
            m, s = divmod(int(sec), 60)
            print(f"  {m}:{s:02d} / 1:00  (frame {f}/{TOTAL_FRAMES})")

    proc.stdin.close()
    proc.wait()
    print(f"\nDone → {OUTPUT}")


if __name__ == "__main__":
    main()
