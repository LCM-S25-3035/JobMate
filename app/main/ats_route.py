"""
ATS Score Recalculation Route
"""

from flask import request, jsonify, current_app
from flask_login import current_user, login_required
from app.main import bp
from bson import ObjectId
import re
import json
from app.ai_agents.gemini_utils import call_gemini_api

@bp.route('/recalculate_ats_score', methods=['POST'])
@login_required
def recalculate_ats_score():
    """Recalculate ATS score for a job based on current resume text"""
    data = request.json
    job_id = data.get('job_id')
    resume_text = data.get('resume_text')
    
    if not job_id or not resume_text:
        return jsonify({'success': False, 'error': 'Missing job ID or resume text'})
    
    try:
        # Get the job description from MongoDB
        mongo_db = current_app.mongo_db
        job = mongo_db.jobs.find_one({"_id": ObjectId(job_id)})
        
        if not job:
            return jsonify({'success': False, 'error': 'Job not found'})
        
        # Calculate ATS score using simplified version of the tailoring logic
        prompt = f"""
        You are an ATS (Applicant Tracking System) score calculator. Given the job description 
        and resume below, calculate a match score from 0-100 based on keyword matches, 
        relevant experience, and formatting compatibility.
        
        ## JOB DESCRIPTION
        ```
        {job.get('description', '')}
        ```
        
        ## RESUME
        ```
        {resume_text}
        ```
        
        Calculate and return only a number from 0-100 representing the ATS match score.
        The number should be based on:
        1. Keyword match percentage
        2. Skills alignment 
        3. Experience relevance
        4. Education requirements match
        
        Return ONLY the number, with no additional text or explanation.
        """
        
        # Call Gemini API for score calculation
        gemini_response = call_gemini_api(prompt)
        
        # Extract the score
        if 'candidates' in gemini_response:
            try:
                content = gemini_response['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Extract numeric value
                match = re.search(r'(\d+)', content)
                if match:
                    ats_score = int(match.group(1))
                    # Ensure score is in valid range
                    if ats_score < 0:
                        ats_score = 0
                    elif ats_score > 100:
                        ats_score = 100
                else:
                    # Default score if unable to parse
                    ats_score = 70
                    current_app.logger.warning(f"Could not parse ATS score from response: {content}")
                
                # Update the score in database
                mongo_db.tailored_resumes.update_one(
                    {"user_id": str(current_user.id), "job_id": str(job_id)},
                    {"$set": {"ats_score": ats_score}}
                )
                
                return jsonify({
                    'success': True, 
                    'ats_score': ats_score
                })
            except Exception as e:
                current_app.logger.error(f"Error extracting ATS score: {str(e)}")
                return jsonify({'success': False, 'error': f"Error extracting ATS score: {str(e)}"})
        else:
            error = gemini_response.get('error', 'Unknown error from Gemini API')
            return jsonify({'success': False, 'error': error})
            
    except Exception as e:
        current_app.logger.error(f"Error recalculating ATS score: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})
