#!/bin/bash
# API Entrypoint Script
# Created: 2025-05-20 06:19:05
# Author: daparthi001

set -e

echo "[$(date -u '+%Y-%m-%d %H:%M:%S')] Starting QuantumVestAI API..."

# Wait for database
#/app/scripts/wait-for-db.sh

# Start the application
if [ "$ENVIRONMENT" = "development" ]; then
    echo "Starting in development mode..."
    exec uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000} --reload
else
    echo "Starting in production mode..."
    exec uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers ${WORKERS:-4}
fi