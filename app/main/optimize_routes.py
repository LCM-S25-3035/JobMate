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


# ========== DEPRECATED AUTO OPTIMIZE ROUTE ==========
# ATS optimization is now built into the regular tailor function
# The entire auto_optimize_resume function has been removed and integrated
# into the main tailor function for a unified user experience.
#
# Original function signature was:
# @bp.route('/auto_optimize_resume', methods=['POST'])
# @login_required  
# def auto_optimize_resume():
#     """Auto-optimize resume to achieve 90%+ ATS score using iterative targeted analysis"""
#     # Function implemented iterative ATS optimization to achieve 90+ scores
#     # This functionality is now built into generate_tailored_resume_with_strict_format()
#     pass
