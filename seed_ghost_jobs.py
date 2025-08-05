"""
Seed MongoDB with sample jobs that have ghost job scores
"""

from pymongo import MongoClient
import random
from datetime import datetime, timedelta
import os

# Connect to MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/jobmate")
client = MongoClient(MONGO_URI)
db = client.get_database()

# Sample company names
companies = [
    "TechNova Systems", "Digital Frontier", "Quantum Solutions", 
    "Horizon Innovations", "Nexus Technologies", "Apex Data Systems",
    "Vertex AI", "Fusion Technologies", "Stellar Computing", "CodeForge"
]

# Sample job titles
job_titles = [
    "Senior Software Engineer", "Full Stack Developer", "DevOps Engineer",
    "Data Scientist", "UI/UX Designer", "Product Manager", "Cloud Architect",
    "Machine Learning Engineer", "QA Automation Engineer", "Python Developer"
]

# Sample locations
locations = [
    "Toronto, ON", "Vancouver, BC", "Montreal, QC", "Calgary, AB",
    "Ottawa, ON", "Edmonton, AB", "Winnipeg, MB", "Remote"
]

# Sample job types
job_types = ["Full-time", "Part-time", "Contract", "Freelance", "Internship"]

# Sample skill sets
skills_pool = [
    "Python", "JavaScript", "React", "Node.js", "AWS", "Docker", "Kubernetes",
    "MongoDB", "SQL", "NoSQL", "Machine Learning", "CI/CD", "Git", "Agile",
    "Scrum", "TDD", "REST API", "GraphQL", "TypeScript", "Flask", "Django"
]

# Sample job levels
job_levels = ["Entry Level", "Mid Level", "Senior", "Lead", "Manager", "Director"]

# Ghost job reasons
ghost_job_reasons_pool = [
    "Unusually high number of required skills",
    "Vague job description",
    "No specific salary information provided",
    "Position has been open for an extended period",
    "Unusually wide salary range",
    "Ambiguous work location or arrangement",
    "Too many skills required for entry-level position",
    "Company information is incomplete or vague",
    "No direct application link provided",
    "Multiple repostings of the same position",
    "Unrealistic experience requirements",
    "Job description contains inconsistencies",
    "Uses excessive buzzwords and vague terminology",
    "Unusually high qualifications for stated salary range",
    "Anonymous or unclear employer identity"
]

print("🔄 Creating sample jobs with ghost job scores...")

# Clear existing jobs
jobs_collection = db.jobs
jobs_collection.delete_many({})

# Create sample jobs
jobs_to_create = 20
created_jobs = []

for i in range(jobs_to_create):
    # Generate random ghost job score
    ghost_percentage = random.randint(0, 100)
    
    # Generate reasons based on score
    reasons = []
    if ghost_percentage > 0:
        possible_reasons = [
            "Job has been reposted multiple times",
            "Vague job description",
            "Extremely high requirements for salary range",
            "Position has been open for more than 3 months",
            "Identical to other postings by same company",
            "No direct application link provided",
            "Contains unusual requirements for position",
            "Company is known for collecting resumes"
        ]
        num_reasons = min(3, max(1, ghost_percentage // 25))
        reasons = random.sample(possible_reasons, num_reasons)
    
    # Generate random skills (3-6 skills per job)
    num_skills = random.randint(3, 6)
    skills = random.sample(skills_pool, num_skills)
    
    # Generate random date in last 30 days
    days_ago = random.randint(0, 30)
    date_posted = datetime.now() - timedelta(days=days_ago)
    
    # Create job document
    job = {
        "title": random.choice(job_titles),
        "company": random.choice(companies),
        "location": random.choice(locations),
        "job_type": random.choice(job_types),
        "job_level": random.choice(job_levels),
        "description": f"This is a sample job description for a {random.choice(job_titles)} position at {random.choice(companies)}. We are looking for a skilled professional with experience in {', '.join(skills)}.",
        "min_amount": random.randint(50000, 90000),
        "max_amount": random.randint(100000, 150000),
        "skills": skills,
        "date_posted": date_posted,
        "ghost_job_percentage": ghost_percentage,
        "ghost_score": ghost_percentage / 100.0,
        "ghost_job_confidence": "high" if ghost_percentage >= 70 else "medium" if ghost_percentage >= 40 else "low",
        "ghost_job_category": "suspicious" if ghost_percentage >= 50 else "normal",
        "ghost_job_reasons": "; ".join(reasons) if reasons else None,
        "ghost_job_updated_at": datetime.now()
    }
    
    # Insert job into MongoDB
    result = jobs_collection.insert_one(job)
    created_jobs.append((job["title"], str(result.inserted_id)))
    
    print(f"  ✓ Created: {job['title']} at {job['company']} with ghost score: {ghost_percentage}%")

print(f"✅ Successfully created {len(created_jobs)} sample jobs with ghost job scores")
print("🔍 Now restart the application and check if the indicators appear")
