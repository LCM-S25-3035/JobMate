import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel(model_name="gemini-1.5-flash")

def question_generator_gemini(rol, level, level_description, type, responsibilities, technical_skills, soft_skills, n=5):
    prompt = (
        f"Generate {n} interview questions for the position '{rol}'. "
        f"The candidate's level is '{level}' ({level_description} - for example: 'recent graduate with little experience', 'professional with 5 years of experience in the sector', 'team leader with management experience'). "
        f"The question type is '{type}'. "
        f"The 3-5 main responsibilities of the position are: '{responsibilities}'. "
        f"The 3-5 key technical skills or knowledge required are: '{technical_skills}'. "
        f"The 3-5 soft skills or competencies important for success in the position are: '{soft_skills}'. "
        f"Questions should be clear, specific, and realistic for job interviews, and should allow for an assessment of responsibilities, skills, and fit with the company culture. "
        f"If the question type is 'technical' and any programming languages are listed in the technical skills (e.g., Python, Java, SQL), include at least one question that asks the candidate to write code using one of those languages. "
        f"When including programming code in the answer, present it inside a properly formatted code block using markdown (for example, triple backticks and the language, such as ```python). "
        f"For each question, provide the following:\n"
        f"1. The interview question.\n"
        f"2. A suggested ideal answer.\n"
        f"3. If applicable, include a code snippet in a formatted code block (e.g., ```python).\n"
        f"4. A brief explanation of why this answer is ideal and what it evaluates regarding the candidate’s fit for the role or company culture."
    )
	
    try:
        # Genera el contenido usando Gemini
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating questions:\n\n{e}"
