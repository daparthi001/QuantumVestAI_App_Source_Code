"""Compatibility wrapper so ``import core`` works in tests."""
from pathlib import Path
import sys

root = Path(__file__).resolve().parent
# The repository structure places the actual ``core`` packages inside the
# ``ai-stock-platform`` directory next to this compatibility wrapper.  There
# are two relevant packages:
#   - ``ai-stock-platform/core``     (general utilities)
#   - ``ai-stock-platform/api/core`` (API-specific utilities such as security)
#
# Both locations need to be on ``__path__`` so imports like ``core.config`` and
# ``core.security`` resolve correctly during tests.
_pkg = root.parent / "ai-stock-platform" / "core"
_api_pkg = root.parent / "ai-stock-platform" / "api" / "core"
__path__ = [str(_pkg), str(_api_pkg)]

for p in [str(_pkg), str(_api_pkg), str(_pkg.parent), str(_api_pkg.parent)]:
    if p not in sys.path:
        sys.path.insert(0, p)
