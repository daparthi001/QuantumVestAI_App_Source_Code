#!/bin/bash
# Direct fix for API_PREFIX issue in WebSocket permissions
# Created: 2025-08-04
# Author: gayatri

set -e

echo "Applying direct fix for API_PREFIX issue..."

# File to fix
AUTH_FILE="/Users/gayatri/QuantumVestAI_App_Source_Code/ai-stock-platform/api/core/security/authentication.py"

if [ -f "$AUTH_FILE" ]; then
  echo "Checking if fix is needed for $AUTH_FILE..."
  
  if grep -q "settings.API_PREFIX" "$AUTH_FILE"; then
    echo "Found API_PREFIX issue, applying fix..."
    sed -i '' "s/settings.API_PREFIX/settings.API_V1_STR/g" "$AUTH_FILE"
    echo "Fix applied successfully"
  else
    echo "No API_PREFIX issue found in $AUTH_FILE"
  fi
else
  echo "Authentication file not found: $AUTH_FILE"
fi

# Also check the original security.py file
SECURITY_FILE="/Users/gayatri/QuantumVestAI_App_Source_Code/ai-stock-platform/api/core/security.py"

if [ -f "$SECURITY_FILE" ]; then
  echo "Checking if fix is needed for $SECURITY_FILE..."
  
  if grep -q "settings.API_PREFIX" "$SECURITY_FILE"; then
    echo "Found API_PREFIX issue, applying fix..."
    sed -i '' "s/settings.API_PREFIX/settings.API_V1_STR/g" "$SECURITY_FILE"
    echo "Fix applied successfully to security.py"
  else
    echo "No API_PREFIX issue found in $SECURITY_FILE"
  fi
else
  echo "Security file not found: $SECURITY_FILE"
fi

echo "Creating a Kubernetes fix job to apply to running pods..."

cat << 'EOF' > fix_api_prefix_job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: api-prefix-fix
  namespace: quantumvestai
spec:
  ttlSecondsAfterFinished: 100
  template:
    spec:
      containers:
      - name: kubectl
        image: bitnami/kubectl:latest
        command:
        - /bin/sh
        - -c
        - |
          # Find all API pods
          PODS=$(kubectl get pods -n quantumvestai -l app=quantumvestai-api -o name)
          
          # Apply fix to each pod
          for POD in $PODS; do
            echo "Fixing $POD..."
            kubectl exec $POD -n quantumvestai -- bash -c '
              # Fix authentication.py
              if [ -f /app/core/security/authentication.py ]; then
                if grep -q "settings.API_PREFIX" /app/core/security/authentication.py; then
                  sed -i "s/settings.API_PREFIX/settings.API_V1_STR/g" /app/core/security/authentication.py
                  echo "Fixed API_PREFIX issue in authentication.py"
                fi
              fi
              
              # Fix security.py if it exists
              if [ -f /app/core/security.py ]; then
                if grep -q "settings.API_PREFIX" /app/core/security.py; then
                  sed -i "s/settings.API_PREFIX/settings.API_V1_STR/g" /app/core/security.py
                  echo "Fixed API_PREFIX issue in security.py"
                fi
              fi
            '
          done
          
          # Restart the deployment
          kubectl rollout restart deployment/quantumvestai-api -n quantumvestai
          
          # Wait for restart to complete
          kubectl rollout status deployment/quantumvestai-api -n quantumvestai
      serviceAccountName: api-fix-sa
      restartPolicy: Never
EOF

echo "To apply the fix to the Kubernetes cluster, run:"
echo "kubectl apply -f fix_api_prefix_job.yaml"

echo "Fix process complete!"
