#!/bin/bash
# Initialize local development database
set -e

echo "Initializing QuantumVestAI local development database..."

# Check if PostgreSQL is running
if ! pg_isready &>/dev/null; then
  echo "Error: PostgreSQL is not running. Please start PostgreSQL first."
  exit 1
fi

# Load environment variables
if [ -f .env ]; then
  echo "Loading environment variables from .env file..."
  export $(grep -v '^#' .env | xargs)
else
  echo "No .env file found, using default values..."
  export POSTGRES_SERVER=localhost
  export POSTGRES_PORT=5432
  export POSTGRES_USER=quantumvest
  export POSTGRES_PASSWORD=localdev
  export POSTGRES_DB=quantumvestai
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
alembic upgrade head

# Initialize reference data
echo "Initializing reference data..."
psql "postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_SERVER:$POSTGRES_PORT/$POSTGRES_DB" -f db_init/02_reference_data.sql

# Create admin user
echo "Creating admin user..."
python db_init/03_create_admin.py

# Seed sample data
echo "Seeding sample data..."
python db_init/04_seed_sample_data.py --env development

echo "Database initialization completed successfully!"
echo "You can now start the application with: uvicorn api.main:app --reload"