from datetime import datetime

from requests_api import RequestsApi, logger




druhFormulare = "F02"
user_date_from = datetime.strptime("19.12.2023", "%d.%m.%Y").date()
user_date_to = datetime.strptime("21.12.2023", "%d.%m.%Y").date()
user_time_from = "17:30:00"
user_time_to = "00:00:00"
druhVz = "PRACE"


params = {
    "page": "1",
    "limit": "100",
    "form": "vz",
    "workflowPlace": "UVEREJNENO_VVZ",
    "data.datumUverejneniVvz[gte]": user_date_from.strftime(
        f"%Y-%m-%dT{user_time_from}+02:00"
    ),
    "data.datumUverejneniVvz[lte]": user_date_to.strftime(
        f"%Y-%m-%dT{user_time_to}+02:00"
    ),
    "data.druhVz": druhVz,
    "order[data.datumUverejneniVvz]": "DESC",
}
if druhFormulare:
    params["data.druhFormulare"] = druhFormulare
payload = {}
headers = {
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



if __name__ == "__main__":
    import os
    import sys
    import logging
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)





    client = RequestsApi("https://api.vvz.nipez.cz")
    response = client.get("/api/submissions/search", params=params, headers=headers)

    response_json = response.json()
    #print(response_json)

    from backend.app.schemas.vvz_search import VvzSearchResult

    for item in response_json:
        #print(item)
        vvz_search_result = VvzSearchResult(**item)
        print(vvz_search_result)
        print("*"*100)

