from app import create_app
app = create_app()
with app.app_context():
    from app.question.question_gen import generate_questions_from_skills
    from app.main.routes import build_questions_data
    from app.utils import split_answer_and_code
    
    # Test skills generator
    print('=== TESTING SKILLS GENERATOR BEFORE AND AFTER build_questions_data ===')
    skills_result = generate_questions_from_skills('Python, SQL', 'intermediate', 'technical', 'English', 2)
    
    print('BEFORE build_questions_data:')
    print(f'Length: {len(skills_result)}')
    if skills_result:
        q = skills_result[0]
        print(f'Keys: {list(q.keys())}')
        print(f'Text: {q.get("text", "MISSING")[:100]}...')
        print(f'Relevance: {q.get("relevance", "MISSING")[:100]}...')
        print(f'Expected: {q.get("expected", "MISSING")[:100]}...')
    
    print('\nAFTER build_questions_data:')
    processed = build_questions_data(skills_result)
    print(f'Length: {len(processed)}')
    if processed:
        q = processed[0]
        print(f'Keys: {list(q.keys())}')
        print(f'Text: {q.get("text", "MISSING")[:100]}...')
        print(f'Relevance: {q.get("relevance", "MISSING")[:100]}...')
        print(f'Expected: {q.get("expected", "MISSING")[:100]}...')
        
    # Test what happens when we have alternativa keys
    print('\n=== TEST WITH ALTERNATIVE KEYS ===')
    fake_data = [{'question': 'Test question', 'explanation': 'Test explanation', 'answer': 'Test answer'}]
    processed_fake = build_questions_data(fake_data)
    print(f'Fake data processed: {processed_fake[0] if processed_fake else "EMPTY"}')
