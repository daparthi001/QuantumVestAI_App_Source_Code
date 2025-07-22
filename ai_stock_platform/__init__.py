import sys
from pathlib import Path

# Resolve path to the existing `ai-stock-platform` folder
_pkg_path = Path(__file__).resolve().parent.parent / 'ai-stock-platform'
__path__ = [str(_pkg_path)]
if str(_pkg_path) not in sys.path:
    sys.path.insert(0, str(_pkg_path))
