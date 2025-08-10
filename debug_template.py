from app import create_app
from flask import render_template_string

app = create_app()
with app.app_context():
    from app.question.question_gen import generate_questions_from_skills
    from app.main.routes import build_questions_data
    
    # Generate test data
    skills_result = generate_questions_from_skills('Python, SQL', 'intermediate', 'technical', 'English', 1)
    questions_data = build_questions_data(skills_result) if skills_result else []
    
    # Create a simple test template to see the raw data
    test_template = """
<!DOCTYPE html>
<html>
<head><title>Debug Questions</title></head>
<body>
<h1>Raw Question Data Debug</h1>
{% for q in questions %}
<div style="border: 1px solid #ccc; margin: 20px; padding: 20px;">
    <h3>Question {{ loop.index }}</h3>
    <p><strong>Text:</strong> {{ q.text }}</p>
    <p><strong>Relevance:</strong> {{ q.relevance }}</p>
    <p><strong>Expected:</strong> {{ q.expected }}</p>
    <p><strong>Code snippet:</strong> {{ q.code_snippet or 'None' }}</p>
    
    <h4>Conditional Checks:</h4>
    <p>q.relevance truthy: {{ q.relevance|length > 0 if q.relevance else False }}</p>
    <p>q.expected truthy: {{ q.expected|length > 0 if q.expected else False }}</p>
</div>
{% endfor %}
</body>
</html>
"""
    
    # Render the test
    html = render_template_string(test_template, questions=questions_data)
    
    # Save to file
    with open('debug_output.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("Generated debug_output.html - open it in a browser to see the data")
    print(f"Questions data: {len(questions_data)} items")
    if questions_data:
        q = questions_data[0]
        print(f"First question relevance length: {len(q.get('relevance', ''))}")
        print(f"First question expected length: {len(q.get('expected', ''))}")
