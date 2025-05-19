"""
Database initialization
Created: 2025-05-19 03:27:22
Author: daparthi001
"""
from sqlalchemy.orm import Session
from api.core.config import settings
from api.models.user import User
from api.core.security import get_password_hash
import logging

logger = logging.getLogger(__name__)

def init_db(db: Session) -> None:
    """Initialize the database with required data"""
    # Create super user if it doesn't exist
    user = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
    if not user:
        user = User(
            email=settings.ADMIN_EMAIL,
            username=settings.ADMIN_USERNAME,
            full_name="System Administrator",
            is_superuser=True
        )
        user.set_password(settings.ADMIN_PASSWORD.get_secret_value())
        db.add(user)
        db.commit()
        logger.info(f"Created admin user: {settings.ADMIN_USERNAME}")