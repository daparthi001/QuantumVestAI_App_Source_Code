"""
Database Migration Tests
Created: 2025-05-20 04:29:52
Author: daparthi001
"""
import pytest
pytest.importorskip("alembic")
pytest.importorskip("sqlalchemy")
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.environment import EnvironmentContext
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.config import settings

def test_migrations_can_run():
    """Test that migrations can run successfully."""
    # Create test database engine
    engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
    
    # Create alembic config
    config = Config()
    config.set_main_option("script_location", "alembic")
    
    # Get migration script directory
    script = ScriptDirectory.from_config(config)
    
    def upgrade(rev, context):
        return script._upgrade_revs(script.get_current_head(), rev)
    
    def downgrade(rev, context):
        return script._downgrade_revs(None, rev)
    
    # Create environment context
    with EnvironmentContext(
        config,
        script,
        fn=upgrade,
        destination_rev="head",
        tag=None
    ):
        # Run migrations
        with engine.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=None
            )
            context.run_migrations()
    
    # Verify tables exist
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Check if tables exist
    for table in ['users', 'watchlists', 'watchlist_stocks', 'stock_analysis']:
        result = session.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')")
        assert result.scalar()
    
    session.close()
