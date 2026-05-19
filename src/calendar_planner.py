import json
from datetime import date, timedelta
from typing import Optional
from config import WEEKLY_SLOTS
from src.models import Case
from src.pipeline import _load_cases, _save_cases

# Day-of-week index for each slot (Monday=0 ... Sunday=6)
SLOT_DAY = {
    "mon_short": 0,
    "wed_short": 2,
    "thu_pi": 3,
    "fri_short": 4,
    "sat_pi": 5,
    "sun_longform": 6,
}

SLOT_LABELS = {
    "mon_short": "Mon Short (Arc 1)",
    "wed_short": "Wed Short (Arc 2)",
    "thu_pi": "Thu Pattern Interrupt",
    "fri_short": "Fri Short (Arc 3)",
    "sat_pi": "Sat Pattern Interrupt",
    "sun_longform": "Sun Long-form",
}


def _next_monday(from_date: Optional[date] = None) -> date:
    d = from_date or date.today()
    days_ahead = (7 - d.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    return d + timedelta(days=days_ahead)


def plan_week(case_id: str, start_date_str: str) -> dict:
    """
    Assign a case to a week's worth of slots.
    start_date_str: ISO format date string for the Monday of that week.
    Returns a dict mapping slot -> publish_date.
    """
    cases = _load_cases()
    case = next((c for c in cases if c.id == case_id), None)
    if not case:
        return {}

    monday = date.fromisoformat(start_date_str)
    schedule = {}
    for slot, day_offset in SLOT_DAY.items():
        publish_date = monday + timedelta(days=day_offset)
        schedule[slot] = publish_date.isoformat()

    # Store schedule in case notes (simple approach without separate calendar store)
    schedule_note = f"SCHEDULE: " + ", ".join(f"{s}={d}" for s, d in schedule.items())
    case.notes = schedule_note
    _save_cases(cases)
    return schedule


def get_four_week_calendar() -> list[dict]:
    """
    Returns a 4-week view starting from the next Monday.
    Each week entry: {"week_start": date_str, "slots": [{slot, label, date, case_id, case_name, stage}]}
    """
    cases = _load_cases()
    case_schedules: dict[str, dict] = {}

    for c in cases:
        if c.notes and c.notes.startswith("SCHEDULE:"):
            parts = c.notes.replace("SCHEDULE:", "").strip().split(", ")
            sched = {}
            for part in parts:
                if "=" in part:
                    slot, d = part.split("=", 1)
                    sched[slot.strip()] = d.strip()
            case_schedules[c.id] = sched

    monday = _next_monday()
    weeks = []
    for week_offset in range(4):
        week_start = monday + timedelta(weeks=week_offset)
        slots_info = []
        for slot, day_offset in SLOT_DAY.items():
            slot_date = week_start + timedelta(days=day_offset)
            slot_date_str = slot_date.isoformat()

            assigned_case = None
            assigned_stage = None
            for c in cases:
                cid = c.id
                if cid in case_schedules:
                    if case_schedules[cid].get(slot) == slot_date_str:
                        assigned_case = c
                        assigned_stage = c.assets.get(slot)
                        break

            slots_info.append({
                "slot": slot,
                "label": SLOT_LABELS[slot],
                "date": slot_date_str,
                "case_id": assigned_case.id if assigned_case else None,
                "case_name": assigned_case.name if assigned_case else None,
                "stage": assigned_stage.stage if assigned_stage else None,
            })

        weeks.append({"week_start": week_start.isoformat(), "slots": slots_info})

    return weeks
