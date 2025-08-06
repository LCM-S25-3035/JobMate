
def get_salary_suggestion(title, location, experience_level=None):
    pass

from app.ai_agents.gemini_utils import call_gemini_api_simple

def suggest_salary(job_title, location, experience_level=None):
    """
    Get AI-powered salary suggestion using Gemini for Canadian job market.
    
    Args:
        job_title (str): The job title
        location (str): Location (city, province, or region)
        experience_level (str, optional): Experience level (entry, mid, senior, etc.)
    
    Returns:
        dict: Contains 'salary_range' and 'explanation' keys, or None if unavailable
    """
    # Normalize inputs
    job_title = job_title.strip().title()
    location = location.strip().title()
    if experience_level:
        experience_level = experience_level.strip().title()

    # Use Gemini AI for salary intelligence
    prompt = f"""
You are a salary intelligence assistant with expertise in the Canadian job market.

Based on current market data and salary trends in Canada, provide a realistic salary range for:

**Job Details:**
- Job Title: {job_title}
- Location: {location}
- Experience Level: {experience_level if experience_level else 'Not specified'}

**Please provide:**
1. Annual salary range in Canadian Dollars (format: C$XX,XXX - C$XX,XXX)
2. Brief explanation considering:
   - Regional market conditions
   - Industry standards
   - Experience level requirements
   - Current market trends in Canada

**Guidelines:**
- Use realistic, market-competitive ranges
- Consider cost of living in the specified location
- If insufficient data exists, respond with "INSUFFICIENT_DATA"
- Always specify amounts in CAD

**Format your response as:**
Salary Range: [range]
Reasoning: [explanation]
"""

    try:
        print(f"Requesting salary data from Gemini for: {job_title} in {location}")
        result = call_gemini_api_simple(prompt)
        print(f"Gemini salary response received for {job_title}")
        
        # Check if the API call was successful
        if isinstance(result, dict) and not result.get('success', False):
            print(f"Gemini API error: {result.get('error', 'Unknown error')}")
            return get_fallback_salary_estimate(job_title, location, experience_level)
        
        # Parse the response
        text = result.get('content') if isinstance(result, dict) else str(result)
        
        if not text or 'INSUFFICIENT_DATA' in text.upper():
            print("Insufficient data from Gemini, using fallback")
            return get_fallback_salary_estimate(job_title, location, experience_level)
        
        # Extract salary range and explanation
        import re
        salary_match = re.search(r'Salary Range[:\s]*(C?\$?[\d,\s\-–]+(?:CAD|C\$[\d,\s\-–]+)?)', text, re.IGNORECASE)
        explanation_match = re.search(r'Reasoning[:\s]*(.+?)(?:\n|$)', text, re.IGNORECASE | re.DOTALL)
        
        salary_range = salary_match.group(1).strip() if salary_match else None
        explanation = explanation_match.group(1).strip() if explanation_match else None
        
        # Clean up salary range format
        if salary_range:
            # Ensure CAD is included
            if salary_range and 'CAD' not in salary_range and 'C$' not in salary_range:
                salary_range = f"{salary_range} CAD"
            
            return {
                'salary_range': salary_range,
                'explanation': explanation or 'Based on current Canadian market analysis.'
            }
        else:
            # Return fallback salary estimates when AI is unavailable
            return get_fallback_salary_estimate(job_title, location, experience_level)
            
    except Exception as e:
        print(f"Gemini AI salary suggestion error: {str(e)}")
        # Return fallback salary estimates when AI service fails
        return get_fallback_salary_estimate(job_title, location, experience_level)

def get_fallback_salary_estimate(job_title, location, experience_level):
    """Provide fallback salary estimates when AI service is unavailable"""
    
    # Basic salary ranges for common tech roles in Canada
    base_salaries = {
        'data analyst': {'min': 55000, 'max': 85000},
        'software engineer': {'min': 70000, 'max': 120000},
        'software developer': {'min': 65000, 'max': 110000},
        'product manager': {'min': 80000, 'max': 130000},
        'data scientist': {'min': 75000, 'max': 125000},
        'devops engineer': {'min': 80000, 'max': 135000},
        'frontend developer': {'min': 60000, 'max': 105000},
        'backend developer': {'min': 70000, 'max': 115000},
        'full stack developer': {'min': 65000, 'max': 110000},
        'qa engineer': {'min': 55000, 'max': 90000},
        'system administrator': {'min': 60000, 'max': 95000},
        'business analyst': {'min': 60000, 'max': 95000},
        'project manager': {'min': 70000, 'max': 110000},
        'ui/ux designer': {'min': 55000, 'max': 90000},
        'marketing manager': {'min': 60000, 'max': 100000}
    }
    
    # Experience level multipliers
    experience_multipliers = {
        'entry': 0.8,
        'junior': 0.85,
        'mid': 1.0,
        'senior': 1.3,
        'lead': 1.5,
        'principal': 1.7
    }
    
    # Location multipliers (Toronto/Vancouver are more expensive)
    location_multiplier = 1.0
    if location and any(city in location.lower() for city in ['toronto', 'vancouver', 'ottawa']):
        location_multiplier = 1.15
    elif location and any(city in location.lower() for city in ['montreal', 'calgary', 'edmonton']):
        location_multiplier = 1.05
    
    # Find matching job title
    job_key = None
    job_title_lower = job_title.lower()
    for key in base_salaries.keys():
        # Check for exact match or if key words are in the job title
        if (key == job_title_lower or 
            key in job_title_lower or 
            job_title_lower in key or
            any(word in job_title_lower for word in key.split()) or
            any(word in key for word in job_title_lower.split())):
            job_key = key
            break
    
    if job_key:
        base_min = base_salaries[job_key]['min']
        base_max = base_salaries[job_key]['max']
        
        # Apply experience level multiplier
        exp_mult = experience_multipliers.get(experience_level.lower() if experience_level else 'mid', 1.0)
        
        # Apply location multiplier
        adjusted_min = int(base_min * exp_mult * location_multiplier)
        adjusted_max = int(base_max * exp_mult * location_multiplier)
        
        return {
            'salary_range': f"${adjusted_min:,} - ${adjusted_max:,} CAD",
            'explanation': f'Estimated range based on {experience_level or "mid-level"} {job_title} positions in {location or "Canada"} (AI service temporarily unavailable)'
        }
    else:
        # Generic fallback for unknown job titles
        return {
            'salary_range': '$55,000 - $95,000 CAD',
            'explanation': 'General salary range for tech positions in Canada (AI service temporarily unavailable)'
        }

# For backward compatibility
get_salary_suggestion = suggest_salary
