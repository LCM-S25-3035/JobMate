"""
Main Routes for JobMate
Landing page, dashboards, and core application routes
"""

from flask import render_template, redirect, url_for, request, jsonify, current_app, send_file, session, flash
from flask_login import current_user, login_required
from app.main import bp
from app import db
from app.models.user import User
from app.models.application import Application
from app.models.job_posting import JobPosting
from datetime import datetime, timedelta
from bson import ObjectId
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from app.ai_agents.gemini_utils import call_gemini_api
from app.models.resume import Resume
from werkzeug.utils import secure_filename
import os
import PyPDF2
import docx
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
import re


# --- MongoDB tailored resume helpers ---
def save_best_tailored_resume(mongo_db, user_id, job_id, ats_score, resume_text, cover_letter):
    collection = mongo_db.tailored_resumes
    existing = collection.find_one({"user_id": user_id, "job_id": job_id})
    # Ensure ats_score is treated as a number for comparison
    try:
        ats_score_num = float(ats_score) if ats_score is not None else 0
        existing_score = float(existing.get("ats_score", 0)) if existing else 0
        should_update = not existing or (ats_score_num > existing_score)
    except (ValueError, TypeError):
        # If conversion fails, always update
        should_update = True
        
    if should_update:
        collection.update_one(
            {"user_id": user_id, "job_id": job_id},
            {"$set": {
                "ats_score": ats_score,
                "resume_text": resume_text,
                "cover_letter": cover_letter,
                "updated_at": datetime.utcnow(),
                "created_at": existing.get("created_at", datetime.utcnow()) if existing else datetime.utcnow()
            }},
            upsert=True
        )

def get_best_tailored_resumes(mongo_db, user_id):
    return list(mongo_db.tailored_resumes.find({"user_id": user_id}))


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
    """Enhanced applicant dashboard with working profile completion"""
    if not current_user.is_applicant():
        return redirect(url_for('main.recruiter_dashboard'))
    
    try:
        # Calculate profile completion
        profile_data = calculate_profile_completion(current_user)
        
        # Get user's active resume
        active_resume = current_user.get_active_resume()
        
        # Get recent applications (limit to 5 for dashboard)
        recent_applications = current_user.applications.order_by(
            Application.created_at.desc()
        ).limit(5).all()
        
        # Get job recommendations using the match module
        from app.models.job_posting import JobPosting
        recommended_jobs = []
        
        # Get active jobs for recommendations
        active_jobs = JobPosting.get_active_jobs(limit=10)
        if active_jobs and active_resume:
            try:
                from app.match.routes import calculate_job_match_score
                job_matches = []
                
                for job in active_jobs:
                    match_score = calculate_job_match_score(job, current_user, active_resume)
                    if match_score > 30:  # Only show jobs with reasonable match
                        job_matches.append({
                            'job': job,
                            'match_score': match_score
                        })
                
                # Sort by match score and limit to top 5 for dashboard
                recommended_jobs = sorted(job_matches, key=lambda x: x['match_score'], reverse=True)[:5]
            except ImportError:
                # If match module is not available, continue without recommendations
                pass
        
        # Fetch MongoDB jobs (limit 6)
        mongo_jobs = []
        try:
            mongo_db = current_app.mongo_db
            mongo_jobs = list(mongo_db.jobs.find({}, {"_id": 1, "title": 1, "company": 1, "description": 1}).limit(6))
            # Convert ObjectId to string for template
            for job in mongo_jobs:
                job['_id'] = str(job['_id'])
        except:
            # If MongoDB is not available, continue without mongo jobs
            pass
        
        return render_template('dashboard/applicant.html',
                             title='Dashboard',
                             user=current_user,
                             completion_percentage=profile_data['percentage'],
                             profile_completion_items=profile_data['items'],
                             missing_profile_items=profile_data['missing_items'],
                             active_resume=active_resume,
                             recent_applications=recent_applications,
                             recommended_jobs=recommended_jobs,
                             mongo_jobs=mongo_jobs)
        
    except Exception as e:
        current_app.logger.error(f"Dashboard error: {str(e)}")
        
        # Provide safe fallbacks
        return render_template('dashboard/applicant.html',
                             title='Dashboard',
                             user=current_user,
                             completion_percentage=0,
                             profile_completion_items=[],
                             missing_profile_items=[],
                             active_resume=None,
                             recent_applications=[],
                             recommended_jobs=[],
                             mongo_jobs=[])


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


@bp.route('/profile')
@login_required
def profile():
    """Enhanced user profile page with better error handling"""
    try:
        current_app.logger.info(f"Loading profile for user {current_user.id}")
        
        # Calculate profile completion using the enhanced function
        try:
            profile_completion = calculate_profile_completion(current_user)
            current_app.logger.info(f"Profile completion calculated: {profile_completion['percentage']}%")
        except Exception as e:
            current_app.logger.error(f"Profile completion calculation error: {str(e)}")
            # Provide fallback data
            profile_completion = {
                'percentage': 0,
                'completed_fields': 0,
                'total_fields': 9,
                'missing_fields': ['Unable to calculate'],
                'filled_fields': []
            }
        
        # Get application stats (safe fallback)
        try:
            total_applications = current_user.applications.count() if hasattr(current_user, 'applications') else 0
            recent_applications = []
            if hasattr(current_user, 'applications'):
                recent_applications = current_user.applications.order_by(
                    Application.created_at.desc()
                ).limit(5).all()
        except Exception as e:
            current_app.logger.error(f"Application stats error: {str(e)}")
            total_applications = 0
            recent_applications = []
        
        profile_stats = {
            'total_applications': total_applications,
            'recent_applications': recent_applications,
            'profile_completion': profile_completion
        }
        
        # Debug log current user fields
        current_app.logger.info(f"User {current_user.id} profile data loading successful")
        
        # Try to render the enhanced profile template, with fallback
        try:
            return render_template('main/enhanced_profile.html', 
                                 user=current_user, 
                                 stats=profile_stats)
        except Exception as template_error:
            current_app.logger.error(f"Enhanced profile template error: {str(template_error)}")
            # Fallback to a simple profile page
            try:
                return render_template('main/simple_profile.html', 
                                     user=current_user, 
                                     stats=profile_stats)
            except Exception as fallback_error:
                current_app.logger.error(f"Simple profile template error: {str(fallback_error)}")
                # Last resort - show error page
                return render_template('main/profile_error.html', 
                                     user=current_user,
                                     error_message=str(template_error))
                             
    except Exception as e:
        current_app.logger.error(f"Profile page error: {str(e)}", exc_info=True)
        # Instead of redirecting, show a simple error page
        try:
            return render_template('main/profile_error.html', 
                                 user=current_user,
                                 error_message=str(e))
        except:
            # Ultimate fallback - just redirect to dashboard
            flash('Error loading profile', 'error')
            return redirect(url_for('main.applicant_dashboard'))


@bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Update user profile information"""
    try:
        current_app.logger.info(f"Updating profile for user {current_user.id}")
        
        # Get form data
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        phone = request.form.get('phone', '').strip()
        city = request.form.get('city', '').strip()
        experience_level = request.form.get('experience_level', '').strip()
        bio = request.form.get('bio', '').strip()
        skills = request.form.get('skills', '').strip()
        
        # Validate required fields
        if not first_name or not last_name:
            flash('First name and last name are required.', 'error')
            return redirect(url_for('main.profile'))
        
        # Update user fields
        current_user.first_name = first_name
        current_user.last_name = last_name
        current_user.phone = phone if phone else None
        current_user.city = city if city else None
        current_user.experience_level = experience_level if experience_level != 'not_specified' else None
        current_user.bio = bio if bio else None
        current_user.skills = skills if skills else None
        
        # Commit changes
        db.session.commit()
        
        current_app.logger.info(f"Profile updated successfully for user {current_user.id}")
        flash('Profile updated successfully!', 'success')
        
    except Exception as e:
        current_app.logger.error(f"Error updating profile for user {current_user.id}: {str(e)}")
        db.session.rollback()
        flash('Error updating profile. Please try again.', 'error')
    
    return redirect(url_for('main.profile'))


@bp.route('/profile/upload-picture', methods=['POST'])
@login_required 
def upload_profile_picture():
    """Upload and update user profile picture"""
    try:
        if 'profile_picture' not in request.files:
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        file = request.files['profile_picture']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # File validation
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({'success': False, 'error': 'Invalid file type. Use PNG, JPG, JPEG, or GIF'}), 400
        
        # Check file size (5MB limit)
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > 5 * 1024 * 1024:  # 5MB
            return jsonify({'success': False, 'error': 'File too large. Maximum size is 5MB'}), 400
        
        # Generate secure filename
        import os
        from datetime import datetime
        
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"profile_{current_user.id}_{timestamp}_{filename}"
        
        # Create upload directory
        upload_dir = os.path.join(current_app.static_folder, 'uploads', 'profiles')
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        # Update user profile picture path
        if hasattr(current_user, 'profile_picture'):
            current_user.profile_picture = f'uploads/profiles/{filename}'
        if hasattr(current_user, 'updated_at'):
            current_user.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        current_app.logger.info(f"Profile picture updated for user {current_user.id}")
        
        return jsonify({
            'success': True,
            'message': 'Profile picture updated successfully!',
            'picture_url': url_for('static', filename=f'uploads/profiles/{filename}')
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Profile picture upload error: {str(e)}")
        return jsonify({'success': False, 'error': 'Error uploading profile picture'}), 500


@bp.route('/profile/delete-picture', methods=['POST'])
@login_required
def delete_profile_picture():
    """Delete user profile picture"""
    try:
        if hasattr(current_user, 'profile_picture') and current_user.profile_picture:
            # Delete the file from filesystem
            try:
                import os
                old_path = os.path.join(current_app.static_folder, current_user.profile_picture)
                if os.path.exists(old_path):
                    os.remove(old_path)
            except Exception as e:
                current_app.logger.warning(f"Could not delete old profile picture file: {e}")
            
            # Clear from database
            current_user.profile_picture = None
            if hasattr(current_user, 'updated_at'):
                current_user.updated_at = datetime.utcnow()
            
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Profile picture deleted successfully!'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Profile picture delete error: {str(e)}")
        return jsonify({'success': False, 'error': 'Error deleting profile picture'}), 500


@bp.route('/profile/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    try:
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not all([current_password, new_password, confirm_password]):
            flash('All password fields are required', 'error')
            return redirect(url_for('main.profile'))
        
        # Verify current password
        if not current_user.check_password(current_password):
            flash('Current password is incorrect', 'error')
            return redirect(url_for('main.profile'))
        
        # Validate new password
        if len(new_password) < 8:
            flash('New password must be at least 8 characters long', 'error')
            return redirect(url_for('main.profile'))
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'error')
            return redirect(url_for('main.profile'))
        
        # Update password
        current_user.set_password(new_password)
        if hasattr(current_user, 'updated_at'):
            current_user.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        current_app.logger.info(f"Password changed for user {current_user.id}")
        flash('Password changed successfully! 🔒', 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Password change error: {str(e)}")
        flash('Error changing password. Please try again.', 'error')
    
    return redirect(url_for('main.profile'))


@bp.route('/profile/update-social', methods=['POST'])
@login_required
def update_social_links():
    """Update user social media links"""
    try:
        linkedin_url = request.form.get('linkedin_url', '').strip()
        github_url = request.form.get('github_url', '').strip()
        portfolio_url = request.form.get('portfolio_url', '').strip()
        
        # Basic URL validation
        def validate_url(url, platform):
            if not url:
                return None
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Platform-specific validation
            if platform == 'linkedin' and 'linkedin.com' not in url:
                return None
            elif platform == 'github' and 'github.com' not in url:
                return None
            
            return url
        
        # Validate and update URLs
        if hasattr(current_user, 'linkedin_url'):
            current_user.linkedin_url = validate_url(linkedin_url, 'linkedin')
        if hasattr(current_user, 'github_url'):
            current_user.github_url = validate_url(github_url, 'github')
        if hasattr(current_user, 'portfolio_url'):
            current_user.portfolio_url = validate_url(portfolio_url, 'portfolio')
        
        if hasattr(current_user, 'updated_at'):
            current_user.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        current_app.logger.info(f"Social links updated for user {current_user.id}")
        flash('Social media links updated successfully! 🔗', 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Social links update error: {str(e)}")
        flash('Error updating social media links. Please try again.', 'error')
    
    return redirect(url_for('main.profile'))


@bp.route('/update_profile', methods=['POST'])
@login_required
def update_profile_legacy():
    """Handle profile update form submission with detailed logging"""
    
    try:
        # Log form data received
        current_app.logger.info(f"=== Profile Update for User {current_user.id} ===")
        current_app.logger.info(f"Form data received: {dict(request.form)}")
        
        # Get form data
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        phone = request.form.get('phone', '').strip()
        city = request.form.get('city', '').strip()
        bio = request.form.get('bio', '').strip()
        experience_level = request.form.get('experience_level', '').strip()
        skills = request.form.get('skills', '').strip()
        
        # Log what we're about to save
        current_app.logger.info("Data to be saved:")
        current_app.logger.info(f"  first_name: '{first_name}' (length: {len(first_name)})")
        current_app.logger.info(f"  last_name: '{last_name}' (length: {len(last_name)})")
        current_app.logger.info(f"  phone: '{phone}' (length: {len(phone)})")
        current_app.logger.info(f"  city: '{city}' (length: {len(city)})")
        current_app.logger.info(f"  bio: '{bio}' (length: {len(bio)})")
        current_app.logger.info(f"  experience_level: '{experience_level}' (length: {len(experience_level)})")
        current_app.logger.info(f"  skills: '{skills}' (length: {len(skills)})")
        
        # Update user fields
        current_user.first_name = first_name if first_name else None
        current_user.last_name = last_name if last_name else None
        current_user.phone = phone if phone else None
        current_user.city = city if city else None
        current_user.bio = bio if bio else None
        current_user.experience_level = experience_level if experience_level else None
        current_user.skills = skills if skills else None
        
        # Save to database
        db.session.commit()
        
        # Log what was actually saved
        current_app.logger.info("After database commit:")
        current_app.logger.info(f"  current_user.first_name: '{current_user.first_name}'")
        current_app.logger.info(f"  current_user.last_name: '{current_user.last_name}'")
        current_app.logger.info(f"  current_user.phone: '{current_user.phone}'")
        current_app.logger.info(f"  current_user.city: '{current_user.city}'")
        current_app.logger.info(f"  current_user.bio: '{current_user.bio}'")
        current_app.logger.info(f"  current_user.experience_level: '{current_user.experience_level}'")
        current_app.logger.info(f"  current_user.skills: '{current_user.skills}'")
        
        # Store timestamp for debugging
        session['last_profile_update'] = datetime.now().isoformat()
        
        # Calculate completion after save
        profile_data = calculate_profile_completion(current_user)
        current_app.logger.info(f"Profile completion after save: {profile_data['percentage']}%")
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.profile'))
        
    except Exception as e:
        current_app.logger.error(f"Profile update error: {str(e)}", exc_info=True)
        db.session.rollback()
        flash('Error updating profile. Please try again.', 'error')
        return redirect(url_for('main.profile'))


@bp.route('/profile/debug')
@login_required
def profile_debug():
    """Debug route to check user profile data"""
    try:
        user_data = {
            'id': current_user.id,
            'email': current_user.email,
            'first_name': getattr(current_user, 'first_name', None),
            'last_name': getattr(current_user, 'last_name', None),
            'phone': getattr(current_user, 'phone', None),
            'city': getattr(current_user, 'city', None),
            'bio': getattr(current_user, 'bio', None),
            'skills': getattr(current_user, 'skills', None),
            'experience_level': getattr(current_user, 'experience_level', None),
            'profile_picture': getattr(current_user, 'profile_picture', None),
        }
        
        return jsonify({
            'user_data': user_data,
            'data_types': {k: str(type(v)) for k, v in user_data.items()},
            'non_empty_fields': [k for k, v in user_data.items() if v and str(v).strip()],
            'empty_fields': [k for k, v in user_data.items() if not v or not str(v).strip()]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/debug/profile')
@login_required
def debug_profile():
    """Debug route to check profile completion calculation"""
    
    profile_data = calculate_profile_completion(current_user)
    
    debug_info = {
        'user_id': str(current_user.id),
        'user_email': current_user.email,
        'completion_percentage': profile_data['percentage'],
        'completed_items': profile_data['completed'],
        'total_items': profile_data['total'],
        'all_items': profile_data['items'],
        'missing_items': profile_data['missing_items'],
        'user_attributes': {
            'first_name': getattr(current_user, 'first_name', 'NOT_SET'),
            'last_name': getattr(current_user, 'last_name', 'NOT_SET'),
            'phone': getattr(current_user, 'phone', 'NOT_SET'),
            'city': getattr(current_user, 'city', 'NOT_SET'),
            'bio': getattr(current_user, 'bio', 'NOT_SET'),
            'skills': getattr(current_user, 'skills', 'NOT_SET'),
            'experience_level': getattr(current_user, 'experience_level', 'NOT_SET')
        }
    }
    
    return jsonify(debug_info)


@bp.route('/applications')
@login_required
def applications():
    """User applications page"""
    
    # Get all applications for the current user
    user_applications = current_user.applications.order_by(
        Application.created_at.desc()
    ).all()
    
    return render_template('main/applications.html',
                         title='My Applications',
                         applications=user_applications)


@bp.route('/debug/routes')
def debug_routes():
    """Debug route to check which routes are available"""
    from flask import current_app
    
    routes_info = []
    for rule in current_app.url_map.iter_rules():
        if rule.endpoint.startswith('main.'):
            routes_info.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'rule': str(rule)
            })
    
    return jsonify({
        'available_main_routes': routes_info,
        'looking_for': [
            'main.profile',
            'main.applications'
        ]
    })


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


@bp.route('/mongo-test')
def mongo_test():
    """Test MongoDB connection and show job count and some job details"""
    mongo_db = current_app.mongo_db
    count = mongo_db.jobs.count_documents({})
    # Fetch up to 5 job documents, only show _id and title if available
    jobs = list(mongo_db.jobs.find({}, {"_id": 1, "title": 1}).limit(5))
    job_list = "<ul>" + "".join([
        f"<li>{str(job.get('_id'))}: {job.get('title', '(no title)')}</li>" for job in jobs
    ]) + "</ul>" if jobs else "<p>No jobs found.</p>"
    return f"Job count in MongoDB: {count}<br>Sample jobs:{job_list}"


@bp.route('/mongo-jobs')
@login_required
def mongo_jobs():
    """Show jobs from MongoDB for tailoring resume/cover letter"""
    mongo_db = current_app.mongo_db
    jobs = list(mongo_db.jobs.find({}, {"_id": 1, "title": 1, "company": 1, "description": 1}))
    return render_template('mongo_jobs.html', jobs=jobs)


def extract_text_from_file(file_path, file_ext):
    if file_ext == '.pdf':
        text = ''
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ''
        return text
    elif file_ext == '.docx':
        doc = docx.Document(file_path)
        return '\n'.join([para.text for para in doc.paragraphs])
    elif file_ext == '.txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        raise ValueError('Unsupported file type')


def postprocess_tailored_resume_output(ai_result, user_resume_sections=None):
    """
    Post-process and validate the AI output for tailored resume.
    - Ensures all required sections are present.
    - Fixes/corrects LinkedIn/contact fields.
    - Deduplicates and merges with user data if needed.
    - Cleans up formatting and section order.
    """
    import re
    required_sections = ["Summary", "Skills", "Experience", "Education"]
    resume_text = ai_result.get("tailored_resume", "")
    # Parse into sections
    def parse_sections(text):
        section_pattern = re.compile(r"^([A-Za-z &]+):$", re.MULTILINE)
        sections = {}
        last = None
        for line in text.splitlines():
            m = section_pattern.match(line.strip())
            if m:
                last = m.group(1).strip()
                sections[last] = []
            elif last:
                sections[last].append(line)
        return sections
    ai_sections = parse_sections(resume_text)
    # Merge with user resume if provided
    if user_resume_sections:
        for sec in required_sections:
            if sec not in ai_sections and sec.upper() in user_resume_sections:
                ai_sections[sec] = user_resume_sections[sec.upper()]
    # Ensure all required sections exist
    for sec in required_sections:
        if sec not in ai_sections:
            ai_sections[sec] = ["(Not provided)"]
    # Fix LinkedIn/contact fields in header
    header_lines = []
    for k in ["Name", "Contact", "Location"]:
        found = False
        for line in resume_text.splitlines():
            if line.strip().lower().startswith(f"{k.lower()}:"):
                val = line.split(":", 1)[-1].strip()
                if k == "Contact":
                    # Try to fix LinkedIn if missing protocol
                    val = re.sub(r"(linkedin\\.com/[^ |]+)", r"https://\\1", val)
                header_lines.append(f"{k}: {val}")
                found = True
                break
        if not found:
            header_lines.append(f"{k}: (Not provided)")
    # Rebuild resume text in canonical order
    section_order = ["Summary", "Skills", "Experience", "Education"] + [k for k in ai_sections if k not in required_sections]
    rebuilt = []
    rebuilt.append("---")
    rebuilt.extend(header_lines)
    rebuilt.append("")
    for sec in section_order:
        rebuilt.append(f"{sec}:")
        rebuilt.extend([l for l in ai_sections[sec] if l.strip()])
        rebuilt.append("")
    rebuilt.append("---")
    ai_result["tailored_resume"] = "\n".join(rebuilt)
    return ai_result


@bp.route('/tailor/<job_id>', methods=['GET', 'POST'])
@login_required
def tailor_resume(job_id):
    """Tailor resume or cover letter for a specific job using Gemini AI"""
    mongo_db = current_app.mongo_db
    job = mongo_db.jobs.find_one({"_id": ObjectId(job_id)})
    if not job:
        return "Job not found", 404

    tailored_result = None
    ats_score = None
    error = None
    resume_text = None
    
    # Get application URL from job data using the correct field name
    application_url = job.get('job_url_direct') or job.get('application_url') or job.get('company_website')
    application_email = job.get('email') or job.get('application_email') or job.get('contact_email')

    if request.method == 'POST':
        # Handle file upload
        if 'resume_file' not in request.files or request.files['resume_file'].filename == '':
            error = 'Please upload a resume file.'
        else:
            resume_file = request.files['resume_file']
            filename = secure_filename(resume_file.filename)
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext not in ['.pdf', '.docx', '.txt']:
                error = 'Unsupported file type. Please upload PDF, DOCX, or TXT.'
            else:
                temp_path = os.path.join('/tmp', filename)
                resume_file.save(temp_path)
                try:
                    resume_text = extract_text_from_file(temp_path, file_ext)
                    session['user_resume_text'] = resume_text  # Save user resume text for later PDF export
                except Exception as e:
                    error = f'Failed to extract text from resume: {e}'
                finally:
                    os.remove(temp_path)

        if resume_text and not error:
            # Prepare prompt for Gemini
            prompt = f"""
# RESUME TAILORING TASK

You are an expert ATS optimization specialist and resume writer with deep expertise in the tech sector. Your task is to tailor the candidate's resume to maximize ATS match score and appeal to hiring managers for the specific job description.

## JOB DESCRIPTION
```
{job.get('description', '')}
```

## ORIGINAL RESUME
```
{resume_text}
```

## TAILORING INSTRUCTIONS

1. MAINTAIN ACCURACY: Never fabricate experience, education, or skills not mentioned in the original resume.

2. KEYWORD OPTIMIZATION:
   - Identify primary and secondary keywords from the job description
   - Naturally integrate these keywords into appropriate sections of the resume
   - Match phrasing used in the job description where appropriate
   - Ensure keyword density is optimized but not excessive (aim for 5-8 exact matches per key requirement)
   - Focus especially on technical skills, tools, and methodologies mentioned in the job

3. FORMATTING & STRUCTURE:
   - Use clean, ATS-friendly formatting
   - Prioritize relevant experience and skills based on job requirements
   - Use standard section headings that ATS systems recognize
   - Maintain chronological order within sections
   - Use bullet points for readability
   - Format the resume using the specified structure below

4. CONTENT ENHANCEMENT:
   - Transform generic statements into achievement-focused bullets
   - For EACH job experience, include EXACTLY 5 bullet points - no more, no less
   - Each bullet point MUST include metrics (numbers, percentages, dollar amounts) and demonstrate clear impact
   - Use strong action verbs at the beginning of bullet points (e.g., Increased, Developed, Implemented)
   - Cover different aspects in the 5 bullets: technical skills, leadership, problem-solving, collaboration, and quantifiable business impact
   - Organize the Skills section with clear subheadings (Programming Languages, Frameworks & Libraries, etc.)
   - Under each skill subheading, list specific skills separated by commas (not as bullet points)
   - Match skills specifically to those mentioned in the job description, prioritizing exact keyword matches
   - Highlight transferable skills that match the job requirements
   - Emphasize Ontario tech sector experience if available

## REQUIRED OUTPUT FORMAT
Format the tailored resume as plain text in the following structure:

---
Name: <Full Name>
Contact: <Email> | <Phone> | <LinkedIn>
Location: <City, Province>

Summary:
<Professional summary paragraph highlighting key qualifications relevant to job>

Skills:
Programming Languages: <List key programming languages from resume that match job requirements>
Frameworks & Libraries: <List relevant frameworks and libraries that match job requirements>
Tools & Technologies: <List relevant tools, platforms, and technologies from resume>
Cloud & Infrastructure: <List cloud platforms (AWS, Azure, GCP) and infrastructure tools (Terraform, Kubernetes) that match job requirements>
Databases & Storage: <List databases (SQL, NoSQL, PostgreSQL, MongoDB) and data storage solutions from resume>
Domain Knowledge: <List industry-specific skills and knowledge areas>
Soft Skills: <List 3-5 most relevant soft skills for the position>

Experience:
<Company Name> | <Job Title> | <Start Date> - <End Date>
- <Quantified achievement with specific metrics (e.g., "Increased application performance by 40% through database optimization")>
- <Technical achievement demonstrating skills required in job posting with measurable outcome>
- <Leadership or collaborative achievement showing teamwork with quantifiable results>
- <Problem-solving achievement with clear business impact and metrics>
- <Innovation or project accomplishment directly relevant to job requirements with measurable success>

# REPEAT THE ABOVE FORMAT WITH EXACTLY 5 BULLET POINTS FOR EACH JOB EXPERIENCE

Education:
<Degree> | <Institution> | <Graduation Year>

---

## OUTPUT REQUIREMENTS

Provide your response in JSON format with the following structure:

```json
{{
  "tailored_resume": "The complete tailored resume text with appropriate formatting",
  "cover_letter": "A matching cover letter highlighting key qualifications for this role",
  "ats_score": "A number between 0-100 representing the estimated ATS match score",
  "suggestions": [
    {{
      "area": "Specific section or aspect of the resume",
      "suggestion": "Detailed actionable suggestion to further improve the resume"
    }}
    // Include 5-8 specific suggestions
  ]
}}
```

For the suggestions, focus on:
1. Areas where keywords could be better integrated
2. Achievements that could be better quantified
3. Skills that should be emphasized based on the job
4. Format improvements for ATS optimization
5. Section ordering or content prioritization

Be specific and actionable with each suggestion.
"""
            gemini_response = call_gemini_api(prompt)
            import json
            if 'candidates' in gemini_response:
                try:
                    content = gemini_response['candidates'][0]['content']['parts'][0]['text']
                    # Try to parse as JSON, but if it fails, attempt to extract JSON from text
                    try:
                        result = json.loads(content)
                        tailored_result = result
                        # Ensure ats_score is a number
                        ats_score_raw = result.get('ats_score')
                        if isinstance(ats_score_raw, str):
                            # Try to extract numeric value if it's a string like "85/100" or just "85"
                            ats_score_match = re.search(r'(\d+)', ats_score_raw)
                            ats_score = int(ats_score_match.group(1)) if ats_score_match else None
                        else:
                            # Keep as is if it's already a number
                            ats_score = ats_score_raw
                    except Exception as e:
                        import re
                        match = re.search(r'\{.*\}', content, re.DOTALL)
                        if match:
                            try:
                                result = json.loads(match.group(0))
                                tailored_result = result
                                # Ensure ats_score is a number
                                ats_score_raw = result.get('ats_score')
                                if isinstance(ats_score_raw, str):
                                    # Try to extract numeric value if it's a string like "85/100" or just "85"
                                    ats_score_match = re.search(r'(\d+)', ats_score_raw)
                                    ats_score = int(ats_score_match.group(1)) if ats_score_match else None
                                else:
                                    # Keep as is if it's already a number
                                    ats_score = ats_score_raw
                            except Exception as e2:
                                error = f"Failed to parse extracted JSON: {e2}. Raw response: {content}"
                        else:
                            error = f"Failed to parse Gemini response as JSON: {e}. Raw response: {content}"
                except Exception as e:
                    error = f"Failed to extract Gemini response: {e}"
            else:
                error = gemini_response.get('error', 'Unknown error from Gemini API')

            # --- Post-process tailored resume output ---
            if tailored_result:
                user_sections = extract_resume_sections(resume_text) if resume_text else None
                tailored_result = postprocess_tailored_resume_output(tailored_result, user_sections)
                # Get updated ATS score and ensure it's numeric
                ats_score_raw = tailored_result.get('ats_score')
                if isinstance(ats_score_raw, str):
                    # Try to extract numeric value if it's a string like "85/100" or just "85"
                    ats_score_match = re.search(r'(\d+)', ats_score_raw)
                    ats_score = int(ats_score_match.group(1)) if ats_score_match else None
                else:
                    # Keep as is if it's already a number
                    ats_score = ats_score_raw

            # --- Save best tailored resume in MongoDB ---
            if tailored_result and ats_score is not None:
                save_best_tailored_resume(
                    mongo_db,
                    str(current_user.id),
                    str(job_id),
                    ats_score,
                    tailored_result.get('tailored_resume', ''),
                    tailored_result.get('cover_letter', '')
                )

    return render_template(
        'tailor.html', 
        job=job,
        tailored_result=tailored_result, 
        ats_score=ats_score, 
        error=error, 
        user_resume_text=resume_text if resume_text else None,
        application_url=application_url,
        application_email=application_email
    )


@bp.route('/download-tailored/<job_id>/<doc_type>', methods=['POST'])
@login_required
def download_tailored(job_id, doc_type):
    """Download tailored resume or cover letter as a PDF file with improved formatting"""
    tailored_resume = request.form.get('tailored_resume')
    cover_letter = request.form.get('cover_letter')
    if doc_type == 'resume':
        content = tailored_resume or ''
        filename = f'tailored_resume_{job_id}.pdf'
    elif doc_type == 'cover_letter':
        content = cover_letter or ''
        filename = f'cover_letter_{job_id}.pdf'
    else:
        return "Invalid document type", 400

    # PDF generation with formatting
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=0.75*inch, rightMargin=0.75*inch, topMargin=0.75*inch, bottomMargin=0.75*inch)
    styles = getSampleStyleSheet()
    story = []

    # Custom styles
    name_style = ParagraphStyle('Name', parent=styles['Heading1'], fontSize=22, alignment=TA_CENTER, spaceAfter=10, spaceBefore=10)
    contact_style = ParagraphStyle('Contact', parent=styles['Normal'], fontSize=11, alignment=TA_CENTER, textColor=colors.black, spaceAfter=10)
    section_style = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=13, textColor=colors.HexColor('#1a4a7c'), spaceBefore=18, spaceAfter=6, leading=16, fontName='Helvetica-Bold')
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=11, leading=15, spaceAfter=6)
    bullet_style = ParagraphStyle('Bullet', parent=styles['Normal'], fontSize=11, leftIndent=15, bulletIndent=5, leading=15)

    # --- Render AI-optimized resume or cover letter only ---
    lines = [l for l in content.splitlines() if l.strip()]

    # --- Remove any '---' separator lines and extract name/contact/location ---
    name = ''
    contact = ''
    location = ''
    extra_contact = ''
    rest_lines = []
    for l in lines:
        l_strip = l.strip()
        l_lower = l_strip.lower()
        if l_strip == '---':
            continue  # skip separator
        if l_lower.startswith('name:'):
            name = l_strip.split(':', 1)[-1].strip()
        elif l_lower.startswith('contact:'):
            contact = l_strip.split(':', 1)[-1].strip()
        elif l_lower.startswith('location:'):
            location = l_strip.split(':', 1)[-1].strip()
        elif l_lower.startswith('www') or l_lower.startswith('http'):
            extra_contact = l_strip
        else:
            rest_lines.append(l_strip)

    # --- Render name bold and centered at the top (no header) ---
    if name:
        story.append(Paragraph(f'<b>{name}</b>', name_style))
    # Render contact/location line centered below name (no headers)
    contact_line = ' | '.join(filter(None, [contact, location, extra_contact]))
    if contact_line:
        story.append(Paragraph(contact_line, contact_style))
    story.append(Spacer(1, 8))

    # --- Section parsing with experience subheader logic, grouped skills, and section reordering ---
    section_keywords = [
        'summary', 'professional summary', 'skills', 'projects', 'relevant projects',
        'experience', 'professional experience', 'education', 'community & interests', 'interests', 'project experience'
    ]
    def is_section_header(line):
        l = line.strip()
        if l.endswith(':'):
            return True
        if l.isupper() and len(l) > 3:
            return True
        l_clean = l.lower().rstrip(':').strip()
        return l_clean in section_keywords

    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=11, leading=15, spaceBefore=8, spaceAfter=4, fontName='Helvetica-Bold')

    # --- Parse all sections into a dict for reordering ---
    sections = {}
    current_section = None
    section_buffer = []
    for line in rest_lines:
        l_strip = line.strip()
        if is_section_header(l_strip):
            if current_section:
                sections[current_section] = section_buffer
                section_buffer = []
            current_section = l_strip
        elif current_section:
            section_buffer.append(line)
        else:
            # If not in a section, treat as intro
            sections.setdefault('intro', []).append(line)
    if current_section:
        sections[current_section] = section_buffer

    # --- Section order: SUMMARY, SKILLS, EXPERIENCE, then others as found ---
    ordered_section_titles = []
    for key in sections.keys():
        if key.lower().startswith('summary'):
            ordered_section_titles.append(key)
    for key in sections.keys():
        if key.lower().startswith('skills'):
            ordered_section_titles.append(key)
    for key in sections.keys():
        if key.lower().startswith('experience'):
            ordered_section_titles.append(key)
    for key in sections.keys():
        # Exclude SUMMARY, SKILLS, EXPERIENCE, and LANGUAGE sections
        if key.lower().startswith('summary') or key.lower().startswith('skills') or key.lower().startswith('experience') or key.lower().startswith('language'):
            continue
        ordered_section_titles.append(key)

    def flush_section(title, buffer):
        if not buffer:
            return
        story.append(Spacer(1, 10))
        story.append(Paragraph(f'<b>{title.rstrip(":").upper()}</b>', section_style))
        # SKILLS section: handle subheadings and skill lists
        if title.lower().startswith('skills'):
            current_category = None
            for line in buffer:
                line_strip = line.strip()
                if not line_strip:
                    continue
                    
                # Check if this is a skill category heading (ends with a colon)
                if ':' in line_strip and not line_strip.startswith('-') and not line_strip.startswith('•'):
                    # This is a category heading like "Programming Languages: Python, Java"
                    parts = line_strip.split(':', 1)
                    if len(parts) == 2:
                        category = parts[0].strip()
                        skills = parts[1].strip()
                        
                        # Add the category as a subheading
                        story.append(Paragraph(f'<b>{category}</b>', subtitle_style))
                        
                        # Add the skills as normal text (not bullets)
                        if skills:
                            story.append(Paragraph(skills, normal_style))
                    else:
                        # Just a heading without skills yet
                        story.append(Paragraph(f'<b>{line_strip}</b>', subtitle_style))
                elif line_strip.startswith('-') or line_strip.startswith('•'):
                    # Handle any bullet points that might still exist in the skills section
                    story.append(Paragraph(line_strip.lstrip('-•').strip(), bullet_style, bulletText='•'))
                else:
                    # Plain text that isn't a category heading
                    story.append(Paragraph(line_strip, normal_style))
        # EXPERIENCE section: bold subheader for lines with ' | '
        elif title.lower().startswith('experience') or title.lower().startswith('professional experience'):
            for line in buffer:
                line_strip = line.strip()
                if '|' in line_strip and not line_strip.startswith('-'):
                    story.append(Paragraph(f'<b>{line_strip}</b>', normal_style))
                elif line_strip.startswith('-') or line_strip.startswith('•'):
                    story.append(Paragraph(line_strip.lstrip('-•').strip(), bullet_style, bulletText='•'))
                else:
                    story.append(Paragraph(line_strip, normal_style))
        # EDUCATION section: bold institution name
        elif title.lower().startswith('education'):
            for line in buffer:
                line_strip = line.strip()
                # Try to bold the institution name (after first '|')
                if '|' in line_strip:
                    parts = [p.strip() for p in line_strip.split('|')]
                    if len(parts) >= 2:
                        # Assume institution is the second part
                        bolded = f"{parts[0]} | <b>{parts[1]}</b>"
                        if len(parts) > 2:
                            bolded += ' | ' + ' | '.join(parts[2:])
                        story.append(Paragraph(bolded, normal_style))
                    else:
                        story.append(Paragraph(line_strip, normal_style))
                else:
                    story.append(Paragraph(line_strip, normal_style))
        # PROJECT EXPERIENCE section: bold project titles (first non-bullet line before bullets)
        elif title.lower().startswith('project experience') or title.lower().startswith('projects'):
            in_project = False
            for idx, line in enumerate(buffer):
                line_strip = line.strip()
                if not line_strip:
                    continue
                if not (line_strip.startswith('-') or line_strip.startswith('•')):
                    # Bold project title
                    story.append(Paragraph(f'<b>{line_strip}</b>', normal_style))
                    in_project = True
                else:
                    story.append(Paragraph(line_strip.lstrip('-•').strip(), bullet_style, bulletText='•'))
        else:
            for line in buffer:
                line_strip = line.strip()
                if line_strip.startswith('-') or line_strip.startswith('•'):
                    story.append(Paragraph(line_strip.lstrip('-•').strip(), bullet_style, bulletText='•'))
                else:
                    story.append(Paragraph(line_strip, normal_style))

    # Render sections in the new order
    for section_title in ordered_section_titles:
        flush_section(section_title, sections[section_title])
    # Add extra space at end
    story.append(Spacer(1, 16))
    doc.build(story)
    buffer.seek(0)
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )


@bp.route('/download-my-tailored/<job_id>/<doc_type>', methods=['GET'])
@login_required
def download_my_tailored(job_id, doc_type):
    """Download tailored resume or cover letter for a job from the resume section (MongoDB source)"""
    mongo_db = current_app.mongo_db
    tailored = mongo_db.tailored_resumes.find_one({"user_id": str(current_user.id), "job_id": str(job_id)})
    if not tailored:
        return "No tailored resume found for this job.", 404
    if doc_type == 'resume':
        content = tailored.get('resume_text', '')
        filename = f'tailored_resume_{job_id}.pdf'
    elif doc_type == 'cover_letter':
        content = tailored.get('cover_letter', '')
        filename = f'cover_letter_{job_id}.pdf'
    else:
        return "Invalid document type", 400
    # PDF generation (reuse logic from download_tailored)
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=0.75*inch, rightMargin=0.75*inch, topMargin=0.75*inch, bottomMargin=0.75*inch)
    styles = getSampleStyleSheet()
    story = []
    name_style = ParagraphStyle('Name', parent=styles['Heading1'], fontSize=22, alignment=TA_CENTER, spaceAfter=10, spaceBefore=10)
    contact_style = ParagraphStyle('Contact', parent=styles['Normal'], fontSize=11, alignment=TA_CENTER, textColor=colors.black, spaceAfter=10)
    section_style = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=13, textColor=colors.HexColor('#1a4a7c'), spaceBefore=18, spaceAfter=6, leading=16, fontName='Helvetica-Bold')
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=11, leading=15, spaceAfter=6)
    bullet_style = ParagraphStyle('Bullet', parent=styles['Normal'], fontSize=11, leftIndent=15, bulletIndent=5, leading=15)
    lines = [l for l in content.splitlines() if l.strip()]
    name = ''
    contact = ''
    location = ''
    extra_contact = ''
    rest_lines = []
    for l in lines:
        l_strip = l.strip()
        l_lower = l_strip.lower()
        if l_strip == '---':
            continue  # skip separator
        if l_lower.startswith('name:'):
            name = l_strip.split(':', 1)[-1].strip()
        elif l_lower.startswith('contact:'):
            contact = l_strip.split(':', 1)[-1].strip()
        elif l_lower.startswith('location:'):
            location = l_strip.split(':', 1)[-1].strip()
        elif l_lower.startswith('www') or l_lower.startswith('http'):
            extra_contact = l_strip
        else:
            rest_lines.append(l_strip)
    if name:
        story.append(Paragraph(f'<b>{name}</b>', name_style))
    contact_line = ' | '.join(filter(None, [contact, location, extra_contact]))
    if contact_line:
        story.append(Paragraph(contact_line, contact_style))
    story.append(Spacer(1, 8))
    section_keywords = [
        'summary', 'professional summary', 'skills', 'projects', 'relevant projects',
        'experience', 'professional experience', 'education', 'community & interests', 'interests', 'project experience'
    ]
    def is_section_header(line):
        l = line.strip()
        if l.endswith(':'):
            return True
        if l.isupper() and len(l) > 3:
            return True
        l_clean = l.lower().rstrip(':').strip()
        return l_clean in section_keywords
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=11, leading=15, spaceBefore=8, spaceAfter=4, fontName='Helvetica-Bold')
    sections = {}
    current_section = None
    section_buffer = []
    for line in rest_lines:
        l_strip = line.strip()
        if is_section_header(l_strip):
            if current_section:
                sections[current_section] = section_buffer
                section_buffer = []
            current_section = l_strip
        elif current_section:
            section_buffer.append(line)
        else:
            sections.setdefault('intro', []).append(line)
    if current_section:
        sections[current_section] = section_buffer
    ordered_section_titles = []
    for key in sections.keys():
        if key.lower().startswith('summary'):
            ordered_section_titles.append(key)
    for key in sections.keys():
        if key.lower().startswith('skills'):
            ordered_section_titles.append(key)
    for key in sections.keys():
        if key.lower().startswith('experience'):
            ordered_section_titles.append(key)
    for key in sections.keys():
        if key.lower().startswith('summary') or key.lower().startswith('skills') or key.lower().startswith('experience') or key.lower().startswith('language'):
            continue
        ordered_section_titles.append(key)
    def flush_section(title, buffer):
        if not buffer:
            return
        story.append(Spacer(1, 10))
        story.append(Paragraph(f'<b>{title.rstrip(":").upper()}</b>', section_style))
        if title.lower().startswith('skills'):
            group = None
            group_buffer = []
            for line in buffer:
                line_strip = line.strip()
                if line_strip.startswith('-') and len(line_strip) > 2 and not line_strip[1].isspace():
                    if group and group_buffer:
                        story.append(Paragraph(f'<b>{group.lstrip("- ")}</b>', subtitle_style))
                        for skill in group_buffer:
                            story.append(Paragraph(skill.lstrip('-•').strip(), bullet_style, bulletText='•'))
                        group_buffer = []
                    group = line_strip
                elif line_strip.startswith('-') or line_strip.startswith('•'):
                    group_buffer.append(line_strip)
                elif line_strip:
                    group_buffer.append(line_strip)
            if group and group_buffer:
                story.append(Paragraph(f'<b>{group.lstrip("- ")}</b>', subtitle_style))
                for skill in group_buffer:
                    story.append(Paragraph(skill.lstrip('-•').strip(), bullet_style, bulletText='•'))
            elif group_buffer:
                for skill in group_buffer:
                    story.append(Paragraph(skill.lstrip('-•').strip(), bullet_style, bulletText='•'))
        elif title.lower().startswith('experience') or title.lower().startswith('professional experience'):
            for line in buffer:
                line_strip = line.strip()
                if '|' in line_strip and not line_strip.startswith('-'):
                    story.append(Paragraph(f'<b>{line_strip}</b>', normal_style))
                elif line_strip.startswith('-') or line_strip.startswith('•'):
                    story.append(Paragraph(line_strip.lstrip('-•').strip(), bullet_style, bulletText='•'))
                else:
                    story.append(Paragraph(line_strip, normal_style))
        elif title.lower().startswith('education'):
            for line in buffer:
                line_strip = line.strip()
                if '|' in line_strip:
                    parts = [p.strip() for p in line_strip.split('|')]
                    if len(parts) >= 2:
                        bolded = f"{parts[0]} | <b>{parts[1]}</b>"
                        if len(parts) > 2:
                            bolded += ' | ' + ' | '.join(parts[2:])
                        story.append(Paragraph(bolded, normal_style))
                    else:
                        story.append(Paragraph(line_strip, normal_style))
                else:
                    story.append(Paragraph(line_strip, normal_style))
        elif title.lower().startswith('project experience') or title.lower().startswith('projects'):
            in_project = False
            for idx, line in enumerate(buffer):
                line_strip = line.strip()
                if not line_strip:
                    continue
                if not (line_strip.startswith('-') or line_strip.startswith('•')):
                    story.append(Paragraph(f'<b>{line_strip}</b>', normal_style))
                    in_project = True
                else:
                    story.append(Paragraph(line_strip.lstrip('-•').strip(), bullet_style, bulletText='•'))
        else:
            for line in buffer:
                line_strip = line.strip()
                if line_strip.startswith('-') or line_strip.startswith('•'):
                    story.append(Paragraph(line_strip.lstrip('-•').strip(), bullet_style, bulletText='•'))
                else:
                    story.append(Paragraph(line_strip, normal_style))
    for section_title in ordered_section_titles:
        flush_section(section_title, sections[section_title])
    story.append(Spacer(1, 16))
    doc.build(story)
    buffer.seek(0)
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )


def calculate_profile_completion(user):
    """Calculate accurate profile completion percentage"""
    try:
        # Define all fields we want to check for completion
        fields_to_check = [
            ('first_name', 'First Name', True),  # (field_name, display_name, is_required)
            ('last_name', 'Last Name', True),
            ('email', 'Email', True),  # Always filled
            ('phone', 'Phone Number', False),
            ('city', 'City', False),
            ('bio', 'Professional Bio', False),
            ('skills', 'Skills', False),
            ('experience_level', 'Experience Level', False),
            ('profile_picture', 'Profile Picture', False),
            ('linkedin_url', 'LinkedIn Profile', False),
            ('github_url', 'GitHub Profile', False),
            ('portfolio_url', 'Portfolio Website', False)
        ]
        
        completed_fields = 0
        total_fields = len(fields_to_check)
        missing_fields = []
        filled_fields = []
        completion_items = []
        
        for field, label, is_required in fields_to_check:
            value = getattr(user, field, None)
            
            # Check if field has meaningful content
            is_filled = False
            
            if field == 'email':
                # Email is always considered filled if user exists
                is_filled = bool(value and str(value).strip())
            elif field == 'profile_picture':
                # Profile picture is filled if not default
                is_filled = bool(value and str(value).strip() and 
                               str(value) not in ['uploads/profiles/default.png', '', 'None', 'null'])
            elif field == 'experience_level':
                # Experience level is filled if not default/empty
                is_filled = bool(value and str(value).strip() and 
                               str(value) not in ['not_specified', 'Not Specified', '', 'None', 'null'])
            elif field in ['linkedin_url', 'github_url', 'portfolio_url']:
                # Social media URLs are filled if they contain valid URLs
                is_filled = bool(value and str(value).strip() and 
                               str(value).startswith(('http://', 'https://')) and
                               str(value) not in ['', 'None', 'null'])
            elif field == 'skills':
                # Skills can be stored as string or array
                if isinstance(value, str):
                    # Check if it's not empty string or empty array string
                    is_filled = bool(value.strip() and value.strip() not in ['[]', '{}', '', 'None', 'null'])
                elif isinstance(value, (list, tuple)):
                    is_filled = bool(value and len(value) > 0)
                else:
                    is_filled = bool(value)
            else:
                # Standard text fields
                is_filled = bool(value and str(value).strip() and 
                               str(value).strip() not in ['', 'None', 'null', 'nan'])
            
            # Create completion item
            completion_items.append({
                'field': field,
                'name': label,
                'completed': is_filled,
                'value': value
            })
            
            if is_filled:
                completed_fields += 1
                filled_fields.append(label)
            else:
                missing_fields.append(label)
                
                # Log missing field values for debugging
                current_app.logger.debug(f"Missing field '{field}': value='{value}', type={type(value)}")
        
        completion_percentage = round((completed_fields / total_fields) * 100) if total_fields > 0 else 0
        
        # Log completion details for debugging
        current_app.logger.info(f"Profile completion for user {user.id}: {completion_percentage}% ({completed_fields}/{total_fields})")
        current_app.logger.debug(f"Filled fields: {filled_fields}")
        current_app.logger.debug(f"Missing fields: {missing_fields}")
        
        return {
            'percentage': completion_percentage,
            'completed': completed_fields,
            'total': total_fields,
            'items': completion_items,
            'missing_items': [item for item in completion_items if not item['completed']],
            'missing_fields': missing_fields,
            'filled_fields': filled_fields,
            'completed_fields': completed_fields,
            'total_fields': total_fields
        }
        
    except Exception as e:
        current_app.logger.error(f"Profile completion calculation error: {str(e)}")
        return {
            'percentage': 0,
            'completed': 0,
            'total': 9,
            'items': [],
            'missing_items': [],
            'missing_fields': ['Unable to calculate'],
            'filled_fields': [],
            'completed_fields': 0,
            'total_fields': 9
        }

def extract_resume_sections(resume_text):
    """
    Parse resume text into a dict of sections: {section_name: [lines]}
    """
    section_headers = [
        'summary', 'professional summary', 'skills', 'projects', 'relevant projects',
        'experience', 'professional experience', 'work experience', 'education',
        'community & interests', 'interests', 'project experience', 'certifications', 'awards'
    ]
    def is_section_header(line):
        l = line.strip()
        if l.endswith(':'):
            return True
        if l.isupper() and len(l) > 3:
            return True
        l_clean = l.lower().rstrip(':').strip()
        return l_clean in section_headers
    sections = {}
    current_section = None
    section_buffer = []
    for line in resume_text.splitlines():
        l_strip = line.strip()
        if is_section_header(l_strip):
            if current_section:
                sections[current_section] = section_buffer
                section_buffer = []
            current_section = l_strip.rstrip(':').upper()
        elif current_section:
            section_buffer.append(line)
        else:
            sections.setdefault('INTRO', []).append(line)
    if current_section:
        sections[current_section] = section_buffer
    return sections

def extract_job_keywords(job_description):
    """
    Extract keywords and requirements from job description.
    Returns a dict with keys: skills, qualifications, responsibilities, keywords
    """
    # Simple regex/keyword-based extraction (can be improved with AI)
    skills = re.findall(r"[Ss]kills?[:\-\s]*([\w, .]+)", job_description)
    qualifications = re.findall(r"[Qq]ualifications?[:\-\s]*([\w, .]+)", job_description)
    responsibilities = re.findall(r"[Rr]esponsabilit(?:y|ies)[:\-\s]*([\w, .]+)", job_description)
    # Extract all unique words longer than 3 chars as keywords (can be improved)
    words = set(w.lower() for w in re.findall(r"\b\w{4,}\b", job_description))
    return {
        'skills': skills,
        'qualifications': qualifications,
        'responsibilities': responsibilities,
        'keywords': list(words)
    }


# @bp.route('/my-tailored-resumes')
# @login_required
# def my_tailored_resumes():
#     """Show all best tailored resumes and cover letters for the current user (from MongoDB)"""
#     if not current_user.is_applicant():
#         return redirect(url_for('main.dashboard'))
#     mongo_db = current_app.mongo_db
#     tailored_list = get_best_tailored_resumes(mongo_db, str(current_user.id))
#     # Fetch job titles for display
#     job_ids = [t['job_id'] for t in tailored_list]
#     jobs = {str(j['_id']): j for j in mongo_db.jobs.find({'_id': {'$in': [ObjectId(jid) for jid in job_ids]}})}
#     # Build display list
#     display_list = []
#     for t in tailored_list:
#         job = jobs.get(t['job_id'])
#         display_list.append({
#             'job_id': t['job_id'],
#             'job_title': job['title'] if job else '(Job not found)',
#             'ats_score': t.get('ats_score'),
#             'updated_at': t.get('updated_at'),
#             'resume_text': t.get('resume_text', ''),
#             'cover_letter': t.get('cover_letter', '')
#         })
#     return render_template('resume/my_resumes.html', tailored_resumes=display_list, title='My Tailored Resumes')


@bp.route('/submit-tailored-feedback/<job_id>', methods=['POST'])
@login_required
def submit_tailored_feedback(job_id):
    """Accept feedback (rating, comments) for a tailored resume/cover letter for a job."""
    if not current_user.is_applicant():
        return jsonify({'error': 'Unauthorized'}), 403
    mongo_db = current_app.mongo_db
    tailored = mongo_db.tailored_resumes.find_one({"user_id": str(current_user.id), "job_id": str(job_id)})
    if not tailored:
        return jsonify({'error': 'No tailored resume found for this job.'}), 404
    data = request.get_json() or {}
    rating = data.get('rating')  # e.g., 1-5
    comments = data.get('comments', '').strip()
    feedback_entry = {
        'rating': rating,
        'comments': comments,
        'submitted_at': datetime.utcnow()
    }
    # Store feedback as a list (history) in the tailored_resumes document
    mongo_db.tailored_resumes.update_one(
        {"user_id": str(current_user.id), "job_id": str(job_id)},
        {"$push": {"feedback": feedback_entry}}
    )
    return jsonify({'success': True, 'message': 'Feedback submitted.'})


@bp.route('/send-application/<job_id>', methods=['POST'])
@login_required
def send_application(job_id):
    """Send application email with resume and cover letter"""
    try:
        mongo_db = current_app.mongo_db
        job = mongo_db.jobs.find_one({"_id": ObjectId(job_id)})
        if not job:
            return jsonify({"success": False, "error": "Job not found"})
        
        # Get application email from job data
        application_email = job.get('email') or job.get('application_email') or job.get('contact_email')
        if not application_email:
            return jsonify({"success": False, "error": "No application email found for this job"})
        
        data = request.json
        resume_text = data.get('resume_text')
        cover_letter_text = data.get('cover_letter_text')
        
        if not resume_text or not cover_letter_text:
            return jsonify({"success": False, "error": "Resume or cover letter is missing"})
        
        # Log the application attempt
        current_app.logger.info(f"User {current_user.id} is sending application for job {job_id}")
        
        # Generate PDF attachments from the text content
        resume_pdf = io.BytesIO()
        cover_letter_pdf = io.BytesIO()
        
        # Create resume PDF
        p = canvas.Canvas(resume_pdf, pagesize=letter)
        p.setTitle(f"Resume for {job.get('title')} at {job.get('company')}")
        text_object = p.beginText(72, 750)  # 1 inch from top
        text_object.setFont("Helvetica", 12)
        for line in resume_text.split('\n'):
            text_object.textLine(line)
        p.drawText(text_object)
        p.save()
        resume_pdf.seek(0)
        
        # Create cover letter PDF
        p = canvas.Canvas(cover_letter_pdf, pagesize=letter)
        p.setTitle(f"Cover Letter for {job.get('title')} at {job.get('company')}")
        text_object = p.beginText(72, 750)  # 1 inch from top
        text_object.setFont("Helvetica", 12)
        for line in cover_letter_text.split('\n'):
            text_object.textLine(line)
        p.drawText(text_object)
        p.save()
        cover_letter_pdf.seek(0)
        
        # Prepare email
        msg = MIMEMultipart()
        msg['From'] = current_user.email
        msg['To'] = application_email
        msg['Subject'] = f"Application for {job.get('title')} position"
        
        # Email body
        body = f"""Dear Hiring Manager,

I am writing to express my interest in the {job.get('title')} position at {job.get('company')}.

Please find my resume and cover letter attached to this email.

Thank you for your consideration.

Sincerely,
{current_user.first_name} {current_user.last_name}
{current_user.email}
"""
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach resume
        resume_attachment = MIMEApplication(resume_pdf.read(), _subtype="pdf")
        resume_attachment.add_header('Content-Disposition', f'attachment; filename=resume_{current_user.last_name}.pdf')
        msg.attach(resume_attachment)
        
        # Attach cover letter
        cover_letter_attachment = MIMEApplication(cover_letter_pdf.read(), _subtype="pdf")
        cover_letter_attachment.add_header('Content-Disposition', f'attachment; filename=cover_letter_{current_user.last_name}.pdf')
        msg.attach(cover_letter_attachment)
        
        # Get SMTP settings from config
        smtp_server = current_app.config.get('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = current_app.config.get('SMTP_PORT', 587)
        smtp_user = current_app.config.get('SMTP_USER', current_user.email)
        smtp_password = current_app.config.get('SMTP_PASSWORD', '')
        
        # Send email through SMTP
        if current_app.config.get('TESTING') or not smtp_password:
            # In testing mode or if no SMTP password is configured, just log the attempt
            current_app.logger.info(f"Email would be sent to {application_email} for job {job.get('title')}")
        else:
            # Real email sending
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
        
        # Record this application in the database
        mongo_db.applications.insert_one({
            "user_id": str(current_user.id),
            "job_id": str(job_id),
            "applied_at": datetime.utcnow(),
            "method": "email",
            "status": "applied",
            "email": application_email,
            "job_title": job.get('title'),
            "company": job.get('company')
        })
        
        return jsonify({
            "success": True, 
            "message": f"Application sent successfully to {application_email}"
        })
        
    except Exception as e:
        current_app.logger.error(f"Error sending application email: {str(e)}", exc_info=True)
        return jsonify({
            "success": False, 
            "error": "An error occurred while sending your application. Please try again."
        })


# --- DEBUG ROUTES ---

@bp.route('/debug/profile-completion')
@login_required
def debug_profile_completion():
    """Debug route to check profile completion details"""
    
    import json
    
    # Get current user data
    user_data = {
        'user_id': str(current_user.id),
        'email': current_user.email,
        'first_name': getattr(current_user, 'first_name', None),
        'last_name': getattr(current_user, 'last_name', None),
        'phone': getattr(current_user, 'phone', None),
        'city': getattr(current_user, 'city', None),
        'bio': getattr(current_user, 'bio', None),
        'skills': getattr(current_user, 'skills', None),
        'experience_level': getattr(current_user, 'experience_level', None),
    }
    
    # Get profile completion calculation
    profile_data = calculate_profile_completion(current_user)
    
    # Check resume status
    resume_status = "No resume found"
    try:
        mongo_db = current_app.mongo_db
        if mongo_db:
            resume = mongo_db.resumes.find_one({'user_id': str(current_user.id)})
            if resume:
                resume_status = f"Resume found: {resume.get('filename', 'Unknown')}"
    except Exception as e:
        resume_status = f"Error checking resume: {str(e)}"
    
    debug_info = {
        'current_user_attributes': user_data,
        'profile_completion': profile_data,
        'resume_status': resume_status,
        'form_last_submitted': session.get('last_profile_update', 'Never')
    }
    
    return f"""
    <html>
    <head><title>Profile Debug</title></head>
    <body style="font-family: monospace; padding: 20px; background: #f5f5f5;">
        <h2 style="color: #333;">Profile Completion Debug</h2>
        <pre style="background: white; padding: 20px; border-radius: 8px; overflow-x: auto; border: 1px solid #ddd;">{json.dumps(debug_info, indent=2, default=str)}</pre>
        <hr>
        <a href="{url_for('main.applicant_dashboard')}" style="color: #007bff; text-decoration: none;">← Back to Dashboard</a> | 
        <a href="{url_for('main.profile')}" style="color: #007bff; text-decoration: none;">Edit Profile</a>
    </body>
    </html>
    """


@bp.route('/debug/user-model')
@login_required  
def debug_user_model():
    """Check what attributes the User model has"""
    
    user_attrs = []
    for attr in dir(current_user):
        if not attr.startswith('_') and not callable(getattr(current_user, attr)):
            try:
                value = getattr(current_user, attr)
                user_attrs.append(f"{attr}: {value} ({type(value).__name__})")
            except Exception as e:
                user_attrs.append(f"{attr}: ERROR - {str(e)}")
    
    return f"""
    <html>
    <head><title>User Model Debug</title></head>
    <body style="font-family: monospace; padding: 20px; background: #f5f5f5;">
        <h2 style="color: #333;">User Model Attributes</h2>
        <pre style="background: white; padding: 20px; border-radius: 8px; overflow-x: auto; border: 1px solid #ddd;">{'<br>'.join(sorted(user_attrs))}</pre>
        <hr>
        <a href="{url_for('main.applicant_dashboard')}" style="color: #007bff; text-decoration: none;">← Back to Dashboard</a>
    </body>
    </html>
    """


@bp.route('/test-login')
def test_login():
    """Quick test login for demo purposes"""
    from flask_login import login_user
    
    # Find or create a test user
    test_user = User.query.filter_by(email='test@example.com').first()
    if not test_user:
        test_user = User(
            email='test@example.com',
            password='testpassword',
            first_name='Test',
            last_name='User',
            user_type='applicant'
        )
        test_user.set_password('testpassword')
        db.session.add(test_user)
        db.session.commit()
    
    # Enable the user and verify them
    test_user.is_active = True
    test_user.is_verified = True
    db.session.commit()
    
    # Login the user
    login_success = login_user(test_user, remember=True)
    
    if login_success:
        flash('Test user logged in successfully!', 'success')
        return redirect(url_for('main.profile'))
    else:
        return f"Login failed for user {test_user.email}"


# --- Interview Questions Integration ---
@bp.route('/tailor/<job_id>/database-questions')
@login_required
def tailor_database_questions(job_id):
    """Generate interview questions for specific job"""
    try:
        # Get MongoDB database from current app
        mongo_db = current_app.mongo_db
        
        if mongo_db is None:
            flash('Database connection not available', 'error')
            return redirect(url_for('main.home'))
        
        # Find the job
        jobs_collection = mongo_db.jobs
        job = jobs_collection.find_one({"_id": ObjectId(job_id)})
        
        if job is None:
            flash('Job not found', 'error')
            return redirect(url_for('main.home'))
        
        # Check if this is for iframe usage
        is_iframe = request.args.get('iframe') == 'true'
        template_name = 'question/tailor_database_questions_iframe.html' if is_iframe else 'question/tailor_database_questions.html'
            
        return render_template(template_name, job=job, job_id=job_id)
    except Exception as e:
        current_app.logger.error(f'Error loading questions page: {str(e)}')
        flash(f'Error loading questions page: {str(e)}', 'error')
        return redirect(url_for('main.tailor_resume', job_id=job_id))


@bp.route('/tailor/<job_id>/generate-database-questions', methods=['POST'])
@login_required
def generate_database_questions_route(job_id):
    """Generate questions endpoint"""
    try:
        # Import the question generation functionality
        from app.question.question_gen_db import generate_database_questions
        
        # Get form data
        num_questions = int(request.form.get('num_questions', 5))
        question_type = request.form.get('question_type', 'mixed')
        
        # Get MongoDB database from current app
        mongo_db = current_app.mongo_db
        
        if mongo_db is None:
            flash('Database connection not available', 'error')
            return redirect(url_for('main.tailor_database_questions', job_id=job_id))
        
        # Find the job
        jobs_collection = mongo_db.jobs
        job = jobs_collection.find_one({"_id": ObjectId(job_id)})
        
        if job is None:
            flash('Job not found', 'error')
            return redirect(url_for('main.tailor_database_questions', job_id=job_id))
            
        # Generate questions with parameters
        questions = generate_database_questions(
            job_id=job_id, 
            job_data=job, 
            n=num_questions,
            question_type=question_type
        )
        
        # Check if this is for iframe usage
        is_iframe = request.args.get('iframe') == 'true'
        template_name = 'question/tailor_database_questions_iframe.html' if is_iframe else 'question/tailor_database_questions.html'
        
        return render_template(template_name, 
                             job=job, 
                             job_id=job_id, 
                             questions=questions,
                             num_questions=num_questions,
                             question_type=question_type)
        
    except Exception as e:
        current_app.logger.error(f'Error generating questions: {str(e)}')
        flash(f'Error generating questions: {str(e)}', 'error')
        return redirect(url_for('main.tailor_database_questions', job_id=job_id))


# --- Interview Questions Main Routes ---
@bp.route('/interview-questions')
@login_required
def interview_questions_home():
    """Main Interview Questions page"""
    return render_template('question/index.html')


@bp.route('/interview-questions/job-skills')
@login_required  
def interview_questions_skills():
    """Interview Questions based on job skills"""
    return render_template('question/skills_questions.html')


@bp.route('/interview-questions/job-description')
@login_required
def interview_questions_description():
    """Interview Questions based on job description"""
    return render_template('question/job_description_questions.html')


@bp.route('/interview-questions/from-database')
@login_required
def interview_questions_database():
    """Interview Questions from database"""
    return render_template('question/questions_from_db.html')


@bp.route('/api/generate-questions-skills', methods=['POST'])
@login_required
def generate_questions_from_skills():
    """Generate questions based on skills"""
    try:
        from app.question.question_gen import generate_questions_from_skills as gen_skills
        
        data = request.get_json()
        skills = data.get('skills', '')
        level = data.get('level', 'intermediate')
        question_type = data.get('question_type', 'technical')
        language = data.get('language', 'English')
        num_questions = data.get('num_questions', 5)
        
        if not skills:
            return jsonify({'error': 'Skills are required', 'success': False}), 400
            
        questions = gen_skills(skills, level, question_type, language, num_questions)
        return jsonify({'questions': questions, 'success': True})
        
    except Exception as e:
        current_app.logger.error(f'Error generating skills questions: {str(e)}')
        return jsonify({'error': str(e), 'success': False}), 500


@bp.route('/api/generate-questions-description', methods=['POST'])
@login_required
def generate_questions_from_description():
    """Generate questions based on job description"""
    try:
        from app.question.question_gen2 import generate_questions_from_description as gen_desc
        
        data = request.get_json()
        job_description = data.get('job_description', '')
        level = data.get('level', 'intermediate')
        question_type = data.get('question_type', 'technical')
        language = data.get('language', 'English')
        num_questions = data.get('num_questions', 5)
        
        if not job_description:
            return jsonify({'error': 'Job description is required', 'success': False}), 400
            
        questions = gen_desc(job_description, level, question_type, language, num_questions)
        return jsonify({'questions': questions, 'success': True})
        
    except Exception as e:
        current_app.logger.error(f'Error generating description questions: {str(e)}')
        return jsonify({'error': str(e), 'success': False}), 500
