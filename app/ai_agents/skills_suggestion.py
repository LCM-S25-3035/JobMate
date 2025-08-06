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
        
        # Check if the API call was successful
        if isinstance(result, dict) and not result.get('success', False):
            print(f"Gemini API error: {result.get('error', 'Unknown error')}")
            return get_fallback_skills(job_title, max_skills)
        
        # Parse the response
        text = result.get('content') if isinstance(result, dict) else str(result)
        
        if not text:
            print("No content from Gemini, using fallback")
            return get_fallback_skills(job_title, max_skills)
        
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
        return skills[:max_skills] if skills else get_fallback_skills(job_title, max_skills)
        
    except Exception as e:
        print(f"Gemini AI skills suggestion error: {str(e)}")
        return get_fallback_skills(job_title, max_skills)

def get_fallback_skills(job_title, max_skills=15):
    """Provide fallback skills when AI service is unavailable"""
    
    job_title_lower = job_title.lower()
    
    # Predefined skills for common job titles
    skills_database = {
        'data analyst': [
            'Python', 'SQL', 'Excel', 'Tableau', 'Power BI', 'R', 'Statistics',
            'Data Visualization', 'Machine Learning', 'Pandas', 'NumPy', 'ETL',
            'Business Intelligence', 'Data Mining', 'Analytics'
        ],
        'software engineer': [
            'Python', 'Java', 'JavaScript', 'Git', 'APIs', 'Docker', 'SQL',
            'Agile', 'System Design', 'Testing', 'Debugging', 'Cloud Computing',
            'Microservices', 'DevOps', 'Object-Oriented Programming'
        ],
        'software developer': [
            'Programming', 'Git', 'JavaScript', 'Python', 'Java', 'SQL', 'APIs',
            'Testing', 'Debugging', 'Agile', 'Problem Solving', 'Version Control',
            'Web Development', 'Database Design', 'Software Architecture'
        ],
        'frontend developer': [
            'JavaScript', 'React', 'HTML', 'CSS', 'TypeScript', 'Vue.js', 'Angular',
            'Responsive Design', 'Git', 'REST APIs', 'SASS', 'Webpack', 'Testing',
            'UI/UX', 'Cross-browser Compatibility'
        ],
        'backend developer': [
            'Python', 'Java', 'Node.js', 'SQL', 'APIs', 'Microservices', 'Docker',
            'Git', 'Database Design', 'System Architecture', 'Security', 'Testing',
            'Cloud Services', 'Performance Optimization', 'DevOps'
        ],
        'full stack developer': [
            'JavaScript', 'Python', 'React', 'Node.js', 'SQL', 'HTML', 'CSS',
            'Git', 'APIs', 'Database Design', 'Testing', 'Agile', 'DevOps',
            'System Design', 'Problem Solving'
        ],
        'data scientist': [
            'Python', 'R', 'Machine Learning', 'Statistics', 'SQL', 'Pandas',
            'NumPy', 'Scikit-learn', 'TensorFlow', 'Data Visualization', 'Jupyter',
            'Deep Learning', 'Feature Engineering', 'Model Deployment', 'Big Data'
        ],
        'product manager': [
            'Product Strategy', 'Agile', 'Scrum', 'Market Research', 'Analytics',
            'Roadmap Planning', 'Stakeholder Management', 'User Research', 'Wireframing',
            'A/B Testing', 'SQL', 'Project Management', 'Leadership', 'Communication', 'Prioritization'
        ],
        'devops engineer': [
            'Docker', 'Kubernetes', 'AWS', 'CI/CD', 'Jenkins', 'Git', 'Linux',
            'Terraform', 'Ansible', 'Monitoring', 'Python', 'Bash', 'Cloud Computing',
            'Infrastructure as Code', 'Security'
        ],
        'qa engineer': [
            'Test Automation', 'Selenium', 'Manual Testing', 'Test Planning',
            'Bug Tracking', 'API Testing', 'Performance Testing', 'Regression Testing',
            'Test Cases', 'Quality Assurance', 'Agile', 'JIRA', 'Python', 'JavaScript', 'Testing Frameworks'
        ],
        'ui/ux designer': [
            'Figma', 'Adobe XD', 'Sketch', 'Prototyping', 'User Research',
            'Wireframing', 'Visual Design', 'Interaction Design', 'Usability Testing',
            'Design Systems', 'HTML', 'CSS', 'User Experience', 'Information Architecture', 'Responsive Design'
        ],
        'business analyst': [
            'Requirements Analysis', 'Process Mapping', 'SQL', 'Excel', 'Documentation',
            'Stakeholder Management', 'Business Process', 'Data Analysis', 'Reporting',
            'Project Management', 'Agile', 'Communication', 'Problem Solving', 'Wireframing', 'Testing'
        ],
        'project manager': [
            'Project Management', 'Agile', 'Scrum', 'Risk Management', 'Stakeholder Management',
            'Budget Management', 'Timeline Planning', 'Resource Planning', 'Communication',
            'Leadership', 'Problem Solving', 'Microsoft Project', 'JIRA', 'Team Management', 'Reporting'
        ],
        'marketing manager': [
            'Digital Marketing', 'SEO', 'SEM', 'Social Media Marketing', 'Content Marketing',
            'Email Marketing', 'Analytics', 'Campaign Management', 'Brand Management',
            'Market Research', 'Google Analytics', 'A/B Testing', 'Lead Generation', 'CRM', 'Strategy'
        ]
    }
    
    # Find matching skills
    matched_skills = []
    for job_pattern, skills_list in skills_database.items():
        if (job_pattern == job_title_lower or 
            job_pattern in job_title_lower or 
            job_title_lower in job_pattern or
            any(word in job_title_lower for word in job_pattern.split()) or
            any(word in job_pattern for word in job_title_lower.split())):
            matched_skills = skills_list
            break
    
    # If no specific match, provide general tech skills
    if not matched_skills:
        matched_skills = [
            'Communication', 'Problem Solving', 'Teamwork', 'Time Management',
            'Analytical Thinking', 'Adaptability', 'Leadership', 'Technical Writing',
            'Project Management', 'Attention to Detail', 'Critical Thinking',
            'Customer Service', 'Microsoft Office', 'Research', 'Planning'
        ]
    
    # Return up to max_skills
    return matched_skills[:max_skills]

# For backward compatibility and alternative function name
get_skills_suggestion = suggest_skills
