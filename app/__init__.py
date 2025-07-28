<<<<<<< Updated upstream
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

    # Added absolute paths for template and static directories
    base_dir = os.path.abspath(os.path.dirname(__file__))
    template_dir = os.path.join(base_dir, '..', 'templates')
    static_dir = os.path.join(base_dir, '..', 'static')

    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    
    @app.template_filter('nl2br')
    def nl2br_filter(s):
        return s.replace('\n', '<br>\n') if s else ''

    
    from dotenv import load_dotenv
    load_dotenv() 
    
    # CSRF protection from Flask-WTF - To fix “Bad Request – The CSRF token is missing.”
    app.config['SECRET_KEY']  = os.getenv('SECRET_KEY')  

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
    
    # TODO: Implement dashboard module
    # # from app.dashboard import bp as dashboard_bp
    # # app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    
    from app.recruiter import bp as recruiter_bp
    app.register_blueprint(recruiter_bp, url_prefix='/recruiter')
    
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.jobs import bp as jobs_bp
    app.register_blueprint(jobs_bp, url_prefix='/jobs')

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
=======
"""
JobMate - AI-Enhanced Job Matching Platform
Flask Application Factory Pattern
"""

from flask import Flask, app, render_template, flash, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect, CSRFError
from pymongo import MongoClient
from config import config
import os
import logging

# Initialize Flask extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
mail = Mail()
csrf = CSRFProtect()
mongo_client = None

def detect_postgresql_driver():
    try:
        import psycopg
        return 'psycopg'
    except ImportError:
        try:
            import psycopg2
            return 'psycopg2'
        except ImportError:
            return None

def adjust_database_url(database_url):
    if not database_url:
        return database_url
    
    driver = detect_postgresql_driver()
    
    if 'postgresql://' in database_url and '+' not in database_url:
        if driver == 'psycopg':
            return database_url.replace('postgresql://', 'postgresql+psycopg://')
        elif driver == 'psycopg2':
            return database_url.replace('postgresql://', 'postgresql+psycopg2://')
    elif 'postgresql+psycopg2://' in database_url and driver == 'psycopg':
        return database_url.replace('postgresql+psycopg2://', 'postgresql+psycopg://')
    elif 'postgresql+psycopg://' in database_url and driver == 'psycopg2':
        return database_url.replace('postgresql+psycopg://', 'postgresql+psycopg2://')
    elif driver is None:
        logging.error("No PostgreSQL driver (psycopg or psycopg2) is available!")
        return None

    return database_url

from app import csrf 

def create_app(config_class=None):
    
    """Application Factory for creating Flask app instances"""

    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    base_dir = os.path.abspath(os.path.dirname(__file__))
    template_dir = os.path.join(base_dir, '..', 'templates')
    static_dir = os.path.join(base_dir, '..', 'static')

    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    
    csrf.init_app(app) 

    # Register custom template filters
    @app.template_filter('nl2br')
    def nl2br_filter(s):
        return s.replace('\n', '<br>\n') if s else ''

    # Load configuration
    if config_class is None:
        config_name = os.environ.get('FLASK_ENV') or 'default'
        config_class = config[config_name]
    app.config.from_object(config_class)

    # Ensure SECRET_KEY is set
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    print(f"🔐 SECRET_KEY configured: {'Yes' if app.config.get('SECRET_KEY') else 'No'}")

    # Configure WTF CSRF settings
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_TIME_LIMIT'] = None  # No time limit
    app.config['WTF_CSRF_SSL_STRICT'] = False  # Allow HTTP in development
    
    # Session configuration for CSRF (ChatGPT's recommendation)
    app.config['SESSION_COOKIE_SECURE'] = False  # False for HTTP in development
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    # Enable detailed logging for debugging
    if app.config.get('FLASK_ENV') == 'development':
        import logging
        logging.basicConfig(level=logging.DEBUG)
        app.logger.setLevel(logging.DEBUG)
        print("🔍 DEBUG logging enabled")

    # Detect and adjust DB driver
    detected_driver = detect_postgresql_driver()
    print(f"🔧 Detected PostgreSQL driver: {detected_driver}")

    database_url = app.config.get('SQLALCHEMY_DATABASE_URI')
    print(f"🔗 Original URL: {database_url}")
    adjusted_url = adjust_database_url(database_url)
    if adjusted_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = adjusted_url
        print(f"🔗 Adjusted URL: {adjusted_url}")
    else:
        print("⚠️ Warning: No PostgreSQL driver available")

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    csrf.init_app(app)

    # Handle CSRF errors
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        print(f"🚨 CSRF Error: {e.description}")
        flash('Security token expired. Please try again.', 'error')
        return redirect(request.url)

    # Make CSRF token available in templates


    # Debug endpoint to test CSRF token generation
    @app.route('/debug/csrf')
    def debug_csrf():
        from flask import jsonify, session
        from flask_wtf.csrf import generate_csrf
        try:
            token = generate_csrf()
            return jsonify({
                'csrf_token': token,
                'csrf_token_length': len(token) if token else 0,
                'secret_key_exists': bool(app.config.get('SECRET_KEY')),
                'secret_key_length': len(app.config.get('SECRET_KEY', '')) if app.config.get('SECRET_KEY') else 0,
                'csrf_enabled': app.config.get('WTF_CSRF_ENABLED', 'Not set'),
                'session_keys': list(session.keys()) if session else [],
                'session_has_csrf': '_csrf_token' in session if session else False
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # Flask-Login setup
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    # MongoDB connection
    global mongo_client
    try:
        mongo_client = MongoClient(
            app.config['MONGODB_URI'],
            serverSelectionTimeoutMS=5000
        )
        mongo_client.admin.command('ping')
        app.mongo_db = mongo_client[app.config['MONGODB_DB']]
        print("✅ MongoDB connected successfully")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        app.mongo_db = None

    # Register Blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.resume import bp as resume_bp
    app.register_blueprint(resume_bp, url_prefix='/resume')

    from app.match import bp as match_bp
    app.register_blueprint(match_bp, url_prefix='/match')

    from app.recruiter import bp as recruiter_bp
    app.register_blueprint(recruiter_bp, url_prefix='/recruiter')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.jobs import bp as jobs_bp
    app.register_blueprint(jobs_bp, url_prefix='/jobs')

    from app.ai_agents import bp as ai_bp
    app.register_blueprint(ai_bp, url_prefix="/ai/api")

    from app.autoapply import bp as autoapply_bp
    app.register_blueprint(autoapply_bp, url_prefix='/autoapply')

    # Print all registered routes for debugging
    print("🔍 Registered Routes:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.methods} -> {rule.rule}")

    # Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('errors/csrf_error.html', reason=e.description), 400

    # Health Check
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

    # User Loader
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))

    print(f"🚀 JobMate Flask application v{app.config.get('VERSION', '1.0.0')} created successfully!")
    return app

def create_database_tables(app):
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully")

def cleanup_mongo():
    global mongo_client
    if mongo_client:
        mongo_client.close()

>>>>>>> Stashed changes
