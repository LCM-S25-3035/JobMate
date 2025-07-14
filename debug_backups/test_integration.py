"""
Integration test for the resume optimization route
"""

import requests
import json
from app import create_app
from app.models.user import User

def main():
    # Create the Flask app
    app = create_app()
    
    with app.app_context():
        # Get the first user from the database (for testing)
        user = User.query.first()
        if not user:
            print("No users found in database")
            return
        
        print(f"Using user: {user.email}")
        
        # Get a job from MongoDB
        mongo_db = app.mongo_db
        job = mongo_db.jobs.find_one()
        if not job:
            print("No jobs found in MongoDB")
            return
            
        job_id = str(job['_id'])
        print(f"Using job ID: {job_id}")
        
        # Start the test server
        app.testing = True
        client = app.test_client()
        
        # Login route
        with client.session_transaction() as sess:
            sess['_user_id'] = user.id
            sess['_fresh'] = True
        
        # First, check if a tailored resume exists and delete it for testing
        existing = mongo_db.tailored_resumes.find_one({"user_id": str(user.id), "job_id": job_id})
        if existing:
            print("Removing existing tailored resume for clean test...")
            mongo_db.tailored_resumes.delete_one({"user_id": str(user.id), "job_id": job_id})
        
        # Prepare test data
        data = {
            'job_id': job_id,
            'resume_text': "This is a test resume for the optimization endpoint.",
            'target_score': 90
        }
        
        # Get a CSRF token first (from any GET request)
        csrf_response = client.get('/dashboard')
        
        # Make the request
        print("\nSending API request...")
        response = client.post('/auto_optimize_resume', 
                             data=json.dumps(data), 
                             content_type='application/json',
                             headers={'X-Requested-With': 'XMLHttpRequest'})  # This bypasses CSRF for AJAX requests
        
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data.decode()[:200]}...")
        
        if response.status_code == 200:
            print("\nSUCCESS! The resume optimization endpoint is working.")
            
            # Verify MongoDB document creation
            doc = mongo_db.tailored_resumes.find_one({"user_id": str(user.id), "job_id": job_id})
            if doc and 'tailored_resume' in doc:
                print("\nMongoDB document was correctly created/updated.")
                print(f"ATS Score: {doc.get('ats_score')}")
                print(f"Resume length: {len(doc.get('tailored_resume', ''))}")
            else:
                print("\nMongoDB document was not created/updated correctly.")
        else:
            print("\nFAILED! The resume optimization endpoint returned an error.")
            
            # Check the logs
            try:
                with open('logs/app.log', 'r') as f:
                    logs = f.read()
                    print("\nLast 500 characters from log:")
                    print(logs[-500:])
            except Exception as e:
                print(f"Could not read logs: {e}")

if __name__ == '__main__':
    main()
