"""Compatibility package exposing shared services for tests and runtime."""
from pathlib import Path
import sys

_here = Path(__file__).resolve().parent
_ui_services = _here.parent / "ai-stock-platform" / "ui" / "services"

# Include both this directory (for test stubs) and the real UI services path
__path__ = [str(_here), str(_ui_services)]

for p in __path__:
    if p not in sys.path:
        sys.path.insert(0, p)
