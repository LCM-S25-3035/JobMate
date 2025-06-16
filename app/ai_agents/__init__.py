"""
AI Agents Module for JobMate
Handles all Gemini-powered AI microservices:
- Resume parsing and analysis
- Job description analysis
- Match scoring
- Resume tailoring
- Ghost job detection
- Interview question generation
"""

from flask import Blueprint

bp = Blueprint('ai_agents', __name__)

# from app.ai_agents import routes  # TODO: Implement routes.py 