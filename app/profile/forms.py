"""
Enhanced Profile Forms for JobMate
Comprehensive forms for user profile management
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, SubmitField, BooleanField, DateField, IntegerField
from wtforms.validators import DataRequired, Length, Optional, URL, Email, NumberRange
from wtforms.widgets import TextArea


class EnhancedProfileForm(FlaskForm):
    """Comprehensive profile form with all fields"""
    
    # Basic Information
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    
    # Location
    city = StringField('City', validators=[Optional(), Length(max=100)])
    province = StringField('Province/State', validators=[Optional(), Length(max=50)])
    country = StringField('Country', validators=[Optional(), Length(max=50)])
    
    # Professional Information
    professional_title = StringField('Professional Title', 
                                    validators=[Optional(), Length(max=100)],
                                    render_kw={'placeholder': 'e.g., Software Developer, Marketing Manager'})
    
    experience_level = SelectField('Experience Level', choices=[
        ('', 'Select experience level'),
        ('entry', 'Entry Level (0-2 years)'),
        ('junior', 'Junior (2-4 years)'),
        ('mid', 'Mid Level (4-7 years)'),
        ('senior', 'Senior Level (7+ years)'),
        ('executive', 'Executive/Leadership')
    ], validators=[Optional()])
    
    # Professional Summary
    bio = TextAreaField('Professional Summary', 
                       validators=[Optional(), Length(max=1000)],
                       render_kw={'rows': 4, 'placeholder': 'Brief description of your professional background, skills, and career goals...'})
    
    # Skills
    skills = TextAreaField('Skills', 
                          validators=[Optional(), Length(max=500)],
                          render_kw={'rows': 3, 'placeholder': 'e.g., Python, JavaScript, Project Management, Data Analysis (separate with commas)'})
    
    # Profile Picture
    profile_picture = FileField('Profile Picture', 
                               validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')],
                               render_kw={'accept': 'image/*'})
    
    # Social Media & Portfolio
    linkedin_url = StringField('LinkedIn Profile', 
                              validators=[Optional(), URL()],
                              render_kw={'placeholder': 'https://linkedin.com/in/yourname'})
    
    github_url = StringField('GitHub Profile', 
                            validators=[Optional(), URL()],
                            render_kw={'placeholder': 'https://github.com/yourusername'})
    
    portfolio_url = StringField('Portfolio/Website', 
                               validators=[Optional(), URL()],
                               render_kw={'placeholder': 'https://yourportfolio.com'})
    
    twitter_url = StringField('Twitter/X Profile', 
                             validators=[Optional(), URL()],
                             render_kw={'placeholder': 'https://twitter.com/yourusername'})
    
    # Privacy Settings
    profile_public = BooleanField('Make profile visible to recruiters')
    show_contact_info = BooleanField('Show contact information on public profile')
    
    submit = SubmitField('Save Profile')


class ExperienceForm(FlaskForm):
    """Form for adding/editing work experience"""
    
    job_title = StringField('Job Title', validators=[DataRequired(), Length(max=100)])
    company = StringField('Company', validators=[DataRequired(), Length(max=100)])
    location = StringField('Location', validators=[Optional(), Length(max=100)])
    
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[Optional()])
    current_job = BooleanField('I currently work here')
    
    description = TextAreaField('Job Description', 
                               validators=[Optional(), Length(max=2000)],
                               render_kw={'rows': 5, 'placeholder': 'Describe your responsibilities, achievements, and key projects...'})
    
    submit = SubmitField('Save Experience')


class EducationForm(FlaskForm):
    """Form for adding/editing education"""
    
    degree = StringField('Degree', validators=[DataRequired(), Length(max=100)])
    institution = StringField('Institution', validators=[DataRequired(), Length(max=100)])
    field_of_study = StringField('Field of Study', validators=[Optional(), Length(max=100)])
    location = StringField('Location', validators=[Optional(), Length(max=100)])
    
    start_year = IntegerField('Start Year', validators=[Optional(), NumberRange(min=1900, max=2030)])
    end_year = IntegerField('End Year', validators=[Optional(), NumberRange(min=1900, max=2030)])
    gpa = StringField('GPA', validators=[Optional(), Length(max=10)])
    
    description = TextAreaField('Description', 
                               validators=[Optional(), Length(max=500)],
                               render_kw={'rows': 3, 'placeholder': 'Relevant coursework, achievements, projects...'})
    
    submit = SubmitField('Save Education')


class CertificationForm(FlaskForm):
    """Form for adding/editing certifications"""
    
    name = StringField('Certification Name', validators=[DataRequired(), Length(max=100)])
    issuing_organization = StringField('Issuing Organization', validators=[DataRequired(), Length(max=100)])
    
    issue_date = DateField('Issue Date', validators=[Optional()])
    expiry_date = DateField('Expiry Date', validators=[Optional()])
    credential_id = StringField('Credential ID', validators=[Optional(), Length(max=100)])
    credential_url = StringField('Credential URL', 
                                validators=[Optional(), URL()],
                                render_kw={'placeholder': 'https://credential-verification-url.com'})
    
    description = TextAreaField('Description', 
                               validators=[Optional(), Length(max=500)],
                               render_kw={'rows': 3, 'placeholder': 'Description of skills or knowledge gained...'})
    
    submit = SubmitField('Save Certification')


class SkillsForm(FlaskForm):
    """Form for managing skills with proficiency levels"""
    
    PROFICIENCY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert')
    ]
    
    skill_name = StringField('Skill', validators=[DataRequired(), Length(max=100)])
    proficiency = SelectField('Proficiency Level', choices=PROFICIENCY_CHOICES, validators=[DataRequired()])
    years_experience = IntegerField('Years of Experience', validators=[Optional(), NumberRange(min=0, max=50)])
    
    submit = SubmitField('Add Skill')


class ProfilePrivacyForm(FlaskForm):
    """Form for managing profile privacy settings"""
    
    profile_public = BooleanField('Make profile visible to recruiters')
    show_contact_info = BooleanField('Show contact information on public profile')
    show_salary_expectations = BooleanField('Show salary expectations')
    allow_recruiter_contact = BooleanField('Allow recruiters to contact me directly')
    
    # Job Search Status
    job_search_status = SelectField('Job Search Status', choices=[
        ('not_looking', 'Not looking for opportunities'),
        ('passive', 'Open to opportunities'),
        ('active', 'Actively looking'),
        ('urgent', 'Urgently seeking new role')
    ], validators=[Optional()])
    
    submit = SubmitField('Update Privacy Settings')


class SocialLinksForm(FlaskForm):
    """Dedicated form for social media links"""
    
    linkedin_url = StringField('LinkedIn Profile', 
                              validators=[Optional(), URL()],
                              render_kw={'placeholder': 'https://linkedin.com/in/yourname'})
    
    github_url = StringField('GitHub Profile', 
                            validators=[Optional(), URL()],
                            render_kw={'placeholder': 'https://github.com/yourusername'})
    
    portfolio_url = StringField('Portfolio/Website', 
                               validators=[Optional(), URL()],
                               render_kw={'placeholder': 'https://yourportfolio.com'})
    
    twitter_url = StringField('Twitter/X Profile', 
                             validators=[Optional(), URL()],
                             render_kw={'placeholder': 'https://twitter.com/yourusername'})
    
    behance_url = StringField('Behance Portfolio', 
                             validators=[Optional(), URL()],
                             render_kw={'placeholder': 'https://behance.net/yourusername'})
    
    dribbble_url = StringField('Dribbble Portfolio', 
                              validators=[Optional(), URL()],
                              render_kw={'placeholder': 'https://dribbble.com/yourusername'})
    
    submit = SubmitField('Save Social Links')
