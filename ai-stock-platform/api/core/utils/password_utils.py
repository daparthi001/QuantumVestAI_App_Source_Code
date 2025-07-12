"""
Password Utilities Module
Created: 2025-05-21 17:07:45
Author: daparthi001
"""
from passlib.context import CryptContext

# Configure password hashing. Use pbkdf2_sha256 to avoid bcrypt dependency issues
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """
    Generate password hash using pbkdf2_sha256
    
    Args:
        password: Plain text password
        
    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        bool: True if password matches hash
    """
    return pwd_context.verify(plain_password, hashed_password)
