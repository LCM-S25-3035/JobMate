import os
import requests

def get_glassdoor_salary(title, location, experience_level=None):
    """
    Query the Glassdoor API for salary data based on job title, location, and experience level.
    Returns a string like '65000 - 90000 CAD' or None if not found.
    """
    partner_id = os.getenv('GLASSDOOR_PARTNER_ID')
    api_key = os.getenv('GLASSDOOR_API_KEY')
    if not partner_id or not api_key:
        return None

    # Glassdoor API endpoint (example, may need adjustment for your actual API access)
    endpoint = 'https://api.glassdoor.com/api/api.htm'
    params = {
        't.p': partner_id,
        't.k': api_key,
        'userip': '0.0.0.0',  # Glassdoor requires a user IP
        'useragent': 'Mozilla/5.0',
        'format': 'json',
        'v': '1',
        'action': 'jobs-salaries',
        'jobTitle': title,
        'location': location,
    }
    if experience_level:
        params['experienceLevel'] = experience_level

    try:
        resp = requests.get(endpoint, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        # Parse the response for salary range (this may need to be adjusted for your API version)
        if 'response' in data and 'payPercentiles' in data['response']:
            pay = data['response']['payPercentiles']
            min_salary = int(pay.get('percentile10', 0))
            max_salary = int(pay.get('percentile90', 0))
            if min_salary and max_salary:
                return f"{min_salary} - {max_salary} CAD"
        # Fallback: try to parse other fields if available
        if 'response' in data and 'salaries' in data['response']:
            salaries = data['response']['salaries']
            if salaries and isinstance(salaries, list):
                min_salary = int(salaries[0].get('min', 0))
                max_salary = int(salaries[0].get('max', 0))
                if min_salary and max_salary:
                    return f"{min_salary} - {max_salary} CAD"
    except Exception as e:
        print(f"Glassdoor API error: {e}")
    return None
