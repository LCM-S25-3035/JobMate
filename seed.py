#!/usr/bin/env python3
"""
JobMate Universal Database Seed Script
Creates test users and sample data for development and testing
Automatically detects Docker environment or manual setup
"""

import os
import sys
import time
import subprocess
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def is_docker_environment():
    """Check if we're running in a Docker environment"""
    return (
        os.path.exists('/.dockerenv') or 
        os.environ.get('DOCKER_ENV') == 'true' or
        'docker' in os.environ.get('container', '')
    )

def is_docker_available():
    """Check if Docker is available and running"""
    try:
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def detect_environment():
    """Detect the current environment and return appropriate configuration"""
    if is_docker_environment():
        return 'docker_container'
    elif is_docker_available():
        # Check if JobMate containers are running
        try:
            result = subprocess.run(['docker', 'ps', '--filter', 'name=jobmate'], 
                                 capture_output=True, text=True, timeout=10)
            if 'jobmate' in result.stdout:
                return 'docker_host'
        except subprocess.TimeoutExpired:
            pass
    
    return 'manual'

def wait_for_docker_services():
    """Wait for Docker services to be ready"""
    print("🔄 Waiting for Docker services to be ready...")
    
    max_retries = 30
    for i in range(max_retries):
        try:
            # Check PostgreSQL
            pg_result = subprocess.run([
                'docker', 'exec', 'jobmate_postgres', 
                'pg_isready', '-U', 'jobmate_user', '-d', 'jobmate_db'
            ], capture_output=True, timeout=5)
            
            # Check MongoDB
            mongo_result = subprocess.run([
                'docker', 'exec', 'jobmate_mongodb',
                'mongosh', '--eval', 'db.runCommand("ping")', '--quiet'
            ], capture_output=True, timeout=5)
            
            if pg_result.returncode == 0 and mongo_result.returncode == 0:
                print("✅ All Docker services are ready!")
                return True
                
        except subprocess.TimeoutExpired:
            pass
        
        print(f"⏳ Waiting for services... ({i+1}/{max_retries})")
        time.sleep(2)
    
    print("❌ Timeout waiting for Docker services")
    return False

def run_seed_in_docker():
    """Run the seed script inside Docker container"""
    print("🔄 Running seed script in Docker container...")
    
    if not wait_for_docker_services():
        return False
    
    try:
        result = subprocess.run([
            'docker', 'exec', 'jobmate_web',
            'python', 'seed_database.py'
        ], timeout=60)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("❌ Timeout running seed script in Docker")
        return False

def run_seed_manual():
    """Run the seed script in manual environment"""
    print("🔄 Running seed script in manual environment...")
    
    try:
        from app import create_app, db
        from app.models.user import User
        from werkzeug.security import generate_password_hash
        
        # Create Flask app
        app = create_app()
        
        with app.app_context():
            return create_test_users_and_data()
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you've activated the virtual environment and installed dependencies")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def create_test_users_and_data():
    """Create test users and sample data"""
    from app import db
    from app.models.user import User
    from werkzeug.security import generate_password_hash
    
    print("🔄 Creating test users...")
    
    # Test users data
    test_users = [
        {
            "email": "applicant@demo.com",
            "password": "password123",
            "first_name": "João",
            "last_name": "Silva",
            "phone": "+1 (416) 123-4567",
            "user_type": "applicant",
            "city": "Toronto",
            "province": "Ontario",
            "is_main_test": True
        },
        {
            "email": "recruiter@demo.com",
            "password": "password123",
            "first_name": "Maria",
            "last_name": "Santos",
            "phone": "+1 (416) 987-6543",
            "user_type": "recruiter",
            "city": "Toronto",
            "province": "Ontario",
            "is_main_test": True
        },
        {
            "email": "john.developer@example.com",
            "password": "password123",
            "first_name": "John",
            "last_name": "Developer",
            "phone": "+1 (647) 111-2222",
            "user_type": "applicant",
            "city": "Ottawa",
            "province": "Ontario",
            "is_main_test": False
        },
        {
            "email": "sarah.designer@example.com",
            "password": "password123",
            "first_name": "Sarah",
            "last_name": "Designer",
            "phone": "+1 (647) 333-4444",
            "user_type": "applicant",
            "city": "Mississauga",
            "province": "Ontario",
            "is_main_test": False
        },
        {
            "email": "mike.analyst@example.com",
            "password": "password123",
            "first_name": "Mike",
            "last_name": "Analyst",
            "phone": "+1 (647) 555-6666",
            "user_type": "applicant",
            "city": "Hamilton",
            "province": "Ontario",
            "is_main_test": False
        },
        {
            "email": "hr.manager@techcorp.com",
            "password": "password123",
            "first_name": "Emily",
            "last_name": "Manager",
            "phone": "+1 (416) 777-8888",
            "user_type": "recruiter",
            "city": "Toronto",
            "province": "Ontario",
            "is_main_test": False
        },
        {
            "email": "talent.acquisition@startup.ca",
            "password": "password123",
            "first_name": "David",
            "last_name": "Wilson",
            "phone": "+1 (647) 999-0000",
            "user_type": "recruiter",
            "city": "Waterloo",
            "province": "Ontario",
            "is_main_test": False
        }
    ]
    
    try:
        created_count = 0
        
        for user_data in test_users:
            existing_user = User.query.filter_by(email=user_data["email"]).first()
            
            if not existing_user:
                new_user = User(
                    email=user_data["email"],
                    password_hash=generate_password_hash(user_data["password"]),
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    phone=user_data["phone"],
                    user_type=user_data["user_type"],
                    city=user_data["city"],
                    province=user_data["province"],
                    country="Canada",
                    is_active=True,
                    is_verified=True,
                    profile_completed=user_data["is_main_test"],  # Main test users have complete profiles
                    onboarding_completed=user_data["is_main_test"],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.session.add(new_user)
                created_count += 1
                status = "✅" if user_data["is_main_test"] else "📝"
                print(f"{status} Created {user_data['user_type']}: {user_data['email']}")
            else:
                status = "⚠️" if user_data["is_main_test"] else "💡"
                print(f"{status} {user_data['user_type'].title()} already exists: {user_data['email']}")
        
        # Commit all changes
        db.session.commit()
        
        print("=" * 50)
        print(f"✅ Database seeding completed! Created {created_count} new users.")
        print("\n📋 Main Test Credentials:")
        print("   Applicant: applicant@demo.com / password123")
        print("   Recruiter: recruiter@demo.com / password123")
        print("\n🔗 Access the application at: http://localhost:5002")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during seeding: {str(e)}")
        db.session.rollback()
        return False

def reset_database():
    """Reset database by dropping all tables and recreating them"""
    env = detect_environment()
    
    print("⚠️  WARNING: This will delete ALL data in the database!")
    confirm = input("Are you sure you want to continue? (yes/no): ")
    
    if confirm.lower() not in ['yes', 'y']:
        print("❌ Operation cancelled.")
        return False
    
    if env == 'docker_host':
        print("🔄 Resetting database in Docker...")
        try:
            # Reset PostgreSQL
            subprocess.run([
                'docker', 'exec', 'jobmate_postgres',
                'psql', '-U', 'jobmate_user', '-d', 'jobmate_db',
                '-c', 'DROP SCHEMA public CASCADE; CREATE SCHEMA public;'
            ], check=True, timeout=30)
            
            # Reset MongoDB
            subprocess.run([
                'docker', 'exec', 'jobmate_mongodb',
                'mongosh', 'jobmate_dev', '--eval', 'db.dropDatabase()'
            ], check=True, timeout=30)
            
            print("✅ Database reset completed in Docker")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error resetting database in Docker: {e}")
            return False
    else:
        # Manual environment
        try:
            from app import create_app, db
            app = create_app()
            
            with app.app_context():
                db.drop_all()
                db.create_all()
                print("✅ Database reset completed")
                return True
                
        except Exception as e:
            print(f"❌ Error resetting database: {str(e)}")
            return False

def main():
    """Main function with command line argument handling"""
    
    # Detect environment
    env = detect_environment()
    print(f"🔍 Detected environment: {env}")
    
    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "reset":
            if reset_database():
                print("🔄 Proceeding with seeding...")
                # Continue to seeding
            else:
                return
        elif command == "seed":
            pass  # Continue to seeding
        elif command == "help":
            print("JobMate Universal Database Seed Script")
            print("Automatically detects Docker environment or manual setup")
            print("")
            print("Usage:")
            print("  python seed.py         - Seed database (default)")
            print("  python seed.py seed    - Seed database")
            print("  python seed.py reset   - Reset and seed database")
            print("  python seed.py help    - Show this help")
            print("")
            print(f"Current environment: {env}")
            return
        else:
            print(f"❌ Unknown command: {command}")
            print("Use 'python seed.py help' for usage information")
            return
    
    # Execute seeding based on environment
    print("🚀 Starting JobMate Database Seeding...")
    print("=" * 50)
    
    success = False
    
    if env == 'docker_host':
        success = run_seed_in_docker()
    elif env == 'docker_container':
        success = run_seed_manual()  # We're inside container, run normally
    else:
        success = run_seed_manual()
    
    if success:
        print("🎉 Seeding completed successfully!")
    else:
        print("❌ Seeding failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
