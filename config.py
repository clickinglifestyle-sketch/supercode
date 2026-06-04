from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
CASES_FILE = DATA_DIR / "cases.json"
REDDIT_LOG_FILE = DATA_DIR / "reddit_log.json"
NOTEBOOKS_FILE = DATA_DIR / "notebooks.json"

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

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

# ---------------------------------------------------------------------------
# YouTube tag system (sourced from vidIQ keyword research)
# ---------------------------------------------------------------------------

# Tier 1 — Use on every single upload (high volume, best opportunity scores)
TAGS_TIER1 = [
    "true crime documentary",
    "crime documentary",
    "true crime",
    "true crime stories",
    "documentary",
    "crime stories",
    "true crime story",
    "detective stories",
]

# Tier 2 — Rotate per video (strong volume, fits the channel format)
TAGS_TIER2 = [
    "serial killer documentary",
    "criminal psychology",
    "missing persons cases",
    "real crime",
    "unsolved mysteries",
    "cold case",
    "mystery",
    "crime investigation",
    "missing persons",
    "cold cases",
]

# Tier 3 — Add when relevant to specific case type
TAGS_TIER3 = [
    "murder documentary",
    "solved cold cases",
    "cold case finally solved",
    "unsolved crime",
    "missing persons case",
    "cold case solved",
]

# Brand tags — always append
TAGS_BRAND = [
    "finally solved",
    "finally solved true crime",
]

# Case-specific tags by micro-series
TAGS_BY_MICRO_SERIES = {
    "The Evidence Was There": [
        "evidence ignored",
        "dna cold case solved",
        "forensic genealogy",
    ],
    "They Called It an Accident": [
        "murder cover up",
        "wrongful death investigation",
        "homicide misclassified",
    ],
    "Caught By One Mistake": [
        "serial killer caught",
        "genetic genealogy solved",
        "cold case dna breakthrough",
    ],
    "They Got The Wrong Person": [
        "wrongful conviction",
        "false confession",
        "wrongful arrest documentary",
    ],
    "The System Knew": [
        "police failure documentary",
        "institutional cover up",
        "system failed documentary",
    ],
}

# Case-specific tags by failure type
TAGS_BY_FAILURE_TYPE = {
    "institutional_failure": [
        "police failure",
        "justice system failure",
        "system failed",
    ],
    "cognitive_blind_spot": [
        "investigative failure",
        "cold case reopened",
        "detective failure",
    ],
    "deliberate_betrayal": [
        "cover up documentary",
        "corruption documentary",
        "deliberate cover up",
    ],
}

# Tags by complexity (long-form format)
TAGS_BY_COMPLEXITY = {
    "triple": ["full documentary 2026", "true crime documentary 2026", "long documentary"],
    "double": ["true crime documentary 2026", "full documentary 2026"],
    "single": ["true crime documentary 2026", "short documentary"],
}
