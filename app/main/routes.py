"""
Main Routes for JobMate
Landing page, dashboards, and core application routes
"""

from flask import render_template, redirect, url_for, request, jsonify
from flask_login import current_user, login_required
from app import db
from app.main import bp
from app.models.user import User
from app.models.application import Application
from app.models.job_posting import JobPosting
from datetime import datetime, timedelta


@bp.route('/')
def index():
    """Landing page"""
    # Redirect logged-in users to their dashboard
    if current_user.is_authenticated:
        if current_user.is_applicant():
            return redirect(url_for('main.applicant_dashboard'))
        else:
            return redirect(url_for('main.recruiter_dashboard'))
    
    return render_template('main/landing.html', title='JobMate - AI-Powered Job Matching')


@bp.route('/dashboard')
@login_required
def dashboard():
    """Generic dashboard redirect"""
    if current_user.is_applicant():
        return redirect(url_for('main.applicant_dashboard'))
    else:
        return redirect(url_for('main.recruiter_dashboard'))


@bp.route('/applicant/dashboard')
@login_required
def applicant_dashboard():
    """Applicant dashboard"""
    if not current_user.is_applicant():
        return redirect(url_for('main.recruiter_dashboard'))
    
    # Get user's active resume
    active_resume = current_user.get_active_resume()
    
    # Get recent applications (limit to 5 for dashboard)
    recent_applications = current_user.applications.order_by(
        Application.created_at.desc()
    ).limit(5).all()
    
    # Get job recommendations using the match module
    from app.models.job_posting import JobPosting
    from app.match.routes import calculate_job_match_score
    
    # Get active jobs and calculate match scores
    active_jobs = JobPosting.get_active_jobs(limit=10)
    job_matches = []
    
    if active_jobs and active_resume:
        for job in active_jobs:
            match_score = calculate_job_match_score(job, current_user, active_resume)
            if match_score > 30:  # Only show jobs with reasonable match
                job_matches.append({
                    'job': job,
                    'match_score': match_score
                })
    
    # Sort by match score and limit to top 5 for dashboard
    recommended_jobs = sorted(job_matches, key=lambda x: x['match_score'], reverse=True)[:5]
    
    # Calculate completion percentage
    completion_percentage = calculate_profile_completion(current_user)
    
    return render_template('dashboard/applicant.html',
                         title='Dashboard',
                         user=current_user,
                         active_resume=active_resume,
                         recent_applications=recent_applications,
                         recommended_jobs=recommended_jobs,
                         completion_percentage=completion_percentage)


@bp.route('/recruiter/dashboard')
@login_required
def recruiter_dashboard():
    """Recruiter dashboard"""
    if not current_user.is_recruiter():
        return redirect(url_for('main.applicant_dashboard'))
    
    # Get recruiter's job postings
    job_postings = current_user.job_postings.order_by(
        JobPosting.created_at.desc()
    ).limit(10).all()
    
    # Calculate statistics
    total_jobs = current_user.job_postings.count()
    active_jobs = current_user.job_postings.filter_by(status='active').count()
    
    # Get recent applications to recruiter's jobs
    job_ids = [job.id for job in current_user.job_postings.all()]
    recent_applications = []
    total_applications = 0
    new_applications = 0
    
    if job_ids:
        recent_applications = Application.query.filter(
            Application.job_posting_id.in_(job_ids)
        ).order_by(Application.created_at.desc()).limit(5).all()
        
        total_applications = Application.query.filter(
            Application.job_posting_id.in_(job_ids)
        ).count()
        
        # Applications from last 7 days
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        new_applications = Application.query.filter(
            Application.job_posting_id.in_(job_ids),
            Application.created_at >= seven_days_ago
        ).count()
    
    # Mock data for demonstration
    stats = {
        'active_jobs': active_jobs,
        'total_applications': total_applications,
        'new_applications': new_applications,
        'total_views': 1250,  # Mock data
        'interview_scheduled': 8  # Mock data
    }
    
    return render_template('dashboard/recruiter.html',
                         title='Recruiter Dashboard',
                         user=current_user,
                         job_postings=job_postings,
                         recent_applications=recent_applications,
                         current_date=datetime.now().strftime('%b %d'),
                         **stats)


@bp.route('/jobs')
@login_required
def browse_jobs():
    """Browse all active job postings for applicants"""
    # Get all active jobs posted by recruiters
    active_jobs = JobPosting.get_active_jobs(limit=50)
    
    # Get filter parameters
    location = request.args.get('location', '')
    job_type = request.args.get('job_type', '')
    remote_type = request.args.get('remote_type', '')
    
    # Apply filters if provided
    filtered_jobs = active_jobs
    if location:
        filtered_jobs = [job for job in filtered_jobs if location.lower() in (job.location or '').lower()]
    if job_type:
        filtered_jobs = [job for job in filtered_jobs if job.employment_type == job_type]
    if remote_type:
        filtered_jobs = [job for job in filtered_jobs if job.remote_type == remote_type]
    
    return render_template('jobs/browse.html',
                         title='Browse Jobs',
                         jobs=filtered_jobs,
                         total_jobs=len(filtered_jobs),
                         filters={
                             'location': location,
                             'job_type': job_type,
                             'remote_type': remote_type
                         })


@bp.route('/jobs/<int:job_id>')
def view_job(job_id):
    """View specific job posting details"""
    job = JobPosting.query.filter_by(id=job_id, status='active').first()
    if not job:
        flash('Job posting not found or no longer available.', 'error')
        return redirect(url_for('main.browse_jobs'))
    
    # Increment view count
    job.increment_view_count()
    
    return render_template('jobs/view.html',
                         title=f'{job.title} - {job.company_name}',
                         job=job)


@bp.route('/jobs/<int:job_id>/apply', methods=['GET', 'POST'])
@login_required
def apply_to_job(job_id):
    """Apply to a specific job posting"""
    from app.main.forms import JobApplicationForm
    from app.models.application import Application
    from datetime import datetime
    
    job = JobPosting.query.filter_by(id=job_id, status='active').first()
    if not job:
        flash('Job posting not found or no longer available.', 'error')
        return redirect(url_for('main.browse_jobs'))
    
    # Check if user already applied to this job
    existing_application = Application.query.filter_by(
        user_id=current_user.id,
        job_posting_id=job.id
    ).first()
    
    if existing_application:
        flash('You have already applied to this job.', 'warning')
        return redirect(url_for('main.view_job', job_id=job.id))
    
    form = JobApplicationForm()
    
    if form.validate_on_submit():
        try:
            # Create new application record
            application = Application(
                user_id=current_user.id,
                job_posting_id=job.id,
                company_name=job.company_name,
                job_title=job.title,
                job_location=job.location,
                cover_letter=form.cover_letter.data,
                notes=form.additional_notes.data if form.additional_notes.data else None,
                status='applied',
                application_method='manual',
                applied_at=datetime.utcnow(),
                remote_type=job.remote_type if hasattr(job, 'remote_type') else None
            )
            
            # Handle resume file if uploaded
            if form.resume_file.data:
                # For now, we'll just note that a resume was uploaded
                # In a full implementation, you'd save the file and store the path
                application.notes = (application.notes or '') + '\n[Resume uploaded with application]'
            
            # Save to database
            db.session.add(application)
            db.session.commit()
            
            print(f"Debug - Application created successfully with ID: {application.id}")
            flash(f'Application submitted successfully for {job.title}!', 'success')
            return redirect(url_for('main.view_job', job_id=job.id))
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creating application: {str(e)}")
            flash('There was an error submitting your application. Please try again.', 'error')
    else:
        if request.method == 'POST':
            print(f"Debug - Form validation failed: {form.errors}")
    
    return render_template('jobs/apply.html',
                         title=f'Apply for {job.title}',
                         job=job,
                         form=form)


@bp.route('/about')
def about():
    """About page"""
    return render_template('main/about.html', title='About JobMate')


@bp.route('/features')
def features():
    """Features page"""
    return render_template('main/features.html', title='Features')


@bp.route('/pricing')
def pricing():
    """Pricing page"""
    return render_template('main/pricing.html', title='Pricing')


@bp.route('/contact')
def contact():
    """Contact page"""
    return render_template('main/contact.html', title='Contact Us')


@bp.route('/privacy')
def privacy():
    """Privacy policy page"""
    return render_template('main/privacy.html', title='Privacy Policy')


@bp.route('/terms')
def terms():
    """Terms of service page"""
    return render_template('main/terms.html', title='Terms of Service')


# API Routes
@bp.route('/api/dashboard/stats')
@login_required
def dashboard_stats():
    """Get dashboard statistics for current user"""
    
    if current_user.is_applicant():
        stats = {
            'total_applications': current_user.applications.count(),
            'pending_applications': current_user.applications.filter_by(status='pending').count(),
            'interviews_scheduled': current_user.applications.filter_by(status='interview').count(),
            'profile_completion': calculate_profile_completion(current_user),
            'active_resume': current_user.get_active_resume() is not None
        }
    else:  # recruiter
        stats = {
            'total_job_postings': current_user.job_postings.count(),
            'active_job_postings': current_user.job_postings.filter_by(status='active').count(),
            'total_applications': 0,  # TODO: Calculate applications to recruiter's jobs
            'new_applications': 0,    # TODO: Calculate new applications this week
            'candidates_reviewed': 0  # TODO: Calculate reviewed candidates
        }
    
    return jsonify(stats)


@bp.route('/api/notifications')
@login_required
def notifications():
    """Get user notifications"""
    # TODO: Implement notifications system
    notifications = [
        {
            'id': 1,
            'type': 'info',
            'title': 'Welcome to JobMate!',
            'message': 'Complete your profile to get better job matches.',
            'created_at': '2024-01-01T10:00:00Z',
            'read': False
        }
    ]
    
    return jsonify(notifications)


@bp.route('/api/available-jobs')
@login_required
def available_jobs():
    """Get list of available job postings for ATS analysis"""
    try:
        # Get active job postings with basic info
        jobs = JobPosting.query.filter_by(status='active').order_by(
            JobPosting.created_at.desc()
        ).limit(20).all()
        
        jobs_data = []
        for job in jobs:
            jobs_data.append({
                'id': job.id,
                'title': job.title,
                'company_name': job.company_name,
                'location': job.location,
                'description': job.description[:200] if job.description else '',
                'experience_level': job.experience_level,
                'job_type': job.job_type,
                'created_at': job.created_at.isoformat() if job.created_at else None
            })
        
        return jsonify({'jobs': jobs_data})
        
    except Exception as e:
        return jsonify({'error': str(e), 'jobs': []}), 500


@bp.route('/api/search')
def search():
    """Global search endpoint"""
    query = request.args.get('q', '').strip()
    search_type = request.args.get('type', 'all')  # jobs, companies, candidates
    
    if not query:
        return jsonify({'results': []})
    
    results = []
    
    if search_type in ['all', 'jobs']:
        # TODO: Search jobs in MongoDB
        pass
    
    if search_type in ['all', 'companies']:
        # TODO: Search companies
        pass
    
    if current_user.is_authenticated and current_user.is_recruiter() and search_type in ['all', 'candidates']:
        # TODO: Search candidates (only for recruiters)
        pass
    
    return jsonify({'results': results, 'total': len(results)})


def calculate_profile_completion(user):
    """Calculate profile completion percentage"""
    completion_items = [
        user.first_name and user.last_name,
        user.email,
        user.phone,
        user.city and user.province,
        user.get_active_resume() is not None,
        user.job_preferences is not None if user.is_applicant() else True,
        user.is_verified
    ]
    
    completed = sum(1 for item in completion_items if item)
    total = len(completion_items)
    
    return int((completed / total) * 100) 