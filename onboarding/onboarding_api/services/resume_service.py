import os
import json
from onboarding_api.db.resume_repository import save_resume_record
from onboarding_api.utils.file_io import call_function_from_file

def extract_resume_experience(file, user_id: str, region: str):
    """
    Handles logic to parse resume and extract data via Gemini
    from previous AutoApply functions.
    """
    # Save resume to db
    resume_id = save_resume_record(file, user_id, region)

    # Dynamically run existing Gemini parser
    try:
        call_function_from_file("utils.py", "extract_cv_information", file)
    except Exception as e:
        print(f"[ERROR] Resume parsing failed: {e}")
        return resume_id, []

    # Load extracted JSON (assumes standard format saved by Gemini parser)
    parsed_json_path = os.path.join("resume", "resume.json")
    if not os.path.exists(parsed_json_path):
        print("[WARNING] resume_extracted.json not found.")
        return resume_id, []
    try:
        with open(parsed_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            work_exps = data.get("work_experience", [])
            # Ensure it's a list of dicts
            if isinstance(work_exps, list) and all(isinstance(w, dict) for w in work_exps):
                return resume_id, work_exps
            else:
                print("[WARNING] Parsed work_experience is not valid.")
                return resume_id, []
    except Exception as e:
        print(f"[ERROR] Failed to load parsed resume JSON: {e}")
        return resume_id, []

# Reference: 
# OpenAI 4o: Getting error "AttributeError: 'str' object has no attribute 'get'"