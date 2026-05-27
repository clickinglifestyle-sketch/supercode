#!/usr/bin/env python3
import sys
import click
from datetime import date
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich import box
from rich.text import Text
from rich.progress import BarColumn, Progress

console = Console()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

STAGE_COLORS = {
    "idea": "dim white",
    "research": "yellow",
    "scripted": "cyan",
    "voiced": "blue",
    "edited": "magenta",
    "scheduled": "orange3",
    "published": "green",
}

SLOT_SHORT_LABELS = {
    "mon_short": "Mon",
    "wed_short": "Wed",
    "thu_pi": "Thu PI",
    "fri_short": "Fri",
    "sat_pi": "Sat PI",
    "sun_longform": "Sun LF",
}

COMPLEXITY_EMOJI = {
    "triple": "●●●",
    "double": "●●○",
    "single": "●○○",
}


def _stage_badge(stage: str) -> Text:
    color = STAGE_COLORS.get(stage, "white")
    return Text(f" {stage} ", style=f"bold {color}")


def _progress_bar(current: int, target: int, width: int = 20) -> str:
    pct = min(current / target, 1.0)
    filled = int(pct * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {pct*100:.1f}%"


# ---------------------------------------------------------------------------
# CLI groups
# ---------------------------------------------------------------------------

@click.group()
def cli():
    """Finally Solved — YouTube channel production CLI."""


@cli.group()
def cases():
    """Case pipeline management."""


@cli.group()
def scripts():
    """AI script generation."""


@cli.group()
def calendar():
    """Content calendar planning."""


@cli.group()
def reddit():
    """Reddit distribution tracker."""


# ---------------------------------------------------------------------------
# cases list
# ---------------------------------------------------------------------------

@cases.command("list")
def cases_list():
    """Show all cases with stage indicators."""
    from src.pipeline import list_cases
    from config import WEEKLY_SLOTS

    all_cases = list_cases()
    if not all_cases:
        console.print("[yellow]No cases found. Use 'fs cases add' to create one.[/yellow]")
        return

    table = Table(
        title="[bold]Finally Solved — Case Pipeline[/bold]",
        box=box.ROUNDED,
        show_lines=True,
        header_style="bold cyan",
    )
    table.add_column("ID", style="dim", no_wrap=True)
    table.add_column("Case", style="bold")
    table.add_column("Year", justify="center")
    table.add_column("Tier", justify="center")
    table.add_column("Series", max_width=24)
    table.add_column("Status", justify="center")
    for slot in WEEKLY_SLOTS:
        table.add_column(SLOT_SHORT_LABELS[slot], justify="center", no_wrap=True)

    for c in all_cases:
        status_color = {"published": "green", "active": "cyan", "archived": "dim"}.get(c.status, "white")
        status_text = Text(c.status, style=f"bold {status_color}")
        tier_text = Text(COMPLEXITY_EMOJI.get(c.complexity, c.complexity), style="bold")
        row = [
            c.id,
            c.name,
            str(c.year or "—"),
            tier_text,
            c.micro_series,
            status_text,
        ]
        for slot in WEEKLY_SLOTS:
            asset = c.assets.get(slot)
            stage = asset.stage if asset else "—"
            color = STAGE_COLORS.get(stage, "dim")
            row.append(Text(stage[:4], style=color))
        table.add_row(*row)

    console.print(table)
    console.print(f"\n[dim]Total: {len(all_cases)} cases | Stages: idea→research→scripted→voiced→edited→scheduled→published[/dim]")


# ---------------------------------------------------------------------------
# cases add
# ---------------------------------------------------------------------------

@cases.command("add")
def cases_add():
    """Add a new case (interactive prompts)."""
    from src.pipeline import add_case
    from config import MICRO_SERIES, FAILURE_TYPES, COMPLEXITY_TIERS

    console.print(Panel("[bold cyan]Add New Case[/bold cyan]", expand=False))

    name = click.prompt("Case name")
    year_str = click.prompt("Year (leave blank if unknown)", default="")
    year = int(year_str) if year_str.strip().isdigit() else None

    console.print("\n[bold]Complexity tiers:[/bold]")
    for k, v in COMPLEXITY_TIERS.items():
        console.print(f"  [cyan]{k}[/cyan] — {v['layers']} failure layer(s), {v['longform_minutes']} min long-form")
    complexity = click.prompt("Complexity", type=click.Choice(list(COMPLEXITY_TIERS.keys())), default="double")

    console.print("\n[bold]Micro-series:[/bold]")
    for i, s in enumerate(MICRO_SERIES, 1):
        console.print(f"  [cyan]{i}[/cyan]. {s}")
    series_idx = click.prompt("Micro-series number", type=click.IntRange(1, len(MICRO_SERIES)), default=1)
    micro_series = MICRO_SERIES[series_idx - 1]

    console.print("\n[bold]Failure types:[/bold]")
    for i, f in enumerate(FAILURE_TYPES, 1):
        console.print(f"  [cyan]{i}[/cyan]. {f}")
    failure_idx = click.prompt("Failure type number", type=click.IntRange(1, len(FAILURE_TYPES)), default=1)
    failure_type = FAILURE_TYPES[failure_idx - 1]

    summary = click.prompt("Brief summary (1-2 sentences)", default="")
    notes = click.prompt("Notes", default="")

    case = add_case(
        name=name,
        complexity=complexity,
        micro_series=micro_series,
        failure_type=failure_type,
        summary=summary,
        year=year,
        notes=notes,
    )
    console.print(f"\n[bold green]✓ Case added:[/bold green] [cyan]{case.id}[/cyan] — {case.name}")


# ---------------------------------------------------------------------------
# cases show
# ---------------------------------------------------------------------------

@cases.command("show")
@click.argument("case_id")
def cases_show(case_id: str):
    """Show full case detail and asset stages."""
    from src.pipeline import get_case
    from config import WEEKLY_SLOTS, COMPLEXITY_TIERS

    case = get_case(case_id)
    if not case:
        console.print(f"[red]Case not found: {case_id}[/red]")
        sys.exit(1)

    tier_info = COMPLEXITY_TIERS.get(case.complexity, {})
    header = (
        f"[bold]{case.name}[/bold]"
        + (f"  ({case.year})" if case.year else "")
        + f"\n[dim]ID:[/dim] {case.id}"
        + f"  [dim]Status:[/dim] {case.status}"
        + f"  [dim]Tier:[/dim] {case.complexity} ({tier_info.get('longform_minutes', '?')} min)"
    )
    console.print(Panel(header, title="[cyan]Case Detail[/cyan]", expand=False))

    console.print(f"[bold]Micro-series:[/bold] {case.micro_series}")
    console.print(f"[bold]Failure type:[/bold] {case.failure_type.replace('_', ' ')}")
    if case.summary:
        console.print(f"[bold]Summary:[/bold] {case.summary}")
    if case.notes:
        console.print(f"[bold]Notes:[/bold] {case.notes}")

    console.print()
    table = Table(title="Asset Stages", box=box.SIMPLE_HEAVY, header_style="bold cyan")
    table.add_column("Slot", style="bold", no_wrap=True)
    table.add_column("Label")
    table.add_column("Stage", justify="center")
    table.add_column("Notes")

    slot_labels = {
        "mon_short": "Monday Short — Arc 1 (hook/setup)",
        "wed_short": "Wednesday Short — Arc 2 (complication)",
        "thu_pi": "Thursday Pattern Interrupt",
        "fri_short": "Friday Short — Arc 3 (escalation/resolution)",
        "sat_pi": "Saturday Pattern Interrupt",
        "sun_longform": "Sunday Long-form",
    }
    for slot in WEEKLY_SLOTS:
        asset = case.assets.get(slot)
        stage = asset.stage if asset else "—"
        notes = asset.notes if asset else ""
        color = STAGE_COLORS.get(stage, "white")
        table.add_row(slot, slot_labels.get(slot, slot), Text(stage, style=f"bold {color}"), notes)

    console.print(table)


# ---------------------------------------------------------------------------
# cases advance
# ---------------------------------------------------------------------------

@cases.command("advance")
@click.argument("case_id")
@click.argument("asset")
def cases_advance(case_id: str, asset: str):
    """Advance an asset to the next stage."""
    from src.pipeline import advance_asset

    case, message = advance_asset(case_id, asset)
    if case is None:
        console.print(f"[red]{message}[/red]")
        sys.exit(1)
    console.print(f"[bold green]✓[/bold green] {case.name} — {message}")


# ---------------------------------------------------------------------------
# scripts generate
# ---------------------------------------------------------------------------

@scripts.command("generate")
@click.argument("case_id")
@click.argument("slot")
@click.option("--context", "-c", default="", help="Extra context for the script generator")
def scripts_generate(case_id: str, slot: str, context: str):
    """Generate a script for a slot using Claude API."""
    from src.pipeline import get_case
    from src.scripts import generate_script
    from config import WEEKLY_SLOTS

    case = get_case(case_id)
    if not case:
        console.print(f"[red]Case not found: {case_id}[/red]")
        sys.exit(1)

    if slot not in WEEKLY_SLOTS:
        console.print(f"[red]Invalid slot '{slot}'. Valid slots: {', '.join(WEEKLY_SLOTS)}[/red]")
        sys.exit(1)

    console.print(f"[cyan]Generating {slot} script for [bold]{case.name}[/bold]...[/cyan]")
    console.print("[dim](Using prompt caching — subsequent calls to same model will be faster)[/dim]\n")

    try:
        script = generate_script(case, slot, extra_context=context)
        console.print(Panel(
            script,
            title=f"[bold cyan]{case.name} — {slot}[/bold cyan]",
            border_style="cyan",
            padding=(1, 2),
        ))
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]API error: {e}[/red]")
        sys.exit(1)


# ---------------------------------------------------------------------------
# calendar show
# ---------------------------------------------------------------------------

@calendar.command("show")
def calendar_show():
    """Show 4-week content calendar."""
    from src.calendar_planner import get_four_week_calendar
    from config import ASSET_STAGES

    weeks = get_four_week_calendar()

    for week_data in weeks:
        week_start = week_data["week_start"]
        table = Table(
            title=f"[bold]Week of {week_start}[/bold]",
            box=box.ROUNDED,
            header_style="bold cyan",
            show_lines=True,
        )
        table.add_column("Date", style="dim", no_wrap=True)
        table.add_column("Slot", style="bold", no_wrap=True)
        table.add_column("Case")
        table.add_column("Stage", justify="center")

        for slot_info in week_data["slots"]:
            case_name = slot_info["case_name"] or "[dim]— unassigned —[/dim]"
            stage = slot_info["stage"] or "—"
            color = STAGE_COLORS.get(stage, "dim")
            stage_text = Text(stage, style=f"bold {color}") if slot_info["stage"] else Text("—", style="dim")
            table.add_row(
                slot_info["date"],
                SLOT_SHORT_LABELS.get(slot_info["slot"], slot_info["slot"]),
                case_name,
                stage_text,
            )

        console.print(table)
        console.print()


# ---------------------------------------------------------------------------
# calendar plan-week
# ---------------------------------------------------------------------------

@calendar.command("plan-week")
@click.argument("case_id")
@click.argument("start_date")
def calendar_plan_week(case_id: str, start_date: str):
    """Assign a case to a week. START_DATE must be the Monday (YYYY-MM-DD)."""
    from src.calendar_planner import plan_week

    try:
        date.fromisoformat(start_date)
    except ValueError:
        console.print("[red]Invalid date format. Use YYYY-MM-DD.[/red]")
        sys.exit(1)

    schedule = plan_week(case_id, start_date)
    if not schedule:
        console.print(f"[red]Case not found: {case_id}[/red]")
        sys.exit(1)

    table = Table(title=f"[bold cyan]Week Schedule — {case_id}[/bold cyan]", box=box.SIMPLE_HEAVY)
    table.add_column("Slot")
    table.add_column("Publish Date")
    for slot, pub_date in schedule.items():
        table.add_row(SLOT_SHORT_LABELS.get(slot, slot), pub_date)
    console.print(table)
    console.print(f"\n[green]✓ Schedule saved.[/green]")


# ---------------------------------------------------------------------------
# reddit log
# ---------------------------------------------------------------------------

@reddit.command("log")
def reddit_log_cmd():
    """Log a Reddit post interactively."""
    from src.reddit import log_post
    from config import REDDIT_SUBREDDITS

    console.print(Panel("[bold cyan]Log Reddit Post[/bold cyan]", expand=False))

    console.print("[bold]Subreddits:[/bold]")
    for i, s in enumerate(REDDIT_SUBREDDITS, 1):
        console.print(f"  [cyan]{i}[/cyan]. {s}")
    sub_idx = click.prompt("Subreddit number", type=click.IntRange(1, len(REDDIT_SUBREDDITS)), default=1)
    subreddit = REDDIT_SUBREDDITS[sub_idx - 1]

    title = click.prompt("Post title")
    post_date = click.prompt("Post date (YYYY-MM-DD)", default=date.today().isoformat())
    case_id = click.prompt("Case ID (leave blank if none)", default="")
    engagement = click.prompt("Engagement (upvotes/comments, e.g. '47u/12c')", default="")
    yt_link = click.confirm("YouTube link included?", default=False)
    notes = click.prompt("Notes", default="")

    post = log_post(
        subreddit=subreddit,
        title=title,
        post_date=post_date,
        case_id=case_id,
        engagement=engagement,
        youtube_link_included=yt_link,
        notes=notes,
    )
    console.print(f"\n[bold green]✓ Logged:[/bold green] [{post.id}] {post.subreddit} — {post.title}")


# ---------------------------------------------------------------------------
# reddit schedule
# ---------------------------------------------------------------------------

@reddit.command("schedule")
def reddit_schedule():
    """Show upcoming Reddit posts and logged history."""
    from src.reddit import get_upcoming_schedule, list_posts, subreddit_stats

    upcoming = get_upcoming_schedule(weeks_ahead=4)
    table = Table(title="[bold]Upcoming Reddit Schedule (Next 4 Weeks)[/bold]", box=box.ROUNDED, header_style="bold cyan")
    table.add_column("Week", justify="center")
    table.add_column("Post Date")
    table.add_column("Subreddit")
    table.add_column("YT Link?", justify="center")

    for entry in upcoming:
        yt_flag = Text("YES", style="bold green") if entry["youtube_link"] else Text("no", style="dim")
        table.add_row(str(entry["week"]), entry["post_date"], entry["subreddit"], yt_flag)
    console.print(table)

    posts = list_posts()
    if posts:
        console.print()
        hist_table = Table(title="[bold]Post History[/bold]", box=box.SIMPLE_HEAVY, header_style="bold cyan")
        hist_table.add_column("ID", style="dim")
        hist_table.add_column("Date")
        hist_table.add_column("Subreddit")
        hist_table.add_column("Title", max_width=40)
        hist_table.add_column("Engagement")
        hist_table.add_column("YT", justify="center")

        for p in sorted(posts, key=lambda x: x.post_date, reverse=True):
            yt_text = Text("✓", style="green") if p.youtube_link_included else Text("—", style="dim")
            hist_table.add_row(p.id, p.post_date, p.subreddit, p.title[:40], p.engagement, yt_text)
        console.print(hist_table)

        stats = subreddit_stats()
        if stats:
            console.print()
            stat_table = Table(title="[bold]Stats by Subreddit[/bold]", box=box.SIMPLE_HEAVY)
            stat_table.add_column("Subreddit")
            stat_table.add_column("Posts", justify="right")
            stat_table.add_column("With YT Link", justify="right")
            for sub, s in stats.items():
                stat_table.add_row(sub, str(s["posts"]), str(s["with_yt_link"]))
            console.print(stat_table)


# ---------------------------------------------------------------------------
# dashboard
# ---------------------------------------------------------------------------

@cli.command("dashboard")
def dashboard():
    """Show growth metrics, YPP countdown, and velocity needed."""
    from src.dashboard import get_metrics

    m = get_metrics()

    console.print()
    console.print(Panel(
        "[bold white]FINALLY SOLVED[/bold white]  [dim]|  Faceless True Crime YouTube[/dim]",
        style="bold cyan",
        padding=(0, 2),
    ))

    # ── Current Stats ──────────────────────────────────────────────────────
    stats_table = Table(box=box.SIMPLE_HEAVY, show_header=False, padding=(0, 2))
    stats_table.add_column("Metric", style="bold dim")
    stats_table.add_column("Value", style="bold white")
    stats_table.add_row("Subscribers", f"{m['current_subs']:,}")
    stats_table.add_row("Total Views", f"{m['current_views']:,}")
    stats_table.add_row("Videos Published", str(m['current_videos']))
    stats_table.add_row("Weeks Live", str(m['weeks_live']))
    stats_table.add_row("Est. Watch Hours", f"{m['watch_hours_estimated']:.1f} hrs")
    stats_table.add_row("Weekly Sub Rate", f"{m['weekly_subs_rate']} subs/wk")
    stats_table.add_row("Weekly View Rate", f"{m['weekly_views_rate']:.0f} views/wk")

    console.print(Panel(stats_table, title="[bold]Channel Stats[/bold]", border_style="blue"))

    # ── YPP Progress ───────────────────────────────────────────────────────
    ypp_table = Table(box=box.SIMPLE_HEAVY, show_header=False, padding=(0, 2))
    ypp_table.add_column("Metric", style="bold dim")
    ypp_table.add_column("Progress", style="bold")
    ypp_table.add_column("Gap", style="dim")

    subs_bar = _progress_bar(m['current_subs'], 1000)
    hours_bar = _progress_bar(m['watch_hours_estimated'], 4000)

    ypp_table.add_row(
        "Subscribers (1,000 req.)",
        f"[cyan]{subs_bar}[/cyan]",
        f"{m['subs_needed_ypp']} needed",
    )
    ypp_table.add_row(
        "Watch Hours (4,000 req.)",
        f"[magenta]{hours_bar}[/magenta]",
        f"{m['watch_hours_needed_ypp']:.0f} hrs needed",
    )

    eta_str = f"{m['eta_ypp_weeks']} weeks at current pace" if m['eta_ypp_weeks'] else "∞ (no sub growth yet)"
    ypp_table.add_row("ETA to YPP (subs)", f"[yellow]{eta_str}[/yellow]", "")

    console.print(Panel(ypp_table, title="[bold]YPP Countdown[/bold]", border_style="yellow"))

    # ── Velocity Needed ────────────────────────────────────────────────────
    vel_table = Table(box=box.SIMPLE_HEAVY, header_style="bold cyan")
    vel_table.add_column("Target Timeline", style="bold")
    vel_table.add_column("Subs/Week Needed", justify="right")
    vel_table.add_column("vs. Current Rate", justify="right")

    current_rate = m['weekly_subs_rate']
    for label, v in [("90 days (3 mo)", m['velocity_90d']), ("120 days (4 mo)", m['velocity_120d']), ("180 days (6 mo)", m['velocity_180d'])]:
        gap = v - current_rate
        gap_str = f"+{gap:.1f}" if gap > 0 else f"{gap:.1f}"
        gap_color = "red" if gap > 0 else "green"
        vel_table.add_row(label, f"{v:.1f}", Text(gap_str, style=gap_color))

    console.print(Panel(vel_table, title="[bold]Velocity Needed — YPP (1,000 subs)[/bold]", border_style="cyan"))

    # ── Competitor Benchmark ───────────────────────────────────────────────
    comp_table = Table(box=box.SIMPLE_HEAVY, show_header=False, padding=(0, 2))
    comp_table.add_column("Metric", style="bold dim")
    comp_table.add_column("Value", style="bold white")
    comp_table.add_row(f"{m['competitor_name']} subs", f"{m['competitor_subs']:,}")
    comp_table.add_row(f"{m['competitor_name']} monthly rate", f"~{m['competitor_weekly_rate']*4.33:.0f} subs/mo")
    comp_table.add_row(f"{m['competitor_name']} weekly rate", f"~{m['competitor_weekly_rate']} subs/wk")
    weeks_str = f"{m['weeks_to_competitor']} weeks at current pace" if m['weeks_to_competitor'] else "∞"
    comp_table.add_row("Weeks to outpace", f"[yellow]{weeks_str}[/yellow]")

    console.print(Panel(comp_table, title=f"[bold]Benchmark vs. {m['competitor_name']}[/bold]", border_style="magenta"))
    console.print()


# ---------------------------------------------------------------------------
# tags
# ---------------------------------------------------------------------------

@cli.group()
def tags():
    """YouTube tag generator."""


@tags.command("generate")
@click.argument("case_id")
@click.option("--slot", default="sun_longform", help="Asset slot (default: sun_longform)")
def tags_generate(case_id, slot):
    """Generate a YouTube-ready tag stack for a case."""
    from src.pipeline import get_case
    from config import (
        TAGS_TIER1, TAGS_TIER2, TAGS_TIER3, TAGS_BRAND,
        TAGS_BY_MICRO_SERIES, TAGS_BY_FAILURE_TYPE, TAGS_BY_COMPLEXITY,
    )

    case = get_case(case_id)
    if not case:
        console.print(f"[red]Case '{case_id}' not found.[/red]")
        return

    is_short = slot in ("mon_short", "wed_short", "fri_short", "thu_pi", "sat_pi")

    # Build tag list in priority order
    tier1 = TAGS_TIER1[:]
    tier2 = TAGS_TIER2[:]
    tier3 = TAGS_TIER3[:] if not is_short else []
    case_tags = (
        TAGS_BY_MICRO_SERIES.get(case.micro_series, [])
        + TAGS_BY_FAILURE_TYPE.get(case.failure_type, [])
        + (TAGS_BY_COMPLEXITY.get(case.complexity, []) if not is_short else [])
    )
    brand = TAGS_BRAND[:]

    # Add case name as a tag
    name_tag = case.name.lower()
    if name_tag not in case_tags:
        case_tags.insert(0, name_tag)

    all_tags = tier1 + tier2 + tier3 + case_tags + brand

    # Deduplicate preserving order
    seen = set()
    unique_tags = []
    for t in all_tags:
        if t not in seen:
            seen.add(t)
            unique_tags.append(t)

    # Trim to YouTube's 500 character limit (preserve priority order)
    youtube_limit = 500
    trimmed_tags = []
    running = 0
    for tag in unique_tags:
        addition = len(tag) + (2 if trimmed_tags else 0)  # ", " separator
        if running + addition <= youtube_limit:
            trimmed_tags.append(tag)
            running += addition
        else:
            break

    youtube_string = ", ".join(trimmed_tags)
    char_count = len(youtube_string)
    dropped = len(unique_tags) - len(trimmed_tags)

    # ── Display ───────────────────────────────────────────────────────────────
    console.print()
    console.print(Panel(
        f"[bold white]{case.name}[/bold white]  [dim]— {slot}[/dim]",
        title="[bold cyan]YouTube Tag Generator[/bold cyan]",
        border_style="cyan",
    ))

    # Tier breakdown
    def print_tier(label, tag_list, color):
        if not tag_list:
            return
        t = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
        t.add_column("Tags", style=color, no_wrap=False)
        t.add_row("  ".join(f"[{color}]{tag}[/{color}]" for tag in tag_list))
        console.print(f"[bold {color}]{label}[/bold {color}]")
        formatted = "  •  ".join(tag_list)
        console.print(f"  [dim]{formatted}[/dim]")
        console.print()

    print_tier("Tier 1 — Always Use", tier1, "green")
    print_tier("Tier 2 — Rotate", tier2, "cyan")
    if tier3:
        print_tier("Tier 3 — Long-form", tier3, "blue")
    print_tier("Case-Specific", case_tags, "yellow")
    print_tier("Brand", brand, "magenta")

    # Character count bar
    bar_width = 30
    filled = int((char_count / youtube_limit) * bar_width)
    bar = "█" * filled + "░" * (bar_width - filled)
    count_color = "green" if char_count <= youtube_limit else "red"
    console.print(f"[bold]Characters:[/bold] [{count_color}]{char_count}/{youtube_limit}[/{count_color}]  [{count_color}]{bar}[/{count_color}]")
    if dropped:
        console.print(f"[dim yellow]  {dropped} low-priority tag(s) trimmed to stay within limit[/dim yellow]")
    console.print()

    # Ready-to-paste output
    console.print(Panel(
        youtube_string,
        title="[bold green]Paste into YouTube Tags[/bold green]",
        border_style="green",
    ))
    console.print()


@tags.command("stack")
def tags_stack():
    """Show the evergreen tag stack for all uploads."""
    from config import TAGS_TIER1, TAGS_TIER2, TAGS_TIER3, TAGS_BRAND

    base = TAGS_TIER1 + TAGS_TIER2[:5] + TAGS_BRAND
    youtube_string = ", ".join(base)

    console.print()
    console.print(Panel(
        youtube_string,
        title="[bold green]Evergreen Base Stack — Paste on Every Upload[/bold green]",
        border_style="green",
    ))
    console.print(f"[dim]Characters: {len(youtube_string)}/500[/dim]")
    console.print()


# ---------------------------------------------------------------------------
# video
# ---------------------------------------------------------------------------

@cli.group()
def video():
    """Video production — render Remotion graphics and assemble episodes."""


@video.command("render-graphics")
@click.argument("case_id")
@click.argument("slot")
@click.option("--channel", default="Finally Solved", help="Channel name for branding")
@click.option("--accent", default="#c41e3a", help="Accent color hex")
def video_render_graphics(case_id: str, slot: str, channel: str, accent: str):
    """Render animated Remotion graphics for a case+slot."""
    from src.pipeline import get_case
    from src.video import render_case_graphics
    from config import WEEKLY_SLOTS

    case = get_case(case_id)
    if not case:
        console.print(f"[red]Case not found: {case_id}[/red]")
        sys.exit(1)

    if slot not in WEEKLY_SLOTS:
        console.print(f"[red]Invalid slot. Valid: {', '.join(WEEKLY_SLOTS)}[/red]")
        sys.exit(1)

    console.print(Panel(
        f"[bold white]{case.name}[/bold white]  [dim]— {slot}[/dim]",
        title="[bold cyan]Render Graphics[/bold cyan]",
        border_style="cyan",
    ))
    console.print("[dim]Running Remotion renderer — this may take a minute...[/dim]\n")

    try:
        rendered = render_case_graphics(case, slot, channel_name=channel, accent_color=accent)
        table = Table(title="[bold]Rendered[/bold]", box=box.SIMPLE_HEAVY, header_style="bold cyan")
        table.add_column("Composition", style="bold")
        table.add_column("Path", style="dim")
        for name, path in rendered.items():
            table.add_row(name, path)
        console.print(table)
        console.print(f"\n[bold green]✓ {len(rendered)} graphic(s) rendered.[/bold green]")
    except RuntimeError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)


@video.command("assemble")
@click.argument("case_id")
@click.argument("slot")
def video_assemble(case_id: str, slot: str):
    """Assemble final episode MP4 from voiceover + BGM + graphics + b-roll."""
    from src.pipeline import get_case
    from src.video import assemble_episode
    from config import WEEKLY_SLOTS

    case = get_case(case_id)
    if not case:
        console.print(f"[red]Case not found: {case_id}[/red]")
        sys.exit(1)

    if slot not in WEEKLY_SLOTS:
        console.print(f"[red]Invalid slot. Valid: {', '.join(WEEKLY_SLOTS)}[/red]")
        sys.exit(1)

    console.print(f"[cyan]Assembling [bold]{case.name}[/bold] — {slot}...[/cyan]\n")

    try:
        output = assemble_episode(case.id, slot)
        console.print(f"\n[bold green]✓ Episode assembled:[/bold green] [cyan]{output}[/cyan]")
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)
    except RuntimeError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)


@video.command("produce")
@click.argument("case_id")
@click.argument("slot")
@click.option("--channel", default="Finally Solved", help="Channel name for branding")
@click.option("--accent", default="#c41e3a", help="Accent color hex")
def video_produce(case_id: str, slot: str, channel: str, accent: str):
    """Render graphics then assemble full episode in one command."""
    from src.pipeline import get_case
    from src.video import render_case_graphics, assemble_episode
    from config import WEEKLY_SLOTS

    case = get_case(case_id)
    if not case:
        console.print(f"[red]Case not found: {case_id}[/red]")
        sys.exit(1)

    if slot not in WEEKLY_SLOTS:
        console.print(f"[red]Invalid slot. Valid: {', '.join(WEEKLY_SLOTS)}[/red]")
        sys.exit(1)

    console.print(Panel(
        f"[bold white]{case.name}[/bold white]  [dim]— {slot}[/dim]",
        title="[bold cyan]Video Production[/bold cyan]",
        border_style="cyan",
    ))

    console.print("\n[bold]Step 1/2 — Rendering Remotion graphics...[/bold]")
    try:
        rendered = render_case_graphics(case, slot, channel_name=channel, accent_color=accent)
        console.print(f"[green]✓ {len(rendered)} graphic(s) rendered[/green]")
    except RuntimeError as e:
        console.print(f"[red]Remotion render failed: {e}[/red]")
        sys.exit(1)

    console.print("\n[bold]Step 2/2 — Assembling episode...[/bold]")
    try:
        output = assemble_episode(case.id, slot)
        console.print(f"[green]✓ Assembled[/green]")
        console.print(Panel(
            f"[bold green]Done![/bold green]\n[dim]{output}[/dim]",
            border_style="green",
        ))
    except FileNotFoundError:
        console.print(
            "[yellow]No voiceover found — graphics rendered but final assembly skipped.[/yellow]\n"
            f"[dim]Add voiceover at: output/{case.id}/{slot}/voiceover.mp3[/dim]"
        )


@video.command("status")
@click.argument("case_id")
def video_status(case_id: str):
    """Show which video assets are ready for each slot."""
    from src.pipeline import get_case
    from config import WEEKLY_SLOTS

    case = get_case(case_id)
    if not case:
        console.print(f"[red]Case not found: {case_id}[/red]")
        sys.exit(1)

    output_base = Path("output") / case.id

    table = Table(
        title=f"[bold]Video Assets — {case.name}[/bold]",
        box=box.ROUNDED,
        header_style="bold cyan",
        show_lines=True,
    )
    table.add_column("Slot", style="bold")
    table.add_column("Voiceover", justify="center")
    table.add_column("BGM", justify="center")
    table.add_column("B-Roll", justify="center")
    table.add_column("Graphics", justify="center")
    table.add_column("Final", justify="center")

    def check(path: Path) -> Text:
        return Text("✓", style="bold green") if path.exists() else Text("—", style="dim")

    for slot in WEEKLY_SLOTS:
        slot_dir = output_base / slot
        graphics_count = len(list((slot_dir / "graphics").glob("*.mp4"))) if (slot_dir / "graphics").exists() else 0
        broll_count = len(list((slot_dir / "broll").glob("*.mp4"))) if (slot_dir / "broll").exists() else 0
        table.add_row(
            SLOT_SHORT_LABELS.get(slot, slot),
            check(slot_dir / "voiceover.mp3"),
            check(slot_dir / "bgm.mp3"),
            Text(str(broll_count), style="bold green" if broll_count else "dim"),
            Text(str(graphics_count), style="bold green" if graphics_count else "dim"),
            check(slot_dir / "final.mp4"),
        )

    console.print(table)
    console.print(
        f"\n[dim]Asset folder: output/{case.id}/<slot>/\n"
        "  voiceover.mp3 — required for assembly\n"
        "  bgm.mp3       — optional background music\n"
        "  broll/        — optional .mp4 clips[/dim]"
    )


# ---------------------------------------------------------------------------
# Entry point — support both `python main.py <cmd>` and `fs <cmd>`
# ---------------------------------------------------------------------------

# Register sub-command aliases so top-level args work directly
cli.add_command(dashboard, "dashboard")

if __name__ == "__main__":
    cli()
