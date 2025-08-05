"""Compatibility wrapper for MarketDataService."""

import importlib.util
from pathlib import Path


try:  # pragma: no cover - handle missing package gracefully
    service_path = (
        Path(__file__).resolve().parent.parent
        / "ai-stock-platform"
        / "api"
        / "services"
        / "market_data_service.py"
    )
    spec = importlib.util.spec_from_file_location(
        "market_data_service", service_path
    )
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        MarketDataService = module.MarketDataService
    else:  # pragma: no cover - invalid spec
        raise ImportError("Cannot load MarketDataService module")
except Exception as exc:  # pragma: no cover - import failures
    raise ImportError(
        "MarketDataService implementation not found. Ensure the API package is on PYTHONPATH"
    ) from exc


__all__ = ["MarketDataService"]

