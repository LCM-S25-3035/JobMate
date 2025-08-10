import os
from dotenv import load_dotenv
import google.generativeai as genai
from app.utils import split_answer_and_code

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel(model_name="gemini-2.0-flash")

def generate_questions_from_skills(skills, level, question_type, language, num_questions):
    """
    Generate interview questions based on specific skills
    
    Args:
        skills (str): Comma-separated list of skills
        level (str): Experience level (junior, intermediate, senior)
        question_type (str): Type of questions (technical, behavioral)
        language (str): Language for questions and answers
        num_questions (int): Number of questions to generate
        
    Returns:
        list: List of dictionaries with question data
    """
    try:
        # Create a comprehensive prompt for skills-based questions
        prompt = f"""
Generate exactly {num_questions} high-quality interview questions focused on evaluating the following skills: {skills}

Requirements:
- Target experience level: {level.capitalize()}
- Question type: {question_type.capitalize()}
- Language: {language}
- For '{question_type.capitalize()}' questions, focus on assessing:
    - **Technical:** Core technical knowledge, problem-solving, and (if applicable and programming languages are mentioned in the skills) include at least one question requiring a code snippet example.
    - **Behavioral:** Soft skills, decision-making, conflict resolution, leadership, and collaboration.
- Ensure a diverse mix of questions covering:
    - Core technical skills and their practical application.
    - Problem-solving abilities related to the specified skills.
    - Real-world scenarios where these skills would be essential.
- All questions, ideal answers, and explanations must be in {language}.

FORMAT EACH QUESTION EXACTLY AS FOLLOWS:

1. INTERVIEW QUESTION:
[Your question here]

WHY THIS QUESTION:
[Brief explanation of what this question aims to assess and why it's relevant for evaluating the specified skills]

IDEAL ANSWER:
[A comprehensive exemplary answer that demonstrates strong competency in the relevant skills. Include specific details, examples, and technical concepts when appropriate.]

2. INTERVIEW QUESTION:
[Your question here]

WHY THIS QUESTION:
[Brief explanation of what this question aims to assess and why it's relevant for evaluating the specified skills]

IDEAL ANSWER:
[A comprehensive exemplary answer that demonstrates strong competency in the relevant skills. Include specific details, examples, and technical concepts when appropriate.]

[Continue for all {num_questions} questions...]

IMPORTANT: Start each question with the exact format "X. INTERVIEW QUESTION:" where X is the question number.
"""
        
        response = model.generate_content(prompt)
        
        # Parse AI response into structured data
        questions_data = _parse_skills_questions_to_dict(response.text)
        return questions_data
        
    except Exception as e:
        return [{"text": f"❌ Error generating questions from skills: {str(e)}", "relevance": "", "expected": "", "code_snippet": None, "code_lang": "python"}]


def question_generator_gemini(rol, level, level_description, type, responsibilities, technical_skills, soft_skills, language, n=5):
    """
    Original function for generating questions based on job description
    """
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
    f"* Any code snippet must be presented within a properly formatted Markdown code block "
    f"(e.g., ```Python).\n\n"
    f"**For each question, provide the following structured format:**\n\n"
    f"1. **Interview Question:** [The clear and concise question goes here]\n"
    f"2. **Suggested Ideal Answer:** [A detailed answer of 150-300 words that demonstrates relevant understanding and skills]\n"
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
        return f"❌ Error generating questions: {e}"


def _parse_skills_questions_to_dict(raw_text):
    """
    Parse AI response into a list of dictionaries for template rendering
    Similar to question_gen_db.py's parsing but adapted for skills format
    
    Args:
        raw_text (str): Raw text response from AI
        
    Returns:
        list: List of dictionaries with question data
    """
    if not raw_text:
        return []
    
    import re
    
    # Split by numbered questions
    text_to_process = "\n" + raw_text.strip()
    parts = re.split(r'\n\s*(\d+)\.\s*INTERVIEW QUESTION:', text_to_process)
    
    questions_data = []
    
    if len(parts) >= 3:
        # Process each question (skip first empty part)
        for i in range(1, len(parts), 2):
            if i + 1 < len(parts):
                question_num = parts[i]
                content = parts[i + 1].strip()
                
                # Parse the content to extract different sections
                question_dict = _extract_skills_question_sections(content)
                questions_data.append(question_dict)
    else:
        # Fallback: treat entire text as single question
        questions_data.append({
            "text": raw_text,
            "relevance": "",
            "expected": "",
            "code_snippet": None,
            "code_lang": "python"
        })
    
    return questions_data


def _extract_skills_question_sections(content):
    """
    Extract different sections from a skills-based question's content
    
    Args:
        content (str): The content of a single question
        
    Returns:
        dict: Dictionary with question components
    """
    import re
    
    # Initialize result
    result = {
        "text": "",
        "relevance": "",
        "expected": "",
        "code_snippet": None,
        "code_lang": "python"
    }
    
    # Split content by sections
    lines = content.split('\n')
    current_section = "text"
    current_content = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check for section headers
        if line.upper().startswith('WHY THIS QUESTION:'):
            if current_section == "text" and current_content:
                result["text"] = '\n'.join(current_content).strip()
            current_section = "relevance"
            current_content = []
            # Add the content after the colon if any
            after_colon = line.split(':', 1)[1].strip() if ':' in line else ""
            if after_colon:
                current_content.append(after_colon)
                
        elif line.upper().startswith('IDEAL ANSWER:'):
            if current_section == "relevance" and current_content:
                result["relevance"] = '\n'.join(current_content).strip()
            current_section = "expected"
            current_content = []
            # Add the content after the colon if any
            after_colon = line.split(':', 1)[1].strip() if ':' in line else ""
            if after_colon:
                current_content.append(after_colon)
                
        else:
            current_content.append(line)
    
    # Handle the last section
    if current_section == "text" and current_content:
        result["text"] = '\n'.join(current_content).strip()
    elif current_section == "relevance" and current_content:
        result["relevance"] = '\n'.join(current_content).strip()
    elif current_section == "expected" and current_content:
        result["expected"] = '\n'.join(current_content).strip()
    
    # Split answer and code for the expected answer
    if result["expected"]:
        answer_text, code_snippet, code_lang = split_answer_and_code(result["expected"])
        result["expected"] = answer_text
        result["code_snippet"] = code_snippet
        result["code_lang"] = code_lang or "python"
    
    return result
