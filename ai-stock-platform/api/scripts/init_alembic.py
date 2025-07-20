"""
Initialize Alembic migration environment
"""
import os
import sys
from pathlib import Path


def init_alembic():
    """Initialize Alembic migration environment"""
    try:
        # Ensure we're in the api directory where alembic.ini resides
        project_root = Path(__file__).resolve().parents[2]
        api_dir = project_root / "api"
        os.chdir(api_dir)
        
        # Create migrations directory if it doesn't exist
        migrations_dir = api_dir / "alembic" / "versions"
        migrations_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize alembic if not already initialized
        if not (api_dir / "alembic.ini").exists():
            os.system("alembic init alembic")
            print("✅ Initialized Alembic")
        
        # Create initial migration
        os.system("alembic revision --autogenerate -m 'Initial migration'")
        print("✅ Created initial migration")
        
        # Apply migrations
        os.system("alembic upgrade head")
        print("✅ Applied migrations")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    init_alembic()
