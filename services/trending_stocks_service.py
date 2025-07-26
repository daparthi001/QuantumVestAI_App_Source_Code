"""Compatibility wrapper for TrendingStocksService."""

# The UI imports ``TrendingStocksService`` from ``services.trending_stocks_service``.
# When the UI is executed in isolation the API package is still available so we
# simply re-export the implementation from ``api.services``.  This thin wrapper
# avoids import errors without duplicating the full service implementation.

try:
    from api.services.trending_stocks_service import TrendingStocksService
except Exception as exc:  # pragma: no cover - API package missing in test envs
    raise ImportError(
        "TrendingStocksService implementation not found. "
        "Ensure the API package is on PYTHONPATH"
    ) from exc

__all__ = ["TrendingStocksService"]
