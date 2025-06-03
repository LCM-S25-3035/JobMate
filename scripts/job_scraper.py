import os
from jobspy import scrape_jobs
import pandas as pd

job_titles = ["Data Scientist", "Data Analyst"]
locations = ["usa", "canada"]
job_types = ["fulltime", "parttime"]

all_jobs = []

for title in job_titles:
    for location in locations:
        for jt in job_types:
            try:
                jobs = scrape_jobs(
                    site_name=["indeed", "linkedin"],
                    search_term=title,
                    location=location,
                    results_wanted=5,
                    job_type=jt
                )
                print(f"Fetched {len(jobs)} jobs for '{title}' in {location} ({jt})")
                if not jobs.empty:
                    print(f"Sample job keys: {list(jobs.columns)}")
                    all_jobs.append(jobs)
            except Exception as e:
                print(f"Failed scraping '{title}' in {location} ({jt}): {e}")

if all_jobs:
    df = pd.concat(all_jobs, ignore_index=True)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "raw_jobs_data.csv")
    df.to_csv(csv_path, index=False)
    print(f"\nSaved {len(df)} jobs to '{csv_path}'")
else:
    print("No jobs scraped. CSV file will not be created.")