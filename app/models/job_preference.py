"""
Job Preference Model for JobMate Platform
Handles user job preferences for AI-powered matching
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from app import db


class JobPreference(db.Model):
    """
    JobPreference model for storing user job search preferences
    Used by AI matching system to find relevant opportunities
    """
    
    __tablename__ = 'job_preferences'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Job Search Preferences
    desired_job_titles = db.Column(db.JSON, nullable=True)  # List of job titles
    preferred_industries = db.Column(db.JSON, nullable=True)  # List of industries
    skills = db.Column(db.JSON, nullable=True)  # Required/preferred skills
    experience_level = db.Column(db.Enum(
        'entry', 'junior', 'mid', 'senior', 'lead', 'executive',
        name='experience_level'
    ), nullable=True)
    
    # Location Preferences
    preferred_locations = db.Column(db.JSON, nullable=True)  # List of cities/regions
    remote_preference = db.Column(db.Enum(
        'onsite_only', 'remote_only', 'hybrid_preferred', 'flexible',
        name='remote_preference'
    ), default='flexible')
    willing_to_relocate = db.Column(db.Boolean, default=False)
    commute_distance = db.Column(db.Integer, nullable=True)  # Max commute in km
    
    # Salary Expectations
    min_salary = db.Column(db.Float, nullable=True)
    max_salary = db.Column(db.Float, nullable=True)
    salary_currency = db.Column(db.String(10), default='CAD')
    salary_type = db.Column(db.Enum('hourly', 'monthly', 'yearly', name='salary_type'), default='yearly')
    salary_negotiable = db.Column(db.Boolean, default=True)
    
    # Employment Type
    employment_types = db.Column(db.JSON, nullable=True)  # full-time, part-time, contract, etc.
    contract_duration_min = db.Column(db.Integer, nullable=True)  # Minimum contract months
    contract_duration_max = db.Column(db.Integer, nullable=True)  # Maximum contract months
    
    # Company Preferences
    company_sizes = db.Column(db.JSON, nullable=True)  # startup, small, medium, large, enterprise
    company_types = db.Column(db.JSON, nullable=True)  # public, private, nonprofit, etc.
    preferred_companies = db.Column(db.JSON, nullable=True)  # List of specific companies
    excluded_companies = db.Column(db.JSON, nullable=True)  # Companies to avoid
    
    # Benefits & Perks
    required_benefits = db.Column(db.JSON, nullable=True)  # Must-have benefits
    preferred_benefits = db.Column(db.JSON, nullable=True)  # Nice-to-have benefits
    work_life_balance_priority = db.Column(db.Enum(
        'low', 'medium', 'high', 'critical',
        name='priority_level'
    ), default='medium')
    
    # Job Search Settings
    job_search_status = db.Column(db.Enum(
        'not_searching', 'passively_looking', 'actively_searching', 'urgently_searching',
        name='search_status'
    ), default='not_searching')
    availability = db.Column(db.Enum(
        'immediate', 'two_weeks', 'one_month', 'two_months', 'flexible',
        name='availability'
    ), default='flexible')
    
    # Notification Preferences
    email_notifications = db.Column(db.Boolean, default=True)
    push_notifications = db.Column(db.Boolean, default=True)
    notification_frequency = db.Column(db.Enum(
        'real_time', 'daily', 'weekly', 'bi_weekly',
        name='notification_frequency'
    ), default='daily')
    
    # AI Matching Preferences
    matching_enabled = db.Column(db.Boolean, default=True)
    auto_apply_enabled = db.Column(db.Boolean, default=False)
    match_threshold = db.Column(db.Float, default=70.0)  # Minimum match score (0-100)
    
    # Privacy Settings
    profile_visibility = db.Column(db.Enum(
        'public', 'recruiter_only', 'private',
        name='visibility'
    ), default='recruiter_only')
    allow_headhunter_contact = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_job_search_activity = db.Column(db.DateTime, nullable=True)
    
    def __init__(self, user_id, **kwargs):
        """Initialize job preferences with user ID"""
        self.user_id = user_id
        
        # Set default preferences for new users
        self.desired_job_titles = []
        self.preferred_industries = []
        self.skills = []
        self.preferred_locations = []
        self.employment_types = ['full-time']
        self.company_sizes = ['small', 'medium', 'large']
        self.required_benefits = []
        self.preferred_benefits = []
        
        # Override with provided values
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @property
    def is_actively_searching(self):
        """Check if user is actively job searching"""
        return self.job_search_status in ['actively_searching', 'urgently_searching']
    
    @property
    def salary_range_formatted(self):
        """Return formatted salary range"""
        if self.min_salary and self.max_salary:
            currency_symbol = {'CAD': '$', 'USD': '$', 'EUR': '€'}.get(self.salary_currency, '$')
            type_suffix = {'hourly': '/hr', 'monthly': '/mo', 'yearly': '/yr'}.get(self.salary_type, '/yr')
            
            return f"{currency_symbol}{self.min_salary:,.0f} - {currency_symbol}{self.max_salary:,.0f}{type_suffix}"
        elif self.min_salary:
            currency_symbol = {'CAD': '$', 'USD': '$', 'EUR': '€'}.get(self.salary_currency, '$')
            type_suffix = {'hourly': '/hr', 'monthly': '/mo', 'yearly': '/yr'}.get(self.salary_type, '/yr')
            return f"{currency_symbol}{self.min_salary:,.0f}+{type_suffix}"
        
        return "Negotiable"
    
    def add_skill(self, skill):
        """Add a skill to the user's skill list"""
        if not self.skills:
            self.skills = []
        
        if skill not in self.skills:
            self.skills.append(skill)
            db.session.commit()
    
    def remove_skill(self, skill):
        """Remove a skill from the user's skill list"""
        if self.skills and skill in self.skills:
            self.skills.remove(skill)
            db.session.commit()
    
    def add_preferred_location(self, location):
        """Add a location to preferred locations"""
        if not self.preferred_locations:
            self.preferred_locations = []
        
        if location not in self.preferred_locations:
            self.preferred_locations.append(location)
            db.session.commit()
    
    def update_job_search_activity(self):
        """Update last job search activity timestamp"""
        self.last_job_search_activity = datetime.utcnow()
        db.session.commit()
    
    def calculate_match_score(self, job_data):
        """Calculate match score for a job posting (0-100)"""
        score = 0
        factors = 0
        
        # Job title match
        if self.desired_job_titles and job_data.get('title'):
            for desired_title in self.desired_job_titles:
                if desired_title.lower() in job_data['title'].lower():
                    score += 25
                    break
        factors += 1
        
        # Location match
        if self.preferred_locations and job_data.get('location'):
            for pref_location in self.preferred_locations:
                if pref_location.lower() in job_data['location'].lower():
                    score += 20
                    break
        elif self.remote_preference == 'remote_only' and job_data.get('remote'):
            score += 20
        factors += 1
        
        # Salary match
        if self.min_salary and job_data.get('salary_min'):
            if job_data['salary_min'] >= self.min_salary:
                score += 15
        factors += 1
        
        # Skills match
        if self.skills and job_data.get('required_skills'):
            matched_skills = len(set(self.skills) & set(job_data['required_skills']))
            skill_percentage = matched_skills / len(job_data['required_skills']) * 100
            score += min(skill_percentage * 0.4, 40)  # Max 40 points for skills
        factors += 1
        
        # Normalize score
        return min(score, 100)
    
    def to_dict(self, include_private=False):
        """Convert preferences to dictionary for API responses"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'desired_job_titles': self.desired_job_titles,
            'preferred_industries': self.preferred_industries,
            'skills': self.skills,
            'experience_level': self.experience_level,
            'preferred_locations': self.preferred_locations,
            'remote_preference': self.remote_preference,
            'willing_to_relocate': self.willing_to_relocate,
            'salary_range_formatted': self.salary_range_formatted,
            'employment_types': self.employment_types,
            'company_sizes': self.company_sizes,
            'job_search_status': self.job_search_status,
            'availability': self.availability,
            'is_actively_searching': self.is_actively_searching,
            'matching_enabled': self.matching_enabled,
            'match_threshold': self.match_threshold,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        # Include private data if requested
        if include_private:
            data.update({
                'min_salary': self.min_salary,
                'max_salary': self.max_salary,
                'salary_currency': self.salary_currency,
                'salary_type': self.salary_type,
                'required_benefits': self.required_benefits,
                'preferred_benefits': self.preferred_benefits,
                'preferred_companies': self.preferred_companies,
                'excluded_companies': self.excluded_companies,
                'email_notifications': self.email_notifications,
                'push_notifications': self.push_notifications,
                'notification_frequency': self.notification_frequency,
                'auto_apply_enabled': self.auto_apply_enabled,
                'profile_visibility': self.profile_visibility,
                'allow_headhunter_contact': self.allow_headhunter_contact
            })
        
        return data
    
    @classmethod
    def get_by_user_id(cls, user_id):
        """Get job preferences for a specific user"""
        return cls.query.filter_by(user_id=user_id).first()
    
    @classmethod
    def get_active_job_seekers(cls):
        """Get all users who are actively job searching"""
        return cls.query.filter(
            cls.job_search_status.in_(['actively_searching', 'urgently_searching']),
            cls.matching_enabled == True
        ).all()
    
    def __repr__(self):
        return f'<JobPreference User: {self.user_id} ({self.job_search_status})>' 