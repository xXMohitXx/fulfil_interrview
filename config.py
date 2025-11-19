import os
from dotenv import load_dotenv
from db_resolver import resolve_ipv4_database_url

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'dev-secret-key'
    
    # Supabase Configuration
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    
    # Database Configuration - Force IPv4 for Render + Supabase
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if DATABASE_URL:
        # Resolve to IPv4 to avoid Render IPv6 routing issues
        resolved_url = resolve_ipv4_database_url(DATABASE_URL)
        
        # Ensure proper connection parameters for Supabase compatibility
        if 'supabase.co' in resolved_url:
            # Add connection parameters for Supabase compatibility
            if '?' in resolved_url:
                SQLALCHEMY_DATABASE_URI = resolved_url + '&connect_timeout=10&application_name=render_app_ipv4'
            else:
                SQLALCHEMY_DATABASE_URI = resolved_url + '?sslmode=require&connect_timeout=10&application_name=render_app_ipv4'
        else:
            SQLALCHEMY_DATABASE_URI = resolved_url
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