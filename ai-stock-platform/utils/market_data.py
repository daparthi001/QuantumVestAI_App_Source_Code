from pathlib import Path
import sys

root_utils = Path(__file__).resolve().parents[2] / 'utils'
if str(root_utils) not in sys.path:
    sys.path.insert(0, str(root_utils))

from market_data import *  # noqa: F401,F403
