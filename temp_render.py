from app import create_app
from flask import render_template
app=create_app()
with app.app_context():
    for tpl in ['question/skills_questions.html','question/job_description_questions.html']:
        try:
            html=render_template(tpl, questions=[], form_data=None)
            print(f'RENDER OK {tpl} length={len(html)}')
        except Exception as e:
            import traceback; traceback.print_exc()
