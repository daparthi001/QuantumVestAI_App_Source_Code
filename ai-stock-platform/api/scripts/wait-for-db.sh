#!/bin/bash
# Database Connection Check Script
# Created: 2025-05-20 14:14:14
# Author: daparthi001

# Disable exit on error to handle errors gracefully
set +e

echo "[$(date -u '+%Y-%m-%d %H:%M:%S')] Starting database connection check"

# Function to log messages with timestamp
log() {
    echo "[$(date -u '+%Y-%m-%d %H:%M:%S')] $1"
}

# Function to check if a variable is set
check_var() {
    local var_name="$1"
    local var_value="$2"
    if [ -z "$var_value" ]; then
        log "❌ Error: $var_name is not set"
        return 1
    fi
    return 0
}

# Initialize connection variables
DB_HOST="${DB_HOST:-quantumvestai-dev.cwbsqsiywwaa.us-east-1.rds.amazonaws.com}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-dbadmin}"
DB_PASSWORD="${DB_PASSWORD}"
DB_NAME="${DB_NAME:-quantumvestaidb}"

# Validate environment variables
log "Validating environment variables..."

check_var "DB_HOST" "$DB_HOST" || exit 1
check_var "DB_PORT" "$DB_PORT" || exit 1
check_var "DB_USER" "$DB_USER" || exit 1
check_var "DB_PASSWORD" "$DB_PASSWORD" || exit 1
check_var "DB_NAME" "$DB_NAME" || exit 1

# Log connection details
log "Connection Details:"
log "Host: $DB_HOST"
log "Port: $DB_PORT"
log "User: $DB_USER"
log "Database: $DB_NAME"
log "Password is $(if [ -n "$DB_PASSWORD" ]; then echo "set"; else echo "not set"; fi)"

# Function to test database connection
test_connection() {
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c '\q' >/dev/null 2>&1
    return $?
}

# Function to check DNS resolution
check_dns() {
    if ! nslookup "$DB_HOST" >/dev/null 2>&1; then
        log "❌ DNS resolution failed for $DB_HOST"
        return 1
    fi
    return 0
}

# Function to check TCP connection
check_tcp() {
    if ! nc -z -w 5 "$DB_HOST" "$DB_PORT" >/dev/null 2>&1; then
        log "❌ TCP connection failed to $DB_HOST:$DB_PORT"
        return 1
    fi
    return 0
}

# Main connection loop
max_attempts=30
counter=0
log "Starting connection attempts..."

while [ $counter -lt $max_attempts ]; do
    counter=$((counter + 1))
    log "Attempt $counter of $max_attempts"

    # Check DNS
    if ! check_dns; then
        log "Waiting for DNS resolution..."
        sleep 2
        continue
    fi

    # Check TCP
    if ! check_tcp; then
        log "Waiting for TCP connection..."
        sleep 2
        continue
    fi

    # Test database connection
    if test_connection; then
        log "✅ Database connection successful!"
        exit 0
    else
        log "Database connection failed, retrying..."
        sleep 2
    fi
done

log "❌ Failed to connect to database after $max_attempts attempts"
exit 1