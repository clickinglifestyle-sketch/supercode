import json
import time
from pathlib import Path
from typing import Optional

from config import GOOGLE_API_KEY, NOTEBOOKS_FILE
from src.models import Case


# ---------------------------------------------------------------------------
# Notebook store  (persists case_id → notebook resource name)
# ---------------------------------------------------------------------------

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
    """Return the NotebookLM resource name for a case, or None."""
    return _load_store().get(case_id)


# ---------------------------------------------------------------------------
# Client factory
# ---------------------------------------------------------------------------

def _client():
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not set. Add it to your .env file.")
    from google import genai
    return genai.Client(api_key=GOOGLE_API_KEY)


# ---------------------------------------------------------------------------
# Notebook lifecycle
# ---------------------------------------------------------------------------

def create_notebook(case: Case) -> str:
    """Create a NotebookLM notebook for a case and return its resource name.

    Seeds the notebook with a structured case brief so every query has
    the Finally Solved frame baked in from the start.
    """
    store = _load_store()
    if case.id in store:
        return store[case.id]

    client = _client()
    from google.genai import types

    title = f"Finally Solved — {case.name}"
    if case.year:
        title += f" ({case.year})"

    notebook = client.notebooks.create(display_name=title)

    seed = _build_case_brief(case)
    client.notebooks.sources.create(
        parent=notebook.name,
        display_name="Case Brief",
        source=types.Source(text=types.TextSource(content=seed)),
    )

    store[case.id] = notebook.name
    _save_store(store)
    return notebook.name


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
# Sources
# ---------------------------------------------------------------------------

def add_source_url(notebook_name: str, url: str, display_name: str = "") -> str:
    """Add a web URL as a source. Returns the new source resource name."""
    client = _client()
    from google.genai import types

    source = client.notebooks.sources.create(
        parent=notebook_name,
        display_name=display_name or url,
        source=types.Source(url=types.UrlSource(url=url)),
    )
    return source.name


def add_source_text(notebook_name: str, text: str, display_name: str) -> str:
    """Add a plain-text source (notes, transcripts, quotes). Returns source name."""
    client = _client()
    from google.genai import types

    source = client.notebooks.sources.create(
        parent=notebook_name,
        display_name=display_name,
        source=types.Source(text=types.TextSource(content=text)),
    )
    return source.name


def list_sources(notebook_name: str) -> list[dict]:
    """Return all sources in a notebook as plain dicts."""
    client = _client()
    results = []
    for s in client.notebooks.sources.list(parent=notebook_name):
        results.append({
            "name": s.name,
            "display_name": getattr(s, "display_name", ""),
            "create_time": str(getattr(s, "create_time", "")),
        })
    return results


# ---------------------------------------------------------------------------
# Research queries
# ---------------------------------------------------------------------------

def query_notebook(notebook_name: str, question: str) -> dict:
    """Ask a research question. Returns {answer, citations}."""
    client = _client()
    response = client.notebooks.query(name=notebook_name, query=question)
    return {
        "answer": getattr(response, "answer", str(response)),
        "citations": getattr(response, "citations", []),
    }


# ---------------------------------------------------------------------------
# Audio overview
# ---------------------------------------------------------------------------

def generate_audio_overview(notebook_name: str, timeout: int = 120) -> bytes:
    """Generate a podcast-style audio overview. Returns raw audio bytes.

    Polls until the long-running operation completes or timeout is reached.
    """
    client = _client()
    operation = client.notebooks.generate_audio_overview(name=notebook_name)

    deadline = time.monotonic() + timeout
    while not getattr(operation, "done", False):
        if time.monotonic() > deadline:
            raise TimeoutError(f"Audio generation did not finish within {timeout}s.")
        time.sleep(4)
        operation = client.operations.get(name=operation.name)

    if getattr(operation, "error", None):
        raise RuntimeError(f"Audio generation failed: {operation.error.message}")

    notebook = operation.response
    return notebook.audio_overview.audio_content
