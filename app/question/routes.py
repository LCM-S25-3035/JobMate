"""
Questions Blueprint - Interview Questions Generator
Integrated into JobMate Application  
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables and configure Gemini
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

try:
    from .question_gen import question_generator_gemini
except ImportError:
    # Fallback - define locally if import fails
    model = genai.GenerativeModel(model_name="gemini-2.0-flash")
    
    def question_generator_gemini(rol, level, level_description, type, responsibilities, technical_skills, soft_skills, language, n=5):
        prompt = (
        f"Generate {n} high-quality interview questions for the '{rol}' position, "
        f"designed for a candidate with a '{level}' experience level ({level_description}). "
        f"The questions and their answers should be generated in **{language}**.\n\n"
        f"The questions should be of type '{type}' and focus on evaluating the following critical areas:\n\n"
        f"**Key Responsibilities (3-5):**\n"
        f"{responsibilities}\n\n"
        f"**Essential Technical Skills (3-5):**\n"
        f"{technical_skills}\n\n"
        f"**Fundamental Soft Skills (3-5):**\n"
        f"{soft_skills}\n\n"
        f"Each question must be clear, specific, and relevant for a professional interview scenario, "
        f"allowing for a deep assessment of:\n"
        f"* The candidate's ability to take on the position's **responsibilities**.\n"
        f"* Mastery of the required **technical skills** and knowledge.\n"
        f"* Fit with the **company culture** and the **soft skills** necessary for success.\n\n"
        f"**Additional Considerations:**\n"
        f"* If the question type is **'technical'** and programming languages are listed in the technical skills "
        f"(e.g., Python, Java, SQL), include at least one question that requires the candidate to write code "
        f"using one of those languages.\n"
        f"* Any code snippet must be presented within a properly formatted Markdown code block "
        f"(e.g., ```Python).\n\n"
        f"**For each question, provide the following structured format:**\n\n"
        f"1. **Interview Question:** [The clear and concise question goes here]\n"
        f"2. **Suggested Ideal Answer:** [A detailed answer of 150-300 words that demonstrates relevant understanding and skills]\n"
        f"3. **Code Snippet (if applicable):**\n"
        f" ```[language]\n"
        f" [relevant code]\n"
        f" ```\n"
        f"4. **Evaluation and Justification:** [Brief explanation of what this question assesses and why the suggested answer is ideal in relation to the role or company culture.]"
        )

        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"❌ Error generating questions: {e}"

try:
    from .question_gen2 import question_generator_for_ui
except ImportError:
    # Fallback if import fails
    def question_generator_for_ui(*args, **kwargs):
        return "Question generator not available"

# Create blueprint
questions_bp = Blueprint('questions', __name__, 
                        url_prefix='/question')

def get_gemini_model():
    """Get configured Gemini model"""
    api_key = current_app.config.get('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY not configured")
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name=current_app.config.get('GEMINI_MODEL', 'gemini-1.5-flash'))

# Basic routes only - no PDF functionality
@questions_bp.route('/')
def index():
    return render_template('question/index.html')

@questions_bp.route('/skills')
def skills_questions():
    return render_template('question/skills_questions.html')

@questions_bp.route('/job-description')
def job_description_questions():
    return render_template('question/job_description_questions.html')

@questions_bp.route('/from-database')
def questions_from_db():
    return render_template('question/questions_from_db.html')
