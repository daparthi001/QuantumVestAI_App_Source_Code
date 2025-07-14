import logging
import os
import sys
import psycopg2

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("db_migration")

# Connection details from environment or default values
DB_HOST = os.getenv("POSTGRES_SERVER", os.getenv("DB_HOST", "localhost"))
DB_PORT = os.getenv("POSTGRES_PORT", os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("POSTGRES_DB", os.getenv("DB_NAME", "postgres"))
DB_USER = os.getenv("POSTGRES_USER", os.getenv("DB_USER", "postgres"))
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", os.getenv("DB_PASSWORD", ""))

conn_str = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

logger.info("Connecting to %s", conn_str)
try:
    conn = psycopg2.connect(conn_str)
except Exception as exc:
    logger.error("Failed to connect: %s", exc)
    sys.exit(1)

with conn:
    with conn.cursor() as cur:
        cur.execute("""SELECT column_name FROM information_schema.columns
                        WHERE table_name='users' AND column_name='hashed_password'""")
        if cur.fetchone():
            logger.info("Column 'hashed_password' already exists")
        else:
            logger.info("Adding missing 'hashed_password' column")
            cur.execute("ALTER TABLE users ADD COLUMN hashed_password VARCHAR(255)")
            logger.info("Column added successfully")

logger.info("Migration complete")
