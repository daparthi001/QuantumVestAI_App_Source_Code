"""Compatibility wrapper for Alembic migrations."""

# Re-export the main application stock models so that legacy migration scripts
# importing from :mod:`alembic.db.models.stock` continue to work without
# creating duplicate table definitions.
from db.models.stock import Alert, Stock, StockPrice, WatchList  # noqa: F401

__all__ = ["Stock", "WatchList", "StockPrice", "Alert"]
