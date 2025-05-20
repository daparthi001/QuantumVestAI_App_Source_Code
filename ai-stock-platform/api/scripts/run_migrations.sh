#!/bin/bash
# Database Migration Script
# Created: 2025-05-20 04:29:52
# Author: daparthi001

set -e

echo "[$(date -u '+%Y-%m-%d %H:%M:%S')] Starting database migrations..."

# Check if alembic is installed
if ! command -v alembic &> /dev/null; then
    echo "Error: alembic is not installed. Please run: pip install alembic"
    exit 1
fi

# Run migrations
echo "Running database migrations..."
alembic upgrade head

echo "[$(date -u '+%Y-%m-%d %H:%M:%S')] Migrations completed successfully!"