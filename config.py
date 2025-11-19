import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'dev-secret-key'
    
    # Supabase Configuration
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    
    # Database Configuration with multiple connection strategies
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if DATABASE_URL:
        # Strategy 1: Try psycopg2 first (most reliable for production)
        SQLALCHEMY_DATABASE_URI_PSYCOPG2 = DATABASE_URL
        if SQLALCHEMY_DATABASE_URI_PSYCOPG2.startswith('postgres://'):
            SQLALCHEMY_DATABASE_URI_PSYCOPG2 = SQLALCHEMY_DATABASE_URI_PSYCOPG2.replace('postgres://', 'postgresql://')
        
        # Strategy 2: pg8000 fallback with proper SSL
        SQLALCHEMY_DATABASE_URI_PG8000 = DATABASE_URL
        if SQLALCHEMY_DATABASE_URI_PG8000.startswith('postgres://'):
            SQLALCHEMY_DATABASE_URI_PG8000 = SQLALCHEMY_DATABASE_URI_PG8000.replace('postgres://', 'postgresql+pg8000://')
        elif SQLALCHEMY_DATABASE_URI_PG8000.startswith('postgresql://'):
            SQLALCHEMY_DATABASE_URI_PG8000 = SQLALCHEMY_DATABASE_URI_PG8000.replace('postgresql://', 'postgresql+pg8000://')
        
        # Add SSL for pg8000
        if 'ssl_context=' not in SQLALCHEMY_DATABASE_URI_PG8000:
            separator = '&' if '?' in SQLALCHEMY_DATABASE_URI_PG8000 else '?'
            SQLALCHEMY_DATABASE_URI_PG8000 += f'{separator}ssl_context=true'
        
        # Start with psycopg2, fallback to pg8000
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI_PSYCOPG2
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///products.db'
    
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 30,
        'connect_args': {
            'connect_timeout': 30,
            'application_name': 'fulfil_interview_app'
        }
    }
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