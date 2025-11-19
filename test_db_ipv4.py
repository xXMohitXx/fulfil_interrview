#!/usr/bin/env python3
"""
Test database connection with forced IPv4 resolution for Render deployment
"""
import os
import sys
import time
import psycopg2
from urllib.parse import urlparse
from db_resolver import resolve_ipv4_database_url

def test_database_connection():
    """Test database connection with IPv4 resolution and retry logic"""
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    print(f"🔍 Testing database connection with IPv4 resolution...")
    print(f"📍 Original DATABASE_URL: {DATABASE_URL[:50]}...")
    
    # Resolve to IPv4
    ipv4_url = resolve_ipv4_database_url(DATABASE_URL)
    print(f"🌐 IPv4 resolved URL: {ipv4_url[:50]}...")
    
    # Parse the resolved URL
    try:
        parsed = urlparse(ipv4_url)
        print(f"🏠 Host: {parsed.hostname}")
        print(f"🔌 Port: {parsed.port}")
        print(f"🗄️ Database: {parsed.path[1:]}")
    except Exception as e:
        print(f"❌ Error parsing resolved URL: {e}")
        return False
    
    # Test connection with retries
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"🔄 Connection attempt {attempt + 1}/{max_retries}...")
            
            # Use IPv4 resolved URL for connection
            conn = psycopg2.connect(
                ipv4_url,
                connect_timeout=10,
                application_name='render_ipv4_test'
            )
            
            # Test query
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            cursor.close()
            conn.close()
            
            print(f"✅ Database connection successful with IPv4!")
            print(f"📊 PostgreSQL version: {version[0][:50]}...")
            return True
            
        except Exception as e:
            print(f"❌ Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"⏳ Waiting 2 seconds before retry...")
                time.sleep(2)
            else:
                print(f"💥 All IPv4 connection attempts failed!")
                return False
    
    return False

if __name__ == "__main__":
    print("🧪 IPv4 Database Connection Test")
    print("=" * 60)
    success = test_database_connection()
    sys.exit(0 if success else 1)