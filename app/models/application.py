"""
Application Model for JobMate Platform
Handles job applications and application tracking
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from app import db


class Application(db.Model):
    """
    Application model for tracking job applications
    Manages application status, documents, and communication
    """
    
    __tablename__ = 'applications'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_posting_id = db.Column(db.Integer, db.ForeignKey('job_postings.id'), nullable=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=True)
    
    # Application Details
    company_name = db.Column(db.String(200), nullable=False)
    job_title = db.Column(db.String(200), nullable=False)
    job_url = db.Column(db.String(500), nullable=True)
    job_board = db.Column(db.String(100), nullable=True)  # LinkedIn, Indeed, etc.
    
    # Application Status
    status = db.Column(db.Enum(
        'draft', 'applied', 'screening', 'interview_scheduled', 
        'interviewed', 'offer_received', 'accepted', 'rejected', 
        'withdrawn', 'no_response', name='application_status'
    ), nullable=False, default='draft')
    
    # Application Method
    application_method = db.Column(db.Enum(
        'manual', 'auto_apply', 'direct', 'referral', 
        name='application_method'
    ), nullable=False, default='manual')
    
    # Auto-Apply related fields
    auto_applied = db.Column(db.Boolean, default=False, nullable=False)
    auto_apply_match_score = db.Column(db.Integer, nullable=True)
    auto_apply_batch_id = db.Column(db.String(36), nullable=True)  # UUID for grouping auto-applications
    
    # Contact Information
    recruiter_name = db.Column(db.String(100), nullable=True)
    recruiter_email = db.Column(db.String(120), nullable=True)
    hr_contact = db.Column(db.String(100), nullable=True)
    
    # Salary Information
    salary_min = db.Column(db.Float, nullable=True)
    salary_max = db.Column(db.Float, nullable=True)
    salary_currency = db.Column(db.String(10), default='CAD')
    salary_type = db.Column(db.Enum('hourly', 'monthly', 'yearly', name='salary_type'), default='yearly')
    
    # Location
    job_location = db.Column(db.String(200), nullable=True)
    remote_type = db.Column(db.Enum('onsite', 'remote', 'hybrid', name='remote_type'), nullable=True)
    
    # Application Documents
    cover_letter = db.Column(db.Text, nullable=True)
    cover_letter_tailored = db.Column(db.Boolean, default=False)
    resume_tailored = db.Column(db.Boolean, default=False)
    additional_documents = db.Column(db.JSON, nullable=True)  # List of document paths
    
    # AI Enhancement
    ai_optimized = db.Column(db.Boolean, default=False)
    match_score = db.Column(db.Float, nullable=True)  # Job match score (0-100)
    ai_suggestions = db.Column(db.JSON, nullable=True)
    keywords_matched = db.Column(db.JSON, nullable=True)
    
    # Cross-database references - temporarily removed due to missing database column
    # mongo_application_id = db.Column(db.String(50), nullable=True)  # Reference to MongoDB application
    
    # Tracking
    application_number = db.Column(db.String(50), nullable=True)  # Company's reference number
    notes = db.Column(db.Text, nullable=True)
    follow_up_date = db.Column(db.DateTime, nullable=True)
    interview_date = db.Column(db.DateTime, nullable=True)
    
    # Response Tracking
    response_received = db.Column(db.Boolean, default=False)
    response_date = db.Column(db.DateTime, nullable=True)
    rejection_reason = db.Column(db.String(200), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    applied_at = db.Column(db.DateTime, nullable=True)
    
    def __init__(self, user_id, company_name, job_title, **kwargs):
        """Initialize application with required fields"""
        self.user_id = user_id
        self.company_name = company_name
        self.job_title = job_title
        
        # Set optional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    @property
    def is_active(self):
        """Check if application is still active"""
        active_statuses = ['draft', 'applied', 'screening', 'interview_scheduled', 'interviewed']
        return self.status in active_statuses
    
    @property
    def is_successful(self):
        """Check if application was successful"""
        return self.status in ['offer_received', 'accepted']
    
    @property
    def days_since_applied(self):
        """Calculate days since application was submitted"""
        if self.applied_at:
            return (datetime.utcnow() - self.applied_at).days
        return 0
    
    @property
    def salary_range_formatted(self):
        """Return formatted salary range"""
        if self.salary_min and self.salary_max:
            currency_symbol = {'CAD': '$', 'USD': '$', 'EUR': '€'}.get(self.salary_currency, '$')
            type_suffix = {'hourly': '/hr', 'monthly': '/mo', 'yearly': '/yr'}.get(self.salary_type, '/yr')
            
            return f"{currency_symbol}{self.salary_min:,.0f} - {currency_symbol}{self.salary_max:,.0f}{type_suffix}"
        
        return None
    
    def update_status(self, new_status, notes=None):
        """Update application status with optional notes"""
        old_status = self.status
        self.status = new_status
        
        # Set applied_at when status changes to applied
        if new_status == 'applied' and old_status != 'applied':
            self.applied_at = datetime.utcnow()
        
        # Set response_received for certain statuses
        if new_status in ['interview_scheduled', 'interviewed', 'offer_received', 'rejected']:
            self.response_received = True
            if not self.response_date:
                self.response_date = datetime.utcnow()
        
        # Add notes if provided
        if notes:
            current_notes = self.notes or ''
            timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M')
            new_note = f"[{timestamp}] Status changed to {new_status}: {notes}\n"
            self.notes = new_note + current_notes
        
        db.session.commit()
    
    def set_interview_date(self, interview_date, notes=None):
        """Set interview date and update status"""
        self.interview_date = interview_date
        self.update_status('interview_scheduled', notes)
    
    def mark_ai_optimized(self, match_score=None, suggestions=None, keywords=None):
        """Mark application as AI optimized with analysis results"""
        self.ai_optimized = True
        
        if match_score is not None:
            self.match_score = match_score
        
        if suggestions:
            self.ai_suggestions = suggestions
        
        if keywords:
            self.keywords_matched = keywords
        
        db.session.commit()
    
    def to_dict(self, include_documents=False):
        """Convert application to dictionary for API responses"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'job_posting_id': self.job_posting_id,
            'resume_id': self.resume_id,
            'company_name': self.company_name,
            'job_title': self.job_title,
            'job_url': self.job_url,
            'job_board': self.job_board,
            'status': self.status,
            'application_method': self.application_method,
            'recruiter_name': self.recruiter_name,
            'recruiter_email': self.recruiter_email,
            'salary_range_formatted': self.salary_range_formatted,
            'job_location': self.job_location,
            'remote_type': self.remote_type,
            'ai_optimized': self.ai_optimized,
            'match_score': self.match_score,
            'is_active': self.is_active,
            'is_successful': self.is_successful,
            'days_since_applied': self.days_since_applied,
            'response_received': self.response_received,
            'follow_up_date': self.follow_up_date.isoformat() if self.follow_up_date else None,
            'interview_date': self.interview_date.isoformat() if self.interview_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None,
            'response_date': self.response_date.isoformat() if self.response_date else None
        }
        
        # Include sensitive data if requested
        if include_documents:
            data.update({
                'cover_letter': self.cover_letter,
                'notes': self.notes,
                'ai_suggestions': self.ai_suggestions,
                'keywords_matched': self.keywords_matched,
                'additional_documents': self.additional_documents
            })
        
        return data
    
    @classmethod
    def get_user_applications(cls, user_id, status=None, limit=None):
        """Get applications for a user with optional filtering"""
        query = cls.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        query = query.order_by(cls.updated_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @classmethod
    def get_application_stats(cls, user_id):
        """Get application statistics for a user"""
        total = cls.query.filter_by(user_id=user_id).count()
        applied = cls.query.filter_by(user_id=user_id, status='applied').count()
        interviews = cls.query.filter_by(user_id=user_id).filter(
            cls.status.in_(['interview_scheduled', 'interviewed'])
        ).count()
        offers = cls.query.filter_by(user_id=user_id).filter(
            cls.status.in_(['offer_received', 'accepted'])
        ).count()
        rejected = cls.query.filter_by(user_id=user_id, status='rejected').count()
        
        return {
            'total': total,
            'applied': applied,
            'interviews': interviews,
            'offers': offers,
            'rejected': rejected,
            'success_rate': round((offers / total * 100) if total > 0 else 0, 1),
            'interview_rate': round((interviews / applied * 100) if applied > 0 else 0, 1)
        }
    
    def __repr__(self):
        return f'<Application {self.job_title} at {self.company_name} ({self.status})>'