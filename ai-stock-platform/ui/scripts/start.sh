#!/bin/bash
# QuantumVestAI UI Startup Script
# Created: 2025-05-19 03:38:30
# Author: daparthi001

set -e

echo "Starting QuantumVestAI UI application..."

# Determine environment and load matching .env file
ENV=${ENV:-production}
ENV_FILE=".env.${ENV}"
if [ -f "$ENV_FILE" ]; then
    echo "Using environment file $ENV_FILE"
    cp "$ENV_FILE" .env
fi

# Load environment variables if .env file exists
if [ -f .env ]; then
    echo "Loading environment variables from .env file"
    set -a
    source .env

    set +a
fi

# Load SECRET_KEY from mounted file if provided
if [ -n "$SECRET_KEY_FILE" ] && [ -f "$SECRET_KEY_FILE" ]; then
    echo "Loading SECRET_KEY from $SECRET_KEY_FILE"
    export SECRET_KEY="$(cat "$SECRET_KEY_FILE")"
fi

# Set default values with proper validation
if [ -z "$PORT" ]; then
    export PORT=3000
fi

if [ -z "$HOST" ]; then
    export HOST="0.0.0.0"
fi

if [ -z "$WORKERS" ]; then
    export WORKERS=$(nproc)
fi

if [ -z "$LOG_LEVEL" ]; then
    export LOG_LEVEL="info"
fi

if [ -z "$ENV" ]; then
    export ENV="production"
fi

echo "Configuration:"
echo "Environment: $ENV"
echo "Host: $HOST"
echo "Port: $PORT"
echo "Workers: $WORKERS"
echo "Log Level: $LOG_LEVEL"

# Verify required directories exist
for dir in "static" "templates" "logs"; do
    if [ ! -d "/app/$dir" ]; then
        echo "Error: Required directory /app/$dir does not exist"
        exit 1
    fi
done

# Check for debug mode
if [ "$ENV" = "development" ]; then
    echo "Starting in development mode with auto-reload..."
    exec uvicorn main:app \
        --host "$HOST" \
        --port "$PORT" \
        --reload \
        --log-level "$LOG_LEVEL"
else
    echo "Starting in production mode..."
    exec gunicorn main:app \
        -k uvicorn.workers.UvicornWorker \
        --bind "$HOST:$PORT" \
        --workers "$WORKERS" \
        --log-level "$LOG_LEVEL" \
        --access-logfile - \
        --error-logfile - \
        --worker-tmp-dir /dev/shm \
        --graceful-timeout 120
fi