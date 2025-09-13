"""
Environment configuration for the AI User Learning System
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the application"""
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///user_learning.db')
    DATABASE_ECHO = os.getenv('DATABASE_ECHO', 'False').lower() == 'true'
    
    # Security Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
    ENCRYPTION_MASTER_KEY = os.getenv('ENCRYPTION_MASTER_KEY')
    
    # Application Configuration
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    PORT = int(os.getenv('PORT', 5000))
    HOST = os.getenv('HOST', '0.0.0.0')
    
    # Privacy and Compliance
    DEFAULT_DATA_RETENTION_DAYS = int(os.getenv('DEFAULT_DATA_RETENTION_DAYS', 365))
    ENABLE_AUDIT_LOGGING = os.getenv('ENABLE_AUDIT_LOGGING', 'True').lower() == 'true'
    ANONYMIZE_LOGS = os.getenv('ANONYMIZE_LOGS', 'True').lower() == 'true'
    
    # AI Learning Configuration
    ENABLE_REAL_TIME_LEARNING = os.getenv('ENABLE_REAL_TIME_LEARNING', 'True').lower() == 'true'
    MIN_INTERACTIONS_FOR_LEARNING = int(os.getenv('MIN_INTERACTIONS_FOR_LEARNING', 5))
    LEARNING_CONFIDENCE_THRESHOLD = float(os.getenv('LEARNING_CONFIDENCE_THRESHOLD', 0.6))
    
    # API Rate Limiting
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', 60))
    RATE_LIMIT_PER_HOUR = int(os.getenv('RATE_LIMIT_PER_HOUR', 1000))
    
    @classmethod
    def validate_config(cls):
        """Validate critical configuration settings"""
        warnings = []
        errors = []
        
        # Check for production-ready secrets
        if cls.SECRET_KEY == 'dev-secret-key-change-in-production':
            warnings.append("Using default SECRET_KEY - change in production!")
        
        if cls.JWT_SECRET_KEY == 'jwt-secret-change-in-production':
            warnings.append("Using default JWT_SECRET_KEY - change in production!")
        
        if not cls.ENCRYPTION_MASTER_KEY:
            warnings.append("No ENCRYPTION_MASTER_KEY set - a new one will be generated")
        
        # Check database configuration
        if cls.DATABASE_URL.startswith('sqlite:///') and not cls.DEBUG:
            warnings.append("Using SQLite in production - consider PostgreSQL for better performance")
        
        return warnings, errors


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    DATABASE_ECHO = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    DATABASE_ECHO = False
    
    # More secure defaults for production
    ENABLE_AUDIT_LOGGING = True
    ANONYMIZE_LOGS = True


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'  # In-memory database for tests
    SECRET_KEY = 'testing-secret-key'
    JWT_SECRET_KEY = 'testing-jwt-secret'


# Configuration factory
def get_config(env_name: str = None):
    """Get configuration based on environment name"""
    env_name = env_name or os.getenv('FLASK_ENV', 'development')
    
    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    return config_map.get(env_name, DevelopmentConfig)