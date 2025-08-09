"""
Jobs Module for JobMate
Handles job scraping, search, and management
"""

from flask import Blueprint

bp = Blueprint('jobs', __name__)

from app.jobs import routes
from app.jobs import ghost_details_api