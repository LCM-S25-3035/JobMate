from flask import render_template, flash, redirect, url_for, request, current_app, jsonify
from flask_login import current_user, login_required
from app import db
from app.autoapply import bp
from app.models.job_posting import JobPosting
from app.models.application import Application
from app.models.user import User
from datetime import datetime

@bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """Display the auto-apply dashboard with settings and history."""
    # Get user's auto-apply settings
    settings = current_user.get_autoapply_settings() if hasattr(current_user, 'get_autoapply_settings') else None
    
    # Get history of auto-applications
    applications = Application.query.filter_by(
        user_id=current_user.id,
        auto_applied=True
    ).order_by(Application.created_at.desc()).all()
    
    return render_template('autoapply/dashboard.html', 
                           settings=settings,
                           applications=applications,
                           title="Auto-Apply Dashboard")

@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Configure auto-apply settings."""
    if request.method == 'POST':
        # Get settings from form
        enabled = request.form.get('enabled') == 'on'
        max_daily = int(request.form.get('max_daily', 5))
        min_match_score = int(request.form.get('min_match_score', 80))
        
        # Save settings (implementation would depend on your model structure)
        current_user.update_autoapply_settings(
            enabled=enabled,
            max_daily=max_daily,
            min_match_score=min_match_score
        )
        
        flash('Auto-apply settings updated successfully!', 'success')
        return redirect(url_for('autoapply.dashboard'))
        
    # Display settings form
    settings = current_user.get_autoapply_settings() if hasattr(current_user, 'get_autoapply_settings') else {
        'enabled': False,
        'max_daily': 5,
        'min_match_score': 80
    }
    
    return render_template('autoapply/settings.html', 
                           settings=settings,
                           title="Auto-Apply Settings")

@bp.route('/autoapply/execute', methods=['POST'])
@login_required
def execute_autoapply():
    """Manually trigger the auto-apply process."""
    # This would typically be a background task, but for demo purposes:
    result = run_autoapply_for_user(current_user.id)
    
    flash(f'Auto-apply process completed! Applied to {result["applied_count"]} jobs.', 'success')
    return redirect(url_for('autoapply.dashboard'))

# Helper function that would typically be in a tasks.py file
def run_autoapply_for_user(user_id):
    """Run the auto-apply process for a specific user."""
    user = User.query.get(user_id)
    if not user:
        return {"success": False, "error": "User not found", "applied_count": 0}
    
    settings = user.get_autoapply_settings() if hasattr(user, 'get_autoapply_settings') else None
    if not settings or not settings.get('enabled'):
        return {"success": False, "error": "Auto-apply not enabled", "applied_count": 0}
    
    # Get recommended jobs that meet the minimum match score
    # This depends on your job matching implementation
    recommended_jobs = get_recommended_jobs_for_user(
        user_id, 
        min_score=settings.get('min_match_score', 80),
        limit=settings.get('max_daily', 5)
    )
    
    applied_count = 0
    for job in recommended_jobs:
        # Check if already applied
        existing = Application.query.filter_by(
            user_id=user_id,
            job_id=job.id
        ).first()
        
        if not existing:
            # Create application
            application = Application(
                user_id=user_id,
                job_id=job.id,
                status="applied",
                auto_applied=True,
                created_at=datetime.utcnow()
            )
            db.session.add(application)
            applied_count += 1
    
    db.session.commit()
    return {"success": True, "applied_count": applied_count}

# This would typically be in a separate module
def get_recommended_jobs_for_user(user_id, min_score=80, limit=5):
    """Get recommended jobs for a user with at least the minimum match score."""
    # This is a placeholder - your actual implementation will depend on 
    # how you're calculating job matches
    
    # Example implementation (modify based on your actual data model):
    # Assuming you have a function or method to get job matches with scores
    # from app.match.utils import get_job_matches
    # matches = get_job_matches(user_id)
    # filtered_matches = [m for m in matches if m.score >= min_score]
    # return [m.job for m in filtered_matches[:limit]]
    
    # For now, just return an empty list
    return []
