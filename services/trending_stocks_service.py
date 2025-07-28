"""Compatibility wrapper for TrendingStocksService."""

# The UI imports ``TrendingStocksService`` from ``services.trending_stocks_service``.
# When the UI is executed in isolation the API package is still available so we
# simply re-export the implementation from ``api.services``.  This thin wrapper
# avoids import errors without duplicating the full service implementation.

import importlib.util
from pathlib import Path

try:  # pragma: no cover - handle missing package gracefully
    # Resolve the path to the API service implementation without importing the
    # entire ``api.services`` package which has heavy side effects (e.g. DB
    # initialization).  Loading the module directly avoids those side effects
    # while providing the same ``TrendingStocksService`` class.
    # Resolve the service path relative to the repository root rather than the
    # ``services`` directory containing this wrapper.
    service_path = (
        Path(__file__).resolve().parent.parent
        / "ai-stock-platform"
        / "api"
        / "services"
        / "trending_stocks_service.py"
    )
    spec = importlib.util.spec_from_file_location(
        "trending_stocks_service", service_path
    )
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        TrendingStocksService = module.TrendingStocksService
    else:  # pragma: no cover - invalid spec
        raise ImportError("Cannot load TrendingStocksService module")
except Exception as exc:
    raise ImportError(
        "TrendingStocksService implementation not found. "
        "Ensure the API package is on PYTHONPATH"
    ) from exc

__all__ = ["TrendingStocksService"]
