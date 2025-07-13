"""List database tables using the application's SQLAlchemy engine."""

import logging
import sys
from pathlib import Path

from sqlalchemy import inspect

# Ensure the parent directory (which contains the `db` package) is on the path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from db.session import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main() -> None:
    """Print all table names in the connected database."""
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        if not tables:
            print("No tables found.")
        else:
            print("Available tables:")
            for table in tables:
                print(f"- {table}")
    except Exception as e:
        logger.error("Failed to list tables: %s", e)
        raise

if __name__ == "__main__":
    main()
