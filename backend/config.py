"""
Configuration settings for the application
Loads environment variables from .env file
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration class"""

    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL')

    # JWT Configuration
    JWT_SECRET = os.getenv('JWT_SECRET', 'default_secret_key_change_this')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
    JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', 2))

    # Flask Configuration
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    PORT = int(os.getenv('PORT', 3000))

    # CORS Configuration
    CORS_ORIGINS = ["*"]  # In production, specify exact origins

    @staticmethod
    def validate():
        """Validate that all required configuration is present"""
        if not Config.DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable is not set!")
        if not Config.JWT_SECRET:
            raise ValueError("JWT_SECRET environment variable is not set!")
        print("✅ Configuration validated successfully")


# Create config instance
config = Config()