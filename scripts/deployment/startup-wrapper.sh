#!/bin/bash
# QuantumVestAI UI Startup Wrapper
# Created: 2025-08-04
# Author: gayatri

set -e

echo "=== QuantumVestAI UI Startup Wrapper ==="
echo "Starting UI service at $(date)"

# Apply fixes first
if [ "${FIX_IMPORT_PATHS:-true}" = "true" ]; then
  echo "Applying import path fixes..."
  if [ -f /fix-imports.sh ]; then
    bash /fix-imports.sh
  else
    echo "⚠ fix-imports.sh not found, skipping import path fixes"
  fi
fi

# Install missing dependencies
if [ "${INSTALL_MISSING_DEPS:-true}" = "true" ]; then
  echo "Checking for missing dependencies..."
  if [ -f /install-dependencies.sh ]; then
    bash /install-dependencies.sh
  else
    echo "⚠ install-dependencies.sh not found, installing critical dependencies directly"
    pip install --no-cache-dir fastapi uvicorn aiohttp requests jinja2
  fi

  # Install project specific dependencies if manifests are present. This ensures
  # containers started in ephemeral environments (like CI or ephemeral pods)
  # have all requirements prior to launching the application.
  if [ -f requirements.txt ]; then
    echo "Installing Python requirements..."
    pip install --no-cache-dir -r requirements.txt
  fi

  if command -v npm >/dev/null 2>&1 && [ -f package.json ]; then
    echo "Installing Node.js packages..."
    npm ci --omit=dev || npm install --production
  fi
fi

# Start the application using the original start script
echo "Starting UI application..."
if [ -f /scripts/start.sh ]; then
  exec /scripts/start.sh
else
  echo "⚠ start.sh not found, using default startup command"
  exec uvicorn main:app --host ${HOST:-0.0.0.0} --port ${PORT:-3000}
fi
