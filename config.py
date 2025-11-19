import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'dev-secret-key'
    
    # Supabase Configuration
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    
    # Database Configuration - pg8000 for Python 3.13 compatibility
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if DATABASE_URL:
        # Convert to pg8000 format for Python 3.13 compatibility
        if DATABASE_URL.startswith('postgres://'):
            SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace('postgres://', 'postgresql+pg8000://')
        elif DATABASE_URL.startswith('postgresql://'):
            SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace('postgresql://', 'postgresql+pg8000://')
        else:
            SQLALCHEMY_DATABASE_URI = DATABASE_URL
        
        # Add SSL for pg8000
        if 'sslmode=' not in SQLALCHEMY_DATABASE_URI:
            separator = '&' if '?' in SQLALCHEMY_DATABASE_URI else '?'
            SQLALCHEMY_DATABASE_URI += f'{separator}sslmode=require'
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///products.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis Configuration
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # Celery Configuration
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    
    # Upload Configuration
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB max file size
    UPLOAD_FOLDER = 'uploads'
    
    # Application Configuration
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')