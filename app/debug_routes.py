"""
Debug routes for the JobMate application
"""

from flask import Blueprint, render_template

# Create a debug blueprint
debug_bp = Blueprint('debug', __name__)

def register_debug_routes(app):
    """Register debug routes with the app"""
    app.register_blueprint(debug_bp, url_prefix='/debug')
