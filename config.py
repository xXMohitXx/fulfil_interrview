import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'dev-secret-key'
    
    # Supabase Configuration
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    
    # Database Configuration - Simple approach for maximum compatibility
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if DATABASE_URL:
        # Keep it simple - just use postgresql://
        if DATABASE_URL.startswith('postgres://'):
            SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace('postgres://', 'postgresql://')
        else:
            SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///products.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis Configuration - Use Render's Redis service
    REDIS_URL = os.environ.get('REDIS_URL') or os.environ.get('REDISCLOUD_URL') or 'redis://red-ct3f31rv2p9s73e63rig:6379'
    
    # Celery Configuration
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    
    # Upload Configuration
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB max file size
    UPLOAD_FOLDER = 'uploads'
    
    # Application Configuration
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')