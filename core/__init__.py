"""Compatibility wrapper so ``import core`` works in tests."""
from pathlib import Path
import sys

root = Path(__file__).resolve().parent
# The repository structure places the actual ``core`` package inside the
# ``ai-stock-platform`` directory next to this compatibility wrapper.  The
# previous implementation incorrectly assumed that directory was located
# inside this package which resulted in an invalid search path like
# ``core/ai-stock-platform/core``.  That path does not exist, preventing
# imports such as ``core.config`` from resolving in the test environment.
#
# Compute the package location relative to the parent of this file so the
# full path ``<repo>/ai-stock-platform/core`` is added to ``__path__``.
_pkg = root.parent / "ai-stock-platform" / "core"
__path__ = [str(_pkg)]
if str(_pkg) not in sys.path:
    sys.path.insert(0, str(_pkg))
if str(_pkg.parent) not in sys.path:
    sys.path.insert(0, str(_pkg.parent))
