#!/usr/bin/env python3
"""
Quick database user creation for testing
"""
import os
import sys
sys.path.append('.')

from app import create_app, db
from app.models.user import User

def create_test_users():
    """Create test users for JobMate"""
    app = create_app()
    
    with app.app_context():
        try:
            print("Creating test users...")
            
            # Create applicant user
            applicant = User.query.filter_by(email='applicant@demo.com').first()
            if not applicant:
                applicant = User.create_user(
                    email='applicant@demo.com',
                    password='password123',
                    first_name='Test',
                    last_name='Applicant',
                    user_type='applicant'
                )
                applicant.is_verified = True
                db.session.commit()
                print("✓ Applicant user created: applicant@demo.com / password123")
            else:
                print("✓ Applicant user already exists")
            
            # Create recruiter user
            recruiter = User.query.filter_by(email='recruiter@demo.com').first()
            if not recruiter:
                recruiter = User.create_user(
                    email='recruiter@demo.com',
                    password='password123',
                    first_name='Test',
                    last_name='Recruiter',
                    user_type='recruiter'
                )
                recruiter.is_verified = True
                db.session.commit()
                print("✓ Recruiter user created: recruiter@demo.com / password123")
            else:
                print("✓ Recruiter user already exists")
                
            print("✓ All test users are ready!")
            return True
            
        except Exception as e:
            print(f"✗ Error creating users: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    create_test_users()
