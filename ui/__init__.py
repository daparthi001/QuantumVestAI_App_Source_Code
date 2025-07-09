from pathlib import Path
import sys

_pkg_path = Path(__file__).resolve().parent.parent / 'ai-stock-platform' / 'ui'
__path__ = [str(_pkg_path)]
if str(_pkg_path) not in sys.path:
    sys.path.insert(0, str(_pkg_path))
