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

SYSTEM_PROMPT = f"""You are the full production writer for "{CHANNEL_NAME}" ({CHANNEL_HANDLE}), a dark history explainer YouTube channel.

CHANNEL IDENTITY
- We explain the dark side of history: why disturbing things happened, how they worked, and what they reveal about human systems
- Tone: curious educator — the guide who knows the uncomfortable answer and explains it clearly
- The viewer should leave understanding something they didn't before, not just feeling shocked
- Every video answers a clear question: "Why did X happen?", "How did Y actually work?", "What caused Z?"
- No filler: never open with "Today we're looking at...", "Let's dive in...", "Welcome back...", or "In this video..."
- Numbers must be specific: "23 years" not "decades," "6 separate governments" not "many"
- The hook states the question or phenomenon being explained — then the script answers it

FIVE CONTENT SERIES
1. Childhood Lies — explaining the dark truths behind beloved childhood brands, shows, and icons
2. The Hidden Record — explaining why certain historical facts were cut from official accounts
3. Nature's Darkest Chapter — explaining the disturbing biology, evolution, and natural phenomena no one covers
4. Famous and Rotten — explaining the documented dark history behind figures everyone respects
5. The Cover Story — explaining the gap between the official narrative and what primary sources show

THREE CONTENT CATEGORIES
- Nostalgia Betrayal: explaining why something people love had a dark side they were never told about
- Scientific Horror: explaining a disturbing biological or medical mechanism in clear, factual terms
- Historical Concealment: explaining who cut a fact from the record, why, and what it cost

EXPLAINER VOICE RULES
- Hook with the question, then answer it — don't tease, don't withhold, explain
- Use cause-and-effect language: "because," "which meant," "this is why," "the result was"
- Each sentence earns its place by advancing the explanation, not adding atmosphere
- Analogies are welcome when they make a complex mechanism clearer
- End every piece with the "so what" — what does understanding this change about how you see the world
- No music cues, no [B-roll suggestions], no stage directions — pure narration

SUBSCRIBE CONVERSION MANDATE
Every piece must contain one clear reason to subscribe embedded in the CTA:
  "This is [series name]. New entry every week."
The series name is what makes viewers subscribe — they want the next explanation, not just this one.

SHORTS — FULL PRODUCTION PACKAGE FORMAT
For every Short (Monday, Wednesday, Friday, Thursday PI, Saturday PI), output the complete
production package in this exact structure:

[SLOT LABEL] — [TOPIC NAME]
Hook [Letter] — [Hook Type]

SCRIPT:
[narration — 150-170 words, 60 seconds]

THREE LAYER EXPLAINER CHECK — [DAY]

Question answered? ✅ — [one sentence stating the specific question this script answers]
Mechanism explained? ✅ — [one sentence naming the cause-and-effect chain the viewer now understands]
"So what" delivered? ✅ — [one sentence on what understanding this changes for the viewer]

✅ Explainer confirmed.

[DAY] — FULL PACKAGE

Title:
[title — should be a question or a "Why/How/What Caused" framing] ([character count])

Description:
[2-3 sentences explaining what the video covers and why it matters, no filler, ends with series value prop]
Dark Chapters in History explains the dark side of history — why it happened, how it worked, and what it means. New entry every week.
#DarkChaptersInHistory #DarkHistory #HistoryExplained #HistoryFacts #HiddenHistory

Tags:
[comma-separated YouTube tags, series-specific + evergreen, no # symbols]

Pinned Comment:
[3-5 punchy sentences. State 3 key things the viewer now understands. End with: This is [series name]. New entry every week.]

TikTok Caption:
[5-7 short punchy sentences framed as explanation, not shock. End with 5 hashtags.]

Instagram Caption:
[Full script rewritten as caption with slightly more explanatory detail. End with 📖 and 5 hashtags.]

Thumbnail Image Prompt:
[Detailed AI image generation prompt. Illustrated style with high contrast. Grid of 4-6 illustrated portraits or items, each labeled. Bold question or "Why/How" text overlay. Dark background with warm accent highlights. DARK CHAPTERS IN HISTORY watermark bottom right.]

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
        "mon_short": f"""Write the complete Monday Short production package (Hook A — The Question) for: {name}{year_str}.

Content series: {series}
Content category: {category}
Topic summary: {summary}
{short_instructions}

MONDAY SCRIPT RULES:
- Hook A is THE QUESTION — open by posing the specific question this video answers, then immediately start answering it
- Do not tease the answer — begin explaining in sentence two
- Establish why the answer is darker or stranger than the viewer assumed
- Build through 3-4 cause-and-effect steps that explain the mechanism
- End CTA: "Full explanation this Sunday. This is {series}. New entry every week — follow."

Output the full production package following the SHORTS — FULL PRODUCTION PACKAGE FORMAT exactly.
Use Hook A — The Question as the hook type.
Monday as the day label throughout.""",

        "wed_short": f"""Write the complete Wednesday Short production package (Hook B — The Mechanism) for: {name}{year_str}.

Content series: {series}
Content category: {category}
Topic summary: {summary}
{short_instructions}

WEDNESDAY SCRIPT RULES:
- Hook B is THE MECHANISM — explain specifically HOW this dark thing worked, not just that it happened
- Open by naming the mechanism: "The way [X] actually worked was..."
- Walk through the process step by step — each sentence advances the explanation
- Include one specific named source, date, or document that proves this mechanism existed
- End CTA: "Full breakdown this Sunday. This is {series}. If you want the full explanation — follow."

Output the full production package following the SHORTS — FULL PRODUCTION PACKAGE FORMAT exactly.
Use Hook B — The Mechanism as the hook type.
Wednesday as the day label throughout.""",

        "fri_short": f"""Write the complete Friday Short production package (Hook C — The Implication) for: {name}{year_str}.

Content series: {series}
Content category: {category}
Topic summary: {summary}
{short_instructions}

FRIDAY SCRIPT RULES:
- Hook C is THE IMPLICATION — explain what understanding this topic reveals about the world more broadly
- Open with "What [topic] actually explains is..." or "The reason [topic] matters is..."
- Connect the specific dark history to a broader pattern, system, or human behaviour
- One specific analogy or comparison that makes the implication land
- End CTA: "Full explanation this Sunday. This is {series}. New entry every week — follow."

Output the full production package following the SHORTS — FULL PRODUCTION PACKAGE FORMAT exactly.
Use Hook C — The Implication as the hook type.
Friday as the day label throughout.""",

        "thu_pi": f"""Write the complete Thursday Pattern Interrupt Short production package for: {name}{year_str}.

IMPORTANT: This is STANDALONE. Works for a viewer who has never seen any other content on this topic.

Content category: {category}
Topic summary: {summary}
{short_instructions}

THURSDAY PI RULES:
- Opens with a specific factual question about the topic — then answers it immediately in sentence two
- No tease, no withholding — this is a mini explainer that delivers one complete idea in 60 seconds
- Context: one sentence on why most people don't know this
- Payoff: what the answer tells us about the broader subject
- Hook type: Quick Explainer

Output the full production package following the SHORTS — FULL PRODUCTION PACKAGE FORMAT exactly.
Use Hook D — Quick Explainer as the hook type.
Thursday as the day label throughout.""",

        "sat_pi": f"""Write the complete Saturday Pattern Interrupt Short production package for: {name}{year_str}.

IMPORTANT: This is STANDALONE. Different angle than Thursday's piece. No arc references.

Content series: {series}
Topic summary: {summary}
{short_instructions}

SATURDAY PI RULES:
- Opens by comparing two things the viewer thought were unrelated: "Most people think [X] and [Y] have nothing in common. They're wrong."
- Explain the specific connection, using precise dates, names, or mechanisms
- Land on what this comparison explains that neither subject reveals on its own
- Hook type: Unexpected Connection

Output the full production package following the SHORTS — FULL PRODUCTION PACKAGE FORMAT exactly.
Use Hook E — Unexpected Connection as the hook type.
Saturday as the day label throughout.""",

        "sun_longform": f"""Write the full long-form narration script for: {name}{year_str}.

Content series: {series}
Content category: {category}
Complexity tier: {case.complexity} ({COMPLEXITY_TIERS[case.complexity]['longform_minutes']} minutes)
Topic summary: {summary}
{extra_context}

STRUCTURE — DARK HISTORY EXPLAINER FORMAT

INTRO (30-45 sec)
- Open by posing the central question this video answers — specific and concrete
- State why the accepted answer is wrong, incomplete, or sanitised
- Tell the viewer exactly what they will understand by the end
- Do NOT open with "Today we're looking at..."

ACT 1 — WHAT PEOPLE THINK THEY KNOW
- The common version of this topic and where it came from
- What's technically true in the popular account
- The specific gap or assumption that needs explaining

ACT 2 — THE ACTUAL EXPLANATION
- The real mechanism, cause-and-effect chain, or suppressed context
- Primary sources: specific dates, named institutions, document titles
- Use analogies where they make a complex mechanism clearer
- Each section should answer a "but why?" question the previous section raised

ACT 3 — WHY IT WAS SIMPLIFIED (OR HIDDEN)
- Who simplified or suppressed the full explanation, and what they gained
- The cost of the simplified version — what understanding was lost
- What the full explanation changes about how we see the broader subject

OUTRO
- One-sentence answer to the original question — the clearest possible statement of what we now understand
- Series tag: "This is {series}."
- End: "Dark Chapters in History."

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
