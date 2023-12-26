from typing import List

from backend.app.models.vvz import SearchResult
from backend.app.schemas.vvz import SearchResultSchema
from datetime import datetime
from backend.crawler.url2data import VvzCrawler

class VvzService:
    @staticmethod
    async def search_vvz() -> List[SearchResult]:
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

        crawler = VvzCrawler()
        # Get mocked data
        data = crawler.get_data(params, mock=0)
        
        for item in data:
            print(item)
            vvz_search_result = SearchResultSchema(**item)
            print(vvz_search_result)
            print("*" * 100)
        
        return data