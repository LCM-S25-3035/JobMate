#!/usr/bin/env python3
"""
Test Job Description Generator with technical job description to see if it includes code snippets.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
from app import create_app
from app.question.question_gen2 import question_generator_for_ui

def test_job_description_with_code():
    """Test Job Description Generator with technical job description."""
    print("=== TESTING JOB DESCRIPTION GENERATOR WITH TECHNICAL JOB ===\n")
    
    app = create_app()
    
    with app.app_context():
        # Technical job description that should trigger code snippets
        technical_job_desc = """
        Senior Python Flask Developer
        
        We are looking for an experienced Python developer to join our team. The ideal candidate will have:
        
        - 5+ years of experience with Python and Flask framework
        - Strong knowledge of RESTful API development
        - Experience with SQLAlchemy ORM and database design
        - Proficiency in JavaScript, HTML, and CSS
        - Knowledge of Docker and containerization
        - Experience with Git version control
        - Understanding of software testing practices (unit tests, integration tests)
        - Familiarity with cloud platforms (AWS, Azure, or GCP)
        
        Responsibilities:
        - Develop and maintain web applications using Flask
        - Design and implement RESTful APIs
        - Write clean, maintainable, and well-tested code
        - Collaborate with frontend developers and designers
        - Optimize application performance and scalability
        """
        
        print("Testing with technical job description...")
        try:
            result = question_generator_for_ui(
                job_description=technical_job_desc,
                role="Senior Python Flask Developer",
                level="senior",
                previous_experience="5+ years Python/Flask development",
                question_type="technical",
                language="English",
                n=3
            )
            
            print(f"✅ Generated {len(result)} questions")
            
            code_questions = 0
            for i, q in enumerate(result, 1):
                print(f"\n--- Question {i} ---")
                print(f"Text: {q.get('text', 'N/A')[:100]}...")
                
                if 'expected' in q and q['expected']:
                    # Check if the expected answer contains code (look for markdown code blocks)
                    expected = q['expected']
                    has_code_block = '```' in expected or 'python' in expected.lower() or 'flask' in expected.lower()
                    print(f"Expected answer has code indicators: {has_code_block}")
                    if has_code_block:
                        code_questions += 1
                        print(f"Expected (first 200 chars): {expected[:200]}...")
                
                if 'code_snippet' in q and q['code_snippet']:
                    print(f"Has explicit code_snippet: {q.get('code_lang', 'No language')}")
                    print(f"Code: {q['code_snippet'][:100]}...")
                    code_questions += 1
            
            print(f"\n✅ Total questions with code content: {code_questions}/{len(result)}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_job_description_with_code()
