#!/usr/bin/env python3
"""
MongoDB Job Data Field Migration Tool

This script migrates job data in MongoDB from old field names to new field names:
- 'url' or 'application_url' to 'job_url_direct'
- 'email' to 'application_email'

Usage:
python update_job_fields.py
"""

import os
from flask import Flask
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

def create_minimal_app():
    """Create a minimal Flask app for MongoDB connection"""
    app = Flask(__name__)
    app.config['MONGODB_URI'] = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
    app.config['MONGODB_DB'] = os.environ.get('MONGODB_DB', 'job_automation')
    
    # Connect to MongoDB
    client = MongoClient(app.config['MONGODB_URI'])
    app.mongo_db = client[app.config['MONGODB_DB']]
    
    return app

def migrate_job_url_fields(mongo_db):
    """Migrate URL fields in job documents"""
    # Get all jobs
    jobs_collection = mongo_db.jobs
    jobs = jobs_collection.find({})
    
    updated_count = 0
    skipped_count = 0
    
    for job in jobs:
        update_data = {}
        job_id = job['_id']
        
        # Check for URL fields
        if 'url' in job and not job.get('job_url_direct'):
            update_data['job_url_direct'] = job['url']
        elif 'application_url' in job and not job.get('job_url_direct'):
            update_data['job_url_direct'] = job['application_url']
            
        # Check for email fields
        if 'email' in job and not job.get('application_email'):
            update_data['application_email'] = job['email']
            
        if update_data:
            jobs_collection.update_one({'_id': job_id}, {'$set': update_data})
            updated_count += 1
            print(f"Updated job {job_id}: {job.get('title', 'No title')} - {update_data}")
        else:
            skipped_count += 1
            
    return updated_count, skipped_count

def print_summary(mongo_db):
    """Print a summary of the job fields in the database"""
    # Get all jobs
    jobs_collection = mongo_db.jobs
    total_jobs = jobs_collection.count_documents({})
    
    # Count documents with various URL and email fields
    job_url_direct_count = jobs_collection.count_documents({'job_url_direct': {'$exists': True}})
    url_count = jobs_collection.count_documents({'url': {'$exists': True}})
    application_url_count = jobs_collection.count_documents({'application_url': {'$exists': True}})
    
    application_email_count = jobs_collection.count_documents({'application_email': {'$exists': True}})
    email_count = jobs_collection.count_documents({'email': {'$exists': True}})
    contact_email_count = jobs_collection.count_documents({'contact_email': {'$exists': True}})
    
    print("\n--- MongoDB Jobs Collection Summary ---")
    print(f"Total jobs: {total_jobs}")
    print("\nURL Fields:")
    print(f"- job_url_direct: {job_url_direct_count}")
    print(f"- url: {url_count}")
    print(f"- application_url: {application_url_count}")
    print("\nEmail Fields:")
    print(f"- application_email: {application_email_count}")
    print(f"- email: {email_count}")
    print(f"- contact_email: {contact_email_count}")
    print("\n")

def main():
    """Main function to run the migration"""
    print("Starting MongoDB job field migration...")
    
    try:
        app = create_minimal_app()
        
        # Print current state
        print("Before migration:")
        print_summary(app.mongo_db)
        
        # Confirm before proceeding
        confirm = input("\nDo you want to proceed with the migration? [y/N]: ")
        if confirm.lower() != 'y':
            print("Migration cancelled.")
            return
        
        # Run migration
        updated, skipped = migrate_job_url_fields(app.mongo_db)
        print(f"\nMigration complete: {updated} jobs updated, {skipped} jobs skipped.")
        
        # Print new state
        print("\nAfter migration:")
        print_summary(app.mongo_db)
        
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
