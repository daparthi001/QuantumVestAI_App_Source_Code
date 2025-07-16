#!/bin/bash
# Quick Database Connection Test
# Created: 2025-05-20 08:01:02
# Author: daparthi001

# Get the password from the secret if not provided via env
NAMESPACE="${NAMESPACE:-dev}"
if [ -z "$DB_PASSWORD" ]; then
  DB_PASSWORD=$(kubectl get secret -n "$NAMESPACE" quantumvestai-cluster-rds-credentials -o jsonpath='{.data.password}' | base64 -d)
fi

# Map host and port
DB_HOST="${DB_HOST}"
DB_PORT="${DB_PORT}"
DB_USER="${DB_USER}"
DB_NAME="${DB_NAME}"

# Test RDS connection
echo "=== Testing RDS Connection ==="
PGPASSWORD="$DB_PASSWORD" psql \
  -h "$DB_HOST" \
  -p "$DB_PORT" \
  -U "$DB_USER" \
  -d "$DB_NAME" \
  -c '\conninfo'

# Test internal service connection
echo -e "\n=== Testing Internal Service Connection ==="
PGPASSWORD="$DB_PASSWORD" psql \
  -h 172.20.234.34 \
  -p "$DB_PORT" \
  -U "$DB_USER" \
  -d "$DB_NAME" \
  -c '\conninfo'
