#!/usr/bin/env python3
"""
Simple test to check a single question generation and see code structure.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
from app import create_app
from app.question.question_gen import generate_questions_from_skills
from app.question.question_gen2 import question_generator_for_ui

def test_single_generation():
    """Test single question generation to debug code syntax."""
    print("=== TESTING QUESTION GENERATION WITH CODE ===\n")
    
    app = create_app()
    
    with app.app_context():
        # Test Skills Generator
        print("1. Testing Skills Generator...")
        try:
            result = generate_questions_from_skills(
                skills="python,flask",
                level="intermediate",
                question_type="technical", 
                language="English",
                num_questions=2
            )
            
            print(f"✅ Skills Generator returned result type: {type(result)}")
            
            # Check structure
            if isinstance(result, list):
                questions = result
                print(f"Questions count: {len(questions)}")
                
                for i, q in enumerate(questions[:2], 1):  # Only check first 2
                    print(f"\n--- Question {i} ---")
                    print(f"Type: {type(q)}")
                    if isinstance(q, dict):
                        print(f"Keys: {list(q.keys())}")
                        print(f"Text: {q.get('text', 'N/A')[:100]}...")
                        print(f"Relevance exists: {'relevance' in q}")
                        print(f"Expected exists: {'expected' in q}")
                        print(f"Code snippet exists: {'code_snippet' in q}")
                        if 'code_snippet' in q and q['code_snippet']:
                            print(f"Code language: {q.get('code_lang', 'Not specified')}")
                            print(f"Code snippet: {q['code_snippet'][:100]}...")
                    else:
                        # If it's an object, check attributes
                        print(f"Attributes: {[attr for attr in dir(q) if not attr.startswith('_')]}")
                        print(f"Text: {getattr(q, 'text', 'N/A')[:100]}...")
                        print(f"Has relevance: {hasattr(q, 'relevance')}")
                        print(f"Has expected: {hasattr(q, 'expected')}")
                        print(f"Has code_snippet: {hasattr(q, 'code_snippet')}")
                        if hasattr(q, 'code_snippet') and q.code_snippet:
                            print(f"Code language: {getattr(q, 'code_lang', 'Not specified')}")
                            print(f"Code snippet: {q.code_snippet[:100]}...")
            elif isinstance(result, dict) and 'questions' in result:
                questions = result['questions']
                print(f"Questions count: {len(questions)}")
                
                for i, q in enumerate(questions[:2], 1):  # Only check first 2
                    print(f"\n--- Question {i} ---")
                    print(f"Type: {type(q)}")
                    if isinstance(q, dict):
                        print(f"Keys: {list(q.keys())}")
                        print(f"Text: {q.get('text', 'N/A')[:100]}...")
                        print(f"Relevance exists: {'relevance' in q}")
                        print(f"Expected exists: {'expected' in q}")
                        print(f"Code snippet exists: {'code_snippet' in q}")
                        if 'code_snippet' in q and q['code_snippet']:
                            print(f"Code language: {q.get('code_lang', 'Not specified')}")
                            print(f"Code snippet: {q['code_snippet'][:100]}...")
                    else:
                        # If it's an object, check attributes
                        print(f"Attributes: {[attr for attr in dir(q) if not attr.startswith('_')]}")
                        print(f"Text: {getattr(q, 'text', 'N/A')[:100]}...")
                        print(f"Has relevance: {hasattr(q, 'relevance')}")
                        print(f"Has expected: {hasattr(q, 'expected')}")
                        print(f"Has code_snippet: {hasattr(q, 'code_snippet')}")
            else:
                print(f"Unexpected result structure: {type(result)}")
                if hasattr(result, '__dict__'):
                    print(f"Result attributes: {result.__dict__}")
                    
        except Exception as e:
            print(f"❌ Skills Generator error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_single_generation()
