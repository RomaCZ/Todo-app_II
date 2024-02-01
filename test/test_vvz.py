import unittest
from datetime import date

from backend.app.core.logger import logger
from backend.crawler.vvz import VvzCrawler


class TestVvzCrawler(unittest.TestCase):
    def test_get_search_results(self):
        crawler = VvzCrawler()
        query = {"date_from": date(2023, 12, 19), "date_to": date(2023, 12, 21)}
        data = crawler.get_search_results(query, mock="get_search_results.json")
        self.assertEqual(len(data), 3)
    
    def test_get_submission_attachments(self):
        crawler = VvzCrawler()
        submission_version = "/api/submission_versions/8f3edb74-19c7-49b0-b22b-293ba821e923"
        submission = crawler.get_submission_attachments(submission_version, mock="get_submission_attachments.json") 
        self.assertEqual(len(submission), 1)

    def test_get_content_public_url(self):
        crawler = VvzCrawler()
        content_public_url = "/download/submission_attachments/public/fUacTxNrULyBWJxM6P0IYMs5TCEj4T0g"
        data = crawler.get_content_public_url(content_public_url, mock="get_content_public_url.xml")
        self.assertEqual(len(data), 3340)



        


if __name__ == "__main__":
    unittest.main()
