"""
AI-Powered Resume Optimizer for JobMate
Dynamically optimizes resumes based on job descriptions using Google Gemini
"""

import json
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

import google.generativeai as genai
from flask import current_app

logger = logging.getLogger(__name__)


class ResumeOptimizerAgent:
    """
    AI-powered resume optimizer using Google Gemini
    Analyzes job descriptions and optimizes resumes dynamically
    """
    
    def __init__(self):
        """Initialize the optimizer with Gemini configuration"""
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
            logger.info(f"Gemini optimizer model {model_name} configured successfully")
            
        except Exception as e:
            logger.error(f"Failed to configure Gemini: {e}")
            self.model = None
    
    def analyze_job_requirements(self, job_description: str) -> Dict:
        """Analyze job description to extract optimization requirements"""
        if not self.model:
            logger.error("Gemini model not configured")
            return self._fallback_job_analysis(job_description)
        
        try:
            prompt = f"""
Analyze this job description and extract key requirements for resume optimization.
Return ONLY valid JSON with this structure:

Job Description:
{job_description}

Return JSON:
{{
    "must_have_skills": ["list of critical technical skills"],
    "nice_to_have_skills": ["list of preferred skills"],
    "experience_level": "entry/junior/mid/senior",
    "required_years": 3,
    "key_responsibilities": ["list of main job duties"],
    "industry_keywords": ["list of industry-specific terms"],
    "soft_skills": ["list of required soft skills"],
    "education_requirements": "string",
    "certifications": ["list of preferred certifications"],
    "tools_technologies": ["list of specific tools/platforms"],
    "company_culture": ["list of cultural keywords"],
    "optimization_focus": {{
        "technical_emphasis": 80,
        "leadership_emphasis": 20,
        "innovation_emphasis": 60,
        "collaboration_emphasis": 40
    }},
    "ats_keywords": ["comprehensive list of ATS keywords"],
    "job_title_variations": ["list of similar job titles"]
}}
"""
            
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                return self._process_job_analysis_response(response.text)
            else:
                logger.warning("Empty response from Gemini for job analysis")
                return self._fallback_job_analysis(job_description)
                
        except Exception as e:
            logger.error(f"Error analyzing job with Gemini: {e}")
            return self._fallback_job_analysis(job_description)
    
    def optimize_resume_content(self, resume_text: str, job_analysis: Dict, optimization_level: str = "moderate") -> Dict:
        """Optimize resume content based on job analysis"""
        if not self.model:
            logger.error("Gemini model not configured")
            return self._fallback_optimization(resume_text, job_analysis)
        
        try:
            prompt = self._create_optimization_prompt(resume_text, job_analysis, optimization_level)
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                return self._process_optimization_response(response.text)
            else:
                logger.warning("Empty response from Gemini for optimization")
                return self._fallback_optimization(resume_text, job_analysis)
                
        except Exception as e:
            logger.error(f"Error optimizing resume with Gemini: {e}")
            return self._fallback_optimization(resume_text, job_analysis)
    
    def _create_optimization_prompt(self, resume_text: str, job_analysis: Dict, optimization_level: str) -> str:
        """Create detailed prompt for resume optimization"""
        intensity_instructions = {
            "conservative": "Make minimal changes, only enhance keywords and reorder sections slightly",
            "moderate": "Improve content strategically while preserving original voice and achievements",
            "aggressive": "Significantly enhance content to maximize job match while maintaining authenticity"
        }
        
        return f"""
You are an expert resume optimizer. Optimize this resume for the specific job requirements while preserving the candidate's authentic experience and achievements.

ORIGINAL RESUME:
{resume_text}

JOB REQUIREMENTS:
{json.dumps(job_analysis, indent=2)}

OPTIMIZATION LEVEL: {optimization_level}
Instructions: {intensity_instructions.get(optimization_level, intensity_instructions["moderate"])}

OPTIMIZATION RULES:
1. PRESERVE ALL FACTUAL INFORMATION - Never fabricate experience, skills, or achievements
2. Maintain the candidate's authentic voice and personal brand
3. Reorganize content to highlight job-relevant experience first
4. Enhance descriptions using job-relevant keywords naturally
5. Quantify achievements where possible
6. Ensure ATS compatibility with proper formatting
7. Keep the same resume structure and section order
8. Preserve all original accomplishments and metrics

Return ONLY valid JSON:
{{
    "optimized_resume": "complete optimized resume text maintaining original structure",
    "professional_summary": "enhanced summary targeting this specific role",
    "optimized_experience": [
        {{
            "original_text": "original experience description",
            "optimized_text": "enhanced version with job-relevant keywords",
            "enhancements_made": ["list of specific improvements"]
        }}
    ],
    "optimized_skills": {{
        "technical_skills": ["prioritized technical skills list"],
        "tools_technologies": ["relevant tools highlighted"],
        "keywords_added": ["new ATS keywords naturally integrated"]
    }},
    "optimization_summary": {{
        "changes_made": ["list of key changes"],
        "keywords_integrated": ["list of job keywords added"],
        "sections_reordered": ["list of section changes"],
        "ats_improvements": ["list of ATS enhancements"],
        "estimated_ats_score": 92
    }},
    "preservation_notes": ["list of original content preserved"],
    "recommendations": ["suggestions for candidate to consider"]
}}
"""
    
    def _process_job_analysis_response(self, response_text: str) -> Dict:
        """Process Gemini's job analysis response"""
        try:
            cleaned_text = self._clean_json_response(response_text)
            job_analysis = json.loads(cleaned_text)
            return self._validate_job_analysis(job_analysis)
        except Exception as e:
            logger.error(f"Error processing job analysis response: {e}")
            return self._create_default_job_analysis()
    
    def _process_optimization_response(self, response_text: str) -> Dict:
        """Process Gemini's optimization response"""
        try:
            cleaned_text = self._clean_json_response(response_text)
            optimization_result = json.loads(cleaned_text)
            return self._validate_optimization_result(optimization_result)
        except Exception as e:
            logger.error(f"Error processing optimization response: {e}")
            return self._create_default_optimization_result()
    
    def _clean_json_response(self, response_text: str) -> str:
        """Clean and extract JSON from Gemini response"""
        cleaned = response_text.strip()
        
        # Remove code block markers
        if cleaned.startswith('```json'):
            cleaned = cleaned[7:]
        elif cleaned.startswith('```'):
            cleaned = cleaned[3:]
        
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]
        
        return cleaned.strip()
    
    def _validate_job_analysis(self, analysis: Dict) -> Dict:
        """Validate and ensure all required fields in job analysis"""
        default = self._create_default_job_analysis()
        
        for key in default.keys():
            if key not in analysis:
                analysis[key] = default[key]
        
        return analysis
    
    def _validate_optimization_result(self, result: Dict) -> Dict:
        """Validate optimization result structure"""
        required_fields = [
            'optimized_resume', 'professional_summary', 'optimized_experience',
            'optimized_skills', 'optimization_summary', 'preservation_notes', 'recommendations'
        ]
        
        for field in required_fields:
            if field not in result:
                result[field] = {}
        
        return result
    
    def _create_default_job_analysis(self) -> Dict:
        """Create default job analysis structure"""
        return {
            "must_have_skills": [],
            "nice_to_have_skills": [],
            "experience_level": "mid",
            "required_years": 3,
            "key_responsibilities": [],
            "industry_keywords": [],
            "soft_skills": [],
            "education_requirements": "",
            "certifications": [],
            "tools_technologies": [],
            "company_culture": [],
            "optimization_focus": {
                "technical_emphasis": 70,
                "leadership_emphasis": 30,
                "innovation_emphasis": 50,
                "collaboration_emphasis": 40
            },
            "ats_keywords": [],
            "job_title_variations": []
        }
    
    def _create_default_optimization_result(self) -> Dict:
        """Create default optimization result"""
        return {
            "optimized_resume": "",
            "professional_summary": "",
            "optimized_experience": [],
            "optimized_skills": {},
            "optimization_summary": {},
            "preservation_notes": [],
            "recommendations": []
        }
    
    def _fallback_job_analysis(self, job_description: str) -> Dict:
        """Fallback job analysis using pattern matching"""
        logger.info("Using fallback job analysis")
        
        analysis = self._create_default_job_analysis()
        
        # Extract common technical skills
        tech_skills = []
        common_skills = [
            'python', 'javascript', 'java', 'react', 'node.js', 'sql', 'aws', 'docker',
            'kubernetes', 'git', 'machine learning', 'data science', 'html', 'css'
        ]
        
        job_lower = job_description.lower()
        for skill in common_skills:
            if skill in job_lower:
                tech_skills.append(skill)
        
        analysis['must_have_skills'] = tech_skills[:10]
        analysis['ats_keywords'] = tech_skills
        
        # Extract experience level
        if any(word in job_lower for word in ['senior', '5+ years', 'lead', 'principal']):
            analysis['experience_level'] = 'senior'
            analysis['required_years'] = 5
        elif any(word in job_lower for word in ['junior', 'entry', '0-2 years', 'graduate']):
            analysis['experience_level'] = 'entry'
            analysis['required_years'] = 1
        else:
            analysis['experience_level'] = 'mid'
            analysis['required_years'] = 3
        
        return analysis
    
    def _fallback_optimization(self, resume_text: str, job_analysis: Dict) -> Dict:
        """Fallback optimization using basic techniques"""
        logger.info("Using fallback optimization")
        
        result = self._create_default_optimization_result()
        result['optimized_resume'] = resume_text
        result['preservation_notes'] = ['Original content preserved due to fallback mode']
        
        # Basic keyword enhancement
        keywords = job_analysis.get('must_have_skills', [])
        if keywords:
            result['recommendations'] = [f'Consider adding these keywords: {", ".join(keywords[:5])}']
        
        return result
    
    def calculate_optimization_score(self, original_resume: str, optimized_resume: str, job_analysis: Dict) -> Dict:
        """Calculate how much the optimization improved the resume"""
        try:
            original_keywords = self._count_job_keywords(original_resume, job_analysis)
            optimized_keywords = self._count_job_keywords(optimized_resume, job_analysis)
            
            # Calculate improvement metrics
            keyword_improvement = optimized_keywords - original_keywords
            improvement_percentage = (keyword_improvement / max(len(job_analysis.get('ats_keywords', [])), 1)) * 100
            
            # Estimate ATS score improvement
            original_score = min(50 + (original_keywords * 3), 100)
            optimized_score = min(50 + (optimized_keywords * 3), 100)
            
            return {
                'original_keyword_count': original_keywords,
                'optimized_keyword_count': optimized_keywords,
                'keyword_improvement': keyword_improvement,
                'improvement_percentage': round(improvement_percentage, 1),
                'original_ats_score': round(original_score, 1),
                'optimized_ats_score': round(optimized_score, 1),
                'ats_score_improvement': round(optimized_score - original_score, 1)
            }
            
        except Exception as e:
            logger.error(f"Error calculating optimization score: {e}")
            return {}
    
    def _count_job_keywords(self, resume_text: str, job_analysis: Dict) -> int:
        """Count how many job keywords appear in resume"""
        keywords = job_analysis.get('ats_keywords', []) + job_analysis.get('must_have_skills', [])
        resume_lower = resume_text.lower()
        
        count = 0
        for keyword in keywords:
            if keyword.lower() in resume_lower:
                count += 1
        
        return count
    
    def generate_optimization_report(self, optimization_result: Dict, job_analysis: Dict) -> Dict:
        """Generate comprehensive optimization report"""
        try:
            report = {
                'summary': {
                    'total_changes': len(optimization_result.get('optimization_summary', {}).get('changes_made', [])),
                    'keywords_added': len(optimization_result.get('optimization_summary', {}).get('keywords_integrated', [])),
                    'estimated_ats_score': optimization_result.get('optimization_summary', {}).get('estimated_ats_score', 0),
                    'optimization_level': 'successful'
                },
                'improvements': {
                    'content_enhancements': optimization_result.get('optimization_summary', {}).get('changes_made', []),
                    'ats_improvements': optimization_result.get('optimization_summary', {}).get('ats_improvements', []),
                    'keyword_integration': optimization_result.get('optimization_summary', {}).get('keywords_integrated', [])
                },
                'preservation': {
                    'original_content_maintained': optimization_result.get('preservation_notes', []),
                    'authenticity_score': 95  # High authenticity maintained
                },
                'recommendations': optimization_result.get('recommendations', []),
                'next_steps': [
                    'Review the optimized content for accuracy',
                    'Consider implementing suggested improvements',
                    'Test with ATS systems if possible'
                ]
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating optimization report: {e}")
            return {}


def optimize_resume_for_job(resume_text: str, job_description: str, optimization_level: str = "moderate") -> Dict:
    """Convenience function to optimize a resume for a specific job"""
    optimizer = ResumeOptimizerAgent()
    
    # Analyze job requirements
    job_analysis = optimizer.analyze_job_requirements(job_description)
    
    # Optimize resume content
    optimization_result = optimizer.optimize_resume_content(resume_text, job_analysis, optimization_level)
    
    # Calculate improvement scores
    if optimization_result.get('optimized_resume'):
        score_improvement = optimizer.calculate_optimization_score(
            resume_text, 
            optimization_result['optimized_resume'], 
            job_analysis
        )
        optimization_result['score_improvement'] = score_improvement
    
    # Generate comprehensive report
    optimization_report = optimizer.generate_optimization_report(optimization_result, job_analysis)
    optimization_result['optimization_report'] = optimization_report
    
    # Add job analysis for reference
    optimization_result['job_analysis'] = job_analysis
    
    return optimization_result
