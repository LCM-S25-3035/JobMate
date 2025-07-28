import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel(model_name="gemini-1.5-flash")

def question_generator_for_ui(
    job_description: str,
    role: str,
    level: str,
    previous_experience: str,
    question_type: str = "behavioral",
    language: str = "English",
    n: int = 5
) -> str:
    """
    Generates structured interview questions based on a job description,
    role, candidate level, desired question type (technical or behavioral),
    and a specified language.

    Parameters:
        - job_description: Full job description text.
        - role: Job title.
        - level: Candidate seniority level (e.g., Junior, Mid, Senior).
        - previous_experience: Detailed level info (e.g., "5 years of experience").
        - question_type: 'technical' or 'behavioral'.
        - n: Number of questions to generate.
        - language: The desired language for the questions and answers (e.g., 'English', 'Spanish', 'French').

    Returns:
        - A string containing a list of questions in a structured text format.
    """

    prompt = f"""
You are an expert in talent selection and technical interviewing.
Generate exactly {n} interview questions for a '{role}' position, targeting a '{level}' candidate with '{previous_experience}' of experience.

---
Job Description:
{job_description}
---

Question Type: {question_type.capitalize()}
Language: {language}

Instructions:
- For '{question_type.capitalize()}' questions, focus on assessing:
    - **Technical:** Core technical knowledge, problem-solving, and (if applicable and programming languages are mentioned in the job description) include at least one question requiring a code snippet example.
    - **Behavioral:** Soft skills, decision-making, conflict resolution, leadership, and collaboration.
- Ensure a diverse mix of questions covering:
    - Core responsibilities of the role.
    - Essential technical skills (frameworks, tools, programming languages).
    - Crucial soft skills (communication, teamwork, adaptability).
- All questions, ideal answers, and explanations must be in {language}.

Format each question as a separate entry, clearly labeling the Question, an Ideal Answer (brief but comprehensive), and a concise Explanation of what the question aims to assess. Use a clear, readable text format, like this example:

Question 1: [Your question here]
Ideal Answer: [A concise, exemplary answer]
Explanation: [What this question evaluates]
"""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Error:\n{e}"
