"""
AutoApplySettings Model for JobMate Platform
Handles user preferences for the auto-apply feature
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from app import db
import json

class AutoApplySettings(db.Model):
    """
    AutoApplySettings model for storing user preferences for automatic job applications
    """
    
    __tablename__ = 'auto_apply_settings'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign Key to User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Core Settings
    enabled = db.Column(db.Boolean, default=False, nullable=False)
    max_daily = db.Column(db.Integer, default=5, nullable=False)
    min_match_score = db.Column(db.Integer, default=80, nullable=False)
    
    # Advanced Settings
    cover_letter_type = db.Column(db.Enum('none', 'generic', 'custom', name='cover_letter_types'), 
                                default='generic', nullable=False)
    preferred_job_types = db.Column(db.Enum('all', 'full_time', 'remote', 'full_time_remote', 
                                         name='preferred_job_types'), 
                                  default='all', nullable=False)
    
    # Additional JSON-based preferences (for extensibility)
    additional_preferences = db.Column(db.Text, nullable=True)
    
    # Last run information
    last_run_at = db.Column(db.DateTime, nullable=True)
    today_application_count = db.Column(db.Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('auto_apply_settings', uselist=False))
    
    def __repr__(self):
        return f'<AutoApplySettings {self.id} for user {self.user_id}>'
    
    def to_dict(self):
        """Convert settings to a dictionary for easy access in templates"""
        data = {
            'enabled': self.enabled,
            'max_daily': self.max_daily,
            'min_match_score': self.min_match_score,
            'cover_letter_type': self.cover_letter_type,
            'preferred_job_types': self.preferred_job_types,
            'last_run_at': self.last_run_at,
            'today_application_count': self.today_application_count
        }
        
        # Add additional preferences if present
        if self.additional_preferences:
            try:
                additional = json.loads(self.additional_preferences)
                data.update(additional)
            except (json.JSONDecodeError, TypeError):
                pass
                
        return data
