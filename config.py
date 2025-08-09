"""
JobMate Configuration Module
Environment-based configuration for different deployment stages
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    """Base configuration class with common settings"""
    
    # Application Version
    VERSION = '1.0.1'
    
    # Core Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'jobmate-super-secret-key-change-in-production'
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 120,
        'pool_pre_ping': True
    }
    
    # MongoDB Configuration
    MONGODB_URI = os.environ.get('MONGODB_URI') # or 'mongodb://localhost:27017/'
    MONGODB_DB = os.environ.get('MONGODB_DB') # or 'jobmate_mongo'
    
    # Redis Configuration (for Celery)
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # Mail Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@jobmate.com'
    
    # SMTP Configuration (for direct email sending)
    SMTP_SERVER = os.environ.get('SMTP_SERVER') or 'smtp.gmail.com'
    SMTP_PORT = int(os.environ.get('SMTP_PORT') or 587)
    SMTP_USER = os.environ.get('SMTP_USER') or MAIL_USERNAME
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD') or MAIL_PASSWORD
    SMTP_USE_TLS = os.environ.get('SMTP_USE_TLS', 'true').lower() in ['true', 'on', '1']
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}
    
    # AI/ML Configuration
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    GEMINI_MODEL = os.environ.get('GEMINI_MODEL') or 'gemini-1.5-flash'
    
    
    # Security Configuration
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'false').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Pagination
    JOBS_PER_PAGE = 20
    CANDIDATES_PER_PAGE = 15
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/1'
    
    # Celery Configuration
    CELERY_BROKER_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    
    # Feature Flags
    ENABLE_AI_RESUME_PARSING = os.environ.get('ENABLE_AI_RESUME_PARSING', 'true').lower() == 'true'
    ENABLE_AUTO_APPLY = os.environ.get('ENABLE_AUTO_APPLY', 'true').lower() == 'true'
    ENABLE_JOB_SCRAPING = os.environ.get('ENABLE_JOB_SCRAPING', 'true').lower() == 'true'


class DevelopmentConfig(Config):
    """Development environment configuration"""
    
    DEBUG = True
    TESTING = False
    
    # Development database (local PostgreSQL)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Development MongoDB
    MONGODB_DB = 'job_automation'
    
    # Disable CSRF for easier development
    WTF_CSRF_ENABLED = True
    
    # Less strict security in development
    SESSION_COOKIE_SECURE = False


class TestingConfig(Config):
    """Testing environment configuration"""
    
    TESTING = True
    DEBUG = False
    
    # Use SQLite for testing (faster)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Testing MongoDB
    MONGODB_DB = 'jobmate_test'
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Disable rate limiting for tests
    RATELIMIT_ENABLED = False


class ProductionConfig(Config):
    """Production environment configuration"""
    
    DEBUG = False
    TESTING = False
    
    # Production database from environment
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    MONGODB_URI = os.environ.get('MONGODB_URI')
    REDIS_URL = os.environ.get('REDIS_URL')
    
    # Strict security in production
    SESSION_COOKIE_SECURE = True
    WTF_CSRF_ENABLED = True
    
    # Production logging
    LOG_LEVEL = 'WARNING'


class DockerConfig(Config):
    """Docker environment configuration"""
    
    DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    
    # Docker service names
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    MONGODB_URI = os.environ.get('MONGODB_URI') or 'mongodb://mongodb:27017/'
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://redis:6379/0'


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'docker': DockerConfig,
    'default': DevelopmentConfig
} 