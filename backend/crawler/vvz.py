import json
import re
from hashlib import md5
from pathlib import Path, PurePath

from pydantic import BaseModel, constr, validator
import jsonpath_ng.ext as jp


from requests_api import RequestsApi

import logging

logger = logging.getLogger(__name__)

FileName = constr(min_length=1)


class SchemaUuidModel(BaseModel):
    """
    A Pydantic model that represents a schema UUID.

    Attributes:
        uuid: A string that represents the UUID of the schema.

    Methods:
        extract_uuid: A validator for the 'uuid' field that extracts the UUID from a string.
    """

    uuid: str

    @validator("uuid")
    def extract_uuid(cls, uuid):
        return uuid.split("/")[-1]


class FileNameModel(BaseModel):
    """
    A Pydantic model for generating a file name based on a URL and parameters.

    Attributes:
        url (str): The URL to be used in the file name.
        params (dict, optional): The parameters to be included in the file name.

    Methods:
        generate_file_name: A validator for the 'url' field that generates the file name.
    """

    url: str
    params: dict = None

    @validator("url")
    def generate_file_name(cls, url, values):
        """
        Generates a file name based on the 'url' and 'params' fields.

        The file name is generated by removing the leading character from the URL, replacing slashes and periods with
        underscores, shortening the result to 45 characters, and appending a hash of the original string.

        Args:
            url (str): The URL to be used in the file name.
            values (dict): The current values of the model's fields.

        Returns:
            str: The generated file name.
        """
        params = values.get("params")
        trimmed_url = re.sub("^.", "", url)
        params_string = json.dumps(params, sort_keys=True) if params else ""
        plain_part = re.sub("[/.]", "_", f"{trimmed_url}_{params_string}")
        shortened_url = re.sub(r"(?u)[^-\w.]", "", plain_part)[:45]
        hash_object = md5(plain_part.encode()).hexdigest()
        file_name = f"{shortened_url}_{hash_object[:10]}.json"
        return file_name


class VvzCrawler:
    MOCK_DATA_FOLDER = "test/mock_data/vvz"
    Path(MOCK_DATA_FOLDER).mkdir(parents=True, exist_ok=True)

    def __init__(self, domain="vvz.nipez.cz", domain_prefix=""):
        self.api_url = f"https://{domain_prefix}api.{domain}"
        self.headers = {
            "authority": f"{domain_prefix}api.{domain}",
            "accept": "application/json, text/plain, */*",
            "accept-language": "cs-CZ,cs;q=0.9,en;q=0.8",
            "cache-control": "no-cache",
            "origin": f"https://{domain}",
            "pragma": "no-cache",
            "referer": f"https://{domain}/",
            "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "sec-gpc": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
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
        file_name = mock
        if mock is True:
            file_name_model = FileNameModel(url=url, params=params)
            file_name = file_name_model.url
        if mock:
            data = self._load_mock_data(file_name=file_name)
            if data:
                return data

        response = self.client.get(url, params=params, headers=headers)
        try:
            response = response.json()
        except json.decoder.JSONDecodeError:
            response = response.text

        if mock:
            self._save_mock_data(data=response, file_name=file_name)
        return response

    def get_search_results(self, query: dict, mock: bool | FileName = False) -> list:
        """
        Retrieves search results based on the provided query.

        Parameters
        ----------
        query : dict
            The search parameters. Must include 'date_from' and 'date_to' keys, and may optionally include 'druh_vz' and 'druh_formulare' keys.
            Example: {"date_from": date(2024, 1, 31), "date_to": date(2024, 2, 3)}
        mock : bool | FileName, optional
            If True, generates a filename from the URL and uses mock data.
            If a FileName (str), uses this as the filename for the mock data (default is False).

        Returns
        -------
        list
            The search results from the GET request.
        """
        url = "/api/submissions/search"
        page_limit = 50

        params = {
            "page": "1",
            "limit": page_limit,
            "form": "vz",
            "workflowPlace": "UVEREJNENO_VVZ",
            "data.datumUverejneniVvz[gte]": query["date_from"].strftime(
                "%Y-%m-%dT17:30:00+01:00"
            ),
            "data.datumUverejneniVvz[lte]": query["date_to"].strftime(
                "%Y-%m-%dT00:00:00+01:00"
            ),
            "order[data.datumUverejneniVvz]": "DESC",
        }

        if "druh_vz" in query:
            params["data.druhVz"] = query["druh_vz"]

        if "druh_formulare" in query:
            params["data.druhFormulare"] = query["druh_formulare"]

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

    def get_form_submissions(
        self, form_vvz_id: str, mock: bool | FileName = False
    ) -> dict:
        """
        Retrieves the submissions of a form.

        Parameters
        ----------
        form_vvz_id : str
            The ID of the form to retrieve submissions for.
            Example: "Z2024-000163"
        mock : bool | FileName, optional
            If True, generates a filename from the URL and uses mock data.
            If a FileName (str), uses this as the filename for the mock data (default is False).

        Returns
        -------
        dict
            The response from the GET request, containing the form submissions.
        """

        url = "/api/submissions/search"
        params = {
            "page": 1,
            "limit": 200,
            "form": "vz",
            "data.evCisloZakazkyVvz": form_vvz_id,
            "order[data.datumUverejneniVvz]": "DESC",
            "order[createdAt]": "DESC",
        }
        response = self._mocked_get(url, params=params, headers=self.headers, mock=mock)
        return response

    def get_form_detail(
        self, form_submission: str, mock: bool | FileName = False
    ) -> dict:
        """
        Retrieves the details of a form submission.

        Parameters
        ----------
        form_submission : str
            The ID of the form submission to retrieve details for.
            Example: "1d408b25-02d2-4cea-82fb-be7689986cbe"
        mock : bool | FileName, optional
            If True, generates a filename from the URL and uses mock data.
            If a FileName (str), uses this as the filename for the mock data (default is False).

        Returns
        -------
        dict
            The response from the GET request, containing the form submission details.
        """
        url = "/api/submissions/children/search"
        params = {
            "submission": form_submission,
        }
        response = self._mocked_get(url, params=params, headers=self.headers, mock=mock)
        return response

    def get_form_schema(
        self, form_schema: str, mock: bool | FileName = False
    ) -> dict:
        """
        Retrieves the form schema.

        Parameters
        ----------
        form_schema : str
            The UUID of the form schema to retrieve.
            Example: "/api/form_schemas/23399c76-ee07-42f3-b28a-e0f22361eaf1"
        mock : bool | FileName, optional
            If True, generates a filename from the URL and uses mock data.
            If a FileName (str), uses this as the filename for the mock data (default is False).

        Returns
        -------
        dict
            The response from's schema as a dictionary.
        """
        url = "/api/form_schema_translations/messages"
        params = {
            "formSchema": SchemaUuidModel(uuid=form_schema).uuid,
            "locale": "cs",
            "domain[0]": "layout",
            "domain[1]": "form",
        }
        logger.error(params)
        response = self._mocked_get(url, params=params, headers=self.headers, mock=mock)
        return response

    def enhance_form_detail_with_schema(self, form_detail):
        form_schema = form_detail[0]["formSchema"]
        form_schema = self.get_form_schema(form_schema, mock= True)
        return self._enhance_json_with_schema(form_detail[0], form_schema)

    def _enhance_json_with_schema(self, json_data, schema):
        for key in json_data:
            if isinstance(json_data[key], dict):
                self._enhance_json_with_schema(json_data[key], schema)
            else:
                schema_description = schema["layout"].get(f'field|description|{key}', None)
                schema_name = schema["layout"].get(f'field|name|{key}', None)

                new_value= json_data[key] = {
                        'value': json_data[key],
                    }

                if schema_description:
                    new_value['description'] = schema_description

                if schema_name:
                    new_value['description'] = schema_name

                json_data[key] = new_value

        return json_data

if __name__ == "__main__":
    import sys
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    domain_prefix = "ref."
    crawler = VvzCrawler(domain_prefix=domain_prefix)
    form_detail = crawler.get_form_detail(
            form_submission="1d408b25-02d2-4cea-82fb-be7689986cbe", mock=True
        )
    logger.info(form_detail)

    form_detail = crawler.enhance_form_detail_with_schema(form_detail)

    logger.info(form_detail)
