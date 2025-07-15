#!/usr/bin/env python3
"""
Script to test login with detailed error logging
"""

import requests
from bs4 import BeautifulSoup
import time

def test_login_and_check_logs():
    """Test login and monitor logs for errors"""
    
    print("🔐 Testing Login with Log Monitoring")
    print("=" * 50)
    
    session = requests.Session()
    
    try:
        # Step 1: Get login page
        print("1. Fetching login page...")
        login_page = session.get('http://localhost:5002/auth/login')
        
        if login_page.status_code != 200:
            print(f"❌ Login page failed: {login_page.status_code}")
            return False
        
        # Extract CSRF token
        soup = BeautifulSoup(login_page.content, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})
        
        if not csrf_token:
            print("❌ CSRF token not found")
            return False
        
        csrf_value = csrf_token.get('value')
        print(f"✅ CSRF token obtained: {csrf_value[:20]}...")
        
        # Step 2: Attempt login
        print("\n2. Attempting login with recruiter credentials...")
        print("   Email: recruiter@demo.com")
        print("   Password: password123")
        
        login_data = {
            'email': 'recruiter@demo.com',
            'password': 'password123',
            'csrf_token': csrf_value
        }
        
        print("\n3. Sending login request...")
        login_response = session.post(
            'http://localhost:5002/auth/login',
            data=login_data,
            allow_redirects=False
        )
        
        print(f"   Response Status: {login_response.status_code}")
        print(f"   Response Headers: {dict(login_response.headers)}")
        
        if login_response.status_code == 302:
            redirect_url = login_response.headers.get('Location', '')
            print(f"✅ Login successful! Redirecting to: {redirect_url}")
            
            # Test accessing recruiter dashboard
            print("\n4. Testing access to recruiter dashboard...")
            dashboard_response = session.get('http://localhost:5002' + redirect_url)
            print(f"   Dashboard Status: {dashboard_response.status_code}")
            
            if dashboard_response.status_code == 200:
                print("✅ Dashboard accessible!")
                
                # Test job listings
                print("\n5. Testing job listings...")
                jobs_response = session.get('http://localhost:5002/recruiter/jobs')
                print(f"   Jobs page status: {jobs_response.status_code}")
                
                if jobs_response.status_code == 200:
                    print("✅ Job listings accessible!")
                    
                    # Check if jobs are displayed
                    jobs_soup = BeautifulSoup(jobs_response.content, 'html.parser')
                    job_cards = jobs_soup.find_all(class_='job-card')
                    job_titles = jobs_soup.find_all('h5')
                    
                    print(f"   Found {len(job_titles)} job elements on page")
                    
                    return True
                else:
                    print(f"❌ Job listings not accessible: {jobs_response.status_code}")
                    return False
            else:
                print(f"❌ Dashboard not accessible: {dashboard_response.status_code}")
                return False
                
        elif login_response.status_code == 200:
            # Login failed, check for error messages
            print("❌ Login failed (stayed on login page)")
            soup = BeautifulSoup(login_response.content, 'html.parser')
            errors = soup.find_all(class_='alert-danger')
            if errors:
                for error in errors:
                    print(f"   Error: {error.get_text().strip()}")
            return False
        elif login_response.status_code == 500:
            print("❌ Server error during login")
            print(f"   Response content preview: {login_response.text[:200]}")
            return False
        else:
            print(f"❌ Unexpected status: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during test: {e}")
        return False

if __name__ == '__main__':
    success = test_login_and_check_logs()
    
    # Read and display app logs
    print("\n" + "=" * 50)
    print("📋 Server Logs:")
    try:
        with open('app.log', 'r') as f:
            log_lines = f.readlines()
            # Show last 20 lines
            for line in log_lines[-20:]:
                print(f"   {line.strip()}")
    except FileNotFoundError:
        print("   No app.log file found")
    except Exception as e:
        print(f"   Error reading logs: {e}")
    
    if success:
        print("\n🎉 Login test completed successfully!")
    else:
        print("\n❌ Login test failed - check logs above") 