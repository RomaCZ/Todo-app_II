from datetime import date
from typing import Annotated, List

from fastapi import APIRouter, Query
from pymongo.errors import DuplicateKeyError

from backend.app.core.logger import logger
from backend.app.models.vvz import SearchResult
from backend.app.services.vvz import VvzService

vvz_router = APIRouter()


@vvz_router.get(
    "/get_one_unprocessed",
    summary="Get all the search results",
    response_model=SearchResult | None,
)
async def get_one():
    item = await SearchResult.find_one({"processed": False})
    

    return item


@vvz_router.get("/vvz_search/")
async def vvz_search(
    date_from: Annotated[
        date,
        Query(
            title="Search date from",
            description="Query string for the VVZ search date from",
        ),
    ] = "2023-12-19",
    date_to: Annotated[
        date,
        Query(
            title="Search date to",
            description="Query string for the VVZ search date from",
        ),
    ] = "2023-12-21",
):
    query_items = {"date_from": date_from, "date_to": date_to}

    results = await VvzService.search_vvz(date_from, date_to, mock=True)
    for result in results:
        try:
            await SearchResult(**result).insert()
        except DuplicateKeyError:
            logger.error("Inserting duplicate _id")
    
    return query_items
