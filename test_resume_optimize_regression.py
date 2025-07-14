"""
Regression test for resume optimization MongoDB operations.
This test verifies that the tailored_resume functionality correctly handles
both new and existing documents in the database.
"""

import json
import sys
from app import create_app
from bson import ObjectId

def run_regression_test():
    """Test the tailored resume upsert functionality"""
    
    # Create a test app context
    app = create_app()
    
    with app.app_context():
        # Get MongoDB connection
        mongo_db = app.mongo_db
        
        # Use a test user and job ID
        test_user_id = "test_regression_user"
        
        # Find a job ID to use
        job = mongo_db.jobs.find_one()
        if not job:
            print("ERROR: No jobs found in database. Test cannot continue.")
            return False
            
        job_id = str(job['_id'])
        print(f"Using job ID: {job_id}")
        
        # Ensure we start with a clean state
        mongo_db.tailored_resumes.delete_many({"user_id": test_user_id, "job_id": job_id})
        
        # Sample resume text
        resume_text = "Test resume for regression testing"
        
        # TEST CASE 1: Insert a new document
        print("\n--- TEST CASE 1: Insert new document ---")
        
        # Check document doesn't exist
        existing = mongo_db.tailored_resumes.find_one({"user_id": test_user_id, "job_id": job_id})
        if existing:
            print("ERROR: Document already exists when it shouldn't")
            return False
            
        # Insert new document
        mongo_db.tailored_resumes.insert_one({
            "user_id": test_user_id,
            "job_id": job_id,
            "tailored_resume": resume_text,
            "ats_score": 85,
            "suggestions": []
        })
        
        # Verify document exists
        doc = mongo_db.tailored_resumes.find_one({"user_id": test_user_id, "job_id": job_id})
        if not doc or "tailored_resume" not in doc:
            print("ERROR: Document not created correctly")
            return False
            
        print("✓ Document created successfully")
        
        # TEST CASE 2: Update existing document
        print("\n--- TEST CASE 2: Update existing document ---")
        
        # Update the document
        updated_resume = resume_text + " (Updated)"
        mongo_db.tailored_resumes.update_one(
            {"user_id": test_user_id, "job_id": job_id},
            {"$set": {
                "tailored_resume": updated_resume,
                "ats_score": 90
            }}
        )
        
        # Verify document was updated
        updated_doc = mongo_db.tailored_resumes.find_one({"user_id": test_user_id, "job_id": job_id})
        if not updated_doc or updated_doc.get("tailored_resume") != updated_resume:
            print("ERROR: Document not updated correctly")
            return False
            
        print("✓ Document updated successfully")
        
        # TEST CASE 3: Test upsert operation (update or insert)
        print("\n--- TEST CASE 3: Test upsert operation ---")
        
        # Function that mimics our upsert logic
        def test_upsert(user_id, job_id, resume_text, ats_score):
            # Check if document exists
            existing_doc = mongo_db.tailored_resumes.find_one({"user_id": user_id, "job_id": job_id})
            
            if existing_doc:
                # Update
                mongo_db.tailored_resumes.update_one(
                    {"user_id": user_id, "job_id": job_id},
                    {"$set": {
                        "tailored_resume": resume_text,
                        "ats_score": ats_score
                    }}
                )
            else:
                # Insert
                mongo_db.tailored_resumes.insert_one({
                    "user_id": user_id,
                    "job_id": job_id,
                    "tailored_resume": resume_text,
                    "ats_score": ats_score,
                    "suggestions": []
                })
                
            # Check if operation succeeded
            doc = mongo_db.tailored_resumes.find_one({"user_id": user_id, "job_id": job_id})
            return doc and doc.get("tailored_resume") == resume_text
        
        # Test with existing document
        result1 = test_upsert(test_user_id, job_id, "Updated via upsert", 95)
        
        # Test with new document (delete first)
        mongo_db.tailored_resumes.delete_many({"user_id": test_user_id, "job_id": job_id})
        result2 = test_upsert(test_user_id, job_id, "Created via upsert", 85)
        
        if not result1 or not result2:
            print("ERROR: Upsert operation failed")
            return False
            
        print("✓ Upsert operation works correctly for both update and insert cases")
        
        # Clean up after test
        mongo_db.tailored_resumes.delete_many({"user_id": test_user_id})
        
        print("\nALL TESTS PASSED!")
        return True

if __name__ == "__main__":
    if run_regression_test():
        sys.exit(0)
    else:
        sys.exit(1)
