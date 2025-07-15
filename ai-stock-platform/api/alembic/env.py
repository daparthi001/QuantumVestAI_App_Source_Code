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

project_root = Path(__file__).resolve().parents[2]
# Handle cases where only the ``api`` directory is packaged separately and the
# project root one level up does not contain the ``core`` package. In Docker
# containers ``env.py`` may live at ``/app/api/alembic`` where ``/app/api``
# holds the actual source tree.
if not (project_root / "core").exists():
    alt_root = Path(__file__).resolve().parents[1]
    if (alt_root / "core").exists():
        project_root = alt_root
    else:
        project_root = project_root.parent
# Prepend the project root to ``sys.path`` so the top-level ``core`` package
# is resolved before the local ``core`` directory inside the Alembic folder.
sys.path.insert(0, str(project_root))

# Import settings directly from the API package to avoid
# the ``core.config`` module shadowing the package when the
# project is installed. Using the explicit path ensures the
# ``settings`` instance is imported reliably across different
# deployment scenarios.
from api.core.config.settings import settings
# Import the SQLAlchemy metadata
from db.base import Base

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
