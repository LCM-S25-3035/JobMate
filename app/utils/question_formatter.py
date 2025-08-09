"""
Question formatting utilities for converting raw AI-generated text to formatted HTML
"""

import re
import html

def format_questions_to_html(raw_text):
    """
    Convert raw AI-generated question text to properly formatted HTML
    
    Args:
        raw_text (str): Raw text from AI generation
        
    Returns:
        str: Formatted HTML
    """
    if not raw_text:
        return ""
        
    # Escape HTML for safety
    text = html.escape(raw_text)
    
    # Split into individual questions
    # Look for patterns like "Question 1:", "1.", "**1.", etc.
    question_pattern = r'(?:(?:Question\s*)?(?:\*\*)?(?:[\d]+)\.?\s*(?:\*\*)?:?\s*(?:Interview\s+Question:?)?)'
    
    # Split the text by question markers
    questions = re.split(question_pattern, text, flags=re.IGNORECASE)
    
    # Remove empty first element if exists
    if questions and not questions[0].strip():
        questions = questions[1:]
    
    if not questions:
        return f'<div class="alert alert-info"><p>{text}</p></div>'
    
    html_output = '<div class="questions-container">'
    
    for i, question_block in enumerate(questions, 1):
        if not question_block.strip():
            continue
            
        # Clean up the question block
        cleaned_block = question_block.strip()
        
        # Split into sections (Question, Ideal Answer, etc.)
        sections = parse_question_sections(cleaned_block)
        
        html_output += f'''
        <div class="question-item card mb-4">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0">
                    <i class="fas fa-question-circle me-2"></i>Question {i}
                </h5>
            </div>
            <div class="card-body">
        '''
        
        # Add each section
        for section_title, content in sections.items():
            if content.strip():
                html_output += format_section(section_title, content)
        
        html_output += '''
            </div>
        </div>
        '''
    
    html_output += '</div>'
    
    return html_output

def parse_question_sections(text):
    """
    Parse a question block into sections (Question, Ideal Answer, Code, etc.)
    """
    sections = {}
    
    # Define section patterns
    patterns = {
        'question': r'(?:interview\s+)?question:?\s*(.+?)(?=(?:ideal|suggested|answer|code|evaluation|explanation|question\s*\d|$))',
        'answer': r'(?:ideal|suggested)\s+answer:?\s*(.+?)(?=(?:code|evaluation|explanation|question\s*\d|$))',
        'code': r'code\s+snippet:?\s*(.+?)(?=(?:evaluation|explanation|question\s*\d|$))',
        'evaluation': r'(?:evaluation|explanation|justification):?\s*(.+?)(?=(?:question\s*\d|$))'
    }
    
    for section_name, pattern in patterns.items():
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            sections[section_name] = match.group(1).strip()
    
    # If no clear structure, treat entire text as question
    if not sections:
        sections['question'] = text
    
    return sections

def format_section(section_title, content):
    """
    Format individual sections with appropriate styling
    """
    content = content.strip()
    
    if section_title == 'question':
        return f'''
        <div class="question-content mb-3">
            <h6 class="text-primary fw-bold">
                <i class="fas fa-comment-dots me-2"></i>Interview Question
            </h6>
            <div class="question-text bg-light p-3 rounded border-start border-primary border-4">
                {format_text_content(content)}
            </div>
        </div>
        '''
    
    elif section_title == 'answer':
        return f'''
        <div class="answer-content mb-3">
            <h6 class="text-success fw-bold">
                <i class="fas fa-lightbulb me-2"></i>Suggested Ideal Answer
            </h6>
            <div class="answer-text bg-light p-3 rounded border-start border-success border-4">
                {format_text_content(content)}
            </div>
        </div>
        '''
    
    elif section_title == 'code':
        return f'''
        <div class="code-content mb-3">
            <h6 class="text-warning fw-bold">
                <i class="fas fa-code me-2"></i>Code Snippet
            </h6>
            <div class="code-block">
                {format_code_content(content)}
            </div>
        </div>
        '''
    
    elif section_title == 'evaluation':
        return f'''
        <div class="evaluation-content mb-3">
            <h6 class="text-info fw-bold">
                <i class="fas fa-chart-line me-2"></i>Evaluation & Justification
            </h6>
            <div class="evaluation-text bg-light p-3 rounded border-start border-info border-4">
                {format_text_content(content)}
            </div>
        </div>
        '''
    
    return f'<div class="section-content mb-3">{format_text_content(content)}</div>'

def format_text_content(text):
    """
    Format text content with basic markdown-like formatting
    """
    # Convert double asterisks to bold
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    
    # Convert single asterisks to italic
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    
    # Convert newlines to br tags
    text = text.replace('\n\n', '<br><br>')
    text = text.replace('\n', '<br>')
    
    # Handle bullet points
    text = re.sub(r'^[\s]*[-\*]\s+(.+)', r'<li>\1</li>', text, flags=re.MULTILINE)
    if '<li>' in text:
        text = f'<ul>{text}</ul>'
    
    return text

def format_code_content(text):
    """
    Format code content with syntax highlighting preparation
    """
    # Look for code blocks
    code_block_pattern = r'```(\w+)?\s*\n?(.*?)\n?```'
    
    def replace_code_block(match):
        language = match.group(1) or 'text'
        code = match.group(2).strip()
        return f'''
        <div class="code-container position-relative">
            <pre class="language-{language} line-numbers"><code class="language-{language}">{html.escape(code)}</code></pre>
            <button class="btn btn-sm btn-outline-secondary copy-btn position-absolute top-0 end-0 m-2" onclick="copyCode(this)">
                <i class="fas fa-copy"></i>
            </button>
        </div>
        '''
    
    formatted = re.sub(code_block_pattern, replace_code_block, text, flags=re.DOTALL)
    
    # If no code blocks found, treat as inline code
    if '```' not in text and formatted == text:
        formatted = f'<code class="bg-light p-2 rounded">{html.escape(text)}</code>'
    
    return formatted

# Additional utility function for question statistics
def get_question_stats(formatted_html):
    """
    Extract statistics from formatted questions
    """
    if not formatted_html:
        return {}
    
    # Count questions
    question_count = formatted_html.count('question-item card')
    
    # Count code snippets
    code_count = formatted_html.count('code-container') + formatted_html.count('language-')
    
    # Estimate reading time (assuming 200 words per minute)
    import re
    text_content = re.sub(r'<[^>]+>', '', formatted_html)
    word_count = len(text_content.split())
    reading_time = max(1, round(word_count / 200))
    
    return {
        'question_count': question_count,
        'code_snippets': code_count,
        'estimated_reading_time': reading_time,
        'word_count': word_count
    }
