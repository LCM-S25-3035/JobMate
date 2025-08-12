import os
from app import create_app

app = create_app()

# Add SQLAlchemy config here
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

if __name__ == '__main__':
    # Use PORT from environment (Render sets this) or default to 5002
    port = int(os.environ.get('PORT', 5002))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port) 