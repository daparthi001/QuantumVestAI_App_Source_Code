import boto3
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from core.config import settings
import logging

logger = logging.getLogger(__name__)

def get_connection_url():
    """
    Generate the database connection URL.
    For RDS with IAM authentication, generates a token.
    """
    if settings.USE_IAM_AUTH:
        try:
            # Generate an authentication token for RDS
            rds_client = boto3.client('rds', region_name=settings.AWS_REGION)
            auth_token = rds_client.generate_db_auth_token(
                DBHostname=settings.POSTGRES_SERVER,
                Port=settings.POSTGRES_PORT,
                DBUsername=settings.POSTGRES_USER,
                Region=settings.AWS_REGION
            )
            
            # Build connection string with token
            connection_url = f"postgresql://{settings.POSTGRES_USER}:{auth_token}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
            return connection_url
            
        except Exception as e:
            logger.error(f"Failed to generate RDS auth token: {e}")
            # Fall back to standard connection if token generation fails
            logger.warning("Falling back to standard password authentication")
            return str(settings.DATABASE_URL)
    else:
        # Use standard connection string
        return str(settings.DATABASE_URL)

# Create engine with appropriate connection settings for RDS
engine = create_engine(
    get_connection_url(),
    # These settings help with RDS connection stability
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,   # Recycle connections every hour
    connect_args={
        # Set statement timeout to 30 seconds to prevent long-running queries
        "options": "-c statement_timeout=30000",
        # Set appropriate SSL mode for RDS
        "sslmode": "require" if not settings.USE_IAM_AUTH else "prefer"
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Update the get_db function in api/db/session.py to use this connection