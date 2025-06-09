import os

def get_resume_path():
    while True:
        path = input("Enter the full path to your resume file (.pdf): ").strip()
        if os.path.exists(path) and path.endswith(".pdf"):
            print(f"Using resume: {path}")
            return path
        else:
            print("Invalid path. Please try again.")
