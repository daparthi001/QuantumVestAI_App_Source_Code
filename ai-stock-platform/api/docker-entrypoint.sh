#!/bin/bash
# Docker Entrypoint Script for QuantumVestAI API
# Created: 2025-06-19 06:26:46
# Author: daparthi001

set -e

echo "=== Starting QuantumVestAI API Service ==="
echo "Date: $(date -u)"
echo "Environment: $API_ENV"
echo "User: $(whoami)"
echo "Python: $(python --version)"
export DB_URL = "postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:5432/quantumvestai"

# Load environment-specific configuration if present
ENV_FILE="/app/.env.${API_ENV}"
if [ -f "$ENV_FILE" ]; then
    echo "Loading environment variables from $ENV_FILE"
    cp "$ENV_FILE" /app/.env
    set -a
    source /app/.env
    set +a

# If SECRET_KEY_FILE is specified, load secret key from that file
if [ -n "$SECRET_KEY_FILE" ] && [ -f "$SECRET_KEY_FILE" ]; then
    echo "Loading SECRET_KEY from $SECRET_KEY_FILE"
    export SECRET_KEY="$(cat "$SECRET_KEY_FILE")"
fi

else
    echo "No environment file found for $API_ENV"
fi

# Create required directories
mkdir -p /app/api /app/logs

# Set Python path to include current directory
export PYTHONPATH=/app:$PYTHONPATH
echo "PYTHONPATH: $PYTHONPATH"

# Check for __init__.py and create if missing
if [ ! -f "/app/api/__init__.py" ]; then
    echo "Warning: api/__init__.py missing. Using deployment version."
    cp /app/api-init-backup.py /app/api/__init__.py
fi

# Check for main.py and create if missing
if [ ! -f "/app/api/main.py" ]; then
    echo "Warning: api/main.py missing. Using deployment version."
    echo '"""API Main Module"""\nfrom api import app' > /app/api/main.py
fi

# Ensure proper permissions
if [ "$(whoami)" = "appuser" ]; then
    chown -R appuser:appuser /app/logs /app/api
fi

# Print directory structure for debugging
echo "Directory structure:"
ls -la /app
ls -la /app/api

# Verify we can import the api module
echo "Verifying api module can be imported..."
python -c "import api; print(f'API module found and app imported. Routes: {len(api.app.routes)}')" || {
    echo "ERROR: Cannot import api module after setup!"
    exit 1
}

# Run database migration to ensure schema is up to date
echo "Running startup database migrations..."
python /app/scripts/database_migrator.py || {
    echo "Database migration failed" >&2
    exit 1
}

# Start the application
echo "Starting API service with command: $@"
exec "$@"