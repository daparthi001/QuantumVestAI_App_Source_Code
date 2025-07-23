import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from agents import DataFetchAgent, DataAnalysisAgent, DataPipelineManager

logger = logging.getLogger(__name__)

async def run_pipeline() -> None:
    """Example job that runs a simple data pipeline."""
    fetch_agent = DataFetchAgent("sample", "https://example.com/data")
    analysis_agent = DataAnalysisAgent("noop", lambda d: d)
    manager = DataPipelineManager([fetch_agent], [analysis_agent])
    try:
        await manager.run()
    except Exception as exc:  # pragma: no cover - scheduler context
        logger.error("Pipeline job failed: %s", exc)


def start_data_pipeline_scheduler() -> AsyncIOScheduler:
    """Start scheduler that periodically runs the data pipeline."""
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        run_pipeline,
        trigger=IntervalTrigger(minutes=5),
        id="data_pipeline_run",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Data pipeline scheduler started")
    return scheduler
