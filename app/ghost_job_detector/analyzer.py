"""
Ghost Job Analyzer

This module analyzes job listings to determine the likelihood
that a job posting is a "ghost job" - a job that isn't actually
available or is misleading in some way.
"""

import re
from datetime import datetime, timedelta

def analyze_job_listing(job):
    """
    Analyzes a job listing to determine if it might be a ghost job.
    
    Args:
        job (dict): The job document from MongoDB
        
    Returns:
        dict: Analysis result with percentage and reasons
    """
    score = 0
    reasons = []
    
    # Check for posting date (older jobs are more suspicious)
    posting_date = job.get('posted_date')
    if posting_date:
        try:
            if isinstance(posting_date, str):
                posting_date = datetime.fromisoformat(posting_date.replace('Z', '+00:00'))
            
            days_old = (datetime.utcnow() - posting_date).days
            if days_old > 90:
                score += 25
                reasons.append("Position has been open for more than 3 months")
            elif days_old > 60:
                score += 15
                reasons.append("Position has been open for more than 2 months")
        except (ValueError, TypeError):
            pass
    
    # Check for vague job description
    description = job.get('description', '')
    if isinstance(description, str):
        word_count = len(description.split())
        if word_count < 100:
            score += 20
            reasons.append("Vague or extremely short job description")
        
        # Check for generic buzzwords with little substance
        buzzword_pattern = r'\b(synergy|disrupt|ninja|rockstar|guru|wizard|unicorn)\b'
        buzzwords = re.findall(buzzword_pattern, description.lower())
        if len(buzzwords) > 3:
            score += 15
            reasons.append("Contains unusually high number of buzzwords")
    
    # Check for excessive requirements
    requirements = job.get('requirements', [])
    if isinstance(requirements, list) and len(requirements) > 15:
        score += 15
        reasons.append("Extremely high number of requirements")
    
    # Check for salary information
    salary_min = job.get('salary_min')
    salary_max = job.get('salary_max')
    if not salary_min and not salary_max:
        score += 10
        reasons.append("No salary information provided")
    
    # Check for company information
    company = job.get('company', {})
    if not company.get('name'):
        score += 15
        reasons.append("Missing company information")
    
    # Check for application method
    apply_url = job.get('apply_url')
    if not apply_url:
        score += 10
        reasons.append("No direct application link provided")
    
    # Check for reposting
    reposted = job.get('reposted', False)
    if reposted:
        score += 20
        reasons.append("Job has been reposted multiple times")
    
    # Cap the score at 100
    score = min(100, score)
    
    return {
        'percentage': score,
        'reasons': reasons
    }
