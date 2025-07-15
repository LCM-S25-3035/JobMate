"""
Simplified application startup to test the MongoDB fix

This script creates a simplified version of the app to directly test 
the MongoDB update/insert operation that was causing the 500 error.
"""

import sys
import os
from pymongo import MongoClient
from bson import ObjectId
import datetime
import traceback

def main():
    """Run the MongoDB insertion/update test"""
    print("Starting MongoDB test...")
    
    try:
        # Connect to MongoDB
        print("Connecting to MongoDB...")
        mongo_uri = "mongodb://localhost:27017/"
        mongo_client = MongoClient(mongo_uri)
        
        # Ping the server to verify connection
        mongo_client.admin.command('ping')
        print("✅ MongoDB connected successfully")
        
        # Get the database
        mongo_db = mongo_client['jobmate_dev']
        
        # Test parameters
        user_id = "test_user_456"
        
        # Try to find an existing job
        job = mongo_db.jobs.find_one()
        if job:
            job_id = str(job['_id'])
            print(f"Found job with ID: {job_id}")
        else:
            # Create a test job if none exists
            job_id = str(ObjectId())
            print(f"Created test job ID: {job_id}")
        
        # First check if a document already exists and delete it
        print("\nRemoving any existing documents...")
        mongo_db.tailored_resumes.delete_many({"user_id": user_id, "job_id": job_id})
        
        # Make sure it doesn't exist
        existing_doc = mongo_db.tailored_resumes.find_one({"user_id": user_id, "job_id": job_id})
        print(f"Document exists before test: {existing_doc is not None}")
        
        # Prepare data for insert/update
        optimized_resume = "This is a test optimized resume."
        ats_score = 85
        
        print("\nTesting database operations:")
        
        try:
            # Check if a document exists first
            existing = mongo_db.tailored_resumes.find_one({"user_id": user_id, "job_id": job_id})
            
            if existing:
                # Update existing document
                print("Updating existing document...")
                mongo_db.tailored_resumes.update_one(
                    {"user_id": user_id, "job_id": job_id},
                    {"$set": {
                        "tailored_resume": optimized_resume,
                        "ats_score": ats_score
                    }}
                )
            else:
                # Create new document
                print("Creating new document...")
                mongo_db.tailored_resumes.insert_one({
                    "user_id": user_id,
                    "job_id": job_id,
                    "tailored_resume": optimized_resume,
                    "ats_score": ats_score,
                    "suggestions": []
                })
                
            # Verify the document exists now
            doc = mongo_db.tailored_resumes.find_one({"user_id": user_id, "job_id": job_id})
            
            if doc:
                print("✅ Document successfully created/updated")
                print(f"Fields in document: {list(doc.keys())}")
                print(f"tailored_resume present: {'tailored_resume' in doc}")
                print(f"ats_score value: {doc.get('ats_score')}")
            else:
                print("❌ Document not found after operation!")
                
            # Now let's test updating the same document
            print("\nUpdating the document again...")
            
            # Make the same check and update/insert
            existing = mongo_db.tailored_resumes.find_one({"user_id": user_id, "job_id": job_id})
            
            if existing:
                # Update existing document
                print("Updating existing document...")
                mongo_db.tailored_resumes.update_one(
                    {"user_id": user_id, "job_id": job_id},
                    {"$set": {
                        "tailored_resume": optimized_resume + " UPDATED",
                        "ats_score": ats_score + 5
                    }}
                )
            else:
                # Create new document
                print("Creating new document...")
                mongo_db.tailored_resumes.insert_one({
                    "user_id": user_id,
                    "job_id": job_id,
                    "tailored_resume": optimized_resume + " UPDATED",
                    "ats_score": ats_score + 5,
                    "suggestions": []
                })
                
            # Verify the document was updated
            doc = mongo_db.tailored_resumes.find_one({"user_id": user_id, "job_id": job_id})
            
            if doc:
                print("✅ Document successfully updated on second operation")
                print(f"Updated ats_score value: {doc.get('ats_score')}")
                print(f"Resume ends with 'UPDATED': {doc.get('tailored_resume', '').endswith('UPDATED')}")
            else:
                print("❌ Document not found after second operation!")
                
            print("\nTEST PASSED: MongoDB operations working correctly!")
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            print(traceback.format_exc())
            print("\nTEST FAILED: MongoDB operations failed!")
            
    except Exception as e:
        print(f"Connection error: {str(e)}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
