from dataclasses import dataclass, field
from typing import Optional
from config import ASSET_STAGES


@dataclass
class Asset:
    slot: str
    stage: str = "idea"
    notes: str = ""

    def advance(self) -> bool:
        idx = ASSET_STAGES.index(self.stage)
        if idx < len(ASSET_STAGES) - 1:
            self.stage = ASSET_STAGES[idx + 1]
            return True
        return False

    def to_dict(self) -> dict:
        return {"slot": self.slot, "stage": self.stage, "notes": self.notes}

    @classmethod
    def from_dict(cls, d: dict) -> "Asset":
        return cls(slot=d["slot"], stage=d.get("stage", "idea"), notes=d.get("notes", ""))


@dataclass
class Case:
    id: str
    name: str
    complexity: str  # triple | double | single
    micro_series: str
    failure_type: str
    summary: str = ""
    year: Optional[int] = None
    status: str = "active"  # active | published | archived
    assets: dict = field(default_factory=dict)
    notes: str = ""

    def __post_init__(self):
        from config import WEEKLY_SLOTS
        for slot in WEEKLY_SLOTS:
            if slot not in self.assets:
                self.assets[slot] = Asset(slot=slot)
            elif isinstance(self.assets[slot], dict):
                self.assets[slot] = Asset.from_dict(self.assets[slot])

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "complexity": self.complexity,
            "micro_series": self.micro_series,
            "failure_type": self.failure_type,
            "summary": self.summary,
            "year": self.year,
            "status": self.status,
            "assets": {k: v.to_dict() for k, v in self.assets.items()},
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Case":
        assets_raw = d.get("assets", {})
        assets = {k: Asset.from_dict(v) if isinstance(v, dict) else v
                  for k, v in assets_raw.items()}
        return cls(
            id=d["id"],
            name=d["name"],
            complexity=d.get("complexity", "single"),
            micro_series=d.get("micro_series", ""),
            failure_type=d.get("failure_type", "institutional_failure"),
            summary=d.get("summary", ""),
            year=d.get("year"),
            status=d.get("status", "active"),
            assets=assets,
            notes=d.get("notes", ""),
        )

    def overall_stage(self) -> str:
        stages = [a.stage for a in self.assets.values()]
        stage_indices = [ASSET_STAGES.index(s) for s in stages]
        min_idx = min(stage_indices)
        return ASSET_STAGES[min_idx]


@dataclass
class RedditPost:
    id: str
    subreddit: str
    post_date: str
    title: str
    case_id: str = ""
    engagement: str = ""
    youtube_link_included: bool = False
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "subreddit": self.subreddit,
            "post_date": self.post_date,
            "title": self.title,
            "case_id": self.case_id,
            "engagement": self.engagement,
            "youtube_link_included": self.youtube_link_included,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "RedditPost":
        return cls(
            id=d["id"],
            subreddit=d["subreddit"],
            post_date=d["post_date"],
            title=d["title"],
            case_id=d.get("case_id", ""),
            engagement=d.get("engagement", ""),
            youtube_link_included=d.get("youtube_link_included", False),
            notes=d.get("notes", ""),
        )
