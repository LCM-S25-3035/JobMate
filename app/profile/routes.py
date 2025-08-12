"""
Enhanced Profile Routes for JobMate
Comprehensive routes for managing user profiles, experience, education, skills, etc.
"""

import os
import uuid
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from PIL import Image

from app import db
from app.profile.forms import (
    EnhancedProfileForm, ExperienceForm, EducationForm, 
    CertificationForm, SkillsForm, ProfilePrivacyForm, SocialLinksForm
)
from app.models.profile import UserExperience, UserEducation, UserCertification, UserSkill, UserSocialLink
from app.utils import calculate_profile_completion

# Import the blueprint from the module
from . import bp

# Configuration for file uploads
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    """Check if uploaded file is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

def process_profile_image(file, user_id):
    """Process and save profile image"""
    if not file or not allowed_file(file.filename):
        return None
    
    try:
        # Create unique filename
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"profile_{user_id}_{uuid.uuid4().hex[:8]}{ext}"
        
        # Create uploads directory if it doesn't exist
        upload_folder = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'static/uploads'), 'profiles')
        os.makedirs(upload_folder, exist_ok=True)
        
        # Save file path
        file_path = os.path.join(upload_folder, unique_filename)
        
        # Process image with PIL
        image = Image.open(file)
        
        # Convert to RGB if necessary
        if image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')
        
        # Resize image (max 400x400, maintain aspect ratio)
        image.thumbnail((400, 400), Image.Resampling.LANCZOS)
        
        # Save processed image
        image.save(file_path, optimize=True, quality=85)
        
        # Return relative path for database storage
        return f"uploads/profiles/{unique_filename}"
        
    except Exception as e:
        current_app.logger.error(f"Error processing profile image: {e}")
        return None


@bp.route('/remove-profile-picture', methods=['POST'])
@login_required
def remove_profile_picture():
    """Remove user's profile picture"""
    try:
        # Get the current profile picture path
        old_picture = current_user.profile_picture
        
        # Remove from database
        current_user.profile_picture = None
        db.session.commit()
        
        # Delete file from filesystem if it exists
        if old_picture:
            file_path = os.path.join(current_app.root_path, 'static', old_picture)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    current_app.logger.info(f"Deleted profile picture file: {file_path}")
                except OSError as e:
                    current_app.logger.warning(f"Could not delete profile picture file {file_path}: {e}")
        
        flash('Profile picture removed successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error removing profile picture: {e}")
        flash('Error removing profile picture. Please try again.', 'error')
    
    return redirect(url_for('user_profile.enhanced_profile'))


@bp.route('/enhanced')
@login_required
def enhanced_profile():
    """Enhanced profile page with all sections"""
    
    # Get profile completion data
    profile_data = calculate_profile_completion(current_user)
    
    # Get user's additional data
    experiences = current_user.experiences.order_by(UserExperience.start_date.desc()).all()
    educations = current_user.educations.order_by(UserEducation.end_year.desc().nullslast()).all()
    certifications = current_user.certifications.order_by(UserCertification.issue_date.desc().nullslast()).all()
    skills = current_user.user_skills.order_by(UserSkill.name).all()
    social_links = current_user.social_links.filter_by(is_public=True).all()
    
    return render_template('profile/enhanced.html',
                         title='Enhanced Profile',
                         user=current_user,
                         profile_data=profile_data,
                         experiences=experiences,
                         educations=educations,
                         certifications=certifications,
                         skills=skills,
                         social_links=social_links)


@bp.route('/enhanced/edit')
@login_required
def edit_enhanced_profile():
    """Edit enhanced profile form"""
    
    form = EnhancedProfileForm()
    
    # Pre-populate form with existing data
    if request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.phone.data = current_user.phone
        form.city.data = current_user.city
        form.province.data = current_user.province
        form.country.data = current_user.country
        form.bio.data = current_user.bio
        form.skills.data = current_user.skills
        form.experience_level.data = current_user.experience_level
        form.linkedin_url.data = current_user.linkedin_url
        form.github_url.data = current_user.github_url
        form.portfolio_url.data = current_user.portfolio_url
    
    return render_template('profile/edit_enhanced.html',
                         title='Edit Profile',
                         form=form)


@bp.route('/enhanced/update', methods=['POST'])
@login_required
def update_enhanced_profile():
    """Update enhanced profile"""
    
    form = EnhancedProfileForm()
    
    if form.validate_on_submit():
        try:
            # Update basic information
            current_user.first_name = form.first_name.data
            current_user.last_name = form.last_name.data
            current_user.phone = form.phone.data
            current_user.city = form.city.data
            current_user.province = form.province.data
            current_user.country = form.country.data
            current_user.bio = form.bio.data
            current_user.skills = form.skills.data
            current_user.experience_level = form.experience_level.data
            current_user.linkedin_url = form.linkedin_url.data
            current_user.github_url = form.github_url.data
            current_user.portfolio_url = form.portfolio_url.data
            
            # Handle profile picture upload
            profile_picture_success = True
            if form.profile_picture.data:
                image_path = process_profile_image(form.profile_picture.data, current_user.id)
                if image_path:
                    # Remove old profile picture if not default
                    old_picture = current_user.profile_picture
                    if old_picture and old_picture != 'uploads/profiles/default.png':
                        try:
                            old_path = os.path.join(current_app.static_folder, old_picture)
                            if os.path.exists(old_path):
                                os.remove(old_path)
                        except Exception as e:
                            current_app.logger.error(f"Error removing old profile picture: {e}")
                    
                    current_user.profile_picture = image_path
                else:
                    profile_picture_success = False
            
            # Update timestamp
            current_user.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            # Show appropriate success message
            if profile_picture_success:
                flash('Profile updated successfully!', 'success')
            else:
                flash('Profile updated, but there was an issue with the profile picture. Please try uploading again.', 'warning')
            
            return redirect(url_for('user_profile.enhanced_profile'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating profile: {e}")
            flash('Error updating profile. Please try again.', 'error')
            return redirect(url_for('user_profile.edit_enhanced_profile'))
    
    # If form validation failed, show errors
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{field}: {error}", 'error')
    
    return render_template('profile/edit_enhanced.html',
                         title='Edit Profile',
                         form=form)


# Experience Management Routes
@bp.route('/experience/add')
@login_required
def add_experience():
    """Add new work experience"""
    form = ExperienceForm()
    return render_template('profile/add_experience.html',
                         title='Add Experience',
                         form=form)


@bp.route('/experience/create', methods=['POST'])
@login_required
def create_experience():
    """Create new work experience"""
    form = ExperienceForm()
    
    if form.validate_on_submit():
        try:
            experience = UserExperience(
                user_id=current_user.id,
                job_title=form.job_title.data,
                company=form.company.data,
                location=form.location.data,
                start_date=form.start_date.data,
                end_date=form.end_date.data if not form.current_job.data else None,
                is_current=form.current_job.data,
                description=form.description.data
            )
            
            db.session.add(experience)
            db.session.commit()
            
            flash('Work experience added successfully!', 'success')
            return redirect(url_for('user_profile.enhanced_profile'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding experience: {e}")
            flash('Error adding experience. Please try again.', 'error')
    
    # Show form errors
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{field}: {error}", 'error')
    
    return render_template('profile/add_experience.html',
                         title='Add Experience',
                         form=form)


@bp.route('/experience/<int:experience_id>/edit')
@login_required
def edit_experience(experience_id):
    """Edit work experience"""
    experience = UserExperience.query.filter_by(id=experience_id, user_id=current_user.id).first_or_404()
    
    form = ExperienceForm()
    
    # Pre-populate form
    if request.method == 'GET':
        form.job_title.data = experience.job_title
        form.company.data = experience.company
        form.location.data = experience.location
        form.start_date.data = experience.start_date
        form.end_date.data = experience.end_date
        form.current_job.data = experience.is_current
        form.description.data = experience.description
    
    return render_template('profile/edit_experience.html',
                         title='Edit Experience',
                         form=form,
                         experience=experience)


@bp.route('/experience/<int:experience_id>/update', methods=['POST'])
@login_required
def update_experience(experience_id):
    """Update work experience"""
    experience = UserExperience.query.filter_by(id=experience_id, user_id=current_user.id).first_or_404()
    form = ExperienceForm()
    
    if form.validate_on_submit():
        try:
            experience.job_title = form.job_title.data
            experience.company = form.company.data
            experience.location = form.location.data
            experience.start_date = form.start_date.data
            experience.end_date = form.end_date.data if not form.current_job.data else None
            experience.is_current = form.current_job.data
            experience.description = form.description.data
            experience.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            flash('Work experience updated successfully!', 'success')
            return redirect(url_for('user_profile.enhanced_profile'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating experience: {e}")
            flash('Error updating experience. Please try again.', 'error')
    
    return render_template('profile/edit_experience.html',
                         title='Edit Experience',
                         form=form,
                         experience=experience)


@bp.route('/experience/<int:experience_id>/delete', methods=['POST'])
@login_required
def delete_experience(experience_id):
    """Delete work experience"""
    experience = UserExperience.query.filter_by(id=experience_id, user_id=current_user.id).first_or_404()
    
    try:
        db.session.delete(experience)
        db.session.commit()
        flash('Work experience deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting experience: {e}")
        flash('Error deleting experience. Please try again.', 'error')
    
    return redirect(url_for('user_profile.enhanced_profile'))


# Skills Management Routes
@bp.route('/skills/add')
@login_required
def add_skill():
    """Add new skill"""
    form = SkillsForm()
    return render_template('profile/add_skill.html',
                         title='Add Skill',
                         form=form)


@bp.route('/skills/create', methods=['POST'])
@login_required
def create_skill():
    """Create new skill"""
    form = SkillsForm()
    
    if form.validate_on_submit():
        try:
            # Check if skill already exists for this user
            existing_skill = UserSkill.query.filter_by(
                user_id=current_user.id,
                name=form.skill_name.data
            ).first()
            
            if existing_skill:
                flash(f'Skill "{form.skill_name.data}" already exists in your profile.', 'warning')
                return redirect(url_for('user_profile.enhanced_profile'))
            
            skill = UserSkill(
                user_id=current_user.id,
                name=form.skill_name.data,
                proficiency=form.proficiency.data,
                years_experience=form.years_experience.data,
                category=UserSkill.categorize_skill(form.skill_name.data)
            )
            
            db.session.add(skill)
            db.session.commit()
            
            flash('Skill added successfully!', 'success')
            return redirect(url_for('user_profile.enhanced_profile'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding skill: {e}")
            flash('Error adding skill. Please try again.', 'error')
    
    return render_template('profile/add_skill.html',
                         title='Add Skill',
                         form=form)


@bp.route('/skills/<int:skill_id>/delete', methods=['POST'])
@login_required
def delete_skill(skill_id):
    """Delete skill"""
    skill = UserSkill.query.filter_by(id=skill_id, user_id=current_user.id).first_or_404()
    
    try:
        db.session.delete(skill)
        db.session.commit()
        flash('Skill deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting skill: {e}")
        flash('Error deleting skill. Please try again.', 'error')
    
    return redirect(url_for('user_profile.enhanced_profile'))


# API Routes for dynamic updates
@bp.route('/api/completion')
@login_required
def api_profile_completion():
    """API endpoint for profile completion data"""
    profile_data = calculate_profile_completion(current_user)
    return jsonify(profile_data)


@bp.route('/api/skills')
@login_required
def api_user_skills():
    """API endpoint for user skills"""
    skills = current_user.user_skills.all()
    return jsonify([skill.to_dict() for skill in skills])


# Social Links Management
@bp.route('/social-links/edit')
@login_required
def edit_social_links():
    """Edit social media links"""
    form = SocialLinksForm()
    
    # Pre-populate form with existing data
    if request.method == 'GET':
        form.linkedin_url.data = current_user.linkedin_url
        form.github_url.data = current_user.github_url
        form.portfolio_url.data = current_user.portfolio_url
        
        # Get additional social links
        twitter_link = current_user.social_links.filter_by(platform='twitter').first()
        if twitter_link:
            form.twitter_url.data = twitter_link.url
    
    return render_template('profile/edit_social_links.html',
                         title='Edit Social Links',
                         form=form)


# Education Management Routes
@bp.route('/education/add')
@login_required
def add_education():
    """Add new education"""
    form = EducationForm()
    return render_template('profile/add_education.html',
                         title='Add Education',
                         form=form)


@bp.route('/education/create', methods=['POST'])
@login_required
def create_education():
    """Create new education"""
    form = EducationForm()
    
    if form.validate_on_submit():
        try:
            education = UserEducation(
                user_id=current_user.id,
                institution=form.institution.data,
                degree=form.degree.data,
                field_of_study=form.field_of_study.data,
                location=form.location.data,
                start_year=form.start_year.data,
                end_year=form.end_year.data,
                gpa=form.gpa.data,
                description=form.description.data
            )
            
            db.session.add(education)
            db.session.commit()
            
            flash('Education added successfully!', 'success')
            return redirect(url_for('user_profile.enhanced_profile'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding education: {e}")
            flash('Error adding education. Please try again.', 'error')
    
    return render_template('profile/add_education.html',
                         title='Add Education',
                         form=form)


@bp.route('/education/<int:education_id>/edit')
@login_required
def edit_education(education_id):
    """Edit education"""
    education = UserEducation.query.filter_by(id=education_id, user_id=current_user.id).first_or_404()
    form = EducationForm(obj=education)
    
    return render_template('profile/edit_education.html',
                         title='Edit Education',
                         form=form,
                         education=education)


@bp.route('/education/<int:education_id>/update', methods=['POST'])
@login_required
def update_education(education_id):
    """Update education"""
    education = UserEducation.query.filter_by(id=education_id, user_id=current_user.id).first_or_404()
    form = EducationForm()
    
    if form.validate_on_submit():
        try:
            education.institution = form.institution.data
            education.degree = form.degree.data
            education.field_of_study = form.field_of_study.data
            education.location = form.location.data
            education.start_year = form.start_year.data
            education.end_year = form.end_year.data
            education.gpa = form.gpa.data
            education.description = form.description.data
            
            db.session.commit()
            flash('Education updated successfully!', 'success')
            return redirect(url_for('user_profile.enhanced_profile'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating education: {e}")
            flash('Error updating education. Please try again.', 'error')
    
    return render_template('profile/edit_education.html',
                         title='Edit Education',
                         form=form,
                         education=education)


@bp.route('/education/<int:education_id>/delete', methods=['POST'])
@login_required
def delete_education(education_id):
    """Delete education"""
    education = UserEducation.query.filter_by(id=education_id, user_id=current_user.id).first_or_404()
    
    try:
        db.session.delete(education)
        db.session.commit()
        flash('Education deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting education: {e}")
        flash('Error deleting education. Please try again.', 'error')
    
    return redirect(url_for('user_profile.enhanced_profile'))


# Certification Management Routes
@bp.route('/certification/add')
@login_required
def add_certification():
    """Add new certification"""
    form = CertificationForm()
    return render_template('profile/add_certification.html',
                         title='Add Certification',
                         form=form)


@bp.route('/certification/create', methods=['POST'])
@login_required
def create_certification():
    """Create new certification"""
    form = CertificationForm()
    
    if form.validate_on_submit():
        try:
            certification = UserCertification(
                user_id=current_user.id,
                name=form.name.data,
                issuing_organization=form.issuing_organization.data,
                issue_date=form.issue_date.data,
                expiry_date=form.expiry_date.data,
                credential_id=form.credential_id.data,
                credential_url=form.credential_url.data,
                description=form.description.data
            )
            
            db.session.add(certification)
            db.session.commit()
            
            flash('Certification added successfully!', 'success')
            return redirect(url_for('user_profile.enhanced_profile'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error adding certification: {e}")
            flash('Error adding certification. Please try again.', 'error')
    
    return render_template('profile/add_certification.html',
                         title='Add Certification',
                         form=form)


@bp.route('/certification/<int:certification_id>/edit')
@login_required
def edit_certification(certification_id):
    """Edit certification"""
    certification = UserCertification.query.filter_by(id=certification_id, user_id=current_user.id).first_or_404()
    form = CertificationForm(obj=certification)
    
    return render_template('profile/edit_certification.html',
                         title='Edit Certification',
                         form=form,
                         certification=certification)


@bp.route('/certification/<int:certification_id>/update', methods=['POST'])
@login_required
def update_certification(certification_id):
    """Update certification"""
    certification = UserCertification.query.filter_by(id=certification_id, user_id=current_user.id).first_or_404()
    form = CertificationForm()
    
    if form.validate_on_submit():
        try:
            certification.name = form.name.data
            certification.issuing_organization = form.issuing_organization.data
            certification.issue_date = form.issue_date.data
            certification.expiry_date = form.expiry_date.data
            certification.credential_id = form.credential_id.data
            certification.credential_url = form.credential_url.data
            certification.description = form.description.data
            
            db.session.commit()
            flash('Certification updated successfully!', 'success')
            return redirect(url_for('user_profile.enhanced_profile'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating certification: {e}")
            flash('Error updating certification. Please try again.', 'error')
    
    return render_template('profile/edit_certification.html',
                         title='Edit Certification',
                         form=form,
                         certification=certification)


@bp.route('/certification/<int:certification_id>/delete', methods=['POST'])
@login_required
def delete_certification(certification_id):
    """Delete certification"""
    certification = UserCertification.query.filter_by(id=certification_id, user_id=current_user.id).first_or_404()
    
    try:
        db.session.delete(certification)
        db.session.commit()
        flash('Certification deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting certification: {e}")
        flash('Error deleting certification. Please try again.', 'error')
    
    return redirect(url_for('user_profile.enhanced_profile'))


@bp.route('/social-links/update', methods=['POST'])
@login_required
def update_social_links():
    """Update social media links"""
    form = SocialLinksForm()
    
    if form.validate_on_submit():
        try:
            # Update basic social links in user model
            current_user.linkedin_url = form.linkedin_url.data
            current_user.github_url = form.github_url.data
            current_user.portfolio_url = form.portfolio_url.data
            
            # Handle additional social links
            social_links_data = [
                ('twitter', form.twitter_url.data),
                ('behance', form.behance_url.data),
                ('dribbble', form.dribbble_url.data),
            ]
            
            for platform, url in social_links_data:
                if url:
                    # Update or create social link
                    social_link = current_user.social_links.filter_by(platform=platform).first()
                    if social_link:
                        social_link.url = url
                    else:
                        social_link = UserSocialLink(
                            user_id=current_user.id,
                            platform=platform,
                            url=url
                        )
                        db.session.add(social_link)
                else:
                    # Remove social link if URL is empty
                    social_link = current_user.social_links.filter_by(platform=platform).first()
                    if social_link:
                        db.session.delete(social_link)
            
            db.session.commit()
            flash('Social links updated successfully!', 'success')
            return redirect(url_for('user_profile.enhanced_profile'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating social links: {e}")
            flash('Error updating social links. Please try again.', 'error')
    
    return render_template('profile/edit_social_links.html',
                         title='Edit Social Links',
                         form=form)
