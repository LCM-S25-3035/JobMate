#!/usr/bin/env python3
"""
Test script for Resume Parser Agent
Tests the AI-powered resume parsing functionality
"""

import os
import sys
from flask import Flask
from app import create_app
from app.ai_agents.resume_parser import ResumeParserAgent

def create_test_resume():
    """Create a sample resume text for testing"""
    return """
John Doe
Software Developer
Email: john.doe@email.com
Phone: (555) 123-4567
Location: Toronto, ON

PROFESSIONAL SUMMARY
Experienced software developer with 5 years of experience in full-stack development.
Passionate about building scalable web applications using modern technologies.

TECHNICAL SKILLS
- Programming Languages: Python, JavaScript, Java, TypeScript
- Frameworks: React, Node.js, Django, Flask, Express.js
- Databases: PostgreSQL, MongoDB, Redis
- Tools: Git, Docker, Kubernetes, AWS
- Methodologies: Agile, Scrum, DevOps, CI/CD

WORK EXPERIENCE

Senior Software Developer | Tech Solutions Inc. | Toronto, ON | 2021 - Present
- Developed and maintained web applications serving 100,000+ users
- Led a team of 3 junior developers in implementing new features
- Improved application performance by 40% through code optimization
- Technologies: React, Node.js, PostgreSQL, Docker

Software Developer | StartupXYZ | Toronto, ON | 2019 - 2021
- Built responsive web applications using React and Python
- Implemented RESTful APIs and microservices architecture
- Worked in an Agile environment with 2-week sprints
- Technologies: Python, Django, React, PostgreSQL

EDUCATION

Bachelor of Computer Science | University of Toronto | Toronto, ON | 2019
- Relevant Coursework: Data Structures, Algorithms, Database Systems
- GPA: 3.7/4.0

CERTIFICATIONS
- AWS Certified Developer Associate | Amazon Web Services | 2022
- Certified Scrum Master | Scrum Alliance | 2021

PROJECTS

Personal Finance Tracker | 2023
- Built a full-stack web application for tracking personal expenses
- Technologies: React, Node.js, MongoDB, Express.js
- Features: Dashboard, expense categorization, budget planning

E-commerce Platform | 2022
- Developed a complete e-commerce solution with payment integration
- Technologies: Django, PostgreSQL, Stripe API
- Features: Product catalog, shopping cart, order management
"""

def test_resume_parser():
    """Test the Resume Parser Agent functionality"""
    
    print("🚀 Testing Resume Parser Agent...")
    print("=" * 50)
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        try:
            # Initialize parser
            parser = ResumeParserAgent()
            print("✅ Parser initialized successfully")
            
            # Test with sample resume
            sample_resume = create_test_resume()
            print("✅ Sample resume created")
            
            # Parse the resume
            print("\n📄 Parsing resume with AI...")
            parsed_data = parser.parse_resume(sample_resume)
            
            # Display results
            print("\n📊 PARSING RESULTS:")
            print("-" * 30)
            
            # Personal Info
            if parsed_data.get('personal_info'):
                print("\n👤 PERSONAL INFO:")
                personal = parsed_data['personal_info']
                for key, value in personal.items():
                    if value:
                        print(f"  {key}: {value}")
            
            # Skills
            if parsed_data.get('skills'):
                print("\n🛠️  SKILLS:")
                skills = parsed_data['skills']
                for category, skill_list in skills.items():
                    if skill_list:
                        print(f"  {category}: {', '.join(skill_list[:5])}{'...' if len(skill_list) > 5 else ''}")
            
            # Experience
            if parsed_data.get('experience'):
                print(f"\n💼 EXPERIENCE ({len(parsed_data['experience'])} positions):")
                for i, exp in enumerate(parsed_data['experience'][:3], 1):
                    print(f"  {i}. {exp.get('job_title', 'N/A')} at {exp.get('company', 'N/A')}")
                    if exp.get('start_date'):
                        print(f"     Duration: {exp.get('start_date')} - {exp.get('end_date', 'Present')}")
            
            # Education
            if parsed_data.get('education'):
                print(f"\n🎓 EDUCATION ({len(parsed_data['education'])} entries):")
                for edu in parsed_data['education']:
                    print(f"  • {edu.get('degree', 'N/A')} - {edu.get('institution', 'N/A')}")
            
            # Analysis
            if parsed_data.get('analysis'):
                print("\n🔍 AI ANALYSIS:")
                analysis = parsed_data['analysis']
                print(f"  Experience Years: {analysis.get('total_experience_years', 0)}")
                print(f"  Career Level: {analysis.get('career_level', 'N/A')}")
                print(f"  Primary Field: {analysis.get('primary_field', 'N/A')}")
                
                if analysis.get('key_strengths'):
                    print(f"  Key Strengths: {', '.join(analysis['key_strengths'][:3])}")
            
            # Test ATS scoring
            print("\n📈 Testing ATS Scoring...")
            ats_score, ats_analysis = parser.calculate_ats_score(parsed_data)
            
            print(f"\n🎯 ATS COMPATIBILITY SCORE: {ats_score:.1f}%")
            
            if ats_analysis.get('strengths'):
                print("\n💪 STRENGTHS:")
                for strength in ats_analysis['strengths'][:3]:
                    print(f"  ✅ {strength}")
            
            if ats_analysis.get('recommendations'):
                print("\n💡 RECOMMENDATIONS:")
                for rec in ats_analysis['recommendations'][:3]:
                    print(f"  🔹 {rec}")
            
            print("\n" + "=" * 50)
            print("✅ Resume Parser Agent test completed successfully!")
            
            # Test with job keywords
            job_keywords = ['python', 'react', 'postgresql', 'aws', 'docker']
            keyword_score, keyword_analysis = parser.calculate_ats_score(parsed_data, job_keywords)
            print(f"\n🎯 JOB MATCH SCORE (with keywords): {keyword_score:.1f}%")
            
        except Exception as e:
            print(f"\n❌ Error during testing: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

def test_fallback_parsing():
    """Test fallback parsing when Gemini is not available"""
    
    print("\n🔧 Testing Fallback Parser...")
    
    app = create_app()
    
    with app.app_context():
        try:
            parser = ResumeParserAgent()
            
            # Force fallback by setting model to None
            parser.model = None
            
            sample_resume = create_test_resume()
            parsed_data = parser.parse_resume(sample_resume)
            
            print("✅ Fallback parsing successful")
            print(f"📧 Email extracted: {parsed_data['personal_info']['email']}")
            print(f"🛠️  Skills found: {len(parsed_data['skills']['technical_skills'])}")
            
        except Exception as e:
            print(f"❌ Fallback test failed: {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("🧪 JobMate Resume Parser Agent Test Suite")
    print("=========================================\n")
    
    # Test main functionality
    if test_resume_parser():
        print("\n🎉 Main parser test: PASSED")
    else:
        print("\n💥 Main parser test: FAILED")
        sys.exit(1)
    
    # Test fallback
    if test_fallback_parsing():
        print("🎉 Fallback parser test: PASSED")
    else:
        print("💥 Fallback parser test: FAILED")
    
    print("\n✨ All tests completed!")
    print("\nNext steps:")
    print("1. Set your GEMINI_API_KEY in .env file")
    print("2. Upload a resume through the web interface")
    print("3. Check the AI analysis results") 