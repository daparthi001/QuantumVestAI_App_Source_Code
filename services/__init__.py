"""Compatibility package that forwards imports to the UI services module."""
import sys
from pathlib import Path
_pkg_path = Path(__file__).resolve().parent.parent / 'ai-stock-platform' / 'ui' / 'services'
__path__ = [str(_pkg_path)]
if str(_pkg_path) not in sys.path:
    sys.path.insert(0, str(_pkg_path))
