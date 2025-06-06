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
    n: int = 5
) -> str:
    """
    Generates structured interview questions based on a job description,
    role, candidate level, and desired question type (technical or behavioral).

    Parameters:
        - job_description: Full job description text.
        - role: Job title.
        - level: Candidate seniority level (e.g., Junior, Mid, Senior).
        - previous_experience: Detailed level info (e.g., "5 years of experience").
        - question_type: 'technical' or 'behavioral'.
        - n: Number of questions to generate.

    Returns:
        - A string containing a list of questions in plain text format.
    """
    prompt = f"""
You are an expert in talent selection and technical interviewing. Below is the job description:

---
{job_description}
---

Your task is to generate **{n} interview questions** for the **'{role}'** position, targeting candidates at **'{level}'** level ({previous_experience}).

Question type requested: **{question_type}**
- If 'technical': include questions that assess technical knowledge, and at least one that requires writing code if programming languages are mentioned If applicable, include a code snippet in a formatted code block (e.g., ```python).
- If 'behavioral': focus on soft skills, decision-making, conflict resolution, leadership, etc.

Diversity of questions:
Include a mix that assesses:
- Core responsibilities of the role.
- Technical skills (frameworks, tools, programming languages).
- Soft skills (collaboration, autonomy, communication, leadership).

Output format must be plain text, like the following: **Question**, **Ideal answer**, **Explanation**.
"""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Error:\n{e}"