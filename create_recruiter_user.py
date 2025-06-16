#!/usr/bin/env python3

from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    # Check if recruiter user exists
    recruiter = User.query.filter_by(email='recruiter@demo.com').first()
    if recruiter:
        print(f'Recruiter user exists: {recruiter.email} - {recruiter.user_type}')
    else:
        print('Creating recruiter user...')
        recruiter = User.create_user(
            email='recruiter@demo.com',
            password='password123',
            first_name='Test',
            last_name='Recruiter',
            user_type='recruiter'
        )
        recruiter.is_verified = True
        db.session.commit()
        print(f'Recruiter user created: {recruiter.email} - {recruiter.user_type}')
    
    # Also create an applicant user if it doesn't exist
    applicant = User.query.filter_by(email='applicant@demo.com').first()
    if applicant:
        print(f'Applicant user exists: {applicant.email} - {applicant.user_type}')
    else:
        print('Creating applicant user...')
        applicant = User.create_user(
            email='applicant@demo.com',
            password='password123',
            first_name='Test',
            last_name='Applicant',
            user_type='applicant'
        )
        applicant.is_verified = True
        db.session.commit()
        print(f'Applicant user created: {applicant.email} - {applicant.user_type}') 