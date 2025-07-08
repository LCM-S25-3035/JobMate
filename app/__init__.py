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
from config import config
import logging

# Initialize Flask extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
mail = Mail()
csrf = CSRFProtect()
mongo_client = None

def detect_postgresql_driver():
    """
    Detect which PostgreSQL driver is available
    """
    try:
        import psycopg
        # psycopg3 is available
        return 'psycopg'
    except ImportError:
        try:
            import psycopg2
            # psycopg2 is available
            return 'psycopg2'
        except ImportError:
            # No PostgreSQL driver available
            return None

def adjust_database_url(database_url):
    """
    Adjust DATABASE_URL to use the available PostgreSQL driver
    """
    if not database_url:
        return database_url
    
    driver = detect_postgresql_driver()
    
    # Handle different URL formats
    if 'postgresql://' in database_url and '+' not in database_url:
        # Convert generic postgresql:// to driver-specific format
        if driver == 'psycopg':
            return database_url.replace('postgresql://', 'postgresql+psycopg://')
        elif driver == 'psycopg2':
            return database_url.replace('postgresql://', 'postgresql+psycopg2://')
    elif 'postgresql+psycopg2://' in database_url and driver == 'psycopg':
        # Replace psycopg2 with psycopg (version 3)
        return database_url.replace('postgresql+psycopg2://', 'postgresql+psycopg://')
    elif 'postgresql+psycopg://' in database_url and driver == 'psycopg2':
        # Replace psycopg with psycopg2
        return database_url.replace('postgresql+psycopg://', 'postgresql+psycopg2://')
    elif driver is None:
        logging.error("No PostgreSQL driver (psycopg or psycopg2) is available!")
        return None
    
    return database_url

def create_app(config_class=None):
    """Application Factory for creating Flask app instances"""
    
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Get configuration class
    if config_class is None:
        config_name = os.environ.get('FLASK_ENV') or 'default'
        config_class = config[config_name]
    
    # Load configuration
    app.config.from_object(config_class)
    
    # Debug: Show detected driver
    detected_driver = detect_postgresql_driver()
    print(f"🔧 Detected PostgreSQL driver: {detected_driver}")
    
    # Adjust DATABASE_URL for available PostgreSQL driver
    database_url = app.config.get('SQLALCHEMY_DATABASE_URI')
    print(f"🔗 Original URL: {database_url}")
    
    adjusted_url = adjust_database_url(database_url)
    if adjusted_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = adjusted_url
        print(f"🔗 Adjusted URL: {adjusted_url}")
    else:
        print("⚠️ Warning: No PostgreSQL driver available")
    
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
        mongo_client = MongoClient(
            app.config['MONGODB_URI'],
            serverSelectionTimeoutMS=5000  # 5 second timeout
        )
        # Test connection
        mongo_client.admin.command('ping')
        app.mongo_db = mongo_client[app.config['MONGODB_DB']]
        print("✅ MongoDB connected successfully")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        app.mongo_db = None
    
    # Register Blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Core modules - implemented
    from app.resume import bp as resume_bp
    app.register_blueprint(resume_bp, url_prefix='/resume')
    
    from app.match import bp as match_bp
    app.register_blueprint(match_bp, url_prefix='/match')
    
    from app.autoapply import bp as autoapply_bp
    app.register_blueprint(autoapply_bp, url_prefix='/autoapply')
    
    # TODO: Implement dashboard module
    # # from app.dashboard import bp as dashboard_bp
    # # app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    
    from app.recruiter import bp as recruiter_bp
    app.register_blueprint(recruiter_bp, url_prefix='/recruiter')
    
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
        postgres_status = 'connected'
        try:
            db.session.execute(db.text('SELECT 1'))
        except Exception as e:
            postgres_status = f'disconnected: {str(e)}'
            
        return {
            'status': 'healthy',
            'postgres': postgres_status,
            'mongodb': 'connected' if mongo_client else 'disconnected',
            'driver': detect_postgresql_driver(),
            'database_url': app.config.get('SQLALCHEMY_DATABASE_URI', '').split('@')[1] if '@' in app.config.get('SQLALCHEMY_DATABASE_URI', '') else 'not configured'
        }
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))
    
    print(f"🚀 JobMate Flask application v{app.config.get('VERSION', '1.0.0')} created successfully!")
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