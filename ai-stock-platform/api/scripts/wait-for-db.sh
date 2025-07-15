#!/bin/sh
# wait-for-db.sh - Script to check RDS PostgreSQL availability
# Updated: 2025-06-15 04:12:45
# Author: daparthi001

set -e

# Log function for clarity
log() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

# Set default values if not provided
# Support legacy POSTGRES_* variables for backward compatibility
DB_HOST="${DB_HOST:-${POSTGRES_SERVER:-${POSTGRES_HOST:-localhost}}}"
DB_PORT="${DB_PORT:-${POSTGRES_PORT:-5432}}"
DB_NAME="${DB_NAME:-${POSTGRES_DB:-quantumvestaidb}}"
DB_USER="${DB_USER:-${POSTGRES_USER:-dbadmin}}"
DB_PASSWORD="${DB_PASSWORD:-${POSTGRES_PASSWORD}}"
# Password should be set via secret

# Maximum number of attempts
MAX_ATTEMPTS=30
# Delay between attempts in seconds
DELAY=10

log "Waiting for RDS PostgreSQL to be available at ${DB_HOST}:${DB_PORT}..."

# Loop to check database availability
for i in $(seq 1 $MAX_ATTEMPTS); do
  log "Attempt $i of $MAX_ATTEMPTS"
  
  # Use PGPASSWORD environment variable for authentication
  export PGPASSWORD="$DB_PASSWORD"
  
  # Try connecting to the database using TCP/IP (-h flag)
  if pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t 5; then
    log "Database is available!"
    
    # Try a simple query to verify credentials and database access
    if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1" >/dev/null 2>&1; then
      log "Database connection successful!"
      exit 0
    else
      log "Connected to database server but could not execute query. Checking credentials..."
    fi
  fi
  
  log "Database is unavailable - sleeping for ${DELAY}s"
  sleep $DELAY
done

log "Could not connect to database after $MAX_ATTEMPTS attempts"
exit 1
