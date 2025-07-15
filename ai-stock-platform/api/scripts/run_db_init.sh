#!/bin/sh
set -e

echo "Starting database initialization..."

# Map K8s secret names to generic variables with sensible fallbacks
DB_HOST="${DB_HOST:-${POSTGRES_SERVER:-${POSTGRES_HOST:-localhost}}}"
DB_PORT="${DB_PORT:-${POSTGRES_PORT:-5432}}"
DB_NAME="${DB_NAME:-${POSTGRES_DB:-quantumvestaidb}}"
DB_USER="${DB_USER:-${POSTGRES_USER:-dbadmin}}"
DB_PASSWORD="${DB_PASSWORD:-${POSTGRES_PASSWORD}}"

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
alembic upgrade head

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
