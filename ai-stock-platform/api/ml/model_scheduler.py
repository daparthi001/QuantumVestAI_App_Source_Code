from __future__ import annotations

"""Simple scheduler to retrain ML models periodically."""

import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger("model_scheduler")


def train_models_job() -> None:
    """Job that retrains all models."""
    logger.info("Starting scheduled model training...")
    from .train_models import ModelTrainer
    trainer = ModelTrainer()
    try:
        trainer.train_all_models()
        logger.info("Model training completed")
    except Exception as exc:
        logger.exception("Model training failed: %s", exc)
        # Notify admin or log additional details
        logger.error("Admin notification: Model training encountered an error.")


def start_model_training_scheduler() -> BackgroundScheduler:
    """Start the background scheduler for model training.

    Returns the scheduler instance so callers can manage its lifecycle.
    """
    scheduler = BackgroundScheduler()
    # Run every day at 02:00 UTC
    scheduler.add_job(
        train_models_job,
        CronTrigger(hour=2, minute=0),
        id="daily_model_training",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Model training scheduler started at %s", datetime.utcnow())
    return scheduler


if __name__ == "__main__":
    sched = start_model_training_scheduler()
    try:
        while True:
            # Keep the main thread alive to allow scheduler to run
            sched.print_jobs()
            import time
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        sched.shutdown()
