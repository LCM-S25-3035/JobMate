from app import create_app
from flask import url_for
app = create_app()
with app.app_context():
    from app.question.question_gen import generate_questions_from_skills
    from app.main.routes import build_questions_data
    
    # Simulate what happens in the route
    print('=== SIMULATING SKILLS ROUTE ===')
    skills_result = generate_questions_from_skills('Python, SQL', 'intermediate', 'technical', 'English', 2)
    questions_data = build_questions_data(skills_result) if skills_result else []
    
    print(f'Original skills_result length: {len(skills_result)}')
    print(f'After build_questions_data length: {len(questions_data)}')
    
    if questions_data:
        q = questions_data[0]
        print(f'\nFirst question data:')
        print(f'Text: {q.get("text", "MISSING")}')
        print(f'Relevance: {q.get("relevance", "MISSING")}')
        print(f'Expected: {q.get("expected", "MISSING")}')
        print(f'Code snippet: {q.get("code_snippet", "MISSING")}')
        
        # Check for empty or None values
        print(f'\nValue checks:')
        print(f'Text empty/None: {not q.get("text")}')
        print(f'Relevance empty/None: {not q.get("relevance")}')
        print(f'Expected empty/None: {not q.get("expected")}')
        
    # Check the template context variables that would be passed
    actual_count = len(questions_data)
    placeholder_count = sum(1 for q in questions_data if q.get('text','').lower().startswith('placeholder'))
    
    print(f'\nTemplate context:')
    print(f'questions: {len(questions_data)} items')
    print(f'num_questions: {actual_count}')
    print(f'placeholder_count: {placeholder_count}')
    print(f'question_stats would be generated: {bool(questions_data)}')
