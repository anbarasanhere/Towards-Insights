from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from .models import AnalysisRequest, AnalysisResult


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "untitled-case"


def case_path(repo_path: str | Path, title: str) -> Path:
    root = Path(repo_path).resolve()
    cases = root / "cases"
    path = (cases / f"{slugify(title)}.md").resolve()
    if path.parent != cases.resolve():
        raise ValueError("Invalid case path.")
    return path


def render_case(
    request: AnalysisRequest,
    result: AnalysisResult,
    created_at: str | None = None,
    conversation: list[dict[str, str]] | None = None,
) -> str:
    now = datetime.now(timezone.utc).isoformat()
    created = created_at or now
    lines = [
        "---",
        f"case_id: {slugify(request.case_title)}",
        f"title: {request.case_title}",
        f"created: {created}",
        f"updated: {now}",
        f"domain: {result.domain}",
        "status: reviewed",
        "columns:",
        *[f"  - {column}" for column in request.columns],
        "---",
        "",
        f"# {request.case_title}",
        "",
        f"**Business domain:** {result.domain}",
        "",
        "## Data Overview",
        "",
        *[
            f"- {item}"
            for item in (
                result.overview.briefing_points
                or [result.overview.profile or result.overview.summary]
            )
        ],
        "",
        f"**Likely grain:** {result.overview.grain}",
        "",
        f"**Likely grain:** {result.overview.grain}",
        "",
        "### Field Roles",
        *[f"- {item}" for item in result.overview.field_roles],
        "",
        "### Quality Checks",
        *[f"- {item}" for item in result.overview.quality_notes],
        "",
        "### Measures",
        *[f"- {item}" for item in result.overview.measures],
        "",
        "### Dimensions",
        *[f"- {item}" for item in result.overview.dimensions],
        "",
        "### Time Fields",
        *[f"- {item}" for item in result.overview.time_fields],
        "",
        "### Analytical Opportunities",
        *[f"- {item}" for item in result.overview.analytical_opportunities],
        "",
        "### Limitations",
        *[f"- {item}" for item in result.overview.limitations],
        "",
        "## Core Entities",
        *[f"- {entity}" for entity in result.entities],
        "",
        "## Relationships",
        *[f"- {relationship}" for relationship in result.relationships],
    ]
    if result.assumptions:
        lines.extend(
            ["", "## Assumptions", *[f"- {item}" for item in result.assumptions]]
        )
    for category, questions in result.questions.items():
        lines.extend(["", f"## {category}"])
        for index, item in enumerate(questions, start=1):
            lines.extend(
                [
                    "",
                    f"### {index}. {item.question}",
                    "",
                    f"**WHY it matters:** {item.why}",
                    "",
                    f"**HOW to compute:** {item.how}",
                    "",
                    f"**WHAT to visualize:** {item.what}",
                ]
            )
    if conversation:
        lines.extend(["", "## Follow-up Discussion"])
        for item in conversation:
            speaker = "You" if item.get("role") == "user" else "Towards Insights"
            lines.extend(["", f"### {speaker}", "", item.get("content", "")])
    return "\n".join(lines) + "\n"
