import json
import uuid
from datetime import date
from typing import Optional
from config import REDDIT_LOG_FILE, REDDIT_SUBREDDITS
from src.models import RedditPost


def _load_posts() -> list[RedditPost]:
    if not REDDIT_LOG_FILE.exists():
        return []
    with open(REDDIT_LOG_FILE) as f:
        raw = json.load(f)
    return [RedditPost.from_dict(d) for d in raw]


def _save_posts(posts: list[RedditPost]) -> None:
    REDDIT_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(REDDIT_LOG_FILE, "w") as f:
        json.dump([p.to_dict() for p in posts], f, indent=2)


def list_posts() -> list[RedditPost]:
    return _load_posts()


def log_post(
    subreddit: str,
    title: str,
    post_date: str,
    case_id: str = "",
    engagement: str = "",
    youtube_link_included: bool = False,
    notes: str = "",
) -> RedditPost:
    posts = _load_posts()
    post_id = str(uuid.uuid4())[:8]
    post = RedditPost(
        id=post_id,
        subreddit=subreddit,
        post_date=post_date,
        title=title,
        case_id=case_id,
        engagement=engagement,
        youtube_link_included=youtube_link_included,
        notes=notes,
    )
    posts.append(post)
    _save_posts(posts)
    return post


def get_upcoming_schedule(weeks_ahead: int = 4) -> list[dict]:
    """
    Return the locked weekly Reddit schedule for the next N weeks.
    Rotation: one post per subreddit per week, cycling through the 5 subreddits.
    """
    today = date.today()
    # Find the next Monday
    days_to_monday = (7 - today.weekday()) % 7 or 7
    next_monday = today.toordinal() + days_to_monday

    schedule = []
    for week_offset in range(weeks_ahead):
        week_monday = date.fromordinal(next_monday + week_offset * 7)
        subreddit = REDDIT_SUBREDDITS[week_offset % len(REDDIT_SUBREDDITS)]
        # Posts go out on Wednesday of each week (middle of content week)
        post_date = date.fromordinal(week_monday.toordinal() + 2)
        schedule.append({
            "week": week_offset + 1,
            "post_date": post_date.isoformat(),
            "subreddit": subreddit,
            "youtube_link": subreddit == "r/crimedocumentaries",
        })
    return schedule


def subreddit_stats() -> dict[str, dict]:
    """Aggregate engagement stats per subreddit."""
    posts = _load_posts()
    stats: dict[str, dict] = {}
    for p in posts:
        sub = p.subreddit
        if sub not in stats:
            stats[sub] = {"posts": 0, "with_yt_link": 0}
        stats[sub]["posts"] += 1
        if p.youtube_link_included:
            stats[sub]["with_yt_link"] += 1
    return stats
