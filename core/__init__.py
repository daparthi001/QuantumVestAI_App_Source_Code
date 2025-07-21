import sys
from pathlib import Path

root = Path(__file__).resolve().parent
base = root.parent / 'ai-stock-platform'
api_core = base / 'api' / 'core'
compat_core = base / 'core'

__path__ = [str(api_core), str(compat_core)]
for p in __path__:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
