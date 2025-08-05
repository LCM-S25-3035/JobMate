"""
Test script to verify ghost job filtering functionality.
"""

import sys
from app import create_app
from app.jobs.routes import build_enhanced_query
from pymongo import MongoClient
from config import Config

def test_ghost_job_query_builder():
    """Test ghost job query builder with different risk levels"""
    
    print("Testing ghost job query builder...")
    
    # Test with low risk
    query_low = build_enhanced_query(
        search_query="",
        location="",
        job_type="",
        job_level="",
        company="",
        salary_min=None,
        salary_max=None,
        ghost_risk="low"
    )
    
    print("\nLow risk query:")
    print(query_low)
    
    # Test with exclude high risk
    query_exclude_high = build_enhanced_query(
        search_query="",
        location="",
        job_type="",
        job_level="",
        company="",
        salary_min=None,
        salary_max=None,
        ghost_risk="exclude_high"
    )
    
    print("\nExclude high risk query:")
    print(query_exclude_high)
    
    # Test with show high risk
    query_show_high = build_enhanced_query(
        search_query="",
        location="",
        job_type="",
        job_level="",
        company="",
        salary_min=None,
        salary_max=None,
        ghost_risk="show_high"
    )
    
    print("\nShow high risk query:")
    print(query_show_high)
    
    # Test with no ghost risk filter
    query_no_filter = build_enhanced_query(
        search_query="",
        location="",
        job_type="",
        job_level="",
        company="",
        salary_min=None,
        salary_max=None,
        ghost_risk=""
    )
    
    print("\nNo ghost risk filter query:")
    print(query_no_filter)
    
    print("\nTest completed!")

def test_ghost_job_filter_mongo():
    """Test ghost job filtering against MongoDB"""
    # Connect directly to MongoDB
    from pymongo import MongoClient
    import os
    
    # Connect to MongoDB using environment variable or default
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/jobmate")
    client = MongoClient(MONGO_URI)
    db = client.get_database()
    
    print("Testing MongoDB ghost job filtering...")
    
    # Get total job count
    total_jobs = db.jobs.count_documents({})
    print(f"Total jobs in database: {total_jobs}")
    
    # Test with low risk
    low_risk_query = {
        '$or': [
            {'ghost_job_percentage': {'$lt': 40}},
            {'ghost_score': {'$lt': 0.4}}
        ]
    }
    low_risk_count = db.jobs.count_documents(low_risk_query)
    print(f"Low risk jobs: {low_risk_count}")
    
    # Test with exclude high risk
    exclude_high_query = {
        '$or': [
            {'ghost_job_percentage': {'$lt': 70}},
            {'ghost_score': {'$lt': 0.7}}
        ]
    }
    exclude_high_count = db.jobs.count_documents(exclude_high_query)
    print(f"Jobs excluding high risk: {exclude_high_count}")
    
    # Test with high risk only
    high_risk_query = {
        '$or': [
            {'ghost_job_percentage': {'$gte': 70}},
            {'ghost_score': {'$gte': 0.7}}
        ]
    }
    high_risk_count = db.jobs.count_documents(high_risk_query)
    print(f"High risk jobs: {high_risk_count}")
    
    # Find jobs with ghost_job_percentage or ghost_score
    has_ghost_data = db.jobs.count_documents({
        '$or': [
            {'ghost_job_percentage': {'$exists': True}},
            {'ghost_score': {'$exists': True}}
        ]
    })
    print(f"Jobs with ghost data: {has_ghost_data}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    print("Testing Ghost Job Filter Implementation")
    print("======================================\n")
    
    test_ghost_job_query_builder()
    print("\n--------------------------------------\n")
    test_ghost_job_filter_mongo()
