from flask import request, jsonify
from . import bp
from app.ai_agents.gemini_utils import call_gemini_api_simple

def generate_skills(job_title):
    """Generate skills suggestions using AI logic"""
    prompt = (
        f"Given the job title: {job_title}\n\n"
        f"Please suggest 5-7 relevant skills for this position. "
        f"Respond with a JSON array of strings only, like: [\"skill1\", \"skill2\", \"skill3\"]"
    )
    
    try:
        response = call_gemini_api_simple(prompt)
        if response.get('success'):
            import json
            skills = json.loads(response['content'].strip())
            return skills
        else:
            return None
    except Exception as e:
        return None

def generate_salary(job_title, location):
    """Generate salary suggestions using AI logic"""
    prompt = (
        f"Given the following job information:\n"
        f"Job Title: {job_title}\n"
        f"Location: {location}\n\n"
        f"Please suggest a salary range in CAD. "
        f"Respond with just the range format like: '65,000 - 80,000 CAD'"
    )
    
    try:
        response = call_gemini_api_simple(prompt)
        if response.get('success'):
            return response['content'].strip()
        else:
            return "70000"  # fallback
    except Exception as e:
        return "70000"  # fallback

