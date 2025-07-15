"""
Main Routes for JobMate
Landing page, dashboards, and core application routes
"""

from flask import render_template, redirect, url_for, request, jsonify, current_app, send_file, session, flash
from flask_login import current_user, login_required
from app.main import bp
from app.models.user import User
from app.models.application import Application
from app.models.job_posting import JobPosting
from datetime import datetime, timedelta
from bson import ObjectId
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from app.ai_agents.gemini_utils import call_gemini_api
from app.models.resume import Resume
from werkzeug.utils import secure_filename
import os
import PyPDF2
import docx
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
import re


# --- MongoDB tailored resume helpers ---
def save_best_tailored_resume(mongo_db, user_id, job_id, ats_score, resume_text, cover_letter):
    collection = mongo_db.tailored_resumes
    existing = collection.find_one({"user_id": user_id, "job_id": job_id})
    # Ensure ats_score is treated as a number for comparison
    try:
        ats_score_num = float(ats_score) if ats_score is not None else 0
        existing_score = float(existing.get("ats_score", 0)) if existing else 0
        should_update = not existing or (ats_score_num > existing_score)
    except (ValueError, TypeError):
        # If conversion fails, always update
        should_update = True
        
    if should_update:
        collection.update_one(
            {"user_id": user_id, "job_id": job_id},
            {"$set": {
                "ats_score": ats_score,
                "resume_text": resume_text,
                "cover_letter": cover_letter,
                "updated_at": datetime.utcnow(),
                "created_at": existing.get("created_at", datetime.utcnow()) if existing else datetime.utcnow()
            }},
            upsert=True
        )

def get_best_tailored_resumes(mongo_db, user_id):
    return list(mongo_db.tailored_resumes.find({"user_id": user_id}))


@bp.route('/')
def index():
    """Landing page"""
    # Redirect logged-in users to their dashboard
    if current_user.is_authenticated:
        if current_user.is_applicant():
            return redirect(url_for('main.applicant_dashboard'))
        else:
            return redirect(url_for('main.recruiter_dashboard'))
    
    return render_template('main/landing.html', title='JobMate - AI-Powered Job Matching')


@bp.route('/dashboard')
@login_required
def dashboard():
    """Generic dashboard redirect"""
    if current_user.is_applicant():
        return redirect(url_for('main.applicant_dashboard'))
    else:
        return redirect(url_for('main.recruiter_dashboard'))


@bp.route('/applicant/dashboard')
@login_required
def applicant_dashboard():
    """Applicant dashboard"""
    if not current_user.is_applicant():
        return redirect(url_for('main.recruiter_dashboard'))
    
    # Get user's active resume
    active_resume = current_user.get_active_resume()
    
    # Get recent applications (limit to 5 for dashboard)
    recent_applications = current_user.applications.order_by(
        Application.created_at.desc()
    ).limit(5).all()
    
    # Get job recommendations using the match module
    from app.models.job_posting import JobPosting
    from app.match.routes import calculate_job_match_score
    
    # Get active jobs and calculate match scores
    active_jobs = JobPosting.get_active_jobs(limit=10)
    job_matches = []
    
    if active_jobs and active_resume:
        for job in active_jobs:
            match_score = calculate_job_match_score(job, current_user, active_resume)
            if match_score > 30:  # Only show jobs with reasonable match
                job_matches.append({
                    'job': job,
                    'match_score': match_score
                })
    
    # Sort by match score and limit to top 5 for dashboard
    recommended_jobs = sorted(job_matches, key=lambda x: x['match_score'], reverse=True)[:5]
    
    # Calculate completion percentage
    completion_percentage = calculate_profile_completion(current_user)
    
    # Fetch MongoDB jobs (limit 5)
    mongo_db = current_app.mongo_db
    mongo_jobs = list(mongo_db.jobs.find({}, {"_id": 1, "title": 1, "company": 1, "description": 1}).limit(5))
    
    return render_template('dashboard/applicant.html',
                         title='Dashboard',
                         user=current_user,
                         active_resume=active_resume,
                         recent_applications=recent_applications,
                         recommended_jobs=recommended_jobs,
                         completion_percentage=completion_percentage,
                         mongo_jobs=mongo_jobs)


@bp.route('/recruiter/dashboard')
@login_required
def recruiter_dashboard():
    """Recruiter dashboard"""
    if not current_user.is_recruiter():
        return redirect(url_for('main.applicant_dashboard'))
    
    # Get recruiter's job postings
    job_postings = current_user.job_postings.order_by(
        JobPosting.created_at.desc()
    ).limit(10).all()
    
    # Calculate statistics
    total_jobs = current_user.job_postings.count()
    active_jobs = current_user.job_postings.filter_by(status='active').count()
    
    # Get recent applications to recruiter's jobs
    job_ids = [job.id for job in current_user.job_postings.all()]
    recent_applications = []
    total_applications = 0
    new_applications = 0
    
    if job_ids:
        recent_applications = Application.query.filter(
            Application.job_posting_id.in_(job_ids)
        ).order_by(Application.created_at.desc()).limit(5).all()
        
        total_applications = Application.query.filter(
            Application.job_posting_id.in_(job_ids)
        ).count()
        
        # Applications from last 7 days
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        new_applications = Application.query.filter(
            Application.job_posting_id.in_(job_ids),
            Application.created_at >= seven_days_ago
        ).count()
    
    # Mock data for demonstration
    stats = {
        'active_jobs': active_jobs,
        'total_applications': total_applications,
        'new_applications': new_applications,
        'total_views': 1250,  # Mock data
        'interview_scheduled': 8  # Mock data
    }
    
    return render_template('dashboard/recruiter.html',
                         title='Recruiter Dashboard',
                         user=current_user,
                         job_postings=job_postings,
                         recent_applications=recent_applications,
                         current_date=datetime.now().strftime('%b %d'),
                         **stats)


@bp.route('/about')
def about():
    """About page"""
    return render_template('main/about.html', title='About JobMate')


@bp.route('/features')
def features():
    """Features page"""
    return render_template('main/features.html', title='Features')


@bp.route('/pricing')
def pricing():
    """Pricing page"""
    return render_template('main/pricing.html', title='Pricing')


@bp.route('/contact')
def contact():
    """Contact page"""
    return render_template('main/contact.html', title='Contact Us')


@bp.route('/privacy')
def privacy():
    """Privacy policy page"""
    return render_template('main/privacy.html', title='Privacy Policy')


@bp.route('/terms')
def terms():
    """Terms of service page"""
    return render_template('main/terms.html', title='Terms of Service')


# API Routes
@bp.route('/api/dashboard/stats')
@login_required
def dashboard_stats():
    """Get dashboard statistics for current user"""
    
    if current_user.is_applicant():
        stats = {
            'total_applications': current_user.applications.count(),
            'pending_applications': current_user.applications.filter_by(status='pending').count(),
            'interviews_scheduled': current_user.applications.filter_by(status='interview').count(),
            'profile_completion': calculate_profile_completion(current_user),
            'active_resume': current_user.get_active_resume() is not None
        }
    else:  # recruiter
        stats = {
            'total_job_postings': current_user.job_postings.count(),
            'active_job_postings': current_user.job_postings.filter_by(status='active').count(),
            'total_applications': 0,  # TODO: Calculate applications to recruiter's jobs
            'new_applications': 0,    # TODO: Calculate new applications this week
            'candidates_reviewed': 0  # TODO: Calculate reviewed candidates
        }
    
    return jsonify(stats)


@bp.route('/api/notifications')
@login_required
def notifications():
    """Get user notifications"""
    # TODO: Implement notifications system
    notifications = [
        {
            'id': 1,
            'type': 'info',
            'title': 'Welcome to JobMate!',
            'message': 'Complete your profile to get better job matches.',
            'created_at': '2024-01-01T10:00:00Z',
            'read': False
        }
    ]
    
    return jsonify(notifications)


@bp.route('/api/available-jobs')
@login_required
def available_jobs():
    """Get list of available job postings for ATS analysis"""
    try:
        # Get active job postings with basic info
        jobs = JobPosting.query.filter_by(status='active').order_by(
            JobPosting.created_at.desc()
        ).limit(20).all()
        
        jobs_data = []
        for job in jobs:
            jobs_data.append({
                'id': job.id,
                'title': job.title,
                'company_name': job.company_name,
                'location': job.location,
                'description': job.description[:200] if job.description else '',
                'experience_level': job.experience_level,
                'job_type': job.job_type,
                'created_at': job.created_at.isoformat() if job.created_at else None
            })
        
        return jsonify({'jobs': jobs_data})
        
    except Exception as e:
        return jsonify({'error': str(e), 'jobs': []}), 500


@bp.route('/api/search')
def search():
    """Global search endpoint"""
    query = request.args.get('q', '').strip()
    search_type = request.args.get('type', 'all')  # jobs, companies, candidates
    
    if not query:
        return jsonify({'results': []})
    
    results = []
    
    if search_type in ['all', 'jobs']:
        # TODO: Search jobs in MongoDB
        pass
    
    if search_type in ['all', 'companies']:
        # TODO: Search companies
        pass
    
    if current_user.is_authenticated and current_user.is_recruiter() and search_type in ['all', 'candidates']:
        # TODO: Search candidates (only for recruiters)
        pass
    
    return jsonify({'results': results, 'total': len(results)})


@bp.route('/mongo-test')
def mongo_test():
    """Test MongoDB connection and show job count and some job details"""
    mongo_db = current_app.mongo_db
    count = mongo_db.jobs.count_documents({})
    # Fetch up to 5 job documents, only show _id and title if available
    jobs = list(mongo_db.jobs.find({}, {"_id": 1, "title": 1}).limit(5))
    job_list = "<ul>" + "".join([
        f"<li>{str(job.get('_id'))}: {job.get('title', '(no title)')}</li>" for job in jobs
    ]) + "</ul>" if jobs else "<p>No jobs found.</p>"
    return f"Job count in MongoDB: {count}<br>Sample jobs:{job_list}"


@bp.route('/mongo-jobs')
@login_required
def mongo_jobs():
    """Show jobs from MongoDB for tailoring resume/cover letter"""
    mongo_db = current_app.mongo_db
    jobs = list(mongo_db.jobs.find({}, {"_id": 1, "title": 1, "company": 1, "description": 1}))
    return render_template('mongo_jobs.html', jobs=jobs)


def extract_text_from_file(file_path, file_ext):
    if file_ext == '.pdf':
        text = ''
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ''
        return text
    elif file_ext == '.docx':
        doc = docx.Document(file_path)
        return '\n'.join([para.text for para in doc.paragraphs])
    elif file_ext == '.txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        raise ValueError('Unsupported file type')


def postprocess_tailored_resume_output(ai_result, user_resume_sections=None):
    """
    Post-process and validate the AI output for tailored resume.
    - Ensures all required sections are present.
    - Fixes/corrects LinkedIn/contact fields.
    - Deduplicates and merges with user data if needed.
    - Cleans up formatting and section order.
    """
    import re
    required_sections = ["Summary", "Skills", "Experience", "Education"]
    resume_text = ai_result.get("tailored_resume", "")
    # Parse into sections
    def parse_sections(text):
        section_pattern = re.compile(r"^([A-Za-z &]+):$", re.MULTILINE)
        sections = {}
        last = None
        for line in text.splitlines():
            m = section_pattern.match(line.strip())
            if m:
                last = m.group(1).strip()
                sections[last] = []
            elif last:
                sections[last].append(line)
        return sections
    ai_sections = parse_sections(resume_text)
    # Merge with user resume if provided
    if user_resume_sections:
        for sec in required_sections:
            if sec not in ai_sections and sec.upper() in user_resume_sections:
                ai_sections[sec] = user_resume_sections[sec.upper()]
    # Ensure all required sections exist
    for sec in required_sections:
        if sec not in ai_sections:
            ai_sections[sec] = ["(Not provided)"]
    # Fix LinkedIn/contact fields in header
    header_lines = []
    for k in ["Name", "Contact", "Location"]:
        found = False
        for line in resume_text.splitlines():
            if line.strip().lower().startswith(f"{k.lower()}:"):
                val = line.split(":", 1)[-1].strip()
                if k == "Contact":
                    # Try to fix LinkedIn if missing protocol
                    val = re.sub(r"(linkedin\\.com/[^ |]+)", r"https://\\1", val)
                header_lines.append(f"{k}: {val}")
                found = True
                break
        if not found:
            header_lines.append(f"{k}: (Not provided)")
    # Rebuild resume text in canonical order
    section_order = ["Summary", "Skills", "Experience", "Education"] + [k for k in ai_sections if k not in required_sections]
    rebuilt = []
    rebuilt.append("---")
    rebuilt.extend(header_lines)
    rebuilt.append("")
    for sec in section_order:
        rebuilt.append(f"{sec}:")
        rebuilt.extend([l for l in ai_sections[sec] if l.strip()])
        rebuilt.append("")
    rebuilt.append("---")
    ai_result["tailored_resume"] = "\n".join(rebuilt)
    return ai_result


@bp.route('/tailor/<job_id>', methods=['GET', 'POST'])
@login_required
def tailor_resume(job_id):
    """Tailor resume or cover letter for a specific job using Gemini AI"""
    mongo_db = current_app.mongo_db
    job = mongo_db.jobs.find_one({"_id": ObjectId(job_id)})
    if not job:
        return "Job not found", 404

    tailored_result = None
    ats_score = None
    error = None
    resume_text = None
    
    # Get application URL from job data using the correct field name
    application_url = job.get('job_url_direct') or job.get('application_url') or job.get('company_website')
    application_email = job.get('email') or job.get('application_email') or job.get('contact_email')

    if request.method == 'POST':
        # Handle file upload
        if 'resume_file' not in request.files or request.files['resume_file'].filename == '':
            error = 'Please upload a resume file.'
        else:
            resume_file = request.files['resume_file']
            filename = secure_filename(resume_file.filename)
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext not in ['.pdf', '.docx', '.txt']:
                error = 'Unsupported file type. Please upload PDF, DOCX, or TXT.'
            else:
                temp_path = os.path.join('/tmp', filename)
                resume_file.save(temp_path)
                try:
                    resume_text = extract_text_from_file(temp_path, file_ext)
                    session['user_resume_text'] = resume_text  # Save user resume text for later PDF export
                except Exception as e:
                    error = f'Failed to extract text from resume: {e}'
                finally:
                    os.remove(temp_path)

        if resume_text and not error:
            # Prepare prompt for Gemini
            prompt = f"""
# RESUME TAILORING TASK

You are an expert ATS optimization specialist and resume writer with deep expertise in the tech sector. Your task is to tailor the candidate's resume to maximize ATS match score and appeal to hiring managers for the specific job description.

## JOB DESCRIPTION
```
{job.get('description', '')}
```

## ORIGINAL RESUME
```
{resume_text}
```

## TAILORING INSTRUCTIONS

1. MAINTAIN ACCURACY: Never fabricate experience, education, or skills not mentioned in the original resume.

2. KEYWORD OPTIMIZATION:
   - Identify primary and secondary keywords from the job description
   - Naturally integrate these keywords into appropriate sections of the resume
   - Match phrasing used in the job description where appropriate
   - Ensure keyword density is optimized but not excessive (aim for 5-8 exact matches per key requirement)
   - Focus especially on technical skills, tools, and methodologies mentioned in the job

3. FORMATTING & STRUCTURE:
   - Use clean, ATS-friendly formatting
   - Prioritize relevant experience and skills based on job requirements
   - Use standard section headings that ATS systems recognize
   - Maintain chronological order within sections
   - Use bullet points for readability
   - Format the resume using the specified structure below

4. CONTENT ENHANCEMENT:
   - Transform generic statements into achievement-focused bullets
   - For EACH job experience, include EXACTLY 5 bullet points - no more, no less
   - Each bullet point MUST include metrics (numbers, percentages, dollar amounts) and demonstrate clear impact
   - Use strong action verbs at the beginning of bullet points (e.g., Increased, Developed, Implemented)
   - Cover different aspects in the 5 bullets: technical skills, leadership, problem-solving, collaboration, and quantifiable business impact
   - Organize the Skills section with clear subheadings (Programming Languages, Frameworks & Libraries, etc.)
   - Under each skill subheading, list specific skills separated by commas (not as bullet points)
   - Match skills specifically to those mentioned in the job description, prioritizing exact keyword matches
   - Highlight transferable skills that match the job requirements
   - Emphasize Ontario tech sector experience if available

## REQUIRED OUTPUT FORMAT
Format the tailored resume as plain text in the following structure:

---
Name: <Full Name>
Contact: <Email> | <Phone> | <LinkedIn>
Location: <City, Province>

Summary:
<Professional summary paragraph highlighting key qualifications relevant to job>

Skills:
Programming Languages: <List key programming languages from resume that match job requirements>
Frameworks & Libraries: <List relevant frameworks and libraries that match job requirements>
Tools & Technologies: <List relevant tools, platforms, and technologies from resume>
Cloud & Infrastructure: <List cloud platforms (AWS, Azure, GCP) and infrastructure tools (Terraform, Kubernetes) that match job requirements>
Databases & Storage: <List databases (SQL, NoSQL, PostgreSQL, MongoDB) and data storage solutions from resume>
Domain Knowledge: <List industry-specific skills and knowledge areas>
Soft Skills: <List 3-5 most relevant soft skills for the position>

Experience:
<Company Name> | <Job Title> | <Start Date> - <End Date>
- <Quantified achievement with specific metrics (e.g., "Increased application performance by 40% through database optimization")>
- <Technical achievement demonstrating skills required in job posting with measurable outcome>
- <Leadership or collaborative achievement showing teamwork with quantifiable results>
- <Problem-solving achievement with clear business impact and metrics>
- <Innovation or project accomplishment directly relevant to job requirements with measurable success>

# REPEAT THE ABOVE FORMAT WITH EXACTLY 5 BULLET POINTS FOR EACH JOB EXPERIENCE

Education:
<Degree> | <Institution> | <Graduation Year>

---

## OUTPUT REQUIREMENTS

Provide your response in JSON format with the following structure:

```json
{{
  "tailored_resume": "The complete tailored resume text with appropriate formatting",
  "cover_letter": "A matching cover letter highlighting key qualifications for this role",
  "ats_score": "A number between 0-100 representing the estimated ATS match score",
  "suggestions": [
    {{
      "area": "Specific section or aspect of the resume",
      "suggestion": "Detailed actionable suggestion to further improve the resume"
    }}
    // Include 5-8 specific suggestions
  ]
}}
```

For the suggestions, focus on:
1. Areas where keywords could be better integrated
2. Achievements that could be better quantified
3. Skills that should be emphasized based on the job
4. Format improvements for ATS optimization
5. Section ordering or content prioritization

Be specific and actionable with each suggestion.
"""
            gemini_response = call_gemini_api(prompt)
            import json
            if 'candidates' in gemini_response:
                try:
                    content = gemini_response['candidates'][0]['content']['parts'][0]['text']
                    # Try to parse as JSON, but if it fails, attempt to extract JSON from text
                    try:
                        result = json.loads(content)
                        tailored_result = result
                        # Ensure ats_score is a number
                        ats_score_raw = result.get('ats_score')
                        if isinstance(ats_score_raw, str):
                            # Try to extract numeric value if it's a string like "85/100" or just "85"
                            ats_score_match = re.search(r'(\d+)', ats_score_raw)
                            ats_score = int(ats_score_match.group(1)) if ats_score_match else None
                        else:
                            # Keep as is if it's already a number
                            ats_score = ats_score_raw
                    except Exception as e:
                        import re
                        match = re.search(r'\{.*\}', content, re.DOTALL)
                        if match:
                            try:
                                result = json.loads(match.group(0))
                                tailored_result = result
                                # Ensure ats_score is a number
                                ats_score_raw = result.get('ats_score')
                                if isinstance(ats_score_raw, str):
                                    # Try to extract numeric value if it's a string like "85/100" or just "85"
                                    ats_score_match = re.search(r'(\d+)', ats_score_raw)
                                    ats_score = int(ats_score_match.group(1)) if ats_score_match else None
                                else:
                                    # Keep as is if it's already a number
                                    ats_score = ats_score_raw
                            except Exception as e2:
                                error = f"Failed to parse extracted JSON: {e2}. Raw response: {content}"
                        else:
                            error = f"Failed to parse Gemini response as JSON: {e}. Raw response: {content}"
                except Exception as e:
                    error = f"Failed to extract Gemini response: {e}"
            else:
                error = gemini_response.get('error', 'Unknown error from Gemini API')

            # --- Post-process tailored resume output ---
            if tailored_result:
                user_sections = extract_resume_sections(resume_text) if resume_text else None
                tailored_result = postprocess_tailored_resume_output(tailored_result, user_sections)
                # Get updated ATS score and ensure it's numeric
                ats_score_raw = tailored_result.get('ats_score')
                if isinstance(ats_score_raw, str):
                    # Try to extract numeric value if it's a string like "85/100" or just "85"
                    ats_score_match = re.search(r'(\d+)', ats_score_raw)
                    ats_score = int(ats_score_match.group(1)) if ats_score_match else None
                else:
                    # Keep as is if it's already a number
                    ats_score = ats_score_raw

            # --- Save best tailored resume in MongoDB ---
            if tailored_result and ats_score is not None:
                save_best_tailored_resume(
                    mongo_db,
                    str(current_user.id),
                    str(job_id),
                    ats_score,
                    tailored_result.get('tailored_resume', ''),
                    tailored_result.get('cover_letter', '')
                )

    return render_template(
        'tailor.html', 
        job=job,
        tailored_result=tailored_result, 
        ats_score=ats_score, 
        error=error, 
        user_resume_text=resume_text if resume_text else None,
        application_url=application_url,
        application_email=application_email
    )


@bp.route('/download-tailored/<job_id>/<doc_type>', methods=['POST'])
@login_required
def download_tailored(job_id, doc_type):
    """Download tailored resume or cover letter as a PDF file with improved formatting"""
    tailored_resume = request.form.get('tailored_resume')
    cover_letter = request.form.get('cover_letter')
    if doc_type == 'resume':
        content = tailored_resume or ''
        filename = f'tailored_resume_{job_id}.pdf'
    elif doc_type == 'cover_letter':
        content = cover_letter or ''
        filename = f'cover_letter_{job_id}.pdf'
    else:
        return "Invalid document type", 400

    # PDF generation with formatting
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=0.75*inch, rightMargin=0.75*inch, topMargin=0.75*inch, bottomMargin=0.75*inch)
    styles = getSampleStyleSheet()
    story = []

    # Custom styles
    name_style = ParagraphStyle('Name', parent=styles['Heading1'], fontSize=22, alignment=TA_CENTER, spaceAfter=10, spaceBefore=10)
    contact_style = ParagraphStyle('Contact', parent=styles['Normal'], fontSize=11, alignment=TA_CENTER, textColor=colors.black, spaceAfter=10)
    section_style = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=13, textColor=colors.HexColor('#1a4a7c'), spaceBefore=18, spaceAfter=6, leading=16, fontName='Helvetica-Bold')
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=11, leading=15, spaceAfter=6)
    bullet_style = ParagraphStyle('Bullet', parent=styles['Normal'], fontSize=11, leftIndent=15, bulletIndent=5, leading=15)

    # --- Render AI-optimized resume or cover letter only ---
    lines = [l for l in content.splitlines() if l.strip()]

    # --- Remove any '---' separator lines and extract name/contact/location ---
    name = ''
    contact = ''
    location = ''
    extra_contact = ''
    rest_lines = []
    for l in lines:
        l_strip = l.strip()
        l_lower = l_strip.lower()
        if l_strip == '---':
            continue  # skip separator
        if l_lower.startswith('name:'):
            name = l_strip.split(':', 1)[-1].strip()
        elif l_lower.startswith('contact:'):
            contact = l_strip.split(':', 1)[-1].strip()
        elif l_lower.startswith('location:'):
            location = l_strip.split(':', 1)[-1].strip()
        elif l_lower.startswith('www') or l_lower.startswith('http'):
            extra_contact = l_strip
        else:
            rest_lines.append(l_strip)

    # --- Render name bold and centered at the top (no header) ---
    if name:
        story.append(Paragraph(f'<b>{name}</b>', name_style))
    # Render contact/location line centered below name (no headers)
    contact_line = ' | '.join(filter(None, [contact, location, extra_contact]))
    if contact_line:
        story.append(Paragraph(contact_line, contact_style))
    story.append(Spacer(1, 8))

    # --- Section parsing with experience subheader logic, grouped skills, and section reordering ---
    section_keywords = [
        'summary', 'professional summary', 'skills', 'projects', 'relevant projects',
        'experience', 'professional experience', 'education', 'community & interests', 'interests', 'project experience'
    ]
    def is_section_header(line):
        l = line.strip()
        if l.endswith(':'):
            return True
        if l.isupper() and len(l) > 3:
            return True
        l_clean = l.lower().rstrip(':').strip()
        return l_clean in section_keywords

    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=11, leading=15, spaceBefore=8, spaceAfter=4, fontName='Helvetica-Bold')

    # --- Parse all sections into a dict for reordering ---
    sections = {}
    current_section = None
    section_buffer = []
    for line in rest_lines:
        l_strip = line.strip()
        if is_section_header(l_strip):
            if current_section:
                sections[current_section] = section_buffer
                section_buffer = []
            current_section = l_strip
        elif current_section:
            section_buffer.append(line)
        else:
            # If not in a section, treat as intro
            sections.setdefault('intro', []).append(line)
    if current_section:
        sections[current_section] = section_buffer

    # --- Section order: SUMMARY, EXPERIENCE, then others as found ---
    ordered_section_titles = []
    for key in sections.keys():
        if key.lower().startswith('summary'):
            ordered_section_titles.append(key)
    for key in sections.keys():
        if key.lower().startswith('experience'):
            ordered_section_titles.append(key)
    for key in sections.keys():
        # Exclude SUMMARY, EXPERIENCE, and LANGUAGE sections
        if key.lower().startswith('summary') or key.lower().startswith('experience') or key.lower().startswith('language'):
            continue
        ordered_section_titles.append(key)

    def flush_section(title, buffer):
        if not buffer:
            return
        story.append(Spacer(1, 10))
        story.append(Paragraph(f'<b>{title.rstrip(":").upper()}</b>', section_style))
        # SKILLS section: handle subheadings and skill lists
        if title.lower().startswith('skills'):
            current_category = None
            for line in buffer:
                line_strip = line.strip()
                if not line_strip:
                    continue
                    
                # Check if this is a skill category heading (ends with a colon)
                if ':' in line_strip and not line_strip.startswith('-') and not line_strip.startswith('•'):
                    # This is a category heading like "Programming Languages: Python, Java"
                    parts = line_strip.split(':', 1)
                    if len(parts) == 2:
                        category = parts[0].strip()
                        skills = parts[1].strip()
                        
                        # Add the category as a subheading
                        story.append(Paragraph(f'<b>{category}</b>', subtitle_style))
                        
                        # Add the skills as normal text (not bullets)
                        if skills:
                            story.append(Paragraph(skills, normal_style))
                    else:
                        # Just a heading without skills yet
                        story.append(Paragraph(f'<b>{line_strip}</b>', subtitle_style))
                elif line_strip.startswith('-') or line_strip.startswith('•'):
                    # Handle any bullet points that might still exist in the skills section
                    story.append(Paragraph(line_strip.lstrip('-•').strip(), bullet_style, bulletText='•'))
                else:
                    # Plain text that isn't a category heading
                    story.append(Paragraph(line_strip, normal_style))
        # EXPERIENCE section: bold subheader for lines with ' | '
        elif title.lower().startswith('experience') or title.lower().startswith('professional experience'):
            for line in buffer:
                line_strip = line.strip()
                if '|' in line_strip and not line_strip.startswith('-'):
                    story.append(Paragraph(f'<b>{line_strip}</b>', normal_style))
                elif line_strip.startswith('-') or line_strip.startswith('•'):
                    story.append(Paragraph(line_strip.lstrip('-•').strip(), bullet_style, bulletText='•'))
                else:
                    story.append(Paragraph(line_strip, normal_style))
        # EDUCATION section: bold institution name
        elif title.lower().startswith('education'):
            for line in buffer:
                line_strip = line.strip()
                # Try to bold the institution name (after first '|')
                if '|' in line_strip:
                    parts = [p.strip() for p in line_strip.split('|')]
                    if len(parts) >= 2:
                        # Assume institution is the second part
                        bolded = f"{parts[0]} | <b>{parts[1]}</b>"
                        if len(parts) > 2:
                            bolded += ' | ' + ' | '.join(parts[2:])
                        story.append(Paragraph(bolded, normal_style))
                    else:
                        story.append(Paragraph(line_strip, normal_style))
                else:
                    story.append(Paragraph(line_strip, normal_style))
        # PROJECT EXPERIENCE section: bold project titles (first non-bullet line before bullets)
        elif title.lower().startswith('project experience') or title.lower().startswith('projects'):
            in_project = False
            for idx, line in enumerate(buffer):
                line_strip = line.strip()
                if not line_strip:
                    continue
                if not (line_strip.startswith('-') or line_strip.startswith('•')):
                    # Bold project title
                    story.append(Paragraph(f'<b>{line_strip}</b>', normal_style))
                    in_project = True
                else:
                    story.append(Paragraph(line_strip.lstrip('-•').strip(), bullet_style, bulletText='•'))
        else:
            for line in buffer:
                line_strip = line.strip()
                if line_strip.startswith('-') or line_strip.startswith('•'):
                    story.append(Paragraph(line_strip.lstrip('-•').strip(), bullet_style, bulletText='•'))
                else:
                    story.append(Paragraph(line_strip, normal_style))

    # Render sections in the new order
    for section_title in ordered_section_titles:
        flush_section(section_title, sections[section_title])
    # Add extra space at end
    story.append(Spacer(1, 16))
    doc.build(story)
    buffer.seek(0)
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )


@bp.route('/download-my-tailored/<job_id>/<doc_type>', methods=['GET'])
@login_required
def download_my_tailored(job_id, doc_type):
    """Download tailored resume or cover letter for a job from the resume section (MongoDB source)"""
    mongo_db = current_app.mongo_db
    tailored = mongo_db.tailored_resumes.find_one({"user_id": str(current_user.id), "job_id": str(job_id)})
    if not tailored:
        return "No tailored resume found for this job.", 404
    if doc_type == 'resume':
        content = tailored.get('resume_text', '')
        filename = f'tailored_resume_{job_id}.pdf'
    elif doc_type == 'cover_letter':
        content = tailored.get('cover_letter', '')
        filename = f'cover_letter_{job_id}.pdf'
    else:
        return "Invalid document type", 400
    # PDF generation (reuse logic from download_tailored)
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=0.75*inch, rightMargin=0.75*inch, topMargin=0.75*inch, bottomMargin=0.75*inch)
    styles = getSampleStyleSheet()
    story = []
    name_style = ParagraphStyle('Name', parent=styles['Heading1'], fontSize=22, alignment=TA_CENTER, spaceAfter=10, spaceBefore=10)
    contact_style = ParagraphStyle('Contact', parent=styles['Normal'], fontSize=11, alignment=TA_CENTER, textColor=colors.black, spaceAfter=10)
    section_style = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=13, textColor=colors.HexColor('#1a4a7c'), spaceBefore=18, spaceAfter=6, leading=16, fontName='Helvetica-Bold')
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=11, leading=15, spaceAfter=6)
    bullet_style = ParagraphStyle('Bullet', parent=styles['Normal'], fontSize=11, leftIndent=15, bulletIndent=5, leading=15)
    lines = [l for l in content.splitlines() if l.strip()]
    name = ''
    contact = ''
    location = ''
    extra_contact = ''
    rest_lines = []
    for l in lines:
        l_strip = l.strip()
        l_lower = l_strip.lower()
        if l_strip == '---':
            continue  # skip separator
        if l_lower.startswith('name:'):
            name = l_strip.split(':', 1)[-1].strip()
        elif l_lower.startswith('contact:'):
            contact = l_strip.split(':', 1)[-1].strip()
        elif l_lower.startswith('location:'):
            location = l_strip.split(':', 1)[-1].strip()
        elif l_lower.startswith('www') or l_lower.startswith('http'):
            extra_contact = l_strip
        else:
            rest_lines.append(l_strip)
    if name:
        story.append(Paragraph(f'<b>{name}</b>', name_style))
    contact_line = ' | '.join(filter(None, [contact, location, extra_contact]))
    if contact_line:
        story.append(Paragraph(contact_line, contact_style))
    story.append(Spacer(1, 8))
    section_keywords = [
        'summary', 'professional summary', 'skills', 'projects', 'relevant projects',
        'experience', 'professional experience', 'education', 'community & interests', 'interests', 'project experience'
    ]
    def is_section_header(line):
        l = line.strip()
        if l.endswith(':'):
            return True
        if l.isupper() and len(l) > 3:
            return True
        l_clean = l.lower().rstrip(':').strip()
        return l_clean in section_keywords
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=11, leading=15, spaceBefore=8, spaceAfter=4, fontName='Helvetica-Bold')
    sections = {}
    current_section = None
    section_buffer = []
    for line in rest_lines:
        l_strip = line.strip()
        if is_section_header(l_strip):
            if current_section:
                sections[current_section] = section_buffer
                section_buffer = []
            current_section = l_strip
        elif current_section:
            section_buffer.append(line)
        else:
            sections.setdefault('intro', []).append(line)
    if current_section:
        sections[current_section] = section_buffer
    ordered_section_titles = []
    for key in sections.keys():
        if key.lower().startswith('summary'):
            ordered_section_titles.append(key)
    for key in sections.keys():
        if key.lower().startswith('experience'):
            ordered_section_titles.append(key)
    for key in sections.keys():
        if key.lower().startswith('summary') or key.lower().startswith('experience') or key.lower().startswith('language'):
            continue
        ordered_section_titles.append(key)
    def flush_section(title, buffer):
        if not buffer:
            return
        story.append(Spacer(1, 10))
        story.append(Paragraph(f'<b>{title.rstrip(":").upper()}</b>', section_style))
        if title.lower().startswith('skills'):
            group = None
            group_buffer = []
            for line in buffer:
                line_strip = line.strip()
                if line_strip.startswith('-') and len(line_strip) > 2 and not line_strip[1].isspace():
                    if group and group_buffer:
                        story.append(Paragraph(f'<b>{group.lstrip("- ")}</b>', subtitle_style))
                        for skill in group_buffer:
                            story.append(Paragraph(skill.lstrip('-•').strip(), bullet_style, bulletText='•'))
                        group_buffer = []
                    group = line_strip
                elif line_strip.startswith('-') or line_strip.startswith('•'):
                    group_buffer.append(line_strip)
                elif line_strip:
                    group_buffer.append(line_strip)
            if group and group_buffer:
                story.append(Paragraph(f'<b>{group.lstrip("- ")}</b>', subtitle_style))
                for skill in group_buffer:
                    story.append(Paragraph(skill.lstrip('-•').strip(), bullet_style, bulletText='•'))
            elif group_buffer:
                for skill in group_buffer:
                    story.append(Paragraph(skill.lstrip('-•').strip(), bullet_style, bulletText='•'))
        elif title.lower().startswith('experience') or title.lower().startswith('professional experience'):
            for line in buffer:
                line_strip = line.strip()
                if '|' in line_strip and not line_strip.startswith('-'):
                    story.append(Paragraph(f'<b>{line_strip}</b>', normal_style))
                elif line_strip.startswith('-') or line_strip.startswith('•'):
                    story.append(Paragraph(line_strip.lstrip('-•').strip(), bullet_style, bulletText='•'))
                else:
                    story.append(Paragraph(line_strip, normal_style))
        elif title.lower().startswith('education'):
            for line in buffer:
                line_strip = line.strip()
                if '|' in line_strip:
                    parts = [p.strip() for p in line_strip.split('|')]
                    if len(parts) >= 2:
                        bolded = f"{parts[0]} | <b>{parts[1]}</b>"
                        if len(parts) > 2:
                            bolded += ' | ' + ' | '.join(parts[2:])
                        story.append(Paragraph(bolded, normal_style))
                    else:
                        story.append(Paragraph(line_strip, normal_style))
                else:
                    story.append(Paragraph(line_strip, normal_style))
        elif title.lower().startswith('project experience') or title.lower().startswith('projects'):
            in_project = False
            for idx, line in enumerate(buffer):
                line_strip = line.strip()
                if not line_strip:
                    continue
                if not (line_strip.startswith('-') or line_strip.startswith('•')):
                    story.append(Paragraph(f'<b>{line_strip}</b>', normal_style))
                    in_project = True
                else:
                    story.append(Paragraph(line_strip.lstrip('-•').strip(), bullet_style, bulletText='•'))
        else:
            for line in buffer:
                line_strip = line.strip()
                if line_strip.startswith('-') or line_strip.startswith('•'):
                    story.append(Paragraph(line_strip.lstrip('-•').strip(), bullet_style, bulletText='•'))
                else:
                    story.append(Paragraph(line_strip, normal_style))
    for section_title in ordered_section_titles:
        flush_section(section_title, sections[section_title])
    story.append(Spacer(1, 16))
    doc.build(story)
    buffer.seek(0)
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )


def calculate_profile_completion(user):
    """Calculate profile completion percentage"""
    completion_items = [
        user.first_name and user.last_name,
        user.email,
        user.phone,
        user.city and user.province,
        user.get_active_resume() is not None,
        user.job_preferences is not None if user.is_applicant() else True,
        user.is_verified
    ]
    
    completed = sum(1 for item in completion_items if item)
    total = len(completion_items)
    
    return int((completed / total) * 100)

def extract_resume_sections(resume_text):
    """
    Parse resume text into a dict of sections: {section_name: [lines]}
    """
    section_headers = [
        'summary', 'professional summary', 'skills', 'projects', 'relevant projects',
        'experience', 'professional experience', 'work experience', 'education',
        'community & interests', 'interests', 'project experience', 'certifications', 'awards'
    ]
    def is_section_header(line):
        l = line.strip()
        if l.endswith(':'):
            return True
        if l.isupper() and len(l) > 3:
            return True
        l_clean = l.lower().rstrip(':').strip()
        return l_clean in section_headers
    sections = {}
    current_section = None
    section_buffer = []
    for line in resume_text.splitlines():
        l_strip = line.strip()
        if is_section_header(l_strip):
            if current_section:
                sections[current_section] = section_buffer
                section_buffer = []
            current_section = l_strip.rstrip(':').upper()
        elif current_section:
            section_buffer.append(line)
        else:
            sections.setdefault('INTRO', []).append(line)
    if current_section:
        sections[current_section] = section_buffer
    return sections

def extract_job_keywords(job_description):
    """
    Extract keywords and requirements from job description.
    Returns a dict with keys: skills, qualifications, responsibilities, keywords
    """
    # Simple regex/keyword-based extraction (can be improved with AI)
    skills = re.findall(r"[Ss]kills?[:\-\s]*([\w, .]+)", job_description)
    qualifications = re.findall(r"[Qq]ualifications?[:\-\s]*([\w, .]+)", job_description)
    responsibilities = re.findall(r"[Rr]esponsabilit(?:y|ies)[:\-\s]*([\w, .]+)", job_description)
    # Extract all unique words longer than 3 chars as keywords (can be improved)
    words = set(w.lower() for w in re.findall(r"\b\w{4,}\b", job_description))
    return {
        'skills': skills,
        'qualifications': qualifications,
        'responsibilities': responsibilities,
        'keywords': list(words)
    }


@bp.route('/my-tailored-resumes')
@login_required
def my_tailored_resumes():
    """Show all best tailored resumes and cover letters for the current user (from MongoDB)"""
    if not current_user.is_applicant():
        return redirect(url_for('main.dashboard'))
    mongo_db = current_app.mongo_db
    tailored_list = get_best_tailored_resumes(mongo_db, str(current_user.id))
    # Fetch job titles for display
    job_ids = [t['job_id'] for t in tailored_list]
    jobs = {str(j['_id']): j for j in mongo_db.jobs.find({'_id': {'$in': [ObjectId(jid) for jid in job_ids]}})}
    # Build display list
    display_list = []
    for t in tailored_list:
        job = jobs.get(t['job_id'])
        display_list.append({
            'job_id': t['job_id'],
            'job_title': job['title'] if job else '(Job not found)',
            'ats_score': t.get('ats_score'),
            'updated_at': t.get('updated_at'),
            'resume_text': t.get('resume_text', ''),
            'cover_letter': t.get('cover_letter', '')
        })
    return render_template('resume/my_resumes.html', tailored_resumes=display_list, title='My Tailored Resumes')


@bp.route('/submit-tailored-feedback/<job_id>', methods=['POST'])
@login_required
def submit_tailored_feedback(job_id):
    """Accept feedback (rating, comments) for a tailored resume/cover letter for a job."""
    if not current_user.is_applicant():
        return jsonify({'error': 'Unauthorized'}), 403
    mongo_db = current_app.mongo_db
    tailored = mongo_db.tailored_resumes.find_one({"user_id": str(current_user.id), "job_id": str(job_id)})
    if not tailored:
        return jsonify({'error': 'No tailored resume found for this job.'}), 404
    data = request.get_json() or {}
    rating = data.get('rating')  # e.g., 1-5
    comments = data.get('comments', '').strip()
    feedback_entry = {
        'rating': rating,
        'comments': comments,
        'submitted_at': datetime.utcnow()
    }
    # Store feedback as a list (history) in the tailored_resumes document
    mongo_db.tailored_resumes.update_one(
        {"user_id": str(current_user.id), "job_id": str(job_id)},
        {"$push": {"feedback": feedback_entry}}
    )
    return jsonify({'success': True, 'message': 'Feedback submitted.'})


@bp.route('/send-application/<job_id>', methods=['POST'])
@login_required
def send_application(job_id):
    """Send application email with resume and cover letter"""
    try:
        mongo_db = current_app.mongo_db
        job = mongo_db.jobs.find_one({"_id": ObjectId(job_id)})
        if not job:
            return jsonify({"success": False, "error": "Job not found"})
        
        # Get application email from job data
        application_email = job.get('email') or job.get('application_email') or job.get('contact_email')
        if not application_email:
            return jsonify({"success": False, "error": "No application email found for this job"})
        
        data = request.json
        resume_text = data.get('resume_text')
        cover_letter_text = data.get('cover_letter_text')
        
        if not resume_text or not cover_letter_text:
            return jsonify({"success": False, "error": "Resume or cover letter is missing"})
        
        # Log the application attempt
        current_app.logger.info(f"User {current_user.id} is sending application for job {job_id}")
        
        # Generate PDF attachments from the text content
        resume_pdf = io.BytesIO()
        cover_letter_pdf = io.BytesIO()
        
        # Create resume PDF
        p = canvas.Canvas(resume_pdf, pagesize=letter)
        p.setTitle(f"Resume for {job.get('title')} at {job.get('company')}")
        text_object = p.beginText(72, 750)  # 1 inch from top
        text_object.setFont("Helvetica", 12)
        for line in resume_text.split('\n'):
            text_object.textLine(line)
        p.drawText(text_object)
        p.save()
        resume_pdf.seek(0)
        
        # Create cover letter PDF
        p = canvas.Canvas(cover_letter_pdf, pagesize=letter)
        p.setTitle(f"Cover Letter for {job.get('title')} at {job.get('company')}")
        text_object = p.beginText(72, 750)  # 1 inch from top
        text_object.setFont("Helvetica", 12)
        for line in cover_letter_text.split('\n'):
            text_object.textLine(line)
        p.drawText(text_object)
        p.save()
        cover_letter_pdf.seek(0)
        
        # Prepare email
        msg = MIMEMultipart()
        msg['From'] = current_user.email
        msg['To'] = application_email
        msg['Subject'] = f"Application for {job.get('title')} position"
        
        # Email body
        body = f"""Dear Hiring Manager,

I am writing to express my interest in the {job.get('title')} position at {job.get('company')}.

Please find my resume and cover letter attached to this email.

Thank you for your consideration.

Sincerely,
{current_user.first_name} {current_user.last_name}
{current_user.email}
"""
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach resume
        resume_attachment = MIMEApplication(resume_pdf.read(), _subtype="pdf")
        resume_attachment.add_header('Content-Disposition', f'attachment; filename=resume_{current_user.last_name}.pdf')
        msg.attach(resume_attachment)
        
        # Attach cover letter
        cover_letter_attachment = MIMEApplication(cover_letter_pdf.read(), _subtype="pdf")
        cover_letter_attachment.add_header('Content-Disposition', f'attachment; filename=cover_letter_{current_user.last_name}.pdf')
        msg.attach(cover_letter_attachment)
        
        # Get SMTP settings from config
        smtp_server = current_app.config.get('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = current_app.config.get('SMTP_PORT', 587)
        smtp_user = current_app.config.get('SMTP_USER', current_user.email)
        smtp_password = current_app.config.get('SMTP_PASSWORD', '')
        
        # Send email through SMTP
        if current_app.config.get('TESTING') or not smtp_password:
            # In testing mode or if no SMTP password is configured, just log the attempt
            current_app.logger.info(f"Email would be sent to {application_email} for job {job.get('title')}")
        else:
            # Real email sending
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
        
        # Record this application in the database
        mongo_db.applications.insert_one({
            "user_id": str(current_user.id),
            "job_id": str(job_id),
            "applied_at": datetime.utcnow(),
            "method": "email",
            "status": "applied",
            "email": application_email,
            "job_title": job.get('title'),
            "company": job.get('company')
        })
        
        return jsonify({
            "success": True, 
            "message": f"Application sent successfully to {application_email}"
        })
        
    except Exception as e:
        current_app.logger.error(f"Error sending application email: {str(e)}", exc_info=True)
        return jsonify({
            "success": False, 
            "error": "An error occurred while sending your application. Please try again."
        })
