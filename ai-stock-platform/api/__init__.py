"""
QuantumVestAI API Package
Created: 2025-06-19 07:11:20
Author: daparthi001
"""
import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("quantumvestai_api")
logger.info("Initializing API package")

# Ensure this package path has priority in sys.path so that modules like
# ``core`` resolve to ``api.core`` rather than the sibling package at the
# repository root.
_pkg_path = Path(__file__).resolve().parent
_parent = _pkg_path.parent
if str(_pkg_path) not in sys.path:
    sys.path.insert(0, str(_pkg_path))
if str(_parent) not in sys.path:
    sys.path.insert(0, str(_parent))

# Map the name ``core`` to this package's ``core`` module so imports of ``core``
# resolve correctly even when a sibling ``ui.core`` package exists.
import importlib
sys.modules.setdefault('core', importlib.import_module('api.core'))

# Remove local ``multipart`` stub if present so the real ``python-multipart``
# package can be used by FastAPI/Starlette.
sys.modules.pop('multipart', None)
for p in list(sys.path):
    if 'site-packages' in p:
        sys.path.remove(p)
        sys.path.insert(0, p)

try:
    from .main import app
    # Re-insert package path at the front in case submodules modified sys.path
    if str(_pkg_path) in sys.path:
        sys.path.remove(str(_pkg_path))
    sys.path.insert(0, str(_pkg_path))
    logger.info(
        "Successfully imported app from api.main with %d routes", len(app.routes)
    )
except Exception as e:  # pragma: no cover - optional dependency may be missing
    logger.error(f"Failed to import app from api.main: {e}")
    app = None

# Export the app variable for external use
__all__ = ["app"]