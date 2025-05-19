#!/bin/bash
"""
Docker Entrypoint Script
Created: 2025-05-19 05:56:45
Author: daparthi001
"""
set -e

# Install any missing dependencies
pip install -r requirements.txt

# Wait for database to be ready
python scripts/test_db_connection.py

# Run database migrations
alembic upgrade head

# Start the FastAPI application
exec uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4