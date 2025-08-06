#!/bin/bash

export PYTHONPATH="${STANDARD_PYTHONPATH}"
# Docker Entrypoint Script for QuantumVestAI API
# Created: 2025-06-19 06:26:46
# Author: daparthi001

set -e

echo "=== Starting QuantumVestAI API Service ==="
echo "Date: $(date -u)"
echo "Environment: $API_ENV"
echo "User: $(whoami)"
echo "Python: $(python --version)"
# Correct environment variable assignment syntax
export DB_URL="postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:5432/quantumvestai"

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

# Set Python path to include both /app/ai-stock-platform and /app/app/core for robust import resolution
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

# Check if the security module is properly installed
echo "Verifying core.security module..."
python -c "from core.security import get_current_active_user; print('Security module imported successfully!')" || {
    echo "Failed to import security module. Creating necessary files..."
    
    # Create directory if it doesn't exist
    mkdir -p /app/core/security
    
    # Create __init__.py if missing
    if [ ! -f "/app/core/security/__init__.py" ]; then
        echo "Creating /app/core/security/__init__.py"
        cat > /app/core/security/__init__.py <<EOL
"""
Core Security Module Init File
"""
# Re-export everything to maintain compatibility
from core.security.tokens import create_access_token, validate_token
from core.security.authentication import (
    get_current_user,
    get_current_active_user,
    check_admin_role,
    verify_password,
    get_password_hash,
    pwd_context,
    oauth2_scheme
)
EOL
    fi
    
    # Check if other necessary files exist and create them if needed
    [ -f "/app/core/security/authentication.py" ] || echo "Warning: authentication.py is missing"
    [ -f "/app/core/security/tokens.py" ] || echo "Warning: tokens.py is missing"
    [ -f "/app/core/security/websocket_permissions.py" ] || echo "Warning: websocket_permissions.py is missing"
    
    # Fix API_PREFIX issue in authentication.py if present
    if [ -f "/app/core/security/authentication.py" ]; then
        echo "Checking for API_PREFIX issue in authentication.py..."
        if grep -q "settings.API_PREFIX" /app/core/security/authentication.py; then
            echo "Fixing API_PREFIX issue..."
            sed -i "s/settings.API_PREFIX/settings.API_V1_STR/g" /app/core/security/authentication.py
            echo "Fixed API_PREFIX issue in authentication.py"
        fi
    fi
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
