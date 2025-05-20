#!/bin/bash
# Database Connection Check Script
# Created: 2025-05-20 06:19:05
# Author: daparthi001

set -e

host="${POSTGRES_HOST:-localhost}"
port="${POSTGRES_PORT:-5432}"
user="${POSTGRES_USER}"
password="${POSTGRES_PASSWORD}"
db="${POSTGRES_DB}"

until PGPASSWORD=$password psql -h "$host" -U "$user" -d "$db" -c '\q'; do
  >&2 echo "Database is unavailable - sleeping"
  sleep 2
done

>&2 echo "Database is up - executing command"