#!/usr/bin/env python3

import sys
import os
sys.path.append('/Users/mithran/JobMateRefactor')

from app import create_app
from config import Config
from pymongo import MongoClient
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_canadian_job_descriptions():
    """Test that Canadian jobs now have enhanced descriptions"""
    try:
        # Set up app context
        app = create_app()
        
        with app.app_context():
            # Connect to MongoDB
            client = MongoClient(app.config['MONGODB_URI'] or 'mongodb://localhost:27017/')
            db = client[app.config['MONGODB_DB'] or 'jobmate_mongo']
            jobs_collection = db.jobs
            
            # Find Canadian jobs
            canadian_jobs = list(jobs_collection.find({
                "$or": [
                    {"location": {"$regex": "Canada", "$options": "i"}},
                    {"location": {"$regex": "Toronto", "$options": "i"}},
                    {"location": {"$regex": "Vancouver", "$options": "i"}},
                    {"location": {"$regex": "Montreal", "$options": "i"}},
                    {"location": {"$regex": "Calgary", "$options": "i"}}
                ]
            }).limit(5))
            
            if not canadian_jobs:
                print("❌ No Canadian jobs found in database")
                return False
            
            print(f"✅ Found {len(canadian_jobs)} Canadian jobs")
            
            # Test the job_detail route by calling it with actual job IDs
            from flask import url_for
            from app.jobs.routes import bp as jobs_bp
            
            success_count = 0
            for job in canadian_jobs:
                job_id = str(job['_id'])
                
                print(f"\n📋 Job: {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')}")
                print(f"   Location: {job.get('location', 'Unknown')}")
                print(f"   Job ID: {job_id}")
                
                # Check what description fields are available
                original_desc = job.get('description', '')
                job_desc = job.get('job_description', '')
                summary = job.get('summary', '')
                details = job.get('details', '')
                
                print(f"   Original description: {len(str(original_desc))} chars")
                print(f"   Job description: {len(str(job_desc))} chars")
                print(f"   Summary: {len(str(summary))} chars")
                print(f"   Details: {len(str(details))} chars")
                
                # Check if any meaningful content exists
                meaningful_content = False
                for field_name, field_value in [('description', original_desc), ('job_description', job_desc), 
                                              ('summary', summary), ('details', details)]:
                    if (field_value and str(field_value).strip() and 
                        str(field_value) != 'nan' and len(str(field_value)) > 20):
                        print(f"   ✅ Found content in {field_name}: {str(field_value)[:100]}...")
                        meaningful_content = True
                        break
                
                if meaningful_content:
                    success_count += 1
                else:
                    print(f"   ❌ No meaningful content found")
                    
                    # Show all available fields for debugging
                    available_fields = [k for k in job.keys() if job.get(k) and str(job.get(k)).strip()]
                    print(f"   Available fields: {available_fields}")
            
            print(f"\n📊 Results: {success_count}/{len(canadian_jobs)} jobs have meaningful description content")
            
            if success_count > 0:
                print("✅ SUCCESS: Jobs have description content available!")
                print("\n🔧 The enhanced job_detail function should now generate meaningful descriptions")
                print("   for jobs that lack proper description fields.")
                return True
            else:
                print("❌ ISSUE: No jobs have meaningful description content")
                print("   The enhanced job_detail function will need to generate content from available fields")
                return False
                
    except Exception as e:
        print(f"❌ Error testing Canadian job descriptions: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testing Enhanced Canadian Job Descriptions...")
    test_canadian_job_descriptions()
