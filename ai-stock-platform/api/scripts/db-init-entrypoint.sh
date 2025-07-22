#!/bin/bash
# DB Init Entrypoint Script
# Created: 2025-05-20 06:19:05
# Author: daparthi001

set -e

# Ensure PYTHONPATH is set for all migration commands
export PYTHONPATH="/app/api:/app:$PYTHONPATH"
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

alembic -c "$ALEMBIC_CFG" upgrade head

# Run seed script if specified
if [ "${RUN_SEED:-false}" = "true" ]; then
    echo "Running database seed..."
    python /app/scripts/seed_db.py
fi

echo "Database initialization completed."
