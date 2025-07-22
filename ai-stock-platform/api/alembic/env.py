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

if importlib.util.find_spec("api") is None:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "api").exists():
            sys.path.insert(0, str(parent))
            break



# Import the settings module directly from its file path. The
# ``core`` package contains both a legacy ``config.py`` module and a
# ``config`` package.  Python will prefer the module when resolving
# ``api.core.config.settings`` which results in ``ModuleNotFoundError``
# for the nested ``settings`` module.  Loading the module via its file
# path avoids that conflict and ensures the correct configuration is
# used during migrations.

# Locate the installed ``api`` package and build the path to
# ``core/config/settings.py`` relative to it. To avoid importing the
# entire package (which triggers database connections via ``api.__init__``),
# derive the package location using ``importlib.util.find_spec``. This works
# even when the Alembic environment is executed from a different directory
# such as a Docker container where ``env.py`` lives in ``/app``.

spec = importlib.util.find_spec("api")
if spec is None or not spec.submodule_search_locations:
    raise ImportError("Unable to locate installed 'api' package")

api_root = Path(next(iter(spec.submodule_search_locations)))
settings_path = api_root / "core" / "config" / "settings.py"
spec = importlib.util.spec_from_file_location(
    "api.core.config.settings", settings_path
)
settings_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(settings_module)
settings = settings_module.settings
# Import the SQLAlchemy metadata
try:
    from db.base import Base
except ModuleNotFoundError:
    # When the compatibility ``db`` package isn't available (such as when
    # the project is installed without the repository root), fall back to the
    # ``api.db`` package which always ships with the application.
    from api.db.base import Base

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def get_url():
    """Get database URL from settings."""
    return str(settings.SQLALCHEMY_DATABASE_URI)

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
