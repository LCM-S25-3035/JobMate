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
    """Upload resume page with AI parsing"""
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
        
        # If user does not select file, browser submits empty part without filename
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # Generate unique filename
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            file_extension = filename.rsplit('.', 1)[1].lower()
            
            # Ensure upload directory exists
            upload_path = os.path.join(current_app.root_path, '..', 'uploads', 'resumes')
            os.makedirs(upload_path, exist_ok=True)
            
            # Save file
            file_path = os.path.join(upload_path, unique_filename)
            file.save(file_path)
            
            try:
                # Use AI Resume Parser Agent
                from app.ai_agents.resume_parser import parse_resume_file
                
                current_app.logger.info(f"Parsing resume with AI: {file_path}")
                parsed_data = parse_resume_file(file_path, file_extension)
                
                # Extract basic info for resume record
                content = parsed_data.get('raw_text', '')
                ats_analysis = parsed_data.get('ats_analysis', {})
                ats_score = ats_analysis.get('total_score', 0)
                
                # Use AI-extracted title if available and user didn't provide one
                ai_name = parsed_data.get('personal_info', {}).get('full_name', '')
                if not title and ai_name:
                    title = f"{ai_name}'s Resume"
                
                # Create resume record
                resume = Resume(
                    user_id=current_user.id,
                    title=title or filename,
                    filename=filename,
                    file_path=unique_filename,
                    file_type=file_extension,
                    file_size=os.path.getsize(file_path),
                    parsed_content=content,
                    is_primary=current_user.resumes.count() == 0  # First resume is primary
                )
                
                # Store AI analysis results
                resume.update_ai_analysis({
                    'parsed_data': parsed_data,
                    'ats_score': ats_score,
                    'skills': parsed_data.get('skills', {}),
                    'experience_years': parsed_data.get('analysis', {}).get('total_experience_years', 0),
                    'education_level': parsed_data.get('analysis', {}).get('career_level', 'entry'),
                    'suggestions': ats_analysis.get('recommendations', [])
                })
                
                db.session.add(resume)
                db.session.commit()
                
                # Show success message with AI insights
                ai_insights = []
                if parsed_data.get('skills', {}).get('technical_skills'):
                    skill_count = len(parsed_data['skills']['technical_skills'])
                    ai_insights.append(f"{skill_count} technical skills identified")
                
                if parsed_data.get('experience'):
                    exp_count = len(parsed_data['experience'])
                    ai_insights.append(f"{exp_count} work experiences found")
                
                insights_text = " | ".join(ai_insights) if ai_insights else "Basic analysis completed"
                flash(f'Resume "{resume.title}" uploaded successfully! ATS Score: {ats_score:.0f}% | {insights_text}', 'success')
                
                current_app.logger.info(f"Resume parsed successfully: ATS Score {ats_score}")
                
            except Exception as e:
                current_app.logger.error(f"Error parsing resume with AI: {str(e)}")
                
                # Fallback to basic text extraction
                content = extract_text_from_file(file_path)
                ats_score, keywords = analyze_ats_compatibility(content)
                
                resume = Resume(
                    user_id=current_user.id,
                    title=title or filename,
                    filename=filename,
                    file_path=unique_filename,
                    file_type=file_extension,
                    file_size=os.path.getsize(file_path),
                    parsed_content=content,
                    ats_score=ats_score,
                    is_primary=current_user.resumes.count() == 0
                )
                
                db.session.add(resume)
                db.session.commit()
                
                flash(f'Resume "{resume.title}" uploaded successfully! ATS Score: {ats_score}% (Basic analysis)', 'warning')
            
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
@bp.route('/analyze-ats/<int:resume_id>/<int:job_id>')
@login_required
def analyze_ats(resume_id, job_id=None):
    """Perform detailed ATS analysis with AI, optionally against a specific job"""
    resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first_or_404()
    
    # Get job if job_id is provided
    job = None
    if job_id:
        from app.models.job_posting import JobPosting
        job = JobPosting.query.get_or_404(job_id)
    
    analysis = {}
    
    # Try to get AI analysis if available
    if resume.ai_analysis:
        ai_data = resume.ai_analysis
        if 'parsed_data' in ai_data:
            parsed_data = ai_data['parsed_data']
            
            # Use AI parser to get updated analysis
            try:
                from app.ai_agents.resume_parser import ResumeParserAgent
                parser = ResumeParserAgent()
                
                if job:
                    # Perform job-specific ATS analysis
                    ats_score, ats_analysis = parser.calculate_job_specific_ats_score(parsed_data, job)
                    analysis = {
                        'ats_score': ats_score,
                        'breakdown': ats_analysis.get('breakdown', {}),
                        'recommendations': ats_analysis.get('recommendations', []),
                        'strengths': ats_analysis.get('strengths', []),
                        'weaknesses': ats_analysis.get('weaknesses', []),
                        'parsed_data': parsed_data,
                        'skills_found': parsed_data.get('skills', {}),
                        'experience_count': len(parsed_data.get('experience', [])),
                        'education_count': len(parsed_data.get('education', [])),
                        'certifications_count': len(parsed_data.get('certifications', [])),
                        'ai_powered': True,
                        'job_specific': True,
                        'job': job
                    }
                else:
                    # General ATS analysis
                    ats_score, ats_analysis = parser.calculate_ats_score(parsed_data)
                    analysis = {
                        'ats_score': ats_score,
                        'breakdown': ats_analysis.get('breakdown', {}),
                        'recommendations': ats_analysis.get('recommendations', []),
                        'strengths': ats_analysis.get('strengths', []),
                        'weaknesses': ats_analysis.get('weaknesses', []),
                        'parsed_data': parsed_data,
                        'skills_found': parsed_data.get('skills', {}),
                        'experience_count': len(parsed_data.get('experience', [])),
                        'education_count': len(parsed_data.get('education', [])),
                        'certifications_count': len(parsed_data.get('certifications', [])),
                        'ai_powered': True,
                        'job_specific': False
                    }
                
                current_app.logger.info(f"AI-powered ATS analysis completed for resume {resume_id}")
                
            except Exception as e:
                current_app.logger.error(f"Error in AI analysis: {e}")
                if job:
                    analysis = perform_job_specific_ats_analysis(resume.parsed_content, job)
                else:
                    analysis = perform_detailed_ats_analysis(resume.parsed_content)
                analysis['ai_powered'] = False
    else:
        # Fallback to basic analysis
        if job:
            analysis = perform_job_specific_ats_analysis(resume.parsed_content, job)
        else:
            analysis = perform_detailed_ats_analysis(resume.parsed_content)
        analysis['ai_powered'] = False
    
    # Debug logging
    current_app.logger.info(f"Analysis data: strengths={analysis.get('strengths', [])}, weaknesses={analysis.get('weaknesses', [])}")
    
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


def perform_job_specific_ats_analysis(resume_content, job):
    """Perform ATS analysis specifically against a job posting"""
    from app.match.routes import extract_skills_from_text
    
    if not resume_content or not job:
        return perform_detailed_ats_analysis(resume_content)
    
    # Extract skills from job description and requirements
    job_text = f"{job.title} {job.description} {job.requirements or ''}"
    job_skills = extract_skills_from_text(job_text)
    resume_skills = extract_skills_from_text(resume_content)
    
    # Calculate skill match
    matching_skills = job_skills.intersection(resume_skills) if job_skills and resume_skills else set()
    missing_skills = job_skills - resume_skills if job_skills and resume_skills else set()
    
    # Calculate job-specific score
    base_score = 20  # Base score
    
    # Skills matching (40 points max)
    if job_skills:
        skill_match_ratio = len(matching_skills) / len(job_skills)
        skills_score = skill_match_ratio * 40
        base_score += skills_score
    
    # Experience level matching (20 points max)
    if job.experience_level:
        job_exp_level = job.experience_level.lower()
        resume_lower = resume_content.lower()
        
        if job_exp_level in resume_lower:
            base_score += 20
        elif any(level in resume_lower for level in ['experience', 'years', 'senior', 'junior', 'lead']):
            base_score += 10
    
    # Job title keyword matching (20 points max)
    job_title_words = set(word.lower() for word in job.title.split() if len(word) > 2)
    resume_words = set(word.lower() for word in resume_content.split())
    title_matches = job_title_words.intersection(resume_words)
    if title_matches:
        title_match_ratio = len(title_matches) / len(job_title_words) if job_title_words else 0
        base_score += title_match_ratio * 20
    
    final_score = min(100, base_score)
    
    analysis = {
        'ats_score': final_score,
        'overall_score': final_score,
        'keywords_found': list(matching_skills),
        'keyword_count': len(matching_skills),
        'word_count': len(resume_content.split()),
        'missing_skills': list(missing_skills),
        'matching_skills': list(matching_skills),
        'job_skills_total': len(job_skills),
        'recommendations': [],
        'strengths': [],
        'weaknesses': [],
        'job_specific': True,
        'job': job
    }
    
    # Job-specific recommendations
    if len(missing_skills) > 0:
        analysis['recommendations'].append(f'Consider adding these missing skills: {", ".join(list(missing_skills)[:5])}')
        if len(missing_skills) > len(matching_skills):
            analysis['weaknesses'].append(f'Missing {len(missing_skills)} key skills required for this role')
    
    if len(matching_skills) > 0:
        analysis['strengths'].append(f'Matches {len(matching_skills)} required skills')
    
    # Experience level analysis
    if job.experience_level:
        job_exp = job.experience_level.lower()
        if job_exp in resume_content.lower():
            analysis['strengths'].append(f'Experience level matches job requirement ({job.experience_level})')
        else:
            analysis['weaknesses'].append(f'Experience level not clearly stated for {job.experience_level} role')
            analysis['recommendations'].append(f'Highlight your {job.experience_level} level experience')
    
    # Location analysis
    if job.location and job.location.lower() not in resume_content.lower():
        analysis['recommendations'].append(f'Consider mentioning willingness to work in {job.location}')
    
    # Company size/type recommendations
    if 'startup' in job.description.lower() and 'startup' not in resume_content.lower():
        analysis['recommendations'].append('Highlight startup experience or adaptability')
    
    if 'remote' in job.description.lower() and 'remote' not in resume_content.lower():
        analysis['recommendations'].append('Mention remote work experience if applicable')
    
    # Score categorization
    if final_score >= 80:
        analysis['score_category'] = 'Excellent Match'
        analysis['score_color'] = 'success'
    elif final_score >= 60:
        analysis['score_category'] = 'Good Match'
        analysis['score_color'] = 'warning'
    elif final_score >= 40:
        analysis['score_category'] = 'Moderate Match'
        analysis['score_color'] = 'info'
    else:
        analysis['score_category'] = 'Poor Match'
        analysis['score_color'] = 'danger'
    
    return analysis 