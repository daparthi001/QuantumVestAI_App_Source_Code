"""
Database Initialization Script
Created: 2025-05-19 05:45:27
Author: daparthi001
"""
import logging
from sqlalchemy.orm import Session
from core.config import settings
from core.security.utils import SecurityUtils
from api.db.base import Base
from api.db.models.user import User

logger = logging.getLogger(__name__)

def init_db(db: Session) -> None:
    """Initialize database with required initial data"""
    try:
        # Create tables
        Base.metadata.create_all(bind=db.get_bind())
        
        # Check if we need to create the initial admin user
        admin_exists = db.query(User).filter(
            User.email == settings.ADMIN_EMAIL
        ).first()
        
        if not admin_exists:
            admin_user = User(
                email=settings.ADMIN_EMAIL,
                username=settings.ADMIN_USERNAME,
                hashed_password=SecurityUtils.get_password_hash(
                    settings.ADMIN_PASSWORD
                ),
                full_name="System Administrator",
                is_superuser=True,
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            logger.info(
                f"Created admin user: {settings.ADMIN_USERNAME}"
            )
    
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise