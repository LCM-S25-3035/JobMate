from ask_resume_path import get_resume_path
from launch_chrome_profile import open_job_in_chrome
from get_questions_from_job_post import get_questions

def main():
    job_url = input("Enter full job URL to apply to: ").strip()
    if not job_url.startswith("http"):
        print("Invalid URL. Exiting.")
        return

    resume_path = get_resume_path()
    print(f"\nUsing resume: {resume_path}")

    print(f"Opening job post in browser...")
    open_job_in_chrome(job_url)

    print("\nPlease manually click 'Apply Now' and upload your resume.")
    
    print("Scanning for questions...")
    qs = get_questions(job_url)

    if qs:
        print("\nQuestions found:")
        for q in qs:
            print(" -", q)
    else:
        print("No questions detected.")
 
    input("Press Enter when you're done to finish...")

if __name__ == "__main__":
    main()