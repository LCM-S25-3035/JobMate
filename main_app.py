import os
import json
import tempfile
import streamlit as st
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



st.set_page_config(page_title="Interview Question Generator", layout="centered")

st.title("🗣️ _Job_ _Interview_ _Question_ _Generator_ 📊", )

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error("Error: The GEMINI_API_KEY environment variable is not configured.")
    st.stop() # Stop execution if no API Key

genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel(model_name="gemini-1.5-flash") # The Gemini model instance

st.markdown("Explore AI-powered functionalities in one place!")

def code_to_image(code_text: str) -> str:
    """
    Renders a code snippet as an image with syntax highlighting using Courier New.
    """
    formatter = ImageFormatter(
        font_name='Courier New',  # compatible with Windows
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
        st.download_button(
            label="📄 Download questions in PDF",
            data=open(tmp_file.name, "rb").read(),
            file_name="interview_questions.pdf",
            mime="application/pdf"
        )
        return tmp_file.name
    
    os.remove(tmp_file.name)

# Sidebar for navigation 
st.sidebar.title("Main Menu 🧭")
st.sidebar.markdown("---") # Visual separator

# We use st.session_state to maintain the state of the current page
if 'page' not in st.session_state:
    st.session_state.page = 'welcome' # Default page

# Navigation buttons in the sidebar
if st.sidebar.button("🏠 Home", key="nav_home"):
    st.session_state.page = 'welcome'
if st.sidebar.button("📝 Question generator using skills", key="nav_questions"):
    st.session_state.page = 'question_generator_gemini'
if st.sidebar.button("📋 Question generator using the job description", key="nav_other_feature"):
    st.session_state.page = 'question_generator_for_ui'

st.sidebar.markdown("---")
st.sidebar.info("Select a menu option to navigate through the application.")


# Page routing logic

if st.session_state.page == 'welcome':
    st.title("👋 Welcome to your Interview Question Generator app!")
    st.markdown("""
        This app helps you prepare for job interviews by generating AI-powered questions.
        Use the menu on the left to explore the different tools available:

        * **📝 Question generator using skills:** Create custom questions for your selection processes, taking into account the required skills.
        * **📋 Question generator using the job description:** Create custom questions for your selection processes, based on the job descriptions posted.

        We hope you find it very useful!
    """)

elif st.session_state.page == 'question_generator_gemini':
    st.title("📝 Question generator using skills")
    st.write("Configure parameters to generate role-specific questions.")

    col1, col2 = st.columns(2)
    
    with col1:
        rol = st.text_input("Job position 🔍", placeholder="Example: Data Analyst")
        level = st.selectbox("Candidate level", ["Entry", "Junior", "Mid", "Senior"])
        type = st.selectbox("Type of questions", ["Technique", "Behavioral", "Logical", "Mixed"])   
        n_questions = st.slider("#️⃣ Number of questions", 1, 10, 5)

    with col2:
        level_description = st.text_input("More detailed description of the candidate's level", placeholder="Example: 'recent graduate with little experience', 'professional with 5 years of experience in the sector'.")
        responsibilities = st.text_input("The 3-5 main responsibilities of the position are: ", placeholder="Example: 'Cleaning data sets', 'Developing predictive models using statistical techniques.'") 
        technical_skills = st.text_input("The 3-5 key technical skills or knowledge required are: ", placeholder="Example: SQL, Python, etc.")
        soft_skills = st.text_input("The 3-5 soft skills or competencies important for success in the position are: ", placeholder="Example: Communication, Collaboration, Critical Thinking,..")

# Button to generate questions
    if st.button("Generate questions"):
        if not rol:
            st.warning("Please enter a role.")
        else:
            with st.spinner("Generating questions...⏳"):
                resultado = question_generator_gemini(
                    rol=rol,
                    level=level,
                    level_description=level_description,
                    type=type,
                    responsibilities=responsibilities,
                    technical_skills=technical_skills,
                    soft_skills=soft_skills,
                    n=n_questions
                )

            st.markdown("### ✅ Questions generated:")
        
            blocks = resultado.split('\n')
            in_code_block = False
            code_lines = []

            for line in blocks:
                
                if line.strip().startswith("```"):
                    in_code_block = not in_code_block
                    if not in_code_block:
                    
                        st.code("\n".join(code_lines), language="python")
                        code_lines = []
                    continue

                if in_code_block:
                    code_lines.append(line)
                else:
                    if line.strip():  # línea no vacía
                        st.markdown(line.strip())
            
            pdf_path = render_questions_to_pdf(blocks)

elif st.session_state.page == 'question_generator_for_ui':
    st.title("⚙️ Otra Funcionalidad de IA")
    st.write("Esta sección demuestra las capacidades de tu segundo backend de IA.")

    rol = st.text_input("Job position 🔍", placeholder="Example: Data Analyst")
    level = st.selectbox("Candidate level", ["Entry", "Junior", "Mid", "Senior"])
    type = st.selectbox("Type of questions", ["technical", "behavioral"])
    n_questions = st.slider("#️⃣ Number of questions", 1, 10, 5)
    level_description = st.text_input("More detailed description of the candidate's level", placeholder="Example: 'recent graduate with little experience', 'professional with 5 years of experience in the sector'.")
    job_description = st.text_area("Full job description or key responsibilities", placeholder="Include main responsibilities, technical and soft skills required...")

    # Botón para generar preguntas
    if st.button("Generate questions"):
        if not rol:
            st.warning("Please enter a role.")
        elif not job_description:
            st.warning("Please provide a job description.")
        else:
            with st.spinner("Generating questions...⏳"):
                resultado = question_generator_for_ui(
                    job_description=job_description,
                    role=rol,
                    level=level,
                    previous_experience=level_description,
                    question_type=type,
                    n=n_questions
                )

            st.markdown("### ✅ Questions generated:")

            blocks = resultado.split('\n')
            in_code_block = False
            code_lines = []

            for line in blocks:
                if line.strip().startswith("```"):
                    in_code_block = not in_code_block
                    if not in_code_block:
                        st.code("\n".join(code_lines), language="python")
                        code_lines = []
                    continue

                if in_code_block:
                    code_lines.append(line)
                else:
                    if line.strip():
                        st.markdown(line.strip())

            pdf_path = render_questions_to_pdf(blocks)
