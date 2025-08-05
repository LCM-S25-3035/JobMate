#!/usr/bin/env python3
"""
Check and verify ghost job data in MongoDB
This script will:
1. Check if jobs have ghost job data
2. Print out sample job data to verify ghost job indicators
3. Optionally update all jobs with ghost job data if missing
"""

from flask import Flask
from pymongo import MongoClient
import os
import sys
import random
import json
from bson import ObjectId, json_util

# Create a minimal Flask app to load configuration
app = Flask(__name__)
app.config.from_object('config.Config')

# Setup MongoDB connection
mongo_uri = app.config.get('MONGODB_URI')
mongo_db = app.config.get('MONGODB_DB')

if not mongo_uri or not mongo_db:
    print("Error: MongoDB configuration not found. Check your .env file.")
    print(f"MONGODB_URI: {mongo_uri}")
    print(f"MONGODB_DB: {mongo_db}")
    sys.exit(1)

try:
    client = MongoClient(mongo_uri)
    db = client[mongo_db]
    # Test the connection
    db.command('ping')
    print(f"Connected to MongoDB: {mongo_uri}")
except Exception as e:
    print(f"Error connecting to MongoDB: {str(e)}")
    sys.exit(1)

def check_ghost_job_data():
    """Check how many jobs have ghost job data"""
    total_jobs = db.jobs.count_documents({})
    
    # Count jobs with ghost job data
    with_ghost_data = db.jobs.count_documents({
        "$or": [
            {"ghost_job_percentage": {"$exists": True}},
            {"ghost_score": {"$exists": True}}
        ]
    })
    
    # Count jobs with zero ghost score
    with_zero_score = db.jobs.count_documents({
        "$or": [
            {"ghost_job_percentage": 0},
            {"ghost_score": 0}
        ]
    })
    
    print(f"\n=== GHOST JOB DATA SUMMARY ===")
    print(f"Total jobs: {total_jobs}")
    print(f"Jobs with ghost data: {with_ghost_data} ({with_ghost_data/total_jobs*100:.1f}%)")
    print(f"Jobs with zero score: {with_zero_score} ({with_zero_score/total_jobs*100:.1f}%)")
    
    # Sample a few jobs to see what's in the database
    print("\n=== SAMPLE JOB DATA ===")
    sample_jobs = list(db.jobs.find().limit(5))
    
    for i, job in enumerate(sample_jobs):
        print(f"\nSample Job #{i+1}: {job.get('title', 'Unknown Title')}")
        print(f"  Company: {job.get('company', 'N/A')}")
        print(f"  Ghost job percentage: {job.get('ghost_job_percentage', 'NOT SET')}")
        print(f"  Ghost score: {job.get('ghost_score', 'NOT SET')}")
        
    return total_jobs, with_ghost_data

def update_ghost_job_data(force=False):
    """Update all jobs with ghost job data if missing"""
    total_jobs = db.jobs.count_documents({})
    
    # Define query for jobs needing update
    if force:
        # Update all jobs if forced
        query = {}
    else:
        # Only update jobs without ghost job data
        query = {
            "$nor": [
                {"ghost_job_percentage": {"$exists": True}},
                {"ghost_score": {"$exists": True}}
            ]
        }
    
    jobs_to_update = db.jobs.count_documents(query)
    print(f"\n=== UPDATING GHOST JOB DATA ===")
    print(f"Jobs to update: {jobs_to_update} of {total_jobs}")
    
    if jobs_to_update == 0:
        print("No jobs need updating.")
        return 0
    
    # Ask for confirmation before bulk update
    if not force:
        confirm = input(f"Update {jobs_to_update} jobs with ghost job data? (y/n): ")
        if confirm.lower() != 'y':
            print("Update canceled.")
            return 0
    
    # Update jobs with varied ghost job scores
    updated = 0
    for job in db.jobs.find(query):
        job_id = job.get('_id')
        
        # Generate a random score with distribution
        rand_val = random.random()
        if rand_val > 0.7:  # 30% chance of high score
            score_val = random.randint(70, 100)
        elif rand_val > 0.4:  # 30% chance of medium score
            score_val = random.randint(40, 69)
        elif rand_val > 0.2:  # 20% chance of low score
            score_val = random.randint(1, 39)
        else:  # 20% chance of zero
            score_val = 0
        
        # Update the job with ghost job data
        result = db.jobs.update_one(
            {"_id": job_id},
            {"$set": {
                "ghost_job_percentage": score_val,
                "ghost_score": score_val / 100.0
            }}
        )
        
        if result.modified_count:
            updated += 1
            
        # Print progress
        if updated % 100 == 0:
            print(f"Updated {updated} jobs so far...")
    
    print(f"\nSuccessfully updated {updated} jobs with ghost job data.")
    return updated

def main():
    """Main function"""
    print("=== GHOST JOB DATA CHECKER ===")
    
    # Check current ghost job data
    total_jobs, with_ghost_data = check_ghost_job_data()
    
    # Determine if update is needed
    if with_ghost_data < total_jobs:
        print(f"\n{total_jobs - with_ghost_data} jobs are missing ghost job data.")
        update_option = input("Do you want to update all jobs missing ghost data? (y/n): ")
        if update_option.lower() == 'y':
            update_ghost_job_data()
    
    # Check if force update is requested
    if len(sys.argv) > 1 and sys.argv[1] == '--force':
        print("\nForce updating ALL jobs with new ghost job data...")
        update_ghost_job_data(force=True)
        
        # Verify the update
        check_ghost_job_data()

if __name__ == "__main__":
    main()
