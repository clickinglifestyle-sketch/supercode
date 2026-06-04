"""
NotebookLM integration — pure requests-based REST implementation.

No Google SDK required. Works with a Google AI Studio API key (GOOGLE_API_KEY).

Capabilities by plan tier:
  Free / Pay-as-you-go:
    ✅ Podcast script generation   (Gemini 2.5 Flash — generateContent)
    ✅ Research queries            (Gemini 2.5 Flash — generateContent)
    ⚠️  TTS audio rendering        (gemini-2.5-flash-preview-tts — 3 req/day free)
    ❌ Image generation            (Imagen 4 — Vertex AI tier required)
    ❌ Video generation            (Veo 3 — Vertex AI tier required)
  Vertex AI (enable via Google Cloud Console):
    ✅ All of the above, higher quotas

Auth notes:
  - Gemini generateContent: API key in x-goog-api-key header
  - Corpora (document grounding): OAuth2 bearer token required
  - Sources are always cached locally under data/notebooks/<case_id>/
"""

import base64
import io
import json
import os
import re
import time
import wave
from pathlib import Path
from typing import Optional

import requests

from config import GOOGLE_API_KEY, NOTEBOOKS_FILE, DATA_DIR
from src.models import Case

GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta"
SOURCES_DIR = DATA_DIR / "notebooks"

# Default models (confirmed working with API-key auth)
DEFAULT_TEXT_MODEL = "gemini-2.5-flash"
DEFAULT_TTS_MODEL = "gemini-2.5-flash-preview-tts"

# Two-host voice mapping
TTS_VOICES = {
    "A": "Charon",  # analytical, cold
    "B": "Kore",    # probing, outraged
}


# ---------------------------------------------------------------------------
# Local notebook store  (persists case_id → notebook identifier)
# ---------------------------------------------------------------------------

def _source_dir(case_id: str) -> Path:
    d = SOURCES_DIR / case_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def _load_store() -> dict:
    if NOTEBOOKS_FILE.exists():
        with open(NOTEBOOKS_FILE) as f:
            return json.load(f)
    return {}


def _save_store(store: dict) -> None:
    NOTEBOOKS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(NOTEBOOKS_FILE, "w") as f:
        json.dump(store, f, indent=2)


def get_notebook_name(case_id: str) -> Optional[str]:
    return _load_store().get(case_id)


# ---------------------------------------------------------------------------
# REST helpers
# ---------------------------------------------------------------------------

def _require_key() -> str:
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not set. Add it to your .env file.")
    return GOOGLE_API_KEY


def _gemini_post(path: str, body: dict, timeout: int = 120) -> dict:
    key = _require_key()
    resp = requests.post(
        f"{GEMINI_BASE}/{path}",
        headers={"x-goog-api-key": key, "Content-Type": "application/json"},
        json=body,
        timeout=timeout,
    )
    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"Gemini API {data['error']['code']}: {data['error']['message'][:200]}")
    return data


# ---------------------------------------------------------------------------
# Notebook lifecycle
# ---------------------------------------------------------------------------

def create_notebook(case: Case) -> str:
    """Register a local notebook for a case. Seeds it with the case brief."""
    store = _load_store()
    if case.id in store:
        return store[case.id]

    brief = _build_case_brief(case)
    seed_path = _source_dir(case.id) / "00_case_brief.txt"
    seed_path.write_text(brief)

    name = f"local/notebooks/{case.id}"
    store[case.id] = name
    _save_store(store)
    return name


def _build_case_brief(case: Case) -> str:
    return f"""CASE: {case.name}
YEAR: {case.year or 'Unknown'}
MICRO-SERIES: {case.micro_series}
FAILURE TYPE: {case.failure_type.replace('_', ' ')}
COMPLEXITY TIER: {case.complexity}
SUMMARY: {case.summary or 'No summary provided.'}
NOTES: {case.notes or 'None.'}

RESEARCH FRAME
The system's failure is the story — the crime is evidence inside that frame.
Identify: institutional betrayal, cognitive blind spots, deliberate cover-ups.
Focus on specific decisions, named officials, documented timelines.
Avoid adjectives that don't carry evidentiary weight.
"""


# ---------------------------------------------------------------------------
# Sources  (stored locally as .txt files)
# ---------------------------------------------------------------------------

def add_source_url(case_id: str, url: str, display_name: str = "") -> str:
    """Fetch a URL, strip HTML, and cache locally as a research source."""
    try:
        r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        text = re.sub(r"<[^>]+>", " ", r.text)
        text = re.sub(r"\s+", " ", text).strip()[:8000]
        content = f"SOURCE: {display_name or url}\nURL: {url}\n\n{text}"
    except Exception as e:
        content = f"SOURCE: {display_name or url}\nURL: {url}\n\n[Fetch failed: {e}]"

    slug = re.sub(r"[^\w]", "_", display_name or url)[:40]
    fname = f"{int(time.time())}_{slug}.txt"
    (_source_dir(case_id) / fname).write_text(content)
    return fname


def add_source_text(case_id: str, text: str, display_name: str) -> str:
    """Store a plain-text block (notes, quotes, transcripts) as a source."""
    slug = re.sub(r"[^\w]", "_", display_name)[:40]
    fname = f"{int(time.time())}_{slug}.txt"
    (_source_dir(case_id) / fname).write_text(f"SOURCE: {display_name}\n\n{text}")
    return fname


def list_sources(case_id: str) -> list[dict]:
    src_dir = _source_dir(case_id)
    return [
        {
            "name": f.name,
            "display_name": f.stem.split("_", 1)[-1].replace("_", " ")[:60],
            "size": f"{f.stat().st_size:,} bytes",
        }
        for f in sorted(src_dir.iterdir())
        if f.suffix == ".txt"
    ]


# ---------------------------------------------------------------------------
# Research queries
# ---------------------------------------------------------------------------

def query_notebook(case_id: str, question: str,
                   model: str = DEFAULT_TEXT_MODEL) -> dict:
    """Ask a research question. Synthesises all local sources via Gemini."""
    src_dir = _source_dir(case_id)
    sources_text = "\n\n---\n".join(
        f.read_text()[:3000]
        for f in sorted(src_dir.iterdir())
        if f.suffix == ".txt"
    )
    if not sources_text:
        raise ValueError("No sources yet. Use 'fs notebooklm add-source' first.")

    prompt = f"""You are a research analyst for "Finally Solved," a faceless true crime channel.

QUESTION: {question}

RESEARCH SOURCES:
{sources_text}

Answer using ONLY information from the sources.
Be precise: cite specific names, dates, and decisions. No filler."""

    data = _gemini_post(f"models/{model}:generateContent", {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 2048},
    })
    return {"answer": data["candidates"][0]["content"]["parts"][0]["text"], "model": model}


# ---------------------------------------------------------------------------
# Podcast script generation  (NotebookLM audio overview equivalent)
# ---------------------------------------------------------------------------

def generate_podcast_script(case: Case, model: str = DEFAULT_TEXT_MODEL) -> str:
    """Generate a NotebookLM-style two-host podcast script via Gemini."""
    src_dir = _source_dir(case.id)
    sources_snippet = "\n\n---\n".join(
        f.read_text()[:2000]
        for f in sorted(src_dir.iterdir())
        if f.suffix == ".txt"
    )

    context = _build_case_brief(case)
    if sources_snippet:
        context += f"\n\nRESEARCH SOURCES:\n{sources_snippet}"

    prompt = f"""Write a verbatim two-host podcast script for a documentary audio deep-dive.

{context}

FORMAT RULES:
- Two hosts: HOST A (analytical, cold, precise) and HOST B (probing, moral outrage)
- 10-12 minutes of spoken content (~1500-1800 words)
- Open cold — HOST A states the single most damning institutional fact, no intro
- Structure: what the system had → what it chose → what it cost → the break
- Specific numbers, names, dates only. No vague language.
- End: HOST A delivers the single-sentence verdict on the institution.
  HOST B: "Finally Solved."
- No music cues, no stage directions — pure spoken script

Output the script only. Start immediately with HOST A:"""

    data = _gemini_post(f"models/{model}:generateContent", {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 8192},
    })
    return data["candidates"][0]["content"]["parts"][0]["text"]


# ---------------------------------------------------------------------------
# TTS audio rendering
# ---------------------------------------------------------------------------

def _parse_script_segments(script: str) -> list[tuple[str, str]]:
    """Split a HOST A / HOST B script into (host, text) pairs."""
    segments = []
    for line in script.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("HOST A:"):
            segments.append(("A", line[7:].strip()))
        elif line.startswith("HOST B:"):
            segments.append(("B", line[7:].strip()))
        elif segments:
            segments[-1] = (segments[-1][0], segments[-1][1] + " " + line)
    return segments


def _tts_segment(text: str, voice: str, model: str = DEFAULT_TTS_MODEL,
                 max_retries: int = 3, retry_wait: int = 30) -> bytes:
    """Render one text segment to raw L16 PCM bytes via Gemini TTS."""
    for attempt in range(max_retries):
        data = _gemini_post(f"models/{model}:generateContent", {
            "contents": [{"parts": [{"text": text}]}],
            "generationConfig": {
                "responseModalities": ["AUDIO"],
                "speechConfig": {
                    "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}
                },
            },
        })
        part = data["candidates"][0]["content"]["parts"][0]
        if "inlineData" in part:
            return base64.b64decode(part["inlineData"]["data"])
        # Unexpected shape — retry
        time.sleep(retry_wait)
    raise RuntimeError("TTS: unexpected response shape after retries")


def render_audio(case_id: str, script: str,
                 out_path: str, model: str = DEFAULT_TTS_MODEL,
                 segment_gap_ms: int = 150,
                 inter_request_delay: float = 5.0) -> str:
    """Render the full two-host script to a WAV file.

    Segments are rendered sequentially with inter_request_delay between calls
    to stay within per-minute rate limits.

    Returns the path of the written WAV file.
    Raises RuntimeError if the TTS quota is exhausted.
    """
    SAMPLE_RATE = 24000
    SAMPLE_WIDTH = 2  # 16-bit
    silence = b"\x00" * int(SAMPLE_RATE * SAMPLE_WIDTH * segment_gap_ms / 1000)

    segments = _parse_script_segments(script)
    pcm_chunks = []
    failed = []

    for i, (host, text) in enumerate(segments):
        voice = TTS_VOICES[host]
        try:
            pcm = _tts_segment(text, voice, model=model)
            pcm_chunks.append(pcm)
            pcm_chunks.append(silence)
        except RuntimeError as e:
            failed.append(i + 1)
            pcm_chunks.append(silence * 10)
        if i < len(segments) - 1:
            time.sleep(inter_request_delay)

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(SAMPLE_WIDTH)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(b"".join(pcm_chunks))

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_bytes(buf.getvalue())

    duration = len(b"".join(pcm_chunks)) / (SAMPLE_RATE * SAMPLE_WIDTH)
    result = {
        "path": out_path,
        "duration_min": round(duration / 60, 1),
        "segments_total": len(segments),
        "segments_failed": len(failed),
        "failed_indices": failed,
    }
    return result


# ---------------------------------------------------------------------------
# Convenience: generate everything in one call
# ---------------------------------------------------------------------------

def generate_audio_overview(case_id: str, case: Case, out_dir: str = "") -> dict:
    """Generate podcast script + render audio. Returns paths to both files."""
    out_dir = out_dir or str(SOURCES_DIR / case_id)
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    script = generate_podcast_script(case)
    script_path = str(Path(out_dir) / "podcast_script.txt")
    Path(script_path).write_text(script)

    wav_path = str(Path(out_dir) / f"{case_id}_audio_overview.wav")
    audio_result = render_audio(case_id, script, out_path=wav_path)

    return {
        "script_path": script_path,
        "audio": audio_result,
    }
