"""Compatibility wrapper for the QuantumVestAI API package."""
import importlib
import logging
import sys
from pathlib import Path

# Path to the actual API package within this repository
_pkg_path = Path(__file__).resolve().parent.parent / "ai-stock-platform" / "api"
_parent = _pkg_path.parent
__path__ = [str(_pkg_path)]

# Ensure the API package path has priority on sys.path
for p in (_pkg_path, _parent):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

# Mirror logic from the real API __init__ to expose common modules
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("quantumvestai_api_wrapper")
logger.info("Loading API compatibility wrapper")

importlib.invalidate_caches()
core_pkg = importlib.import_module("api.core")
sys.modules.setdefault("core", core_pkg)
for name in ("exceptions", "responses", "validation", "database", "security", "models"):
    submod = f"api.core.{name}"
    try:
        sys.modules.setdefault(f"core.{name}", importlib.import_module(submod))
    except Exception:
        pass

# Expose `db` package as top level alias
try:
    db_pkg = importlib.import_module("api.db")
    sys.modules.setdefault("db", db_pkg)
except Exception:
    pass

# Load FastAPI app if available
try:
    from api.main import app
    logger.info("Loaded FastAPI app with %d routes", len(app.routes))
except Exception as e:  # pragma: no cover
    logger.error("Failed to load app from api.main: %s", e)
    app = None

__all__ = ["app"]
