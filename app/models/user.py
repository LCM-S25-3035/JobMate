"""
User Model for JobMate Platform
Supports both Applicant and Recruiter user types
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    """
    User model for authentication and profile management
    Supports both Applicant and Recruiter roles
    """
    
    __tablename__ = 'users'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Authentication Fields
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    verification_token = db.Column(db.String(100), unique=True, nullable=True)
    
    # Profile Fields
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    
    # User Role
    user_type = db.Column(db.Enum('applicant', 'recruiter', name='user_types'), 
                         nullable=False, default='applicant')
    
    # Location Information
    city = db.Column(db.String(100), nullable=True)
    province = db.Column(db.String(50), nullable=True)
    country = db.Column(db.String(50), default='Canada')
    
    # Profile Completion
    profile_completed = db.Column(db.Boolean, default=False)
    onboarding_completed = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    resumes = db.relationship('Resume', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    applications = db.relationship('Application', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    job_preferences = db.relationship('JobPreference', backref='user', uselist=False, cascade='all, delete-orphan')
    job_postings = db.relationship('JobPosting', backref='recruiter', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, email, password, first_name, last_name, user_type='applicant', **kwargs):
        """Initialize user with required fields"""
        self.email = email.lower().strip()
        self.set_password(password)
        self.first_name = first_name.strip()
        self.last_name = last_name.strip()
        self.user_type = user_type
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        """Return full name"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def location(self):
        """Return formatted location"""
        if self.city and self.province:
            return f"{self.city}, {self.province}"
        elif self.city:
            return self.city
        elif self.province:
            return self.province
        return self.country or 'Canada'
    
    def is_applicant(self):
        """Check if user is an applicant"""
        return self.user_type == 'applicant'
    
    def is_recruiter(self):
        """Check if user is a recruiter"""
        return self.user_type == 'recruiter'
    
    def get_active_resume(self):
        """Get user's primary/active resume"""
        return self.resumes.filter_by(is_primary=True, is_active=True).first()
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary for API responses"""
        data = {
            'id': self.id,
            'email': self.email if include_sensitive else None,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'user_type': self.user_type,
            'city': self.city,
            'province': self.province,
            'country': self.country,
            'location': self.location,
            'profile_completed': self.profile_completed,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        
        # Remove None values
        return {k: v for k, v in data.items() if v is not None}
    
    @classmethod
    def find_by_email(cls, email):
        """Find user by email address"""
        return cls.query.filter_by(email=email.lower().strip()).first()
    
    @classmethod
    def create_user(cls, email, password, first_name, last_name, user_type='applicant', **kwargs):
        """Create a new user with validation"""
        # Check if email already exists
        if cls.find_by_email(email):
            raise ValueError("Email already registered")
        
        # Create new user
        user = cls(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            user_type=user_type,
            **kwargs
        )
        
        db.session.add(user)
        db.session.commit()
        return user
    
    def __repr__(self):
        return f'<User {self.email} ({self.user_type})>' 