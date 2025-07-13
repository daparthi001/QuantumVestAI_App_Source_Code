import sys
from pathlib import Path

# Make the API models package importable as ``models`` without side effects.
root_dir = Path(__file__).resolve().parent
api_models = root_dir / 'ai-stock-platform' / 'api' / 'models'
__path__ = [str(root_dir), str(api_models)]
for p in __path__:
    if p not in sys.path:
        sys.path.insert(0, p)
