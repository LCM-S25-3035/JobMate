# app/ai_agents/routes.py

from flask import Blueprint, request, jsonify
from . import bp
from app.ai_agents.suggestions import generate_skills, generate_salary

@bp.route("/suggest_skills", methods=["POST"])
def suggest_skills():
    print("🔥 suggest_skills called")
    data = request.get_json()
    print("Payload:", data)
    job_title = data.get("job_title", "")
    
    skills = generate_skills(job_title)
    
    if skills:
        return jsonify({"suggested_skills": skills})
    else:
        return jsonify({"error": "Unable to generate skills"}), 500

@bp.route("/suggest_salary", methods=["POST"])
def suggest_salary():
    print("🔥 suggest_salary called")
    data = request.get_json()
    print("Payload:", data)
    job_title = data.get("job_title", "")
    location = data.get("location", "")
    
    salary = generate_salary(job_title, location)
    
    return jsonify({
        "job_title": job_title,
        "location": location,
        "suggested_salary": salary
    })
