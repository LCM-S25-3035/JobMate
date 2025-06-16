"""
Authentication Module for JobMate
Handles user registration, login, logout, and password management
"""

from flask import Blueprint

bp = Blueprint('auth', __name__)

from app.auth import routes 