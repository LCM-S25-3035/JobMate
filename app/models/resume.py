"""
Resume Model for JobMate Platform
Handles resume storage, parsing, and AI-powered optimization
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from app import db


class Resume(db.Model):
    """
    Resume model for storing and managing user resumes
    Supports multiple resumes per user with AI analysis
    """
    
    __tablename__ = 'resumes'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Resume Basic Info
    title = db.Column(db.String(200), nullable=False, default='My Resume')
    filename = db.Column(db.String(255), nullable=True)  # Original filename
    file_path = db.Column(db.String(500), nullable=True)  # Storage path
    file_size = db.Column(db.Integer, nullable=True)  # File size in bytes
    file_type = db.Column(db.String(20), nullable=True)  # pdf, docx, txt
    
    # Resume Status
    is_primary = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # AI Analysis Results
    parsed_content = db.Column(db.Text, nullable=True)  # Extracted text content
    ai_analysis = db.Column(db.JSON, nullable=True)  # AI analysis results
    skills_extracted = db.Column(db.JSON, nullable=True)  # Extracted skills
    experience_years = db.Column(db.Float, nullable=True)  # Calculated experience
    education_level = db.Column(db.String(50), nullable=True)  # Highest education
    
    # ATS Optimization
    ats_score = db.Column(db.Float, nullable=True)  # ATS compatibility score (0-100)
    keyword_matches = db.Column(db.JSON, nullable=True)  # Keyword analysis
    suggestions = db.Column(db.JSON, nullable=True)  # Improvement suggestions
    
    # Usage Tracking
    view_count = db.Column(db.Integer, default=0)
    download_count = db.Column(db.Integer, default=0)
    last_viewed = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    parsed_at = db.Column(db.DateTime, nullable=True)  # When AI analysis was done
    
    def __init__(self, user_id, title='My Resume', **kwargs):
        """Initialize resume with required fields"""
        self.user_id = user_id
        self.title = title
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @property
    def file_size_mb(self):
        """Return file size in MB"""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return 0
    
    @property
    def is_parsed(self):
        """Check if resume has been parsed by AI"""
        return self.parsed_content is not None and len(self.parsed_content.strip()) > 0
    
    @property
    def has_ai_analysis(self):
        """Check if AI analysis is available"""
        return self.ai_analysis is not None
    
    def set_as_primary(self):
        """Set this resume as primary and unset others"""
        # Remove primary status from other resumes
        Resume.query.filter_by(user_id=self.user_id, is_primary=True).update({'is_primary': False})
        
        # Set this as primary
        self.is_primary = True
        db.session.commit()
    
    def increment_view_count(self):
        """Increment view count and update last viewed"""
        self.view_count += 1
        self.last_viewed = datetime.utcnow()
        db.session.commit()
    
    def increment_download_count(self):
        """Increment download count"""
        self.download_count += 1
        db.session.commit()
    
    def update_ai_analysis(self, analysis_data):
        """Update AI analysis results"""
        self.ai_analysis = analysis_data
        self.parsed_at = datetime.utcnow()
        
        # Extract key metrics from analysis
        if 'skills' in analysis_data:
            self.skills_extracted = analysis_data['skills']
        
        if 'experience_years' in analysis_data:
            self.experience_years = analysis_data['experience_years']
        
        if 'education_level' in analysis_data:
            self.education_level = analysis_data['education_level']
        
        if 'ats_score' in analysis_data:
            self.ats_score = analysis_data['ats_score']
        
        if 'suggestions' in analysis_data:
            self.suggestions = analysis_data['suggestions']
        
        db.session.commit()
    
    def to_dict(self, include_content=False):
        """Convert resume to dictionary for API responses"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'filename': self.filename,
            'file_size': self.file_size,
            'file_size_mb': self.file_size_mb,
            'file_type': self.file_type,
            'is_primary': self.is_primary,
            'is_active': self.is_active,
            'is_parsed': self.is_parsed,
            'has_ai_analysis': self.has_ai_analysis,
            'skills_extracted': self.skills_extracted,
            'experience_years': self.experience_years,
            'education_level': self.education_level,
            'ats_score': self.ats_score,
            'view_count': self.view_count,
            'download_count': self.download_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'parsed_at': self.parsed_at.isoformat() if self.parsed_at else None,
            'last_viewed': self.last_viewed.isoformat() if self.last_viewed else None
        }
        
        # Include content if requested (for AI processing)
        if include_content:
            data['parsed_content'] = self.parsed_content
            data['ai_analysis'] = self.ai_analysis
            data['keyword_matches'] = self.keyword_matches
            data['suggestions'] = self.suggestions
        
        return data
    
    @classmethod
    def get_user_resumes(cls, user_id, active_only=True):
        """Get all resumes for a user"""
        query = cls.query.filter_by(user_id=user_id)
        
        if active_only:
            query = query.filter_by(is_active=True)
        
        return query.order_by(cls.is_primary.desc(), cls.updated_at.desc()).all()
    
    @classmethod
    def get_primary_resume(cls, user_id):
        """Get user's primary resume"""
        return cls.query.filter_by(user_id=user_id, is_primary=True, is_active=True).first()
    
    def __repr__(self):
        return f'<Resume {self.title} (User: {self.user_id})>' 