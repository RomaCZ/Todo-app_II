from fastapi import APIRouter

from app.api.v1.endpoints import contracts, crawler, manual_processing

api_router = APIRouter()

api_router.include_router(contracts.router, prefix="/contracts", tags=["contracts"])
api_router.include_router(crawler.router, prefix="/crawler", tags=["crawler"])
api_router.include_router(manual_processing.router, tags=["manual-processing"])
