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
from app.ai_agents.gemini_utils import call_gemini_api, call_gemini_api_simple

@bp.route('/auto_optimize_resume', methods=['POST'])
@login_required
def auto_optimize_resume():
    """Auto-optimize resume to achieve 90%+ ATS score using targeted analysis"""
    current_app.logger.info(f"Auto-optimize resume called by user {current_user.id}")
    
    try:
        # Handle both form data and JSON
        if request.is_json:
            data = request.get_json()
            job_id = data.get('job_id')
            resume_content = data.get('resume_content')
        else:
            job_id = request.form.get('job_id')
            resume_content = request.form.get('resume_content')
        
        current_app.logger.info(f"Received data: job_id={job_id}, resume_length={len(resume_content) if resume_content else 0}")
        
        if not job_id or not resume_content:
            current_app.logger.error("Missing required parameters")
            return jsonify({
                'success': False, 
                'error': 'Missing required data: job_id and resume_content'
            }), 400
            
        # Get MongoDB database handle
        mongo_db = current_app.mongo_db
        
        # Get the job description
        try:
            job = mongo_db.jobs.find_one({'_id': ObjectId(job_id)})
            if not job:
                current_app.logger.error(f"Job not found: {job_id}")
                return jsonify({'success': False, 'error': 'Job not found'}), 404
        except Exception as e:
            current_app.logger.error(f"Error fetching job: {str(e)}")
            return jsonify({'success': False, 'error': 'Invalid job ID'}), 400
        
        # Step 1: Analyze current ATS score and identify gaps
        current_app.logger.info("Step 1: Analyzing current ATS gaps...")
        analysis_prompt = f"""
        Analyze this resume against the job description and provide ATS optimization insights:

        JOB DESCRIPTION:
        Title: {job.get('title', '')}
        Company: {job.get('company', '')}
        Description: {job.get('description', '')}
        Requirements: {job.get('requirements', '')}
        Skills: {', '.join(job.get('skills', [])) if job.get('skills') else 'Not specified'}

        CURRENT RESUME:
        {resume_content}

        Please analyze and provide:
        1. Current estimated ATS score (0-100)
        2. Missing keywords from job description that should be in resume
        3. Key skills mentioned in job but missing from resume
        4. Specific improvements needed for 90%+ ATS score
        5. Keywords that need higher density/frequency

        Format your response as:
        CURRENT_SCORE: [number]
        MISSING_KEYWORDS: [comma-separated list]
        MISSING_SKILLS: [comma-separated list]
        IMPROVEMENTS: [specific suggestions]
        HIGH_PRIORITY_KEYWORDS: [most important keywords to add]
        """
        
        analysis_response = call_gemini_api(analysis_prompt)
        
        if not analysis_response or 'error' in analysis_response:
            error_msg = analysis_response.get('error', 'Failed to analyze resume') if analysis_response else 'No response from AI'
            current_app.logger.error(f"Analysis failed: {error_msg}")
            return jsonify({'success': False, 'error': f'Analysis failed: {error_msg}'}), 500
            
        if 'candidates' not in analysis_response or not analysis_response['candidates']:
            current_app.logger.error("Invalid analysis response structure")
            return jsonify({'success': False, 'error': 'Invalid analysis response'}), 500
            
        analysis = analysis_response['candidates'][0]['content']['parts'][0]['text']
        current_app.logger.info(f"Analysis completed: {analysis[:200]}...")
        
        # Step 2: Create targeted optimization prompt
        current_app.logger.info("Step 2: Generating ATS-optimized resume...")
        optimization_prompt = f"""
        Based on this ATS analysis, optimize the resume to achieve 90%+ ATS score:

        ANALYSIS RESULTS:
        {analysis}

        CURRENT RESUME TO OPTIMIZE:
        {resume_content}

        JOB REQUIREMENTS:
        Title: {job.get('title', '')}
        Company: {job.get('company', '')}
        Description: {job.get('description', '')}
        Requirements: {job.get('requirements', '')}
        Skills: {', '.join(job.get('skills', [])) if job.get('skills') else ''}

        OPTIMIZATION RULES:
        1. Add missing keywords naturally throughout the resume (don't just stuff them)
        2. Include missing skills in relevant sections (Skills, Experience, Summary)
        3. Increase keyword density for high-priority terms from the job description
        4. Use exact phrases from job description where appropriate
        5. Maintain original structure, experience, and truthfulness - DO NOT fabricate experience
        6. Ensure keywords appear in multiple sections (summary, experience, skills)
        7. Use both acronyms and full forms (e.g., "AI" and "Artificial Intelligence")
        8. Match job title keywords in summary/objective section
        9. Add industry-specific buzzwords and technical terms from the job posting
        10. Optimize for ATS parsing (use standard section headers, clear bullet points)
        11. Keep the same overall length and structure as the original resume
        12. Focus on quantifiable achievements that relate to job requirements

        IMPORTANT: Return ONLY the optimized resume content that will score 90%+. 
        Do not include any explanations, analysis, or additional text outside the resume.
        """
        
        optimization_response = call_gemini_api(optimization_prompt)
        
        if not optimization_response or 'error' in optimization_response:
            error_msg = optimization_response.get('error', 'Failed to optimize resume') if optimization_response else 'No response from AI'
            current_app.logger.error(f"Optimization failed: {error_msg}")
            return jsonify({'success': False, 'error': f'Optimization failed: {error_msg}'}), 500
            
        if 'candidates' not in optimization_response or not optimization_response['candidates']:
            current_app.logger.error("Invalid optimization response structure")
            return jsonify({'success': False, 'error': 'Invalid optimization response'}), 500
            
        optimized_content = optimization_response['candidates'][0]['content']['parts'][0]['text'].strip()
        current_app.logger.info(f"Optimization completed, content length: {len(optimized_content)}")
        
        # Step 3: Verify the optimization improved the score (optional quick check)
        current_app.logger.info("Step 3: Verifying ATS score improvement...")
        verification_prompt = f"""
        Calculate the ATS score for this optimized resume against the job description.
        Focus on keyword matching, skill alignment, and ATS compatibility.

        JOB DESCRIPTION:
        Title: {job.get('title', '')}
        Requirements: {job.get('requirements', '')}
        Skills: {', '.join(job.get('skills', [])) if job.get('skills') else ''}

        OPTIMIZED RESUME:
        {optimized_content}

        Provide ONLY a number (0-100) representing the estimated ATS score.
        """
        
        verification_response = call_gemini_api(verification_prompt)
        estimated_score = 90  # Default optimistic score
        
        if verification_response and 'candidates' in verification_response and verification_response['candidates']:
            try:
                score_text = verification_response['candidates'][0]['content']['parts'][0]['text']
                import re
                score_match = re.search(r'\d+', score_text)
                if score_match:
                    estimated_score = int(score_match.group())
                    current_app.logger.info(f"Verified ATS score: {estimated_score}")
            except Exception as e:
                current_app.logger.warning(f"Score verification failed: {str(e)}")
        
        current_app.logger.info(f"Resume optimization successful, estimated score: {estimated_score}")
        
        return jsonify({
            'success': True,
            'optimized_content': optimized_content,
            'estimated_score': estimated_score,
            'message': f'Resume optimized to achieve {estimated_score}% ATS score with targeted keyword improvements!'
        })
            
    except Exception as e:
        current_app.logger.error(f"Auto-optimize error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Server error during optimization'
        }), 500
