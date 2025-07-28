import os
import json
import tempfile
from flask import Flask, render_template, request, redirect, url_for, flash, session
import io
import google.generativeai as genai
from fpdf import FPDF
from pygments import highlight
from pygments.lexers import PythonLexer, get_lexer_by_name
from pygments.formatters import ImageFormatter, HtmlFormatter
from pygments.util import ClassNotFound
from PIL import Image
from dotenv import load_dotenv
import re

from flask import send_file
from question_gen import question_generator_gemini
from question_gen2 import question_generator_for_ui
from question_gen_db import question_generator_from_db
from question_gen_db import get_job_details_from_db

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("Error: The GEMINI_API_KEY environment variable is not configured.")
    exit("GEMINI_API_KEY is not configured.")

genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel(model_name="gemini-1.5-flash")

def code_to_image(code_text: str, language: str = 'python') -> str:
    """
    Converts a code snippet to a PNG image for PDF export.
    """
    try:
        # Get appropriate lexer
        if language:
            try:
                lexer = get_lexer_by_name(language, stripall=True)
            except ClassNotFound:
                lexer = PythonLexer()
        else:
            lexer = PythonLexer()
        
        formatter = ImageFormatter(
            font_name='Courier New',
            line_numbers=True,
            style='vs',  # Visual Studio style
            image_format='PNG',
            font_size=12
        )
        
        img_data = io.BytesIO()
        highlight(code_text, lexer, formatter, outfile=img_data)
        img_data.seek(0)
        image = Image.open(img_data)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            image.save(tmp_file.name)
            return tmp_file.name
            
    except Exception as e:
        print(f"Error creating code image: {e}")
        # Fallback: create simple text image
        return create_text_fallback_image(code_text)

def create_text_fallback_image(text: str) -> str:
    """Fallback function to create a simple text image"""
    from PIL import Image, ImageDraw, ImageFont
    
    # Create image
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 12)
    except:
        font = ImageFont.load_default()
    
    # Draw text
    y_position = 10
    for line in text.split('\n')[:30]:  # Limit lines
        draw.text((10, y_position), line, fill='black', font=font)
        y_position += 20
    
    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
        img.save(tmp_file.name)
        return tmp_file.name

def format_questions_for_web_display(raw_text: str) -> str:
    """
    Formats questions for web display with syntax highlighting.
    This creates HTML that looks like VS Code.
    """
    if not raw_text:
        return ""
    
    # Pattern to match code blocks with optional language
    code_block_pattern = re.compile(r'```(\w+)?\n(.*?)```', re.DOTALL)

    def replace_code_block(match):
        lang = match.group(1) if match.group(1) else 'python'
        code_content = match.group(2).strip()

        try:
            lexer = get_lexer_by_name(lang, stripall=True)
        except ClassNotFound:
            lexer = PythonLexer()

        # VS Code-like formatter
        formatter = HtmlFormatter(
            linenos=True,
            cssclass="highlight",
            style='vs',  # Visual Studio style
            linenostart=1,
            lineanchors='line',
            anchorlinenos=True
        )
        
        highlighted_code = highlight(code_content, lexer, formatter)
        
        # Wrap in a container that looks like VS Code
        return f'''
        <div class="code-block-container">
            <div class="code-header">
                <span class="language-tag">{lang}</span>
            </div>
            <div class="code-content">
                {highlighted_code}
            </div>
        </div>
        '''

    # Replace all code blocks
    formatted_text = code_block_pattern.sub(replace_code_block, raw_text)
    
    # Convert line breaks to HTML
    formatted_text = formatted_text.replace('\n', '<br>')
    
    return formatted_text

def render_questions_to_pdf(raw_text: str):
    """
    Renders questions to PDF, converting code blocks to images.
    Uses the original markdown text, not HTML.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    try:
        # Try to use a Unicode-supporting font
        font_path = os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf")
        if os.path.exists(font_path):
            pdf.add_font("DejaVu", "", font_path, uni=True)
            pdf.set_font("DejaVu", size=12)
        else:
            pdf.set_font("Arial", size=12)
    except Exception:
        pdf.set_font("Arial", size=12)

    # Title
    pdf.set_font_size(16)
    pdf.cell(0, 10, "Job Interview Questions", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font_size(12)

    # Process the text line by line
    lines = raw_text.split('\n')
    i = 0
    temp_images = []  # Keep track of temp images for cleanup
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Check if this line starts a code block
        if line.startswith('```'):
            # Extract language if present
            lang_match = re.match(r'```(\w+)?', line)
            language = lang_match.group(1) if lang_match and lang_match.group(1) else 'python'
            
            # Collect code lines
            code_lines = []
            i += 1
            
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            
            # Create image from code
            if code_lines:
                code_text = '\n'.join(code_lines)
                try:
                    image_path = code_to_image(code_text, language)
                    temp_images.append(image_path)
                    
                    # Add some space before code block
                    pdf.ln(5)
                    
                    # Add the image to PDF
                    pdf.image(image_path, x=10, w=190)
                    
                    # Add some space after code block
                    pdf.ln(10)
                    
                except Exception as e:
                    print(f"Error adding image to PDF: {e}")
                    # Fallback: add as text
                    pdf.multi_cell(0, 5, f"[Code Block - {language}]")
                    for code_line in code_lines[:10]:  # Limit lines
                        pdf.multi_cell(0, 5, code_line)
                    pdf.ln(5)
        
        elif line:  # Regular text line
            try:
                pdf.multi_cell(0, 8, line)
                pdf.ln(2)
            except UnicodeEncodeError:
                # Handle unicode issues
                safe_line = line.encode('ascii', 'ignore').decode('ascii')
                pdf.multi_cell(0, 8, safe_line)
                pdf.ln(2)
        
        i += 1

    # Create temporary PDF file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        pdf.output(tmp_file.name)
        pdf_path = tmp_file.name
    
    # Clean up temporary images
    for img_path in temp_images:
        try:
            os.remove(img_path)
        except:
            pass
    
    return pdf_path

# === ROUTES ===

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
        
        try:
            n_questions = int(request.form.get('n_questions', 5))
        except (ValueError, TypeError):
            n_questions = 5
            
        language = request.form.get('language')
        level_description = request.form.get('level_description')
        responsibilities = request.form.get('responsibilities')
        technical_skills = request.form.get('technical_skills')
        soft_skills = request.form.get('soft_skills')

        if not rol:
            flash("Please enter a role.", 'warning')
        else:
            try:
                # Generate questions (this returns markdown text)
                questions_raw = question_generator_gemini(
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
                
                # Store raw text in session for PDF export
                session['questions_raw'] = questions_raw
                
                # Format for web display
                questions_result = format_questions_for_web_display(questions_raw)
                
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
        question_type = request.form.get('question_type')
        language = request.form.get('language')
        
        try:
            n_questions = int(request.form.get('n_questions', 5))
        except (ValueError, TypeError):
            n_questions = 5
            
        level_description = request.form.get('level_description')
        job_description = request.form.get('job_description')

        if not rol:
            flash("Please enter a role.", 'warning')
        elif not job_description:
            flash("Please provide a job description.", 'warning')
        else:
            try:
                questions_raw = question_generator_for_ui(
                    job_description=job_description,
                    role=rol,
                    level=level,
                    previous_experience=level_description,
                    question_type=question_type,
                    language=language,
                    n=n_questions
                )
                
                # Store raw text in session for PDF export
                session['questions_raw'] = questions_raw
                
                # Format for web display
                questions_result = format_questions_for_web_display(questions_raw)
                
                flash("Questions generated successfully!", 'success')
                
            except Exception as e:
                flash(f"Error generating questions: {e}", 'error')

    return render_template('job_description_questions.html', questions_result=questions_result)

@app.route('/questions/from_db', methods=['GET', 'POST'])
def questions_from_db():
    questions_result = None
    
    if request.method == 'POST':
        try:
            job_id = int(request.form.get('job_id'))
        except (ValueError, TypeError):
            job_id = None
            
        rol = request.form.get('rol')
        level = request.form.get('level')
        question_type = request.form.get('question_type')
        language = request.form.get('language')
        
        try:
            n_questions = int(request.form.get('n_questions', 5))
        except (ValueError, TypeError):
            n_questions = 5
            
        level_description = request.form.get('level_description')

        if not job_id:
            flash("Please enter a valid job ID.", 'warning')
        elif not rol:
            flash("Please enter a role.", 'warning')
        else:
            try:
                questions_raw = question_generator_from_db(
                    job_id=job_id,
                    level=level,
                    previous_experience=level_description,
                    question_type=question_type,
                    language=language,
                    n=n_questions
                )
                
                # Store raw text in session for PDF export
                session['questions_raw'] = questions_raw
                
                # Format for web display
                questions_result = format_questions_for_web_display(questions_raw)
                
                flash("Questions generated successfully from the database!", 'success')
                
            except Exception as e:
                flash(f"Error generating questions from the database: {e}", 'error')

    return render_template('questions_from_db.html', questions_result=questions_result)

@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    """Download questions as PDF using the original markdown text"""
    questions_raw = session.get('questions_raw')
    
    if questions_raw:
        try:
            pdf_file_path = render_questions_to_pdf(questions_raw)
            return send_file(
                pdf_file_path, 
                as_attachment=True, 
                download_name="interview_questions.pdf", 
                mimetype='application/pdf'
            )
        except Exception as e:
            flash(f"Error generating PDF: {e}", 'error')
            return redirect(url_for('index'))
        finally:
            # Clean up PDF file
            try:
                os.remove(pdf_file_path)
            except:
                pass
    else:
        flash("No questions to download.", 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)