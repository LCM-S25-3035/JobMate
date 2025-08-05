
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
        
        # Parse the response
        text = result.get('content') if isinstance(result, dict) else result
        
        if not text or 'INSUFFICIENT_DATA' in text.upper():
            return {
                'salary_range': 'Data unavailable', 
                'explanation': 'Insufficient market data for this role and location.'
            }
        
        # Extract salary range and explanation
        import re
        salary_match = re.search(r'Salary Range[:\s]*(C?\$?[\d,\s\-–]+(?:CAD|C\$[\d,\s\-–]+)?)', text, re.IGNORECASE)
        explanation_match = re.search(r'Reasoning[:\s]*(.+?)(?:\n|$)', text, re.IGNORECASE | re.DOTALL)
        
        salary_range = salary_match.group(1).strip() if salary_match else None
        explanation = explanation_match.group(1).strip() if explanation_match else None
        
        # Clean up salary range format
        if salary_range:
            # Ensure CAD is included
            if 'CAD' not in salary_range and 'C$' not in salary_range:
                salary_range = f"{salary_range} CAD"
            
            return {
                'salary_range': salary_range,
                'explanation': explanation or 'Based on current Canadian market analysis.'
            }
        else:
            return {
                'salary_range': 'Range not available',
                'explanation': 'Unable to determine salary range from market data.'
            }
            
    except Exception as e:
        print(f"Gemini AI salary suggestion error: {str(e)}")
        return {
            'salary_range': 'Service unavailable', 
            'explanation': 'Salary suggestion service is temporarily unavailable.'
        }

# For backward compatibility
get_salary_suggestion = suggest_salary
