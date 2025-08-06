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
DB_HOST="${DB_HOST}"
DB_PORT="${DB_PORT}"
DB_NAME="${DB_NAME}"
DB_USER="${DB_USER}"
DB_PASSWORD="${DB_PASSWORD}"
# Password should be set via secret

# Maximum number of attempts
MAX_ATTEMPTS=30
# Delay between attempts in seconds
DELAY=10

log "Waiting for RDS PostgreSQL to be available at ${DB_HOST}:${DB_PORT}..."

# Helper to verify DNS resolution for the DB host. Kubernetes service names
# sometimes take a moment to propagate which previously resulted in immediate
# failures from ``pg_isready``.  This additional check makes the script more
# tolerant of internal DNS delays.
resolve_host() {
  getent hosts "$DB_HOST" >/dev/null 2>&1
}

# Loop to check database availability
for i in $(seq 1 $MAX_ATTEMPTS); do
  log "Attempt $i of $MAX_ATTEMPTS"

  if ! resolve_host; then
    log "Host $DB_HOST not yet resolvable - sleeping for ${DELAY}s"
    sleep $DELAY
    continue
  fi

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
