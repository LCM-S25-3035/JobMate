import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel(model_name="gemini-1.5-flash")

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
    f"* Any code snippet must be presented within a properly formatted markdown code block "
    f"(e.g., ```python).\n\n"
    f"**For each question, provide the following structured format:**\n\n"
    f"1.  **Interview Question:** [Here goes the clear and concise question]\n"
    f"2.  **Suggested Ideal Answer:** [A model answer demonstrating relevant understanding and skills]\n"
    f"3.  **Code Snippet (if applicable):**\n"
    f"    ```[language]\n"
    f"    [relevant code]\n"
    f"    ```\n"
    f"4.  **Evaluation and Justification:** [Brief explanation of what this question evaluates and why the suggested "
    f"answer is ideal in relation to the role or company culture.]"
)


    try:
        # Genera el contenido usando Gemini
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Error generating questions:\n\n{e}"
