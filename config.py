from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
CASES_FILE = DATA_DIR / "cases.json"
REDDIT_LOG_FILE = DATA_DIR / "reddit_log.json"

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Channel identity
CHANNEL_NAME = "Dark Chapters in History"
CHANNEL_HANDLE = "@DarkChaptersInHistory"

# Channel stats (update periodically)
CURRENT_SUBS = 74
CURRENT_VIEWS = 13261
CURRENT_VIDEOS = 43
LAUNCH_DATE = "2026-04-01"

# YPP targets
YPP_SUBS_TARGET = 1000
YPP_WATCH_HOURS_TARGET = 4000

# Competitor benchmark — The Crooked Explainer
# 8.2K subs, 2.3M views, 29 videos, launched Mar 2026
# Weakness: 0.35% sub conversion rate, no consistent series structure
COMPETITOR_NAME = "The Crooked Explainer"
COMPETITOR_SUBS = 8200
COMPETITOR_MONTHS = 4

# Average watch time assumption (minutes) for mixed Shorts + long content
AVG_WATCH_TIME_MINUTES = 8.0

# Asset stages in order
ASSET_STAGES = [
    "idea",
    "research",
    "scripted",
    "voiced",
    "edited",
    "scheduled",
    "published",
]

# Content slots per week
WEEKLY_SLOTS = [
    "mon_short",    # Curiosity Hook — one dark fact, opens the topic
    "wed_short",    # Deep Cut — shocking revelation mid-topic
    "thu_pi",       # Pattern Interrupt — standalone dark historical fact
    "fri_short",    # The Worst Part — most disturbing element of this week's topic
    "sat_pi",       # Did You Know — standalone pattern interrupt
    "sun_longform", # Full dark documentary deep dive
]

# ---------------------------------------------------------------------------
# Five content series (micro-series)
# These map to the highest-converting video types on comparable channels.
# "Childhood Lies" and "Nature's Darkest Chapter" are the proven top performers
# from competitor analysis. Series structure solves the 0.35% sub conversion
# problem — subscribers come back for the next entry in the series.
# ---------------------------------------------------------------------------
MICRO_SERIES = [
    "Childhood Lies",            # dark truth behind beloved childhood things — competitor's best format
    "The Hidden Record",         # history facts cut from textbooks
    "Nature's Darkest Chapter",  # biology/animals dark facts — top SEO performer
    "Famous and Rotten",         # dark sides of beloved historical figures
    "The Cover Story",           # official narrative vs. what actually happened
]

# Content categories (what makes the topic dark/disturbing)
FAILURE_TYPES = [
    "nostalgia_betrayal",       # beloved icons/childhood had dark secrets
    "scientific_horror",        # biology/medicine/nature dark facts
    "historical_concealment",   # facts deliberately hidden from history
]

# Case complexity tiers
COMPLEXITY_TIERS = {
    "triple": {"layers": 3, "longform_minutes": "20-25"},
    "double": {"layers": 2, "longform_minutes": "15"},
    "single": {"layers": 1, "longform_minutes": "10-12"},
}

# Reddit subreddits in rotation
REDDIT_SUBREDDITS = [
    "r/DarkHistory",
    "r/history",
    "r/todayilearned",
    "r/Damnthatsinteresting",
    "r/interestingasfuck",
    "r/morbidquestions",
    "r/WTF",
]

# ---------------------------------------------------------------------------
# YouTube tag system
# Built for dark history niche. Priority order: broad volume → niche authority.
# Tier 1 tags target "dark history" cluster which has high volume + manageable
# competition vs. true crime (too competitive at this channel size).
# ---------------------------------------------------------------------------

# Tier 1 — Use on every single upload
TAGS_TIER1 = [
    "dark history",
    "history facts",
    "disturbing history",
    "dark facts",
    "history you weren't taught",
    "shocking history",
    "dark truth",
    "hidden history",
]

# Tier 2 — Rotate per video
TAGS_TIER2 = [
    "dark history facts",
    "disturbing facts",
    "history documentary",
    "dark documentary",
    "true history",
    "history exposed",
    "history secrets",
    "disturbing true stories",
    "dark historical facts",
    "history they don't teach you",
]

# Tier 3 — Long-form only
TAGS_TIER3 = [
    "dark history documentary",
    "history documentary 2026",
    "dark facts documentary",
    "disturbing historical events",
    "history you won't believe",
    "shocking true history",
]

# Brand tags — always append
TAGS_BRAND = [
    "dark chapters in history",
    "dark chapters history",
]

# Series-specific tags
TAGS_BY_MICRO_SERIES = {
    "Childhood Lies": [
        "dark side of disney",
        "dark childhood nostalgia",
        "disturbing facts about childhood shows",
        "dark truth behind cartoons",
        "childhood shows dark secrets",
    ],
    "The Hidden Record": [
        "history facts you didn't know",
        "history they don't teach",
        "untold history",
        "history facts omitted from textbooks",
        "real history",
    ],
    "Nature's Darkest Chapter": [
        "disturbing animal facts",
        "dark nature facts",
        "weird biology",
        "disturbing biology facts",
        "inbreeding effects",
    ],
    "Famous and Rotten": [
        "dark side of historical figures",
        "famous people dark history",
        "disturbing facts about famous people",
        "historical figures exposed",
    ],
    "The Cover Story": [
        "history cover up",
        "dark historical cover up",
        "official story vs truth",
        "history lies exposed",
        "they didn't want you to know",
    ],
}

# Category-specific tags (replaces failure type tags)
TAGS_BY_FAILURE_TYPE = {
    "nostalgia_betrayal": [
        "childhood nostalgia dark truth",
        "dark side of your favorite show",
        "beloved icons exposed",
        "dark side of famous brands",
    ],
    "scientific_horror": [
        "disturbing science facts",
        "dark biology",
        "nature's dark side",
        "disturbing animal behavior",
        "medical history dark facts",
    ],
    "historical_concealment": [
        "suppressed history",
        "erased from history",
        "cover up history",
        "censored history",
    ],
}

# Tags by complexity (long-form format)
TAGS_BY_COMPLEXITY = {
    "triple": ["full documentary 2026", "dark history documentary 2026", "long documentary"],
    "double": ["dark history documentary 2026", "full documentary 2026"],
    "single": ["dark history documentary 2026", "short documentary"],
}
