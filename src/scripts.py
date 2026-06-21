import anthropic
from config import (
    ANTHROPIC_API_KEY, COMPLEXITY_TIERS,
    TAGS_TIER1, TAGS_TIER2, TAGS_BY_MICRO_SERIES, TAGS_BY_FAILURE_TYPE, TAGS_BRAND,
    CHANNEL_NAME, CHANNEL_HANDLE,
)
from src.models import Case

# ---------------------------------------------------------------------------
# Channel voice & system prompt  (cached — stable across all requests)
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = f"""You are the full production writer for "{CHANNEL_NAME}" ({CHANNEL_HANDLE}), a dark history YouTube channel.

CHANNEL IDENTITY
- The version of history they cut from the textbook
- Tone: curious, precise, slightly unsettling — NOT gruesome or clickbait
- The viewer should feel like they were lied to by a trusted source, not just horrified
- Open with the most revelatory fact — the thing that reframes everything they thought they knew
- No filler: never open with "Today we're looking at...", "Let's dive in...", "Welcome back...", or "In this video..."
- Numbers must be specific: "23 years" not "decades," "6 separate governments" not "many"
- The hook is always a reframe, not a tease: state the dark truth, then prove it

FIVE CONTENT SERIES
1. Childhood Lies — beloved brands, shows, and icons had dark secrets hidden from children
2. The Hidden Record — documented historical facts that were deliberately cut from official accounts
3. Nature's Darkest Chapter — biology, evolution, and the natural world in ways that disturb
4. Famous and Rotten — the documented dark history behind figures everyone respects
5. The Cover Story — what the official narrative says vs. what the primary sources actually show

THREE CONTENT CATEGORIES
- Nostalgia Betrayal: the darker truth behind something people love
- Scientific Horror: documented biological or medical fact that is genuinely disturbing
- Historical Concealment: a fact that was actively suppressed or omitted from the record

VOICE CALIBRATION
- Lead with the most disturbing specific fact, not a question
- Passive voice forbidden for perpetrators; use it only for institutions
- Sentences under 15 words when delivering the key revelation
- No rhetorical questions used as hooks — state the fact, let the fact work
- No music cues, no [B-roll suggestions], no stage directions — pure narration

SUBSCRIBE CONVERSION MANDATE
Every piece must contain one clear reason to subscribe embedded in the CTA:
  "This is [series name]. New entry every week."
The series name is what makes viewers subscribe — they want the next one, not just this one.

SHORTS — FULL PRODUCTION PACKAGE FORMAT
For every Short (Monday, Wednesday, Friday, Thursday PI, Saturday PI), output the complete
production package in this exact structure:

[SLOT LABEL] — [TOPIC NAME]
Hook [Letter] — [Hook Type]

SCRIPT:
[narration — 150-170 words, 60 seconds]

THREE LAYER REVELATION CHECK — [DAY]

Reframe strength? ✅ — [one sentence: what assumption does this overturn?]
Specific source detail? ✅ — [one sentence naming the institution, date, or document]
Absurdity amplifier? ✅ — [the single most disturbing specific detail, then what it means]

✅ Superior hook confirmed.

[DAY] — FULL PACKAGE

Title:
[title] ([character count])

Description:
[2-3 sentence description with the core revelation, no filler, ends with series value prop]
Dark Chapters covers the version of history they didn't put in the textbook — new entry every week.
#DarkChapters #DarkHistory #HistoryFacts #DisturbingFacts #HiddenHistory

Tags:
[comma-separated YouTube tags, series-specific + evergreen, no # symbols]

Pinned Comment:
[3-5 punchy sentences. Restate 3 key dark facts. End with: This is [series name]. New entry every week.]

TikTok Caption:
[5-7 short punchy sentences. Dark facts only. End with 5 hashtags.]

Instagram Caption:
[Full script rewritten as caption — slightly more detail than TikTok. End with 📖 and 5 hashtags.]

Thumbnail Image Prompt:
[Detailed AI image generation prompt. Illustrated style with high contrast. Grid of 4-6 illustrated portraits or items, each labeled. Bold text overlay stating the core dark fact. Dark background with warm accent highlights. DARK CHAPTERS watermark bottom right.]

LONG-FORM — NARRATION ONLY
For Sunday long-form scripts, output narration only. No metadata. Start immediately with the first spoken word.
"""

# ---------------------------------------------------------------------------
# Evergreen tag base — injected into every Short package
# ---------------------------------------------------------------------------

def _base_tags() -> str:
    base = (
        TAGS_TIER1[:6]
        + ["history facts", "dark historical facts", "history exposed",
           "disturbing history", "history they don't teach you",
           "dark truth revealed", "hidden history facts"]
    )
    return ", ".join(base)


def _case_tags(case: Case) -> str:
    specific = (
        TAGS_BY_MICRO_SERIES.get(case.micro_series, [])
        + TAGS_BY_FAILURE_TYPE.get(case.failure_type, [])
    )
    name_tag = case.name.lower()
    tags = [name_tag] + specific
    seen = set()
    unique = []
    for t in tags:
        if t not in seen:
            seen.add(t)
            unique.append(t)
    return ", ".join(unique)


# ---------------------------------------------------------------------------
# Per-slot user prompt templates
# ---------------------------------------------------------------------------

def _slot_prompt(slot: str, case: Case, extra_context: str = "") -> str:
    name = case.name
    summary = case.summary or f"a {case.complexity}-layer dark history topic"
    series = case.micro_series
    category = case.failure_type.replace("_", " ")
    year_str = f" ({case.year})" if case.year else ""
    base_tags = _base_tags()
    case_tags = _case_tags(case)
    all_tags = f"{base_tags}, {case_tags}"

    short_instructions = f"""
EVERGREEN TAGS TO INCLUDE IN THE TAGS SECTION (add topic-specific terms on top):
{all_tags}

{extra_context}
"""

    prompts = {
        "mon_short": f"""Write the complete Monday Short production package (Hook A — Revelation) for: {name}{year_str}.

Content series: {series}
Content category: {category}
Topic summary: {summary}
{short_instructions}

MONDAY SCRIPT RULES:
- Hook A is REVELATION — state the most disturbing fact in the first sentence, no build-up
- Open with the specific documented detail that overturns the official story
- Introduce the topic in 1-2 sentences of context
- Build through 3-4 escalating dark facts from primary sources
- End CTA: "Full story dropping this Sunday. This is {series}. New entry every week — follow."

Output the full production package following the SHORTS — FULL PRODUCTION PACKAGE FORMAT exactly.
Use Hook A — Revelation as the hook type.
Monday as the day label throughout.""",

        "wed_short": f"""Write the complete Wednesday Short production package (Hook B — The Part They Cut Out) for: {name}{year_str}.

Content series: {series}
Content category: {category}
Topic summary: {summary}
{short_instructions}

WEDNESDAY SCRIPT RULES:
- Hook B is THE PART THEY CUT OUT — reveal the specific fact that was omitted from the official version
- Open mid-topic — assume the viewer knows the surface level story
- Reveal the specific mechanism of concealment or omission
- Include one specific primary source quote, document, or date
- End CTA: "Full story dropping this Sunday. This is {series}. If that didn't sit right — follow."

Output the full production package following the SHORTS — FULL PRODUCTION PACKAGE FORMAT exactly.
Use Hook B — The Part They Cut Out as the hook type.
Wednesday as the day label throughout.""",

        "fri_short": f"""Write the complete Friday Short production package (Hook C — The Worst Part) for: {name}{year_str}.

Content series: {series}
Content category: {category}
Topic summary: {summary}
{short_instructions}

FRIDAY SCRIPT RULES:
- Hook C is THE WORST PART — the single most disturbing specific detail of the entire topic
- Open with "The worst part of [topic] isn't [expected thing]. It's [actual worst thing]."
- One specific, documented, verifiable detail — not vague horror
- Land on why this detail changes how you see [the institution / the icon / the story]
- End CTA: "Full breakdown this Sunday. This is {series}. New entry every week — follow."

Output the full production package following the SHORTS — FULL PRODUCTION PACKAGE FORMAT exactly.
Use Hook C — The Worst Part as the hook type.
Friday as the day label throughout.""",

        "thu_pi": f"""Write the complete Thursday Pattern Interrupt Short production package for: {name}{year_str}.

IMPORTANT: This is STANDALONE. Works for a viewer who has never seen any other content on this topic.

Content category: {category}
Topic summary: {summary}
{short_instructions}

THURSDAY PI RULES:
- Opens with a single specific dark fact, stated as a declarative sentence — no question, no tease
- Context: one sentence explaining what makes this fact shocking
- Implication: what this reveals about the broader institution, system, or accepted narrative
- No CTA to "follow the arc" — this piece stands alone
- Hook type: Standalone Dark Fact

Output the full production package following the SHORTS — FULL PRODUCTION PACKAGE FORMAT exactly.
Use Hook D — Standalone Dark Fact as the hook type.
Thursday as the day label throughout.""",

        "sat_pi": f"""Write the complete Saturday Pattern Interrupt Short production package for: {name}{year_str}.

IMPORTANT: This is STANDALONE. Different angle than Thursday's piece. No arc references.

Content series: {series}
Topic summary: {summary}
{short_instructions}

SATURDAY PI RULES:
- Opens with a dark historical comparison or parallel — "In [year], [entity] did [thing]. They called it [euphemism]."
- Uses a DIFFERENT specific detail than Thursday
- Grounds it in a verifiable primary source (name the document, institution, or year)
- Ends on the implication — no resolution, just the disturbing truth sitting there
- Hook type: Historical Parallel

Output the full production package following the SHORTS — FULL PRODUCTION PACKAGE FORMAT exactly.
Use Hook E — Historical Parallel as the hook type.
Saturday as the day label throughout.""",

        "sun_longform": f"""Write the full long-form narration script for: {name}{year_str}.

Content series: {series}
Content category: {category}
Complexity tier: {case.complexity} ({COMPLEXITY_TIERS[case.complexity]['longform_minutes']} minutes)
Topic summary: {summary}
{extra_context}

STRUCTURE — DARK HISTORY DOCUMENTARY FORMAT

INTRO HOOK (30-45 sec)
- Open with the single most disturbing documented fact — not a question, not a tease
- State what the official version says, then immediately state what the primary sources show
- Do NOT open with "Today we're looking at..."

ACT 1 — THE OFFICIAL STORY
- What the accepted narrative says
- How it got established — the specific sources, textbooks, or institutions that spread it
- What felt off even in the official version

ACT 2 — WHAT THE RECORD ACTUALLY SHOWS
- The specific documented evidence that contradicts the official story
- Primary sources: dates, institutions, named individuals, document titles
- Each revelation should be more specific than the last

ACT 3 — WHY IT WAS BURIED
- The specific mechanism of concealment or omission
- Who benefited from the official version and how
- The cost: what was lost, who was harmed, how long the false version persisted

OUTRO
- One-sentence verdict on the institution or narrative
- Series tag: "This is {series}."
- End: "Dark Chapters."

Target word count: {'4500-5500' if case.complexity == 'triple' else '3000-3500' if case.complexity == 'double' else '2000-2500'} words

Output narration only. No metadata. No preamble. Start immediately with the first spoken word.""",
    }

    return prompts.get(slot, f"Write a script for slot '{slot}' for the topic: {name}.")


# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------

def generate_script(case: Case, slot: str, extra_context: str = "") -> str:
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY not set. Add it to your .env file.")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    user_prompt = _slot_prompt(slot, case, extra_context)

    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=8000,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_prompt}],
    )

    text_blocks = [b.text for b in response.content if b.type == "text"]
    return "\n".join(text_blocks).strip()
