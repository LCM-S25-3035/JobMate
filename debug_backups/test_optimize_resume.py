import requests
import json
import sys
from flask import Flask, session
from app import create_app
from app.models.user import User

def run_test():
    """Test the auto_optimize_resume endpoint with a controlled input"""
    
    # Create a test app context
    app = create_app()
    
    with app.app_context():
        # Set up a test client
        client = app.test_client()
        
        # Get a test user
        user = User.query.first()
        if not user:
            print("No users found in database. Please create a test user first.")
            return
        
        print(f"Testing with user: {user.username}")
        
        # Get a job ID from the database
        mongo_db = app.mongo_db
        job = mongo_db.jobs.find_one()
        if not job:
            print("No jobs found in database. Please create a test job first.")
            return
        
        job_id = str(job['_id'])
        print(f"Using job ID: {job_id}")
        
        # Test data
        data = {
            'job_id': job_id,
            'resume_text': """# PROFESSIONAL RESUME

TECHNICAL SKILLS
* Programming: Python, JavaScript, HTML/CSS, SQL
* Tools: Git, Docker, AWS, Kubernetes
* Frameworks: React, Django, Flask, Node.js
* Methodologies: Agile, Scrum, Test-Driven Development

WORK EXPERIENCE

Software Engineer | XYZ Tech | Jan 2020 - Present
* Developed scalable microservices using Python and Flask
* Implemented CI/CD pipelines using GitHub Actions
* Optimized database queries, resulting in faster response times
* Created responsive web interfaces using React.js and modern JavaScript

Junior Developer | ABC Solutions | Jun 2018 - Dec 2019
* Built RESTful APIs using Node.js and Express
* Designed and maintained MongoDB schemas
* Fixed critical bugs in production code
* Integrated third-party payment services

EDUCATION

Bachelor of Science, Computer Science | State University | 2014-2018
* GPA: 3.8/4.0
* Relevant coursework: Data Structures, Algorithms, Database Systems
* Senior Project: Developed an AI-powered recommendation system for e-commerce

CERTIFICATIONS

* AWS Certified Solutions Architect
* Google Cloud Professional Developer
* MongoDB Certified Developer
""",
            'target_score': 90
        }
        
        # We need to login first through the login form
        with client as c:
            # First, get the login page to get CSRF token
            response = c.get('/login')
            
            # Manually login
            login_data = {
                'username': user.username,
                'password': 'password123',  # Use a known test password
                'remember_me': False
            }
            
            print("Logging in...")
            login_response = c.post('/login', data=login_data, follow_redirects=True)
            
            if 'Dashboard' in login_response.data.decode():
                print("Login successful!")
            else:
                print("Login failed. Using test mode instead.")
                
                # Use a testing backdoor to simulate authentication if available
                # This is just for testing purposes
                with client.session_transaction() as sess:
                    sess['_user_id'] = user.id
                    sess['_fresh'] = True
            
            # Now try the optimization request
            print("Sending optimization request...")
            response = c.post('/auto_optimize_resume', 
                              data=json.dumps(data),
                              content_type='application/json')
            
            print(f"Status code: {response.status_code}")
            
            # Print response summary - truncate if large
            response_data = response.data.decode()
            if len(response_data) > 500:
                print(f"Response (truncated): {response_data[:500]}...")
            else:
                print(f"Response: {response_data}")

if __name__ == '__main__':
    run_test()
