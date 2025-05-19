"""
Database Connection Test Script
Created: 2025-05-19 06:19:17
Author: daparthi001
"""
import sys
import os
import logging

# Add parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.utils.db import test_db_connection

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    success = test_db_connection()
    sys.exit(0 if success else 1)