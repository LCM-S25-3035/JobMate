from app import create_app
app = create_app()
with app.app_context():
    from app.question.question_gen import generate_questions_from_skills
    from app.question.question_gen2 import question_generator_for_ui
    
    # Test skills generator
    print('=== TESTING SKILLS GENERATOR ===')
    try:
        skills_result = generate_questions_from_skills('Python, SQL', 'intermediate', 'technical', 'English', 3)
        print(f'Skills returned: {len(skills_result)} questions')
        if skills_result:
            print(f'First question type: {type(skills_result[0])}')
            print(f'First question keys: {skills_result[0].keys() if isinstance(skills_result[0], dict) else "Not dict"}')
            print(f'First question text preview: {skills_result[0].get("text", "No text")[:100]}...')
            print(f'Has relevance: {"relevance" in skills_result[0]}')
            print(f'Has expected: {"expected" in skills_result[0]}')
    except Exception as e:
        print(f'Skills generator error: {e}')
    
    print('\n=== TESTING DESCRIPTION GENERATOR ===')
    try:
        desc_result = question_generator_for_ui('Senior Python Developer position requiring 5+ years experience', 'Python Developer', 'senior', '5+ years', 'technical', 'English', 3)
        print(f'Description returned: {len(desc_result)} questions')
        if desc_result:
            print(f'First question type: {type(desc_result[0])}')
            print(f'First question keys: {desc_result[0].keys() if isinstance(desc_result[0], dict) else "Not dict"}')
            print(f'First question text preview: {desc_result[0].get("text", "No text")[:100]}...')
            print(f'Has relevance: {"relevance" in desc_result[0]}')
            print(f'Has expected: {"expected" in desc_result[0]}')
    except Exception as e:
        print(f'Description generator error: {e}')
