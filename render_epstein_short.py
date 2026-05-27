"""60-second YouTube Short — Jeffrey Epstein / Finally Solved."""
import math, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FFMPEG  = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
OUTPUT  = "/home/user/supercode/output/epstein_short_60s.mp4"
W, H    = 1080, 1920
FPS     = 30
TOTAL   = 1800   # 60 s

F_SERIF  = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
F_SANS   = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
F_BOLD   = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

BG      = (8,   8,  16)
ACCENT  = (196, 30,  58)
TEXT    = (240, 240, 240)
DIM     = (136, 136, 153)
PANEL   = (14,  14,  28)
LINE    = (40,  40,  70)

Path(OUTPUT).parent.mkdir(parents=True, exist_ok=True)

# ── helpers ───────────────────────────────────────────────────────────────────

def f(path, sz):   return ImageFont.truetype(path, sz)
def clamp(v):      return max(0.0, min(1.0, v))
def eo(t):         t=clamp(t); return 1-(1-t)**3
def eio(t):        t=clamp(t); return t*t*(3-2*t)
def sp(t, d=12):
    t=clamp(t)
    return 0 if t==0 else 1-math.exp(-d*t)*math.cos(math.pi*t*2.5)

def it(frame, f0, f1, v0=0.0, v1=1.0):
    t = clamp((frame-f0)/max(f1-f0,1))
    return v0+(v1-v0)*t

def cx(draw, text, font, y, color, alpha=255):
    w = draw.textlength(text, font=font)
    draw.text(((W-w)/2, y), text, font=font, fill=(*color, alpha))

def bars(draw):
    draw.rectangle([(0,0),(W,6)],       fill=(*ACCENT,255))
    draw.rectangle([(0,H-6),(W,H)],     fill=(*ACCENT,255))

def bug(draw, a):
    fo = f(F_BOLD, 26)
    draw.rectangle([(32,56),(36,92)],   fill=(*ACCENT, int(a*255)))
    draw.text((46,60), "FINALLY SOLVED", font=fo, fill=(*ACCENT, int(a*255)))

def fade_overlay(img, color, alpha):
    if alpha <= 0: return img
    ov = Image.new("RGBA", img.size, (*color, int(alpha*255)))
    return Image.alpha_composite(img, ov)

# ── scenes ────────────────────────────────────────────────────────────────────

def s1_hook(lf, img, draw):
    """0-7s  Cold open — hook text."""
    bars(draw)
    bug(draw, eo(it(lf,0,20)))

    lines = [
        ("He trafficked minors",   0,  TEXT),
        ("for the world's most",  14,  TEXT),
        ("powerful men.",         28,  ACCENT),
        ("",                      40,  TEXT),
        ("And the system",        46,  DIM),
        ("let him.",              60,  DIM),
    ]
    font_big = f(F_SERIF, 86)
    font_sm  = f(F_SERIF, 72)
    y = 340
    for i, (line, start, color) in enumerate(lines):
        if not line:
            y += 30; continue
        font = font_big if i < 3 else font_sm
        t = eo(it(lf, start, start+22))
        cx(draw, line, font, y, color, int(t*255))
        y += 110 if i < 3 else 95


def s2_who(lf, img, draw):
    """7-14s  Who was he — data graphic."""
    bars(draw)
    bug(draw, eo(it(lf,0,18)))

    t_name = sp(it(lf,10,48), 10)
    t_sub  = eo(it(lf,38,62))
    t_tag  = eo(it(lf,55,78))
    t_line = eo(it(lf,5,28))

    # Divider line
    lw = int(t_line * (W-80))
    draw.rectangle([(40,200),(40+lw,202)], fill=(*LINE,255))

    # Name
    fn = f(F_SERIF, 118)
    for i,(word,delay) in enumerate([("Jeffrey",12),("Epstein",22)]):
        tw = sp(it(lf, delay, delay+36), 10)
        ww = draw.textlength(word, fn)
        yo = int((1-tw)*40)
        draw.text(((W-ww)/2, 700+i*140+yo), word, font=fn,
                  fill=(*TEXT, int(tw*255)))

    # Years + role
    fs = f(F_SANS, 34)
    cx(draw, "1953 – 2019  ·  Financier", fs, 1005, DIM, int(t_sub*255))

    # Micro-series badge
    fb = f(F_BOLD, 24)
    tag = "THE SYSTEM KNEW"
    tw2 = draw.textlength(tag, fb)
    bx = (W-tw2-40)//2
    draw.rectangle([(bx,1068),(bx+tw2+40,1108)],
                   fill=(*ACCENT, int(t_tag*45)))
    draw.rectangle([(bx,1068),(bx+tw2+40,1108)],
                   outline=(*ACCENT, int(t_tag*90)), width=1)
    cx(draw, tag, fb, 1076, ACCENT, int(t_tag*255))


def s3_network(lf, img, draw):
    """14-21s  The network."""
    bars(draw)
    bug(draw, 1.0)

    t_hdr = eo(it(lf,0,20))
    names = [
        ("Bill Clinton",         22, TEXT),
        ("Prince Andrew",        36, TEXT),
        ("Bill Gates",           50, TEXT),
        ("Alan Dershowitz",      64, TEXT),
        ("Donald Trump",         78, TEXT),
        ("Les Wexner",           92, TEXT),
    ]
    fn_hdr = f(F_BOLD, 34)
    fn_nm  = f(F_SERIF, 74)

    cx(draw, "CONNECTED TO:", fn_hdr, 320, ACCENT, int(t_hdr*255))
    draw.rectangle([(80,376),(W-80,378)], fill=(*LINE, int(t_hdr*255)))

    y = 420
    for name, start, color in names:
        t = sp(it(lf, start, start+26), 11)
        xoff = int((1-t)*-50)
        draw.text((80+xoff, y), name, font=fn_nm, fill=(*color, int(t*255)))
        y += 100

    t_note = eo(it(lf,100,128))
    fn = f(F_SANS, 28)
    cx(draw, "Flight logs. Visitor records. Court filings.", fn, 1060, DIM, int(t_note*255))


def s4_arrest(lf, img, draw):
    """21-28s  First arrest 2005."""
    bars(draw)
    bug(draw, 1.0)

    t_hdr  = eo(it(lf,0,22))
    t_dot  = eo(it(lf,15,32))
    t_evt  = sp(it(lf,20,52), 11)
    t_sub  = eo(it(lf,45,70))
    t_note = eo(it(lf,65,90))

    fn_hdr  = f(F_BOLD, 32)
    fn_yr   = f(F_SERIF, 110)
    fn_evt  = f(F_SERIF, 68)
    fn_sub  = f(F_SANS, 34)
    fn_note = f(F_SANS, 30)

    cx(draw, "TIMELINE", fn_hdr, 240, ACCENT, int(t_hdr*255))

    # Timeline spine
    draw.rectangle([(W//2-2, 330),(W//2+2, H-160)], fill=(*LINE,255))

    # Dot
    if t_dot > 0:
        r = 16
        draw.ellipse([(W//2-r,560-r),(W//2+r,560+r)], fill=(*ACCENT,int(t_dot*255)))

    # Year
    yr_w = draw.textlength("2005", font=fn_yr)
    yo = int((1-t_evt)*35)
    draw.text(((W-yr_w)/2, 620+yo), "2005", font=fn_yr,
              fill=(*TEXT, int(t_evt*255)))

    cx(draw, "FIRST ARREST", fn_evt, 756, TEXT, int(t_evt*255))
    cx(draw, "Palm Beach, Florida", fn_sub, 850, DIM, int(t_sub*255))

    lines = ["30+ underage victims identified.", "FBI opens investigation."]
    y = 950
    for line in lines:
        cx(draw, line, fn_note, y, DIM, int(t_note*255))
        y += 52


def s5_deal(lf, img, draw):
    """28-35s  The sweetheart deal."""
    img = fade_overlay(img, (28,4,8), 0.82)
    draw = ImageDraw.Draw(img)
    bars(draw)
    bug(draw, 1.0)

    t_lbl  = eo(it(lf,0,22))
    t_big  = sp(it(lf,16,52), 9)
    t_mo   = eo(it(lf,40,62))
    t_d1   = eo(it(lf,58,80))
    t_d2   = eo(it(lf,70,92))
    t_d3   = eo(it(lf,82,104))

    fn_lbl = f(F_BOLD, 34)
    fn_big = f(F_SERIF, 290)
    fn_mo  = f(F_SERIF, 82)
    fn_det = f(F_SANS, 32)

    cx(draw, "THE DEAL", fn_lbl, 290, DIM, int(t_lbl*255))

    bw = draw.textlength("13", font=fn_big)
    yo = int((1-t_big)*55)
    draw.text(((W-bw)/2, 380+yo), "13", font=fn_big,
              fill=(*ACCENT, int(t_big*255)))

    cx(draw, "MONTHS", fn_mo, 730, TEXT, int(t_mo*255))

    details = [
        ("Work release 6 days/week.", t_d1),
        ("Victims were never notified.", t_d2),
        ("Signed in secret.", t_d3),
    ]
    y = 880
    for line, t in details:
        cx(draw, line, fn_det, y, DIM, int(t*255))
        y += 60

    return img


def s6_coverup(lf, img, draw):
    """35-42s  The cover-up."""
    bars(draw)
    draw.rectangle([(0,0),(6,H)],   fill=(*ACCENT,255))
    draw.rectangle([(W-6,0),(W,H)], fill=(*ACCENT,255))
    bug(draw, 1.0)

    t_hdr = eo(it(lf,0,22))
    fn_hdr = f(F_BOLD, 34)
    cx(draw, "WHO SIGNED OFF?", fn_hdr, 270, ACCENT, int(t_hdr*255))
    draw.rectangle([(80,318),(W-80,320)], fill=(*LINE,255))

    entries = [
        ("FBI",           "Had evidence. Filed it away.",    20, 48),
        ("DOJ",           "Approved the non-prosecution\nagreement.", 40, 68),
        ("Alex Acosta",   "Signed the deal. Told nobody.",   60, 88),
        ("Federal Judge", "Sealed victims' identities.",     80, 108),
    ]
    fn_nm  = f(F_BOLD, 46)
    fn_sub = f(F_SANS, 30)
    y = 380
    for name, detail, t_start_n, t_start_d in entries:
        tn = sp(it(lf, t_start_n, t_start_n+30), 11)
        td = eo(it(lf, t_start_d, t_start_d+24))
        xo = int((1-tn)*-50)
        draw.text((90+xo, y), name, font=fn_nm, fill=(*TEXT, int(tn*255)))
        y += 58
        for dline in detail.split("\n"):
            draw.text((90, y), dline, font=fn_sub, fill=(*DIM, int(td*255)))
            y += 42
        y += 30


def s7_second(lf, img, draw):
    """42-49s  Second arrest 2019."""
    bars(draw)
    bug(draw, 1.0)

    t_dot  = eo(it(lf,10,28))
    t_evt  = sp(it(lf,18,52), 11)
    t_sub  = eo(it(lf,44,68))
    t_note = eo(it(lf,62,88))

    fn_hdr  = f(F_BOLD, 32)
    fn_yr   = f(F_SERIF, 110)
    fn_evt  = f(F_SERIF, 68)
    fn_sub  = f(F_SANS, 34)
    fn_note = f(F_SANS, 30)

    cx(draw, "TIMELINE", fn_hdr, 240, ACCENT, int(eo(it(lf,0,20))*255))
    draw.rectangle([(W//2-2,330),(W//2+2,H-160)], fill=(*LINE,255))

    if t_dot > 0:
        r = 16
        draw.ellipse([(W//2-r,560-r),(W//2+r,560+r)], fill=(*ACCENT,int(t_dot*255)))

    yr_w = draw.textlength("2019", font=fn_yr)
    yo = int((1-t_evt)*35)
    draw.text(((W-yr_w)/2, 620+yo), "2019", font=fn_yr,
              fill=(*TEXT, int(t_evt*255)))

    cx(draw, "ARRESTED AGAIN", fn_evt, 756, TEXT, int(t_evt*255))
    cx(draw, "Federal charges — 45 counts", fn_sub, 850, DIM, int(t_sub*255))

    notes = ["No plea deal offered.", "Bail denied. Held in Manhattan."]
    y = 950
    for note in notes:
        cx(draw, note, fn_note, y, DIM, int(t_note*255))
        y += 52


def s8_death(lf, img, draw):
    """49-56s  Dead in his cell."""
    img = fade_overlay(img, (28,4,4), 0.88)
    draw = ImageDraw.Draw(img)

    if lf < 10:
        img = fade_overlay(img, ACCENT, eo(it(lf,0,6)) * 0.6)
        draw = ImageDraw.Draw(img)

    bars(draw)
    bug(draw, 1.0)

    t_date = eo(it(lf,8,28))
    t_w1   = sp(it(lf,14,46), 9)
    t_w2   = sp(it(lf,22,54), 9)
    t_w3   = sp(it(lf,30,62), 9)
    t_det  = eo(it(lf,60,88))

    fn_date = f(F_BOLD, 30)
    fn_big  = f(F_SERIF, 162)
    fn_det  = f(F_SANS, 32)

    cx(draw, "AUGUST 10, 2019", fn_date, 260, DIM, int(t_date*255))

    words = [("DEAD",    t_w1, 380),
             ("IN HIS",  t_w2, 560),
             ("CELL.",   t_w3, 740)]
    for word, t, y in words:
        yo = int((1-t)*40)
        ww = draw.textlength(word, fn_big)
        draw.text(((W-ww)/2, y+yo), word, font=fn_big,
                  fill=(*TEXT, int(t*255)))

    details = [
        "Guards were both asleep.",
        "Security cameras malfunctioned.",
        "Cellmate removed day before.",
        "Client list remains sealed.",
    ]
    y = 960
    for det in details:
        cx(draw, det, fn_det, y, DIM, int(t_det*255))
        y += 54

    return img


def s9_question(lf, img, draw):
    """56-60s  The question + CTA."""
    bars(draw)
    bug(draw, 1.0)

    t_div = eo(it(lf,0,22))
    lw = int(t_div*500)
    draw.rectangle([((W-lw)//2,340),((W+lw)//2,342)], fill=(*LINE,255))

    fn_q   = f(F_SERIF, 90)
    fn_sub = f(F_SERIF, 68)
    fn_cta = f(F_BOLD, 30)

    lines = [
        ("Was it",              sp(it(lf,12,46),11), fn_q,   380, TEXT),
        ("suicide?",            sp(it(lf,20,54),11), fn_q,   488, TEXT),
        ("",                    0,                   fn_q,   0,   TEXT),
        ("Or did the system",   sp(it(lf,32,66),11), fn_sub, 632, ACCENT),
        ("protect itself",      sp(it(lf,42,76),11), fn_sub, 722, ACCENT),
        ("one last time?",      sp(it(lf,52,86),11), fn_sub, 812, ACCENT),
    ]
    for line, t, font, y, color in lines:
        if not line: continue
        yo = int((1-t)*32)
        cx(draw, line, font, y+yo, color, int(t*255))

    t_cta = eo(it(lf,72,100))
    t_out = eio(it(lf,100,120))

    cx(draw, "Follow for the full breakdown ↓", fn_cta, 1000, TEXT, int(t_cta*255))
    cx(draw, "@FinallySolved",                  fn_cta, 1050, ACCENT, int(t_cta*255))

    if t_out > 0:
        img = fade_overlay(img, BG, t_out)
    return img


# ── scene schedule ────────────────────────────────────────────────────────────
# (global_start_frame, duration_frames, render_fn, needs_img_return)

SCENES = [
    (0,    210, s1_hook,     False),
    (210,  210, s2_who,      False),
    (420,  210, s3_network,  False),
    (630,  210, s4_arrest,   False),
    (840,  210, s5_deal,     True),
    (1050, 210, s6_coverup,  False),
    (1260, 210, s7_second,   False),
    (1470, 210, s8_death,    True),
    (1680, 120, s9_question, True),
]
FADE = 20


def render_frame(frame: int) -> Image.Image:
    img = Image.new("RGBA", (W, H), (*BG, 255))
    draw = ImageDraw.Draw(img)

    for start, dur, fn, returns_img in SCENES:
        if start <= frame < start + dur:
            lf = frame - start

            result = fn(lf, img, draw)
            if returns_img and result is not None:
                img = result
                draw = ImageDraw.Draw(img)

            # crossfade at boundaries
            fi = 1 - eo(clamp(lf / FADE))
            fo = eo(clamp((lf - (dur - FADE)) / FADE))
            alpha = max(fi, fo)
            if alpha > 0:
                img = fade_overlay(img, BG, alpha)
            break

    return img.convert("RGB")


def main():
    print(f"Rendering {TOTAL} frames (60s) at {W}×{H} vertical…")
    cmd = [
        FFMPEG, "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{W}x{H}", "-pix_fmt", "rgb24",
        "-r", str(FPS), "-i", "pipe:0",
        "-vcodec", "libx264", "-pix_fmt", "yuv420p",
        "-crf", "16", OUTPUT,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    for fr in range(TOTAL):
        proc.stdin.write(render_frame(fr).tobytes())
        if fr % 150 == 0:
            print(f"  {fr//FPS}s / 60s")
    proc.stdin.close()
    proc.wait()
    print(f"\nDone → {OUTPUT}")


if __name__ == "__main__":
    main()
