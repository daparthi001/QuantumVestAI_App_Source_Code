#!/bin/bash
# Docker Entrypoint Script
# Created: 2025-05-20 04:36:10
# Author: daparthi001

set -e

# Initialize environment variables
export PYTHONPATH=/app
export CURRENT_TIME="2025-05-20 04:36:10"
export CURRENT_USER="daparthi001"

# Wait for database
echo "[${CURRENT_TIME}] Waiting for database..."
python scripts/wait_for_db.py

# Run database migrations
echo "[${CURRENT_TIME}] Running database migrations..."
alembic upgrade head

# Start the application
echo "[${CURRENT_TIME}] Starting QuantumVestAI API..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4