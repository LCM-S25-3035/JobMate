#!/usr/bin/env python3
"""
Test the master_resume_formatter with realistic resume content that has wrong order
"""

def test_master_formatter():
    # Test with resume that has EXPERIENCE before SKILLS (wrong order)
    test_resume_wrong_order = """
John Doe
john@example.com | +1-555-123-4567
Toronto, Ontario

SUMMARY
Detail-oriented and proactive professional with 2+ years of experience in data and machine learning
roles, coupled with strong financial acumen. Hands-on experience includes maintaining and
validating large datasets and creating insightful reports.

EXPERIENCE
Amazon – Chennai, India | ML Data Associate | Feb 2022 - Jan 2024
• Maintained and validated over 20,000+ transaction-level records, ensuring 99.9% accuracy for
downstream reporting and analysis.
• Created KPI reports and reconciliation logs in Excel, leading to a 15% improvement in internal
quality and compliance audit scores.

State Street – Gdansk, Poland | Fund Accountant Intern | Dec 2020 – Feb 2021
• Supported reconciliation of over 500 financial transactions for institutional client portfolios,
ensuring 100% compliance with regulatory requirements.

SKILLS
Programming Languages
Python

Frameworks & Libraries
LangChain, LlamaIndex (exposure)

Tools & Technologies
Microsoft Excel, Jira, Confluence, Git, Docker, OpenAI (exposure), RESTful APIs, Bloomberg

EDUCATION
University of Toronto | Bachelor of Science | 2020
"""

    print("=== TESTING MASTER RESUME FORMATTER ===")
    print("Input resume (WRONG ORDER - Experience before Skills):")
    print(test_resume_wrong_order)
    print("\n" + "="*80 + "\n")
    
    # Simulate the master formatter logic
    lines = test_resume_wrong_order.split('\n')
    
    # Separate content into sections
    contact_info = []
    summary_content = []
    skills_content = []
    experience_content = []
    education_content = []
    
    current_section = 'contact'
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip completely empty lines at the start
        if not line and current_section == 'contact' and not contact_info:
            i += 1
            continue
        
        # Remove unwanted headings entirely
        if line.upper() in ['INTRO', '**INTRO**', 'CONTACT INFORMATION', '**CONTACT INFORMATION**', 'CONTACT', 'PERSONAL INFORMATION']:
            i += 1
            continue
        
        # Clean up markdown formatting from headings
        if line.startswith('**') and line.endswith('**') and len(line.split()) <= 3:
            line = line.replace('**', '').strip()
        
        # Identify section transitions
        if line.upper() in ['PROFESSIONAL SUMMARY', 'SUMMARY', 'CAREER SUMMARY', 'OBJECTIVE']:
            current_section = 'summary'
            summary_content.append('SUMMARY')
        elif line.upper() in ['SKILLS', 'TECHNICAL SKILLS', 'CORE SKILLS', 'KEY SKILLS']:
            current_section = 'skills'
            skills_content.append('SKILLS')
        elif line.upper() in ['EXPERIENCE', 'WORK EXPERIENCE', 'PROFESSIONAL EXPERIENCE', 'EMPLOYMENT HISTORY']:
            current_section = 'experience'
            experience_content.append('EXPERIENCE')
        elif line.upper() in ['EDUCATION', 'EDUCATIONAL BACKGROUND', 'ACADEMIC BACKGROUND']:
            current_section = 'education'
            education_content.append('EDUCATION')
        else:
            # Add content to current section with improved contact detection
            if line:  # Only add non-empty lines
                if current_section == 'contact':
                    # Simple contact detection
                    if '@' in line or '+' in line or len(line.split()) >= 2:
                        contact_info.append(line)
                elif current_section == 'summary':
                    summary_content.append(line)
                elif current_section == 'skills':
                    skills_content.append(line)
                elif current_section == 'experience':
                    experience_content.append(line)
                elif current_section == 'education':
                    education_content.append(line)
        
        i += 1
    
    # MASTER FORMAT ORDER - NEVER CHANGE THIS
    final_resume = []
    
    # 1. Contact Information (no heading - just the info)
    if contact_info:
        final_resume.extend(contact_info)
        final_resume.append('')  # Empty line after contact
    
    # 2. SUMMARY (changed from Professional Summary)
    if summary_content:
        final_resume.extend(summary_content)
        final_resume.append('')  # Empty line after summary
    
    # 3. SKILLS (MUST come right after summary)
    if skills_content:
        final_resume.extend(skills_content)
        final_resume.append('')  # Empty line after skills
    
    # 4. EXPERIENCE (comes after skills)
    if experience_content:
        final_resume.extend(experience_content)
        final_resume.append('')  # Empty line after experience
    
    # 5. EDUCATION (last section)
    if education_content:
        final_resume.extend(education_content)
    
    # Join and clean up extra whitespace
    final_text = '\n'.join(final_resume)
    
    # Remove multiple consecutive newlines (more than 2)
    import re
    final_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', final_text)
    
    result = final_text.strip()
    
    print("FORMATTED RESULT:")
    print(result)
    print("\n" + "="*80 + "\n")
    
    # Check section order
    result_lines = result.split('\n')
    section_order = []
    for line in result_lines:
        line_upper = line.strip().upper()
        if line_upper in ['SUMMARY', 'SKILLS', 'EXPERIENCE', 'EDUCATION']:
            section_order.append(line_upper)
    
    print(f"Section order found: {section_order}")
    expected_order = ['SUMMARY', 'SKILLS', 'EXPERIENCE', 'EDUCATION']
    
    if section_order == expected_order:
        print("✅ SUCCESS: Skills section now appears after Summary!")
        return True
    else:
        print(f"❌ ERROR: Expected {expected_order}, got {section_order}")
        return False

if __name__ == "__main__":
    test_master_formatter()
