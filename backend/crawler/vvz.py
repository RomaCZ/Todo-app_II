import json
from pathlib import Path, PurePath

from backend.app.core.logger import logger
from backend.crawler.requests_api import RequestsApi


class VvzCrawler:
    MOCK_DATA_FOLDER = "test/mock_data/vvz"
    Path(MOCK_DATA_FOLDER).mkdir(parents=True, exist_ok=True)

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

    def _save_mock_data(self, data, file_name):
        file_path = PurePath(self.MOCK_DATA_FOLDER, file_name)
        with open(file_path, mode="w", encoding="utf8") as file:
            if ".json" in file_name:
                json.dump(data, file)
            else:
                file.write(data)
        logger.info(f"Mock data saved to {file_path}")

    def _load_mock_data(self, file_name):
        file_path = PurePath(self.MOCK_DATA_FOLDER, file_name)
        if not Path(file_path).exists():
            logger.error(f"Mock data file {file_path} not found")
            return None

        with open(file_path, mode="r", encoding="utf8") as file:
            data = file.read()
            if ".json" in file_name:
                data = json.loads(data)
            logger.info(f"Mock data loaded from {file_path}")
            return data

    def _mocked_get(self, url, params=None, headers=None, mock=None):
        if mock:
            data = self._load_mock_data(file_name=mock)
            if data:
                return data

        response = self.client.get(url, params=params, headers=headers)
        try:
            response = response.json()
        except json.decoder.JSONDecodeError:
            response = response.text

        if mock:
            self._save_mock_data(data=response, file_name=mock)
        return response

    def get_search_results(self, query, mock=False):
        url = "/api/submissions/search"
        page_limit = 50

        params = {
            "page": "1",
            "limit": page_limit,
            "form": "vz",
            "workflowPlace": "UVEREJNENO_VVZ",
            "data.datumUverejneniVvz[gte]": query["date_from"].strftime(
                "%Y-%m-%dT17:30:00+02:00"
            ),
            "data.datumUverejneniVvz[lte]": query["date_to"].strftime(
                "%Y-%m-%dT00:00:00+02:00"
            ),
            "data.druhVz": "PRACE",
            "order[data.datumUverejneniVvz]": "DESC",
        }

        results = []

        for page in range(1, 11):
            params["page"] = str(page)
            items = self._mocked_get(
                url, params=params, headers=self.headers, mock=mock
            )
            results.extend(items)
            if len(items) < page_limit:
                break

        logger.info(f"Results: {len(results)}, last items: {len(items)}")
        return results

    def get_submission_attachments(self, submission_version, mock=False):
        url = "/api/submission_attachments"
        params = {
            "limit": "50",
            "submissionVersion": submission_version,
        }
        attachments = self._mocked_get(
            url, params=params, headers=self.headers, mock=mock
        )
        return attachments

    def get_content_public_url(self, contentPublicUrl, mock=False):
        response = self._mocked_get(contentPublicUrl, headers=self.headers, mock=mock)
        return response
