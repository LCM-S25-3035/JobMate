#!/usr/bin/env python3

print("=== JobMate Database Test ===")

try:
    print("1. Importing modules...")
    from app import create_app, db
    from app.models.user import User
    print("✅ Imports successful")
    
    print("2. Creating app context...")
    app = create_app()
    with app.app_context():
        print("✅ App context created")
        
        print("3. Testing database connection...")
        # Try a simple query
        user_count = User.query.count()
        print(f"✅ Database connected. Total users: {user_count}")
        
        print("4. Looking for applicant user...")
        applicant = User.query.filter_by(email='applicant@demo.com').first()
        if applicant:
            print(f"✅ Found applicant: {applicant.email}")
            print(f"   - ID: {applicant.id}")
            print(f"   - Name: {applicant.first_name} {applicant.last_name}")
            print(f"   - User type: {applicant.user_type}")
            print(f"   - Verified: {applicant.is_verified}")
            
            print("5. Testing password...")
            if applicant.check_password('password123'):
                print("✅ Password check successful!")
            else:
                print("❌ Password check failed!")
                
            print("6. Testing user methods...")
            print(f"   - Is applicant: {applicant.is_applicant()}")
            print(f"   - Is recruiter: {applicant.is_recruiter()}")
            
        else:
            print("❌ No applicant user found")
            
        print("7. Testing recruiter user...")
        recruiter = User.query.filter_by(email='recruiter@demo.com').first()
        if recruiter:
            print(f"✅ Found recruiter: {recruiter.email}")
            print(f"   - User type: {recruiter.user_type}")
        else:
            print("❌ No recruiter user found")
            
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n=== Test Complete ===")
