import os
from dotenv import load_dotenv
import google.generativeai as genai
from app.utils import split_answer_and_code

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# ---------------- Enforcement Helpers (mirroring skills generator) ---------------- #
def _desc_generate_missing(job_description, role, level, previous_experience, question_type, language, start_number: int, missing: int):
    prompt = f"""
You already generated some interview questions but we still need EXACTLY {missing} more to reach the requested total.
Generate ONLY questions numbered from {start_number} to {start_number + missing - 1}.

Context Role: {role}
Level: {level}
Experience Detail: {previous_experience}
Question Type: {question_type}
Language: {language}

Job Description (for context):\n{job_description}\n

Requirements:
- Questions must be relevant to the job description and role requirements
- If the job description mentions programming languages, frameworks, or technical skills, consider including code examples when appropriate

Strict Format per question (no extra commentary):
{start_number}. INTERVIEW QUESTION:
[Question]

IDEAL ANSWER:
[Concise exemplary answer. Include specifics and, if appropriate for technical roles, brief inline code examples fenced in markdown.]

EXPLANATION:
[Brief relevance and what it evaluates]
"""
    try:
        response = model.generate_content(prompt)
        return _parse_description_questions_to_dict(response.text)
    except Exception:
        return []

def _desc_placeholder(idx:int, role:str, question_type:str, language:str):
    base_q = f"Placeholder question {idx}: Provide an example scenario relevant to the {role} role and discuss your approach."
    if question_type.lower() == 'technical':
        base_q = f"Placeholder technical question {idx}: Explain a design or optimization decision for a key {role} system component."
    relevance = f"Ensures requested total; evaluates {role} core competencies (auto-generated)."
    expected = f"Structured answer outlining context, approach, reasoning, and impact. (Placeholder in {language})."
    return {
        'text': base_q,
        'relevance': relevance,
        'expected': expected,
        'code_snippet': None,
        'code_lang': 'python'
    }

def question_generator_for_ui(job_description: str,
                              role: str,
                              level: str,
                              previous_experience: str,
                              question_type: str = "behavioral",
                              language: str = "English",
                              n: int = 5):
    """Generate EXACTLY n description-based questions with enforcement (returns list[dict])."""
    base_prompt = f"""
You are an expert interviewer.
Generate EXACTLY {n} interview questions for the '{role}' role.
Candidate level: {level} ({previous_experience})
Question Type: {question_type.capitalize()}
Language: {language}

Job Description Context:\n{job_description}\n

Requirements:
- Questions must be relevant to the job description and role requirements
- Provide diversity; avoid near duplicates
- If the job description mentions programming languages, frameworks, or technical skills, include at least ONE question that could naturally involve code examples
- All output must be in {language}

Strict per-question format:
1. INTERVIEW QUESTION:
[Question]

IDEAL ANSWER:
[Strong exemplary answer. Include specifics and, if appropriate for technical roles, brief inline code examples fenced in markdown.]

EXPLANATION:
[Why this question is relevant to the role and what it evaluates]

Repeat sequential numbering up to {n}. No extra commentary before or after.
"""
    try:
        response = model.generate_content(base_prompt)
        questions = _parse_description_questions_to_dict(response.text)

        # Supplemental attempts
        attempts = 0
        while len(questions) < n and attempts < 2:
            missing = n - len(questions)
            start_number = len(questions) + 1
            supplemental = _desc_generate_missing(job_description, role, level, previous_experience, question_type, language, start_number, missing)
            existing = {q['text'] for q in questions}
            filtered = [q for q in supplemental if q.get('text') and q['text'] not in existing]
            questions.extend(filtered)
            attempts += 1

        # Placeholders if still short
        if len(questions) < n:
            for idx in range(len(questions)+1, n+1):
                questions.append(_desc_placeholder(idx, role, question_type, language))

        if len(questions) > n:
            questions = questions[:n]

        return questions
    except Exception as e:
        return [{"text": f"❌ Error generating questions from description: {str(e)}", "relevance": "", "expected": "", "code_snippet": None, "code_lang": "python"}]


def _parse_description_questions_to_dict(raw_text):
    """
    Parse AI response into a list of dictionaries for template rendering
    Similar to question_gen.py's parsing but adapted for description format
    
    Args:
        raw_text (str): Raw text response from AI
        
    Returns:
        list: List of dictionaries with question data
    """
    if not raw_text:
        return []
    
    import re
    
    # Split by numbered questions (Question 1:, Question 2:, etc.)
    text_to_process = "\n" + raw_text.strip()
    # Accept either 'Question X:' or 'X. INTERVIEW QUESTION:' for flexibility
    parts = re.split(r'\n\s*(?:Question\s+(\d+):|(\d+)\.\s*INTERVIEW QUESTION:)', text_to_process, flags=re.IGNORECASE)
    
    questions_data = []
    
    if len(parts) >= 3:
        # Pattern produces alternating captures; some slots may be None
        for i in range(1, len(parts), 3):
            # Due to two capture groups, stride 3: [full, g1, g2, content, g1, g2, content, ...]
            # Simplify by scanning for next non-empty content after number groups
            if i + 2 < len(parts):
                num1 = parts[i]
                num2 = parts[i+1]
                content = parts[i+2].strip()
                question_num = num1 or num2 or '?'
                if content:
                    question_dict = _extract_description_question_sections(content)
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


def _extract_description_question_sections(content):
    """
    Extract different sections from a description-based question's content
    Format: Question, Ideal Answer, Explanation
    
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
        if line.upper().startswith('IDEAL ANSWER:'):
            if current_section == "text" and current_content:
                result["text"] = '\n'.join(current_content).strip()
            current_section = "expected"
            current_content = []
            # Add the content after the colon if any
            after_colon = line.split(':', 1)[1].strip() if ':' in line else ""
            if after_colon:
                current_content.append(after_colon)
                
        elif line.upper().startswith('EXPLANATION:'):
            if current_section == "expected" and current_content:
                result["expected"] = '\n'.join(current_content).strip()
            current_section = "relevance"
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
    elif current_section == "expected" and current_content:
        result["expected"] = '\n'.join(current_content).strip()
    elif current_section == "relevance" and current_content:
        result["relevance"] = '\n'.join(current_content).strip()
    
    # Split answer and code for the expected answer
    if result["expected"]:
        answer_text, code_snippet, code_lang = split_answer_and_code(result["expected"])
        result["expected"] = answer_text
        result["code_snippet"] = code_snippet
        result["code_lang"] = code_lang or "python"
    
    return result