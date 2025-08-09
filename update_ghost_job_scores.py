#!/usr/bin/env python3
"""
JobMate Ghost Job Score Update Script
Adds ghost job scores to existing MongoDB job entries
"""

import os
import sys
import random
import logging
from datetime import datetime
from flask import current_app
from pymongo import MongoClient
from bson import ObjectId

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from config import Config

def update_ghost_job_scores():
    """Update MongoDB jobs with ghost job scores"""
    
    app = create_app()
    
    with app.app_context():
        try:
            # Get MongoDB connection
            mongo_db = current_app.mongo_db
            
            if mongo_db is None:
                logger.error("MongoDB connection not available")
                return
            
            # Find all jobs in the jobs collection
            query = {}
            
            jobs = list(mongo_db.jobs.find(query))
            
            if not jobs:
                logger.info("No jobs found in the database")
                return
            
            logger.info(f"Found {len(jobs)} jobs to analyze")
            
            # List of possible ghost job reasons
            ghost_reasons = [
                "Job has been reposted multiple times",
                "Vague job description",
                "Extremely high requirements for salary range",
                "Position has been open for more than 3 months",
                "Identical to other postings by same company",
                "No direct application link provided",
                "Contains unusual requirements for position",
                "Company is known for collecting resumes",
                "Multiple positions with identical description",
                "No specific location given for on-site role"
            ]
            
            for job in jobs:
                # Skip if not a proper document
                if not isinstance(job, dict):
                    continue
                    
                # Generate a random ghost job score (higher probability of low scores)
                score_distribution = [0] * 60 + list(range(1, 101)) * 2  # More zeros for realistic distribution
                ghost_percentage = random.choice(score_distribution)
                
                # Only add reasons if the score is above 0
                reasons = []
                if ghost_percentage > 0:
                    # Number of reasons based on the score
                    num_reasons = max(1, min(5, ghost_percentage // 20))
                    reasons = random.sample(ghost_reasons, num_reasons)
                
                # Determine confidence level
                confidence = "low"
                if ghost_percentage >= 70:
                    confidence = "high"
                elif ghost_percentage >= 40:
                    confidence = "medium"
                
                # Update the job with ghost job data
                update_data = {
                    "ghost_job_percentage": ghost_percentage,
                    "ghost_score": ghost_percentage / 100.0,
                    "ghost_job_confidence": confidence,
                    "ghost_job_category": "suspicious" if ghost_percentage >= 50 else "normal",
                    "ghost_job_updated_at": datetime.utcnow()
                }
                
                if reasons:
                    update_data["ghost_job_reasons"] = "; ".join(reasons)
                
                # Debug output for each job
                job_id = str(job["_id"])
                job_title = job.get("title", "Unknown Title")
                logger.info(f"Updating job '{job_title}' (ID: {job_id}) with ghost score: {ghost_percentage}%")
                
                mongo_db.jobs.update_one(
                    {"_id": job["_id"]},
                    {"$set": update_data}
                )
            
            logger.info(f"Successfully updated ghost job scores for {len(jobs)} jobs")
            
        except Exception as e:
            logger.error(f"Error updating ghost job scores: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())

if __name__ == "__main__":
    logger.info("Starting ghost job score update")
    update_ghost_job_scores()
    logger.info("Ghost job score update script completed")
