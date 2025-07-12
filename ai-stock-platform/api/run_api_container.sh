#!/bin/bash
# Run the QuantumVestAI API container with Docker Compose
# This script builds and starts the API along with its dependencies
# to help debug container build issues.
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Choose docker compose command
if command -v docker-compose >/dev/null 2>&1; then
    COMPOSE="docker-compose"
else
    COMPOSE="docker compose"
fi

$COMPOSE -f docker-compose.yml up --build
