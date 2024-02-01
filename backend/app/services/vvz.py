from typing import List

from backend.app.models.vvz import SearchResult
from backend.app.schemas.vvz import SearchResultSchema
from datetime import date
from backend.crawler.vvz import VvzCrawler

crawler = VvzCrawler()


class VvzService:
    @staticmethod
    async def search_vvz(
        date_from: date, date_to: date, mock: bool = False
    ) -> List[SearchResult]:
        params = {
            "page": "1",
            "limit": "100",
            "form": "vz",
            "workflowPlace": "UVEREJNENO_VVZ",
            "data.datumUverejneniVvz[gte]": date_from.strftime(
                "%Y-%m-%dT17:30:00+02:00"
            ),
            "data.datumUverejneniVvz[lte]": date_to.strftime("%Y-%m-%dT00:00:00+02:00"),
            "data.druhVz": "PRACE",
            "order[data.datumUverejneniVvz]": "DESC",
        }

        data = crawler.get_data(params, mock=mock)

        return data
