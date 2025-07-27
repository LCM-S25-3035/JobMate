#!/usr/bin/env python3

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text

def check_and_create_tables():
    """Check if tables exist and create them if needed"""
    
    app = create_app()
    
    with app.app_context():
        try:
            print("🔄 Checking database tables...")
            
            with db.engine.connect() as conn:
                # Check what tables exist
                tables_query = text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                """)
                result = conn.execute(tables_query)
                existing_tables = [row[0] for row in result.fetchall()]
                
                print(f"📋 Existing tables: {existing_tables}")
                
                # Check for user table variations
                user_table_name = None
                possible_names = ['user', 'users', 'User', 'Users']
                
                for name in possible_names:
                    if name in existing_tables:
                        user_table_name = name
                        break
                
                if not user_table_name:
                    print("⚠️  No user table found. Creating tables...")
                    # Create all tables using SQLAlchemy
                    db.create_all()
                    print("✅ Tables created successfully!")
                    
                    # Check again
                    result = conn.execute(tables_query)
                    new_tables = [row[0] for row in result.fetchall()]
                    print(f"📋 New tables: {new_tables}")
                    
                    # Find user table again
                    for name in possible_names:
                        if name in new_tables:
                            user_table_name = name
                            break
                
                return user_table_name
                
        except Exception as e:
            print(f"❌ Error checking tables: {str(e)}")
            return None

def add_profile_columns():
    """Add missing profile columns to user table for PostgreSQL"""
    
    app = create_app()
    
    with app.app_context():
        try:
            print("🔄 Connecting to PostgreSQL database...")
            
            # First, check and create tables if needed
            user_table_name = check_and_create_tables()
            
            if not user_table_name:
                print("❌ Could not find or create user table!")
                return False
                
            print(f"✅ Found user table: {user_table_name}")
            
            columns_to_add = [
                ("bio", "TEXT"),
                ("skills", "VARCHAR(500)"),
                ("experience_level", "VARCHAR(50)")
            ]
            
            with db.engine.connect() as conn:
                # Check existing columns
                existing_columns_query = text(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = '{user_table_name}'
                """)
                result = conn.execute(existing_columns_query)
                existing_columns = [row[0] for row in result.fetchall()]
                
                print(f"📋 Existing columns in {user_table_name}: {existing_columns}")
                
                for column_name, column_type in columns_to_add:
                    try:
                        if column_name not in existing_columns:
                            # Add the column using PostgreSQL syntax with proper quoting
                            add_column_query = text(f'ALTER TABLE "{user_table_name}" ADD COLUMN {column_name} {column_type};')
                            conn.execute(add_column_query)
                            conn.commit()
                            print(f"✅ Added column: {column_name}")
                        else:
                            print(f"ℹ️  Column {column_name} already exists")
                            
                    except Exception as e:
                        print(f"❌ Error adding {column_name}: {str(e)}")
                        conn.rollback()
            
            print("✅ Database updated successfully!")
            
            # Verify columns were added
            print("\n🔍 Verifying columns...")
            with db.engine.connect() as conn:
                verify_query = text(f"""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = '{user_table_name}'
                    ORDER BY ordinal_position
                """)
                result = conn.execute(verify_query)
                user_columns = result.fetchall()
            
            print(f"📋 Current {user_table_name} table columns:")
            for i, (column_name, data_type) in enumerate(user_columns, 1):
                print(f"   {i}. {column_name} ({data_type})")
            
            # Check if our new columns are present
            column_names = [col[0] for col in user_columns]
            missing_columns = []
            
            for column_name, _ in columns_to_add:
                if column_name in column_names:
                    print(f"✅ {column_name} column verified")
                else:
                    print(f"❌ {column_name} column missing")
                    missing_columns.append(column_name)
            
            if not missing_columns:
                print("\n🎉 All required columns are present!")
                return True
            else:
                print(f"\n⚠️  Missing columns: {missing_columns}")
                return False
                    
        except Exception as e:
            print(f"❌ Database error: {str(e)}")
            print("💡 Make sure your PostgreSQL server is running and accessible")
            
            # Additional debugging information
            print("\n🔍 Debug information:")
            try:
                print(f"   App config: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not found')}")
                print(f"   Database type: PostgreSQL")
                
                # Test basic connection
                with db.engine.connect() as conn:
                    result = conn.execute(text("SELECT version();"))
                    version = result.fetchone()
                    print(f"   PostgreSQL version: {version[0] if version else 'Unknown'}")
                    
            except Exception as debug_e:
                print(f"   Could not get debug info: {debug_e}")
            
            return False

def check_user_model():
    """Check if User model has the required fields"""
    
    app = create_app()
    
    with app.app_context():
        try:
            from app.models.user import User
            
            print("\n🔍 Checking User model attributes...")
            
            required_fields = ['bio', 'skills', 'experience_level']
            
            for field in required_fields:
                if hasattr(User, field):
                    print(f"✅ User.{field} exists in model")
                else:
                    print(f"❌ User.{field} missing from model")
                    
            # Also check the table name from SQLAlchemy
            print(f"📋 SQLAlchemy table name: {User.__tablename__}")
                    
        except Exception as e:
            print(f"❌ Error checking User model: {str(e)}")

def test_profile_completion():
    """Test the profile completion function"""
    
    app = create_app()
    
    with app.app_context():
        try:
            from app.models.user import User
            from app.main.routes import calculate_profile_completion
            
            print("\n🧪 Testing profile completion function...")
            
            # Get a test user
            user = User.query.first()
            if user:
                print(f"📝 Testing with user: {user.email}")
                completion_data = calculate_profile_completion(user)
                print(f"📊 Completion percentage: {completion_data['percentage']}%")
                print(f"📊 Completed fields: {completion_data['completed']}/{completion_data['total']}")
                
                print("\n📋 Field details:")
                for item in completion_data['items']:
                    status = "✅" if item['completed'] else "❌"
                    print(f"   {status} {item['name']}: '{item['value']}'")
            else:
                print("⚠️  No users found in database")
                
        except Exception as e:
            print(f"❌ Error testing profile completion: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting PostgreSQL database update...")
    print("=" * 60)
    
    # First check the User model
    check_user_model()
    
    print("\n" + "=" * 60)
    
    # Then update the database
    success = add_profile_columns()
    
    if success:
        print("\n" + "=" * 60)
        # Test the profile completion function
        test_profile_completion()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Database update completed successfully!")
        print("\n📝 Next steps:")
        print("   1. Restart your Flask application")
        print("   2. Go to /profile and fill out your details")
        print("   3. Save your profile")
        print("   4. Check /debug/profile-completion to verify")
        print("   5. Your completion percentage should now be higher!")
    else:
        print("❌ Database update failed!")
        print("\n🛠️  Troubleshooting:")
        print("   1. Make sure PostgreSQL server is running")
        print("   2. Check database connection settings")
        print("   3. Verify database credentials")
        print("   4. Make sure your Flask app is not running")
        print("   5. Try running the script again")
    
    print("\n" + "=" * 60)
