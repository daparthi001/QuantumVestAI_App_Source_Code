import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

# Import from the current package to avoid conflicts with the top-level
# ``services`` package used for API clients.
from .trending_stocks_service import TrendingStocksService
from social.multi_source_sentiment import MultiSourceSentimentAnalyzer

logger = logging.getLogger(__name__)


async def fetch_and_analyze() -> None:
    """Fetch trending stocks and analyze Twitter sentiment."""
    service = TrendingStocksService()
    try:
        trending = await service.get_trending_stocks(page=1, limit=5)
    except Exception as exc:
        logger.error("Failed fetching trending stocks: %s", exc)
        return

    symbols = [s.get("symbol") for s in trending.get("stocks", [])]
    if not symbols:
        logger.warning("No symbols returned from trending stocks service")
        return

    async with MultiSourceSentimentAnalyzer() as analyzer:
        for symbol in symbols:
            try:
                sentiment = await analyzer.analyze_comprehensive_sentiment(symbol)
                logger.info(
                    "Sentiment for %s: %s", symbol, sentiment.get("sentiment_category")
                )
            except Exception as exc:
                logger.error("Sentiment analysis failed for %s: %s", symbol, exc)


def start_data_fetch_scheduler() -> AsyncIOScheduler:
    """Start scheduler to fetch market and sentiment data every 15 minutes."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # Create a loop if none is running (e.g. during unit tests)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    scheduler = AsyncIOScheduler(event_loop=loop)
    scheduler.add_job(
        fetch_and_analyze,
        trigger=IntervalTrigger(minutes=15),
        id="market_sentiment_fetch",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Data fetch scheduler started")
    return scheduler


if __name__ == "__main__":
    sched = start_data_fetch_scheduler()
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        sched.shutdown()
