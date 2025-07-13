import os
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..", "ai-stock-platform")
sys.path.append(ROOT)
sys.path.append(os.path.join(ROOT, "api"))

from api.ml.model_scheduler import start_model_training_scheduler


def test_scheduler_adds_job():
    scheduler = start_model_training_scheduler()
    try:
        jobs = scheduler.get_jobs()
        assert any(job.id == "daily_model_training" for job in jobs)
    finally:
        scheduler.shutdown()
