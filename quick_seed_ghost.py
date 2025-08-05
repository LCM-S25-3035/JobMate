"""
Quick script to add ghost job scores to existing MongoDB jobs
"""

from pymongo import MongoClient
import random
from datetime import datetime
import os

print("🔄 Adding ghost job scores to existing jobs...")

# Connect to MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/jobmate")
client = MongoClient(MONGO_URI)
db = client.get_database()

# Get jobs collection
jobs_collection = db.jobs

# Get all job IDs
jobs = list(jobs_collection.find({}, {"_id": 1}))
updated_count = 0

# Update each job with a different random ghost job score
for job in jobs:
    # Generate a random score between 0 and 100
    score = random.randint(0, 100)
    
    # Determine confidence level based on score
    if score >= 70:
        confidence = "high"
        category = "suspicious"
    elif score >= 40:
        confidence = "medium" 
        category = "suspicious"
    elif score >= 20:
        confidence = "low"
        category = "normal"
    else:
        confidence = "very low"
        category = "normal"
    
    # Generate reasons based on score
    reasons = []
    if score > 0:
        possible_reasons = [
            "Job has been reposted multiple times",
            "Vague job description",
            "Extremely high requirements for salary range",
            "Position has been open for more than 3 months",
            "Identical to other postings by same company",
            "No direct application link provided",
            "Contains unusual requirements for position",
            "Company is known for collecting resumes"
        ]
        num_reasons = min(3, max(1, score // 25))
        reasons = random.sample(possible_reasons, num_reasons)
    
    # Update the job with its unique ghost job score
    result = jobs_collection.update_one(
        {"_id": job["_id"]},
        {
            "$set": {
                "ghost_job_percentage": score,
                "ghost_score": score / 100.0,
                "ghost_job_confidence": confidence,
                "ghost_job_category": category,
                "ghost_job_reasons": "; ".join(reasons) if reasons else None,
                "ghost_job_updated_at": datetime.now()
            }
        }
    )
    
    if result.modified_count > 0:
        updated_count += 1

print(f"✅ Successfully updated {updated_count} jobs with varied ghost job scores")
print("🔍 Now restart the application and check if the indicators appear with different values")
