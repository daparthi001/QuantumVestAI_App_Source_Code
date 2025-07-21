#!/bin/sh
set -e

echo "Starting database initialization..."

# Support legacy POSTGRES_* variables for backward compatibility
DB_HOST="${DB_HOST}"
DB_PORT="${DB_PORT}"
DB_NAME="${DB_NAME}"
DB_USER="${DB_USER}"
DB_PASSWORD="${DB_PASSWORD}"

# Wait for database to be ready
echo "Waiting for database to be ready..."
until PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1" > /dev/null 2>&1; do
  echo "Database is unavailable - sleeping"
  sleep 2
done

echo "Database is available"

# Set environment variables for Alembic
export PYTHONPATH=/db-init

# Step 1: Run database migrations
echo "Running database migrations..."
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

# Step 2: Apply reference data
echo "Initializing reference data..."
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -f /db-init/02_reference_data.sql

# Step 3: Create admin user if requested
if [ -n "$ADMIN_USERNAME" ] && [ -n "$ADMIN_PASSWORD" ]; then
  echo "Creating admin user: $ADMIN_USERNAME"
  python3 /db-init/03_create_admin.py
else
  echo "Skipping admin user creation (credentials not provided)"
fi

# Step 4: Seed sample data if in development mode
if [ "$ENVIRONMENT" = "development" ] || [ "$SEED_SAMPLE_DATA" = "true" ]; then
  echo "Seeding sample data..."
  python3 /db-init/04_seed_sample_data.py --env "$ENVIRONMENT"
else
  echo "Skipping sample data seeding (not in development mode)"
fi

echo "Database initialization completed successfully!"
