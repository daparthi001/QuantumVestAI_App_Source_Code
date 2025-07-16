#!/bin/bash
# Database Connection Monitor
# Created: 2025-05-20 08:03:38
# Author: daparthi001

# Configuration
# Namespace to pull secret from
NAMESPACE="${NAMESPACE:-dev}"

# Map environment variables for database connection
DB_HOST="${DB_HOST}"
DB_PORT="${DB_PORT}"
DB_USER="${DB_USER}"
DB_NAME="${DB_NAME}"

# Get the password from the secret
DB_PASSWORD=$(kubectl get secret -n $NAMESPACE quantumvestai-cluster-rds-credentials -o jsonpath='{.data.password}' | base64 -d)

# Test RDS connection and get SSL info
echo "=== Database Connection Monitor ==="
echo "Timestamp: $(date -u '+%Y-%m-%d %H:%M:%S')"
echo "User: daparthi001"

connection_info=$(PGPASSWORD="$DB_PASSWORD" psql \
  "postgresql://$DB_USER@$DB_HOST:$DB_PORT/$DB_NAME?sslmode=require" \
  -c '\conninfo' 2>&1)

if [ $? -eq 0 ]; then
    echo "✅ RDS Connection: SUCCESS"
    echo "Connection Details:"
    echo "$connection_info"
    
    # Extract SSL information
    ssl_info=$(echo "$connection_info" | grep "SSL connection")
    echo "SSL Configuration:"
    echo "$ssl_info"
else
    echo "❌ RDS Connection: FAILED"
    echo "Error:"
    echo "$connection_info"
fi