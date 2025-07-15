"""
Optimize Routes for JobMate
"""

import json
import re
import datetime
import traceback
from flask import render_template, redirect, url_for, request, jsonify, current_app
from flask_login import current_user, login_required
from bson import ObjectId

from app.main import bp
from app.ai_agents.gemini_utils import call_gemini_api

@bp.route('/auto_optimize_resume', methods=['POST'])
@login_required
def auto_optimize_resume():
    data = request.json
    job_id = data.get('job_id')
    resume_text = data.get('resume_text')
    target_score = data.get('target_score', 90)
    
    if not job_id or not resume_text:
        return jsonify({'success': False, 'error': 'Missing job ID or resume text'})
    
    try:
        # Get MongoDB database handle
        mongo_db = current_app.mongo_db
        
        # Get the job description
        job = mongo_db.jobs.find_one({'_id': ObjectId(job_id)})
        if not job:
            return jsonify({'success': False, 'error': 'Job not found'})
        
        # Get the original suggestions if available
        tailored_resume = mongo_db.tailored_resumes.find_one({"user_id": str(current_user.id), "job_id": job_id})
        suggestions = []
        if tailored_resume and 'suggestions' in tailored_resume:
            suggestions = tailored_resume['suggestions']
        
        # Use AI to optimize the resume to reach 90% score
        prompt = f"""
        You are an expert ATS optimization specialist and resume writer. You need to optimize the provided resume 
        to achieve at least a {target_score}% match with the job description. Use the provided suggestions 
        as a guide for what needs to be improved.

        JOB DESCRIPTION:
        ```
        {job.get('description', '')}
        ```

        CURRENT RESUME:
        ```
        {resume_text}
        ```

        SUGGESTIONS FOR IMPROVEMENT:
        ```
        {json.dumps(suggestions, indent=2)}
        ```

        INSTRUCTIONS:
        1. Maintain the same overall structure of the resume
        2. Implement the suggestions given
        3. Add relevant keywords from the job description
        4. Quantify achievements where possible
        5. Ensure proper formatting for ATS compatibility
        6. DO NOT fabricate experience or qualifications not mentioned in the original resume
        7. Make sure experience section has 5 bullet points per job with metrics
        8. Keep skills organized in proper categories with commas between skills

        IMPORTANT: Return ONLY a valid JSON object with the following exact keys:
        1. "optimized_resume" - containing the full text of the optimized resume
        2. "ats_score" - a number that must be {target_score} or higher
        3. "implemented_suggestions" - an array of integers representing the 0-based indices of implemented suggestions
        
        Example format (but with your actual optimized resume):
        {{
          "optimized_resume": "Resume text goes here...",
          "ats_score": 92,
          "implemented_suggestions": [0, 1, 2]
        }}

        Do not include any other text, explanation, or markdown formatting outside the JSON object.
        """
        
        # Call AI for optimization
        api_response = call_gemini_api(prompt)
        
        try:
            # Extract the text content from the Gemini API response structure
            if (isinstance(api_response, dict) and
                'candidates' in api_response and
                len(api_response['candidates']) > 0 and
                'content' in api_response['candidates'][0] and
                'parts' in api_response['candidates'][0]['content'] and
                len(api_response['candidates'][0]['content']['parts']) > 0 and
                'text' in api_response['candidates'][0]['content']['parts'][0]):
                
                response_text = api_response['candidates'][0]['content']['parts'][0]['text']
                
                # Clean up the response text
                
                # First, remove any markdown formatting
                if "```" in response_text:
                    # Extract content between code blocks if present
                    code_block_pattern = r"```(?:json)?(.*?)```"
                    code_match = re.search(code_block_pattern, response_text, re.DOTALL)
                    if code_match:
                        response_text = code_match.group(1).strip()
                
                # Remove any text before the first { and after the last }
                first_brace = response_text.find('{')
                last_brace = response_text.rfind('}')
                
                if first_brace >= 0 and last_brace >= 0 and last_brace > first_brace:
                    response_text = response_text[first_brace:last_brace+1]
                
                # Now try to parse the JSON
                # Try parsing the JSON
                try:
                    result = json.loads(response_text)
                except json.JSONDecodeError as e:
                    current_app.logger.error(f"JSON decode error: {str(e)}")
                    
                    # Try to fix common JSON issues and retry
                    try:
                        # Replace single quotes with double quotes
                        fixed_text = response_text.replace("'", '"')
                        # Try to parse again
                        result = json.loads(fixed_text)
                    except json.JSONDecodeError:
                        # If all else fails, return an error
                        current_app.logger.error("Failed to parse JSON even after fixing quotes")
                        return jsonify({'success': False, 'error': f'Failed to parse AI response as valid JSON. Details: {str(e)}'})
                        
                # Validate the required fields are present
                if not all(k in result for k in ['optimized_resume', 'ats_score', 'implemented_suggestions']):
                    missing = [k for k in ['optimized_resume', 'ats_score', 'implemented_suggestions'] if k not in result]
                    current_app.logger.error(f"Missing required fields in response: {missing}")
                    return jsonify({'success': False, 'error': f'AI response missing required fields: {", ".join(missing)}'})
                
                # Extract the required fields from the result
                optimized_resume = result['optimized_resume']
                new_ats_score = result['ats_score']
                implemented_suggestions = result['implemented_suggestions']
                
                # Additional validation
                if not isinstance(optimized_resume, str):
                    current_app.logger.error(f"Optimized resume is not a string: {type(optimized_resume)}")
                    optimized_resume = str(optimized_resume)
                    
                if not isinstance(new_ats_score, (int, float)):
                    current_app.logger.error(f"ATS score is not a number: {type(new_ats_score)}")
                    try:
                        new_ats_score = int(new_ats_score)
                    except:
                        new_ats_score = 90
                
                if not isinstance(implemented_suggestions, list):
                    current_app.logger.error(f"Implemented suggestions is not a list: {type(implemented_suggestions)}")
                    implemented_suggestions = []
                
                # Convert to 1-based indexing to match template loop.index
                implemented_indices = [idx + 1 for idx in implemented_suggestions]
                
                # Update the database with the new optimized resume
                try:
                    # Check if a tailored resume document already exists for this user and job
                    existing_doc = mongo_db.tailored_resumes.find_one({"user_id": str(current_user.id), "job_id": job_id})
                    
                    if existing_doc:
                        # Update existing document
                        mongo_db.tailored_resumes.update_one(
                            {"user_id": str(current_user.id), "job_id": job_id},
                            {"$set": {
                                "tailored_resume": optimized_resume,
                                "ats_score": new_ats_score
                            }}
                        )
                    else:
                        # Create new document
                        mongo_db.tailored_resumes.insert_one({
                            "user_id": str(current_user.id),
                            "job_id": job_id,
                            "tailored_resume": optimized_resume,
                            "ats_score": new_ats_score,
                            "suggestions": [] # Initialize with empty suggestions
                        })
                        current_app.logger.info(f"Created new tailored resume document for user {current_user.id} and job {job_id}")
                except Exception as db_error:
                    current_app.logger.error(f"Database error: {str(db_error)}")
                    # Continue despite database error, returning successful response
                    # This allows the user to still see the optimized resume even if saving fails
                
                return jsonify({
                    'success': True,
                    'optimized_resume': optimized_resume,
                    'ats_score': new_ats_score,
                    'implemented_suggestions': implemented_indices
                })
            else:
                current_app.logger.error(f"Unexpected API response structure: {str(api_response)[:200]}...")
                return jsonify({'success': False, 'error': 'Invalid response from AI service: missing expected fields'})
                
        except Exception as e:
            current_app.logger.error(f"Error parsing optimization result: {str(e)}")
            return jsonify({'success': False, 'error': f'Error parsing optimization result: {str(e)}'})
    
    except Exception as e:
        # Log the error with traceback for server logs
        current_app.logger.error(f"Error optimizing resume: {str(e)}")
        current_app.logger.debug(traceback.format_exc())
        
        # Return a user-friendly error message
        return jsonify({'success': False, 'error': f'Error optimizing resume: {str(e)}'})
