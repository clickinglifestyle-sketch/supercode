import json
import uuid
from typing import Optional
from config import CASES_FILE, ASSET_STAGES, WEEKLY_SLOTS
from src.models import Case, Asset


def _load_cases() -> list[Case]:
    if not CASES_FILE.exists():
        return []
    with open(CASES_FILE) as f:
        raw = json.load(f)
    return [Case.from_dict(d) for d in raw]


def _save_cases(cases: list[Case]) -> None:
    CASES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CASES_FILE, "w") as f:
        json.dump([c.to_dict() for c in cases], f, indent=2)


def list_cases() -> list[Case]:
    return _load_cases()


def get_case(case_id: str) -> Optional[Case]:
    for c in _load_cases():
        if c.id == case_id:
            return c
    return None


def add_case(
    name: str,
    complexity: str,
    micro_series: str,
    failure_type: str,
    summary: str = "",
    year: Optional[int] = None,
    notes: str = "",
) -> Case:
    cases = _load_cases()
    case_id = name.lower().replace(" ", "-").replace("'", "")[:30]
    # Ensure uniqueness
    existing_ids = {c.id for c in cases}
    base_id = case_id
    counter = 1
    while case_id in existing_ids:
        case_id = f"{base_id}-{counter}"
        counter += 1

    case = Case(
        id=case_id,
        name=name,
        complexity=complexity,
        micro_series=micro_series,
        failure_type=failure_type,
        summary=summary,
        year=year,
        notes=notes,
    )
    cases.append(case)
    _save_cases(cases)
    return case


def update_case(case_id: str, **kwargs) -> Optional[Case]:
    cases = _load_cases()
    for i, c in enumerate(cases):
        if c.id == case_id:
            for key, val in kwargs.items():
                if hasattr(c, key):
                    setattr(c, key, val)
            _save_cases(cases)
            return c
    return None


def advance_asset(case_id: str, slot: str) -> tuple[Optional[Case], str]:
    cases = _load_cases()
    for i, c in enumerate(cases):
        if c.id == case_id:
            if slot not in c.assets:
                return None, f"Slot '{slot}' not found"
            asset = c.assets[slot]
            old_stage = asset.stage
            advanced = asset.advance()
            if advanced:
                _save_cases(cases)
                return c, f"{slot}: {old_stage} → {asset.stage}"
            else:
                return c, f"{slot} already at final stage: {asset.stage}"
    return None, f"Case '{case_id}' not found"
