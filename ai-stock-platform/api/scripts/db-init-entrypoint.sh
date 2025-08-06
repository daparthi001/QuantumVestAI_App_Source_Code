#!/bin/bash
# DB Init Entrypoint Script
# Created: 2025-05-20 06:19:05
# Author: daparthi001

set -e

# Resolve the project structure so PYTHONPATH includes both the
# project root and the API package. When running inside containers the
# repository is typically located under */ai-stock-platform*.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
API_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PROJECT_ROOT="$(dirname "$API_DIR")"

export PYTHONPATH="${PROJECT_ROOT}:${API_DIR}:$PYTHONPATH"
echo "PYTHONPATH set to: $PYTHONPATH"

echo "[$(date -u '+%Y-%m-%d %H:%M:%S')] Starting database initialization..."

# Wait for database. Support both old and new script locations
if [ -x /app/scripts/wait-for-db.sh ]; then
    /app/scripts/wait-for-db.sh
elif [ -x /app/api/scripts/wait-for-db.sh ]; then
    /app/api/scripts/wait-for-db.sh
else
    echo "wait-for-db.sh script not found!" >&2
    exit 1
fi

# Run migrations
echo "Running database migrations..."
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
API_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

ROOT_DIR="$(dirname "$API_DIR")"

# Prefer alembic.ini next to the API directory, fall back to project root
if [ -f "${API_DIR}/alembic.ini" ]; then
    ALEMBIC_CFG="${API_DIR}/alembic.ini"
elif [ -f "${ROOT_DIR}/alembic.ini" ]; then
    ALEMBIC_CFG="${ROOT_DIR}/alembic.ini"
else
    echo "alembic.ini not found" >&2
    exit 1
fi


# Attempt upgrade, handle missing revisions by stamping baseline
if ! alembic -c "$ALEMBIC_CFG" upgrade heads; then
    echo "Alembic upgrade failed. Stamping database to initial revision and retrying..." >&2
    alembic -c "$ALEMBIC_CFG" stamp 0001
    alembic -c "$ALEMBIC_CFG" upgrade heads
fi

# Run seed script if specified
if [ "${RUN_SEED:-false}" = "true" ]; then
    echo "Verifying database schema before seeding..."
    python <<'PY'
import os, sys, psycopg2
dsn = os.getenv("DATABASE_URL") or "postgresql://{user}:{password}@{host}:{port}/{db}".format(
    user=os.getenv("POSTGRES_USER", "postgres"),
    password=os.getenv("POSTGRES_PASSWORD", "postgres"),
    host=os.getenv("POSTGRES_HOST", "db"),
    port=os.getenv("POSTGRES_PORT", "5432"),
    db=os.getenv("POSTGRES_DB", "postgres"),
)
conn = psycopg2.connect(dsn)
cur = conn.cursor()
cur.execute("SELECT to_regclass('public.users')")
exists = cur.fetchone()[0] is not None
conn.close()
sys.exit(0 if exists else 1)
PY
    if [ $? -ne 0 ]; then
        echo "Database schema not found; aborting seed." >&2
        exit 1
    fi
    echo "Running database seed..."
    python /app/scripts/seed_db.py
fi

echo "Database initialization completed."
