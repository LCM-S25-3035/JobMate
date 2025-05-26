import streamlit as st
from question_gen import question_generator_gemini

st.set_page_config(page_title="Interview Question Generator", layout="centered")

st.title("🗣️ Job Interview Question Generator 📊")

rol = st.text_input("Job position 🔍", placeholder="Example: Data Analyst")
level = st.selectbox("Candidate level", ["Entry", "Junior", "Mid", "Senior"])
type = st.selectbox("Type of questions", ["Technique", "Behavioral", "Logical", "Mixed"])
n_questions = st.slider("#️⃣ Number of questions", 1, 10, 5)
level_description = st.text_input("More detailed description of the candidate's level", placeholder="Example: 'recent graduate with little experience', 'professional with 5 years of experience in the sector'.")
responsibilities = st.text_input("The 3-5 main responsibilities of the position are: ", placeholder="Example: 'Cleaning data sets', 'Developing predictive models using statistical techniques.'") 
technical_skills = st.text_input("The 3-5 key technical skills or knowledge required are: ", placeholder="Example: SQL, Python, etc.")
soft_skills = st.text_input("The 3-5 soft skills or competencies important for success in the position are: ", placeholder="Example: Communication, Collaboration, Critical Thinking,..")

if st.button("Generate questions"):
    if not rol:
        st.warning("Please enter a role.")
    else:
        with st.spinner("Generating questions..."):
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
            # Detectar inicio o fin de bloque de código
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                if not in_code_block:
                    # Mostrar bloque de código acumulado
                    st.code("\n".join(code_lines), language="python")
                    code_lines = []
                continue

            if in_code_block:
                code_lines.append(line)
            else:
                if line.strip():  # línea no vacía
                    st.markdown(f"- {line.strip()}")
