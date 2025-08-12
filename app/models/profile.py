"""
Enhanced Profile Models for JobMate
Models to support comprehensive user profiles with experience, education, skills, etc.
"""

from datetime import datetime
from app import db


class UserExperience(db.Model):
    """Model for user work experience"""
    
    __tablename__ = 'user_experiences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Job Information
    job_title = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=True)
    
    # Dates
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    is_current = db.Column(db.Boolean, default=False)
    
    # Description
    description = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('experiences', lazy='dynamic', cascade='all, delete-orphan'))
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'job_title': self.job_title,
            'company': self.company,
            'location': self.location,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_current': self.is_current,
            'description': self.description,
            'duration': self.get_duration_text()
        }
    
    def get_duration_text(self):
        """Get human-readable duration text"""
        if not self.start_date:
            return ""
        
        end = self.end_date if self.end_date else datetime.now().date()
        duration = end - self.start_date
        
        years = duration.days // 365
        months = (duration.days % 365) // 30
        
        if years > 0 and months > 0:
            return f"{years} year{'s' if years > 1 else ''}, {months} month{'s' if months > 1 else ''}"
        elif years > 0:
            return f"{years} year{'s' if years > 1 else ''}"
        elif months > 0:
            return f"{months} month{'s' if months > 1 else ''}"
        else:
            return "Less than a month"
    
    def __repr__(self):
        return f'<UserExperience {self.job_title} at {self.company}>'


class UserEducation(db.Model):
    """Model for user education"""
    
    __tablename__ = 'user_educations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Education Information
    degree = db.Column(db.String(100), nullable=False)
    institution = db.Column(db.String(100), nullable=False)
    field_of_study = db.Column(db.String(100), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    
    # Academic Details
    start_year = db.Column(db.Integer, nullable=True)
    end_year = db.Column(db.Integer, nullable=True)
    gpa = db.Column(db.String(10), nullable=True)
    
    # Description
    description = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('educations', lazy='dynamic', cascade='all, delete-orphan'))
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'degree': self.degree,
            'institution': self.institution,
            'field_of_study': self.field_of_study,
            'location': self.location,
            'start_year': self.start_year,
            'end_year': self.end_year,
            'gpa': self.gpa,
            'description': self.description,
            'year_range': self.get_year_range_text()
        }
    
    def get_year_range_text(self):
        """Get human-readable year range"""
        if self.start_year and self.end_year:
            return f"{self.start_year} - {self.end_year}"
        elif self.start_year:
            return f"{self.start_year} - Present"
        elif self.end_year:
            return str(self.end_year)
        return ""
    
    def __repr__(self):
        return f'<UserEducation {self.degree} from {self.institution}>'


class UserCertification(db.Model):
    """Model for user certifications"""
    
    __tablename__ = 'user_certifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Certification Information
    name = db.Column(db.String(100), nullable=False)
    issuing_organization = db.Column(db.String(100), nullable=False)
    
    # Dates and Credentials
    issue_date = db.Column(db.Date, nullable=True)
    expiry_date = db.Column(db.Date, nullable=True)
    credential_id = db.Column(db.String(100), nullable=True)
    credential_url = db.Column(db.String(200), nullable=True)
    
    # Description
    description = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('certifications', lazy='dynamic', cascade='all, delete-orphan'))
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'issuing_organization': self.issuing_organization,
            'issue_date': self.issue_date.isoformat() if self.issue_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'credential_id': self.credential_id,
            'credential_url': self.credential_url,
            'description': self.description,
            'is_expired': self.is_expired()
        }
    
    def is_expired(self):
        """Check if certification is expired"""
        if not self.expiry_date:
            return False
        return self.expiry_date < datetime.now().date()
    
    def __repr__(self):
        return f'<UserCertification {self.name} from {self.issuing_organization}>'


class UserSkill(db.Model):
    """Model for user skills with proficiency levels"""
    
    __tablename__ = 'user_skills'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Skill Information
    name = db.Column(db.String(100), nullable=False)
    proficiency = db.Column(db.Enum('beginner', 'intermediate', 'advanced', 'expert', name='skill_proficiency'), 
                           nullable=False, default='intermediate')
    years_experience = db.Column(db.Integer, nullable=True)
    
    # Skill Category (can be populated automatically or by user)
    category = db.Column(db.String(50), nullable=True)  # e.g., 'Technical', 'Language', 'Soft Skills'
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('user_skills', lazy='dynamic', cascade='all, delete-orphan'))
    
    # Unique constraint to prevent duplicate skills per user
    __table_args__ = (db.UniqueConstraint('user_id', 'name', name='unique_user_skill'),)
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'proficiency': self.proficiency,
            'years_experience': self.years_experience,
            'category': self.category,
            'proficiency_level': self.get_proficiency_level()
        }
    
    def get_proficiency_level(self):
        """Get numeric proficiency level (1-5)"""
        levels = {
            'beginner': 1,
            'intermediate': 2, 
            'advanced': 3,
            'expert': 4
        }
        return levels.get(self.proficiency, 2)
    
    @classmethod
    def categorize_skill(cls, skill_name):
        """Automatically categorize skill based on name"""
        skill_lower = skill_name.lower()
        
        # Technical skills
        tech_keywords = ['python', 'java', 'javascript', 'sql', 'html', 'css', 'react', 'node', 'aws', 'docker', 'git']
        if any(keyword in skill_lower for keyword in tech_keywords):
            return 'Technical'
        
        # Language skills
        language_keywords = ['english', 'french', 'spanish', 'mandarin', 'german', 'arabic']
        if any(keyword in skill_lower for keyword in language_keywords):
            return 'Language'
        
        # Design skills
        design_keywords = ['photoshop', 'illustrator', 'figma', 'sketch', 'design', 'ui', 'ux']
        if any(keyword in skill_lower for keyword in design_keywords):
            return 'Design'
        
        # Management skills
        mgmt_keywords = ['management', 'leadership', 'project', 'agile', 'scrum']
        if any(keyword in skill_lower for keyword in mgmt_keywords):
            return 'Management'
        
        return 'Other'
    
    def __repr__(self):
        return f'<UserSkill {self.name} ({self.proficiency})>'


class UserSocialLink(db.Model):
    """Model for user social media and portfolio links"""
    
    __tablename__ = 'user_social_links'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Social Link Information
    platform = db.Column(db.String(50), nullable=False)  # 'linkedin', 'github', 'twitter', etc.
    url = db.Column(db.String(200), nullable=False)
    display_name = db.Column(db.String(100), nullable=True)  # Custom display name
    
    # Visibility
    is_public = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('social_links', lazy='dynamic', cascade='all, delete-orphan'))
    
    # Unique constraint to prevent duplicate platforms per user
    __table_args__ = (db.UniqueConstraint('user_id', 'platform', name='unique_user_platform'),)
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'platform': self.platform,
            'url': self.url,
            'display_name': self.display_name,
            'is_public': self.is_public,
            'icon_class': self.get_icon_class()
        }
    
    def get_icon_class(self):
        """Get Bootstrap icon class for the platform"""
        icon_map = {
            'linkedin': 'bi-linkedin',
            'github': 'bi-github',
            'twitter': 'bi-twitter',
            'portfolio': 'bi-globe',
            'behance': 'bi-behance',
            'dribbble': 'bi-dribbble',
            'instagram': 'bi-instagram',
            'facebook': 'bi-facebook'
        }
        return icon_map.get(self.platform, 'bi-link')
    
    def __repr__(self):
        return f'<UserSocialLink {self.platform}: {self.url}>'
