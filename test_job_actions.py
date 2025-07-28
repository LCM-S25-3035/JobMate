#!/usr/bin/env python3
"""
Test script to verify job action endpoints are working
Run this after starting the Flask application
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:5000"
RECRUITER_LOGIN_URL = f"{BASE_URL}/auth/login"

def test_job_actions():
    """Test the job action endpoints"""
    
    print("=== JobMate Job Actions Test ===")
    print("Note: This script requires:")
    print("1. Flask app running on localhost:5000")
    print("2. A logged-in recruiter session")
    print("3. Existing job postings to test with")
    print()
    
    # Test endpoints (these will return 401/403 without proper authentication)
    test_job_id = 1  # Replace with actual job ID
    
    endpoints = [
        {
            'name': 'Toggle Job Status (Pause)',
            'url': f"{BASE_URL}/recruiter/jobs/{test_job_id}/status",
            'method': 'POST',
            'data': {'status': 'paused'}
        },
        {
            'name': 'Toggle Job Status (Activate)',
            'url': f"{BASE_URL}/recruiter/jobs/{test_job_id}/status", 
            'method': 'POST',
            'data': {'status': 'active'}
        },
        {
            'name': 'Repost Job',
            'url': f"{BASE_URL}/recruiter/jobs/{test_job_id}/repost",
            'method': 'POST',
            'data': {}
        },
        {
            'name': 'Archive Job',
            'url': f"{BASE_URL}/recruiter/jobs/{test_job_id}/archive",
            'method': 'POST', 
            'data': {}
        }
    ]
    
    print("Testing endpoint availability...")
    
    for endpoint in endpoints:
        try:
            if endpoint['method'] == 'POST':
                response = requests.post(
                    endpoint['url'], 
                    json=endpoint['data'],
                    headers={'Content-Type': 'application/json'}
                )
            
            print(f"✓ {endpoint['name']}: {endpoint['url']}")
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 401:
                print("  Note: Authentication required (expected)")
            elif response.status_code == 404:
                print("  Note: Endpoint not found - check route implementation")
            elif response.status_code == 403:
                print("  Note: Access denied (expected without recruiter login)")
                
        except requests.exceptions.ConnectionError:
            print(f"✗ {endpoint['name']}: Connection failed")
            print("  Make sure Flask app is running on localhost:5000")
        except Exception as e:
            print(f"✗ {endpoint['name']}: Error - {e}")
        
        print()
    
    print("=== Manual Testing Instructions ===")
    print("1. Start the Flask application: python run.py")
    print("2. Login as a recruiter user")
    print("3. Navigate to job listings page")
    print("4. Try the Pause, Repost, and Archive buttons")
    print("5. Check that the job status changes accordingly")

if __name__ == "__main__":
    test_job_actions()
