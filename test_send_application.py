#!/usr/bin/env python3
"""
Test script for the send_application function

This script tests the send_application functionality by:
1. Finding a job with an application email
2. Making a POST request to the send_application endpoint
3. Verifying the response

Usage:
python test_send_application.py
"""

import os
import sys
import json
import requests
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def find_job_with_email():
    """Find a job with an application email in MongoDB"""
    # Connect to MongoDB
    mongo_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
    mongo_db_name = os.environ.get('MONGODB_DB', 'job_automation')
    
    client = MongoClient(mongo_uri)
    db = client[mongo_db_name]
    
    # Find a job with an application email
    query = {"$or": [
        {"application_email": {"$exists": True, "$ne": ""}},
        {"email": {"$exists": True, "$ne": ""}},
        {"contact_email": {"$exists": True, "$ne": ""}}
    ]}
    
    job = db.jobs.find_one(query)
    
    if not job:
        logger.error("No job with an application email found")
        return None
        
    return job

def test_send_application(job_id):
    """Test the send_application endpoint"""
    # Login credentials
    login_data = {
        'email': 'applicant@example.com',
        'password': 'password123'
    }
    
    # Base URL
    base_url = 'http://localhost:5002'
    
    # Start a session
    session = requests.Session()
    
    # Login
    login_response = session.post(f'{base_url}/auth/login', data=login_data)
    
    if login_response.status_code != 200:
        logger.error(f"Login failed with status code {login_response.status_code}")
        return False
        
    logger.info("Login successful")
    
    # Extract CSRF token from cookies
    csrf_token = session.cookies.get('csrf_token')
    
    # Prepare application data
    application_data = {
        'resume_text': 'This is a test resume.',
        'cover_letter_text': 'This is a test cover letter.'
    }
    
    # Send application
    headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf_token
    }
    
    response = session.post(
        f'{base_url}/send-application/{job_id}',
        data=json.dumps(application_data),
        headers=headers
    )
    
    # Check response
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            logger.info(f"Application sent successfully: {result.get('message')}")
            return True
        else:
            logger.error(f"Application failed: {result.get('error')}")
            return False
    else:
        logger.error(f"Request failed with status code {response.status_code}")
        return False

def main():
    """Main function"""
    logger.info("Starting send_application test")
    
    # Find a job with an application email
    job = find_job_with_email()
    if not job:
        sys.exit(1)
        
    logger.info(f"Found job: {job['title']} (ID: {job['_id']})")
    
    # Test send_application endpoint
    success = test_send_application(str(job['_id']))
    
    if success:
        logger.info("Test completed successfully")
    else:
        logger.error("Test failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
