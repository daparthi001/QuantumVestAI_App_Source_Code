#!/bin/bash
# Quick Database Connection Test
# Created: 2025-05-20 08:01:02
# Author: daparthi001

# Get the password from the secret
DB_PASSWORD=$(kubectl get secret -n dev quantumvestai-cluster-rds-credentials -o jsonpath='{.data.password}' | base64 -d)

# Test RDS connection
echo "=== Testing RDS Connection ==="
PGPASSWORD="$DB_PASSWORD" psql \
  -h quantumvestai-dev.cwbsqsiywwaa.us-east-1.rds.amazonaws.com \
  -p 5432 \
  -U dbadmin \
  -d quantumvestaidb \
  -c '\conninfo'

# Test internal service connection
echo -e "\n=== Testing Internal Service Connection ==="
PGPASSWORD="$DB_PASSWORD" psql \
  -h 172.20.234.34 \
  -p 5432 \
  -U dbadmin \
  -d quantumvestaidb \
  -c '\conninfo'