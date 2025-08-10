from app import create_app
from flask import render_template
app=create_app()
with app.app_context():
  try:
    html=render_template('question/skills_questions.html', questions=[], form_data=None)
    print('SKILLS OK length', len(html))
  except Exception as e:
    import traceback; traceback.print_exc()
