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
        if question_type.lower() == 'behavioral':
            prompt = f"""
Generate exactly {num_questions} BEHAVIORAL interview questions that evaluate how a candidate has used or would use the following skills in real workplace situations: {skills}

IMPORTANT: These must be BEHAVIORAL questions only - focusing on past experiences, situations, and how the candidate handled them.

Requirements:
- Target experience level: {level.capitalize()}
- Question type: BEHAVIORAL (situation-based, not technical knowledge)
- Language: {language}
- Focus on soft skills, leadership, decision-making, conflict resolution, teamwork, and communication
- Each question should ask about specific situations or experiences where these skills were demonstrated
- Use STAR method approach (Situation, Task, Action, Result)
- NO technical coding questions or technical knowledge questions

Examples of good behavioral question starters:
- "Describe a time when you had to use [skill] to..."
- "Tell me about a situation where you demonstrated [skill]..."
- "Give me an example of when you used [skill] to overcome a challenge..."
- "How have you used [skill] in a team setting?"

FORMAT EACH QUESTION EXACTLY AS FOLLOWS:

1. INTERVIEW QUESTION:
[Your behavioral question here - must be situation/experience based]

WHY THIS QUESTION:
[Brief explanation of what this question aims to assess about the candidate's behavioral competencies]

SAMPLE KEY POINTS:
[Provide 3-5 bullet points of specific behaviors, actions, and measurable outcomes that demonstrate strong competency. Format as:
• Demonstrates [specific skill/behavior]
• Shows [specific action or approach]
• Achieves [measurable result or impact]
• Uses [specific method or strategy]
• Exhibits [key trait or capability]]

[Continue for all {num_questions} questions...]

IMPORTANT: ALL questions must be behavioral/situational, NOT technical knowledge questions.
"""
        elif question_type.lower() == 'technical':
            prompt = f"""
Generate exactly {num_questions} TECHNICAL interview questions focused on evaluating technical knowledge and skills: {skills}

Requirements:
- Target experience level: {level.capitalize()}
- Question type: TECHNICAL (knowledge-based, problem-solving)
- Language: {language}
- Focus on technical knowledge, problem-solving abilities, and practical application
- Include code snippets where appropriate for programming skills
- Test deep understanding of technical concepts

FORMAT EACH QUESTION EXACTLY AS FOLLOWS:

1. INTERVIEW QUESTION:
[Your technical question here]

WHY THIS QUESTION:
[Brief explanation of what this question aims to assess technically]

SAMPLE KEY POINTS:
[A comprehensive technical answer with examples, code if applicable, and detailed explanations.]

[Continue for all {num_questions} questions...]
"""
        else:  # mixed or other types
            prompt = f"""
Generate exactly {num_questions} MIXED interview questions (both behavioral and technical) focused on evaluating the following skills: {skills}

Requirements:
- Target experience level: {level.capitalize()}
- Question type: {question_type.capitalize()}
- Language: {language}
- Include both behavioral (situation-based) and technical (knowledge-based) questions
- For behavioral questions: focus on past experiences and situations
- For technical questions: focus on knowledge and problem-solving

FORMAT EACH QUESTION EXACTLY AS FOLLOWS:

1. INTERVIEW QUESTION:
[Your question here]

WHY THIS QUESTION:
[Brief explanation of what this question aims to assess]

SAMPLE KEY POINTS:
[A comprehensive answer appropriate to the question type]

[Continue for all {num_questions} questions...]
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
