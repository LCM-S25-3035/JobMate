import os
import json
import tempfile
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session
import io
import google.generativeai as genai
from fpdf import FPDF
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import ImageFormatter
from PIL import Image
from dotenv import load_dotenv

from question_gen import question_generator_gemini
from question_gen2 import question_generator_for_ui

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("Error: The GEMINI_API_KEY environment variable is not configured.")
    exit("GEMINI_API_KEY is not configured.")

genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel(model_name="gemini-1.5-flash")

def code_to_image(code_text: str) -> str:
    
    formatter = ImageFormatter(
        font_name='Courier New',
        line_numbers=True,
        style='default',
        image_format='PNG'
    )
    img_data = io.BytesIO()
    highlight(code_text, PythonLexer(), formatter, outfile=img_data)
    img_data.seek(0)
    image = Image.open(img_data)
    tmp_image_path = tempfile.NamedTemporaryFile(delete=False, suffix='.png').name
    image.save(tmp_image_path)
    return tmp_image_path

def render_questions_to_pdf(blocks):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    try:
        font_path = os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf")
        pdf.add_font("DejaVu", "", font_path, uni=True)
        pdf.set_font("DejaVu", size=12)
    except Exception:
        pdf.set_font("Arial", size=12)

    pdf.multi_cell(0, 10, "Job Interview Questions", align='C')
    pdf.ln(5)

    code_block = []
    in_code = False

    for line in blocks:
        if line.strip().startswith("```"):
            in_code = not in_code
            if not in_code:
                code_image_path = code_to_image("\n".join(code_block))
                pdf.image(code_image_path, w=180)
                os.remove(code_image_path)
                code_block = []
            continue

        if in_code:
            code_block.append(line)
        else:
            if line.strip():
                pdf.multi_cell(0, 10, line.strip())
                pdf.ln(1)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        pdf.output(tmp_file.name)
        return tmp_file.name

# --- Flask Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/questions/skills', methods=['GET', 'POST'])
def skills_questions():
    questions_result = None
    if request.method == 'POST':
        rol = request.form.get('rol')
        level = request.form.get('level')
        type = request.form.get('type')
        n_questions = int(request.form.get('n_questions', 5)) # Default to 5 if not provided
        language = request.form.get('language')
        level_description = request.form.get('level_description')
        responsibilities = request.form.get('responsibilities')
        technical_skills = request.form.get('technical_skills')
        soft_skills = request.form.get('soft_skills')

        if not rol:
            flash("Please enter a role.", 'warning')
        else:
            try:
                # Call your backend function
                questions_result = question_generator_gemini(
                    rol=rol,
                    level=level,
                    level_description=level_description,
                    type=type,
                    responsibilities=responsibilities,
                    technical_skills=technical_skills,
                    soft_skills=soft_skills,
                    n=n_questions,
                    language=language
                )
                flash("Questions generated successfully!", 'success')
            except Exception as e:
                flash(f"Error generating questions: {e}", 'error')

    return render_template('skills_questions.html', questions_result=questions_result)

@app.route('/questions/job_description', methods=['GET', 'POST'])
def job_description_questions():
    questions_result = None
    if request.method == 'POST':
        rol = request.form.get('rol')
        level = request.form.get('level')
        question_type = request.form.get('question_type') # Changed from 'type' to avoid conflict with Python's built-in type
        language = request.form.get('language')
        n_questions = int(request.form.get('n_questions', 5))
        level_description = request.form.get('level_description')
        job_description = request.form.get('job_description')

        if not rol:
            flash("Please enter a role.", 'warning')
        elif not job_description:
            flash("Please provide a job description.", 'warning')
        else:
            try:
                questions_result = question_generator_for_ui(
                    job_description=job_description,
                    role=rol,
                    level=level,
                    previous_experience=level_description,
                    question_type=question_type,
                    language=language,
                    n=n_questions
                )
                flash("Questions generated successfully!", 'success')
            except Exception as e:
                flash(f"Error generating questions: {e}", 'error')

    return render_template('job_description_questions.html', questions_result=questions_result)

@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    questions_text = request.form.get('questions_text')
    if questions_text:
        blocks = questions_text.split('\n')
        pdf_file_path = render_questions_to_pdf(blocks)
        try:
            return send_file(pdf_file_path, as_attachment=True, download_name="interview_questions.pdf", mimetype='application/pdf')
        finally:
            os.remove(pdf_file_path)
    else:
        flash("No questions to download.", 'error')
        return redirect(url_for('index')) # Or redirect to the page that generated the questions

if __name__ == '__main__':
    app.run(debug=True)