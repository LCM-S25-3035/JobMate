"""
Recruiter Routes for JobMate
Handles recruiter dashboard, job posting management, and candidate management
"""

from flask import render_template, redirect, url_for, request, jsonify, flash, current_app
from flask_login import login_required, current_user
from app.recruiter import bp
from app.models.user import User
from app.models.job_posting import JobPosting
from app.models.application import Application
from app import db
from datetime import datetime, timedelta
from app.ai_agents.salary_suggestion import get_salary_suggestion
from app.ai_agents.skills_suggestion import suggest_skills


# Removed duplicate dashboard route - using main.recruiter_dashboard instead


@bp.route('/jobs')
@login_required
def job_listings():
    """View all job postings for current recruiter"""
    if not current_user.is_recruiter():
        flash('Access denied. Recruiter access required.', 'error')
        return redirect(url_for('main.applicant_dashboard'))
    
    # Get recruiter's job postings
    jobs = JobPosting.query.filter_by(recruiter_id=current_user.id).order_by(
        JobPosting.created_at.desc()
    ).all()
    
    # Calculate statistics
    total_jobs = len(jobs)
    active_jobs = len([job for job in jobs if job.status == 'active'])
    total_applications = sum(job.application_count for job in jobs)
    
    stats = {
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'draft_jobs': len([job for job in jobs if job.status == 'draft']),
        'expired_jobs': len([job for job in jobs if job.is_expired]),
        'total_applications': total_applications
    }
    
    return render_template('recruiter/job_listings.html',
                         title='My Job Postings',
                         jobs=jobs,
                         stats=stats)


@bp.route('/jobs/create', methods=['GET', 'POST'])
@login_required
def create_job():
    """Create a new job posting"""
    if not current_user.is_recruiter():
        flash('Access denied. Recruiter access required.', 'error')
        return redirect(url_for('main.applicant_dashboard'))
    
    if request.method == 'POST':
        try:
            # Get form data
            title = request.form.get('title', '').strip()
            company_name = request.form.get('company_name', '').strip()
            description = request.form.get('description', '').strip()
            requirements = request.form.get('requirements', '').strip()
            location = request.form.get('location', '').strip()
            salary_min = request.form.get('salary_min', type=int)
            salary_max = request.form.get('salary_max', type=int)
            employment_type = request.form.get('employment_type', 'full_time')
            remote_type = request.form.get('remote_type', 'office')
            experience_level = request.form.get('experience_level', 'mid')
            
            # Basic validation
            if not all([title, company_name, description, location]):
                flash('Please fill in all required fields.', 'error')
                return render_template('recruiter/create_job.html', title='Create Job Posting')
            
            # Create job posting
            job = JobPosting(
                title=title,
                company_name=company_name,
                description=description,
                requirements=requirements,
                recruiter_id=current_user.id,
                location=location,
                city=location.split(',')[0].strip() if ',' in location else location,
                province='Ontario',  # Default for Ontario focus
                country='Canada',
                salary_min=salary_min,
                salary_max=salary_max,
                employment_type=employment_type,
                remote_type=remote_type,
                experience_level=experience_level,
                status='active'
            )
            
            db.session.add(job)
            db.session.commit()
            
            flash(f'Job posting "{title}" created successfully!', 'success')
            return redirect(url_for('recruiter.job_listings'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating job posting: {e}")
            flash('Error creating job posting. Please try again.', 'error')
    
    return render_template('recruiter/create_job.html', title='Create Job Posting')


@bp.route('/jobs/<int:job_id>')
@login_required
def view_job(job_id):
    """View specific job posting with applications"""
    if not current_user.is_recruiter():
        flash('Access denied. Recruiter access required.', 'error')
        return redirect(url_for('main.applicant_dashboard'))
    
    job = JobPosting.query.filter_by(id=job_id, recruiter_id=current_user.id).first()
    if not job:
        flash('Job posting not found.', 'error')
        return redirect(url_for('recruiter.job_listings'))
    
    # Get applications for this job
    applications = Application.query.filter_by(job_posting_id=job_id).order_by(
        Application.created_at.desc()
    ).all()
    
    # Calculate application statistics
    total_applications = len(applications)
    new_applications = len([app for app in applications if app.status == 'pending'])
    interviewed = len([app for app in applications if app.status == 'interview'])
    hired = len([app for app in applications if app.status == 'hired'])
    
    stats = {
        'total_applications': total_applications,
        'new_applications': new_applications,
        'interviewed': interviewed,
        'hired': hired,
        'rejection_rate': round((len([app for app in applications if app.status == 'rejected']) / total_applications * 100), 1) if total_applications > 0 else 0
    }
    
    return render_template('recruiter/view_job.html',
                         title=f'Job: {job.title}',
                         job=job,
                         applications=applications,
                         stats=stats)


@bp.route('/jobs/<int:job_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_job(job_id):
    """Edit an existing job posting"""
    if not current_user.is_recruiter():
        flash('Access denied. Recruiter access required.', 'error')
        return redirect(url_for('main.applicant_dashboard'))
    
    job = JobPosting.query.filter_by(id=job_id, recruiter_id=current_user.id).first()
    if not job:
        flash('Job posting not found.', 'error')
        return redirect(url_for('recruiter.job_listings'))
    
    if request.method == 'POST':
        try:
            # Update job posting
            job.title = request.form.get('title', '').strip()
            job.company_name = request.form.get('company_name', '').strip()
            job.description = request.form.get('description', '').strip()
            job.requirements = request.form.get('requirements', '').strip()
            job.location = request.form.get('location', '').strip()
            job.salary_min = request.form.get('salary_min', type=int)
            job.salary_max = request.form.get('salary_max', type=int)
            job.employment_type = request.form.get('employment_type', 'full_time')
            job.remote_type = request.form.get('remote_type', 'office')
            job.experience_level = request.form.get('experience_level', 'mid')
            job.status = request.form.get('status', 'active')
            job.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            flash(f'Job posting "{job.title}" updated successfully!', 'success')
            return redirect(url_for('recruiter.view_job', job_id=job.id))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating job posting: {e}")
            flash('Error updating job posting. Please try again.', 'error')
    
    return render_template('recruiter/edit_job.html', title=f'Edit: {job.title}', job=job)


@bp.route('/candidates')
@login_required
def candidates():
    """View all candidates who applied to recruiter's jobs"""
    if not current_user.is_recruiter():
        flash('Access denied. Recruiter access required.', 'error')
        return redirect(url_for('main.applicant_dashboard'))
    
    # Get all applications to recruiter's jobs
    recruiter_jobs = JobPosting.query.filter_by(recruiter_id=current_user.id).all()
    job_ids = [job.id for job in recruiter_jobs]
    
    applications = Application.query.filter(
        Application.job_posting_id.in_(job_ids)
    ).order_by(Application.created_at.desc()).all()
    
    # Group applications by candidate
    candidates = {}
    for app in applications:
        if app.user_id not in candidates:
            candidates[app.user_id] = {
                'user': User.query.get(app.user_id),
                'applications': [],
                'latest_application': app.created_at
            }
        candidates[app.user_id]['applications'].append(app)
    
    # Convert to list and sort by latest application
    candidates_list = list(candidates.values())
    candidates_list.sort(key=lambda x: x['latest_application'], reverse=True)
    
    return render_template('recruiter/candidates.html',
                         title='Candidates',
                         candidates=candidates_list,
                         total_candidates=len(candidates_list))


@bp.route('/analytics')
@login_required
def analytics():
    """Recruiter analytics dashboard"""
    if not current_user.is_recruiter():
        flash('Access denied. Recruiter access required.', 'error')
        return redirect(url_for('main.applicant_dashboard'))
    
    # Get recruiter's jobs
    jobs = JobPosting.query.filter_by(recruiter_id=current_user.id).all()
    job_ids = [job.id for job in jobs]
    
    # Get applications to recruiter's jobs
    applications = Application.query.filter(
        Application.job_posting_id.in_(job_ids)
    ).all()
    
    # Calculate analytics
    total_jobs = len(jobs)
    total_applications = len(applications)
    
    # Applications in last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_applications = [app for app in applications if app.created_at >= thirty_days_ago]
    
    # Application status breakdown
    status_counts = {}
    for app in applications:
        status_counts[app.status] = status_counts.get(app.status, 0) + 1
    
    # Most popular jobs (by application count)
    job_popularity = {}
    for app in applications:
        job_popularity[app.job_posting_id] = job_popularity.get(app.job_posting_id, 0) + 1
    
    # Top performing jobs
    top_jobs = []
    for job in jobs:
        app_count = job_popularity.get(job.id, 0)
        if app_count > 0:
            top_jobs.append({
                'job': job,
                'applications': app_count,
                'applications_per_day': round(app_count / max(1, (datetime.utcnow() - job.created_at).days), 1)
            })
    
    top_jobs.sort(key=lambda x: x['applications'], reverse=True)
    
    analytics_data = {
        'total_jobs': total_jobs,
        'active_jobs': len([job for job in jobs if job.status == 'active']),
        'total_applications': total_applications,
        'recent_applications': len(recent_applications),
        'status_breakdown': status_counts,
        'top_jobs': top_jobs[:5],  # Top 5 jobs
        'avg_applications_per_job': round(total_applications / max(1, total_jobs), 1),
        'conversion_rate': round(status_counts.get('hired', 0) / max(1, total_applications) * 100, 1)
    }
    
    return render_template('recruiter/analytics.html',
                         title='Analytics',
                         analytics=analytics_data)


# API Routes
@bp.route('/api/jobs/<int:job_id>/toggle-status', methods=['POST'])
@login_required
def toggle_job_status(job_id):
    """Toggle job posting status (active/paused)"""
    if not current_user.is_recruiter():
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    job = JobPosting.query.filter_by(id=job_id, recruiter_id=current_user.id).first()
    if not job:
        return jsonify({'success': False, 'message': 'Job not found'}), 404
    
    try:
        # Toggle between active and paused
        if job.status == 'active':
            job.status = 'paused'
            message = 'Job posting paused'
        else:
            job.status = 'active'
            message = 'Job posting activated'
        
        job.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': message,
            'new_status': job.status
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error toggling job status: {e}")
        return jsonify({
            'success': False,
            'message': 'Error updating job status'
        }), 500


@bp.route('/api/jobs/<int:job_id>/status', methods=['POST'])
@login_required
def update_job_status(job_id):
    """Update job posting to specific status"""
    if not current_user.is_recruiter():
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    job = JobPosting.query.filter_by(id=job_id, recruiter_id=current_user.id).first()
    if not job:
        return jsonify({'success': False, 'message': 'Job not found'}), 404
    
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        # Validate status
        valid_statuses = ['active', 'paused', 'closed']
        if new_status not in valid_statuses:
            return jsonify({
                'success': False, 
                'message': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
            }), 400
        
        old_status = job.status
        job.status = new_status
        job.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Job status changed from {old_status} to {new_status}',
            'old_status': old_status,
            'new_status': new_status
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating job status: {e}")
        return jsonify({
            'success': False,
            'message': 'Error updating job status'
        }), 500


@bp.route('/api/applications/<int:app_id>/update-status', methods=['POST'])
@login_required
def update_application_status(app_id):
    """Update application status"""
    if not current_user.is_recruiter():
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    # Verify this application belongs to recruiter's job
    application = Application.query.join(JobPosting).filter(
        Application.id == app_id,
        JobPosting.recruiter_id == current_user.id
    ).first()
    
    if not application:
        return jsonify({'success': False, 'message': 'Application not found'}), 404
    
    try:
        new_status = request.json.get('status')
        valid_statuses = ['pending', 'reviewed', 'interview', 'hired', 'rejected']
        
        if new_status not in valid_statuses:
            return jsonify({'success': False, 'message': 'Invalid status'}), 400
        
        application.status = new_status
        application.response_date = datetime.utcnow()
        application.response_received = True
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Application status updated to {new_status}',
            'new_status': new_status
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating application status: {e}")
        return jsonify({
            'success': False,
            'message': 'Error updating application status'
        }), 500


@bp.route('/api/salary-suggestion', methods=['GET'])
def api_salary_suggestion():
    title = request.args.get('title', '').strip()
    location = request.args.get('location', '').strip()
    experience_level = request.args.get('experience_level', '').strip()
    if not title or not location:
        return jsonify({'success': False, 'error': 'Missing title or location'}), 400
    suggestion = get_salary_suggestion(title, location, experience_level)
    if not suggestion:
        return jsonify({'success': True, 'salary_range': None, 'explanation': None})
    # AI-powered suggestion returns a dict with salary_range and explanation
    return jsonify({'success': True, 'salary_range': suggestion['salary_range'], 'explanation': suggestion.get('explanation')})

@bp.route('/api/skills-suggestion', methods=['GET'])
def api_skills_suggestion():
    """API endpoint for AI-powered skills suggestions based on job title"""
    title = request.args.get('title', '').strip()
    max_skills = request.args.get('max_skills', 10)
    
    if not title:
        return jsonify({'success': False, 'error': 'Missing job title'}), 400
    
    try:
        max_skills = int(max_skills)
        if max_skills <= 0 or max_skills > 20:
            max_skills = 15
    except (ValueError, TypeError):
        max_skills = 15
    
    suggested_skills = suggest_skills(title, max_skills)
    
    return jsonify({
        'success': True, 
        'skills': suggested_skills,
        'count': len(suggested_skills)
    })


@bp.route('/jobs/<int:job_id>', methods=['DELETE'])
@login_required
def delete_job(job_id):
    """Permanently delete a job posting and all associated data"""
    if not current_user.is_recruiter():
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    job = JobPosting.query.filter_by(id=job_id, recruiter_id=current_user.id).first()
    if not job:
        return jsonify({'success': False, 'message': 'Job not found'}), 404
    
    try:
        # Delete all applications for this job
        from app.models.application import Application
        Application.query.filter_by(job_posting_id=job_id).delete()
        
        # Delete the job posting
        db.session.delete(job)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Job posting and all associated data have been permanently deleted'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting job {job_id}: {e}")
        return jsonify({
            'success': False,
            'message': 'Error deleting job posting'
        }), 500