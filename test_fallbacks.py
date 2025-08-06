#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

def test_fallback_functions():
    """Test the fallback functions directly"""
    
    print("=== Testing Salary Suggestions ===")
    
    # Test cases
    test_cases = [
        ("Software Developer", "Vancouver, BC", "mid"),
        ("Data Analyst", "Toronto, ON", "senior"), 
        ("Frontend Developer", "Montreal, QC", "junior"),
        ("Random Job Title", "Calgary, AB", "entry")
    ]
    
    try:
        from app.ai_agents.salary_suggestion import get_fallback_salary_estimate
        
        for title, location, experience in test_cases:
            print(f"\n--- Testing: {title} in {location} ({experience} level) ---")
            result = get_fallback_salary_estimate(title, location, experience)
            print(f"Salary Range: {result['salary_range']}")
            print(f"Explanation: {result['explanation']}")
    except Exception as e:
        print(f"Error testing salary suggestions: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== Testing Skills Suggestions ===")
    
    # Test skills
    skill_test_cases = [
        "Software Developer",
        "Data Analyst", 
        "Frontend Developer",
        "Random Job Title"
    ]
    
    try:
        from app.ai_agents.skills_suggestion import get_fallback_skills
        
        for title in skill_test_cases:
            print(f"\n--- Testing skills for: {title} ---")
            skills = get_fallback_skills(title, 10)
            print(f"Skills: {', '.join(skills)}")
    except Exception as e:
        print(f"Error testing skills suggestions: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fallback_functions()
