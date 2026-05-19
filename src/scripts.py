import anthropic
from config import ANTHROPIC_API_KEY, COMPLEXITY_TIERS
from src.models import Case

# ---------------------------------------------------------------------------
# Channel voice & system prompt  (cached — stable across all requests)
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a script writer for "Finally Solved," a faceless true crime YouTube channel.

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

FIVE MICRO-SERIES (reference when assigning a script)
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
- No music cues, no [B-roll suggestions], no stage directions — pure narration script

OUTPUT FORMAT
Return only the narration script. No preamble, no "Here is the script:", no metadata. Start immediately with the first spoken word.
"""

# ---------------------------------------------------------------------------
# Per-slot user prompt templates
# ---------------------------------------------------------------------------

def _slot_prompt(slot: str, case: Case, extra_context: str = "") -> str:
    name = case.name
    summary = case.summary or f"a {case.complexity}-layer true crime case"
    series = case.micro_series
    failure = case.failure_type.replace("_", " ")
    year_str = f" ({case.year})" if case.year else ""

    prompts = {
        "mon_short": f"""Write a 60-second Monday Short (Arc 1) for the case: {name}{year_str}.

Micro-series: {series}
Failure type: {failure}
Case summary: {summary}
{extra_context}

STRUCTURE
- Open with ONE specific systemic failure fact — the most damning number or institutional decision
- Introduce the case in 1-2 sentences (victim name, what happened, when)
- Establish the institutional failure angle
- End exactly with a variation of: "[X] people reported it. No one listened. Wednesday."

Length: approx 150-170 words spoken (60 seconds at 150 wpm)""",

        "wed_short": f"""Write a 60-second Wednesday Short (Arc 2) for the case: {name}{year_str}.

Micro-series: {series}
Failure type: {failure}
Case summary: {summary}
{extra_context}

STRUCTURE
- Open by escalating the failure introduced Monday
- Reveal the specific institutional decision that deepened the failure (name the agency, the year, the choice)
- Show the consequence of that decision on the case
- End exactly with a variation of: "They had everything. They still looked away. Friday."

Length: approx 150-170 words spoken (60 seconds at 150 wpm)""",

        "fri_short": f"""Write a 60-second Friday Short (Arc 3) for the case: {name}{year_str}.

Micro-series: {series}
Failure type: {failure}
Case summary: {summary}
{extra_context}

STRUCTURE
- Open by naming what finally broke through — the specific person, technology, or event that changed everything
- Contrast it sharply with how long the failure lasted
- Build urgency toward the full case
- End exactly with: "Full case drops Sunday. You need to see this."

Length: approx 150-170 words spoken (60 seconds at 150 wpm)""",

        "thu_pi": f"""Write a 60-second Thursday Pattern Interrupt Short for the case: {name}{year_str}.

IMPORTANT: This is a STANDALONE piece. Do NOT reference "Monday" or "the arc." It must work for a viewer who has never seen any other piece about this case.

Failure type for this angle: {failure}
Case summary: {summary}
{extra_context}

STRUCTURE
- Open with a psychological principle or cognitive bias (name it precisely)
- Apply it to this case as a concrete example — specific detail, specific moment
- Zoom out to the systemic implication: why this pattern recurs across institutions
- NO call to action, no "subscribe," no arc reference

Length: approx 150-170 words spoken (60 seconds at 150 wpm)""",

        "sat_pi": f"""Write a 60-second Saturday Pattern Interrupt Short for the case: {name}{year_str}.

IMPORTANT: This is a STANDALONE piece. Do NOT reference any other day's content. Different psychological dimension than Thursday's piece.

Case summary: {summary}
Micro-series: {series}
{extra_context}

STRUCTURE
- Open with an algorithm-hook question or statement — something that stops the scroll
- Pivot immediately to a different psychological principle than Thursday's (authority bias, sunk cost fallacy, in-group protection, etc.)
- Ground it in a specific detail from this case
- End with the systemic implication — no resolution, no wrap-up

Length: approx 150-170 words spoken (60 seconds at 150 wpm)""",

        "sun_longform": f"""Write the full long-form script for the case: {name}{year_str}.

Micro-series: {series}
Failure type: {failure}
Complexity tier: {case.complexity} ({COMPLEXITY_TIERS[case.complexity]['longform_minutes']} minutes)
Case summary: {summary}
{extra_context}

STRUCTURE — THREE-LAYER DOCUMENTARY FORMAT

INTRO HOOK (30-45 sec)
- Open with the most disturbing systemic fact about this case — a specific number, date, or institutional failure
- Do NOT open with the crime itself
- State the case name and the core question: "Why did it take so long for justice to arrive?"

LAYER 1 — THE CRIME AND "THEY HAD IT" (establish what happened AND what the system already knew)
- What happened to the victim
- What evidence existed from day one
- What the system had — specific documents, witnesses, data points

LAYER 2 — THE FAILURE AND "THEY LOOKED AWAY" (the institutional failure in detail)
- The specific decisions that buried the case
- Who made them, when, what they chose instead
- The cost: years lost, harm done

LAYER 3 — THE BREAK AND "WHAT FINALLY WORKED" (what changed and why)
- The specific person, technology, or moment that cracked it
- The final reckoning — conviction, exoneration, or ongoing fight
- Why it took exactly as long as it did

OUTRO
- One-sentence verdict on the institution
- Micro-series tag: "This is [micro-series name]."
- No call to subscribe, no "see you next week"

Target word count for {case.complexity} tier: {'4500-5500' if case.complexity == 'triple' else '3000-3500' if case.complexity == 'double' else '2000-2500'} words""",
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
                "cache_control": {"type": "ephemeral"},  # cache the long stable system prompt
            }
        ],
        messages=[{"role": "user", "content": user_prompt}],
    )

    text_blocks = [b.text for b in response.content if b.type == "text"]
    return "\n".join(text_blocks).strip()
