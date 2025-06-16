#!/usr/bin/env python3
"""
Database Initialization Script for JobMate
Creates all tables and initializes the database
"""

from app import create_app, db
from app.models.user import User
from app.models.job_posting import JobPosting

def init_database():
    """Initialize the database with all tables"""
    app = create_app()
    
    with app.app_context():
        try:
            # Create all tables
            print("Creating database tables...")
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Verify tables exist
            tables = db.inspect(db.engine).get_table_names()
            print(f"📊 Created tables: {', '.join(tables)}")
            
            # Test User creation
            print("\n🧪 Testing User model...")
            test_user = User.query.first()
            if not test_user:
                print("No users found - ready for registration!")
            else:
                print(f"Found existing user: {test_user.email}")
                
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            return False
    
    return True

if __name__ == '__main__':
    init_database() 