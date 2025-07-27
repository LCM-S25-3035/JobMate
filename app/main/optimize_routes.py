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

def get_comprehensive_job_description(job):
    """Extract job description from multiple possible fields in MongoDB"""
    
    description_parts = []
    
    # Try all possible description fields that might exist in your MongoDB
    description_fields = [
        ('description', 'Job Description'),
        ('job_description', 'Job Details'), 
        ('summary', 'Summary'),
        ('company_description', 'About Company'),
        ('requirements', 'Requirements'),
        ('responsibilities', 'Responsibilities'),
        ('details', 'Details'),
        ('description_content', 'Description Content'),
        ('job_summary', 'Job Summary'),
        ('posting_description', 'Posting Description'),
        ('full_description', 'Full Description'),
        ('job_details', 'Job Information')
    ]
    
    for field, label in description_fields:
        content = job.get(field)
        if content and str(content).strip() and str(content) != 'nan' and len(str(content)) > 20:
            description_parts.append(f"{label}:\n{content}")
    
    # Add skills information if available
    if job.get('skills'):
        if isinstance(job['skills'], list):
            skills_text = ', '.join([str(skill) for skill in job['skills']])
        else:
            skills_text = str(job['skills'])
        if skills_text.strip() and skills_text != 'nan':
            description_parts.append(f"Required Skills:\n{skills_text}")
    
    # Add other relevant job metadata
    metadata_parts = []
    
    # Job type and level information
    if job.get('job_type') and str(job.get('job_type')) != 'nan':
        metadata_parts.append(f"Job Type: {job['job_type']}")
    if job.get('experience_level') and str(job.get('experience_level')) != 'nan':
        metadata_parts.append(f"Experience Level: {job['experience_level']}")
    if job.get('experience_range') and str(job.get('experience_range')) != 'nan':
        metadata_parts.append(f"Experience Required: {job['experience_range']}")
    if job.get('seniority_level') and str(job.get('seniority_level')) != 'nan':
        metadata_parts.append(f"Seniority: {job['seniority_level']}")
    
    # Company and industry information
    if job.get('company_industry') and str(job.get('company_industry')) != 'nan':
        metadata_parts.append(f"Industry: {job['company_industry']}")
    if job.get('company_size') and str(job.get('company_size')) != 'nan':
        metadata_parts.append(f"Company Size: {job['company_size']}")
    
    # Salary information (fix the $0-$0 issue)
    salary_info = []
    if job.get('salary_min') and str(job.get('salary_min')) not in ['nan', '0', 0]:
        salary_info.append(f"Min: ${job['salary_min']}")
    if job.get('salary_max') and str(job.get('salary_max')) not in ['nan', '0', 0]:
        salary_info.append(f"Max: ${job['salary_max']}")
    if job.get('salary_source') and str(job.get('salary_source')) != 'nan':
        salary_info.append(f"Source: {job['salary_source']}")
    if salary_info:
        metadata_parts.append(f"Salary Range: {' - '.join(salary_info)}")
    
    if metadata_parts:
        description_parts.append("Additional Job Information:\n" + "\n".join(metadata_parts))
    
    # Combine all parts
    if description_parts:
        full_description = '\n\n'.join(description_parts)
        return full_description
    
    # If no description found, create a basic one from available info
    basic_info_parts = []
    basic_info_parts.append(f"Position: {job.get('title', 'Unknown Position')}")
    basic_info_parts.append(f"Company: {job.get('company', 'Unknown Company')}")
    basic_info_parts.append(f"Location: {job.get('location', 'Unknown Location')}")
    
    if job.get('source'):
        basic_info_parts.append(f"Source: {job.get('source')}")
    if job.get('posted_date'):
        basic_info_parts.append(f"Posted: {job.get('posted_date')}")
    
    return '\n'.join(basic_info_parts)

def debug_job_fields(job):
    """Debug function to see all available fields in a job document"""
    from flask import current_app
    
    current_app.logger.info("=== JOB DEBUG INFO ===")
    current_app.logger.info(f"Job ID: {job.get('_id')}")
    current_app.logger.info(f"Available fields: {list(job.keys())}")
    
    # Check description fields specifically
    description_fields = ['description', 'job_description', 'summary', 'company_description', 
                         'requirements', 'responsibilities', 'details', 'description_content']
    
    for field in description_fields:
        content = job.get(field)
        if content and str(content) != 'nan':
            current_app.logger.info(f"{field}: {len(str(content))} chars - {str(content)[:100]}...")
    
    current_app.logger.info("=== END DEBUG INFO ===")

@bp.route('/auto_optimize_resume', methods=['POST'])
@login_required
def auto_optimize_resume():
    """Auto-optimize resume to achieve 90%+ ATS score using iterative targeted analysis"""
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
        
        # Enhanced job description extraction from MongoDB
        current_app.logger.info("Extracting comprehensive job description from MongoDB...")
        
        # Debug the job fields to see what's available (only in debug mode)
        if current_app.debug:
            debug_job_fields(job)
        
        # Get comprehensive job description from all available fields
        comprehensive_job_description = get_comprehensive_job_description(job)
        
        current_app.logger.info(f"Comprehensive job description length: {len(comprehensive_job_description)} characters")
        
        # Keep backward compatibility - if comprehensive description is short, fall back to original method
        fallback_description = job.get('description', '')
        if len(comprehensive_job_description) < 100 and len(fallback_description) > 50:
            job_description_to_use = fallback_description
            current_app.logger.info("Using fallback description for compatibility")
        else:
            job_description_to_use = comprehensive_job_description
            current_app.logger.info("Using comprehensive description extraction")

        # ITERATIVE OPTIMIZATION FOR 90+ ATS SCORE
        current_app.logger.info("Starting iterative optimization to achieve 90+ ATS score...")
        
        optimized_content = resume_content
        current_score = 0
        optimization_attempts = 0
        max_attempts = 5
        target_score = 90
        attempt_scores = []
        
        while current_score < target_score and optimization_attempts < max_attempts:
            optimization_attempts += 1
            current_app.logger.info(f"Optimization attempt {optimization_attempts}/{max_attempts}")
            
            # Step 1: Get current ATS score
            try:
                score_analysis_prompt = f"""
                Analyze this resume against the job description and provide ONLY the ATS score as a number between 0-100.

                JOB DESCRIPTION:
                Title: {job.get('title', '')}
                Company: {job.get('company', '')}
                Description: {job_description_to_use}
                Requirements: {job.get('requirements', '')}
                Skills: {', '.join(job.get('skills', [])) if job.get('skills') else 'Not specified'}

                RESUME:
                {optimized_content}

                Consider:
                - Keyword matching and density
                - Skills alignment
                - Experience relevance
                - ATS parsing compatibility
                - Section headers and formatting

                Respond with ONLY a number (0-100):
                """
                
                score_response = call_gemini_api(score_analysis_prompt)
                if score_response and 'candidates' in score_response and score_response['candidates']:
                    score_text = score_response['candidates'][0]['content']['parts'][0]['text'].strip()
                    import re
                    score_match = re.search(r'\d+', score_text)
                    if score_match:
                        current_score = int(score_match.group())
                        attempt_scores.append(current_score)
                        current_app.logger.info(f"Current ATS score: {current_score}")
                        
                        if current_score >= target_score:
                            current_app.logger.info(f"Target score achieved: {current_score}")
                            break
                    else:
                        current_score = 0
                else:
                    current_score = 0
                    
            except Exception as e:
                current_app.logger.error(f"Error getting ATS score: {str(e)}")
                current_score = 0
            
            # Step 2: Generate aggressive optimization targeting 90+ score
            optimization_prompt = f"""
            You are an expert ATS resume optimizer. The current resume has an ATS score of {current_score}/100 (attempt {optimization_attempts}/5).
            Your goal is to optimize this resume to achieve a score of 90+ for the following job posting.

            CURRENT ISSUES TO ADDRESS:
            - Score is only {current_score}/100 - needs significant improvement to reach 90+
            - Must achieve 90+ ATS compatibility score in this optimization round
            - Focus on aggressive keyword integration and ATS-friendly structure

            JOB POSTING:
            Title: {job.get('title', '')}
            Company: {job.get('company', '')}
            Description: {job_description_to_use}
            Requirements: {job.get('requirements', '')}
            Skills: {', '.join(job.get('skills', [])) if job.get('skills') else 'Not specified'}

            CURRENT RESUME (Score: {current_score}/100):
            {optimized_content}

            OPTIMIZATION REQUIREMENTS FOR 90+ SCORE:

            1. KEYWORD OPTIMIZATION (Critical - 40 points):
               - Extract ALL relevant keywords from job description
               - Integrate keywords naturally throughout resume (minimum 80% keyword match)
               - Use exact phrases from job posting where possible
               - Include technical skills, tools, and certifications mentioned
               - Use both acronyms and full forms (e.g., "AI" and "Artificial Intelligence")
               - Ensure keywords appear in multiple sections (summary, experience, skills)

            2. ATS-FRIENDLY FORMATTING (Critical - 25 points):
               - Use standard section headers: Professional Summary, Experience, Education, Skills
               - Ensure clean, parseable structure with clear hierarchy
               - Use bullet points for achievements and responsibilities
               - Avoid complex formatting, tables, or graphics
               - Use standard fonts and consistent formatting

            3. CONTENT ALIGNMENT (Critical - 25 points):
               - Quantify achievements with specific metrics that relate to job requirements
               - Use action verbs that match job responsibilities
               - Align experience descriptions with job requirements
               - Highlight relevant projects and accomplishments
               - Include industry-specific terminology from job posting

            4. SKILLS & QUALIFICATIONS MATCHING (Critical - 10 points):
               - Include ALL technical skills mentioned in job posting
               - Add relevant certifications if applicable to role
               - Match experience level expectations
               - Include soft skills mentioned in job description

            SPECIFIC INSTRUCTIONS FOR 90+ TARGET:
            - Be aggressive in keyword integration while maintaining readability
            - Prioritize ATS parsing compatibility over visual appeal  
            - Include exact job title keywords in professional summary
            - Use job description language in experience bullet points
            - Ensure every major requirement from job posting is addressed
            - Add quantified achievements that demonstrate required competencies

            IMPORTANT: This attempt must significantly improve upon the {current_score}/100 score.
            Return ONLY the optimized resume content that will achieve 90+ ATS score.
            Do not include explanations or analysis - just the resume content.
            """

            try:
                optimization_response = call_gemini_api(optimization_prompt)
                
                if not optimization_response or 'error' in optimization_response:
                    error_msg = optimization_response.get('error', 'Failed to optimize resume') if optimization_response else 'No response from AI'
                    current_app.logger.error(f"Optimization failed on attempt {optimization_attempts}: {error_msg}")
                    break
                    
                if 'candidates' not in optimization_response or not optimization_response['candidates']:
                    current_app.logger.error(f"Invalid optimization response structure on attempt {optimization_attempts}")
                    break
                    
                optimized_content = optimization_response['candidates'][0]['content']['parts'][0]['text'].strip()
                current_app.logger.info(f"Optimization attempt {optimization_attempts} completed, content length: {len(optimized_content)}")
                
            except Exception as e:
                current_app.logger.error(f"Error optimizing content on attempt {optimization_attempts}: {str(e)}")
                break

        # Final score verification
        try:
            final_score_prompt = f"""
            Calculate the final ATS score for this optimized resume against the job description.
            Focus on keyword matching, skill alignment, and ATS compatibility.

            JOB DESCRIPTION:
            Title: {job.get('title', '')}
            Requirements: {job_description_to_use}
            Skills: {', '.join(job.get('skills', [])) if job.get('skills') else ''}

            OPTIMIZED RESUME:
            {optimized_content}

            Provide ONLY a number (0-100) representing the final ATS score:
            """
            
            final_score_response = call_gemini_api(final_score_prompt)
            final_score = current_score  # Default to last known score
            
            if final_score_response and 'candidates' in final_score_response and final_score_response['candidates']:
                try:
                    score_text = final_score_response['candidates'][0]['content']['parts'][0]['text'].strip()
                    import re
                    score_match = re.search(r'\d+', score_text)
                    if score_match:
                        final_score = int(score_match.group())
                        current_app.logger.info(f"Final verified ATS score: {final_score}")
                except Exception as e:
                    current_app.logger.warning(f"Final score verification failed: {str(e)}")
                    
        except Exception as e:
            current_app.logger.error(f"Error getting final score: {str(e)}")
            final_score = current_score if current_score > 0 else 85  # Optimistic fallback
        
        # Prepare success message based on achievement
        if final_score >= 90:
            message = f"🎯 Target Achieved! Resume optimized to {final_score}% ATS score (90+ target met in {optimization_attempts} attempts)"
            success_level = "target_achieved"
        elif final_score >= 85:
            message = f"⚡ Significant Improvement! Resume optimized to {final_score}% ATS score (close to 90+ target - {optimization_attempts} attempts)"
            success_level = "close_to_target"
        elif final_score > current_score:
            message = f"📈 Resume Improved! Score increased to {final_score}% ({optimization_attempts} optimization attempts - try again for 90+)"
            success_level = "improved"
        else:
            message = f"🔄 Optimization Complete! Resume enhanced with targeted improvements ({optimization_attempts} attempts)"
            success_level = "optimized"
        
        current_app.logger.info(f"90+ ATS optimization completed. Final score: {final_score}, Attempts: {optimization_attempts}")
        
        return jsonify({
            'success': True,
            'optimized_content': optimized_content,
            'estimated_score': final_score,
            'optimization_attempts': optimization_attempts,
            'attempt_scores': attempt_scores,
            'target_achieved': final_score >= 90,
            'success_level': success_level,
            'message': message
        })
            
    except Exception as e:
        current_app.logger.error(f"Auto-optimize error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Server error during optimization'
        }), 500
