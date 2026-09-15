import tempfile
import unittest
from pathlib import Path

from towards_insights.markdown import case_path, render_case, slugify
from towards_insights.models import (
    AnalysisRequest,
    AnalysisResult,
    BusinessQuestion,
    CATEGORIES,
)


class MarkdownTests(unittest.TestCase):
    def setUp(self):
        self.request = AnalysisRequest("Customer Churn", ["customer_id", "revenue"])
        question = BusinessQuestion(
            "What changed?",
            "Leadership needs direction.",
            "Aggregate by period.",
            "Line chart.",
        )
        self.result = AnalysisResult(
            "Subscription",
            ["Customer"],
            ["Customer has subscriptions"],
            {category: [question] for category in CATEGORIES},
        )

    def test_slug_is_stable(self):
        self.assertEqual(slugify("Customer Churn / Q1"), "customer-churn-q1")

    def test_case_uses_one_stable_path(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(
                case_path(directory, "Customer Churn"),
                case_path(directory, "Customer Churn"),
            )
            content = render_case(self.request, self.result)
            path = case_path(directory, self.request.case_title)
            path.parent.mkdir()
            path.write_text(content)
            self.assertTrue(Path(path).exists())
            self.assertIn("## Key Metrics & KPIs", content)
            self.assertIn("**WHY it matters:**", content)
