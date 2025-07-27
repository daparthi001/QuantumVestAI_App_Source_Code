"""Utility package compatibility wrapper.

This module exposes the utility packages from both the UI and API portions of
the project under a single namespace.  Earlier revisions only exposed the UI
utilities which meant imports such as ``utils.data_loader`` failed during test
collection.  The path handling has been extended to include the API utilities as
well so that ``import utils.*`` works consistently across the codebase.
"""

from pathlib import Path
import sys

root = Path(__file__).resolve().parent.parent / "ai-stock-platform"
ui_utils = root / "ui" / "utils"
api_utils = root / "api" / "utils"

__path__ = [str(ui_utils), str(api_utils)]

for pkg_path in (ui_utils, api_utils):
    if str(pkg_path) not in sys.path:
        sys.path.insert(0, str(pkg_path))
