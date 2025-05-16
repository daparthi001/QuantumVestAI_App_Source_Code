import os
import shutil
from datetime import datetime
import logging
from pathlib import Path
import sys

class ProjectOrganizer:
    def __init__(self, root_dir, backup=True):
        self.root_dir = Path(root_dir)
        self.backup = backup
        self.timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'project_organizer_{self.timestamp}.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def create_backup(self):
        """Create a backup of the current directory"""
        if self.backup:
            backup_dir = self.root_dir.parent / f"backup_{self.timestamp}"
            shutil.copytree(self.root_dir, backup_dir)
            self.logger.info(f"Created backup at {backup_dir}")

    def create_directory_structure(self):
        """Create the main directory structure"""
        directories = {
            # Configuration
            "config": [".env.example", ".env.template", "alembic.ini", "pyproject.toml", 
                      "requirements.txt", "setup.py"],
            
            # Docker
            "docker": ["Dockerfile", "Dockerfile.db-init", "docker-compose.yml"],
            
            # Scripts
            "scripts": ["build-db-init.sh", "deploy-to-eks.sh", "init_local_db.sh", 
                       "run_db_init.sh", "run_db_init_job.sh"],
            
            # Policies
            "policies": ["iam-policy.json", "rds_connect_policy.json"],
            
            # Main application structure
            "api": {
                "routers": ["admin.py", "auth.py", "data.py", "forecast.py", "sentiment.py", 
                           "stocks.py", "users.py", "watchlist.py", "whitepaper.py"],
                "core": ["config.py"],
                "endpoints": ["predictions.py", "social.py"],
                "db/models": ["stock.py", "stock_forecast.py", "user.py", "user_activity_log.py", 
                            "watchlist.py", "watchlist_stock.py"]
            },
            
            # Core functionality
            "core": {
                ".": ["cache.py", "config.py", "db_init.py", "deps.py", "exceptions.py", 
                      "logging_config.py", "middleware.py", "security.py"],
                "security": ["rds.py"]
            },
            
            # Database
            "db": {
                ".": ["base_class.py", "rds_session.py"],
                "models": ["stock.py", "user.py", "whitepaper.py"]
            },
            
            # Database initialization
            "db_init": ["01_create_database.sql", "01_create_tables.sql", "01_seed_data.py",
                       "02_reference_data.sql", "03_create_admin.py", "04_seed_sample_data.py"],
            
            # Alembic migrations
            "alembic": {
                ".": ["README", "env.py", "script.py.mako"],
                "core": {
                    ".": ["cache.py", "config.py", "db_init.py", "deps.py", "exceptions.py",
                          "logging_config.py", "middleware.py", "security_utils.py"],
                    "security_pkg": ["rds.py"]
                },
                "versions": ["0001_initial_schema.py", "20250515_initial_schema.py"],
                "db/models": ["stock.py", "user.py", "whitepaper.py"]
            },
            
            # Machine Learning
            "ml": ["models.py", "train_models.py"],
            "models": {
                ".": ["arima.py", "base.py", "ensemble.py", "finbert_sentiment.py", "lstm.py",
                      "prophet.py", "xgboost_model.py"],
                "forecasting": []
            },
            
            # Schemas
            "schemas": ["prediction.py", "stock.py", "token.py", "user.py", "watchlist.py",
                       "whitepaper.py"],
            
            # Services
            "services": ["data_service.py", "forecast_service.py", "twitter_service.py",
                        "twitter_sentiment_scheduler.py"],
            
            # Utils
            "utils": ["data_loader.py", "feature_engineering.py", "logging.py", "pipeline.py",
                     "validators.py", "whitepaper_analysis.py"]
        }
        
        return directories

    def create_init_files(self, directory):
        """Create __init__.py files in Python package directories"""
        if any(f.endswith('.py') for f in os.listdir(directory)):
            init_file = directory / '__init__.py'
            if not init_file.exists():
                init_file.touch()
                self.logger.info(f"Created {init_file}")

    def create_directory(self, path):
        """Create directory if it doesn't exist"""
        if not path.exists():
            path.mkdir(parents=True)
            self.logger.info(f"Created directory {path}")

    def move_file(self, src, dest):
        """Move file to new location"""
        if src.exists():
            if dest.exists():
                new_dest = dest.parent / f"{dest.stem}_{self.timestamp}{dest.suffix}"
                self.logger.warning(f"File {dest} exists, moving to {new_dest}")
                dest = new_dest
            shutil.move(str(src), str(dest))
            self.logger.info(f"Moved {src} to {dest}")
        else:
            self.logger.warning(f"Source file {src} does not exist")

    def organize_directory(self, base_path, structure):
        """Recursively organize directory structure"""
        for name, content in structure.items():
            current_path = base_path / name
            self.create_directory(current_path)
            
            if isinstance(content, list):
                # Handle files
                for file in content:
                    src = self.root_dir / file
                    dest = current_path / file
                    self.move_file(src, dest)
                self.create_init_files(current_path)
            elif isinstance(content, dict):
                # Handle nested directories
                self.organize_directory(current_path, content)
                if "." in content:
                    # Handle files in current directory
                    for file in content["."]:
                        src = self.root_dir / file
                        dest = current_path / file
                        self.move_file(src, dest)
                self.create_init_files(current_path)

    def organize(self):
        """Main organization method"""
        try:
            self.logger.info(f"Starting project organization in {self.root_dir}")
            self.create_backup()
            
            # Create and move main.py and root __init__.py
            for file in ["main.py", "__init__.py"]:
                src = self.root_dir / file
                if src.exists():
                    self.logger.info(f"Keeping {file} in root directory")
            
            # Create and organize directory structure
            structure = self.create_directory_structure()
            self.organize_directory(self.root_dir, structure)
            
            self.logger.info("Project organization completed successfully")
        except Exception as e:
            self.logger.error(f"Error during organization: {str(e)}")
            raise

def main():
    # Get current directory or use provided path
    current_dir = Path.cwd()
    
    # Create organizer instance
    organizer = ProjectOrganizer(current_dir)
    
    # Run organization
    try:
        organizer.organize()
        print(f"Organization completed. Check project_organizer_{organizer.timestamp}.log for details")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()