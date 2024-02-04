import unittest
from datetime import date

from backend.app.core.logger import logger
from backend.crawler.vvz import VvzCrawler
import jsonpath_ng.ext as jp


class TestVvzCrawler(unittest.TestCase):
    domain_prefix = "ref."

    def setUp(self):
        self.crawler = VvzCrawler(domain_prefix=self.domain_prefix)

    def test_get_search_results(self):
        query = {"date_from": date(2024, 1, 31), "date_to": date(2024, 2, 3)}
        data = self.crawler.get_search_results(query, mock=True)
        self.assertEqual(len(data), 14)

    def test_get_form_submissions(self):
        submissions = self.crawler.get_form_submissions(
            form_vvz_id="Z2024-000163", mock=True
        )
        self.assertEqual(len(submissions), 3)

    def test_get_form_detail(self):
        form_detail = self.crawler.get_form_detail(
            form_submission="1d408b25-02d2-4cea-82fb-be7689986cbe", mock=True
        )
        self.assertEqual(len(form_detail), 1)

        jp_first = lambda query, data: jp.parse(query).find(data)[0].value
        jp_all = lambda query, data: [
            match.value for match in jp.parse(query).find(data)
        ]

        self.assertEqual(
            jp_first(
                "$..ND-ProcedureProcurementScope..ND-ProcedureValueEstimate.._value",
                form_detail,
            ),
            45_000_000,
        )

    def test_get_form_schema(self):
        form_detail = self.crawler.get_form_schema(
            form_schema="/api/form_schemas/d4831dca-2fa3-4a7c-9102-c4114083cad9",
            mock=True,
        )

        jp_first = lambda query, data: jp.parse(query).find(data)[0].value
        jp_all = lambda query, data: [
            match.value for match in jp.parse(query).find(data)
        ]

        # prop_data = jp_first("$..propertyDetails", data)

        self.assertEqual(jp_first("$..layout", form_detail), "111")


if __name__ == "__main__":
    unittest.main()
