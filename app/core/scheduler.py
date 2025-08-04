import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import settings
from app.services.crawler import crawler_service


logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


async def scheduled_crawl():
    """Scheduled crawling task"""
    try:
        logger.info("Starting scheduled crawl")
        contracts_found = await crawler_service.crawl_today()
        logger.info(f"Scheduled crawl completed. Found {contracts_found} new contracts.")
    except Exception as e:
        logger.error(f"Error in scheduled crawl: {e}")


def start_scheduler():
    """Start the background scheduler"""
    try:
        scheduler.add_job(
            scheduled_crawl,
            IntervalTrigger(minutes=settings.CRAWLER_INTERVAL_MINUTES),
            id="crawl_contracts",
            name="Crawl VVZ contracts",
            replace_existing=True
        )
        scheduler.start()
        logger.info(f"Scheduler started. Will run every {settings.CRAWLER_INTERVAL_MINUTES} minutes.")
    except Exception as e:
        logger.error(f"Error starting scheduler: {e}")


def stop_scheduler():
    """Stop the background scheduler"""
    try:
        scheduler.shutdown()
        logger.info("Scheduler stopped.")
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")
