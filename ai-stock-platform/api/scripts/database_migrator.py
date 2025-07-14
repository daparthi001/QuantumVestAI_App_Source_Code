#!/usr/bin/env python3
"""Database Migration Script for QuantumVestAI
Ensures required columns exist and creates indexes if missing.
"""

import asyncio
import asyncpg
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseMigrator:
    def __init__(self, db_url=None):
        """Initialize the migrator with a database URL.

        The migrator mirrors the application's database configuration logic.
        ``DATABASE_URL`` takes precedence, followed by ``ASYNC_DATABASE_URL``.
        If neither are set, individual ``DB_*`` variables are used to build the
        connection string. Finally a sensible local default is used.
        """

        # default_url = "postgresql://postgres:postgres@localhost:5432/quantumvestai"

        # env_url = db_url or os.getenv("DATABASE_URL") or os.getenv("ASYNC_DATABASE_URL")

        if not env_url:
            db_user = os.getenv("DB_USER", "postgres")
            db_password = os.getenv("DB_PASSWORD", "postgres")
            db_host = os.getenv("DB_HOST", "localhost")
            db_port = os.getenv("DB_PORT", "5432")
            db_name = os.getenv("DB_NAME", "quantumvestai")
            env_url = os.getenv("DB_URL", "postgresql://${db_user}:${db_password}@${db_host}:5432/${db_name}")

        # async SQLAlchemy URLs may contain the ``+asyncpg`` driver indicator
        if env_url.startswith("postgresql+asyncpg://"):
            env_url = env_url.replace("postgresql+asyncpg://", "postgresql://")

        self.db_url = env_url or default_url
        self.connection = None

    async def connect(self):
        try:
            self.connection = await asyncpg.connect(self.db_url)
            logger.info("Connected to database successfully")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    async def disconnect(self):
        if self.connection:
            await self.connection.close()
            logger.info("Disconnected from database")

    async def check_table_exists(self, table_name: str) -> bool:
        query = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name = $1
        );
        """
        return await self.connection.fetchval(query, table_name)

    async def check_column_exists(self, table_name: str, column_name: str) -> bool:
        query = """
        SELECT EXISTS (
            SELECT FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = $1
              AND column_name = $2
        );
        """
        return await self.connection.fetchval(query, table_name, column_name)

    async def create_users_table(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            username VARCHAR(100) UNIQUE NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            is_active BOOLEAN DEFAULT TRUE,
            is_verified BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP WITH TIME ZONE
        );
        """
        await self.connection.execute(create_table_query)
        logger.info("Users table created successfully")

    async def add_missing_columns(self):
        users_exists = await self.check_table_exists('users')
        if not users_exists:
            logger.info("Users table doesn't exist, creating it...")
            await self.create_users_table()
            return

        has_hashed_password = await self.check_column_exists('users', 'hashed_password')
        if not has_hashed_password:
            logger.info("Adding hashed_password column to users table...")
            await self.connection.execute(
                "ALTER TABLE users ADD COLUMN hashed_password VARCHAR(255)"
            )
            logger.info("hashed_password column added successfully")
        else:
            logger.info("hashed_password column already exists")

        missing_columns = [
            ('is_active', 'BOOLEAN DEFAULT TRUE'),
            ('is_verified', 'BOOLEAN DEFAULT FALSE'),
            ('created_at', 'TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP'),
            ('updated_at', 'TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP'),
            ('last_login', 'TIMESTAMP WITH TIME ZONE'),
            ('first_name', 'VARCHAR(100)'),
            ('last_name', 'VARCHAR(100)')
        ]

        for column_name, column_def in missing_columns:
            has_column = await self.check_column_exists('users', column_name)
            if not has_column:
                logger.info(f"Adding {column_name} column to users table...")
                await self.connection.execute(
                    f"ALTER TABLE users ADD COLUMN {column_name} {column_def}"
                )
                logger.info(f"{column_name} column added successfully")

    async def create_indexes(self):
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);",
            "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);",
            "CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);",
            "CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);"
        ]
        for index_query in indexes:
            await self.connection.execute(index_query)
            logger.info(f"Index created or exists: {index_query}")

    async def create_migration_log_table(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS migration_log (
            id SERIAL PRIMARY KEY,
            migration_name VARCHAR(255) NOT NULL,
            executed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            success BOOLEAN DEFAULT TRUE,
            error_message TEXT
        );
        """
        await self.connection.execute(create_table_query)
        logger.info("Migration log table created")

    async def log_migration(
        self,
        migration_name: str,
        success: bool = True,
        error_message: str | None = None,
    ) -> None:
        """Record the result of a migration run.

        If no database connection is available, the log entry is skipped to
        avoid further errors when the connection attempt itself fails.
        """
        if not self.connection:
            logger.warning(
                "Skipping migration log because no database connection is available"
            )
            return

        query = """
        INSERT INTO migration_log (migration_name, success, error_message)
        VALUES ($1, $2, $3);
        """
        await self.connection.execute(query, migration_name, success, error_message)

    async def run_migration(self):
        try:
            await self.connect()
            await self.create_migration_log_table()
            await self.add_missing_columns()
            await self.create_indexes()
            await self.log_migration("add_hashed_password_column", True)
            logger.info("Migration completed successfully!")
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            await self.log_migration("add_hashed_password_column", False, str(e))
            raise
        finally:
            await self.disconnect()

async def main():
    db_url = os.getenv('DATABASE_URL')
    migrator = DatabaseMigrator(db_url)
    await migrator.run_migration()

if __name__ == "__main__":
    asyncio.run(main())
