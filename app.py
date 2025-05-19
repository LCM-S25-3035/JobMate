import streamlit as st
from question_gen import question_generator_gemini  # Asegúrate que el archivo y función se llamen así

st.set_page_config(page_title="Generador de Preguntas de Entrevista", layout="centered")

st.title("🗣️ Job Interview Question Generator 📊")

# Entradas del usuario
rol = st.text_input("Job position 🔍", placeholder="Example: Data Analyst")
level = st.selectbox("Candidate level", ["Entry", "Junior", "Mid", "Senior"])
type = st.selectbox("Type of questions", ["Technique", "Behavioral", "Logical", "Mixed"])
n_questions = st.slider("#️⃣ Number of questions", 1, 10, 5)
level_description = st.text_input("More detailed description of the candidate's level", placeholder="Example: 'recent graduate with little experience', 'professional with 5 years of experience in the sector'.")
responsibilities = st.text_input("The 3-5 main responsibilities of the position are: ", placeholder="Example: 'Cleaning data sets', 'Developing predictive models using statistical techniques.'") 
technical_skills = st.text_input("The 3-5 key technical skills or knowledge required are: ", placeholder="Example: SQL, Python, etc.")
soft_skills = st.text_input("The 3-5 soft skills or competencies important for success in the position are: ", placeholder="Example: Communication, Collaboration, Critical Thinking,..")

# Botón para generar preguntas
if st.button("Generar preguntas"):
    if not rol:
        st.warning("Por favor, ingresa un rol.")
    else:
        with st.spinner("Generando preguntas..."):
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

        st.markdown("### ✅ Preguntas generadas:")
        
        # Mostrar preguntas directamente sin columnas
        preguntas = resultado.strip().split('\n')
        for pregunta in preguntas:
            st.markdown(f"- {pregunta}")
