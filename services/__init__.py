"""Compatibility package exposing shared services for tests and runtime."""
from pathlib import Path
import sys

_here = Path(__file__).resolve().parent
# Paths to the actual service implementations used by the UI and API
_ui_services = _here.parent / "ai-stock-platform" / "ui" / "services"
_api_services = _here.parent / "ai-stock-platform" / "api" / "services"

# Include both this directory (for test stubs) and the real UI services path
__path__ = [str(_here), str(_api_services), str(_ui_services)]

# Insert paths so that the repository root services take precedence.
# Add paths in reverse order so ``_here`` ends up first.
for p in reversed(__path__):
    if p not in sys.path:
        sys.path.insert(0, p)
