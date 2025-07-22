"""Compatibility wrapper for API db package."""
import importlib
import sys
from pathlib import Path

# Ensure api package path is on sys.path. ``db`` lives at the repository root
# so ``api`` is located one level up under ``ai-stock-platform/api``.
repo_root = Path(__file__).resolve().parent
api_path = repo_root.parent / "ai-stock-platform" / "api"
if api_path.exists() and str(api_path) not in sys.path:
    sys.path.insert(0, str(api_path))

# Make this module appear as a package pointing to the real ``api/db``
# directory so Python can locate submodules under ``db``.
__path__ = [str(api_path / "db")]

# Avoid circular import issues by registering this module under the "db" name
# before loading the actual API package. Submodules inside ``api.db`` sometimes
# import ``db`` during initialization. By setting the alias early, those imports
# will resolve to this compatibility wrapper instead of failing with
# ``ModuleNotFoundError``.
sys.modules.setdefault("db", sys.modules[__name__])

api_db = importlib.import_module("api.db")

# Expose common submodules so `import db.session` works
for sub in ("session", "models", "base", "base_class", "mixins", "init_db", "rds_session"):
    try:
        sys.modules[f"db.{sub}"] = importlib.import_module(f"api.db.{sub}")
    except Exception:
        pass

# Re-export all public attributes from api.db
__all__ = getattr(api_db, "__all__", [])
for name in __all__:
    globals()[name] = getattr(api_db, name)
