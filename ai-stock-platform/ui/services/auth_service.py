# Import directly from services instead of ui.services
from services.api_client import APIClient

import jwt
import datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic import BaseModel
from config.settings import get_settings

settings = get_settings()

# Authentication models
class UserCredentials(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

# Security utilities
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    """Service for handling authentication and authorization"""

    def __init__(self, api_client=None):
        self.api_client = api_client or APIClient()
        
    def verify_password(self, plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password):
        return pwd_context.hash(password)
    
    async def authenticate_user(self, username: str, password: str):
        """Authenticate a user with username and password"""
        user = await self.api_client.get_user(username)
        if not user:
            return False
        if not self.verify_password(password, user.hashed_password):
            return False
        return user
    
    def create_access_token(self, data: dict, expires_delta: datetime.timedelta = None):
        """Create a JWT token for authenticated users"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.datetime.utcnow() + expires_delta
        else:
            expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt
    
    async def get_current_user(self, token: str = Depends(oauth2_scheme)):
        """Get the current user from a JWT token"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = TokenData(username=username)
        except jwt.PyJWTError:
            raise credentials_exception
        user = await self.api_client.get_user(token_data.username)
        if user is None:
            raise credentials_exception
        return user
    
    async def get_current_active_user(self, current_user = Depends(get_current_user)):
        """Check if the current user is active"""
        if not current_user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
        return current_user
    
    async def check_admin_access(self, current_user = Depends(get_current_user)):
        """Check if the current user has admin privileges"""
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Insufficient permissions"
            )
        return current_user