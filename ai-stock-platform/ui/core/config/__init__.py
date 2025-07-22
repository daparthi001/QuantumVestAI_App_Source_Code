"""Compatibility layer for configuration imports.

This module used to contain the UI specific configuration.  The real
settings implementation now lives in ``core.config`` at the repository
root.  When the ``ui`` package ends up ahead of the shared ``core``
package on ``sys.path`` importing ``core.config`` would resolve to this
package which previously lacked the ``get_settings`` helper causing
``ImportError`` during application start up.

To keep backward compatibility and avoid import errors we dynamically
locate the project root and re-export the objects from the shared
``core.config`` module.
"""

from __future__ import annotations

import sys
from pathlib import Path

candidate = Path(__file__).resolve()
project_root: Path | None = None

for parent in candidate.parents:
    if (parent / "core" / "config").exists():
        project_root = parent
        break

if project_root and str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from core.config import Settings, get_settings, settings

__all__ = ["settings", "Settings", "get_settings"]
