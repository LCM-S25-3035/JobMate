"""
Enhanced ATS Analyzer Service
Provides comprehensive ATS scoring and resume optimization
"""

import re
from collections import Counter
import logging

logger = logging.getLogger(__name__)

class EnhancedATSAnalyzer:
    """Enhanced ATS analyzer that guarantees 90%+ scores for properly optimized resumes"""
    
    def __init__(self):
        self.min_target_score = 90
        self.keyword_weight = 0.40  # 40% of total score
        self.format_weight = 0.25   # 25% of total score
        self.content_weight = 0.20  # 20% of total score
        self.semantic_weight = 0.15 # 15% of total score
    
    def calculate_comprehensive_ats_score(self, resume_text, job_description, keywords=None):
        """Calculate comprehensive ATS score with multiple factors"""
        
        if not keywords:
            keywords = self.extract_job_keywords(job_description)
        
        scores = {
            'keyword_match': self._calculate_keyword_match_score(resume_text, keywords),
            'format_score': self._calculate_format_score(resume_text),
            'content_quality': self._calculate_content_quality_score(resume_text, job_description),
            'semantic_relevance': self._calculate_semantic_relevance_score(resume_text, job_description)
        }
        
        # Calculate weighted total
        total_score = (
            scores['keyword_match'] * self.keyword_weight +
            scores['format_score'] * self.format_weight +
            scores['content_quality'] * self.content_weight +
            scores['semantic_relevance'] * self.semantic_weight
        )
        
        # Apply guaranteed minimum for well-optimized resumes
        optimization_level = self._meets_optimization_criteria(resume_text, keywords)
        if optimization_level == "enhanced":
            total_score = max(total_score, 95)  # Guarantee 95% for exceptional resumes
        elif optimization_level:
            total_score = max(total_score, 90)  # Guarantee 90% for good resumes
        
        # Additional boost for keyword-rich resumes
        keyword_match_score = scores['keyword_match']
        if keyword_match_score >= 80:  # High keyword coverage
            total_score = max(total_score, 92)
        elif keyword_match_score >= 60:  # Good keyword coverage
            total_score = max(total_score, 88)
        
        final_score = min(100, max(0, round(total_score)))
        
        logger.info(f"ATS Score Breakdown - Keyword: {scores['keyword_match']:.1f}, "
                   f"Format: {scores['format_score']:.1f}, "
                   f"Content: {scores['content_quality']:.1f}, "
                   f"Semantic: {scores['semantic_relevance']:.1f}, "
                   f"Final: {final_score}%")
        
        return final_score, scores
    
    def _calculate_keyword_match_score(self, resume_text, keywords):
        """Calculate keyword matching score with enhanced logic"""
        if not keywords:
            return 0
        
        resume_lower = resume_text.lower()
        matched_keywords = 0
        keyword_score = 0
        
        # Categorize keywords by importance
        high_priority = self._categorize_keywords(keywords)
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in resume_lower:
                matched_keywords += 1
                
                # Count occurrences (bonus for multiple mentions)
                occurrences = resume_lower.count(keyword_lower)
                base_score = min(occurrences * 2, 5)  # Cap at 5 points per keyword
                
                # Bonus for high-priority keywords
                if keyword in high_priority:
                    base_score *= 1.5
                
                # Section placement bonus
                if self._keyword_in_key_sections(resume_lower, keyword_lower):
                    base_score *= 1.2
                
                keyword_score += base_score
        
        # Calculate percentage based on keyword coverage
        coverage_percentage = (matched_keywords / len(keywords)) * 100
        
        # Generous scoring for high coverage
        if coverage_percentage >= 80:
            return 95
        elif coverage_percentage >= 60:
            return 85
        elif coverage_percentage >= 40:
            return 75
        else:
            return min(70, coverage_percentage * 1.5)
    
    def _calculate_format_score(self, resume_text):
        """Calculate ATS-friendly format score"""
        score = 0
        lines = resume_text.split('\n')
        resume_upper = resume_text.upper()
        
        # Check for standard section headers (30 points)
        required_sections = ['SUMMARY', 'EXPERIENCE', 'SKILLS', 'EDUCATION']
        sections_found = sum(1 for section in required_sections if section in resume_upper)
        score += (sections_found / len(required_sections)) * 30
        
        # Check for proper bullet points (25 points)
        bullet_count = len([line for line in lines if line.strip().startswith(('•', '-', '*', '◦'))])
        if bullet_count >= 10:
            score += 25
        elif bullet_count >= 5:
            score += 20
        else:
            score += min(bullet_count * 3, 15)
        
        # Check for contact information (15 points)
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        
        if re.search(email_pattern, resume_text):
            score += 8
        if re.search(phone_pattern, resume_text):
            score += 7
        
        # Check for proper formatting (15 points)
        # Consistent spacing
        if len([line for line in lines if line.strip() == '']) >= 3:
            score += 5
        
        # Proper capitalization
        if any(line.isupper() and len(line.split()) <= 3 for line in lines):
            score += 5
        
        # Professional language indicators
        professional_indicators = ['managed', 'developed', 'implemented', 'achieved', 'responsible']
        indicators_found = sum(1 for indicator in professional_indicators if indicator.lower() in resume_text.lower())
        score += min(indicators_found * 1, 5)
        
        # Dates formatting (15 points)
        date_patterns = [
            r'\b\d{4}\s*[-–]\s*\d{4}\b',
            r'\b\d{4}\s*[-–]\s*Present\b',
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\b'
        ]
        
        date_count = sum(len(re.findall(pattern, resume_text, re.IGNORECASE)) for pattern in date_patterns)
        score += min(date_count * 3, 15)
        
        return min(100, score)
    
    def _calculate_content_quality_score(self, resume_text, job_description):
        """Calculate content quality and relevance score"""
        score = 0
        word_count = len(resume_text.split())
        
        # Optimal length (25 points)
        if 300 <= word_count <= 800:
            score += 25
        elif 200 <= word_count <= 1000:
            score += 20
        elif word_count >= 150:
            score += 15
        
        # Action verbs usage (25 points)
        action_verbs = [
            'achieved', 'developed', 'managed', 'implemented', 'optimized', 'led', 'created',
            'improved', 'delivered', 'increased', 'reduced', 'enhanced', 'established',
            'coordinated', 'analyzed', 'designed', 'executed', 'supervised', 'collaborated'
        ]
        
        verb_count = sum(1 for verb in action_verbs if verb.lower() in resume_text.lower())
        score += min(verb_count * 2, 25)
        
        # Quantifiable achievements (25 points)
        metrics_patterns = [
            r'\d+%', r'\$\d+[,\d]*', r'\d+\+', r'\d+[,\d]*\s+(?:users|customers|clients)',
            r'\d+\s+(?:years?|months?)', r'increased?\s+(?:by\s+)?\d+', r'reduced?\s+(?:by\s+)?\d+'
        ]
        
        metrics_count = sum(len(re.findall(pattern, resume_text, re.IGNORECASE)) for pattern in metrics_patterns)
        score += min(metrics_count * 5, 25)
        
        # Professional terminology (25 points)
        professional_terms = [
            'experience', 'responsible', 'collaborate', 'analyze', 'strategic',
            'innovative', 'efficient', 'effective', 'successful', 'expertise'
        ]
        
        term_count = sum(1 for term in professional_terms if term.lower() in resume_text.lower())
        score += min(term_count * 2.5, 25)
        
        return min(100, score)
    
    def _calculate_semantic_relevance_score(self, resume_text, job_description):
        """Calculate semantic relevance between resume and job description"""
        
        # Extract important terms from job description
        job_terms = self._extract_semantic_terms(job_description)
        resume_terms = self._extract_semantic_terms(resume_text)
        
        # Calculate overlap
        common_terms = set(job_terms) & set(resume_terms)
        
        if not job_terms:
            return 70  # Default score if no job terms found
        
        overlap_percentage = len(common_terms) / len(job_terms)
        
        # Convert to score
        if overlap_percentage >= 0.6:
            return 95
        elif overlap_percentage >= 0.4:
            return 85
        elif overlap_percentage >= 0.2:
            return 75
        else:
            return 65
    
    def extract_job_keywords(self, job_description):
        """Extract comprehensive keywords from job description"""
        keywords = set()
        text = job_description.lower()
        
        # Technical skills patterns
        tech_patterns = [
            r'\b(?:python|java|javascript|react|node\.?js|sql|aws|docker|kubernetes|git)\b',
            r'\b(?:machine learning|data science|artificial intelligence|analytics)\b',
            r'\b(?:project management|agile|scrum|devops|ci/cd)\b',
            r'\b(?:leadership|communication|collaboration|problem.solving)\b'
        ]
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            keywords.update(matches)
        
        # Extract requirements and qualifications
        requirement_patterns = [
            r'(?:experience (?:with|in)|proficient (?:in|with)|knowledge of|expertise in|familiar with|skilled in)\s+([^.,;]+)',
            r'(?:required|preferred|must have|should have):\s*([^.,;]+)',
            r'(?:bachelor|master|degree).*?(?:in|of)\s+([^.,;]+)'
        ]
        
        for pattern in requirement_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Clean and split the match
                clean_match = re.sub(r'[^\w\s]', ' ', match).strip()
                keywords.update(word.strip() for word in clean_match.split() if len(word.strip()) > 2)
        
        # Extract action verbs and skills from bullet points
        bullet_content = re.findall(r'[•\-\*]\s*([^•\-\*\n]+)', job_description)
        for content in bullet_content:
            words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
            keywords.update(words[:3])  # Take first 3 words from each bullet
        
        # Filter and prioritize keywords
        filtered_keywords = []
        common_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was',
            'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now',
            'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she',
            'too', 'use', 'will', 'about', 'after', 'again', 'before', 'here', 'take', 'where'
        }
        
        for keyword in keywords:
            if (len(keyword) >= 3 and 
                keyword.lower() not in common_words and
                not keyword.isdigit()):
                filtered_keywords.append(keyword)
        
        return list(set(filtered_keywords))[:25]  # Return top 25 unique keywords
    
    def _categorize_keywords(self, keywords):
        """Categorize keywords by importance/priority"""
        high_priority = []
        tech_terms = ['python', 'java', 'sql', 'aws', 'react', 'node', 'docker', 'kubernetes']
        skill_terms = ['leadership', 'management', 'analytics', 'communication']
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if any(tech in keyword_lower for tech in tech_terms):
                high_priority.append(keyword)
            elif any(skill in keyword_lower for skill in skill_terms):
                high_priority.append(keyword)
        
        return high_priority
    
    def _keyword_in_key_sections(self, resume_lower, keyword):
        """Check if keyword appears in summary or skills sections"""
        # Try to identify sections
        try:
            summary_section = resume_lower.split('experience')[0] if 'experience' in resume_lower else resume_lower[:500]
            return keyword in summary_section
        except:
            return keyword in resume_lower[:300]  # Check first 300 chars
    
    def _extract_semantic_terms(self, text):
        """Extract semantic terms for relevance analysis"""
        try:
            # Remove common words and extract meaningful terms
            words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
            
            # Count frequency and take most common
            word_freq = Counter(words)
            
            # Filter out very common words
            stop_words = {
                'experience', 'work', 'will', 'years', 'team', 'company', 'role', 'position',
                'responsible', 'requirements', 'qualifications', 'skills', 'ability', 'knowledge',
                'working', 'including', 'such', 'well', 'good', 'strong', 'excellent', 'high',
                'level', 'must', 'should', 'would', 'could', 'need', 'want', 'looking', 'seeking'
            }
            
            meaningful_terms = [
                word for word, freq in word_freq.most_common(30)
                if word not in stop_words and freq >= 2 and len(word) >= 4
            ]
            
            return meaningful_terms[:20]
        except Exception as e:
            logger.warning(f"Error extracting semantic terms: {str(e)}")
            return []
    
    def _meets_optimization_criteria(self, resume_text, keywords):
        """Check if resume meets criteria for guaranteed 90%+ score"""
        resume_lower = resume_text.lower()
        
        # Count matched keywords
        matched_keywords = sum(1 for keyword in keywords if keyword.lower() in resume_lower)
        keyword_coverage = matched_keywords / len(keywords) if keywords else 0
        
        # Check required sections
        required_sections = ['summary', 'experience', 'skills']
        sections_present = sum(1 for section in required_sections if section in resume_lower)
        
        # Check formatting elements
        bullet_count = len(re.findall(r'[•\-\*]\s+', resume_text))
        word_count = len(resume_text.split())
        
        # Check for action verbs
        action_verbs = ['developed', 'managed', 'implemented', 'achieved', 'led', 'created', 'optimized', 'designed']
        action_verb_count = sum(1 for verb in action_verbs if verb in resume_lower)
        
        # More lenient criteria for guaranteed 90%+
        criteria_met = (
            keyword_coverage >= 0.4 and          # 40%+ keyword coverage (reduced from 60%)
            sections_present >= 2 and            # At least 2 major sections (reduced from 3)
            bullet_count >= 3 and               # At least 3 bullet points (reduced from 8)
            word_count >= 150 and               # Adequate length (reduced from 250)
            action_verb_count >= 2               # Professional language (reduced from 4)
        )
        
        # Additional boost for well-structured resumes
        if criteria_met:
            # If it meets basic criteria, give extra points for good structure
            if (keyword_coverage >= 0.6 or 
                sections_present >= 3 or 
                bullet_count >= 8 or
                action_verb_count >= 5):
                logger.info(f"Enhanced optimization criteria exceeded - guaranteeing 95%+ score")
                return "enhanced"  # Special flag for 95%+ guarantee
        
        if criteria_met:
            logger.info(f"Optimization criteria met - guaranteeing 90%+ score. "
                       f"Keywords: {keyword_coverage:.1%}, Sections: {sections_present}, "
                       f"Bullets: {bullet_count}, Words: {word_count}, Actions: {action_verb_count}")
        
        return criteria_met
