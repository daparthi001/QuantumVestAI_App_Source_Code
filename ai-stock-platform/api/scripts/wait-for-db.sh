#!/bin/bash
# Database Connection Check Script
# Created: 2025-05-20 13:55:45
# Author: daparthi001

set -e

echo "=== Starting Database Connection Check ==="
echo "Timestamp: $(date -u '+%Y-%m-%d %H:%M:%S')"
echo "User: daparthi001"

# Force use of DB_* variables, no fallback to POSTGRES_* variables
host="${DB_HOST}"
port="${DB_PORT}"
user="${DB_USER}"
password="${DB_PASSWORD}"
db="${DB_NAME}"

# Print current environment for debugging
echo "Current Environment:"
env | grep -i "DB_"

# Validate required environment variables
if [ -z "$host" ]; then
    echo "❌ Error: DB_HOST is not set"
    exit 1
fi

if [ -z "$port" ]; then
    echo "❌ Error: DB_PORT is not set"
    exit 1
fi

if [ -z "$user" ]; then
    echo "❌ Error: DB_USER is not set"
    exit 1
fi

if [ -z "$password" ]; then
    echo "❌ Error: DB_PASSWORD is not set"
    exit 1
fi

if [ -z "$db" ]; then
    echo "❌ Error: DB_NAME is not set"
    exit 1
fi

echo "Connection Details:"
echo "Host: $host"
echo "Port: $port"
echo "User: $user"
echo "Database: $db"
echo "Password is $(if [ -n "$password" ]; then echo "set"; else echo "not set"; fi)"

# Wait for database connection
max_attempts=30
counter=0
echo "Waiting for database to become available..."

until PGPASSWORD="$password" psql -h "$host" -U "$user" -d "$db" -c '\q' 2>/dev/null; do
    counter=$((counter + 1))
    if [ $counter -ge $max_attempts ]; then
        echo "❌ Error: Maximum attempts ($max_attempts) reached"
        echo "Database connection failed after $((counter * 2)) seconds"
        exit 1
    fi
    
    echo "Database is unavailable - sleeping (Attempt $counter/$max_attempts)"
    sleep 2
done

echo "✅ Database is up - executing command"
echo "Successfully connected after $counter attempts"
echo "Timestamp: $(date -u '+%Y-%m-%d %H:%M:%S')"