"""Utility script to refresh market data in the database.

This script fetches the latest price information for all stocks
stored in the database and updates the corresponding records.
It is intended to be run as a CronJob (see `ci-cd/k8s/dev/10-db-update-cronjob.yaml`).
"""

import asyncio
import logging
from typing import List

from db.session import SessionLocal
from db.models.stock import Stock
from services.stock_service import StockService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def update_all_stocks() -> None:
    """Fetch latest data for all stocks and update the database."""
    db = SessionLocal()
    service = StockService(db)
    try:
        stocks: List[Stock] = db.query(Stock).all()
        if not stocks:
            logger.info("No stocks found in database; nothing to update")
            return

        for stock in stocks:
            try:
                updated = await service.update_stock_data(stock.ticker)
                if updated:
                    logger.info("Updated %s", stock.ticker)
                else:
                    logger.info("No data returned for %s", stock.ticker)
            except Exception as exc:
                logger.warning("Failed to update %s: %s", stock.ticker, exc)
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(update_all_stocks())
