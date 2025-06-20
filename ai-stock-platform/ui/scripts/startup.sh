#!/bin/bash
# Startup script for QuantumVestAI UI container
# Last updated: 2025-06-20 03:02:57
# Updated by: daparthi001

set -e

echo "Starting QuantumVestAI UI container"
echo "Current time: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"

# Create necessary directories if they don't exist
echo "Setting up directory structure..."
mkdir -p /app/utils /app/controllers /app/auth /app/templates/dashboard /app/templates/auth

# Copy configuration files from ConfigMap mount if they exist
echo "Checking for configuration files in /config..."
if [ -d "/config" ]; then
    echo "ConfigMap volume found, copying files..."
    
    # Copy utils files
    if [ -f "/config/utils.template_filters.py" ]; then
        echo "Copying template filters..."
        cp /config/utils.template_filters.py /app/utils/template_filters.py
    else
        echo "Warning: utils.template_filters.py not found in ConfigMap"
    fi
    
    # Copy controller files
    if [ -f "/config/controllers.dashboard_controller.py" ]; then
        echo "Copying dashboard controller..."
        cp /config/controllers.dashboard_controller.py /app/controllers/dashboard_controller.py
    else
        echo "Warning: controllers.dashboard_controller.py not found in ConfigMap"
    fi
    
    # Copy auth files
    if [ -f "/config/auth.dependencies.py" ]; then
        echo "Copying auth dependencies..."
        cp /config/auth.dependencies.py /app/auth/dependencies.py
    else
        echo "Warning: auth.dependencies.py not found in ConfigMap"
    fi
    
    # Copy template files
    if [ -f "/config/templates.base.html" ]; then
        echo "Copying base template..."
        cp /config/templates.base.html /app/templates/base.html
    else
        echo "Warning: templates.base.html not found in ConfigMap"
    fi
    
    if [ -f "/config/templates.dashboard.index.html" ]; then
        echo "Copying dashboard template..."
        cp /config/templates.dashboard.index.html /app/templates/dashboard/index.html
    else
        echo "Warning: templates.dashboard.index.html not found in ConfigMap"
    fi
    
    if [ -f "/config/templates.error.html" ]; then
        echo "Copying error template..."
        cp /config/templates.error.html /app/templates/error.html
    else
        echo "Warning: templates.error.html not found in ConfigMap"
    fi
    
    if [ -f "/config/templates.auth.login.html" ]; then
        echo "Copying login template..."
        cp /config/templates.auth.login.html /app/templates/auth/login.html
    else
        echo "Warning: templates.auth.login.html not found in ConfigMap"
    fi
    
    echo "Configuration files setup complete."
else
    echo "Warning: ConfigMap volume not found at /config"
    echo "Using default configuration files if available."
fi

# Set proper permissions
echo "Setting file permissions..."
chmod -R 755 /app

# Generate static assets if needed
echo "Checking if static assets need to be generated..."
if [ -f "/app/static/css/styles.css" ]; then
    echo "Static assets already exist, skipping generation."
else
    echo "Generating static assets..."
    npm run build
fi

# Start the application
echo "Starting the application..."
exec gunicorn --bind 0.0.0.0:8080 --workers 4 --worker-class uvicorn.workers.UvicornWorker --timeout 120 app.main:app