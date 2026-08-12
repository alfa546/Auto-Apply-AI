import asyncio
import logging
from src.app.db.database import SessionLocal
from src.app.core.config import settings
from src.app.services.search.aggregator import SearchAggregator

logger = logging.getLogger(__name__)

# Global flag to track background scheduler loop task
_scheduler_task = None
_shutdown_event = asyncio.Event()

async def start_search_scheduler():
    global _scheduler_task
    if _scheduler_task is not None:
        logger.warning("Search scheduler background task is already running.")
        return
        
    _shutdown_event.clear()
    _scheduler_task = asyncio.create_task(run_scheduler_loop())
    logger.info("Search scheduler background daemon started successfully.")

async def stop_search_scheduler():
    global _scheduler_task
    if _scheduler_task is None:
        return
        
    logger.info("Stopping search scheduler background daemon...")
    _shutdown_event.set()
    try:
        # Wait a moment for it to terminate or cancel it
        await asyncio.wait_for(_scheduler_task, timeout=5.0)
    except Exception:
        if _scheduler_task:
            _scheduler_task.cancel()
    _scheduler_task = None
    logger.info("Search scheduler background daemon stopped.")

async def run_scheduler_loop():
    try:
        aggregator = SearchAggregator()
    except Exception as e:
        logger.error(f"Failed to initialize SearchAggregator (non-fatal): {e}")
        return

    interval_seconds = settings.SEARCH_INTERVAL_HOURS * 3600

    try:
        await asyncio.sleep(30.0)
    except asyncio.CancelledError:
        return

    while not _shutdown_event.is_set():
        logger.info("Background scheduler executing periodic search crawl...")
        db = None
        try:
            db = SessionLocal()
            queries = ["Python Developer", "React Developer", "AI Engineer"]
            for query in queries:
                if _shutdown_event.is_set():
                    break
                await aggregator.run_aggregation(db, query)
                await asyncio.sleep(2.0)
        except Exception as e:
            logger.error(f"Error during scheduled background search crawl (non-fatal): {e}")
        finally:
            if db:
                db.close()

        elapsed = 0
        while elapsed < interval_seconds and not _shutdown_event.is_set():
            try:
                await asyncio.sleep(10.0)
                elapsed += 10
            except asyncio.CancelledError:
                return
