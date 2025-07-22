"""
Alembic Environment Configuration
Created: 2025-05-20 04:29:52
Author: daparthi001
"""
import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Add the project root containing the ``core`` package to ``sys.path``.
from pathlib import Path

# Ensure the ``api`` package is importable. When running migrations from a
# packaged installation the ``alembic`` directory may live outside the source
# tree.  If ``api`` can't be imported, walk up the directory tree from this
# file until a parent containing an ``api`` directory is found and add that
# parent to ``sys.path``.
import importlib.util

current = Path(__file__).resolve()

# When executed directly, Python places this file's directory at the start of
# ``sys.path``.  The Alembic directory contains a lightweight ``db`` package
# used only for offline operations which can inadvertently shadow the real
# application package.  Remove this directory so imports resolve to the actual
# modules bundled with the API.
script_dir = str(current.parent)
if script_dir in sys.path:
    sys.path.remove(script_dir)

# Build a list of candidate directories to search for the API package.  Include
# paths from PYTHONPATH so deployments that set it explicitly are handled as
# well as any parent directories of this file.
candidates = [Path(p) for p in os.environ.get("PYTHONPATH", "").split(os.pathsep) if p]
candidates += list(current.parents)

for parent in candidates:
    api_dir = parent / "api"
    alt_dir = parent / "ai-stock-platform" / "api"
    # Prefer an api package that contains the db module to avoid picking up
    # an incomplete sibling directory.
    if api_dir.exists() and (api_dir / "db" / "base" / "base_class.py").exists():
        sys.path.insert(0, str(parent))
        break
    if alt_dir.exists() and (alt_dir / "db" / "base" / "base_class.py").exists():
        sys.path.insert(0, str(parent / "ai-stock-platform"))
        break



# Import the settings from the new shared core config package
try:
    from core.config import settings
except ImportError as e:
    raise ImportError(
        "Could not import settings from 'core.config'. Make sure PYTHONPATH includes the ai-stock-platform directory."
    ) from e

# Import the SQLAlchemy metadata
try:
    # Try importing Base from the new location first (api.db.base.base_class)
    from api.db.base.base_class import Base
except ImportError:
    # Fallback to legacy location (api.db.base)
    from api.db.base import Base
# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def get_url():
    """Get database URL from settings."""
    # Use the new settings structure
    if hasattr(settings, 'SQLALCHEMY_DATABASE_URI'):
        return str(settings.SQLALCHEMY_DATABASE_URI)
    elif hasattr(settings, 'DB') and hasattr(settings.DB, 'build_dsn'):
        return settings.DB.build_dsn()
    raise RuntimeError("No valid database URL found in settings")

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
