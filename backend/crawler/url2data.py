import json
import logging
import os
import sys
from datetime import datetime

from backend.crawler.requests_api import RequestsApi
from backend.app.schemas.vvz import SearchResultSchema

logger = logging.getLogger(__name__)


class VvzCrawler:
    MOCK_DATA_FILE = "vvz_mock_data.json"

    def __init__(self):
        self.api_url = "https://api.vvz.nipez.cz"
        self.headers = {
            "authority": "api.vvz.nipez.cz",
            "accept": "application/json, text/plain, */*",
            "accept-language": "cs-CZ,cs;q=0.5",
            "cache-control": "no-cache",
            "origin": "https://vvz.nipez.cz",
            "pragma": "no-cache",
            "referer": "https://vvz.nipez.cz/",
            "sec-ch-ua": '"Brave";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
        }
        self.client = RequestsApi(self.api_url)

    def get_data(self, params, mock=False):
        if mock:
            return self.get_mock_data()

        try:
            data = self._get_api_data(params)
            self.save_data(data, self.MOCK_DATA_FILE)
        except Exception as e:
            logger.error("Error getting data: %s", e)
            data = []

        return data

    def _get_api_data(self, params):
        response = self.client.get(
            "/api/submissions/search", params=params, headers=self.headers
        )
        return response.json()

    def get_mock_data(self):
        with open(self.MOCK_DATA_FILE) as file:
            return json.load(file)

    def save_data(self, data, file_path):
        if os.path.exists(file_path):
            with open(file_path) as file:
                existing_data = json.load(file)
                data = existing_data + data

        with open(file_path, "w") as file:
            json.dump(data, file)


if __name__ == "__main__":
    sys.path.append(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    crawler = VvzCrawler()

    params = {
        "page": "1",
        "limit": "100",
        "form": "vz",
        "workflowPlace": "UVEREJNENO_VVZ",
        "data.datumUverejneniVvz[gte]": datetime.strptime("19.12.2023", "%d.%m.%Y")
            .date().strftime("%Y-%m-%dT17:30:00+02:00"),
        "data.datumUverejneniVvz[lte]": datetime.strptime("21.12.2023", "%d.%m.%Y")
            .date().strftime("%Y-%m-%dT00:00:00+02:00"),
        "data.druhVz": "PRACE",
        "order[data.datumUverejneniVvz]": "DESC",
    }

    # Get real data
    data = crawler.get_data(params)

    # Get mocked data
    mock_data = crawler.get_data(params, mock=True)

    for item in mock_data:
        vvz_search_result = SearchResultSchema(**item)
        print(vvz_search_result)
        print("*" * 100)
