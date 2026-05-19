from datetime import date, datetime
from config import (
    CURRENT_SUBS,
    CURRENT_VIEWS,
    CURRENT_VIDEOS,
    LAUNCH_DATE,
    YPP_SUBS_TARGET,
    YPP_WATCH_HOURS_TARGET,
    AVG_WATCH_TIME_MINUTES,
    COMPETITOR_NAME,
    COMPETITOR_SUBS,
    COMPETITOR_MONTHS,
)


def _weeks_since_launch() -> float:
    launch = date.fromisoformat(LAUNCH_DATE)
    delta = date.today() - launch
    return max(delta.days / 7, 1)


def _estimated_watch_hours() -> float:
    return (CURRENT_VIEWS * AVG_WATCH_TIME_MINUTES) / 60


def _subs_per_week() -> float:
    return CURRENT_SUBS / _weeks_since_launch()


def _views_per_week() -> float:
    return CURRENT_VIEWS / _weeks_since_launch()


def _weeks_to_target_subs(target: int) -> float:
    weekly_rate = _subs_per_week()
    if weekly_rate <= 0:
        return float("inf")
    return (target - CURRENT_SUBS) / weekly_rate


def _velocity_needed(target_subs: int, days: int) -> float:
    weeks = days / 7
    return max((target_subs - CURRENT_SUBS) / weeks, 0)


def get_metrics() -> dict:
    weeks_live = _weeks_since_launch()
    watch_hours = _estimated_watch_hours()
    watch_hours_needed = max(YPP_WATCH_HOURS_TARGET - watch_hours, 0)
    subs_needed = max(YPP_SUBS_TARGET - CURRENT_SUBS, 0)
    current_weekly_subs = _subs_per_week()
    current_weekly_views = _views_per_week()

    competitor_monthly = COMPETITOR_SUBS / COMPETITOR_MONTHS
    competitor_weekly = competitor_monthly / 4.33

    weeks_to_ypp = _weeks_to_target_subs(YPP_SUBS_TARGET)
    weeks_to_competitor = _weeks_to_target_subs(COMPETITOR_SUBS)

    return {
        # Current state
        "current_subs": CURRENT_SUBS,
        "current_views": CURRENT_VIEWS,
        "current_videos": CURRENT_VIDEOS,
        "weeks_live": round(weeks_live, 1),
        "watch_hours_estimated": round(watch_hours, 1),

        # YPP gap
        "subs_needed_ypp": subs_needed,
        "watch_hours_needed_ypp": round(watch_hours_needed, 1),

        # Current velocity
        "weekly_subs_rate": round(current_weekly_subs, 1),
        "weekly_views_rate": round(current_weekly_views, 1),

        # Velocity needed to hit YPP in N days
        "velocity_90d": round(_velocity_needed(YPP_SUBS_TARGET, 90), 1),
        "velocity_120d": round(_velocity_needed(YPP_SUBS_TARGET, 120), 1),
        "velocity_180d": round(_velocity_needed(YPP_SUBS_TARGET, 180), 1),

        # ETA at current pace
        "eta_ypp_weeks": round(weeks_to_ypp, 1) if weeks_to_ypp != float("inf") else None,

        # Competitor benchmark
        "competitor_name": COMPETITOR_NAME,
        "competitor_subs": COMPETITOR_SUBS,
        "competitor_weekly_rate": round(competitor_weekly, 1),
        "weeks_to_competitor": round(weeks_to_competitor, 1) if weeks_to_competitor != float("inf") else None,

        # Watch hours % of YPP target
        "watch_hours_pct": round((watch_hours / YPP_WATCH_HOURS_TARGET) * 100, 1),
        "subs_pct": round((CURRENT_SUBS / YPP_SUBS_TARGET) * 100, 1),
    }
