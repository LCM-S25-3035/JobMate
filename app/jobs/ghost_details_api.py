"""
API endpoint for ghost job details
"""

from flask import jsonify, current_app
from pymongo import MongoClient
from bson import ObjectId
from app.jobs import bp

@bp.route('/api/jobs/<job_id>/ghost-details')
def ghost_job_details(job_id):
    """Get detailed ghost job analysis for a specific job"""
    try:
        # Get MongoDB connection
        mongo_db = current_app.mongo_db
        
        if not mongo_db:
            return jsonify({"error": "Database connection failed"}), 500
        
        # Find job by ID
        job = mongo_db.jobs.find_one({"_id": ObjectId(job_id)})
        
        if not job:
            return jsonify({"error": "Job not found"}), 404
        
        # Extract ghost job data
        ghost_percentage = job.get('ghost_job_percentage', 0)
        ghost_score = job.get('ghost_score', 0)
        
        # Use either percentage or score (whichever is available)
        if ghost_percentage == 0 and ghost_score:
            ghost_percentage = int(ghost_score * 100)
        
        # Get reasons if available, or create default ones based on score
        reasons = []
        if job.get('ghost_job_reasons'):
            # If reasons are stored as a string with separator
            if isinstance(job['ghost_job_reasons'], str):
                reasons = job['ghost_job_reasons'].split('; ')
            # If reasons are stored as a list
            elif isinstance(job['ghost_job_reasons'], list):
                reasons = job['ghost_job_reasons']
        
        # If no specific reasons are available, generate generic ones based on score
        if not reasons and ghost_percentage > 0:
            if ghost_percentage >= 70:
                reasons = [
                    "Job posting shows multiple high-risk characteristics",
                    "Similar to known fraudulent job listings",
                    "Unusual requirements for the stated position"
                ]
            elif ghost_percentage >= 40:
                reasons = [
                    "Some suspicious elements detected in this posting",
                    "Potential discrepancies in job requirements",
                    "Consider researching the company before applying"
                ]
            else:
                reasons = [
                    "Minor concerns detected with this job posting",
                    "Some elements of the listing seem unusual"
                ]
        
        # Determine risk category
        risk_category = "no_risk"
        if ghost_percentage >= 70:
            risk_category = "high_risk"
        elif ghost_percentage >= 40:
            risk_category = "medium_risk"
        elif ghost_percentage > 0:
            risk_category = "low_risk"
        
        # Return the ghost job details
        return jsonify({
            "job_id": str(job["_id"]),
            "title": job.get("title", ""),
            "company": job.get("company", ""),
            "percentage": ghost_percentage,
            "reasons": reasons,
            "category": job.get("ghost_job_category", risk_category),
            "confidence": job.get("ghost_job_confidence", "medium"),
            "updated_at": job.get("ghost_job_updated_at", "")
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting ghost job details: {str(e)}")
        return jsonify({"error": str(e)}), 500
