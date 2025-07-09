import os
import shutil
from datetime import datetime
from pathlib import Path
import logging
from typing import List, Dict
import json

class ProjectSetup:
    """Main project setup implementation"""
    def __init__(self, api_root: Path, logger: logging.Logger):
        self.api_root = api_root
        self.logger = logger

    def create_directory_structure(self):
        """Create necessary directories"""
        directories = [
            "core/security",
            "db/models",
            "schemas",
            "routers",
            "core/config"
        ]
        
        for directory in directories:
            dir_path = self.api_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created directory: {dir_path}")

    def create_file(self, path: str, content: str):
        """Create a file with given content"""
        file_path = self.api_root / path
        file_path.write_text(content)
        self.logger.info(f"Created/Updated file: {file_path}")
        return file_path

    def setup(self):
        """Execute the actual setup process"""
        # Create directory structure
        self.create_directory_structure()
        
        # Create/Update all files
        self.setup_security_package()
        self.setup_database()
        self.setup_schemas()
        self.setup_config()
        self.setup_requirements()
        
        return True

    def setup_security_package(self):
        """Set up the security package"""
        security_files = {
            "core/security/__init__.py": '''"""
Security package initialization.
"""
from .auth import *
from .utils import *
from .tokens import *
from .permissions import *
from .encryption import *
from .rds import *

__version__ = "1.0.0"
''',
            "core/security/auth.py": '''"""
Authentication functionality.
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
# Updated import to absolute path to avoid relative import issues
from db.session import get_db
from ...schemas.token import TokenData
from ...schemas.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
''',
            # Add all other security files here...
        }
        
        for file_path, content in security_files.items():
            self.create_file(file_path, content)

    def setup_database(self):
        """Set up database related files"""
        db_files = {
            "db/__init__.py": '''"""
Database package initialization.
"""
from .session import SessionLocal, get_db

__all__ = ["SessionLocal", "get_db"]
''',
            # Add other DB files...
        }
        
        for file_path, content in db_files.items():
            self.create_file(file_path, content)

    def setup_schemas(self):
        """Set up schema files"""
        schema_files = {
            "schemas/__init__.py": '''"""
Schemas package initialization.
"""
from .user import User, UserCreate, UserBase
from .token import Token, TokenData
from .stock import *
from .prediction import *
from .watchlist import *
from .whitepaper import *

__all__ = [
    "User", "UserCreate", "UserBase",
    "Token", "TokenData"
]
''',
            # Add other schema files...
        }
        
        for file_path, content in schema_files.items():
            self.create_file(file_path, content)

    def setup_config(self):
        """Set up configuration"""
        self.create_file("core/config/__init__.py", '''"""
Application configuration.
"""
from pydantic_settings import BaseSettings
import os
from functools import lru_cache

class Settings(BaseSettings):
    # Database
    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/dbname"
    )
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-for-jwt")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AWS
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_DEFAULT_REGION: str = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
''')

    def setup_requirements(self):
        """Create requirements.txt"""
        requirements = '''fastapi==0.105.0
uvicorn==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.2
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
email-validator==2.1.0.post1
psycopg2-binary==2.9.9
boto3==1.34.7
pandas==2.1.3
numpy==1.26.2
scikit-learn==1.3.2
'''
        self.create_file("requirements.txt", requirements)

class SafeProjectSetup:
    """Safe wrapper for project setup with backup and rollback capabilities"""
    def __init__(self):
        self.api_root = Path.cwd()
        self.timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = self.api_root / f"backup_{self.timestamp}"
        self.modified_files: List[Path] = []
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'setup_{self.timestamp}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def analyze_existing_structure(self) -> Dict[str, List[str]]:
        """Analyze existing project structure"""
        analysis = {
            "existing_files": [],
            "existing_dirs": [],
            "will_modify": [],
            "will_create": []
        }
        
        dirs_to_check = [
            "core/security",
            "db/models",
            "schemas",
            "routers",
            "core/config"
        ]
        
        for dir_path in dirs_to_check:
            full_path = self.api_root / dir_path
            if full_path.exists():
                analysis["existing_dirs"].append(dir_path)
                for file in full_path.glob("**/*"):
                    if file.is_file():
                        rel_path = str(file.relative_to(self.api_root))
                        analysis["existing_files"].append(rel_path)
                        analysis["will_modify"].append(rel_path)
            else:
                analysis["will_create"].append(dir_path)
        
        return analysis

    def create_backup(self, files_to_backup: List[str]):
        """Create backup of existing files"""
        if not files_to_backup:
            self.logger.info("No files to backup")
            return
        
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Creating backup in {self.backup_dir}")
        
        for file_path in files_to_backup:
            source = self.api_root / file_path
            if source.exists():
                dest = self.backup_dir / file_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                
                if source.is_file():
                    shutil.copy2(source, dest)
                    self.logger.info(f"Backed up {file_path}")

    def restore_from_backup(self):
        """Restore files from backup"""
        if not self.backup_dir.exists():
            self.logger.error("No backup directory found!")
            return
        
        self.logger.info("Restoring from backup...")
        
        for root, _, files in os.walk(self.backup_dir):
            for file in files:
                backup_file = Path(root) / file
                relative_path = backup_file.relative_to(self.backup_dir)
                target_file = self.api_root / relative_path
                
                if target_file.exists():
                    target_file.unlink()
                
                target_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(backup_file, target_file)
                self.logger.info(f"Restored {relative_path}")

    def run(self):
        """Execute the setup process with safety checks"""
        try:
            self.logger.info("Starting safe project setup...")
            
            # Analyze existing structure
            analysis = self.analyze_existing_structure()
            
            # Create backup
            self.create_backup(analysis["existing_files"])
            
            # Execute actual setup
            project_setup = ProjectSetup(self.api_root, self.logger)
            if project_setup.setup():
                self.logger.info("Project setup completed successfully!")
            else:
                raise Exception("Setup failed")
            
        except Exception as e:
            self.logger.error(f"Error during setup: {str(e)}")
            print("\nError occurred during setup. Attempting to restore from backup...")
            self.restore_from_backup()
            print("Restoration completed. Please check the log file for details.")
            raise

if __name__ == "__main__":
    # Verify we're in the api directory
    if not Path.cwd().name == "api":
        print("Error: This script must be run from the api directory!")
        print("Please cd to the api directory first.")
        exit(1)
    
    # Create and run the safe setup
    safe_setup = SafeProjectSetup()
    safe_setup.run()