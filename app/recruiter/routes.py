<<<<<<< Updated upstream
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
from app.recruiter.forms import CreateJobForm


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
    if not current_user.is_recruiter():
        flash('Access denied. Recruiter access required.', 'error')
        return redirect(url_for('main.applicant_dashboard'))

    form = CreateJobForm()

    if form.validate_on_submit():
        try:
            job = JobPosting(
                title=form.title.data,
                company_name=form.company_name.data,
                description=form.description.data,
                requirements=form.requirements.data,
                recruiter_id=current_user.id,
                location=form.location.data,
                city=form.location.data.split(',')[0].strip() if ',' in form.location.data else form.location.data,
                province='Ontario',
                country='Canada',
                salary_min=form.salary_min.data,
                salary_max=form.salary_max.data,
                employment_type=form.employment_type.data,
                work_setting=form.work_setting.data,
                experience_level=form.experience_level.data,
                status='active'
            )
            db.session.add(job)
            db.session.commit()
            flash(f'Job posting \"{form.title.data}\" created successfully!', 'success')
            return redirect(url_for('recruiter.job_listings'))
        except Exception as e:
            db.session.rollback()
            print("Exception occurred:", e)
            current_app.logger.error(f"Error creating job posting: {e}")
            flash('Error creating job posting. Please try again.', 'error')

    return render_template('recruiter/create_job.html', title='Create Job Posting', form=form)



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
            job.work_setting = request.form.get('work_setting', 'office')
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


@bp.route('/jobs/<int:job_id>/delete', methods=['POST'])
@login_required
def delete_job(job_id):
    """Delete a job posting"""
    if not current_user.is_recruiter():
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    job = JobPosting.query.filter_by(id=job_id, recruiter_id=current_user.id).first()
    if not job:
        return jsonify({'success': False, 'message': 'Job not found'}), 404
    
    try:
        job_title = job.title
        db.session.delete(job)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Job posting "{job_title}" deleted successfully.'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting job posting: {e}")
        return jsonify({
            'success': False,
            'message': 'Error deleting job posting.'
        }), 500


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
=======
"""
Recruiter Routes for JobMate
Handles recruiter dashboard, job posting management, and candidate management
"""

from flask import render_template, redirect, url_for, request, jsonify, flash, current_app
from flask_login import login_required, current_user
from app.recruiter import bp
from app.recruiter.forms import CreateJobForm
from app.models.user import User
from app.models.job_posting import JobPosting
from app.models.application import Application
from app import db
from datetime import datetime, timedelta


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
    """Create a new job posting using WTForms"""
    try:
        print(f"🔍 DEBUG: create_job route accessed - Method: {request.method}")
        
        if not current_user.is_recruiter():
            flash('Access denied. Recruiter access required.', 'error')
            return redirect(url_for('main.applicant_dashboard'))
        
        form = CreateJobForm()
        print(f"CSRF DEBUG 🔐 token: {form.csrf_token}")
        
        if form.validate_on_submit():
            print("✅ WTForms validation passed!")
            try:
                # Create job posting using form data
                job = JobPosting(
                    title=form.title.data,
                    company_name=form.company_name.data,
                    description=form.description.data,
                    requirements=form.requirements.data,
                    recruiter_id=current_user.id,
                    location=form.location.data,
                    city=form.location.data.split(',')[0].strip() if ',' in form.location.data else form.location.data,
                    province='Ontario',  # Default for Ontario focus
                    country='Canada',
                    salary_min=form.salary_min.data,
                    salary_max=form.salary_max.data,
                    employment_type=form.employment_type.data,
                    remote_type=form.remote_type.data,
                    experience_level=form.experience_level.data,
                    status='active'
                )
                
                db.session.add(job)
                db.session.commit()
                
                flash(f'Job posting "{form.title.data}" created successfully!', 'success')
                return redirect(url_for('recruiter.job_listings'))
                
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Error creating job posting: {e}")
                flash('Error creating job posting. Please try again.', 'error')
        else:
            print(f"❌ Form validation failed: {form.errors}")
    
    except Exception as outer_e:
        print(f"❌ Route error: {outer_e}")
        current_app.logger.error(f"Route error in create_job: {outer_e}")
        flash('An error occurred. Please try again.', 'error')
        form = CreateJobForm()  # Create a fresh form if there was an error
    
    return render_template('recruiter/create_job.html', title='Create Job Posting', form=form)
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
            job.remote_type = request.form.get('remote_type', 'onsite')
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


@bp.route('/jobs/<int:job_id>/delete', methods=['POST'])
@login_required
def delete_job(job_id):
    """Delete a job posting"""
    if not current_user.is_recruiter():
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    job = JobPosting.query.filter_by(id=job_id, recruiter_id=current_user.id).first()
    if not job:
        return jsonify({'success': False, 'message': 'Job not found'}), 404
    
    try:
        job_title = job.title
        db.session.delete(job)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Job posting "{job_title}" deleted successfully.'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting job posting: {e}")
        return jsonify({
            'success': False,
            'message': 'Error deleting job posting.'
        }), 500


@bp.route('/candidates')
@login_required
def candidates():
    """Redirect to hiring pipeline (legacy route)"""
    return redirect(url_for('recruiter.hiring_pipeline'))


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
        # Check if specific status is provided in request
        requested_status = request.json.get('status') if request.json else None
        
        if requested_status and requested_status in ['active', 'paused']:
            # Use the specific status provided
            job.status = requested_status
            message = f'Job posting {requested_status}'
        else:
            # Fallback to toggle behavior
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




@bp.route('/jobs/<int:job_id>/repost', methods=['POST'])
@login_required
def repost_job(job_id):
    """Repost a job (make it active again)"""
    if not current_user.is_recruiter():
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    job = JobPosting.query.filter_by(
        id=job_id, 
        recruiter_id=current_user.id
    ).first()
    
    if not job:
        return jsonify({'success': False, 'message': 'Job not found'}), 404
    
    try:
        # Set job as active and extend expiration
        job.status = 'active'
        job.updated_at = datetime.utcnow()
        job.published_at = datetime.utcnow()
        job.expires_at = datetime.utcnow() + timedelta(days=30)
        
        db.session.commit()
        
        flash('Job posting has been reposted successfully.', 'success')
        
        return jsonify({
            'success': True,
            'message': 'Job reposted successfully',
            'new_status': 'active'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error reposting job: {e}")
        return jsonify({
            'success': False,
            'message': 'Error reposting job'
        }), 500


@bp.route('/jobs/<int:job_id>/archive', methods=['POST'])
@login_required
def archive_job(job_id):
    """Archive a job posting"""
    if not current_user.is_recruiter():
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    job = JobPosting.query.filter_by(
        id=job_id, 
        recruiter_id=current_user.id
    ).first()
    
    if not job:
        return jsonify({'success': False, 'message': 'Job not found'}), 404
    
    try:
        # Use 'cancelled' status for archived jobs
        job.status = 'cancelled'
        job.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('Job posting has been archived successfully.', 'success')
        
        return jsonify({
            'success': True,
            'message': 'Job archived successfully',
            'new_status': 'cancelled'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error archiving job: {e}")
        return jsonify({
            'success': False,
            'message': 'Error archiving job'
        }), 500


@bp.route('/hiring-pipeline')
@bp.route('/hiring-pipeline/<int:job_id>')
@login_required
def hiring_pipeline(job_id=None):
    """Hiring pipeline - shows applications for all jobs or specific job"""
    if not current_user.is_recruiter():
        flash('Access denied. Recruiter access required.', 'error')
        return redirect(url_for('main.applicant_dashboard'))
    
    # Get recruiter's job postings
    job_ids = [job.id for job in current_user.job_postings.all()]
    
    if job_id:
        # Show applications for specific job
        job = JobPosting.query.filter_by(id=job_id, recruiter_id=current_user.id).first()
        if not job:
            flash('Job not found.', 'error')
            return redirect(url_for('recruiter.hiring_pipeline'))
        
        applications = Application.query.filter_by(job_posting_id=job_id).join(User).order_by(
            Application.created_at.desc()
        ).all()
        
        return render_template('recruiter/hiring_pipeline.html',
                             title=f'Hiring Pipeline - {job.title}',
                             applications=applications,
                             job=job,
                             single_job=True)
    else:
        # Show applications for all jobs
        applications = Application.query.filter(
            Application.job_posting_id.in_(job_ids)
        ).join(User).join(JobPosting).order_by(
            Application.created_at.desc()
        ).all()
        
        return render_template('recruiter/hiring_pipeline.html',
                             title='Hiring Pipeline',
                             applications=applications,
                             single_job=False)


@bp.route('/application/<int:application_id>/update-status', methods=['POST'])
@login_required
def update_application_status(application_id):
    """Update application status and notes"""
    if not current_user.is_recruiter():
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    application = Application.query.join(JobPosting).filter(
        Application.id == application_id,
        JobPosting.recruiter_id == current_user.id
    ).first()
    
    if not application:
        return jsonify({'success': False, 'message': 'Application not found'}), 404
    
    try:
        status = request.json.get('status')
        notes = request.json.get('notes', '')
        
        if status:
            application.status = status
        if notes is not None:
            application.notes = notes
        
        application.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Application updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating application: {e}")
        return jsonify({
            'success': False,
            'message': 'Error updating application'
>>>>>>> Stashed changes
        }), 500 