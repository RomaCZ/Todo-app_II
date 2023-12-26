from typing import List

from fastapi import APIRouter
from pymongo.errors import DuplicateKeyError

from backend.app.core.logger import logger
from backend.app.models.vvz import SearchResult
from backend.app.services.vvz import VvzService

vvz_router = APIRouter()


@vvz_router.get(
    "/list",
    summary="Get all the search results",
    response_model=List[SearchResult] | None,
)
async def list():
    results = await VvzService.search_vvz()
    for result in results:
        try:
            await SearchResult(**result).insert()
        except DuplicateKeyError:
            logger.error("Error inserting duplicate _id")

    return results
