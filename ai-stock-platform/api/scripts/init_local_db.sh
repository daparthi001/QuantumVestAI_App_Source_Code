#!/bin/bash
# Initialize local development database
set -e

echo "Initializing QuantumVestAI local development database..."

# Check if PostgreSQL is running
if ! pg_isready &>/dev/null; then
  echo "Error: PostgreSQL is not running. Please start PostgreSQL first."
  exit 1
fi

# Support legacy POSTGRES_* variables for backward compatibility
DB_HOST="${DB_HOST}"
DB_PORT="${DB_PORT}"
DB_USER="${DB_USER}"
DB_PASSWORD="${DB_PASSWORD}"
DB_NAME="${DB_NAME}"

# Load environment variables
if [ -f .env ]; then
  echo "Loading environment variables from .env file..."
  export $(grep -v '^#' .env | xargs)
else
  echo "No .env file found, using default values..."
  export DB_HOST=localhost
  export DB_PORT=5432
  export DB_USER=quantumvest
  export DB_PASSWORD=localdev
  export DB_NAME=quantumvestai
  export ADMIN_USERNAME=admin
  export ADMIN_EMAIL=admin@example.com
  export ADMIN_PASSWORD=admin123
  export ADMIN_FULL_NAME="Local Admin"
fi

# Create database and user
echo "Creating database and user..."
sudo -u postgres psql -f db_init/01_create_database.sql

# Apply migrations
echo "Applying database migrations..."
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
API_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Run migrations from the API directory so Alembic can locate env.py
pushd "$API_DIR" >/dev/null
alembic upgrade head
popd >/dev/null

# Initialize reference data
echo "Initializing reference data..."
psql "postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME" -f db_init/02_reference_data.sql

# Create admin user
echo "Creating admin user..."
python db_init/03_create_admin.py

# Seed sample data
echo "Seeding sample data..."
python db_init/04_seed_sample_data.py --env development

echo "Database initialization completed successfully!"
echo "You can now start the application with: uvicorn api.main:app --reload"
