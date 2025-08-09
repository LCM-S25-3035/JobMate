#!/usr/bin/env python3
"""
JobMate Database Seed Script
Creates test users and sample data for development and testing
"""

import os
import sys
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash
from flask import current_app

def create_test_users():
    """Create test users: applicant and recruiter"""
    
    print("🔄 Creating test users...")
    
    # Test Applicant User
    applicant_email = "applicant@demo.com"
    existing_applicant = User.query.filter_by(email=applicant_email).first()
    
    if not existing_applicant:
        test_applicant = User(
            email=applicant_email,
            password_hash=generate_password_hash("password123"),
            first_name="João",
            last_name="Silva",
            phone="+1 (416) 123-4567",
            user_type="applicant",
            city="Toronto",
            province="Ontario",
            country="Canada",
            is_active=True,
            is_verified=True,
            profile_completed=True,
            onboarding_completed=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(test_applicant)
        print(f"✅ Created test applicant: {applicant_email}")
    else:
        print(f"⚠️  Test applicant already exists: {applicant_email}")
    
    # Test Recruiter User
    recruiter_email = "recruiter@demo.com"
    existing_recruiter = User.query.filter_by(email=recruiter_email).first()
    
    if not existing_recruiter:
        test_recruiter = User(
            email=recruiter_email,
            password_hash=generate_password_hash("password123"),
            first_name="Maria",
            last_name="Santos",
            phone="+1 (416) 987-6543",
            user_type="recruiter",
            city="Toronto",
            province="Ontario",
            country="Canada",
            is_active=True,
            is_verified=True,
            profile_completed=True,
            onboarding_completed=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(test_recruiter)
        print(f"✅ Created test recruiter: {recruiter_email}")
    else:
        print(f"⚠️  Test recruiter already exists: {recruiter_email}")

def create_additional_sample_data():
    """Create additional sample data if needed"""
    
    print("🔄 Creating additional sample data...")
    
    # Create additional applicants for testing
    sample_applicants = [
        {
            "email": "john.developer@example.com",
            "first_name": "John",
            "last_name": "Developer",
            "phone": "+1 (647) 111-2222",
            "city": "Ottawa",
            "province": "Ontario"
        },
        {
            "email": "sarah.designer@example.com",
            "first_name": "Sarah",
            "last_name": "Designer",
            "phone": "+1 (647) 333-4444",
            "city": "Mississauga",
            "province": "Ontario"
        },
        {
            "email": "mike.analyst@example.com",
            "first_name": "Mike",
            "last_name": "Analyst",
            "phone": "+1 (647) 555-6666",
            "city": "Hamilton",
            "province": "Ontario"
        }
    ]
    
    for applicant_data in sample_applicants:
        existing_user = User.query.filter_by(email=applicant_data["email"]).first()
        if not existing_user:
            new_applicant = User(
                email=applicant_data["email"],
                password_hash=generate_password_hash("password123"),
                first_name=applicant_data["first_name"],
                last_name=applicant_data["last_name"],
                phone=applicant_data["phone"],
                user_type="applicant",
                city=applicant_data["city"],
                province=applicant_data["province"],
                country="Canada",
                is_active=True,
                is_verified=True,
                profile_completed=False,  # These are in progress
                onboarding_completed=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(new_applicant)
            print(f"✅ Created sample applicant: {applicant_data['email']}")
    
    # Create additional recruiters for testing
    sample_recruiters = [
        {
            "email": "hr.manager@techcorp.com",
            "first_name": "Emily",
            "last_name": "Manager",
            "phone": "+1 (416) 777-8888",
            "city": "Toronto",
            "province": "Ontario"
        },
        {
            "email": "talent.acquisition@startup.ca",
            "first_name": "David",
            "last_name": "Wilson",
            "phone": "+1 (647) 999-0000",
            "city": "Waterloo",
            "province": "Ontario"
        }
    ]
    
    for recruiter_data in sample_recruiters:
        existing_user = User.query.filter_by(email=recruiter_data["email"]).first()
        if not existing_user:
            new_recruiter = User(
                email=recruiter_data["email"],
                password_hash=generate_password_hash("password123"),
                first_name=recruiter_data["first_name"],
                last_name=recruiter_data["last_name"],
                phone=recruiter_data["phone"],
                user_type="recruiter",
                city=recruiter_data["city"],
                province=recruiter_data["province"],
                country="Canada",
                is_active=True,
                is_verified=True,
                profile_completed=True,
                onboarding_completed=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(new_recruiter)
            print(f"✅ Created sample recruiter: {recruiter_data['email']}")

def seed_database():
    """Main seed function"""
    
    print("🚀 Starting JobMate Database Seeding...")
    print("=" * 50)
    
    try:
        # Create test users (main ones from README)
        create_test_users()
        
        # Create additional sample data
        create_additional_sample_data()
        
        # Commit all changes
        db.session.commit()
        
        print("=" * 50)
        print("✅ Database seeding completed successfully!")
        print("\n📋 Test Credentials:")
        print("   Applicant: applicant@demo.com / password123")
        print("   Recruiter: recruiter@demo.com / password123")
        print("\n🔗 Access the application at: http://localhost:5002")
        
    except Exception as e:
        print(f"❌ Error during seeding: {str(e)}")
        db.session.rollback()
        return False
    
    return True

def reset_database():
    """Reset database by dropping all tables and recreating them"""
    
    print("⚠️  WARNING: This will delete ALL data in the database!")
    confirm = input("Are you sure you want to continue? (yes/no): ")
    
    if confirm.lower() not in ['yes', 'y']:
        print("❌ Operation cancelled.")
        return False
    
    print("🔄 Resetting database...")
    
    try:
        # Drop all tables
        db.drop_all()
        print("✅ Dropped all tables")
        
        # Create all tables
        db.create_all()
        print("✅ Created all tables")
        
        return True
        
    except Exception as e:
        print(f"❌ Error resetting database: {str(e)}")
        return False

def main():
    """Main function with command line argument handling"""
    
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        # Check command line arguments
        if len(sys.argv) > 1:
            command = sys.argv[1].lower()
            
            if command == "reset":
                if reset_database():
                    seed_database()
            elif command == "seed":
                seed_database()
            elif command == "help":
                print("JobMate Database Seed Script")
                print("Usage:")
                print("  python seed_database.py         - Seed database (default)")
                print("  python seed_database.py seed    - Seed database")
                print("  python seed_database.py reset   - Reset and seed database")
                print("  python seed_database.py help    - Show this help")
            else:
                print(f"❌ Unknown command: {command}")
                print("Use 'python seed_database.py help' for usage information")
        else:
            # Default: just seed
            seed_database()

if __name__ == "__main__":
    main()
