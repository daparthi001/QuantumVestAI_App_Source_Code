import os
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..", "ai-stock-platform")
sys.path.append(ROOT)
sys.path.append(os.path.join(ROOT, "api"))

from api.services.data_fetch_scheduler import start_data_fetch_scheduler


def test_data_fetch_scheduler_adds_job():
    scheduler = start_data_fetch_scheduler()
    try:
        jobs = scheduler.get_jobs()
        assert any(job.id == "market_sentiment_fetch" for job in jobs)
    finally:
        scheduler.shutdown()
