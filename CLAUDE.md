# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

**Finally Solved** is a CLI production tool for a faceless true-crime YouTube channel. It manages the full content pipeline: cases (research subjects), per-asset production stages, weekly content calendar, AI script generation via Claude, and Reddit distribution tracking.

## Setup & Running

```bash
pip install -e .          # installs `fs` CLI entry point
cp .env.example .env      # add ANTHROPIC_API_KEY
```

Run as either `fs <command>` (after `pip install -e .`) or `python main.py <command>`.

## Common Commands

```bash
fs dashboard                          # channel stats, YPP countdown, velocity needed
fs cases list                         # show all cases with per-slot stage grid
fs cases add                          # interactive: create a new case
fs cases show <case-id>               # full detail + asset stage table
fs cases advance <case-id> <slot>     # advance one asset to next stage
fs scripts generate <case-id> <slot>  # call Claude API to generate a script
fs calendar show                      # 4-week content calendar view
fs calendar plan-week <case-id> <monday-date>  # assign case to a week
fs reddit log                         # interactive: log a Reddit post
fs reddit schedule                    # upcoming schedule + post history + stats
```

Valid `<slot>` values: `mon_short`, `wed_short`, `thu_pi`, `fri_short`, `sat_pi`, `sun_longform`

## Architecture

### Data model
- **`Case`** (`src/models.py`) — the central entity. Each case has metadata (name, year, complexity tier, micro-series, failure type) and six `Asset` objects, one per weekly slot.
- **`Asset`** — tracks production stage for a single slot. Stages advance linearly: `idea → research → scripted → voiced → edited → scheduled → published`.
- **`RedditPost`** — independent entity tracking Reddit distribution.
- All data is persisted as flat JSON files in `data/`: `cases.json` and `reddit_log.json`.

### Module responsibilities
| File | Role |
|---|---|
| `config.py` | All hardcoded constants: channel stats, YPP targets, slot names, stage list, micro-series, etc. **Update `CURRENT_SUBS`, `CURRENT_VIEWS`, `CURRENT_VIDEOS` manually as the channel grows.** |
| `main.py` | CLI layer only — Click command definitions with `rich` rendering. No business logic here. |
| `src/pipeline.py` | CRUD for cases: load/save JSON, add/get/update/advance. |
| `src/scripts.py` | Claude API integration. System prompt is sent with `cache_control: ephemeral` to enable prompt caching across calls. |
| `src/calendar_planner.py` | Week scheduling. Schedule data is stored inside `Case.notes` as a `SCHEDULE: slot=date, ...` string (not a separate data store). |
| `src/dashboard.py` | Pure calculation from `config.py` constants — no I/O. |
| `src/reddit.py` | Reddit post log CRUD (parallel to pipeline.py). |

### Content structure
Each case maps to one week of content (6 pieces):
- Mon/Wed/Fri shorts form a narrative arc (Arc 1 / Arc 2 / Arc 3)
- Thu/Sat are standalone "pattern interrupt" shorts (no arc references)
- Sun is the full long-form documentary

The `complexity` tier (`single` / `double` / `triple`) controls the long-form target length and number of failure layers.

### Script generation
`fs scripts generate` calls `claude-opus-4-7` with a large stable system prompt (cached) plus a slot-specific user prompt. The system prompt encodes the channel's editorial voice — analytical, institutional-failure framing, no filler phrases, specific numbers over vague language.
