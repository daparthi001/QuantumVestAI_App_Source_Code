"""
Security utility functions.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

from api.db.session import get_db  # Changed to absolute import
from api.core.config import settings  # Changed to absolute import

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class SecurityUtils:
    """Security utility functions."""
    
    @staticmethod
    def get_db_session(db: Session = Depends(get_db)) -> Session:
        """Get database session."""
        return db

    @staticmethod
    def validate_token(token: str) -> bool:
        """
        Validate JWT token.
        
        Args:
            token: JWT token to validate
            
        Returns:
            bool: True if token is valid
            
        Raises:
            HTTPException: If token is invalid
        """
        try:
            # Decode JWT token
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            
            # Check if token has expired
            exp = payload.get("exp")
            if exp is None:
                return False
                
            expiration = datetime.fromtimestamp(exp)
            if datetime.utcnow() > expiration:
                return False
                
            return True
            
        except JWTError:
            return False

    @staticmethod
    def hash_data(data: str) -> str:
        """
        Hash sensitive data using bcrypt.
        
        Args:
            data: Data to hash
            
        Returns:
            str: Hashed data
        """
        return pwd_context.hash(data)
    
    @staticmethod
    def verify_hash(plain_data: str, hashed_data: str) -> bool:
        """
        Verify hashed data.
        
        Args:
            plain_data: Plain text data
            hashed_data: Hashed data to verify against
            
        Returns:
            bool: True if verification succeeds
        """
        return pwd_context.verify(plain_data, hashed_data)
    
    @staticmethod
    def create_access_token(
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT access token.
        
        Args:
            data: Data to encode in token
            expires_delta: Optional expiration time
            
        Returns:
            str: Encoded JWT token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
            
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "sub": str(data.get("user_id", ""))
        })
        
        return jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify password against hash.
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password to verify against
            
        Returns:
            bool: True if verification succeeds
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """
        Get password hash.
        
        Args:
            password: Plain text password
            
        Returns:
            str: Hashed password
        """
        return pwd_context.hash(password)
