"""
Match Module for JobMate
Handles job-to-candidate matching and recommendations
"""

from flask import Blueprint

bp = Blueprint('match', __name__)

from app.match import routes 