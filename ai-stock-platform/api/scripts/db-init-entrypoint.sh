#!/bin/bash
# DB Init Entrypoint Script
# Created: 2025-05-20 06:19:05
# Author: daparthi001

set -e

echo "[$(date -u '+%Y-%m-%d %H:%M:%S')] Starting database initialization..."

# Wait for database
/app/scripts/wait-for-db.sh

# Run migrations
echo "Running database migrations..."
# Temporarily remove PYTHONPATH so the real Alembic package is used
PYTHONPATH_BACKUP="$PYTHONPATH"
unset PYTHONPATH
alembic upgrade head
export PYTHONPATH="$PYTHONPATH_BACKUP"

# Run seed script if specified
if [ "${RUN_SEED:-false}" = "true" ]; then
    echo "Running database seed..."
    python /app/scripts/seed_db.py
fi

echo "Database initialization completed."
