from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
import os
import sys

# Add the parent directory to the path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import Base from your models
from api.db.base_class import Base
# Import all models so Alembic can detect them
from api.db.models import *

# This is the Alembic Config object
config = context.config

# Configure SQLAlchemy URL from environment variables
section = config.config_ini_section
config.set_section_option(section, "DB_USER", os.environ.get("DB_USER", "postgres"))
config.set_section_option(section, "DB_PASSWORD", os.environ.get("DB_PASSWORD", "postgres"))
config.set_section_option(section, "DB_HOST", os.environ.get("DB_HOST", "localhost"))
config.set_section_option(section, "DB_PORT", os.environ.get("DB_PORT", "5432"))
config.set_section_option(section, "DB_NAME", os.environ.get("DB_NAME", "quantumvestai"))

# Interpret the config file for Python logging
fileConfig(config.config_file_name)

# Set the MetaData object for Alembic to use
target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
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
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
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