#!/bin/bash
# DB Init Entrypoint Script
# Created: 2025-05-20 06:19:05
# Author: daparthi001

set -e

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
alembic upgrade head

# Run seed script if specified
if [ "${RUN_SEED:-false}" = "true" ]; then
    echo "Running database seed..."
    python /app/scripts/seed_db.py
fi

echo "Database initialization completed."
