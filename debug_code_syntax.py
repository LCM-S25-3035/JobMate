#!/usr/bin/env python3
"""
Debug script to check code syntax highlighting issues.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
from app import create_app
from app.question.skills_generator import SkillsQuestionGenerator
from app.question.job_description_generator import JobDescriptionQuestionGenerator

def debug_code_syntax():
    """Debug code syntax highlighting in question generators."""
    print("=== DEBUGGING CODE SYNTAX HIGHLIGHTING ===\n")
    
    app = create_app()
    
    with app.app_context():
        # Test Skills Generator
        print("1. Testing Skills Generator...")
        skills_gen = SkillsQuestionGenerator()
        
        try:
            skills_questions = skills_gen.generate_questions(
                skills="python,flask",
                num_questions=2,
                question_types=["technical"]
            )
            
            print(f"✅ Skills Generator returned {len(skills_questions)} questions")
            
            # Check if any have code snippets
            for i, q in enumerate(skills_questions, 1):
                print(f"\n--- Question {i} ---")
                print(f"Text: {q.text[:100]}...")
                print(f"Has relevance: {hasattr(q, 'relevance') and q.relevance is not None}")
                print(f"Has expected: {hasattr(q, 'expected') and q.expected is not None}")
                print(f"Has code_snippet: {hasattr(q, 'code_snippet') and q.code_snippet is not None}")
                if hasattr(q, 'code_snippet') and q.code_snippet:
                    print(f"Code language: {getattr(q, 'code_lang', 'Not specified')}")
                    print(f"Code snippet (first 100 chars): {q.code_snippet[:100]}...")
                    
        except Exception as e:
            print(f"❌ Skills Generator error: {e}")
        
        # Test Job Description Generator
        print("\n\n2. Testing Job Description Generator...")
        desc_gen = JobDescriptionQuestionGenerator()
        
        try:
            desc_questions = desc_gen.generate_questions(
                job_description="Senior Python Flask Developer position requiring expertise in web development",
                num_questions=2,
                question_types=["technical"]
            )
            
            print(f"✅ Description Generator returned {len(desc_questions)} questions")
            
            # Check if any have code snippets
            for i, q in enumerate(desc_questions, 1):
                print(f"\n--- Question {i} ---")
                print(f"Text: {q.text[:100]}...")
                print(f"Has relevance: {hasattr(q, 'relevance') and q.relevance is not None}")
                print(f"Has expected: {hasattr(q, 'expected') and q.expected is not None}")
                print(f"Has code_snippet: {hasattr(q, 'code_snippet') and q.code_snippet is not None}")
                if hasattr(q, 'code_snippet') and q.code_snippet:
                    print(f"Code language: {getattr(q, 'code_lang', 'Not specified')}")
                    print(f"Code snippet (first 100 chars): {q.code_snippet[:100]}...")
                    
        except Exception as e:
            print(f"❌ Description Generator error: {e}")

if __name__ == "__main__":
    debug_code_syntax()
