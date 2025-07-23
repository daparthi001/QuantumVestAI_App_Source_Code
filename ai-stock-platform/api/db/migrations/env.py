"""
Alembic Environment Configuration
Created: 2025-05-19 05:29:26
Author: daparthi001
"""
from logging.config import fileConfig

from alembic import context

# Ensure the ``api`` package can be imported when this file is executed from
# outside the source tree. If ``api`` is not importable, walk up the directory
# hierarchy until we locate a parent containing an ``api`` folder and add that
# parent to ``sys.path``.
import sys
from pathlib import Path
import importlib.util

current = Path(__file__).resolve()
for parent in current.parents:
    if (parent / "api").exists():
        sys.path.insert(0, str(parent))
        break
    alt = parent / "ai-stock-platform"
    if (alt / "api").exists():
        sys.path.insert(0, str(alt))
        break

# Import settings directly from the API package to avoid the
# ``core.config`` module shadowing the package when installed
# without the full repository. This ensures the Alembic environment
# can always access the correct configuration.
from core.config import settings
try:
    from db.base import Base
except ModuleNotFoundError:
    try:
        from api.db.base import Base
    except ModuleNotFoundError:
        from api.db.base.base_class import Base
from sqlalchemy import engine_from_config, pool

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def get_url():
    return str(settings.SQLALCHEMY_DATABASE_URI)

def run_migrations_offline():
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
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
