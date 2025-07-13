"""
Database Connection Tests
Created: 2025-05-20 05:09:26
Author: daparthi001
"""
import pytest

pytest.importorskip("sqlalchemy")
import logging
import os
from datetime import datetime
from typing import Generator, Optional

from core.config import settings
from core.logger import setup_logger
from db.session import Base, get_db, get_db_async
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

# Setup logging
logger = setup_logger(__name__)

def get_test_db_url() -> str:
    """Get test database URL from environment or default to SQLite."""
    return os.getenv(
        "TEST_DATABASE_URL",
        "sqlite:///./test.db"
    )

def create_test_engine():
    """Create SQLAlchemy engine for tests."""
    return create_engine(
        get_test_db_url(),
        pool_pre_ping=True,
        echo=False
    )

def get_test_session() -> Generator[Session, None, None]:
    """Get test database session."""
    engine = create_test_engine()
    TestSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
    
    try:
        db = TestSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture(scope="session")
def test_engine():
    """Fixture for database engine."""
    engine = create_test_engine()
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        yield engine
    finally:
        # Drop all tables after tests
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def test_db(test_engine) -> Generator[Session, None, None]:
    """Fixture for database session."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

class TestDatabaseConnection:
    """Test database connection and basic operations."""

    def test_database_connection(self, test_db: Session):
        """Test basic database connectivity."""
        try:
            # Execute simple query
            result = test_db.execute(text("SELECT 1"))
            assert result.scalar() == 1
            logger.info("Database connection test successful")
        except SQLAlchemyError as e:
            logger.error(f"Database connection test failed: {e}")
            raise

    def test_database_tables(self, test_db: Session):
        """Test if all required tables exist."""
        try:
            # Get list of all tables
            inspector = test_db.get_bind().dialect.inspector
            tables = inspector.get_table_names()
            
            # Required tables
            required_tables = {
                "users",
                "stocks",
                "portfolios",
                "transactions",
                "alerts",
                "watchlists"
            }
            
            # Check if all required tables exist
            missing_tables = required_tables - set(tables)
            assert not missing_tables, f"Missing tables: {missing_tables}"
            
            logger.info(f"All required tables exist: {', '.join(required_tables)}")
        except SQLAlchemyError as e:
            logger.error(f"Database tables test failed: {e}")
            raise

    def test_database_permissions(self, test_db: Session):
        """Test database user permissions."""
        operations = [
            ("SELECT", "SELECT 1"),
            ("INSERT", """
                INSERT INTO users (username, email, hashed_password)
                VALUES ('test_user', 'test@example.com', 'hashed_password')
            """),
            ("UPDATE", """
                UPDATE users 
                SET email = 'updated@example.com'
                WHERE username = 'test_user'
            """),
            ("DELETE", """
                DELETE FROM users
                WHERE username = 'test_user'
            """)
        ]
        
        for operation, query in operations:
            try:
                test_db.execute(text(query))
                test_db.commit()
                logger.info(f"{operation} permission test successful")
            except SQLAlchemyError as e:
                logger.error(f"{operation} permission test failed: {e}")
                raise

    def test_connection_pool(self, test_engine):
        """Test database connection pool configuration."""
        try:
            # Check pool settings
            pool = test_engine.pool
            
            assert pool.size() >= 0, "Invalid pool size"
            assert pool._overflow >= 0, "Invalid overflow size"
            
            # Test multiple connections
            connections = []
            for _ in range(3):
                conn = test_engine.connect()
                connections.append(conn)
                
            # Verify connections are working
            for conn in connections:
                result = conn.execute(text("SELECT 1"))
                assert result.scalar() == 1
                
            # Close connections
            for conn in connections:
                conn.close()
                
            logger.info("Connection pool test successful")
        except SQLAlchemyError as e:
            logger.error(f"Connection pool test failed: {e}")
            raise

    def test_transaction_rollback(self, test_db: Session):
        """Test transaction rollback functionality."""
        try:
            # Start transaction
            test_db.begin_nested()
            
            # Insert test data
            test_db.execute(
                text("""
                    INSERT INTO users (username, email, hashed_password)
                    VALUES ('rollback_test', 'rollback@example.com', 'test_password')
                """)
            )
            
            # Verify data exists
            result = test_db.execute(
                text("SELECT username FROM users WHERE username = 'rollback_test'")
            )
            assert result.scalar() == 'rollback_test'
            
            # Rollback transaction
            test_db.rollback()
            
            # Verify data was rolled back
            result = test_db.execute(
                text("SELECT username FROM users WHERE username = 'rollback_test'")
            )
            assert result.scalar() is None
            
            logger.info("Transaction rollback test successful")
        except SQLAlchemyError as e:
            logger.error(f"Transaction rollback test failed: {e}")
            raise

    @pytest.mark.asyncio
    async def test_async_connection(self):
        """Test async database operations."""
        try:
            # Get async session
            async for db in get_db_async():
                # Execute simple query
                result = await db.execute(text("SELECT 1"))
                assert await result.scalar() == 1
                
                logger.info("Async database connection test successful")
                break
        except Exception as e:
            logger.error(f"Async database connection test failed: {e}")
            raise

def main():
    """Main function to run tests directly."""
    import sys
    pytest.main(sys.argv)

if __name__ == "__main__":
    main()
