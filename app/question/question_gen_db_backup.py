"""
Interview Questions Generator for JobMate
Generates interview questions based on job data from MongoDB
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv
from flask import current_app
from bson import ObjectId

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv('GEMINI_API_KEY')
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
else:
    model = None
    print("Warning: GEMINI_API_KEY not found in environment variables")


def get_job_details_from_mongodb(job_id, job_data=None):
    """
    Fetch job details from MongoDB database.
    
    Args:
        job_id (str): The job ID to search for
        job_data (dict, optional): Pre-fetched job data
        
    Returns:
        dict: Job details including role, company, description, etc.
    """
    if job_data:
        return job_data
        
    try:
        mongo_db = current_app.mongo_db
        if not mongo_db:
            print("MongoDB connection not available")
            return None
            
        jobs_collection = mongo_db.jobs
        job = jobs_collection.find_one({"_id": ObjectId(job_id)})
        
        if job is not None:
            job_details = {
                'role': job.get('title', ''),
                'job_description': job.get('description', ''),
                'company': job.get('company', ''),
                'location': job.get('location', ''),
                'requirements': job.get('requirements', ''),
                'technical_skills': job.get('technical_skills', ''),
                'soft_skills': job.get('soft_skills', '')
            }
            return job_details
        else:
            print(f"No job details found for ID: {job_id}")
            return None
            
    except Exception as e:
        print(f"Error fetching job details: {str(e)}")
        return None


def generate_database_questions(job_id, job_data=None, level="intermediate", 
                               previous_experience="3-5 years", question_type="mixed", 
                               language="English", n=5):
    """
    Generate interview questions based on job data from MongoDB.
    
    Args:
        job_id (str): MongoDB job ID
        job_data (dict, optional): Pre-fetched job data
        level (str): Experience level (junior, intermediate, senior)
        previous_experience (str): Years of experience description
        question_type (str): Type of questions (technical, behavioral, mixed)
        language (str): Language for questions and answers
        n (int): Number of questions to generate
        
    Returns:
        str: Generated questions in raw text format
    """
    # Extract job details
    job_details = get_job_details_from_mongodb(job_id, job_data)
    if not job_details:
        return "❌ Error: Job details could not be retrieved from the database."

    # Extract relevant fields
    role = job_details.get('role', '')
    company = job_details.get('company', '')
    job_description = job_details.get('job_description', '') or job_details.get('description', '')
    requirements = job_details.get('requirements', '')
    technical_skills = job_details.get('technical_skills', '')
    soft_skills = job_details.get('soft_skills', '')

    # Combine description and requirements
    full_description = f"{job_description}\n\n{requirements}".strip()

    # Build AI prompt for question generation
    prompt = _build_question_prompt(
        n=n, role=role, company=company, level=level, 
        previous_experience=previous_experience, language=language,
        question_type=question_type, full_description=full_description,
        technical_skills=technical_skills, soft_skills=soft_skills
    )

    # Generate questions using Gemini AI
    try:
        response = model.generate_content(prompt)
        if not response.text:
            return "❌ Error: Empty response from AI model."
        
        # DEBUG: Log the raw response to check if we got the right number
        import re
        question_count = len(re.findall(r'\d+\.\s*INTERVIEW QUESTION:', response.text))
        print(f"🔍 DEBUG: Solicitadas {n} preguntas, encontradas {question_count} en respuesta de IA")
        
        # Convert raw text to elegant HTML cards using simple formatter
        formatted_questions = _format_questions_preserve_all(response.text)
        return formatted_questions
        
    except Exception as e:
        return f"❌ Error generating questions: {str(e)}"


def _format_questions_preserve_all(raw_text):
    """
    Format questions preserving ALL content in elegant cards
    """
    if not raw_text:
        return ""
    
    import re
    
    # Split ONLY by main question numbers that are followed by "INTERVIEW QUESTION:"
    # This prevents splitting on internal numbered sections like "2. SUGGESTED IDEAL ANSWER:"
    text_to_process = "\n" + raw_text.strip()
    parts = re.split(r'\n\s*(\d+)\.\s*INTERVIEW QUESTION:', text_to_process)
    
    if len(parts) >= 3:
        # Found numbered questions - format each one
        html_output = '<div class="questions-container">'
        
        # Skip the first part (text before first question, now just \n)
        for i in range(1, len(parts), 2):
            if i + 1 < len(parts):
                question_num = parts[i]
                content = parts[i + 1].strip()
                
                # Clean up any residual numbering artifacts in the content
                # Remove standalone numbers followed by periods at the start of lines
                content = re.sub(r'\n\s*\d+\.\s*(?!INTERVIEW QUESTION:)', '\n', content)
                
                html_output += f'''
                <div class="question-item card mb-4">
                    <div class="card-header bg-primary text-white">
                        <h5 class="mb-0">
                            <i class="fas fa-question-circle me-2"></i>Question
                        </h5>
                    </div>
                    <div class="card-body">
                        <div class="question-text bg-light p-3 rounded border-start border-primary border-4">
                            <div style="white-space: pre-wrap; font-family: inherit; line-height: 1.6;">INTERVIEW QUESTION: {content}</div>
                        </div>
                    </div>
                </div>
                '''
        
        html_output += '</div>'
        return html_output
    else:
        # No numbered format found - show everything as single card
        return f'''
        <div class="question-item card mb-4">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0"><i class="fas fa-question-circle me-2"></i>Generated Questions</h5>
            </div>
            <div class="card-body">
                <div class="question-text bg-light p-3 rounded">
                    <div style="white-space: pre-wrap; font-family: inherit; line-height: 1.6;">{raw_text}</div>
                </div>
            </div>
        </div>
        '''


def _simple_format_questions(raw_text):
    """
    Simple formatter that preserves ALL content and creates elegant cards
    """
    if not raw_text:
        return ""
    
    # Split by numbered questions (1., 2., etc.) but preserve everything
    import re
    parts = re.split(r'\n\s*(\d+)\.\s*INTERVIEW QUESTION:', raw_text)
    
    if len(parts) < 3:  # No numbered format found, show everything as single card
        return f'''
        <div class="question-item card mb-4">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0"><i class="fas fa-question-circle me-2"></i>Generated Questions</h5>
            </div>
            <div class="card-body">
                <div class="question-text bg-light p-3 rounded">
                    <div style="white-space: pre-wrap; font-family: inherit;">{raw_text}</div>
                </div>
            </div>
        </div>
        '''
    
    html_output = '<div class="questions-container">'
    
    # Process each question (skip first empty part)
    for i in range(1, len(parts), 2):
        if i + 1 < len(parts):
            question_num = parts[i]
            question_content = parts[i + 1].strip()
            
            # Add the Interview Question header back since we split on it
            full_content = f"INTERVIEW QUESTION: {question_content}"
            
            html_output += f'''
            <div class="question-item card mb-4">
                <div class="card-header bg-primary text-white">
                    <h5 class="mb-0">
                        <i class="fas fa-question-circle me-2"></i>Question
                    </h5>
                </div>
                <div class="card-body">
                    <div class="question-text bg-light p-3 rounded border-start border-primary border-4">
                        <div style="white-space: pre-wrap; font-family: inherit; margin: 0;">{full_content}</div>
                    </div>
                </div>
            </div>
            '''
    
    html_output += '</div>'
    return html_output


def _build_question_prompt(n, role, company, level, previous_experience, 
                          language, question_type, full_description, 
                          technical_skills, soft_skills):
    """
    Build the AI prompt for question generation.
    
    Returns:
        str: Formatted prompt for Gemini AI
    """
    return (
        f"You must generate EXACTLY {n} interview questions - no more, no less.\n\n"
        f"Generate {n} high-quality interview questions for the '{role}' position at {company}, "
        f"designed for a candidate with a '{level}' experience level ({previous_experience}). "
        f"Questions and their answers must be generated in **{language}**.\n\n"
        f"IMPORTANT: You must provide exactly {n} questions numbered from 1 to {n}.\n\n"
        f"Questions must be of type '{question_type}' and based on the following job information:\n\n"
        f"**Job Description:**\n"
        f"{full_description}\n\n"
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
        f"1. INTERVIEW QUESTION: [The clear and concise question goes here]\n"
        f"2. SUGGESTED IDEAL ANSWER: [A detailed answer of 150-300 words that demonstrates relevant understanding and skills]\n"
        f"3. CODE SNIPPET (IF APPLICABLE):\n"
        f" ```[language]\n"
        f" [relevant code]\n"
        f" ```\n"
        f"4. EVALUATION AND JUSTIFICATION: [Brief explanation of what this question assesses and why the suggested answer is ideal in relation to the role or company culture.]"
    )
