#!/bin/bash
# Startup script for the QuantumVestAI UI application

set -e

echo "Starting QuantumVestAI UI application..."

# Load environment variables if .env file exists
if [ -f .env ]; then
    echo "Loading environment variables from .env file"
    export $(grep -v '^#' .env | xargs)
fi

# Set default values for environment variables if not set
export PORT=${PORT:-8000}
export HOST=${HOST:-0.0.0.0}
export WORKERS=${WORKERS:-4}
export LOG_LEVEL=${LOG_LEVEL:-info}
export ENV=${ENV:-production}

echo "Environment: $ENV"
echo "Host: $HOST"
echo "Port: $PORT"
echo "Workers: $WORKERS"
echo "Log Level: $LOG_LEVEL"

# Check for debug mode
if [ "$ENV" = "development" ]; then
    echo "Starting application in development mode with auto-reload..."
    exec uvicorn ui.main:app --host $HOST --port $PORT --reload --log-level $LOG_LEVEL
else
    # Start using gunicorn for production
    echo "Starting application in production mode..."
    exec gunicorn ui.main:app -k uvicorn.workers.UvicornWorker \
        --bind $HOST:$PORT \
        --workers $WORKERS \
        --log-level $LOG_LEVEL \
        --access-logfile - \
        --error-logfile -
fi