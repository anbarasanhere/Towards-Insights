import unittest

from towards_insights.models import AnalysisRequest, AnalysisResult, CATEGORIES


class ModelTests(unittest.TestCase):
    def test_request_normalizes_columns(self):
        request = AnalysisRequest(" Churn ", [" customer_id ", "", " plan "])
        request.validate()
        self.assertEqual(request.columns, ["customer_id", "plan"])

    def test_request_requires_columns(self):
        with self.assertRaises(ValueError):
            AnalysisRequest("Churn", []).validate()

    def test_result_requires_all_categories(self):
        with self.assertRaises(ValueError):
            AnalysisResult.from_dict(
                {"domain": "Retail", "questions": {CATEGORIES[0]: []}}
            )
