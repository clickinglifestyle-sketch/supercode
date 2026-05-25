import anthropic
from config import (
    ANTHROPIC_API_KEY, COMPLEXITY_TIERS,
    TAGS_TIER1, TAGS_TIER2, TAGS_BY_MICRO_SERIES, TAGS_BY_FAILURE_TYPE, TAGS_BRAND,
)
from src.models import Case

# ---------------------------------------------------------------------------
# Channel voice & system prompt  (cached — stable across all requests)
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a full production writer for "Finally Solved," a faceless true crime YouTube channel.

CHANNEL IDENTITY
- Analytical, cold, precise — NOT sensational
- The disturbing thread: the system is scarier than the crime
- Viewer should feel betrayed by the institution, not just horrified by the killer
- Open with the most disturbing systemic fact, not the crime itself
- No filler phrases: never start with "Today we're looking at...", "Let's dive in...", "Welcome back...", or "In this video..."
- Numbers must be specific: "23 years" not "decades," "14 detectives" not "many"

STRUCTURAL RULES
- Every script opens cold — straight into the most damning systemic detail
- The system's failure is always the frame; the crime is the evidence inside that frame
- Each piece must make the viewer angry at an institution, not just sad about a victim

FIVE MICRO-SERIES
1. The Evidence Was There — police/prosecutors had proof and ignored it
2. They Called It an Accident — murder misclassified to close the case
3. Caught By One Mistake — killer's single error after years of evasion
4. They Got The Wrong Person — wrongful conviction buried the real perpetrator
5. The System Knew — institutions protected the killer

THREE FAILURE TYPES
- Institutional failure: bureaucratic negligence, turf wars, underfunding, bad policy
- Cognitive blind spot: confirmation bias, tunnel vision, pattern mismatch
- Deliberate betrayal: active cover-up, complicity, corruption

VOICE CALIBRATION
- Cut every adjective that doesn't carry load
- Passive voice is forbidden for the killer's actions; use it only when describing institutional inaction
- Sentences under 15 words when building tension
- Rhetorical questions only at the very end of a segment, not mid-section
- No music cues, no [B-roll suggestions], no stage directions — pure narration

SHORTS — FULL PRODUCTION PACKAGE FORMAT
For every Short (Monday, Wednesday, Friday, Thursday PI, Saturday PI), output the complete
production package in this exact structure with these exact section headers:

[SLOT LABEL] — [CASE NAME]
Hook [Letter] — [Hook Type]

SCRIPT:
[narration — 150-170 words, 60 seconds]

THREE LAYER OUTRAGE CHECK — [DAY]

Duration of injustice? ✅ — [one sentence]
Specific failure point? ✅ — [one sentence naming the institution, decision, and consequence]
Absurdity amplifier? ✅ — [the single most absurd detail in quotes, then what it means]

✅ Superior hook confirmed.

[DAY] — FULL PACKAGE

Title:
[title] ([character count])

Description:
[2-3 sentence documentary description, no filler, ends with channel value prop sentence]
Finally Solved names the exact decision that let a killer walk free — and proves that justice delayed is a choice somebody made.
#FinallySolved #ColdCase #TrueCrime #ColdCaseSolved #JusticeServed

Tags:
[comma-separated YouTube tags, case-specific + evergreen, no # symbols]

Pinned Comment:
[3-5 punchy sentences. Restate the 3 key failures as facts. End with: Follow — we cover cases like this every week.]

TikTok Caption:
[5-7 short punchy sentences. Facts only. End with 5 hashtags.]

Instagram Caption:
[Full script rewritten as caption — slightly more detail than TikTok. End with 🔍 and 5 hashtags.]

Thumbnail Image Prompt:
[Detailed AI image generation prompt. Split-panel composition with torn paper divider. Left panel: warm amber, aged photograph of victim or key evidence. Right panel: cold blue institutional scene. Bold white number/stat top left. Bold red revelation text bottom right. FINALLY SOLVED watermark bottom right.]

LONG-FORM — NARRATION ONLY
For Sunday long-form scripts, output narration only. No metadata. Start immediately with the first spoken word.
"""

# ---------------------------------------------------------------------------
# Evergreen tag base — injected into every Short package
# ---------------------------------------------------------------------------

def _base_tags() -> str:
    base = (
        TAGS_TIER1[:6]
        + ["cold case solved", "cold cases solved", "cold case breakthrough",
           "truth revealed", "finally solved cold case", "justice delayed",
           "missing person found", "murder solved years later"]
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
    summary = case.summary or f"a {case.complexity}-layer true crime case"
    series = case.micro_series
    failure = case.failure_type.replace("_", " ")
    year_str = f" ({case.year})" if case.year else ""
    base_tags = _base_tags()
    case_tags = _case_tags(case)
    all_tags = f"{base_tags}, {case_tags}"

    short_instructions = f"""
EVERGREEN TAGS TO INCLUDE IN THE TAGS SECTION (add case-specific terms on top):
{all_tags}

{extra_context}
"""

    prompts = {
        "mon_short": f"""Write the complete Monday Short production package (Hook A — Outrage) for: {name}{year_str}.

Micro-series: {series}
Failure type: {failure}
Case summary: {summary}
{short_instructions}

MONDAY SCRIPT RULES:
- Hook A is OUTRAGE — the viewer should feel immediate institutional betrayal
- Open with the most damning number or institutional decision in the case
- Introduce the case in 1-2 sentences
- Build through 3-4 escalating failure facts
- End CTA: "Full story dropping soon. We cover cases like this every week — start with any video on the channel. If that doesn't sit right with you — follow."

Output the full production package following the SHORTS — FULL PRODUCTION PACKAGE FORMAT exactly.
Use Hook A — Outrage as the hook type.
Monday as the day label throughout.""",

        "wed_short": f"""Write the complete Wednesday Short production package (Hook B — Disbelief) for: {name}{year_str}.

Micro-series: {series}
Failure type: {failure}
Case summary: {summary}
{short_instructions}

WEDNESDAY SCRIPT RULES:
- Hook B is DISBELIEF — the viewer should feel the system actively worked against victims
- Open mid-story — reference a victim's experience or a specific official decision
- Reveal the specific institutional mechanism that made the failure worse
- Include one victim quote or documented institutional statement
- End CTA: "Full story dropping soon. Cases like this are already on the channel. If that doesn't make sense to you — follow. It gets worse."

Output the full production package following the SHORTS — FULL PRODUCTION PACKAGE FORMAT exactly.
Use Hook B — Disbelief as the hook type.
Wednesday as the day label throughout.""",

        "fri_short": f"""Write the complete Friday Short production package (Hook C — Curiosity Gap) for: {name}{year_str}.

Micro-series: {series}
Failure type: {failure}
Case summary: {summary}
{short_instructions}

FRIDAY SCRIPT RULES:
- Hook C is CURIOSITY GAP — the viewer must need to know what happened
- Open with the re-arrest, re-opening, or break in the case
- Build through the final failure (something that should have prevented the end outcome but didn't)
- Land on the accountability gap — what punishment actually looked like vs. what it should have been
- End CTA: "Full story dropping soon. If you can't wait — there are cases on the channel right now that will keep you up tonight. If you need to know what the system was protecting — follow."

Output the full production package following the SHORTS — FULL PRODUCTION PACKAGE FORMAT exactly.
Use Hook C — Curiosity Gap as the hook type.
Friday as the day label throughout.""",

        "thu_pi": f"""Write the complete Thursday Pattern Interrupt Short production package for: {name}{year_str}.

IMPORTANT: This is STANDALONE. No arc references. Works for a viewer who has never seen any other content about this case.

Failure type: {failure}
Case summary: {summary}
{short_instructions}

THURSDAY PI RULES:
- Opens with a psychological principle or cognitive bias named precisely
- Applies it to one specific moment in this case
- Zooms out to the systemic implication — why this pattern recurs
- No CTA to "follow the arc" — this piece stands alone
- Hook type: Psychological Hook

Output the full production package following the SHORTS — FULL PRODUCTION PACKAGE FORMAT exactly.
Use Hook D — Psychological Hook as the hook type.
Thursday as the day label throughout.""",

        "sat_pi": f"""Write the complete Saturday Pattern Interrupt Short production package for: {name}{year_str}.

IMPORTANT: This is STANDALONE. Different psychological angle than Thursday's piece. No arc references.

Micro-series: {series}
Case summary: {summary}
{short_instructions}

SATURDAY PI RULES:
- Opens with an algorithm-stopping question or statement
- Uses a DIFFERENT psychological principle than Thursday (authority bias, sunk cost, in-group protection, etc.)
- Grounds it in a specific detail from this case
- Ends on the systemic implication — no resolution
- Hook type: Pattern Interrupt

Output the full production package following the SHORTS — FULL PRODUCTION PACKAGE FORMAT exactly.
Use Hook E — Pattern Interrupt as the hook type.
Saturday as the day label throughout.""",

        "sun_longform": f"""Write the full long-form narration script for: {name}{year_str}.

Micro-series: {series}
Failure type: {failure}
Complexity tier: {case.complexity} ({COMPLEXITY_TIERS[case.complexity]['longform_minutes']} minutes)
Case summary: {summary}
{extra_context}

STRUCTURE — THREE-LAYER DOCUMENTARY FORMAT

INTRO HOOK (30-45 sec)
- Open with the most disturbing systemic fact — a specific number, date, or institutional failure
- Do NOT open with the crime itself
- State the case name and the core question: why did it take so long

LAYER 1 — THE CRIME AND "THEY HAD IT"
- What happened to the victim
- What evidence existed from day one
- What the system already had

LAYER 2 — THE FAILURE AND "THEY LOOKED AWAY"
- The specific decisions that buried the case
- Who made them, when, what they chose instead
- The cost: years lost, harm done

LAYER 3 — THE BREAK AND "WHAT FINALLY WORKED"
- The specific person, technology, or moment that cracked it
- The final reckoning
- Why it took exactly as long as it did

OUTRO
- One-sentence verdict on the institution
- Micro-series tag: "This is [micro-series name]."
- End: "Finally Solved."

Target word count: {'4500-5500' if case.complexity == 'triple' else '3000-3500' if case.complexity == 'double' else '2000-2500'} words

Output narration only. No metadata. No preamble. Start immediately with the first spoken word.""",
    }

    return prompts.get(slot, f"Write a script for slot '{slot}' for the case: {name}.")


# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------

def generate_script(case: Case, slot: str, extra_context: str = "") -> str:
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY not set. Add it to your .env file.")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    user_prompt = _slot_prompt(slot, case, extra_context)

    response = client.messages.create(
        model="claude-opus-4-7",
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
