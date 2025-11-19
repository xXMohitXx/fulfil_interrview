#!/usr/bin/env python3
"""
Database setup script for Supabase PostgreSQL
This script creates all necessary tables in Supabase
"""

import os
import sys
from dotenv import load_dotenv

# Try different connection approaches
try:
    import psycopg
    print("Using psycopg3...")
except ImportError:
    try:
        import psycopg2
        print("Using psycopg2...")
    except ImportError:
        print("No PostgreSQL driver found! Please install psycopg or psycopg2")
        sys.exit(1)

load_dotenv()

def setup_database():
    """Create all necessary tables in Supabase using direct connection"""
    
    # Get database URL
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set!")
        print("Please set your Supabase database URL in the .env file")
        return False
    
    # Parse the URL
    import urllib.parse as urlparse
    parsed = urlparse.urlparse(database_url)
    
    print(f"Connecting to database: {parsed.hostname}...")
    
    try:
        # Try psycopg3 first
        try:
            import psycopg
            conn = psycopg.connect(
                host=parsed.hostname,
                port=parsed.port,
                dbname=parsed.path[1:],  # psycopg3 uses dbname, not database
                user=parsed.username,
                password=parsed.password,
                sslmode='require'
            )
            print("✅ Connected with psycopg3")
        except ImportError:
            import psycopg2
            conn = psycopg2.connect(
                host=parsed.hostname,
                port=parsed.port,
                database=parsed.path[1:],
                user=parsed.username,
                password=parsed.password,
                sslmode='require'
            )
            print("✅ Connected with psycopg2")
        
        cursor = conn.cursor()
        
        # Test connection
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        print(f"✅ PostgreSQL: {version[0][:50]}...")
        
        # Create products table
        print("Creating products table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                sku VARCHAR(100) UNIQUE NOT NULL,
                description TEXT,
                price DECIMAL(10,2) DEFAULT 0.00,
                quantity INTEGER DEFAULT 0,
                category VARCHAR(100),
                active BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create webhooks table
        print("Creating webhooks table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS webhooks (
                id SERIAL PRIMARY KEY,
                url VARCHAR(500) NOT NULL,
                event_type VARCHAR(100) NOT NULL,
                active BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_triggered TIMESTAMP
            )
        """)
        
        # Create upload_logs table
        print("Creating upload_logs table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS upload_logs (
                id SERIAL PRIMARY KEY,
                task_id VARCHAR(100),
                filename VARCHAR(255) NOT NULL,
                total_rows INTEGER DEFAULT 0,
                processed_rows INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                error_count INTEGER DEFAULT 0,
                status VARCHAR(50) DEFAULT 'pending',
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)
        
        # Create indexes for better performance
        print("Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_active ON products(active)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_upload_logs_status ON upload_logs(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_webhooks_active ON webhooks(active)")
        
        # Commit all changes
        conn.commit()
        
        print("✅ Database schema created successfully!")
        
        # Verify tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema='public' 
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        print(f"✅ Created tables: {[t[0] for t in tables]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

if __name__ == "__main__":
    success = setup_database()
    if success:
        print("\n🎉 Supabase database is ready!")
        print("Your Flask app should now connect successfully.")
    else:
        print("\n💥 Database setup failed!")
        print("Please check your DATABASE_URL and try again.")
        sys.exit(1)