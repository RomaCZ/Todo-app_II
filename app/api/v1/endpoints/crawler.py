from datetime import date
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel

from app.services.crawler import crawler_service

router = APIRouter()


class CrawlRequest(BaseModel):
    date_from: date
    date_to: date


class CrawlResponse(BaseModel):
    message: str
    task_id: str = "manual_crawl"


@router.post("/manual-crawl", response_model=CrawlResponse)
async def manual_crawl(
    crawl_request: CrawlRequest,
    background_tasks: BackgroundTasks
):
    """Manually trigger crawling for specific date range"""
    print(f"MANUAL CRAWL ENDPOINT CALLED: {crawl_request.date_from} to {crawl_request.date_to}")
    try:
        # Run synchronously for debugging
        contracts_found = await crawler_service.crawl_contracts(
            crawl_request.date_from,
            crawl_request.date_to
        )
        
        return CrawlResponse(
            message=f"Crawling completed for {crawl_request.date_from} to {crawl_request.date_to}. Found {contracts_found} contracts."
        )
    except Exception as e:
        return CrawlResponse(
            message=f"Crawling failed: {str(e)}"
        )


@router.post("/crawl-today", response_model=CrawlResponse)
async def crawl_today(background_tasks: BackgroundTasks):
    """Manually trigger crawling for today's range"""
    background_tasks.add_task(crawler_service.crawl_today)
    
    return CrawlResponse(
        message="Crawling initiated for today's date range"
    )


@router.get("/status")
async def get_crawler_status():
    """Get crawler status"""
    return {
        "status": "running",
        "message": "Crawler service is operational"
    }
