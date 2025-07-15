"""
Job Description Utilities
Utilities for parsing and extracting information from job descriptions
"""

import re
import json
from app.ai_agents.gemini_utils import call_gemini_api

def extract_job_positions(job_description, use_ai=False, min_confidence=70):
    """
    Extract potential job positions/titles from a job description.
    
    Args:
        job_description (str): The job description text
        use_ai (bool): Whether to use AI for extraction (more accurate but slower)
        min_confidence (int): Minimum confidence score (0-100) to include a position
    
    Returns:
        list: A list of dictionaries with job titles and confidence scores
    """
    
    # Basic pattern-based extraction
    positions = []
    
    # Common patterns for job titles
    patterns = [
        r"(?:job title|position title|role|position|hiring for|looking for|seeking|hiring a|hiring an)\s*(?:a|an|:|\s-\s)?\s*(?P<title>[A-Z][A-Za-z\s\-\/&]+(?:\s?[IV]+)?)",
        r"(?P<title>[A-Z][A-Za-z\s\-\/]+(?:\s?[IV]+)?)\s*(?:position|role|job)",
        r"^(?P<title>[A-Z][A-Za-z0-9\s\-\/&]+(?:\s?[IV]+)?)$",  # Standalone capitalized lines
    ]
    
    # Extract using patterns
    for pattern in patterns:
        for match in re.finditer(pattern, job_description, re.MULTILINE):
            title = match.group('title').strip()
            # Filter out common non-title phrases
            if (len(title.split()) <= 6 and  # Most job titles are 1-5 words
                not any(w in title.lower() for w in ['etc', 'following', 'qualification', 'experience'])):
                positions.append({
                    'title': title,
                    'confidence': 80,  # Default confidence for pattern matches
                    'method': 'pattern'
                })
    
    # NLP-based extraction (simplified)
    # Look for capitalized phrases that look like job titles
    title_candidates = re.findall(r'(?:^|(?<=[.!?]\s))([A-Z][a-zA-Z\s\-\/&]+?(?:Developer|Engineer|Designer|Analyst|Manager|Specialist|Consultant|Architect|Administrator|Director|Lead|Officer|Associate|Executive|Coordinator))\b', job_description)
    
    for candidate in title_candidates:
        candidate = candidate.strip()
        if 3 <= len(candidate.split()) <= 6:  # Most job titles are 3-6 words
            positions.append({
                'title': candidate,
                'confidence': 70,  # Lower confidence for NLP detection
                'method': 'nlp'
            })
    
    # Use AI model for extraction if requested
    if use_ai:
        prompt = f"""
        Extract all potential job position titles from this job description.
        Return a JSON array of objects, each with 'title' and 'confidence' (0-100) properties.
        
        Job description:
        {job_description}
        """
        
        api_response = call_gemini_api(prompt, temperature=0.1)
        
        try:
            # Extract the text content from the Gemini API response structure
            if (isinstance(api_response, dict) and
                'candidates' in api_response and
                len(api_response['candidates']) > 0 and
                'content' in api_response['candidates'][0] and
                'parts' in api_response['candidates'][0]['content'] and
                len(api_response['candidates'][0]['content']['parts']) > 0 and
                'text' in api_response['candidates'][0]['content']['parts'][0]):
                
                response_text = api_response['candidates'][0]['content']['parts'][0]['text']
                
                # Try to extract a JSON array from the response
                match = re.search(r'\[[\s\S]*\]', response_text)
                if match:
                    json_str = match.group(0)
                    ai_positions = json.loads(json_str)
                    for pos in ai_positions:
                        if isinstance(pos, dict) and 'title' in pos:
                            pos['method'] = 'ai'
                            positions.append(pos)
            else:
                print(f"Unexpected API response structure: {str(api_response)[:100]}...")
        except Exception as e:
            print(f"Error parsing AI response: {str(e)}")
    
    # Filter, deduplicate, and sort results
    result = []
    seen_titles = set()
    
    for pos in positions:
        title = pos['title'].strip()
        title_lower = title.lower()
        
        # Skip if we've seen this title or similar
        if title_lower in seen_titles or any(title_lower in t for t in seen_titles):
            continue
        
        # Skip if confidence is too low
        if pos.get('confidence', 0) < min_confidence:
            continue
        
        # Clean up the title
        title = re.sub(r'\s+', ' ', title)  # Remove extra spaces
        title = title.strip(' :/,.-')  # Remove trailing punctuation
        
        # Add to results
        seen_titles.add(title_lower)
        result.append({
            'title': title,
            'confidence': pos.get('confidence', 70),
            'method': pos.get('method', 'pattern')
        })
    
    # Sort by confidence (highest first)
    result.sort(key=lambda x: x.get('confidence', 0), reverse=True)
    
    return result
