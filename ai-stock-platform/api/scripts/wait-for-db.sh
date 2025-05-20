#!/bin/sh
# Database Connection Check Script
# Created: 2025-05-20 14:46:05
# Author: daparthi001

echo "[$(date -u '+%Y-%m-%d %H:%M:%S')] Starting database connection check"

# Connection details
echo "Checking connection to:"
echo "Host: $DB_HOST"
echo "Port: $DB_PORT"
echo "User: $DB_USER"
echo "Database: $DB_NAME"

# Test connection
until PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null; do
  echo "[$(date -u '+%Y-%m-%d %H:%M:%S')] Waiting for database connection..."
  sleep 2
done

echo "[$(date -u '+%Y-%m-%d %H:%M:%S')] Database connection successful"