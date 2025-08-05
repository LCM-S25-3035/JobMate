from app.ai_agents.gemini_utils import call_gemini_api_simple

def suggest_skills(job_title, max_skills=15):
    """
    Get AI-powered skills suggestions based on job title using Gemini.
    
    Args:
        job_title (str): The job title to suggest skills for
        max_skills (int): Maximum number of skills to suggest (default: 15)
    
    Returns:
        list: List of suggested skills, or empty list if unavailable
    """
    if not job_title or len(job_title.strip()) < 2:
        return []
    
    # Normalize input
    job_title = job_title.strip().title()
    
    # Create AI prompt for skills suggestion
    prompt = f"""
You are a skills intelligence assistant with expertise in job market requirements.

Based on the job title "{job_title}", suggest the most relevant and in-demand skills that candidates should possess for this role.

**Guidelines:**
- Provide exactly {max_skills} skills maximum
- Focus on the most essential and commonly required skills
- Include both technical and soft skills where appropriate
- Consider current industry standards and trends
- Skills should be specific and actionable
- Avoid overly generic skills like "communication" unless truly essential for the role

**Format your response as a simple comma-separated list:**
Skill1, Skill2, Skill3, Skill4, Skill5, Skill6, Skill7, Skill8, Skill9, Skill10

**Example for "Frontend Developer":**
JavaScript, React, HTML, CSS, TypeScript, Node.js, Git, Responsive Design, REST APIs, Agile, Vue.js, SASS, Webpack, Testing, UX/UI

**Now provide skills for: {job_title}**
"""

    try:
        print(f"Requesting skills suggestions from Gemini for: {job_title}")
        result = call_gemini_api_simple(prompt)
        print(f"Gemini skills response received for {job_title}")
        
        # Parse the response
        text = result.get('content') if isinstance(result, dict) else result
        
        if not text:
            return []
        
        # Extract skills from the response
        # Look for comma-separated list
        lines = text.strip().split('\n')
        skills_line = None
        
        # Find the line with skills (should be comma-separated)
        for line in lines:
            line = line.strip()
            if ',' in line and not line.startswith('#') and not line.startswith('*'):
                # Remove any leading labels like "Skills:" or "Suggested:"
                if ':' in line:
                    line = line.split(':', 1)[1].strip()
                skills_line = line
                break
        
        if not skills_line:
            # If no comma-separated line found, try to extract from the whole response
            skills_line = text.strip()
        
        # Parse skills
        skills = []
        if skills_line:
            raw_skills = skills_line.split(',')
            for skill in raw_skills:
                skill = skill.strip()
                # Clean up skill names (remove numbers, bullets, etc.)
                skill = skill.split('.', 1)[-1].strip()  # Remove "1. " type prefixes
                skill = skill.split(')', 1)[-1].strip()  # Remove "1) " type prefixes
                
                if skill and len(skill) > 1 and len(skill) < 50:  # Reasonable skill name length
                    skills.append(skill)
                
                if len(skills) >= max_skills:
                    break
        
        # Return up to max_skills
        return skills[:max_skills] if skills else []
        
    except Exception as e:
        print(f"Gemini AI skills suggestion error: {str(e)}")
        return []

# For backward compatibility and alternative function name
get_skills_suggestion = suggest_skills
