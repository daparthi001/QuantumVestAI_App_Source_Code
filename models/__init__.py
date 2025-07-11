import sys
from pathlib import Path
_pkg_path = Path(__file__).resolve().parent.parent / 'ai-stock-platform' / 'models'
__path__ = [str(_pkg_path)]
if str(_pkg_path) not in sys.path:
    sys.path.insert(0, str(_pkg_path))

from importlib import import_module
sys.modules[__name__] = import_module('api.models')
