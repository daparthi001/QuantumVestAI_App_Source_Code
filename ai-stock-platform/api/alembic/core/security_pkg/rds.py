"""
RDS security utilities for QuantumVestAI.

This module provides security utilities for working with Amazon RDS.
"""

import logging

import boto3
from botocore.exceptions import ClientError
from core.config import settings

logger = logging.getLogger(__name__)

def validate_rds_connection():
    """
    Validates that the application can connect to the RDS instance.
    """
    try:
        from db.rds_session import get_connection_url
        from sqlalchemy import create_engine, text
        from sqlalchemy.exc import SQLAlchemyError

        connection_url = get_connection_url()
        # Create a temporary engine just for testing
        test_engine = create_engine(connection_url)
        
        # Try to execute a simple query
        with test_engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            row = result.fetchone()
            if row and row[0] == 1:
                logger.info("RDS connection validated successfully")
                return True
            else:
                logger.error("RDS connection validation failed")
                return False
    
    except SQLAlchemyError as e:
        logger.error(f"Database connection error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error validating RDS connection: {e}")
        return False

def describe_rds_instance():
    """
    Gets information about the RDS instance, if AWS credentials allow.
    """
    try:
        # Extract the instance identifier from the host name
        db_instance_identifier = settings.POSTGRES_SERVER.split('.')[0]
        
        # Create RDS client
        rds_client = boto3.client('rds', region_name=settings.AWS_REGION)
        
        # Get instance information
        response = rds_client.describe_db_instances(
            DBInstanceIdentifier=db_instance_identifier
        )
        
        if 'DBInstances' in response and len(response['DBInstances']) > 0:
            instance = response['DBInstances'][0]
            return {
                'status': instance['DBInstanceStatus'],
                'instance_class': instance['DBInstanceClass'],
                'engine': instance['Engine'],
                'engine_version': instance['EngineVersion'],
                'storage': f"{instance['AllocatedStorage']} GB",
                'multi_az': instance['MultiAZ'],
                'publicly_accessible': instance['PubliclyAccessible']
            }
        return None
    
    except ClientError as e:
        logger.warning(f"Could not describe RDS instance: {e}")
        return None
