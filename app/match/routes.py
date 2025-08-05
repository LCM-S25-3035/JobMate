"""
Match Routes for JobMate
Handles job-to-candidate matching and AI-powered recommendations
"""

from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import current_user, login_required
from sqlalchemy import func, text
from app.match import bp
from app.models.user import User
from app.models.job_posting import JobPosting
from app.models.resume import Resume
from app.models.application import Application
from app.models.job_preference import JobPreference
from app import db
import re
from datetime import datetime, timedelta


@bp.route('/jobs')
@login_required
def recommended_jobs():
    """Show recommended jobs for current user"""
    if not current_user.is_applicant():
        flash('Only applicants can view job recommendations.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Get user preferences
    if current_user.job_preferences:
        preferences = current_user.job_preferences.first()
    else:
        preferences = None
    
    # Get user's primary resume for skills analysis
    primary_resume = current_user.resumes.filter_by(is_primary=True).first()
    
    # Base query for active job postings
    jobs_query = JobPosting.query.filter_by(status='active')
    
    # Apply location filtering if preferences exist
    if preferences and preferences.preferred_location:
        jobs_query = jobs_query.filter(
            JobPosting.location.ilike(f'%{preferences.preferred_location}%')
        )
    
    # Apply salary filtering if preferences exist
    if preferences and preferences.salary_min:
        jobs_query = jobs_query.filter(
            JobPosting.salary_max >= preferences.salary_min
        )
    
    # Get all matching jobs
    all_jobs = jobs_query.order_by(JobPosting.created_at.desc()).limit(50).all()
    
    # Calculate match scores and sort by relevance
    scored_jobs = []
    for job in all_jobs:
        score = calculate_job_match_score(job, current_user, primary_resume, preferences)
        scored_jobs.append({
            'job': job,
            'score': score,
            'match_percentage': min(100, score)
        })
    
    # Sort by match score descending
    scored_jobs.sort(key=lambda x: x['score'], reverse=True)
    
    # Take top 20 recommendations
    recommended_jobs = scored_jobs[:20]
    
    return render_template('match/recommended_jobs.html', 
                         title='Recommended Jobs',
                         recommended_jobs=recommended_jobs,
                         total_available=len(all_jobs))


@bp.route('/job/<int:job_id>/match-details')
@login_required
def job_match_details(job_id):
    """Show detailed match analysis for a specific job"""
    if not current_user.is_applicant():
        flash('Only applicants can view match details.', 'error')
        return redirect(url_for('main.dashboard'))
    
    job = JobPosting.query.get_or_404(job_id)
    
    # Only allow access to active jobs for applicants
    if job.status != 'active':
        flash('This job posting is no longer available.', 'warning')
        return redirect(url_for('match.recommended_jobs'))
    
    preferences = current_user.job_preferences.first()
    primary_resume = current_user.resumes.filter_by(is_primary=True).first()
    
    # Calculate detailed match analysis
    match_analysis = calculate_detailed_match_analysis(job, current_user, primary_resume, preferences)
    
    return render_template('match/job_match_details.html',
                         title=f'Match Analysis: {job.title}',
                         job=job,
                         analysis=match_analysis)


@bp.route('/update-preferences', methods=['GET', 'POST'])
@login_required
def update_preferences():
    """Update user job preferences for better matching"""
    if not current_user.is_applicant():
        flash('Only applicants can update preferences.', 'error')
        return redirect(url_for('main.dashboard'))
    
    preferences = current_user.job_preferences.first()
    if not preferences:
        preferences = JobPreference(user_id=current_user.id)
    
    if request.method == 'POST':
        # Update preferences from form
        preferences.job_types = request.form.get('job_types', '')
        preferences.preferred_location = request.form.get('preferred_location', '')
        preferences.remote_preference = request.form.get('remote_preference', 'no_preference')
        preferences.salary_min = int(request.form.get('salary_min', 0)) if request.form.get('salary_min') else None
        preferences.salary_max = int(request.form.get('salary_max', 0)) if request.form.get('salary_max') else None
        preferences.experience_level = request.form.get('experience_level', '')
        preferences.skills = request.form.get('skills', '')
        preferences.industries = request.form.get('industries', '')
        
        db.session.add(preferences)
        db.session.commit()
        
        flash('Job preferences updated successfully!', 'success')
        return redirect(url_for('match.recommended_jobs'))
    
    return render_template('match/update_preferences.html',
                         title='Update Job Preferences',
                         preferences=preferences)


@bp.route('/api/quick-match/<int:job_id>')
@login_required
def api_quick_match(job_id):
    """API endpoint for quick match score calculation"""
    if not current_user.is_applicant():
        return jsonify({'error': 'Unauthorized'}), 403
    
    job = JobPosting.query.get_or_404(job_id)
    
    # Only allow access to active jobs for applicants
    if job.status != 'active':
        return jsonify({'error': 'Job posting is no longer available'}), 404
    
    preferences = current_user.job_preferences.first()
    primary_resume = current_user.resumes.filter_by(is_primary=True).first()
    
    score = calculate_job_match_score(job, current_user, primary_resume, preferences)
    
    return jsonify({
        'job_id': job_id,
        'match_score': score,
        'match_percentage': min(100, score),
        'recommendation': get_match_recommendation(score)
    })


@bp.route('/discovery')
@login_required
def job_discovery():
    """Advanced job discovery with filters"""
    if not current_user.is_applicant():
        flash('Only applicants can use job discovery.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Get filter parameters
    location = request.args.get('location', '')
    job_type = request.args.get('job_type', '')
    experience_level = request.args.get('experience_level', '')
    salary_min = request.args.get('salary_min', type=int)
    remote = request.args.get('remote', '')
    keywords = request.args.get('keywords', '')
    
    # Build query
    jobs_query = JobPosting.query.filter_by(status='active')
    
    if location:
        jobs_query = jobs_query.filter(JobPosting.location.ilike(f'%{location}%'))
    
    if job_type:
        jobs_query = jobs_query.filter(JobPosting.job_type.ilike(f'%{job_type}%'))
    
    if experience_level:
        jobs_query = jobs_query.filter(JobPosting.experience_level.ilike(f'%{experience_level}%'))
    
    if salary_min:
        jobs_query = jobs_query.filter(JobPosting.salary_max >= salary_min)
    
    if remote == 'yes':
        jobs_query = jobs_query.filter(JobPosting.is_remote == True)
    elif remote == 'no':
        jobs_query = jobs_query.filter(JobPosting.is_remote == False)
    
    if keywords:
        search_filter = f'%{keywords}%'
        jobs_query = jobs_query.filter(
            db.or_(
                JobPosting.title.ilike(search_filter),
                JobPosting.description.ilike(search_filter),
                JobPosting.requirements.ilike(search_filter)
            )
        )
    
    # Get results with pagination
    page = request.args.get('page', 1, type=int)
    jobs = jobs_query.order_by(JobPosting.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('match/job_discovery.html',
                         title='Job Discovery',
                         jobs=jobs,
                         location=location,
                         job_type=job_type,
                         experience_level=experience_level,
                         salary_min=salary_min,
                         remote=remote,
                         keywords=keywords)


# Helper Functions

def calculate_job_match_score(job, user, resume=None, preferences=None):
    """Calculate job match score based on multiple factors"""
    score = 0.0
    
    # Base score
    score += 20
    
    # Location matching (30 points max)
    if preferences and preferences.preferred_location:
        if preferences.preferred_location.lower() in job.location.lower():
            score += 30
        elif any(word in job.location.lower() for word in preferences.preferred_location.lower().split()):
            score += 15
    
    # Salary matching (20 points max)
    if preferences and preferences.salary_min and job.salary_max:
        if job.salary_max >= preferences.salary_min:
            score += 20
        elif job.salary_max >= preferences.salary_min * 0.8:  # Within 20%
            score += 10
    
    # Skills matching (30 points max)
    if resume and resume.parsed_content:
        job_skills = extract_skills_from_text(job.description + " " + (job.requirements or ""))
        resume_skills = extract_skills_from_text(resume.parsed_content)
        
        if job_skills and resume_skills:
            matching_skills = job_skills.intersection(resume_skills)
            skill_match_ratio = len(matching_skills) / len(job_skills) if job_skills else 0
            score += skill_match_ratio * 30
    
    # Experience level matching (10 points max)
    if preferences and preferences.experience_level and job.experience_level:
        if preferences.experience_level.lower() == job.experience_level.lower():
            score += 10
        elif abs(get_experience_level_numeric(preferences.experience_level) - 
                get_experience_level_numeric(job.experience_level)) <= 1:
            score += 5
    
    # Job type matching (10 points max)
    if preferences and preferences.job_types:
        user_job_types = [t.strip().lower() for t in preferences.job_types.split(',')]
        if any(jt in job.title.lower() for jt in user_job_types):
            score += 10
    
    return min(100, score)


def calculate_detailed_match_analysis(job, user, resume=None, preferences=None):
    """Calculate detailed match analysis with breakdown"""
    analysis = {
        'overall_score': 0,
        'factors': {
            'location': {'score': 0, 'max': 30, 'details': ''},
            'salary': {'score': 0, 'max': 20, 'details': ''},
            'skills': {'score': 0, 'max': 30, 'details': ''},
            'experience': {'score': 0, 'max': 10, 'details': ''},
            'job_type': {'score': 0, 'max': 10, 'details': ''}
        },
        'recommendations': [],
        'missing_skills': [],
        'matching_skills': []
    }
    
    # Location analysis
    if preferences and preferences.preferred_location:
        if preferences.preferred_location.lower() in job.location.lower():
            analysis['factors']['location']['score'] = 30
            analysis['factors']['location']['details'] = 'Perfect location match'
        elif any(word in job.location.lower() for word in preferences.preferred_location.lower().split()):
            analysis['factors']['location']['score'] = 15
            analysis['factors']['location']['details'] = 'Partial location match'
        else:
            analysis['factors']['location']['details'] = 'Location mismatch'
    else:
        analysis['factors']['location']['details'] = 'No location preference set'
    
    # Salary analysis
    if preferences and preferences.salary_min and job.salary_max:
        if job.salary_max >= preferences.salary_min:
            analysis['factors']['salary']['score'] = 20
            analysis['factors']['salary']['details'] = 'Salary meets expectations'
        elif job.salary_max >= preferences.salary_min * 0.8:
            analysis['factors']['salary']['score'] = 10
            analysis['factors']['salary']['details'] = 'Salary slightly below expectations'
        else:
            analysis['factors']['salary']['details'] = 'Salary below expectations'
    else:
        analysis['factors']['salary']['details'] = 'No salary information available'
    
    # Skills analysis
    if resume and resume.parsed_content:
        job_skills = extract_skills_from_text(job.description + " " + (job.requirements or ""))
        resume_skills = extract_skills_from_text(resume.parsed_content)
        
        if job_skills and resume_skills:
            matching_skills = job_skills.intersection(resume_skills)
            missing_skills = job_skills - resume_skills
            
            analysis['matching_skills'] = list(matching_skills)
            analysis['missing_skills'] = list(missing_skills)
            
            skill_match_ratio = len(matching_skills) / len(job_skills)
            analysis['factors']['skills']['score'] = skill_match_ratio * 30
            analysis['factors']['skills']['details'] = f'{len(matching_skills)}/{len(job_skills)} required skills matched'
    
    # Calculate overall score
    total_score = sum(factor['score'] for factor in analysis['factors'].values())
    analysis['overall_score'] = min(100, total_score + 20)  # Base 20 points
    
    # Generate recommendations
    if analysis['factors']['skills']['score'] < 15:
        analysis['recommendations'].append('Consider developing the missing technical skills')
    if analysis['factors']['location']['score'] == 0 and preferences:
        analysis['recommendations'].append('Consider expanding your location preferences')
    if analysis['factors']['salary']['score'] == 0:
        analysis['recommendations'].append('Consider adjusting salary expectations or negotiating')
    
    return analysis


def extract_skills_from_text(text):
    """Extract technical skills from text"""
    if not text:
        return set()
    
    # Common technical skills
    tech_skills = {
        'python', 'java', 'javascript', 'typescript', 'react', 'node.js', 'angular', 'vue.js',
        'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'aws', 'azure', 'gcp', 'docker',
        'kubernetes', 'git', 'jenkins', 'terraform', 'ansible', 'linux', 'windows',
        'machine learning', 'ai', 'data science', 'tensorflow', 'pytorch', 'pandas',
        'numpy', 'scikit-learn', 'spark', 'hadoop', 'kafka', 'elasticsearch',
        'rest api', 'graphql', 'microservices', 'devops', 'ci/cd', 'agile', 'scrum'
    }
    
    text_lower = text.lower()
    found_skills = set()
    
    for skill in tech_skills:
        if skill in text_lower:
            found_skills.add(skill)
    
    return found_skills


def get_experience_level_numeric(level):
    """Convert experience level to numeric for comparison"""
    level_map = {
        'entry': 1,
        'junior': 1,
        'intermediate': 2,
        'mid': 2,
        'senior': 3,
        'lead': 4,
        'principal': 5,
        'director': 6
    }
    
    if not level:
        return 0
    
    level_lower = level.lower()
    for key, value in level_map.items():
        if key in level_lower:
            return value
    
    return 0


def get_match_recommendation(score):
    """Get recommendation text based on match score"""
    if score >= 80:
        return "Excellent match! Highly recommended to apply."
    elif score >= 60:
        return "Good match. Consider applying."
    elif score >= 40:
        return "Moderate match. Review requirements carefully."
    else:
        return "Low match. Consider developing additional skills."