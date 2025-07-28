#!/usr/bin/env python3

from app import create_app, db
from app.models.user import User
from flask_login import login_user
from flask import request, session

app = create_app()

with app.app_context():
    # Test if we can load the applicant user
    print("Testing user loading...")
    applicant = User.query.filter_by(email='applicant@demo.com').first()
    if applicant:
        print(f"✅ Found applicant: {applicant.email}, user_type: {applicant.user_type}")
        print(f"User ID: {applicant.id}")
        print(f"Is verified: {applicant.is_verified}")
        
        # Test user methods
        try:
            print(f"Is applicant: {applicant.is_applicant()}")
            print(f"Is recruiter: {applicant.is_recruiter()}")
        except Exception as e:
            print(f"❌ Error with user type methods: {e}")
        
        # Test resume loading
        try:
            active_resume = applicant.get_active_resume()
            print(f"Active resume: {active_resume}")
        except Exception as e:
            print(f"❌ Error getting active resume: {e}")
        
        # Test applications
        try:
            applications = applicant.applications.limit(5).all()
            print(f"Applications count: {len(applications)}")
        except Exception as e:
            print(f"❌ Error getting applications: {e}")
        
        # Test job preferences
        try:
            if applicant.is_applicant():
                job_prefs = applicant.job_preferences.first()
                print(f"Job preferences: {job_prefs}")
            else:
                print("Not an applicant, skipping job preferences")
        except Exception as e:
            print(f"❌ Error getting job preferences: {e}")
            
    else:
        print("❌ No applicant user found")
        
    # Test calculating profile completion
    try:
        from app.main.routes import calculate_profile_completion
        completion = calculate_profile_completion(applicant)
        print(f"✅ Profile completion: {completion}%")
    except Exception as e:
        print(f"❌ Error calculating profile completion: {e}")
        import traceback
        traceback.print_exc()
