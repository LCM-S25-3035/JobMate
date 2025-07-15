"""
Job Posting Model for JobMate Platform
Handles job postings from recruiters and job boards
"""

from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from app import db
from sqlalchemy.dialects.postgresql import ENUM


class JobPosting(db.Model):
    """
    JobPosting model for storing job opportunities
    Supports both internal recruiter postings and external job board imports
    """
    
    __tablename__ = 'job_postings'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Key (optional for external postings)
    recruiter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Basic Job Information
    title = db.Column(db.String(200), nullable=False, index=True)
    company_name = db.Column(db.String(200), nullable=False, index=True)
    department = db.Column(db.String(100), nullable=True)
    team = db.Column(db.String(100), nullable=True)
    
    # Job Description
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text, nullable=True)
    responsibilities = db.Column(db.Text, nullable=True)
    benefits = db.Column(db.Text, nullable=True)
    
    # Skills and Experience
    required_skills = db.Column(db.JSON, nullable=True)  # List of required skills
    preferred_skills = db.Column(db.JSON, nullable=True)  # List of preferred skills
    experience_level = db.Column(db.Enum(
        'entry', 'junior', 'mid', 'senior', 'lead', 'executive',
        name='job_experience_level'
    ), nullable=True)
    min_experience_years = db.Column(db.Integer, nullable=True)
    max_experience_years = db.Column(db.Integer, nullable=True)
    
    # Education Requirements
    education_level = db.Column(db.Enum(
        'high_school', 'college', 'bachelor', 'master', 'phd', 'certification',
        name='education_level'
    ), nullable=True)
    education_field = db.Column(db.String(100), nullable=True)
    certifications_required = db.Column(db.JSON, nullable=True)
    
    # Employment Details
    employment_type = db.Column(db.Enum(
        'full_time', 'part_time', 'contract', 'temporary', 'internship', 'co_op',
        name='employment_type'
    ), nullable=False, default='full_time')
    contract_duration = db.Column(db.Integer, nullable=True)  # Duration in months for contracts
    
    # Location and Remote
    location = db.Column(db.String(200), nullable=True, index=True)
    city = db.Column(db.String(100), nullable=True, index=True)
    province = db.Column(db.String(50), nullable=True)
    country = db.Column(db.String(50), default='Canada')
    postal_code = db.Column(db.String(20), nullable=True)
    
    
    work_setting = db.Column(
        ENUM('office', 'remote', 'hybrid', name='work_setting_type', create_type=False),
        nullable=False
    )
    remote_percentage = db.Column(db.Integer, nullable=True)  # For hybrid jobs
    
    # Salary Information
    salary_min = db.Column(db.Float, nullable=True)
    salary_max = db.Column(db.Float, nullable=True)
    salary_currency = db.Column(db.String(10), default='CAD')
    salary_type = db.Column(db.Enum('hourly', 'monthly', 'yearly', name='job_salary_type'), default='yearly')
    salary_disclosed = db.Column(db.Boolean, default=True)
    
    # Company Information
    company_size = db.Column(db.Enum(
        'startup', 'small', 'medium', 'large', 'enterprise',
        name='company_size'
    ), nullable=True)
    company_type = db.Column(db.Enum(
        'public', 'private', 'nonprofit', 'government', 'startup',
        name='company_type'
    ), nullable=True)
    industry = db.Column(db.String(100), nullable=True, index=True)
    company_website = db.Column(db.String(500), nullable=True)
    company_logo_url = db.Column(db.String(500), nullable=True)
    
    # Application Details
    application_email = db.Column(db.String(120), nullable=True)
    application_url = db.Column(db.String(500), nullable=True)
    application_instructions = db.Column(db.Text, nullable=True)
    
    # Job Status
    status = db.Column(db.Enum(
        'draft', 'active', 'paused', 'filled', 'expired', 'cancelled',
        name='job_status'
    ), nullable=False, default='draft')
    
    # External Source Information
    source = db.Column(db.Enum(
        'internal', 'linkedin', 'indeed', 'glassdoor', 'workopolis', 'monster', 'other',
        name='job_source'
    ), default='internal')
    external_id = db.Column(db.String(200), nullable=True)  # ID from external source
    external_url = db.Column(db.String(500), nullable=True)  # Original URL
    
    # AI and Matching
    ai_processed = db.Column(db.Boolean, default=False)
    keywords = db.Column(db.JSON, nullable=True)  # Extracted keywords
    ai_summary = db.Column(db.Text, nullable=True)  # AI-generated summary
    match_score_threshold = db.Column(db.Float, default=60.0)  # Minimum match score for candidates
    
    # Metrics and Tracking
    view_count = db.Column(db.Integer, default=0)
    application_count = db.Column(db.Integer, default=0)
    featured = db.Column(db.Boolean, default=False)
    urgent = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime, nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True, index=True)
    filled_at = db.Column(db.DateTime, nullable=True)
    
    def __init__(self, title, company_name, description, **kwargs):
        """Initialize job posting with required fields"""
        self.title = title
        self.company_name = company_name
        self.description = description
        
        # Set default expiration (30 days from creation)
        self.expires_at = datetime.utcnow() + timedelta(days=30)
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @property
    def is_active(self):
        """Check if job posting is currently active"""
        return (self.status == 'active' and 
                (not self.expires_at or self.expires_at > datetime.utcnow()))
    
    @property
    def is_expired(self):
        """Check if job posting has expired"""
        return self.expires_at and self.expires_at <= datetime.utcnow()
    
    @property
    def days_remaining(self):
        """Calculate days remaining until expiration"""
        if self.expires_at:
            delta = self.expires_at - datetime.utcnow()
            return max(0, delta.days)
        return None
    
    @property
    def salary_range_formatted(self):
        """Return formatted salary range"""
        if self.salary_min and self.salary_max:
            currency_symbol = {'CAD': '$', 'USD': '$', 'EUR': '€'}.get(self.salary_currency, '$')
            type_suffix = {'hourly': '/hr', 'monthly': '/mo', 'yearly': '/yr'}.get(self.salary_type, '/yr')
            
            return f"{currency_symbol}{self.salary_min:,.0f} - {currency_symbol}{self.salary_max:,.0f}{type_suffix}"
        elif self.salary_min:
            currency_symbol = {'CAD': '$', 'USD': '$', 'EUR': '€'}.get(self.salary_currency, '$')
            type_suffix = {'hourly': '/hr', 'monthly': '/mo', 'yearly': '/yr'}.get(self.salary_type, '/yr')
            return f"{currency_symbol}{self.salary_min:,.0f}+{type_suffix}"
        
        return "Competitive" if not self.salary_disclosed else "Not disclosed"
    
    @property
    def location_formatted(self):
        """Return formatted location string"""
        if self.remote_type == 'remote':
            return f"Remote ({self.country})"
        elif self.remote_type == 'hybrid':
            base_location = f"{self.city}, {self.province}" if self.city and self.province else self.location
            return f"{base_location} (Hybrid)"
        else:
            return f"{self.city}, {self.province}" if self.city and self.province else self.location
    
    def publish(self):
        """Publish the job posting"""
        self.status = 'active'
        self.published_at = datetime.utcnow()
        db.session.commit()
    
    def pause(self):
        """Pause the job posting"""
        self.status = 'paused'
        db.session.commit()
    
    def mark_filled(self):
        """Mark job as filled"""
        self.status = 'filled'
        self.filled_at = datetime.utcnow()
        db.session.commit()
    
    def extend_expiration(self, days=30):
        """Extend job posting expiration"""
        if self.expires_at:
            self.expires_at = max(self.expires_at, datetime.utcnow()) + timedelta(days=days)
        else:
            self.expires_at = datetime.utcnow() + timedelta(days=days)
        db.session.commit()
    
    def increment_view_count(self):
        """Increment view count"""
        self.view_count += 1
        db.session.commit()
    
    def increment_application_count(self):
        """Increment application count"""
        self.application_count += 1
        db.session.commit()
    
    def update_ai_analysis(self, keywords=None, summary=None):
        """Update AI analysis results"""
        self.ai_processed = True
        
        if keywords:
            self.keywords = keywords
        
        if summary:
            self.ai_summary = summary
        
        db.session.commit()
    
    def to_dict(self, include_sensitive=False):
        """Convert job posting to dictionary for API responses"""
        data = {
            'id': self.id,
            'title': self.title,
            'company_name': self.company_name,
            'department': self.department,
            'description': self.description,
            'requirements': self.requirements,
            'responsibilities': self.responsibilities,
            'benefits': self.benefits,
            'required_skills': self.required_skills,
            'preferred_skills': self.preferred_skills,
            'experience_level': self.experience_level,
            'education_level': self.education_level,
            'employment_type': self.employment_type,
            'location_formatted': self.location_formatted,
            'remote_type': self.remote_type,
            'salary_range_formatted': self.salary_range_formatted,
            'company_size': self.company_size,
            'company_type': self.company_type,
            'industry': self.industry,
            'status': self.status,
            'source': self.source,
            'is_active': self.is_active,
            'is_expired': self.is_expired,
            'days_remaining': self.days_remaining,
            'view_count': self.view_count,
            'application_count': self.application_count,
            'featured': self.featured,
            'urgent': self.urgent,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }
        
        # Include sensitive data if requested (for recruiters/admins)
        if include_sensitive:
            data.update({
                'recruiter_id': self.recruiter_id,
                'application_email': self.application_email,
                'application_url': self.application_url,
                'application_instructions': self.application_instructions,
                'external_id': self.external_id,
                'external_url': self.external_url,
                'keywords': self.keywords,
                'ai_summary': self.ai_summary
            })
        
        return data
    
    @classmethod
    def get_active_jobs(cls, limit=None, location=None, remote_type=None, skills=None):
        """Get active job postings with optional filtering"""
        query = cls.query.filter_by(status='active').filter(
            cls.expires_at > datetime.utcnow()
        )
        
        if location:
            query = query.filter(cls.city.ilike(f'%{location}%'))
        
        if remote_type:
            query = query.filter_by(remote_type=remote_type)
        
        if skills:
            # Filter by required skills (simplified - in production use full-text search)
            for skill in skills:
                query = query.filter(cls.required_skills.contains([skill]))
        
        query = query.order_by(cls.featured.desc(), cls.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @classmethod
    def get_recruiter_jobs(cls, recruiter_id):
        """Get all jobs posted by a specific recruiter"""
        return cls.query.filter_by(recruiter_id=recruiter_id).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def search_jobs(cls, search_term, location=None):
        """Search jobs by title, company, or description"""
        query = cls.query.filter_by(status='active').filter(
            cls.expires_at > datetime.utcnow()
        )
        
        if search_term:
            search_filter = f'%{search_term}%'
            query = query.filter(
                db.or_(
                    cls.title.ilike(search_filter),
                    cls.company_name.ilike(search_filter),
                    cls.description.ilike(search_filter)
                )
            )
        
        if location:
            query = query.filter(cls.city.ilike(f'%{location}%'))
        
        return query.order_by(cls.featured.desc(), cls.created_at.desc()).all()
    
    def __repr__(self):
        return f'<JobPosting {self.title} at {self.company_name} ({self.status})>' 
