"""
Simple test profile routes to debug the issue
"""

from flask import Blueprint, render_template
from flask_login import login_required, current_user

# Import the blueprint from the same module
from . import bp

@bp.route('/test')
def test():
    """Simple test route"""
    return "Enhanced Profile Test - Routes are working!"

@bp.route('/enhanced')
@login_required  
def enhanced_profile():
    """Enhanced profile page"""
    return f"Enhanced Profile for {current_user.full_name if current_user else 'Anonymous'}"
