import os
from dotenv import load_dotenv

# Load variables from .env file (install python-dotenv first)
load_dotenv()

class Config:
    """Base Configuration - The Chassis"""
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
class DevelopmentConfig(Config):
    """Training Wheels"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///app.db')
    # It's okay to have a fallback key here for local testing
    if not Config.SECRET_KEY:
        SECRET_KEY = 'dev-secret-key-only-for-testing'

class ProductionConfig(Config):
    """War Mode"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI') # Must be Postgres
    
    # SAFETY CHECK: Crash if no key is present
    @property
    def SECRET_KEY(self):
        key = os.getenv('SECRET_KEY')
        if not key:
            raise ValueError("No SECRET_KEY set for Production configuration")
        return key

# The Selector
config_by_name = dict(
    dev=DevelopmentConfig,
    prod=ProductionConfig
)

key = Config.SECRET_KEY