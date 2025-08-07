#!/bin/bash
# QuantumVestAI Import Path Fix
# Created: 2025-08-04
# Author: gayatri

set -e

echo "=== QuantumVestAI Import Path Fix ==="
echo "Starting fix process at $(date)"

# Fix utils/__init__.py import paths
if [ -f /utils/__init__.py ]; then
  echo "Fixing import paths in utils/__init__.py"
  # Replace "from ui.utils" with "from utils"
  sed -i 's/from ui\.utils/from utils/g' /utils/__init__.py
  echo "✓ utils/__init__.py updated"
else
  echo "⚠ utils/__init__.py not found"
fi

# Fix template_filters.py
if [ -f /utils/template_filters.py ]; then
  echo "Fixing template_filters.py"
  # Replace app.jinja_env with templates.env if it exists
  sed -i 's/app\.jinja_env/templates.env/g' /utils/template_filters.py
  echo "✓ utils/template_filters.py updated"
else
  echo "⚠ utils/template_filters.py not found"
fi

# Update main.py to store templates in app.state
if [ -f /main.py ]; then
  echo "Checking main.py for app.state.templates setting"
  if grep -q "templates = Jinja2Templates" /main.py && ! grep -q "app.state.templates = templates" /main.py; then
    echo "Adding app.state.templates assignment to main.py"
    sed -i '/templates = Jinja2Templates/a app.state.templates = templates  # Store templates in app.state' /main.py
    echo "✓ main.py updated"
  else
    echo "✓ main.py already has correct templates configuration"
  fi
else
  echo "⚠ main.py not found"
fi

echo "Import path fix completed at $(date)"
echo "===================================="
