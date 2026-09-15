from __future__ import annotations

import json
import os
import urllib.request

from .models import AnalysisRequest, AnalysisResult, BusinessQuestion, CATEGORIES

SYSTEM_PROMPT = """You are a Principal Data Scientist and Business Intelligence Strategist. Analyze a dataset schema and optional sample data. Return JSON only with keys: domain (string), entities (array of strings), relationships (array of strings), assumptions (array of strings), questions (object). questions must contain exactly these categories: Key Metrics & KPIs, Customer & Behavioral Segmentation, Operational Efficiency. Each category must have 2-4 objects with question, why, how, what strings. Explain concrete metrics and transformations without inventing unavailable fields."""


def _fallback(request: AnalysisRequest) -> AnalysisResult:
    names = ", ".join(request.columns[:8])
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
    )


def analyze(request: AnalysisRequest) -> AnalysisResult:
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
    with urllib.request.urlopen(http_request, timeout=90) as response:
        content = json.loads(response.read())
    result = AnalysisResult.from_dict(
        json.loads(content["choices"][0]["message"]["content"])
    )
    return result
