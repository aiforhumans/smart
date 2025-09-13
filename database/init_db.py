"""
Database initialization script
Run this to set up the database for the first time
"""

import os
import sys
import logging
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

from database import init_database, db_manager
from models import User, UserProfile

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_sample_data():
    """Create some sample data for testing"""
    logger.info("Creating sample data...")
    
    try:
        with db_manager.get_session() as session:
            from database import UserRepository
            
            user_repo = UserRepository(session)
            
            # Create a sample user
            sample_user = user_repo.create_user(
                username="demo_user",
                email="demo@example.com",
                data_sharing_consent=True,
                learning_enabled=True
            )
            
            # Update the user's profile with some basic info
            profile = sample_user.profile
            profile.preferred_language = "en"
            profile.communication_style = "friendly"
            profile.response_length_preference = "detailed"
            profile.technical_level = "intermediate"
            profile.interests = ["technology", "science", "programming"]
            profile.hobbies = ["reading", "coding", "learning"]
            
            logger.info(f"Created sample user: {sample_user.username} (ID: {sample_user.id})")
            
    except Exception as e:
        logger.error(f"Failed to create sample data: {e}")
        raise


def main():
    """Main initialization function"""
    logger.info("Initializing AI User Learning System database...")
    
    try:
        # Check if database file already exists
        db_path = "user_learning.db"
        if os.path.exists(db_path):
            response = input(f"Database file {db_path} already exists. Recreate it? (y/N): ")
            if response.lower() != 'y':
                logger.info("Database initialization cancelled.")
                return
            
            # Remove existing database
            os.remove(db_path)
            logger.info("Existing database removed.")
        
        # Initialize database tables
        logger.info("Creating database tables...")
        init_database()
        
        # Check database health
        if db_manager.health_check():
            logger.info("Database health check passed!")
        else:
            logger.error("Database health check failed!")
            return
        
        # Create sample data
        create_sample = input("Create sample data for testing? (Y/n): ")
        if create_sample.lower() != 'n':
            create_sample_data()
        
        logger.info("Database initialization completed successfully!")
        logger.info(f"Database file created at: {os.path.abspath(db_path)}")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()