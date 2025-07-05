import os
import requests
from flask import current_app

def call_gemini_api(prompt, model=None):
    """
    Calls the Gemini API with the given prompt and returns the response.
    """
    api_key = current_app.config.get('GEMINI_API_KEY')
    model = model or current_app.config.get('GEMINI_MODEL', 'gemini-1.5-flash')
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.text, "status_code": response.status_code}

def merge_resume_sections(ai_resume, user_resume):
    """
    Given two resumes as plain text, merge each section so that all user content is always present,
    and any new/reworded AI lines are added (never omitting user content).
    Handles arbitrary user resumes: normalizes section headers, always includes all user lines (even if not under a recognized section),
    and ensures no user content is ever omitted, even if the AI omits or renames sections.
    Returns a dict of merged sections.
    """
    import re
    import logging
    def parse_sections(resume_text):
        # More robust: match headers case-insensitively, allow trailing colon/whitespace
        section_pattern = re.compile(r'^([A-Za-z][A-Za-z &]+)\s*:?[ \t]*$', re.MULTILINE)
        sections = {}
        last_header = None
        for line in resume_text.splitlines():
            line_stripped = line.strip()
            if not line_stripped:
                continue
            match = section_pattern.match(line_stripped)
            if match:
                last_header = match.group(1).strip().upper()
                if last_header not in sections:
                    sections[last_header] = []
            elif last_header:
                sections[last_header].append(line_stripped)
            else:
                # Lines before any section header go into 'UNASSIGNED'
                sections.setdefault('UNASSIGNED', []).append(line_stripped)
        return sections

    def normalize_header(header):
        mapping = {
            'PROFESSIONAL SUMMARY': 'SUMMARY',
            'SUMMARY': 'SUMMARY',
            'SKILLS': 'SKILLS',
            'RELEVANT PROJECTS': 'PROJECTS',
            'PROJECTS': 'PROJECTS',
            'PROJECT EXPERIENCE': 'PROJECTS',
            'EXPERIENCE': 'EXPERIENCE',
            'PROFESSIONAL EXPERIENCE': 'EXPERIENCE',
            'EDUCATION': 'EDUCATION',
            'COMMUNITY & INTERESTS': 'INTERESTS',
            'INTERESTS': 'INTERESTS',
            'UNASSIGNED': 'UNASSIGNED',
        }
        h = header.upper().strip(':')
        return mapping.get(h, h)

    ai_sections_raw = parse_sections(ai_resume)
    user_sections_raw = parse_sections(user_resume)
    # Normalize headers
    ai_sections = {}
    for h, lines in ai_sections_raw.items():
        nh = normalize_header(h)
        ai_sections.setdefault(nh, []).extend(lines)
    user_sections = {}
    for h, lines in user_sections_raw.items():
        nh = normalize_header(h)
        user_sections.setdefault(nh, []).extend(lines)
    merged = {}
    # Merge all sections found in either resume, preserving user order first
    all_headers = list(user_sections.keys()) + [h for h in ai_sections.keys() if h not in user_sections]
    for header in all_headers:
        user_lines = user_sections.get(header, [])
        ai_lines = ai_sections.get(header, [])
        user_set = set(l.strip() for l in user_lines if l.strip())
        merged_lines = list(user_lines)
        for l in ai_lines:
            l_strip = l.strip()
            if l_strip and l_strip not in user_set:
                merged_lines.append(l_strip)
        merged[header] = merged_lines
    # Ensure all user lines are present, even if not under a recognized section
    for h, lines in user_sections_raw.items():
        nh = normalize_header(h)
        for l in lines:
            if l.strip() and l.strip() not in merged.get(nh, []):
                merged.setdefault(nh, []).append(l.strip())
    # Fallback: If merged is empty or only contains empty sections, use user_resume as UNASSIGNED
    if (not merged or all(not v for v in merged.values())) and (user_resume.strip() or ai_resume.strip()):
        logging.warning("[merge_resume_sections] Fallback: AI and merged resume are empty, using user resume as UNASSIGNED.")
        merged = {'UNASSIGNED': user_resume.strip().splitlines() if user_resume.strip() else ai_resume.strip().splitlines()}
    return merged

def format_merged_resume(merged_sections):
    """
    Convert merged_sections dict to a formatted string for PDF or DOCX export.
    """
    section_order = [
        'SUMMARY', 'SKILLS', 'PROJECTS', 'EXPERIENCE', 'EDUCATION', 'INTERESTS', 'UNASSIGNED'
    ]
    output = []
    for section in section_order:
        lines = merged_sections.get(section)
        if lines:
            if section != 'UNASSIGNED':
                output.append(f"\n{section.title()}\n" + '-'*len(section))
            output.extend(lines)
    # Add any other sections not in the default order
    for section, lines in merged_sections.items():
        if section not in section_order and lines:
            output.append(f"\n{section.title()}\n" + '-'*len(section))
            output.extend(lines)
    return '\n'.join(output)

# Example Flask route for PDF download (add to your Flask app, e.g. in routes.py):
#
# from flask import send_file, make_response
# from io import BytesIO
# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas
# from app.ai_agents.gemini_utils import merge_resume_sections, format_merged_resume
#
# @app.route('/download_resume', methods=['POST'])
# def download_resume():
#     ai_resume = request.form.get('ai_resume', '')
#     user_resume = request.form.get('user_resume', '')
#     merged = merge_resume_sections(ai_resume, user_resume)
#     resume_text = format_merged_resume(merged)
#     if not resume_text.strip():
#         return 'ERROR: Resume content could not be generated. Please try again.', 400
#     buffer = BytesIO()
#     p = canvas.Canvas(buffer, pagesize=letter)
#     width, height = letter
#     y = height - 40
#     for line in resume_text.split('\n'):
#         if y < 40:
#             p.showPage()
#             y = height - 40
#         p.drawString(40, y, line)
#         y -= 15
#     p.save()
#     buffer.seek(0)
#     return send_file(buffer, as_attachment=True, download_name='custom_resume.pdf', mimetype='application/pdf')
