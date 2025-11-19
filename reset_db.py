#!/usr/bin/env python3
"""
Database reset and initialization script
This script will drop all tables and recreate them with the correct schema
"""
from app_simple import app
from models import db

def reset_database():
    with app.app_context():
        try:
            # Drop all tables
            print("Dropping all existing tables...")
            db.drop_all()
            print("Tables dropped successfully")
            
            # Create all tables with current schema
            print("Creating tables with updated schema...")
            db.create_all()
            print("Tables created successfully")
            
            print("Database reset completed!")
            
        except Exception as e:
            print(f"Error resetting database: {e}")
            return False
    
    return True

if __name__ == "__main__":
    reset_database()