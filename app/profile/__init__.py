"""
Profile Module for JobMate
Handles user profile management and job preferences
"""

from flask import Blueprint

bp = Blueprint('user_profile', __name__)

from . import routes 