#!/bin/bash

echo "🔍 Verifying PYTHONPATH configurations..."

echo ""
echo "=== Shell Scripts ==="
grep -n "PYTHONPATH" setup_env.sh ai-stock-platform/api/build-db-init.sh ai-stock-platform/api/docker-entrypoint.sh ai-stock-platform/api/scripts/*.sh 2>/dev/null | head -20

echo ""
echo "=== Docker Files ==="
grep -n "PYTHONPATH" ai-stock-platform/*/Dockerfile* 2>/dev/null

echo ""
echo "=== Docker Compose Files ==="
grep -n "PYTHONPATH" ai-stock-platform/*/docker-compose.yml 2>/dev/null

echo ""
echo "=== Config Files ==="
grep -n "PYTHONPATH" ci-cd/k8s/*.yaml 2>/dev/null

echo ""
echo "✅ Verification complete!"
