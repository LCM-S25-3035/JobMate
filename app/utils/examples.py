"""
Examples of using utility functions
"""

from app.utils.job_description_utils import extract_job_positions

def example_job_position_extraction():
    """Example of how to use the job position extraction function"""
    
    # Sample job description
    job_description = """
    Job Title: Senior Software Engineer (Python/Flask)
    
    XYZ Tech Company is looking for a Full Stack Developer with experience in 
    building web applications. The ideal candidate will have 3+ years of experience
    in Python and JavaScript.
    
    Position: Software Developer
    
    Responsibilities:
    - Develop and maintain web applications
    - Collaborate with cross-functional teams
    - Write clean, maintainable code
    
    We are hiring a Data Scientist with experience in machine learning and 
    data analysis. This role is perfect for someone passionate about AI.
    
    The successful DevOps Engineer will be responsible for infrastructure management
    and deployment automation.
    """
    
    # Simple pattern-based extraction
    print("=== Pattern-based extraction ===")
    positions = extract_job_positions(job_description, use_ai=False)
    for pos in positions:
        print(f"{pos['title']} (Confidence: {pos['confidence']}%, Method: {pos['method']})")
    
    # AI-assisted extraction
    print("\n=== AI-assisted extraction ===")
    positions = extract_job_positions(job_description, use_ai=True)
    for pos in positions:
        print(f"{pos['title']} (Confidence: {pos['confidence']}%, Method: {pos['method']})")
    
    return positions

if __name__ == "__main__":
    example_job_position_extraction()
