#!/bin/bash
# Simple environment setup script for QuantumVestAI
set -e

# Create virtual environment if not present
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

echo "Environment setup complete. Activate with 'source venv/bin/activate'"
echo "Add the API package to PYTHONPATH: export PYTHONPATH=\"$(pwd)/ai-stock-platform:$(pwd)/ai-stock-platform/api:$PYTHONPATH\""
