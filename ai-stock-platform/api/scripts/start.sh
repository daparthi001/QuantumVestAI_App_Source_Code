#!/bin/bash
# API Start Script
# Created: 2025-05-20 04:32:43
# Author: daparthi001

set -e

# Map K8s secret names to generic variables with sensible fallbacks
DB_HOST="${DB_HOST:-${POSTGRES_SERVER:-${POSTGRES_HOST:-localhost}}}"
DB_PORT="${DB_PORT:-${POSTGRES_PORT:-5432}}"

# Wait for database
echo "Waiting for database..."
timeout 30 bash -c "until curl -s http://${DB_HOST}:${DB_PORT}; do sleep 1; done"

# Run migrations if needed
if [ "${AUTO_MIGRATE}" = "true" ]; then
    echo "Running database migrations..."
    if command -v alembic >/dev/null 2>&1; then
        SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
        API_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
        ROOT_DIR="$(dirname "$API_DIR")"

        if [ -f "${API_DIR}/alembic.ini" ]; then
            ALEMBIC_CFG="${API_DIR}/alembic.ini"
        elif [ -f "${ROOT_DIR}/alembic.ini" ]; then
            ALEMBIC_CFG="${ROOT_DIR}/alembic.ini"
        else
            echo "alembic.ini not found" >&2
            exit 1
        fi

        alembic -c "$ALEMBIC_CFG" upgrade head
    else
        echo "Alembic not installed; skipping migrations" >&2
    fi
fi

# Start the application
echo "Starting API server..."
exec uvicorn main:app --host 0.0.0.0 --port ${PORT} --workers 4
