#!/bin/bash
# JWT Secret Generation Script
# Created: 2025-05-15 22:23:16 (UTC)
# Author: daparthi001

# Generate a random 32-byte string and encode it in base64
JWT_SECRET=$(openssl rand -base64 32)
echo "Generated JWT Secret: $JWT_SECRET"

# Create a Kubernetes Secret YAML file with the JWT secret
cat > jwt-secret.yaml << EOF
# JWT Secret for QuantumVest API Authentication
# Created: $(date -u +"%Y-%m-%d %H:%M:%S") (UTC)
# Author: daparthi001
apiVersion: v1
kind: Secret
metadata:
  name: api-jwt-secret
  namespace: default
  labels:
    app: quantumvest-ai
    component: api
    created-by: daparthi001
type: Opaque
stringData:
  JWT_SECRET: $JWT_SECRET
EOF

echo "JWT Secret YAML file created: jwt-secret.yaml"
#echo "Apply with: kubectl apply -f jwt-secret.yaml"