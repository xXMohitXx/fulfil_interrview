#!/usr/bin/env python3
"""
Database connection test and setup utility
"""
import os
import sys
import time
import psycopg2
from urllib.parse import urlparse

def test_database_connection():
    """Test database connection with retry logic"""
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    print(f"🔍 Testing database connection...")
    print(f"📍 Database URL: {DATABASE_URL[:50]}...")
    
    # Parse the URL
    try:
        parsed = urlparse(DATABASE_URL)
        print(f"🏠 Host: {parsed.hostname}")
        print(f"🔌 Port: {parsed.port}")
        print(f"🗄️ Database: {parsed.path[1:]}")
    except Exception as e:
        print(f"❌ Error parsing DATABASE_URL: {e}")
        return False
    
    # Test connection with retries
    max_retries = 5
    for attempt in range(max_retries):
        try:
            print(f"🔄 Connection attempt {attempt + 1}/{max_retries}...")
            
            # Use direct psycopg2 connection
            conn = psycopg2.connect(
                DATABASE_URL,
                connect_timeout=10,
                application_name='render_connection_test'
            )
            
            # Test query
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            cursor.close()
            conn.close()
            
            print(f"✅ Database connection successful!")
            print(f"📊 PostgreSQL version: {version[0][:50]}...")
            return True
            
        except Exception as e:
            print(f"❌ Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"⏳ Waiting 3 seconds before retry...")
                time.sleep(3)
            else:
                print(f"💥 All connection attempts failed!")
                return False
    
    return False

if __name__ == "__main__":
    success = test_database_connection()
    sys.exit(0 if success else 1)