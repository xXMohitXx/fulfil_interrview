import os
from dotenv import load_dotenv
from urllib.parse import urlparse
from ipv6_workaround import apply_ipv6_workaround, get_alternative_database_url

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    
    # Supabase Configuration
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    
    # Apply IPv6 workaround for Render deployment
    apply_ipv6_workaround()
    
    # Database Configuration - Use alternative URL if available
    DATABASE_URL = get_alternative_database_url() or os.environ.get('DATABASE_URL')
    
    if DATABASE_URL:
        # Parse the original URL to extract components
        parsed = urlparse(DATABASE_URL)
        
        # Check if this is a Supabase connection that needs IPv4 forcing
        if 'supabase.co' in DATABASE_URL:
            print("🔄 Detected Supabase database - using IPv6 workaround connection")
            
            # Use the modified URL with additional parameters
            SQLALCHEMY_DATABASE_URI = DATABASE_URL
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
            'application_name': 'render_flask_app',
            # Force IPv4 connection to avoid Render IPv6 routing issues
            'host': 'db.bhyrldeuwxmtaebjpcmu.supabase.co',
            'options': '-c default_transaction_isolation=read_committed'
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