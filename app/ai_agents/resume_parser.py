"""
Resume Parser Agent for JobMate
Uses Google Gemini AI to parse and analyze resume content
"""

import json
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

import google.generativeai as genai
from PyPDF2 import PdfReader
from docx import Document
from flask import current_app

logger = logging.getLogger(__name__)


class ResumeParserAgent:
    """
    AI-powered resume parser using Google Gemini
    Extracts structured data from resume files
    """
    
    def __init__(self):
        """Initialize the parser with Gemini configuration"""
        self.model = None
        self._configure_gemini()
    
    def _configure_gemini(self):
        """Configure Gemini AI model"""
        try:
            api_key = current_app.config.get('GEMINI_API_KEY')
            if not api_key:
                logger.error("GEMINI_API_KEY not found in configuration")
                return
            
            genai.configure(api_key=api_key)
            model_name = current_app.config.get('GEMINI_MODEL', 'gemini-1.5-flash')
            self.model = genai.GenerativeModel(model_name)
            logger.info(f"Gemini model {model_name} configured successfully")
            
        except Exception as e:
            logger.error(f"Failed to configure Gemini: {e}")
            self.model = None
    
    def extract_text_from_file(self, file_path: str, file_type: str) -> str:
        """Extract text content from uploaded resume file"""
        try:
            if file_type.lower() == 'pdf':
                return self._extract_from_pdf(file_path)
            elif file_type.lower() in ['docx', 'doc']:
                return self._extract_from_docx(file_path)
            elif file_type.lower() == 'txt':
                return self._extract_from_txt(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
                
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            return ""
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            logger.error(f"Error reading PDF: {e}")
        return text.strip()
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        text = ""
        try:
            doc = Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            logger.error(f"Error reading DOCX: {e}")
        return text.strip()
    
    def _extract_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error reading TXT: {e}")
            return ""
    
    def parse_resume(self, resume_text: str) -> Dict:
        """Parse resume text using Gemini AI"""
        if not self.model:
            logger.error("Gemini model not configured")
            return self._fallback_parse(resume_text)
        
        try:
            prompt = self._create_parsing_prompt(resume_text)
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                return self._process_gemini_response(response.text)
            else:
                logger.warning("Empty response from Gemini")
                return self._fallback_parse(resume_text)
                
        except Exception as e:
            logger.error(f"Error parsing resume with Gemini: {e}")
            return self._fallback_parse(resume_text)
    
    def _create_parsing_prompt(self, resume_text: str) -> str:
        """Create a detailed prompt for Gemini to parse the resume"""
        return f"""
Please analyze this resume and extract structured information as JSON:

Resume Text:
{resume_text}

Return ONLY valid JSON with this structure:
{{
    "personal_info": {{
        "full_name": "string",
        "email": "string", 
        "phone": "string",
        "location": "string",
        "linkedin": "string",
        "website": "string"
    }},
    "professional_summary": "string",
    "skills": {{
        "technical_skills": ["list"],
        "soft_skills": ["list"], 
        "tools_technologies": ["list"],
        "programming_languages": ["list"],
        "frameworks": ["list"],
        "databases": ["list"]
    }},
    "experience": [
        {{
            "job_title": "string",
            "company": "string",
            "location": "string", 
            "start_date": "YYYY-MM",
            "end_date": "YYYY-MM or Present",
            "duration_months": 12,
            "responsibilities": ["list"],
            "achievements": ["list"],
            "technologies_used": ["list"]
        }}
    ],
    "education": [
        {{
            "degree": "string",
            "field_of_study": "string",
            "institution": "string",
            "location": "string",
            "graduation_date": "YYYY-MM",
            "gpa": "string",
            "relevant_coursework": ["list"]
        }}
    ],
    "certifications": [
        {{
            "name": "string", 
            "issuer": "string",
            "date_obtained": "YYYY-MM",
            "expiry_date": "YYYY-MM or null"
        }}
    ],
    "projects": [
        {{
            "name": "string",
            "description": "string", 
            "technologies": ["list"],
            "url": "string"
        }}
    ],
    "languages": [
        {{
            "language": "string",
            "proficiency": "string"
        }}
    ],
    "analysis": {{
        "total_experience_years": 5,
        "career_level": "mid",
        "primary_field": "Software Development",
        "key_strengths": ["list"],
        "missing_sections": ["list"],
        "ats_keywords": ["list"]
    }}
}}

Return ONLY the JSON, no additional text.
"""
    
    def _process_gemini_response(self, response_text: str) -> Dict:
        """Process and validate Gemini's JSON response"""
        try:
            # Clean the response text
            cleaned_text = response_text.strip()
            
            # Remove code block markers if present
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith('```'):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]
            
            # Parse JSON
            parsed_data = json.loads(cleaned_text.strip())
            
            # Validate and fill missing fields
            return self._validate_parsed_data(parsed_data)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return self._create_empty_structure()
        except Exception as e:
            logger.error(f"Error processing Gemini response: {e}")
            return self._create_empty_structure()
    
    def _validate_parsed_data(self, data: Dict) -> Dict:
        """Validate and ensure all required fields are present"""
        validated = self._create_empty_structure()
        
        try:
            # Update with parsed data, keeping structure intact
            if isinstance(data, dict):
                for key in validated.keys():
                    if key in data:
                        validated[key] = data[key]
            
            return validated
            
        except Exception as e:
            logger.error(f"Error validating parsed data: {e}")
            return self._create_empty_structure()
    
    def _create_empty_structure(self) -> Dict:
        """Create empty structure for parsed resume data"""
        return {
            "personal_info": {
                "full_name": "",
                "email": "",
                "phone": "",
                "location": "",
                "linkedin": "",
                "website": ""
            },
            "professional_summary": "",
            "skills": {
                "technical_skills": [],
                "soft_skills": [],
                "tools_technologies": [],
                "programming_languages": [],
                "frameworks": [],
                "databases": []
            },
            "experience": [],
            "education": [],
            "certifications": [],
            "projects": [],
            "languages": [],
            "analysis": {
                "total_experience_years": 0,
                "career_level": "entry",
                "primary_field": "",
                "key_strengths": [],
                "missing_sections": [],
                "ats_keywords": []
            }
        }
    
    def _fallback_parse(self, resume_text: str) -> Dict:
        """Fallback parsing when Gemini is not available"""
        logger.info("Using fallback parsing method")
        
        result = self._create_empty_structure()
        
        # Basic email extraction
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, resume_text)
        if emails:
            result['personal_info']['email'] = emails[0]
        
        # Basic phone extraction
        phone_pattern = r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        phones = re.findall(phone_pattern, resume_text)
        if phones:
            result['personal_info']['phone'] = ''.join(phones[0])
        
        # Basic skills extraction
        common_skills = [
            'python', 'javascript', 'java', 'react', 'node.js', 'sql', 'html', 'css',
            'machine learning', 'data science', 'aws', 'docker', 'kubernetes', 'git'
        ]
        
        found_skills = []
        text_lower = resume_text.lower()
        for skill in common_skills:
            if skill in text_lower:
                found_skills.append(skill.title())
        
        result['skills']['technical_skills'] = found_skills
        result['analysis']['ats_keywords'] = found_skills
        
        return result
    
    def calculate_ats_score(self, parsed_data: Dict, job_keywords: List[str] = None) -> Tuple[float, Dict]:
        """Calculate ATS compatibility score"""
        score = 0
        analysis = {
            'total_score': 0,
            'breakdown': {},
            'recommendations': [],
            'strengths': [],
            'weaknesses': []
        }
        
        try:
            # Contact Information (20 points)
            contact_score = 0
            if parsed_data['personal_info']['email']:
                contact_score += 8
                analysis['strengths'].append('Email address provided')
            else:
                analysis['recommendations'].append('Add email address')
            
            if parsed_data['personal_info']['phone']:
                contact_score += 6
                analysis['strengths'].append('Phone number provided')
            
            if parsed_data['personal_info']['location']:
                contact_score += 6
                analysis['strengths'].append('Location provided')
            
            analysis['breakdown']['contact_info'] = contact_score
            score += contact_score
            
            # Skills Section (30 points)
            skills_score = 0
            total_skills = (len(parsed_data['skills']['technical_skills']) + 
                          len(parsed_data['skills']['programming_languages']) +
                          len(parsed_data['skills']['frameworks']))
            
            if total_skills >= 10:
                skills_score = 30
                analysis['strengths'].append('Comprehensive skills section')
            elif total_skills >= 5:
                skills_score = 20
                analysis['strengths'].append('Good technical skills coverage')
            elif total_skills >= 1:
                skills_score = 10
                analysis['weaknesses'].append('Limited technical skills listed')
            else:
                analysis['recommendations'].append('Add technical skills')
                analysis['weaknesses'].append('No technical skills found')
            
            analysis['breakdown']['skills'] = skills_score
            score += skills_score
            
            # Experience Section (30 points)
            exp_score = 0
            experiences = parsed_data['experience']
            
            if len(experiences) >= 3:
                exp_score = 30
                analysis['strengths'].append('Strong work history')
            elif len(experiences) >= 2:
                exp_score = 20
                analysis['strengths'].append('Adequate work experience')
            elif len(experiences) >= 1:
                exp_score = 10
                analysis['weaknesses'].append('Limited work experience')
            else:
                analysis['recommendations'].append('Add work experience')
                analysis['weaknesses'].append('No work experience listed')
            
            analysis['breakdown']['experience'] = exp_score
            score += exp_score
            
            # Education Section (20 points)
            edu_score = 0
            if parsed_data['education']:
                edu_score = 20
                analysis['strengths'].append('Education provided')
            else:
                analysis['recommendations'].append('Add education')
                analysis['weaknesses'].append('No education information provided')
            
            analysis['breakdown']['education'] = edu_score
            score += edu_score
            
            analysis['total_score'] = min(score, 100)
            
            return analysis['total_score'], analysis
            
        except Exception as e:
            logger.error(f"Error calculating ATS score: {e}")
            return 0, {'error': str(e)}
    
    def calculate_job_specific_ats_score(self, parsed_data: Dict, job) -> Tuple[float, Dict]:
        """Calculate ATS compatibility score against a specific job posting"""
        score = 0
        analysis = {
            'total_score': 0,
            'breakdown': {},
            'recommendations': [],
            'strengths': [],
            'weaknesses': []
        }
        
        try:
            # Extract job requirements
            job_text = f"{job.title} {job.description} {job.requirements or ''}"
            job_skills = self._extract_skills_from_job(job_text)
            resume_skills = self._get_all_resume_skills(parsed_data)
            
            # Contact Information (15 points)
            contact_score = 0
            if parsed_data['personal_info']['email']:
                contact_score += 6
            if parsed_data['personal_info']['phone']:
                contact_score += 5
            if parsed_data['personal_info']['location']:
                contact_score += 4
            
            analysis['breakdown']['contact_info'] = contact_score
            score += contact_score
            
            # Job-Specific Skills Matching (40 points)
            skills_score = 0
            matching_skills = job_skills.intersection(resume_skills)
            missing_skills = job_skills - resume_skills
            
            if job_skills:
                match_ratio = len(matching_skills) / len(job_skills)
                skills_score = match_ratio * 40
                
                if match_ratio >= 0.8:
                    analysis['strengths'].append(f'Excellent skill match ({len(matching_skills)}/{len(job_skills)} skills)')
                elif match_ratio >= 0.5:
                    analysis['strengths'].append(f'Good skill match ({len(matching_skills)}/{len(job_skills)} skills)')
                else:
                    analysis['weaknesses'].append(f'Limited skill match ({len(matching_skills)}/{len(job_skills)} skills)')
                
                if missing_skills:
                    missing_list = list(missing_skills)[:5]  # Show top 5 missing
                    analysis['recommendations'].append(f'Consider learning: {", ".join(missing_list)}')
            
            analysis['breakdown']['job_skills'] = skills_score
            score += skills_score
            
            # Experience Level Matching (20 points)
            exp_score = 0
            if job.experience_level:
                job_exp_level = job.experience_level.lower()
                total_experience = parsed_data['analysis']['total_experience_years']
                career_level = parsed_data['analysis']['career_level'].lower()
                
                # Match experience requirements
                if job_exp_level in ['entry', 'junior'] and total_experience <= 2:
                    exp_score = 20
                    analysis['strengths'].append('Experience level matches job requirement')
                elif job_exp_level in ['mid', 'intermediate'] and 2 <= total_experience <= 5:
                    exp_score = 20
                    analysis['strengths'].append('Experience level matches job requirement')
                elif job_exp_level == 'senior' and total_experience >= 5:
                    exp_score = 20
                    analysis['strengths'].append('Experience level matches job requirement')
                elif career_level == job_exp_level:
                    exp_score = 15
                    analysis['strengths'].append('Career level aligns with job')
                else:
                    exp_score = 5
                    analysis['weaknesses'].append(f'Experience level may not match {job.experience_level} requirement')
                    analysis['recommendations'].append(f'Highlight relevant {job.experience_level} level skills')
            
            analysis['breakdown']['experience_level'] = exp_score
            score += exp_score
            
            # Job Title Relevance (15 points)
            title_score = 0
            job_title_words = set(word.lower() for word in job.title.split() if len(word) > 2)
            resume_text_all = self._get_resume_full_text(parsed_data)
            resume_words = set(word.lower() for word in resume_text_all.split())
            
            title_matches = job_title_words.intersection(resume_words)
            if title_matches:
                match_ratio = len(title_matches) / len(job_title_words) if job_title_words else 0
                title_score = match_ratio * 15
                
                if match_ratio >= 0.5:
                    analysis['strengths'].append('Resume content aligns with job title')
                else:
                    analysis['recommendations'].append('Include more job-title relevant keywords')
            
            analysis['breakdown']['title_relevance'] = title_score
            score += title_score
            
            # Industry/Domain Match (10 points)
            industry_score = 0
            if hasattr(job, 'industry') and job.industry:
                industry_keywords = job.industry.lower().split()
                if any(keyword in resume_text_all.lower() for keyword in industry_keywords):
                    industry_score = 10
                    analysis['strengths'].append('Industry experience evident')
                else:
                    analysis['recommendations'].append(f'Highlight {job.industry} industry experience')
            else:
                industry_score = 5  # Default if no industry specified
            
            analysis['breakdown']['industry_match'] = industry_score
            score += industry_score
            
            # Final score calculation
            final_score = min(score, 100)
            analysis['total_score'] = final_score
            
            # Overall assessment
            if final_score >= 85:
                analysis['overall_assessment'] = 'Excellent match for this position'
            elif final_score >= 70:
                analysis['overall_assessment'] = 'Strong candidate for this role'
            elif final_score >= 55:
                analysis['overall_assessment'] = 'Good potential with some improvements'
            elif final_score >= 40:
                analysis['overall_assessment'] = 'Moderate fit, significant gaps to address'
            else:
                analysis['overall_assessment'] = 'Limited match, extensive improvements needed'
            
            return final_score, analysis
            
        except Exception as e:
            logger.error(f"Error calculating job-specific ATS score: {e}")
            return 0, {'error': str(e), 'recommendations': [], 'strengths': [], 'weaknesses': []}
    
    def _extract_skills_from_job(self, job_text: str) -> set:
        """Extract technical skills mentioned in job posting"""
        common_skills = {
            'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue', 'node.js',
            'express', 'django', 'flask', 'spring', 'mysql', 'postgresql', 'mongodb', 'redis',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'github',
            'html', 'css', 'bootstrap', 'tailwind', 'sass', 'rest api', 'graphql',
            'machine learning', 'ai', 'data science', 'tensorflow', 'pytorch', 'pandas',
            'numpy', 'scikit-learn', 'sql server', 'oracle', 'elasticsearch', 'kafka',
            'microservices', 'devops', 'ci/cd', 'agile', 'scrum', 'jira', 'confluence'
        }
        
        job_text_lower = job_text.lower()
        found_skills = set()
        
        for skill in common_skills:
            if skill in job_text_lower:
                found_skills.add(skill)
        
        return found_skills
    
    def _get_all_resume_skills(self, parsed_data: Dict) -> set:
        """Get all skills from parsed resume data"""
        skills = set()
        
        skills_data = parsed_data.get('skills', {})
        for skill_category in ['technical_skills', 'programming_languages', 'frameworks', 'tools_technologies']:
            if skill_category in skills_data:
                skills.update(skill.lower() for skill in skills_data[skill_category])
        
        # Also add from analysis keywords
        analysis = parsed_data.get('analysis', {})
        if 'ats_keywords' in analysis:
            skills.update(keyword.lower() for keyword in analysis['ats_keywords'])
        
        return skills
    
    def _get_resume_full_text(self, parsed_data: Dict) -> str:
        """Get full text representation of resume for keyword matching"""
        text_parts = []
        
        # Add professional summary
        if parsed_data.get('professional_summary'):
            text_parts.append(parsed_data['professional_summary'])
        
        # Add experience descriptions
        for exp in parsed_data.get('experience', []):
            if 'description' in exp:
                text_parts.append(exp['description'])
            if 'responsibilities' in exp:
                text_parts.append(' '.join(exp['responsibilities']) if isinstance(exp['responsibilities'], list) else exp['responsibilities'])
        
        # Add project descriptions
        for proj in parsed_data.get('projects', []):
            if 'description' in proj:
                text_parts.append(proj['description'])
        
        # Add skills as text
        skills_data = parsed_data.get('skills', {})
        for skill_list in skills_data.values():
            if isinstance(skill_list, list):
                text_parts.extend(skill_list)
        
        return ' '.join(text_parts)


def parse_resume_file(file_path: str, file_type: str) -> Dict:
    """Convenience function to parse a resume file"""
    parser = ResumeParserAgent()
    
    # Extract text from file
    resume_text = parser.extract_text_from_file(file_path, file_type)
    
    if not resume_text.strip():
        logger.error(f"No text extracted from file: {file_path}")
        return parser._create_empty_structure()
    
    # Parse with AI
    parsed_data = parser.parse_resume(resume_text)
    
    # Calculate ATS score
    ats_score, ats_analysis = parser.calculate_ats_score(parsed_data)
    
    # Add analysis to parsed data
    parsed_data['ats_analysis'] = ats_analysis
    parsed_data['raw_text'] = resume_text[:1000]
    
    return parsed_data
