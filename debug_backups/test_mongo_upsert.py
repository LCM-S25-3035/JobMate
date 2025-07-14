"""
Test script to validate MongoDB tailored_resumes collection upsert functionality
"""

import json
import sys
from app import create_app
from bson import ObjectId
from pprint import pprint

def test_mongo_upsert():
    """Test MongoDB upsert operations for tailored_resumes"""
    
    # Create a test app context
    app = create_app()
    
    with app.app_context():
        mongo_db = app.mongo_db
        
        # 1. First, get a test user and job
        user_id = None
        job_id = None
        
        # Find a job from MongoDB
        job = mongo_db.jobs.find_one()
        if job:
            job_id = str(job['_id'])
            print(f"Using job ID: {job_id}")
        else:
            print("No jobs found in database.")
            return
        
        # Create a test user ID (can be arbitrary for testing)
        user_id = "test_user_123"
        print(f"Using test user ID: {user_id}")
        
        # 2. Delete any existing tailored resume for this user and job
        print("\nStep 1: Cleaning up any existing documents...")
        result = mongo_db.tailored_resumes.delete_many({
            "user_id": user_id,
            "job_id": job_id
        })
        print(f"Deleted {result.deleted_count} existing documents")
        
        # 3. Try to find a tailored resume (should return None)
        print("\nStep 2: Checking for document (should be None)...")
        existing_doc = mongo_db.tailored_resumes.find_one({
            "user_id": user_id,
            "job_id": job_id
        })
        print(f"Found document: {existing_doc}")
        
        # 4. Insert a new tailored resume
        print("\nStep 3: Inserting new document...")
        new_doc = {
            "user_id": user_id,
            "job_id": job_id,
            "tailored_resume": "This is a test resume",
            "ats_score": 85,
            "suggestions": []
        }
        
        try:
            insert_result = mongo_db.tailored_resumes.insert_one(new_doc)
            print(f"Inserted document with ID: {insert_result.inserted_id}")
        except Exception as e:
            print(f"Error inserting document: {e}")
            return
        
        # 5. Try to find the tailored resume (should return the document)
        print("\nStep 4: Checking for document (should exist now)...")
        existing_doc = mongo_db.tailored_resumes.find_one({
            "user_id": user_id,
            "job_id": job_id
        })
        print("Found document:")
        pprint(existing_doc)
        
        # 6. Update the existing document
        print("\nStep 5: Updating existing document...")
        try:
            update_result = mongo_db.tailored_resumes.update_one(
                {"user_id": user_id, "job_id": job_id},
                {"$set": {
                    "tailored_resume": "This is an updated resume",
                    "ats_score": 90
                }}
            )
            print(f"Updated {update_result.modified_count} documents")
        except Exception as e:
            print(f"Error updating document: {e}")
        
        # 7. Get the updated document
        print("\nStep 6: Checking updated document...")
        updated_doc = mongo_db.tailored_resumes.find_one({
            "user_id": user_id,
            "job_id": job_id
        })
        print("Updated document:")
        pprint(updated_doc)
        
        print("\nTest completed successfully!")

if __name__ == '__main__':
    test_mongo_upsert()
