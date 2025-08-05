import logging
import os
import re
import shutil
from datetime import datetime
from pathlib import Path


class ImportFixer:
    def __init__(self):
        self.api_root = Path.cwd()
        self.timestamp = "20250517_000635"
        self.backup_dir = self.api_root / f"backup_imports_{self.timestamp}"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'import_fix_{self.timestamp}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def create_base_module(self):
        """Create the database base module"""
        base_content = '''"""
SQLAlchemy declarative base.
"""
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
'''
        base_path = self.api_root / 'db' / 'base.py'
        base_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Backup if exists
        if base_path.exists():
            self.backup_file(base_path)
        
        base_path.write_text(base_content)
        self.logger.info("Created/Updated database base module")

        # Update db/__init__.py to export Base
        init_content = '''"""
Database package initialization.
"""
from .session import SessionLocal, get_db
from .base import Base

__all__ = ["SessionLocal", "get_db", "Base"]
'''
        init_path = self.api_root / 'db' / '__init__.py'
        if init_path.exists():
            self.backup_file(init_path)
        init_path.write_text(init_content)
        self.logger.info("Updated database __init__.py")

    def update_db_session(self):
        """Update database session module"""
        session_content = '''"""
Database session handling module.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from ..core.config import settings

# Create SQLAlchemy engine
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """
    Get database session.
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''
        session_path = self.api_root / 'db' / 'session.py'
        if session_path.exists():
            self.backup_file(session_path)
        session_path.write_text(session_content)
        self.logger.info("Updated database session module")

    def update_models(self):
        """Update model files to use correct Base import"""
        model_files = {
            'user.py': '''"""
User model.
"""
from sqlalchemy import Boolean, Column, Integer, String
from ..base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
''',
            'stock.py': '''"""
Stock model.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime
from ..base import Base

class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True)
    name = Column(String)
    current_price = Column(Float)
    last_updated = Column(DateTime)
''',
            '__init__.py': '''"""
Models package initialization.
"""
from .user import User
from .stock import Stock

__all__ = ["User", "Stock"]
'''
        }
        
        models_dir = self.api_root / 'db' / 'models'
        models_dir.mkdir(parents=True, exist_ok=True)
        
        for filename, content in model_files.items():
            file_path = models_dir / filename
            if file_path.exists():
                self.backup_file(file_path)
            file_path.write_text(content)
            self.logger.info(f"Updated model file: {filename}")

    def fix_imports_in_file(self, file_path: Path):
        try:
            if not file_path.suffix == '.py':
                return

            content = file_path.read_text()
            original_content = content

            base_import_pattern = r'from [\.\w]+db\.session import (?:[\w, ]+,\s*)?Base(?:\s*,\s*[\w, ]+)?'
            if re.search(base_import_pattern, content):
                self.backup_file(file_path)

                rel_path = len(file_path.relative_to(self.api_root).parts) - 1
                dots = '.' * rel_path

                content = re.sub(
                    base_import_pattern,
                    lambda m: m.group().replace('db.session import', f'db.base import').replace('session import Base', 'base import Base'),
                    content
                )

                if content != original_content:
                    file_path.write_text(content)
                    self.logger.info(f"Fixed Base import in {file_path}")
        except Exception as e:
            self.logger.error(f"Error processing {file_path}: {str(e)}")

    def backup_file(self, file_path: Path):
        """Create backup of a file"""
        if not file_path.exists():
            return
            
        relative_path = file_path.relative_to(self.api_root)
        backup_path = self.backup_dir / relative_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, backup_path)
        self.logger.info(f"Backed up {relative_path}")

    def run(self):
        """Execute the import fixing process"""
        try:
            self.logger.info("Starting import fixes...")
            
            # Create backup directory
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Create/Update base module first
            self.create_base_module()
            
            # Update session module
            self.update_db_session()
            
            # Update models
            self.update_models()
            
            # Fix imports in all Python files
            for root, _, files in os.walk(self.api_root):
                for file in files:
                    if file.endswith('.py'):
                        file_path = Path(root) / file
                        self.fix_imports_in_file(file_path)
            
            self.logger.info("Import fixes completed successfully!")
            
            print("\nNext steps:")
            print("1. Review the changes in the updated files")
            print("2. Test the application:")
            print("   uvicorn main:app --reload")
            print(f"\nBackup of original files is in: {self.backup_dir}")
            print("Check the log file for details of all changes made.")
            
        except Exception as e:
            self.logger.error(f"Error during update: {str(e)}")
            raise

if __name__ == "__main__":
    # Verify we're in the api directory
    if not Path.cwd().name == "api":
        print("Error: This script must be run from the api directory!")
        print("Please cd to the api directory first.")
        exit(1)
    
    # Create and run the fixer
    fixer = ImportFixer()
    fixer.run()
