"""Compatibility wrapper so ``import api`` works in tests.

This module adjusts ``sys.path`` so the actual API package located under
``ai-stock-platform/api`` can be imported as ``api``.  It also mirrors the
real package's initialization logic to expose expected modules and aliases
(such as ``core`` and ``db``).
"""
from pathlib import Path
import sys
import importlib

root = Path(__file__).resolve().parent.parent
_pkg = root / "ai-stock-platform" / "api"
__path__ = [str(_pkg)]
if str(_pkg) not in sys.path:
    sys.path.insert(0, str(_pkg))
if str(_pkg.parent) not in sys.path:
    sys.path.insert(0, str(_pkg.parent))

# Replicate key side effects from the real package's ``__init__``
core_pkg = importlib.import_module("api.core")
sys.modules.setdefault("core", core_pkg)
for name in ("exceptions", "responses", "validation", "database", "security", "models"):
    submod = f"api.core.{name}"
    try:
        sys.modules.setdefault(f"core.{name}", importlib.import_module(submod))
    except Exception:
        pass

db_pkg = importlib.import_module("api.db")
sys.modules.setdefault("db", db_pkg)

models_pkg = importlib.import_module("api.models")
sys.modules.setdefault("models", models_pkg)

try:  # pragma: no cover - optional dependency may be missing
    from api.main import app
except Exception:
    app = None

__all__ = ["app"]
