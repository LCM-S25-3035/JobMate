import os
import google.generativeai as genai
import psycopg2
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

def get_job_details_from_db(job_id: int):
    """
    Retrieves job details (role, description, technical skills, soft skills) from the PostgreSQL database.
    """
    conn = None
    job_details = None
    try:
        # Connecting to the PostgreSQL database
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT", 5432)
        )
        cur = conn.cursor()

        # SQL query to get the role, job description, technical and soft skills by ID
        # Make sure your table is named 'job_descriptions' and has the columns:
        # 'role', 'description', 'technical_skills', and 'soft_skills'.
        cur.execute(
            "SELECT role, description, technical_skills, soft_skills FROM job_descriptions WHERE id = %s",
            (job_id,)
        )
        result = cur.fetchone()

        if result:
            job_details = {
                'role': result[0],
                'job_description': result[1],
                'technical_skills': result[2],
                'soft_skills': result[3]
            }
        else:
            print(f"No job details found for ID: {job_id}")

        cur.close()

    except Exception as e:
        print(f"Error connecting to or querying the database: {e}")
    finally:
        if conn:
            conn.close()
    return job_details

def question_generator_from_db(job_id: int, level: str, previous_experience: str,
                               question_type: str, language: str, n: int = 5):
    job_details = get_job_details_from_db(job_id)

    if not job_details:
        return "❌ Error: Job details could not be retrieved from the database."

    role = job_details.get('role', '')
    job_description = job_details.get('job_description', '')
    technical_skills = job_details.get('technical_skills', '')
    soft_skills = job_details.get('soft_skills', '')

    prompt = (
        f"Generate {n} high-quality interview questions for the '{role}' position, "
        f"designed for a candidate with a '{level}' experience level ({previous_experience}). "
        f"Questions and their answers must be generated in **{language}**.\n\n"
        f"Questions must be of type '{question_type}' and based on the following job information:\n\n"
        f"**Job Description:**\n"
        f"{job_description}\n\n"
        f"**Required Technical Skills:**\n"
        f"{technical_skills}\n\n"
        f"**Essential Soft Skills:**\n"
        f"{soft_skills}\n\n"
        f"Each question should be clear, specific, and relevant to a professional interview scenario, "
        f"allowing for an in-depth assessment of:\n"
        f"* The candidate's ability to assume the **responsibilities** of the position.\n"
        f"* Mastery of the required **technical skills** and knowledge.\n"
        f"* The fit with the **company culture** and the **soft skills** necessary for success.\n\n"
        f"**Additional Considerations:**\n"
        f"* If the question type is **'technical'** and programming languages are listed in the technical skills "
        f"(e.g., Python, Java, SQL), include at least one question that requires the candidate to write code "
        f"using one of those languages.\n"
        f"* Any code snippet must be presented within a properly formatted Markdown code block "
        f"(e.g., ```Python).\n\n"
        f"**For each question, provide the following structured format:**\n\n"
        f"1. **Interview Question:** [The clear and concise question goes here]\n"
        f"2. **Suggested Ideal Answer:** [A sample answer that demonstrates relevant understanding and skills]\n"
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
        return f"❌ Error generating questions:\n\n{e}"