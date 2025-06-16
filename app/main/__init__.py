"""
Main Module for JobMate
Handles main application routes including dashboards and landing pages
"""

from flask import Blueprint

bp = Blueprint('main', __name__)

from app.main import routes 
from app.models.application import Application
from app.models.job_posting import JobPosting 