"""Compatibility wrapper for the main stock models."""

# Re-export the actual models defined in :mod:`db.models.stock` so that any
# legacy imports from :mod:`api.models.stock` continue to work without creating
# duplicate table definitions during SQLAlchemy setup.
from db.models.stock import Stock, WatchList, StockPrice, Alert  # noqa: F401

__all__ = ["Stock", "WatchList", "StockPrice", "Alert"]
