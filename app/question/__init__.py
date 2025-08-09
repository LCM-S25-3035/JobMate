"""
Question Generator Module for JobMate
Provides AI-powered interview question generation capabilities
"""

from flask import Blueprint

# Create the blueprint for the question module
question_bp = Blueprint('question', __name__)

# Import routes after blueprint creation to avoid circular imports
from . import routes

# Make the blueprint available for import
__all__ = ['question_bp']
