from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
CASES_FILE = DATA_DIR / "cases.json"
REDDIT_LOG_FILE = DATA_DIR / "reddit_log.json"

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Channel stats (update periodically)
CURRENT_SUBS = 74
CURRENT_VIEWS = 13261
CURRENT_VIDEOS = 43
LAUNCH_DATE = "2026-04-01"

# YPP targets
YPP_SUBS_TARGET = 1000
YPP_WATCH_HOURS_TARGET = 4000

# Competitor benchmark
COMPETITOR_NAME = "Cold Case Desk"
COMPETITOR_SUBS = 10500
COMPETITOR_MONTHS = 8

# Average watch time assumption (minutes) for mixed Shorts+long content
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
    "mon_short",   # Arc 1 – hook/setup
    "wed_short",   # Arc 2 – complication
    "thu_pi",      # Pattern Interrupt
    "fri_short",   # Arc 3 – escalation/resolution tease
    "sat_pi",      # Pattern Interrupt
    "sun_longform", # Full case
]

# Micro-series
MICRO_SERIES = [
    "The Evidence Was There",
    "They Called It an Accident",
    "Caught By One Mistake",
    "They Got The Wrong Person",
    "The System Knew",
]

# Failure types
FAILURE_TYPES = [
    "institutional_failure",
    "cognitive_blind_spot",
    "deliberate_betrayal",
]

# Case complexity tiers
COMPLEXITY_TIERS = {
    "triple": {"layers": 3, "longform_minutes": "20-25"},
    "double": {"layers": 2, "longform_minutes": "15"},
    "single": {"layers": 1, "longform_minutes": "10-12"},
}

# Reddit subreddits in rotation
REDDIT_SUBREDDITS = [
    "r/UnsolvedMysteries",
    "r/TrueCrime",
    "r/criminaljustice",
    "r/Missing411",
    "r/crimedocumentaries",
]
