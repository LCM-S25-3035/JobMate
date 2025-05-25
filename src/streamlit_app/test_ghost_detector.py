import json
from ghost_job_detector import detect_ghost_jobs

# Load your test job listings
with open("scraped_jobs.json", "r") as f:
    jobs = json.load(f)

# Run detection
results = detect_ghost_jobs(jobs)

# Print output for each job
for data in results:
    print(f"{data['url']} → Ghost: {data['is_ghost']}, Score: {data['score']}, Company: {data['company']}")

