#!/bin/bash
# API Start Script
# Created: 2025-05-20 04:32:43
# Author: daparthi001

set -e

# Wait for database
echo "Waiting for database..."
timeout 30 bash -c "until curl -s http://${POSTGRES_SERVER}:${POSTGRES_PORT}; do sleep 1; done"

# Run migrations if needed
if [ "${AUTO_MIGRATE}" = "true" ]; then
    echo "Running database migrations..."
    alembic upgrade head
fi

# Start the application
echo "Starting API server..."
exec uvicorn main:app --host 0.0.0.0 --port ${PORT} --workers 4