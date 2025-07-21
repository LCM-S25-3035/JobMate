"""
Debug routes for application monitoring and troubleshooting
"""

from flask import Blueprint

bp = Blueprint('debug', __name__)

from app.debug import mongodb_routes
