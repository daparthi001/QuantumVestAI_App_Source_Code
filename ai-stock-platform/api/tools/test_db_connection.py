"""
Database Connection Test Script
Created: 2025-05-22 04:45:11
Author: daparthi001
"""
from sqlalchemy import create_engine
from urllib.parse import quote_plus

# Database configuration
config = {
    'host': 'quantumvestai-dev.cwbsqsiywwaa.us-east-1.rds.amazonaws.com',
    'port': '5432',
    'database': 'quantumvestaidb',
    'user': 'dbadmin',
    'password': '75LerK%0_J<t$H}Z'
}

# Create connection URL
password = quote_plus(config['password'])
db_url = (
    f"postgresql://{config['user']}:{password}"
    f"@{config['host']}:{config['port']}/{config['database']}"
)

# Create engine
engine = create_engine(
    db_url,
    connect_args={
        "connect_timeout": 10,
        "application_name": "quantumvestai_test",
        "sslmode": "require"
    }
)

# Test connection
try:
    with engine.connect() as conn:
        result = conn.execute("SELECT version()").scalar()
        print(f"Successfully connected to PostgreSQL:\n{result}")
except Exception as e:
    print(f"Connection failed: {str(e)}")