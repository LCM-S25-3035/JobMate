from app import create_app
app = create_app()
with app.app_context():
    from app.question.question_gen_db import generate_database_questions
    from app.main.routes import build_questions_data
    
    # Test database generator (simulating a job)
    print('=== TESTING DATABASE GENERATOR ===')
    try:
        # Create a mock job data
        mock_job = {
            'title': 'Senior Python Developer',
            'company': 'Tech Corp',
            'description': 'We are looking for a senior Python developer with 5+ years of experience.',
            'requirements': 'Strong Python skills, SQL knowledge, REST APIs',
            'technical_skills': 'Python, SQL, REST APIs, Docker',
            'soft_skills': 'Communication, teamwork, problem-solving'
        }
        
        db_result = generate_database_questions(
            job_id='test', 
            job_data=mock_job, 
            n=3,
            question_type='technical'
        )
        print(f'Database returned: {type(db_result)} with length {len(db_result) if isinstance(db_result, list) else "not list"}')
        if isinstance(db_result, list) and db_result:
            print(f'First question type: {type(db_result[0])}')
            print(f'First question keys: {db_result[0].keys() if isinstance(db_result[0], dict) else "Not dict"}')
            print(f'First question text preview: {db_result[0].get("text", "No text")[:100]}...')
            print(f'Has relevance: {"relevance" in db_result[0]}')
            print(f'Has expected: {"expected" in db_result[0]}')
            
        # Test with build_questions_data function
        processed_result = build_questions_data(db_result) if db_result else []
        print(f'After build_questions_data: {len(processed_result)} questions')
        
    except Exception as e:
        import traceback
        print(f'Database generator error: {e}')
        traceback.print_exc()
