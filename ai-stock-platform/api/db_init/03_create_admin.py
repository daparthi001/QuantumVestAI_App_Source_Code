#!/usr/bin/env python3
"""
Create admin user for QuantumVestAI application.
"""

import argparse
import logging
import os
import sys
from datetime import datetime

import psycopg2
from passlib.context import CryptContext

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('db-init')

# Password hashing
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def create_admin_user():
    """Create admin user in the database."""
    # Get credentials from environment variables
    db_host = os.environ.get('DB_HOST', os.environ.get('POSTGRES_SERVER', 'db'))
    db_name = os.environ.get('DB_NAME', os.environ.get('POSTGRES_DB'))
    db_user = os.environ.get('DB_USER', os.environ.get('POSTGRES_USER'))
    db_password = os.environ.get('DB_PASSWORD', os.environ.get('POSTGRES_PASSWORD'))
    db_port = os.environ.get('DB_PORT', os.environ.get('POSTGRES_PORT', '5432'))
    
    # Get admin user details
    admin_username = os.environ.get('ADMIN_USERNAME')
    admin_email = os.environ.get('ADMIN_EMAIL')
    admin_password = os.environ.get('ADMIN_PASSWORD')
    admin_fullname = os.environ.get('ADMIN_FULL_NAME', 'System Administrator')
    
    if not all([admin_username, admin_email, admin_password]):
        logger.warning("Admin credentials incomplete. Skipping admin creation.")
        return False
    
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
            port=db_port
        )
        
        # Create a cursor
        cur = conn.cursor()
        
        # Check if user already exists
        cur.execute("SELECT id FROM users WHERE username = %s OR email = %s", 
                    (admin_username, admin_email))
        existing_user = cur.fetchone()
        
        now = datetime.utcnow()
        
        if existing_user:
            # Update existing user to admin role
            logger.info(f"User {admin_username} already exists. Updating to admin role.")
            cur.execute("""
                UPDATE users 
                SET role = 'admin', 
                    is_active = true,
                    last_login = %s
                WHERE id = %s
            """, (now, existing_user[0]))
        else:
            # Create new admin user
            hashed_password = pwd_context.hash(admin_password)
            
            logger.info(f"Creating new admin user: {admin_username}")
            cur.execute("""
                INSERT INTO users (
                    username, email, full_name, hashed_password, 
                    is_active, role, created_at, last_login
                ) VALUES (
                    %s, %s, %s, %s, true, 'admin', %s, %s
                )
            """, (admin_username, admin_email, admin_fullname, 
                 hashed_password, now, now))
        
        # Commit the transaction
        conn.commit()
        
        # Close the cursor and connection
        cur.close()
        conn.close()
        
        logger.info("Admin user setup completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error creating admin user: {e}")
        return False

if __name__ == "__main__":
    create_admin_user()
