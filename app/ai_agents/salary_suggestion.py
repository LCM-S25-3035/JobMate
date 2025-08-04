
def get_salary_suggestion(title, location, experience_level=None):
    pass
from app.ai_agents.gemini_utils import call_gemini_api_simple
from app.ai_agents.glassdoor_utils import get_glassdoor_salary

def suggest_salary(job_title, location, experience_level=None):
    # Normalize inputs
    job_title = job_title.strip().title()
    location = location.strip().title()
    if experience_level:
        experience_level = experience_level.strip().title()

    # Try Glassdoor first
    try:
        glassdoor_salary = get_glassdoor_salary(job_title, location, experience_level)
        if glassdoor_salary:
            return {'salary_range': glassdoor_salary, 'explanation': 'Based on Glassdoor data.'}
    except Exception as e:
        print("Glassdoor error:", str(e))

    # Fallback to Gemini
    prompt = f"""
You are a salary intelligence assistant.\n\nBased on publicly available salary data and your knowledge of the job market in Canada, what is the typical salary range in **CAD** for the following role:\n\n- Job Title: {job_title}\n- Location: {location}\n- Experience Level: {experience_level if experience_level else 'Not specified'}\n\nPlease provide:\n1. Estimated annual salary range in CAD (e.g., C$50,000 - C$65,000)\n2. A short explanation or reasoning based on market trends or regional factors.\n3. If data is unclear or insufficient, say \"UNKNOWN\" instead of guessing.\n\nKeep the output concise and structured.\n"""
    try:
        print("Calling Gemini for:", job_title, location, experience_level)
        result = call_gemini_api_simple(prompt)
        print("Gemini response:", result)
        import re
        text = result.get('content') if isinstance(result, dict) else result
        if not text or 'UNKNOWN' in text.upper():
            return None
        salary_match = re.search(r'Salary Range[:\s]*([\w$,. \-–]+)', text, re.IGNORECASE)
        explanation_match = re.search(r'Reasoning[:\s]*(.+)', text, re.IGNORECASE)
        salary_range = salary_match.group(1).strip() if salary_match else None
        explanation = explanation_match.group(1).strip() if explanation_match else None
        if salary_range:
            return {'salary_range': salary_range, 'explanation': explanation}
    except Exception as e:
        print("Gemini error:", str(e))
        return {"salary_range": None, "explanation": "No salary available due to error."}
    return None

# For backward compatibility
get_salary_suggestion = suggest_salary
