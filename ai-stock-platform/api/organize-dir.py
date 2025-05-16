import os
import shutil
from pathlib import Path
import logging
from datetime import datetime
import sys

class SecurityPackageOrganizer:
    def __init__(self, root_dir):
        self.root_dir = Path(root_dir)
        self.timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self.security_dir = self.root_dir / "api" / "core" / "security"
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'security_consolidation_{self.timestamp}.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def create_security_package_structure(self):
        """Create the new security package structure"""
        structure = {
            "api/core/security": {
                "__init__.py": self._create_init_content(),
                "auth.py": self._create_auth_content(),
                "rds.py": self._move_file("core/security/rds.py"),
                "utils.py": self._move_file("alembic/core/security_utils.py"),
                "tokens.py": self._create_token_content(),
                "encryption.py": self._create_encryption_content(),
                "permissions.py": self._create_permissions_content()
            }
        }
        return structure

    def _create_init_content(self):
        """Create content for __init__.py"""
        return '''"""
Security package for the API.

This package contains all security-related functionality including:
- Authentication and authorization
- Token handling
- Encryption utilities
- RDS security
- Permissions management
"""

from .auth import *
from .rds import *
from .utils import *
from .tokens import *
from .encryption import *
from .permissions import *

__all__ = (
    'authenticate_user',
    'create_access_token',
    'get_current_user',
    'verify_password',
    'get_password_hash',
    'RDSSecurityManager',
    'SecurityUtils',
    'TokenHandler',
    'EncryptionService',
    'PermissionManager'
)
'''

    def _create_auth_content(self):
        """Create content for auth.py"""
        return '''"""
Authentication and authorization functionality.
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .utils import SecurityUtils
from .tokens import TokenHandler
from ..deps import get_db
from ...schemas.token import TokenData
from ...schemas.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

async def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    user = await get_user(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token_data = TokenHandler.decode_token(token)
        if token_data is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = await get_user(db, token_data.username)
    if user is None:
        raise credentials_exception
    return user
'''

    def _create_token_content(self):
        """Create content for tokens.py"""
        return '''"""
Token handling functionality.
"""
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from pydantic import BaseModel

from ..config import settings

class TokenHandler:
    SECRET_KEY = settings.SECRET_KEY
    ALGORITHM = settings.ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    @classmethod
    def create_access_token(cls, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, cls.SECRET_KEY, algorithm=cls.ALGORITHM)
        return encoded_jwt

    @classmethod
    def decode_token(cls, token: str) -> Optional[BaseModel]:
        return jwt.decode(token, cls.SECRET_KEY, algorithms=[cls.ALGORITHM])
'''

    def _create_encryption_content(self):
        """Create content for encryption.py"""
        return '''"""
Encryption and hashing utilities.
"""
from cryptography.fernet import Fernet
from ..config import settings

class EncryptionService:
    def __init__(self):
        self.fernet = Fernet(settings.ENCRYPTION_KEY)

    def encrypt(self, data: str) -> str:
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        return self.fernet.decrypt(encrypted_data.encode()).decode()
'''

    def _create_permissions_content(self):
        """Create content for permissions.py"""
        return '''"""
Permission management functionality.
"""
from enum import Enum
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

class Permission(str, Enum):
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"

class PermissionManager:
    @staticmethod
    def check_permission(user_id: int, required_permission: Permission, 
                        db: Session) -> bool:
        # Implementation of permission checking logic
        pass

    @staticmethod
    def grant_permission(user_id: int, permission: Permission, 
                        db: Session) -> None:
        # Implementation of permission granting logic
        pass

    @staticmethod
    def revoke_permission(user_id: int, permission: Permission, 
                         db: Session) -> None:
        # Implementation of permission revoking logic
        pass
'''

    def _move_file(self, source_path: str):
        """Move and read content from existing file, or return None if not found"""
        source_file = self.root_dir / source_path
        if source_file.exists():
            with open(source_file, 'r') as f:
                return f.read()
        return None

    def create_backup(self):
        """Create backup of existing security files"""
        backup_dir = self.root_dir / f"security_backup_{self.timestamp}"
        
        # List of directories to backup
        backup_paths = [
            "core/security",
            "alembic/core/security_utils.py",
            "core/security.py"
        ]
        
        for path in backup_paths:
            source = self.root_dir / path
            if source.exists():
                if source.is_file():
                    dest = backup_dir / path
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, dest)
                else:
                    dest = backup_dir / path
                    shutil.copytree(source, dest, dirs_exist_ok=True)
                
        self.logger.info(f"Created backup at {backup_dir}")

    def organize(self):
        """Main organization method"""
        try:
            self.logger.info("Starting security package consolidation")
            
            # Create backup
            self.create_backup()
            
            # Create new security package structure
            structure = self.create_security_package_structure()
            
            # Create and populate the new security package
            for path, contents in structure.items():
                package_dir = self.root_dir / path
                package_dir.mkdir(parents=True, exist_ok=True)
                
                for filename, content in contents.items():
                    file_path = package_dir / filename
                    if content is None:  # File wasn't found in old location
                        self.logger.warning(f"Could not find original content for {filename}")
                        continue
                        
                    with open(file_path, 'w') as f:
                        f.write(content)
                    self.logger.info(f"Created {file_path}")
            
            self.logger.info("Security package consolidation completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error during consolidation: {str(e)}")
            raise

def main():
    # Get current directory or use provided path
    current_dir = Path.cwd()
    
    # Create organizer instance
    organizer = SecurityPackageOrganizer(current_dir)
    
    # Run organization
    try:
        organizer.organize()
        print(f"Security package consolidation completed. Check security_consolidation_{organizer.timestamp}.log for details")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()