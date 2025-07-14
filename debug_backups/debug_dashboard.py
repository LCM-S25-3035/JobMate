#!/usr/bin/env python3
"""Debug script to test dashboard route and capture errors"""

import sys
import traceback
from app import create_app

def test_dashboard():
    try:
        print("🔍 Creating Flask app...")
        app = create_app()
        print("✅ Flask app created successfully")
        
        print("🔍 Testing dashboard route...")
        with app.test_client() as client:
            # Test dashboard route directly (without authentication for now)
            response = client.get('/recruiter/dashboard')
            print(f"📊 Dashboard response status: {response.status_code}")
            
            if response.status_code == 500:
                print("❌ Internal Server Error detected!")
                error_data = response.get_data(as_text=True)
                print("Error response data:")
                print("-" * 50)
                print(error_data)
                print("-" * 50)
            else:
                print("✅ Dashboard route working")
                
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        print("\n🔍 Full traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    test_dashboard() 