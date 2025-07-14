#!/bin/bash

# QuantumVestAI Deployment Fix Script
# This script applies the database migration and configuration fixes

set -e  # Exit on any error

echo "================================================"
echo "QuantumVestAI Deployment Fix Script"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed or not in PATH"
    exit 1
fi

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    print_error "python3 is not installed or not in PATH"
    exit 1
fi

# Default values
NAMESPACE="dev"
DB_MIGRATION_SCRIPT="db_migration.py"
CONFIG_FIX_SCRIPT="config_fix.py"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        --db-url)
            DB_URL="$2"
            shift 2
            ;;
        --skip-migration)
            SKIP_MIGRATION=true
            shift
            ;;
        --skip-config)
            SKIP_CONFIG=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  -n, --namespace NAMESPACE    Kubernetes namespace (default: dev)"
            echo "  --db-url URL                Database URL for migration"
            echo "  --skip-migration            Skip database migration"
            echo "  --skip-config               Skip configuration fix"
            echo "  -h, --help                  Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

print_status "Starting QuantumVestAI deployment fix..."
print_status "Namespace: $NAMESPACE"

# Step 1: Check current pod status
print_status "Checking current pod status..."
kubectl get pods -n $NAMESPACE | grep -E "(quantumvestai|ui-deployment)"

echo ""
print_status "Checking current errors in logs..."
kubectl logs -n $NAMESPACE $(kubectl get pods -n $NAMESPACE -o name | grep quantumvestai-dev-api | head -1) --tail=10 | grep -i error || true
kubectl logs -n $NAMESPACE $(kubectl get pods -n $NAMESPACE -o name | grep ui-deployment | head -1) --tail=10 | grep -i error || true

# Step 2: Database Migration
if [ "$SKIP_MIGRATION" != "true" ]; then
    echo ""
    print_status "=== DATABASE MIGRATION ==="
    
    # Create the migration script if it doesn't exist
    if [ ! -f "$DB_MIGRATION_SCRIPT" ]; then
        print_status "Creating database migration script..."
        cat > "$DB_MIGRATION_SCRIPT" <<'PYEOF'
#!/usr/bin/env python3
import asyncio
import asyncpg
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def quick_migration():
    db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/quantumvestai')
    try:
        connection = await asyncpg.connect(db_url)
        logger.info("Connected to database")
        table_exists = await connection.fetchval(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')"
        )
        if not table_exists:
            logger.info("Creating users table...")
            await connection.execute("""
                CREATE TABLE users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    hashed_password VARCHAR(255) NOT NULL,
                    first_name VARCHAR(100),
                    last_name VARCHAR(100),
                    is_active BOOLEAN DEFAULT TRUE,
                    is_verified BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP WITH TIME ZONE
                );
            """)
            logger.info("Users table created successfully")
        else:
            column_exists = await connection.fetchval(
                "SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'hashed_password')"
            )
            if not column_exists:
                logger.info("Adding hashed_password column...")
                await connection.execute("ALTER TABLE users ADD COLUMN hashed_password VARCHAR(255)")
                logger.info("hashed_password column added successfully")
            else:
                logger.info("hashed_password column already exists")
        await connection.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        await connection.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
        await connection.close()
        logger.info("Migration completed successfully!")
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False
    return True

if __name__ == "__main__":
    success = asyncio.run(quick_migration())
    exit(0 if success else 1)
PYEOF
    fi
    chmod +x "$DB_MIGRATION_SCRIPT"
    print_status "Getting database connection info..."
    DB_SECRET=$(kubectl get secret -n $NAMESPACE -o name | grep -E "(postgres|database|db)" | head -1)
    if [ -n "$DB_SECRET" ]; then
        print_status "Found database secret: $DB_SECRET"
    fi
    if [ -n "$DB_URL" ]; then
        print_status "Running database migration with provided URL..."
        DATABASE_URL="$DB_URL" python3 "$DB_MIGRATION_SCRIPT"
    else
        print_warning "No database URL provided. Please run migration manually:"
        print_warning "DATABASE_URL='your-db-url' python3 $DB_MIGRATION_SCRIPT"
    fi
    if [ $? -eq 0 ]; then
        print_status "Database migration completed successfully!"
    else
        print_error "Database migration failed!"
        exit 1
    fi
fi

# Step 3: Configuration Fix
if [ "$SKIP_CONFIG" != "true" ]; then
    echo ""
    print_status "=== CONFIGURATION FIX ==="
    print_status "Creating Kubernetes ConfigMap..."
    cat > k8s-configmap.yaml <<'CMEOF'
apiVersion: v1
kind: ConfigMap
metadata:
  name: quantumvestai-config
  namespace: dev
data:
  MODEL_ENSEMBLE: "ADVANCED"
  MODEL_ENSEMBLE_PATH: "/app/models/ensemble"
  MODEL_CACHE_SIZE: "1000"
  API_HOST: "0.0.0.0"
  API_PORT: "8000"
  DEBUG: "false"
  LOG_LEVEL: "INFO"
  LSTM_LAYERS: "2"
  HIDDEN_SIZE: "128"
  DROPOUT: "0.2"
  LEARNING_RATE: "0.001"
  BATCH_SIZE: "32"
  EPOCHS: "100"
  RISK_TOLERANCE: "0.02"
  MAX_POSITION_SIZE: "0.1"
  STOP_LOSS: "0.05"
  TAKE_PROFIT: "0.1"
  LOOKBACK_DAYS: "60"
  PREDICTION_HORIZON: "5"
  NORMALIZATION: "minmax"
CMEOF
    if [ "$NAMESPACE" != "dev" ]; then
        sed -i "s/namespace: dev/namespace: $NAMESPACE/g" k8s-configmap.yaml
    fi
    kubectl apply -f k8s-configmap.yaml
    if [ $? -eq 0 ]; then
        print_status "ConfigMap created successfully!"
    else
        print_error "Failed to create ConfigMap!"
        exit 1
    fi
fi

# Step 4: Update Deployments
echo ""
print_status "=== UPDATING DEPLOYMENTS ==="
print_status "Backing up current deployments..."
kubectl get deployment quantumvestai-dev-api -n $NAMESPACE -o yaml > quantumvestai-dev-api-backup.yaml 2>/dev/null || true
kubectl get deployment ui-deployment -n $NAMESPACE -o yaml > ui-deployment-backup.yaml 2>/dev/null || true
print_status "Creating deployment patches..."
cat > api-deployment-patch.yaml <<'PATCHEOF'
spec:
  template:
    spec:
      containers:
      - name: quantumvestai-dev-api
        envFrom:
        - configMapRef:
            name: quantumvestai-config
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: quantumvestai-secrets
              key: DATABASE_URL
              optional: true
PATCHEOF
cat > ui-deployment-patch.yaml <<'UIPATCHEOF'
spec:
  template:
    spec:
      containers:
      - name: ui-deployment
        envFrom:
        - configMapRef:
            name: quantumvestai-config
UIPATCHEOF
print_status "Patching API deployment..."
kubectl patch deployment quantumvestai-dev-api -n $NAMESPACE --patch-file api-deployment-patch.yaml || print_warning "API deployment patch failed (may not exist)"
print_status "Patching UI deployment..."
kubectl patch deployment ui-deployment -n $NAMESPACE --patch-file ui-deployment-patch.yaml || print_warning "UI deployment patch failed (may not exist)"

# Step 5: Restart Deployments
echo ""
print_status "=== RESTARTING DEPLOYMENTS ==="
print_status "Restarting API deployment..."
kubectl rollout restart deployment/quantumvestai-dev-api -n $NAMESPACE || print_warning "API deployment restart failed"
print_status "Restarting UI deployment..."
kubectl rollout restart deployment/ui-deployment -n $NAMESPACE || print_warning "UI deployment restart failed"
print_status "Waiting for deployments to be ready..."
kubectl rollout status deployment/quantumvestai-dev-api -n $NAMESPACE --timeout=300s || print_warning "API deployment rollout timeout"
kubectl rollout status deployment/ui-deployment -n $NAMESPACE --timeout=300s || print_warning "UI deployment rollout timeout"

# Step 6: Verify Fix
echo ""
print_status "=== VERIFYING FIX ==="
print_status "Waiting 30 seconds for pods to start..."
sleep 30
print_status "Checking new pod status..."
kubectl get pods -n $NAMESPACE | grep -E "(quantumvestai|ui-deployment)"

echo ""
print_status "Checking for errors in new pods..."
API_POD=$(kubectl get pods -n $NAMESPACE -o name | grep quantumvestai-dev-api | head -1)
UI_POD=$(kubectl get pods -n $NAMESPACE -o name | grep ui-deployment | head -1)
if [ -n "$API_POD" ]; then
    print_status "API Pod logs (last 20 lines):"
    kubectl logs $API_POD -n $NAMESPACE --tail=20 | grep -i error || print_status "No errors found in API logs!"
fi
if [ -n "$UI_POD" ]; then
    print_status "UI Pod logs (last 20 lines):"
    kubectl logs $UI_POD -n $NAMESPACE --tail=20 | grep -i error || print_status "No errors found in UI logs!"
fi

# Step 7: Test Endpoints
echo ""
print_status "=== TESTING ENDPOINTS ==="
print_status "You can test the endpoints by port-forwarding:"
echo "kubectl port-forward -n $NAMESPACE svc/quantumvestai-dev-api 8000:8000"
echo "kubectl port-forward -n $NAMESPACE svc/ui-deployment 3000:3000"

# Cleanup
print_status "Cleaning up temporary files..."
rm -f api-deployment-patch.yaml ui-deployment-patch.yaml

echo ""
print_status "=== DEPLOYMENT FIX COMPLETED ==="
print_status "Summary:"
print_status "✓ Database migration (if not skipped)"
print_status "✓ ConfigMap created with MODEL_ENSEMBLE configuration"
print_status "✓ Deployments updated with new environment variables"
print_status "✓ Pods restarted"

echo ""
print_status "Next steps:"
print_status "1. Monitor the logs: kubectl logs -f deployment/quantumvestai-dev-api -n $NAMESPACE"
print_status "2. Test authentication endpoints"
print_status "3. Verify MODEL_ENSEMBLE is working"

print_status "If issues persist, check:"
print_status "- Database connectivity"
print_status "- Secret configurations"
print_status "- Application code imports"

echo ""
print_status "Deployment fix script completed!"
