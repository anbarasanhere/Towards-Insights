from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

CATEGORIES = (
    "Key Metrics & KPIs",
    "Customer & Behavioral Segmentation",
    "Operational Efficiency",
)


@dataclass
class AnalysisRequest:
    case_title: str
    columns: list[str]
    sample_data: str = ""

    def validate(self) -> None:
        self.case_title = self.case_title.strip()
        self.columns = [column.strip() for column in self.columns if column.strip()]
        if not self.case_title:
            raise ValueError("A case title is required.")
        if not self.columns:
            raise ValueError("Add at least one column name.")
        if len(self.columns) > 200:
            raise ValueError("Use 200 columns or fewer.")
        if len(self.sample_data) > 50_000:
            raise ValueError("Sample data must be 50,000 characters or fewer.")


@dataclass
class BusinessQuestion:
    question: str
    why: str
    how: str
    what: str


@dataclass
class DataOverview:
    summary: str
    grain: str
    field_roles: list[str]
    quality_notes: list[str] = field(default_factory=list)
    profile: str = ""
    briefing_points: list[str] = field(default_factory=list)
    measures: list[str] = field(default_factory=list)
    dimensions: list[str] = field(default_factory=list)
    time_fields: list[str] = field(default_factory=list)
    analytical_opportunities: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)


@dataclass
class AnalysisResult:
    domain: str
    entities: list[str]
    relationships: list[str]
    questions: dict[str, list[BusinessQuestion]]
    assumptions: list[str] = field(default_factory=list)
    overview: DataOverview = field(
        default_factory=lambda: DataOverview(
            "The dataset overview is inferred from the supplied schema.",
            "One row per record, subject to confirmation.",
            [],
            [],
        )
    )

    def validate(self) -> None:
        missing = [
            category for category in CATEGORIES if not self.questions.get(category)
        ]
        if missing:
            raise ValueError(f"Missing analysis categories: {', '.join(missing)}")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "AnalysisResult":
        questions = {
            category: [
                BusinessQuestion(**item)
                for item in payload.get("questions", {}).get(category, [])
            ]
            for category in CATEGORIES
        }
        result = cls(
            overview=DataOverview(
                **payload.get(
                    "overview",
                    {
                        "summary": "The dataset overview is inferred from the supplied schema.",
                        "grain": "One row per record, subject to confirmation.",
                        "field_roles": [],
                        "quality_notes": [],
                    },
                )
            ),
            domain=str(payload.get("domain", "Unknown")),
            entities=[str(item) for item in payload.get("entities", [])],
            relationships=[str(item) for item in payload.get("relationships", [])],
            questions=questions,
            assumptions=[str(item) for item in payload.get("assumptions", [])],
        )
        result.validate()
        return result
