import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'dev-secret-key'
    
    # Supabase Configuration
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    
    # Database Configuration - Optimized for Render + Supabase
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if DATABASE_URL:
        # Ensure proper connection parameters for Render + Supabase
        if 'supabase.co' in DATABASE_URL:
            # Add connection parameters for Supabase compatibility
            if '?' in DATABASE_URL:
                SQLALCHEMY_DATABASE_URI = DATABASE_URL + '&connect_timeout=10&application_name=render_app'
            else:
                SQLALCHEMY_DATABASE_URI = DATABASE_URL + '?sslmode=require&connect_timeout=10&application_name=render_app'
        else:
            SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///products.db'
    
    # SQLAlchemy configuration for better connection handling
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 5,
        'pool_timeout': 20,
        'pool_recycle': 300,
        'pool_pre_ping': True,
        'connect_args': {
            'connect_timeout': 10,
            'application_name': 'render_flask_app'
        }
    }
    
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