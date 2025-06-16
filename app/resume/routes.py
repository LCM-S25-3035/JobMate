"""
Resume Routes for JobMate
Handles resume upload, management, and ATS analysis
"""

import os
import uuid
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, jsonify, current_app, send_from_directory
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from app.resume import bp
from app.models.resume import Resume
from app.models.user import User
from app import db
import PyPDF2
import docx
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False


# Allowed file extensions for resume upload
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_resume():
    """Upload resume page"""
    if not current_user.is_applicant():
        flash('Only applicants can upload resumes.', 'error')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'resume_file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['resume_file']
        title = request.form.get('title', '')
        description = request.form.get('description', '')
        
        # If user does not select file, browser submits empty part without filename
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # Generate unique filename
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            
            # Ensure upload directory exists
            upload_path = os.path.join(current_app.root_path, '..', 'uploads', 'resumes')
            os.makedirs(upload_path, exist_ok=True)
            
            # Save file
            file_path = os.path.join(upload_path, unique_filename)
            file.save(file_path)
            
            # Extract text content from file
            content = extract_text_from_file(file_path)
            
            # Create resume record
            resume = Resume(
                user_id=current_user.id,
                title=title or filename,
                file_path=unique_filename,
                content=content,
                description=description,
                file_size=os.path.getsize(file_path),
                is_primary=current_user.resumes.count() == 0  # First resume is primary
            )
            
            # Perform basic ATS analysis
            ats_score, keywords = analyze_ats_compatibility(content)
            resume.ats_score = ats_score
            resume.keywords_found = keywords
            
            db.session.add(resume)
            db.session.commit()
            
            flash(f'Resume "{resume.title}" uploaded successfully! ATS Score: {ats_score}%', 'success')
            return redirect(url_for('resume.my_resumes'))
        else:
            flash('Invalid file type. Please upload PDF, DOC, DOCX, or TXT files only.', 'error')
    
    return render_template('resume/upload.html', title='Upload Resume')


@bp.route('/my-resumes')
@login_required
def my_resumes():
    """List user's resumes"""
    if not current_user.is_applicant():
        flash('Only applicants can view resumes.', 'error')
        return redirect(url_for('main.dashboard'))
    
    resumes = current_user.resumes.order_by(Resume.created_at.desc()).all()
    return render_template('resume/my_resumes.html', title='My Resumes', resumes=resumes)


@bp.route('/view/<int:resume_id>')
@login_required
def view_resume(resume_id):
    """View resume details"""
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    return render_template('resume/view.html', title=f'Resume: {resume.title}', resume=resume)


@bp.route('/download/<int:resume_id>')
@login_required
def download_resume(resume_id):
    """Download resume file"""
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    upload_path = os.path.join(current_app.root_path, '..', 'uploads', 'resumes')
    return send_from_directory(upload_path, resume.file_path, as_attachment=True)


@bp.route('/set-primary/<int:resume_id>', methods=['POST'])
@login_required
def set_primary(resume_id):
    """Set resume as primary"""
    # Remove primary from all user's resumes
    current_user.resumes.update({'is_primary': False})
    
    # Set new primary
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    resume.is_primary = True
    
    db.session.commit()
    flash(f'Resume "{resume.title}" set as primary', 'success')
    return redirect(url_for('resume.my_resumes'))


@bp.route('/delete/<int:resume_id>', methods=['POST'])
@login_required
def delete_resume(resume_id):
    """Delete resume"""
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    
    # Delete file from filesystem
    upload_path = os.path.join(current_app.root_path, '..', 'uploads', 'resumes')
    file_path = os.path.join(upload_path, resume.file_path)
    
    if os.path.exists(file_path):
        os.remove(file_path)
    
    db.session.delete(resume)
    db.session.commit()
    
    flash(f'Resume "{resume.title}" deleted successfully', 'success')
    return redirect(url_for('resume.my_resumes'))


@bp.route('/analyze-ats/<int:resume_id>')
@login_required
def analyze_ats(resume_id):
    """Perform detailed ATS analysis"""
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    
    # Perform detailed ATS analysis
    analysis = perform_detailed_ats_analysis(resume.content)
    
    return render_template('resume/ats_analysis.html', 
                         title=f'ATS Analysis: {resume.title}', 
                         resume=resume, 
                         analysis=analysis)


# Helper Functions

def extract_text_from_file(file_path):
    """Extract text content from uploaded file"""
    text = ""
    file_extension = file_path.lower().split('.')[-1]
    
    try:
        if file_extension == 'pdf':
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        
        elif file_extension in ['doc', 'docx']:
            doc = docx.Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        
        elif file_extension == 'txt':
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
    
    except Exception as e:
        current_app.logger.error(f"Error extracting text from {file_path}: {str(e)}")
        text = "Error extracting text from file"
    
    return text.strip()


def analyze_ats_compatibility(content):
    """Basic ATS compatibility analysis"""
    if not content:
        return 0, []
    
    # Common tech keywords for Ontario market
    tech_keywords = [
        'python', 'java', 'javascript', 'sql', 'react', 'node', 'aws', 'azure',
        'machine learning', 'data science', 'artificial intelligence', 'deep learning',
        'tensorflow', 'pytorch', 'pandas', 'numpy', 'scikit-learn', 'docker',
        'kubernetes', 'git', 'agile', 'scrum', 'api', 'rest', 'microservices',
        'cloud', 'devops', 'ci/cd', 'jenkins', 'mongodb', 'postgresql', 'mysql'
    ]
    
    content_lower = content.lower()
    found_keywords = []
    
    for keyword in tech_keywords:
        if keyword in content_lower:
            found_keywords.append(keyword)
    
    # Calculate basic ATS score
    score = min(100, len(found_keywords) * 3)  # Each keyword adds 3 points, max 100
    
    # Additional scoring factors
    if len(content.split()) > 200:  # Sufficient length
        score += 10
    if '@' in content:  # Has email
        score += 5
    if any(char.isdigit() for char in content):  # Has phone number or dates
        score += 5
    
    return min(100, score), found_keywords


def perform_detailed_ats_analysis(content):
    """Perform detailed ATS analysis with recommendations"""
    basic_score, keywords = analyze_ats_compatibility(content)
    
    analysis = {
        'overall_score': basic_score,
        'keywords_found': keywords,
        'keyword_count': len(keywords),
        'word_count': len(content.split()) if content else 0,
        'recommendations': [],
        'strengths': [],
        'weaknesses': []
    }
    
    # Generate recommendations
    if analysis['keyword_count'] < 10:
        analysis['recommendations'].append('Add more relevant technical keywords')
        analysis['weaknesses'].append('Low keyword density')
    else:
        analysis['strengths'].append('Good keyword coverage')
    
    if analysis['word_count'] < 200:
        analysis['recommendations'].append('Expand resume content for better ATS parsing')
        analysis['weaknesses'].append('Resume too short')
    elif analysis['word_count'] > 800:
        analysis['recommendations'].append('Consider condensing content for better readability')
    else:
        analysis['strengths'].append('Appropriate length')
    
    if '@' not in content:
        analysis['recommendations'].append('Include email address')
        analysis['weaknesses'].append('Missing contact information')
    else:
        analysis['strengths'].append('Contact information present')
    
    # Score categorization
    if basic_score >= 80:
        analysis['score_category'] = 'Excellent'
        analysis['score_color'] = 'success'
    elif basic_score >= 60:
        analysis['score_category'] = 'Good'
        analysis['score_color'] = 'warning'
    else:
        analysis['score_category'] = 'Needs Improvement'
        analysis['score_color'] = 'danger'
    
    return analysis 