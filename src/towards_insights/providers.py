from __future__ import annotations

import json
import os
import ssl
import urllib.request
from pathlib import Path

import certifi

from .models import (
    AnalysisRequest,
    AnalysisResult,
    BusinessQuestion,
    CATEGORIES,
    DataOverview,
)


def _load_local_env() -> None:
    """Load simple KEY=value settings without requiring a dotenv dependency."""
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


SYSTEM_PROMPT = """You are a Principal Data Scientist and Business Intelligence Strategist. Analyze a dataset schema and optional sample data. Return JSON only with keys: overview, domain, entities, relationships, assumptions, questions. The overview must contain briefing_points: exactly 5 concise, sentence-case Markdown bullet strings in this order: (1) what business activity and domain the dataset captures, (2) what each row represents and how key entities relate, (3) the main quantitative metrics, (4) customer, product, geographic, channel, status, or other attributes, and (5) concrete data-quality risks or reporting limitations. Match this style: '- Captures a retail e-commerce order log containing completed transactions, customer demographics, and product attributes.\n- Defines each row as a single order line linked to individual customer profiles and items across various product categories.\n- Tracks key quantitative metrics including quantities, discounts, sales, and order values.\n- Details customer profile attributes like age, city, and segmentation, as well as product names, categories, and unit prices.\n- Highlights data quality risks such as inconsistent date formats and redundant or unclear fields like Sales and OrderValue that could impact financial reporting.' Do not copy the example facts unless the supplied data supports them. Use normal sentence case, not all capitals. Also return profile as a concise plain-text summary for backward compatibility, plus summary, grain, field_roles, measures, dimensions, time_fields, quality_notes, analytical_opportunities, and limitations. Infer carefully from field names and sample values, label uncertainty, and never invent unavailable fields or statistics. questions must contain exactly these categories: Key Metrics & KPIs, Customer & Behavioral Segmentation, Operational Efficiency. Each category must have 2-4 objects with question, why, how, what strings. Explain concrete metrics and transformations without inventing unavailable fields."""


def _open_url(request: urllib.request.Request):
    context = ssl.create_default_context(cafile=certifi.where())
    try:
        return urllib.request.urlopen(request, timeout=90, context=context)
    except ssl.SSLCertVerificationError as error:
        raise RuntimeError(
            "TLS certificate verification failed. The provider certificate could not be trusted; "
            "check your network proxy or CA configuration."
        ) from error


def _fallback(request: AnalysisRequest) -> AnalysisResult:
    names = ", ".join(request.columns[:8])
    lower_names = [column.lower() for column in request.columns]
    measures = [
        column
        for column, lowered in zip(request.columns, lower_names)
        if any(
            token in lowered
            for token in (
                "amount",
                "revenue",
                "sales",
                "spend",
                "price",
                "cost",
                "quantity",
                "count",
                "value",
                "score",
            )
        )
    ]
    time_fields = [
        column
        for column, lowered in zip(request.columns, lower_names)
        if any(
            token in lowered
            for token in ("date", "time", "created", "updated", "timestamp")
        )
    ]
    dimensions = [
        column
        for column in request.columns
        if column not in measures and column not in time_fields
    ][:8]
    identifier = next(
        (
            column
            for column, lowered in zip(request.columns, lower_names)
            if any(token in lowered for token in ("id", "key", "number"))
        ),
        request.columns[0],
    )
    domain = (
        "retail, commerce, or transactional operations"
        if any(
            token in " ".join(lower_names)
            for token in ("order", "product", "sku", "cart", "payment", "customer")
        )
        else "business operations"
    )
    measure_text = ", ".join(measures[:5]) or "the available fields"
    dimension_text = ", ".join(dimensions[:5]) or "the available categorical fields"
    time_text = ", ".join(time_fields[:4])
    sample_rows = max(0, len(request.sample_data.strip().splitlines()) - 1)
    briefing_points = [
        f"Captures a {domain} dataset containing records that can support performance and decision analysis.",
        f"Defines each row as a business record identified by {identifier}, with relationships to customer, product, or process entities inferred where fields support them.",
        f"Tracks key quantitative metrics including {measure_text}.",
        f"Details business attributes including {dimension_text}{f' and time fields such as {time_text}' if time_text else ''}.",
        "Highlights data quality risks such as missing values, inconsistent dates, duplicate identifiers, and redundant or unclear measures that could affect reporting.",
    ]
    questions = {
        CATEGORIES[0]: [
            {
                "question": "What is the primary volume, value, or revenue trend over time?",
                "why": "Leadership needs a reliable view of business scale and direction.",
                "how": f"Identify date and measure fields among {names}; aggregate the measure by week or month and compare period-over-period change.",
                "what": "A KPI strip with a time-series line chart and period-over-period variance.",
            },
            {
                "question": "Which dimensions explain the largest differences in performance?",
                "why": "This focuses attention on the segments where decisions can change outcomes.",
                "how": "Group the core measure by available categorical fields, calculate contribution percentage, and rank descending.",
                "what": "A ranked bar chart with contribution labels.",
            },
        ],
        CATEGORIES[1]: [
            {
                "question": "Which customer or user segments behave differently?",
                "why": "Segment-level differences support targeted investment rather than average-based decisions.",
                "how": "Identify customer, account, geography, channel, or product fields; calculate volume, value, frequency, and retention proxies by segment.",
                "what": "A cohort or segment matrix colored by value and engagement.",
            },
            {
                "question": "Where are high-value customers at risk of disengagement?",
                "why": "Protecting valuable relationships is often cheaper than replacing them.",
                "how": "Combine recency, frequency, monetary value, and activity fields where available; flag high-value segments with declining recency or frequency.",
                "what": "A scatter plot of value versus recency with risk coloring.",
            },
        ],
        CATEGORIES[2]: [
            {
                "question": "Where do delays, drop-offs, or rework concentrate?",
                "why": "Operational friction consumes capacity and directly affects customer outcomes.",
                "how": "Use status, timestamp, duration, error, and outcome fields to calculate stage conversion, cycle time, backlog, and exception rates.",
                "what": "A funnel for drop-offs plus a box plot or control chart for cycle time.",
            },
            {
                "question": "Which processes or teams have the greatest efficiency opportunity?",
                "why": "Leadership can prioritize improvement work by measurable impact and feasibility.",
                "how": "Compare throughput, cycle time, utilization, and quality outcomes across the available process, team, or channel dimensions.",
                "what": "A quadrant chart plotting impact against efficiency.",
            },
        ],
    }
    return AnalysisResult(
        "To be confirmed from schema",
        ["Record or transaction", "Customer or account (if present)"],
        [
            "Records belong to a customer, account, product, or process when matching identifiers exist."
        ],
        {
            category: [BusinessQuestion(**item) for item in items]
            for category, items in questions.items()
        },
        [
            "No sample data or data dictionary was supplied; field meanings are inferred from names."
        ],
        DataOverview(
            "The dataset appears to contain operational records that can support performance, segmentation, and process analysis.",
            "One row per record or transaction, subject to confirmation.",
            [
                f"Potential identifier or dimension: {column}"
                for column in request.columns[:4]
            ],
            [
                "Field meaning, row grain, missingness, and time coverage should be confirmed with a data dictionary."
            ],
            profile=(
                f"This dataset appears to be a **{domain} dataset** capturing records that can support performance and decision analysis. "
                f"Each row likely represents one business record identified by **{identifier}**; this row grain should be confirmed before aggregation. "
                f"Key quantitative fields include **{measure_text}**, while business attributes include **{dimension_text}**. "
                f"{f'Time context is provided by **{time_text}**. ' if time_text else ''}Initial quality checks should confirm duplicate identifiers, missing values, inconsistent dates, and whether similarly named measures are redundant. "
                f"This first view is based on {len(request.columns)} column names and {sample_rows} reference rows, so conclusions remain directional until the full dataset is profiled."
            ),
            briefing_points=briefing_points,
            measures=measures
            or [
                "No clear numeric measure was identifiable from the supplied column names."
            ],
            dimensions=dimensions
            or [
                "No clear categorical dimension was identifiable from the supplied column names."
            ],
            time_fields=time_fields
            or ["No obvious date or timestamp field was identified."],
            analytical_opportunities=[
                "Establish the row grain and a trusted primary measure before building KPIs.",
                "Compare the primary measure across the strongest available dimensions.",
                "Check whether time fields support trend, cohort, or retention analysis.",
            ],
            limitations=[
                "This overview is inferred from column names and a small reference sample, not a full data profile.",
                "No reliable row counts, distributions, missingness rates, or statistical relationships are available yet.",
            ],
        ),
    )


def analyze(request: AnalysisRequest) -> AnalysisResult:
    _load_local_env()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return _fallback(request)
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    payload = {
        "model": model,
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": json.dumps(
                    {"columns": request.columns, "sample_data": request.sample_data}
                ),
            },
        ],
    }
    body = json.dumps(payload).encode()
    http_request = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with _open_url(http_request) as response:
        content = json.loads(response.read())
    result = AnalysisResult.from_dict(
        json.loads(content["choices"][0]["message"]["content"])
    )
    return result


def answer_question(
    request: AnalysisRequest,
    analysis: AnalysisResult,
    question: str,
    history: list[dict[str, str]],
) -> str:
    _load_local_env()
    question = question.strip()
    if not question:
        raise ValueError("Ask a question about the dataset or analysis.")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return (
            f"Based on the available schema, I would investigate **{question}** by defining the relevant measure, "
            "checking its grain and time window, then comparing it across the strongest available dimensions. "
            "The current evidence is directional because no profiling or full data extract has been run yet."
        )
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    payload = {
        "model": model,
        "temperature": 0.2,
        "messages": [
            {
                "role": "system",
                "content": "You are a Principal Data Scientist answering follow-up questions about a dataset analysis. Be precise, state assumptions, and distinguish what the schema supports from what requires profiling. Use concise Markdown.",
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "columns": request.columns,
                        "sample_data": request.sample_data,
                        "analysis": analysis.to_dict(),
                        "conversation": history,
                        "question": question,
                    }
                ),
            },
        ],
    }
    http_request = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with _open_url(http_request) as response:
        content = json.loads(response.read())
    return content["choices"][0]["message"]["content"]
