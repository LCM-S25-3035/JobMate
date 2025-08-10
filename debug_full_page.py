from app import create_app
from flask import render_template

app = create_app()
with app.app_context():
    from app.question.question_gen import generate_questions_from_skills
    from app.main.routes import build_questions_data
    
    # Generate test data exactly like the route does
    skills_result = generate_questions_from_skills('Python, SQL', 'intermediate', 'technical', 'English', 2)
    questions_data = build_questions_data(skills_result) if skills_result else []
    
    # Calculate all the same variables as the route
    actual_count = len(questions_data)
    placeholder_count = sum(1 for q in questions_data if q.get('text','').lower().startswith('placeholder'))
    qt_display = 'technical'
    
    # Create question statistics exactly like the route
    question_stats = None
    if questions_data and isinstance(questions_data, list):
        code_snippets = sum(1 for q in questions_data if q.get('code_snippet'))
        total_words = sum(len(str(q.get('text', '') + q.get('expected', '') + q.get('relevance', '')).split()) for q in questions_data)
        question_stats = {
            'question_count': len(questions_data),
            'code_snippets': code_snippets,
            'word_count': total_words,
            'estimated_reading_time': max(1, total_words // 200)
        }
    
    form_data = {
        'skills': 'Python, SQL',
        'level': 'intermediate', 
        'question_type': 'technical',
        'language': 'English',
        'count': '2'
    }
    
    try:
        # Try to render the skills template exactly as the route does
        html = render_template('question/skills_questions.html', 
                               questions=questions_data, 
                               form_data=form_data,
                               num_questions=actual_count,
                               requested_num_questions=2,
                               returned_num_questions=actual_count,
                               placeholder_count=placeholder_count,
                               question_type=qt_display,
                               question_stats=question_stats)
        
        with open('debug_skills_page.html', 'w', encoding='utf-8') as f:
            f.write(html)
        
        print("Generated debug_skills_page.html")
        print(f"Passed {len(questions_data)} questions to template")
        print(f"Question stats: {question_stats}")
        
    except Exception as e:
        print(f"Error rendering template: {e}")
        import traceback
        traceback.print_exc()
