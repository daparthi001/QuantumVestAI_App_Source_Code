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

# Determine the directory of this script and the API root
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
API_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

ROOT_DIR="$(dirname "$API_DIR")"

# Run Alembic using the configuration inside the api directory or project root
if [ -f "${API_DIR}/alembic.ini" ]; then
    ALEMBIC_CFG="${API_DIR}/alembic.ini"
elif [ -f "${ROOT_DIR}/alembic.ini" ]; then
    ALEMBIC_CFG="${ROOT_DIR}/alembic.ini"
else
    echo "alembic.ini not found" >&2
    exit 1
fi


# Attempt upgrade, handle missing revisions by stamping baseline
if ! alembic -c "$ALEMBIC_CFG" upgrade heads; then
    echo "Alembic upgrade failed. Stamping database to initial revision and retrying..." >&2
    alembic -c "$ALEMBIC_CFG" stamp 0001
    alembic -c "$ALEMBIC_CFG" upgrade heads
fi

echo "[$(date -u '+%Y-%m-%d %H:%M:%S')] Migrations completed successfully!"
