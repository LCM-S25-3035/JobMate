#!/usr/bin/env python3
"""
Debug script to test applicant login and identify the issue
"""
import requests
from bs4 import BeautifulSoup
import json

def test_applicant_login():
    """Test applicant login and see what's causing the error"""
    print("🔍 Debugging Applicant Login Issue")
    print("=" * 50)
    
    session = requests.Session()
    
    try:
        # Step 1: Get login page
        print("1. Getting login page...")
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
        print(f"✅ CSRF token obtained")
        
        # Step 2: Try applicant login
        print("\n2. Testing applicant login...")
        print("   Email: applicant@demo.com")
        print("   Password: password123")
        
        login_data = {
            'email': 'applicant@demo.com',
            'password': 'password123',
            'csrf_token': csrf_value
        }
        
        login_response = session.post(
            'http://localhost:5002/auth/login',
            data=login_data,
            allow_redirects=False
        )
        
        print(f"   Response Status: {login_response.status_code}")
        
        if login_response.status_code == 302:
            redirect_url = login_response.headers.get('Location', '')
            print(f"✅ Login successful! Redirecting to: {redirect_url}")
            
            # Step 3: Follow redirect to see what happens
            print("\n3. Following redirect...")
            dashboard_response = session.get('http://localhost:5002' + redirect_url)
            print(f"   Dashboard Status: {dashboard_response.status_code}")
            
            if dashboard_response.status_code == 500:
                print("❌ Internal Server Error on dashboard!")
                print("   Error content preview:")
                print(f"   {dashboard_response.text[:500]}")
                return False
            elif dashboard_response.status_code == 200:
                print("✅ Dashboard loaded successfully!")
                return True
            else:
                print(f"❌ Unexpected dashboard status: {dashboard_response.status_code}")
                return False
                
        elif login_response.status_code == 200:
            # Login form returned again, check for errors
            error_soup = BeautifulSoup(login_response.content, 'html.parser')
            error_messages = error_soup.find_all(class_='alert-danger')
            if error_messages:
                print("❌ Login failed with error:")
                for error in error_messages:
                    print(f"   {error.get_text().strip()}")
            else:
                print("❌ Login failed - no specific error message")
            return False
        else:
            print(f"❌ Unexpected login status: {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during test: {e}")
        return False

if __name__ == '__main__':
    success = test_applicant_login()
    if success:
        print("\n🎉 Applicant login test completed successfully!")
    else:
        print("\n❌ Applicant login test failed")
