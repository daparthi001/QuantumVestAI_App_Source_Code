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

"""Compatibility loader for the shared configuration module.

This package used to provide UI specific settings but the real implementation
now lives in the shared ``core`` package at the repository root.  When the UI
package ends up first on ``sys.path`` importing ``core.config`` resolves to this
package which lacks the actual configuration objects.  Importing from here would
therefore cause a circular import.  To maintain backwards compatibility we
dynamically locate and load the real settings module directly from its file
path, bypassing the Python package resolution mechanism.
"""

import importlib.util
import sys
from pathlib import Path

candidate = Path(__file__).resolve()
project_root: Path | None = None

# Walk upwards until we find the real ``core/config/settings.py``.  Prefer an
# ``ai-stock-platform`` package layout if present but fall back to any parent
# containing ``core/config``.
for parent in candidate.parents:
    if (parent / "ai-stock-platform" / "core" / "config" / "settings.py").exists():
        project_root = parent / "ai-stock-platform"
        break
    if (parent / "core" / "config" / "settings.py").exists() and project_root is None:
        project_root = parent

if project_root is None:
    raise ImportError("Unable to locate shared core configuration module")

settings_path = project_root / "core" / "config" / "settings.py"

spec = importlib.util.spec_from_file_location("core_real_settings", settings_path)
if spec is None or spec.loader is None:  # pragma: no cover - environment issue
    raise ImportError(f"Could not load settings from {settings_path}")

module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

Settings = module.Settings  # type: ignore[attr-defined]
get_settings = module.get_settings  # type: ignore[attr-defined]
settings = module.settings  # type: ignore[attr-defined]

__all__ = ["settings", "Settings", "get_settings"]
