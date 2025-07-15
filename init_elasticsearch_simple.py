#!/usr/bin/env python3
"""
Simple Elasticsearch Initialization Script for JobMate
"""

import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.job_posting import JobPosting

def init_elasticsearch():
    """Initialize Elasticsearch with indices and data"""
    app = create_app()
    
    with app.app_context():
        print("🔍 Initializing Elasticsearch for JobMate...")
        
        # Import here to avoid circular imports
        from app.services.index_manager import index_manager
        
        # Check if Elasticsearch is available
        if not index_manager.is_available():
            print("❌ Elasticsearch is not available. Please ensure it's running.")
            return False
        
        print("✅ Elasticsearch is available")
        
        # Create index
        print("\n📁 Creating job index...")
        if index_manager.create_index(delete_existing=True):
            print("✅ Job index created successfully")
        else:
            print("❌ Failed to create job index")
            return False
        
        # Get active jobs from database
        print("\n📊 Fetching active jobs from database...")
        active_jobs = JobPosting.query.filter_by(status='active').all()
        print(f"Found {len(active_jobs)} active jobs")
        
        if not active_jobs:
            print("⚠️  No active jobs found in database")
            return True
        
        # Index all jobs
        print("\n🔄 Indexing jobs...")
        result = index_manager.bulk_index_jobs(active_jobs)
        
        print(f"✅ Successfully indexed {result['indexed']} jobs")
        if result['failed'] > 0:
            print(f"⚠️  Failed to index {result['failed']} jobs")
        
        # Get index statistics
        print("\n📈 Index Statistics:")
        stats = index_manager.get_index_stats()
        if stats:
            print(f"   📄 Total documents: {stats['total_docs']}")
            print(f"   💾 Index size: {stats['total_size']} bytes")
            print(f"   🏷️  Index name: {stats['index_name']}")
        
        print("\n🎉 Elasticsearch initialization completed!")
        return True

if __name__ == '__main__':
    try:
        success = init_elasticsearch()
        if success:
            print("\n🚀 JobMate Elasticsearch is ready!")
        else:
            print("\n❌ Elasticsearch initialization failed")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error during initialization: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 