def categorize_skills(skills_text):
    """Simple categorization for test"""
    return {
        "Programming Languages": ["Python", "SQL", "R", "Java"],
        "Frameworks & Libraries": ["Pandas", "NumPy", "Scikit-learn", "Matplotlib"],
        "Tools & Technologies": ["Git", "Docker", "RESTful APIs"],
        "Cloud & Infrastructure": ["AWS", "Azure", "GCP"],
        "Databases & Storage": ["MySQL", "PostgreSQL", "MongoDB"],
        "Domain Knowledge": ["Machine Learning", "Data Analysis"],
        "Soft Skills": ["Problem-Solving", "Communication"]
    }

def format_skills_normal():
    skills = categorize_skills("")
    output = ["SKILLS"]
    
    for category, skill_list in skills.items():
        if skill_list:
            output.append(f"{category}: {', '.join(skill_list)}")
    
    return "\n".join(output)

def format_skills_compact():
    skills = categorize_skills("")
    output = ["SKILLS"]
    
    for category, skill_list in skills.items():
        if skill_list:
            output.append(f"{category}")
            output.append(f"{', '.join(skill_list)}")
    
    return "\n".join(output)

print("===== NORMAL FORMAT (BEFORE) =====")
print(format_skills_normal())
print("\n===== COMPACT FORMAT (AFTER) =====")
print(format_skills_compact())
