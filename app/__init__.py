"""
JobMate - AI-Enhanced Job Matching Platform
Flask Application Factory Pattern Implementation
"""

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from pymongo import MongoClient
import os
from config import Config

# Initialize Flask extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
mail = Mail()
csrf = CSRFProtect()
mongo_client = None


def create_app(config_class=Config):
    """Application Factory for creating Flask app instances"""
    
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Load configuration
    app.config.from_object(config_class)
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    csrf.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Initialize MongoDB connection
    global mongo_client
    try:
        mongo_client = MongoClient(app.config['MONGODB_URI'])
        app.mongo_db = mongo_client[app.config['MONGODB_DB']]
        print("✅ MongoDB connected successfully")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        app.mongo_db = None
    
    # Register Blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # TODO: Implement remaining modules
    # from app.profile import bp as profile_bp
    # app.register_blueprint(profile_bp, url_prefix='/profile')
    
    # from app.resume import bp as resume_bp
    # app.register_blueprint(resume_bp, url_prefix='/resume')
    
    # from app.jobs import bp as jobs_bp
    # app.register_blueprint(jobs_bp, url_prefix='/jobs')
    
    # from app.match import bp as match_bp
    # app.register_blueprint(match_bp, url_prefix='/match')
    
    # from app.apply import bp as apply_bp
    # app.register_blueprint(apply_bp, url_prefix='/apply')
    
    # from app.recruiter import bp as recruiter_bp
    # app.register_blueprint(recruiter_bp, url_prefix='/recruiter')
    
    # from app.ai_agents import bp as ai_agents_bp
    # app.register_blueprint(ai_agents_bp, url_prefix='/ai')
    
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {
            'status': 'healthy',
            'postgres': 'connected' if db.engine else 'disconnected',
            'mongodb': 'connected' if mongo_client else 'disconnected'
        }
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))
    
    print("🚀 JobMate Flask application created successfully!")
    return app


def create_database_tables(app):
    """Create database tables if they don't exist"""
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully")


# Cleanup function for MongoDB connection
def cleanup_mongo():
    global mongo_client
    if mongo_client:
        mongo_client.close()
        print("📦 MongoDB connection closed") 