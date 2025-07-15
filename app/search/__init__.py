"""
Search Blueprint for JobMate
Handles job search functionality
"""

from flask import Blueprint

bp = Blueprint('search', __name__, url_prefix='/search')

# Import routes after blueprint creation to avoid circular imports
from app.search import routes 