#!/usr/bin/env python3
"""
Script to create sample jobs for testing the recruiter module
"""

import os
import sys
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app import create_app
from app.models.user import User
from app.models.job_posting import JobPosting
from app import db

def create_sample_jobs():
    """Create sample jobs for testing"""
    app = create_app()
    
    with app.app_context():
        # Find the recruiter user
        recruiter = User.query.filter_by(email='recruiter@demo.com').first()
        if not recruiter:
            print("❌ Recruiter user not found. Please run create_recruiter_user.py first")
            return
        
        print(f"Creating sample jobs for recruiter: {recruiter.email}")
        
        # Sample jobs data
        jobs_data = [
            {
                'title': 'Senior Full Stack Developer',
                'company': 'TechCorp Inc.',
                'location': 'Toronto, ON',
                'job_type': 'full-time',
                'salary_min': 90000,
                'salary_max': 120000,
                'experience_level': 'senior',
                'remote_allowed': True,
                'description': '''We are looking for a Senior Full Stack Developer to join our growing team. 
                
Key Responsibilities:
• Develop and maintain web applications using React and Node.js
• Design and implement RESTful APIs
• Collaborate with cross-functional teams
• Mentor junior developers

Requirements:
• 5+ years of experience in full stack development
• Proficiency in React, Node.js, and PostgreSQL
• Experience with cloud platforms (AWS/Azure)
• Strong problem-solving skills''',
                'requirements': 'React, Node.js, PostgreSQL, AWS, 5+ years experience',
                'benefits': 'Health insurance, dental, vision, 401k matching, flexible hours, remote work options'
            },
            {
                'title': 'Data Scientist',
                'company': 'Analytics Solutions Ltd.',
                'location': 'Ottawa, ON',
                'job_type': 'full-time',
                'salary_min': 85000,
                'salary_max': 110000,
                'experience_level': 'mid',
                'remote_allowed': True,
                'description': '''Join our data science team to build machine learning models and extract insights from large datasets.

Key Responsibilities:
• Develop predictive models using Python and R
• Analyze large datasets to identify trends and patterns
• Create data visualizations and reports
• Collaborate with business stakeholders

Requirements:
• Master's degree in Data Science, Statistics, or related field
• 3+ years of experience in data science
• Proficiency in Python, R, SQL
• Experience with machine learning frameworks''',
                'requirements': 'Python, R, SQL, Machine Learning, Statistics, 3+ years experience',
                'benefits': 'Competitive salary, health benefits, professional development budget, remote work'
            },
            {
                'title': 'Frontend Developer',
                'company': 'StartupXYZ',
                'location': 'Waterloo, ON',
                'job_type': 'full-time',
                'salary_min': 70000,
                'salary_max': 90000,
                'experience_level': 'junior',
                'remote_allowed': False,
                'description': '''We're seeking a talented Frontend Developer to create beautiful, responsive web applications.

Key Responsibilities:
• Build user interfaces using React and TypeScript
• Implement responsive designs
• Optimize applications for performance
• Work closely with designers and backend developers

Requirements:
• Bachelor's degree in Computer Science or related field
• 2+ years of experience with React
• Strong knowledge of HTML, CSS, JavaScript
• Experience with modern development tools''',
                'requirements': 'React, TypeScript, HTML, CSS, JavaScript, 2+ years experience',
                'benefits': 'Startup equity, health benefits, flexible schedule, learning opportunities'
            },
            {
                'title': 'DevOps Engineer',
                'company': 'CloudTech Solutions',
                'location': 'Mississauga, ON',
                'job_type': 'contract',
                'salary_min': 95000,
                'salary_max': 125000,
                'experience_level': 'senior',
                'remote_allowed': True,
                'description': '''Looking for an experienced DevOps Engineer to help scale our infrastructure and improve deployment processes.

Key Responsibilities:
• Design and maintain CI/CD pipelines
• Manage cloud infrastructure on AWS
• Implement monitoring and logging solutions
• Automate deployment processes

Requirements:
• 4+ years of DevOps experience
• Strong knowledge of AWS services
• Experience with Docker, Kubernetes
• Proficiency in Infrastructure as Code (Terraform)''',
                'requirements': 'AWS, Docker, Kubernetes, Terraform, CI/CD, 4+ years experience',
                'benefits': 'Competitive contract rate, remote work, cutting-edge technology'
            },
            {
                'title': 'UX/UI Designer',
                'company': 'Design Studio Pro',
                'location': 'Toronto, ON',
                'job_type': 'part-time',
                'salary_min': 45000,
                'salary_max': 65000,
                'experience_level': 'mid',
                'remote_allowed': True,
                'description': '''Join our creative team to design intuitive and beautiful user experiences for web and mobile applications.

Key Responsibilities:
• Create user-centered designs through research and testing
• Develop wireframes, prototypes, and high-fidelity mockups
• Collaborate with development teams
• Conduct usability testing

Requirements:
• 3+ years of UX/UI design experience
• Proficiency in Figma, Sketch, Adobe Creative Suite
• Strong portfolio demonstrating design thinking
• Knowledge of front-end development basics''',
                'requirements': 'Figma, Sketch, Adobe Creative Suite, UX Research, 3+ years experience',
                'benefits': 'Flexible hours, creative environment, professional development, portfolio projects'
            }
        ]
        
        created_jobs = []
        
        for job_data in jobs_data:
            # Check if job already exists
            existing_job = JobPosting.query.filter_by(
                title=job_data['title'], 
                recruiter_id=recruiter.id
            ).first()
            
            if existing_job:
                print(f"✅ Job already exists: {job_data['title']}")
                continue
            
            # Map job type
            employment_type_map = {
                'full-time': 'full_time',
                'part-time': 'part_time',
                'contract': 'contract'
            }
            employment_type = employment_type_map.get(job_data['job_type'], 'full_time')
            
            # Map remote type
            remote_type = 'remote' if job_data['remote_allowed'] else 'onsite'
            
            # Create new job
            job = JobPosting(
                title=job_data['title'],
                company_name=job_data['company'],
                location=job_data['location'],
                employment_type=employment_type,
                salary_min=job_data['salary_min'],
                salary_max=job_data['salary_max'],
                experience_level=job_data['experience_level'],
                remote_type=remote_type,
                description=job_data['description'],
                requirements=job_data['requirements'],
                benefits=job_data['benefits'],
                recruiter_id=recruiter.id,
                status='active'
            )
            
            db.session.add(job)
            created_jobs.append(job_data['title'])
        
        if created_jobs:
            db.session.commit()
            print(f"✅ Created {len(created_jobs)} sample jobs:")
            for title in created_jobs:
                print(f"   • {title}")
        else:
            print("✅ All sample jobs already exist")

if __name__ == '__main__':
    create_sample_jobs() 