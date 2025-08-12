"""
Models Package for JobMate Platform
Contains all database models and their relationships
"""

from .user import User
from .resume import Resume
from .application import Application
from .job_preference import JobPreference
from .job_posting import JobPosting
from .profile import UserExperience, UserEducation, UserCertification, UserSkill, UserSocialLink

# Export all models for easy importing
__all__ = [
    'User',
    'Resume', 
    'Application',
    'JobPreference',
    'JobPosting',
    'UserExperience',
    'UserEducation', 
    'UserCertification',
    'UserSkill',
    'UserSocialLink'
] 