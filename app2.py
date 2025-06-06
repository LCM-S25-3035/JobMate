import os
import json
import streamlit as st
from question_gen2 import question_generator_for_ui
from fpdf import FPDF
import tempfile
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import ImageFormatter
from PIL import Image
import io

st.set_page_config(page_title="Interview Question Generator", layout="centered")

st.title("🗣️ Job Interview Question Generator 📊")

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

# Entradas del usuario
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
