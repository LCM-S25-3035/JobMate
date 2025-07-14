#!/usr/bin/env python3
"""
Script to create sample MongoDB jobs for testing the application
"""

import os
import sys
import random
from datetime import datetime, timedelta
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_mongo_sample_jobs():
    """Create sample jobs in MongoDB for testing"""
    print("Creating sample MongoDB jobs...")
    
    # Connect to MongoDB
    mongo_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/')
    mongo_db_name = os.environ.get('MONGODB_DB', 'job_automation')
    
    client = MongoClient(mongo_uri)
    db = client[mongo_db_name]
    jobs_collection = db.jobs
    
    # Sample company data
    companies = [
        {
            'name': 'TechNova Solutions',
            'website': 'https://www.technovasolutions.com',
            'logo': 'https://logo.clearbit.com/technovasolutions.com'
        },
        {
            'name': 'DataWave Analytics',
            'website': 'https://www.datawaveanalytics.com',
            'logo': 'https://logo.clearbit.com/datawaveanalytics.com'
        },
        {
            'name': 'CloudPeak Systems',
            'website': 'https://www.cloudpeaksystems.com',
            'logo': 'https://logo.clearbit.com/cloudpeaksystems.com'
        },
        {
            'name': 'Quantum Code Labs',
            'website': 'https://www.quantumcodelabs.com',
            'logo': 'https://logo.clearbit.com/quantumcodelabs.com'
        },
        {
            'name': 'Horizon Digital',
            'website': 'https://www.horizondigital.com',
            'logo': 'https://logo.clearbit.com/horizondigital.com'
        }
    ]
    
    # Sample job data
    job_templates = [
        {
            'title': 'Senior Full Stack Developer',
            'description': '''We're looking for a Senior Full Stack Developer to join our growing team. You'll be working on our flagship product, using React, Node.js, and MongoDB. You'll be responsible for designing, developing, and deploying new features and ensuring high-quality code.''',
            'requirements': '''• 5+ years of experience with JavaScript/TypeScript
• Strong experience with React and Node.js
• Experience with MongoDB or similar NoSQL databases
• Knowledge of CI/CD pipelines and testing frameworks
• Experience with cloud platforms (AWS/Azure/GCP)''',
            'salary_min': 110000,
            'salary_max': 150000,
            'experience_level': 'Senior',
            'remote_allowed': True,
            'application_method': 'email',
        },
        {
            'title': 'Data Scientist',
            'description': '''Join our data science team to help us extract insights from our vast datasets. You'll be working with the latest AI/ML technologies to build predictive models and improve our recommendation systems.''',
            'requirements': '''• MS or PhD in Computer Science, Statistics, or related field
• Experience with Python, R, and data visualization tools
• Knowledge of machine learning algorithms and statistical methods
• Experience with big data technologies like Spark
• Strong communication skills''',
            'salary_min': 100000,
            'salary_max': 135000,
            'experience_level': 'Mid-Senior',
            'remote_allowed': True,
            'application_method': 'url',
        },
        {
            'title': 'DevOps Engineer',
            'description': '''We're seeking a DevOps Engineer to help us build and maintain our cloud infrastructure. You'll be responsible for CI/CD pipelines, infrastructure as code, and ensuring high availability of our services.''',
            'requirements': '''• 3+ years of experience in DevOps or SRE roles
• Strong experience with Kubernetes, Docker, and container orchestration
• Experience with infrastructure as code (Terraform, CloudFormation)
• Knowledge of monitoring and logging systems
• Experience with cloud platforms (AWS/Azure/GCP)''',
            'salary_min': 95000,
            'salary_max': 130000,
            'experience_level': 'Mid-Senior',
            'remote_allowed': True,
            'application_method': 'both',
        },
        {
            'title': 'UI/UX Designer',
            'description': '''Join our design team to create beautiful, intuitive user interfaces for our products. You'll be working closely with product managers and developers to ensure a seamless user experience.''',
            'requirements': '''• 3+ years of experience in UI/UX design
• Proficiency in design tools like Figma, Sketch, or Adobe XD
• Understanding of design systems and component libraries
• Experience with user research and usability testing
• Portfolio demonstrating UI/UX projects''',
            'salary_min': 85000,
            'salary_max': 120000,
            'experience_level': 'Mid',
            'remote_allowed': True,
            'application_method': 'email',
        },
        {
            'title': 'Product Manager',
            'description': '''We're looking for a Product Manager to drive the development of our next-generation products. You'll be responsible for defining product strategy, gathering requirements, and working with engineering to deliver features.''',
            'requirements': '''• 4+ years of product management experience
• Strong analytical and problem-solving skills
• Experience with agile methodologies
• Excellent communication and stakeholder management
• Technical background preferred''',
            'salary_min': 100000,
            'salary_max': 140000,
            'experience_level': 'Mid-Senior',
            'remote_allowed': True,
            'application_method': 'url',
        }
    ]
    
    # Locations
    locations = [
        'Toronto, ON', 'Vancouver, BC', 'Montreal, QC', 'Ottawa, ON', 
        'Calgary, AB', 'Edmonton, AB', 'Waterloo, ON', 'Remote'
    ]
    
    # Create jobs
    created_jobs = []
    for template in job_templates:
        for company in companies:
            # Check if similar job already exists
            existing_job = jobs_collection.find_one({
                'title': template['title'],
                'company': company['name']
            })
            
            if existing_job:
                continue
                
            # Generate unique job data
            job_data = {
                'title': template['title'],
                'company': company['name'],
                'company_website': company['website'],
                'logo': company['logo'],
                'description': template['description'],
                'requirements': template['requirements'],
                'location': random.choice(locations),
                'salary_min': template['salary_min'],
                'salary_max': template['salary_max'],
                'experience_level': template['experience_level'],
                'remote_allowed': template['remote_allowed'],
                'posted_date': datetime.now() - timedelta(days=random.randint(1, 14)),
                'expires_date': datetime.now() + timedelta(days=random.randint(14, 30))
            }
            
            # Add application method details using the new field names
            if template['application_method'] == 'email' or template['application_method'] == 'both':
                company_domain = company['website'].split('//')[1].split('.')[0]
                job_data['application_email'] = f"jobs@{company_domain}.com"
                
            if template['application_method'] == 'url' or template['application_method'] == 'both':
                company_domain = company['website'].split('//')[1]
                job_data['job_url_direct'] = f"{company['website']}/careers/{template['title'].lower().replace(' ', '-')}"
                
            # Insert job into MongoDB
            result = jobs_collection.insert_one(job_data)
            created_jobs.append({'id': result.inserted_id, 'title': job_data['title']})
    
    # Print results
    if created_jobs:
        print(f"✅ Created {len(created_jobs)} MongoDB sample jobs:")
        for job in created_jobs:
            print(f"   • {job['title']} (ID: {job['id']})")
    else:
        print("✅ All sample MongoDB jobs already exist")

if __name__ == "__main__":
    create_mongo_sample_jobs()
