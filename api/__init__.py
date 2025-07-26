"""Compatibility wrapper so ``import api`` works in tests."""
from pathlib import Path
import sys

root = Path(__file__).resolve().parent.parent
_pkg = root / "ai-stock-platform" / "api"
__path__ = [str(_pkg)]
if str(_pkg) not in sys.path:
    sys.path.insert(0, str(_pkg))
if str(_pkg.parent) not in sys.path:
    sys.path.insert(0, str(_pkg.parent))
