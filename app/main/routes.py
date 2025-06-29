"""
Main Routes for JobMate
Landing page, dashboards, and core application routes
"""

from flask import render_template, redirect, url_for, request, jsonify, current_app, send_file
from flask_login import current_user, login_required
from app.main import bp
from app.models.user import User
from app.models.application import Application
from app.models.job_posting import JobPosting
from datetime import datetime, timedelta
from bson import ObjectId
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
                except Exception as e:
                    error = f'Failed to extract text from resume: {e}'
                finally:
                    os.remove(temp_path)

        if resume_text and not error:
            # Prepare prompt for Gemini
            prompt = f"""
You are an expert career coach and resume writer. Given the following job description and resume, tailor the resume and generate a cover letter for this job. Also, provide an ATS (Applicant Tracking System) compatibility score (0-100) and suggestions for improvement.

Format the tailored resume as plain text in the following structure:

---
Name: <Full Name>
Contact: <Email> | <Phone> | <LinkedIn>
Location: <City, Province>

Summary:
<Professional summary paragraph>

Skills:
- Skill 1
- Skill 2
- ...

Experience:
Company Name | Job Title | Start Date - End Date
- Key achievement 1
- Key achievement 2

Education:
Degree | Institution | Graduation Year

---

Job Description:
{job.get('description', '')}

Resume:
{resume_text}

Respond in JSON with keys: tailored_resume (as plain text in the above format), cover_letter, ats_score, suggestions.
"""
            gemini_response = call_gemini_api(prompt)
            import json
            if 'candidates' in gemini_response:
                try:
                    content = gemini_response['candidates'][0]['content']['parts'][0]['text']
                    # Try to parse as JSON, but if it fails, attempt to extract JSON from text
                    try:
                        # Try direct parse
                        result = json.loads(content)
                        tailored_result = result
                        ats_score = result.get('ats_score')
                    except Exception as e:
                        # Try to extract JSON substring from the response
                        import re
                        match = re.search(r'\{.*\}', content, re.DOTALL)
                        if match:
                            try:
                                result = json.loads(match.group(0))
                                tailored_result = result
                                ats_score = result.get('ats_score')
                            except Exception as e2:
                                error = f"Failed to parse extracted JSON: {e2}. Raw response: {content}"
                        else:
                            error = f"Failed to parse Gemini response as JSON: {e}. Raw response: {content}"
                except Exception as e:
                    error = f"Failed to extract Gemini response: {e}"
            else:
                error = gemini_response.get('error', 'Unknown error from Gemini API')

    return render_template('tailor.html', job=job, tailored_result=tailored_result, ats_score=ats_score, error=error)

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

    # --- REFACTORED LOGIC: Render sections in strict DOCX order and style ---
    # Parse lines and extract all header fields and section indices first
    lines = [l for l in content.splitlines() if l.strip()]
    # Header extraction (strict: only contact/location, stop at summary/skills)
    header_lines = []
    name = ''
    for i, line in enumerate(lines[:10]):
        l = line.strip()
        l_lower = l.lower()
        # Stop if we hit a section marker
        if l_lower.startswith('summary') or l_lower.startswith('professional summary') or l_lower.startswith('skills'):
            break
        # Only include lines that look like contact/location
        if (
            '@' in l or 'linkedin' in l_lower or 'github' in l_lower or '+' in l or
            l_lower.startswith('contact:') or l_lower.startswith('location:') or
            re.match(r'.*\b(city|province|state|country|canada|usa|uk|india)\b.*', l_lower)
        ):
            header_lines.append(l)
        # Try to get name if not set and this line is not contact/location/section
        elif not name and not l_lower.startswith('name:') and not l_lower.startswith('contact:') and not l_lower.startswith('location:') and not l_lower.startswith('summary') and not l_lower.startswith('skills') and not re.match(r'.*\b(city|province|state|country|canada|usa|uk|india)\b.*', l_lower) and not ('@' in l or 'linkedin' in l_lower or 'github' in l_lower or '+' in l):
            name = l
    # Parse header fields
    contact = ''
    location = ''
    extra_contact = ''
    for l in header_lines:
        if l.lower().startswith('name:'):
            name = l.split(':', 1)[-1].strip()
        elif '@' in l or 'linkedin' in l.lower() or 'github' in l.lower() or '+' in l:
            contact = l
        elif l.lower().startswith('location:') or re.match(r'.*\b(city|province|state|country|canada|usa|uk|india)\b.*', l.lower()):
            location = l.split(':', 1)[-1].strip() if ':' in l else l.strip()
        elif l.lower().startswith('www') or l.lower().startswith('http'):
            extra_contact = l
    # Remove any prefixes
    name = re.sub(r'^(name:|name)', '', name, flags=re.I).strip()
    contact = re.sub(r'^(contact:|contact)', '', contact, flags=re.I).strip()
    location = re.sub(r'^(location:|location)', '', location, flags=re.I).strip()
    # Section titles in order
    section_titles = [
        'PROFESSIONAL SUMMARY', 'SUMMARY', 'SKILLS', 'RELEVANT PROJECTS', 'PROJECTS',
        'PROFESSIONAL EXPERIENCE', 'EXPERIENCE', 'EDUCATION', 'COMMUNITY & INTERESTS', 'INTERESTS'
    ]
    # Helper: find section start indices
    section_indices = {}
    for idx, line in enumerate(lines):
        l = line.strip().upper()
        for title in section_titles:
            if l.startswith(title):
                section_indices[title] = idx
    # Helper: extract lines for a given section
    def extract_section_lines(section_name):
        idx = None
        for t in section_titles:
            if t.startswith(section_name):
                idx = section_indices.get(t)
                if idx is not None:
                    break
        if idx is None:
            return []
        # Find next section or end
        next_idx = len(lines)
        for t, i in section_indices.items():
            if i > idx and i < next_idx:
                next_idx = i
        return [l.strip() for l in lines[idx+1:next_idx] if l.strip()]
    # Header rendering
    if name:
        story.insert(0, Paragraph(f'<b>{name}</b>', name_style))
    contact_line = ' | '.join(filter(None, [contact, location, extra_contact]))
    if contact_line:
        story.append(Paragraph(contact_line, contact_style))
    story.append(Spacer(1, 8))
    # PROFESSIONAL SUMMARY
    summary_lines = extract_section_lines('PROFESSIONAL SUMMARY') or extract_section_lines('SUMMARY')
    if summary_lines:
        story.append(Paragraph('PROFESSIONAL SUMMARY', section_style))
        story.append(Paragraph(' '.join(summary_lines), normal_style))
    # SKILLS (auto-grouped: detect categories, split comma-separated, bold group headings)
    skills_lines = extract_section_lines('SKILLS')
    if skills_lines:
        story.append(Paragraph('SKILLS', section_style))
        # Define categories and keywords
        categories = {
            'Programming Languages': ['python', 'java', 'c++', 'c#', 'javascript', 'typescript', 'r', 'go', 'ruby', 'php', 'scala', 'swift'],
            'Frameworks': ['tensorflow', 'pytorch', 'keras', 'scikit-learn', 'django', 'flask', 'react', 'angular', 'vue', 'spring'],
            'Libraries/Packages': ['numpy', 'pandas', 'matplotlib', 'seaborn', 'scipy', 'sklearn', 'opencv', 'nltk', 'spacy'],
            'Databases': ['sql', 'mysql', 'postgresql', 'mongodb', 'sqlite', 'redis', 'oracle'],
            'Cloud/DevOps': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'ci/cd', 'jenkins', 'git', 'github', 'gitlab'],
            'Data Science': ['data analysis', 'data validation', 'data visualization', 'model deployment', 'machine learning', 'deep learning', 'nlp', 'computer vision'],
            'Soft Skills': ['problem-solving', 'teamwork', 'communication', 'leadership', 'risk assessment', 'agile', 'scrum'],
            'Other': []
        }
        grouped = {cat: [] for cat in categories}
        # Flatten and split skills
        for item in skills_lines:
            line = item.lstrip('-•').strip()
            # Split comma-separated
            for skill in re.split(r',|;', line):
                skill = skill.strip()
                if not skill:
                    continue
                found = False
                for cat, keywords in categories.items():
                    for kw in keywords:
                        if kw.lower() in skill.lower():
                            grouped[cat].append(skill)
                            found = True
                            break
                    if found:
                        break
                if not found:
                    grouped['Other'].append(skill)
        # Render groups (skip empty)
        for cat, skills in grouped.items():
            if skills:
                story.append(Paragraph(f'<b>{cat}:</b>', normal_style))
                for skill in skills:
                    story.append(Paragraph(skill, bullet_style, bulletText='•'))
    # RELEVANT PROJECTS
    projects_lines = extract_section_lines('RELEVANT PROJECTS') or extract_section_lines('PROJECTS')
    if projects_lines:
        story.append(Paragraph('RELEVANT PROJECTS', section_style))
        current_project = None
        for line in projects_lines:
            if not (line.startswith('-') or line.startswith('•')):
                current_project = line
                story.append(Paragraph(current_project, bullet_style, bulletText='•'))
            else:
                story.append(Paragraph(line.lstrip('-•').strip(), normal_style))
    # PROFESSIONAL EXPERIENCE
    experience_lines = extract_section_lines('PROFESSIONAL EXPERIENCE') or extract_section_lines('EXPERIENCE')
    if experience_lines:
        story.append(Paragraph('PROFESSIONAL EXPERIENCE', section_style))
        current_exp = None
        for line in experience_lines:
            if not (line.startswith('-') or line.startswith('•')):
                current_exp = line
                story.append(Paragraph(current_exp, bullet_style, bulletText='•'))
            else:
                story.append(Paragraph(line.lstrip('-•').strip(), normal_style))
    # EDUCATION
    education_lines = extract_section_lines('EDUCATION')
    if education_lines:
        story.append(Paragraph('EDUCATION', section_style))
        for line in education_lines:
            if not (line.startswith('-') or line.startswith('•')):
                story.append(Paragraph(line, normal_style))
            else:
                story.append(Paragraph(line.lstrip('-•').strip(), normal_style))
    # COMMUNITY & INTERESTS (optional)
    interests_lines = extract_section_lines('COMMUNITY & INTERESTS') or extract_section_lines('INTERESTS')
    if interests_lines:
        story.append(Paragraph('COMMUNITY & INTERESTS', section_style))
        for item in interests_lines:
            story.append(Paragraph(item.lstrip('-•').strip(), bullet_style, bulletText='•'))
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