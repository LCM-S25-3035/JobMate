# scrape/scrape_linkedin.py

from jobspy import scrape_jobs
import pandas as pd

def scrape_linkedin_data_analyst_toronto():
    print("🔍 Scraping LinkedIn for 'Data Analyst' jobs in Toronto...")
    jobs = scrape_jobs(
        site_name="linkedin",
        search_term="data analyst",
        location="Toronto, Ontario, Canada",
        results_wanted=100,
        linkedin_fetch_description=True
    )
    
    # Save results to CSV
    jobs.to_csv("linkedin_data_analyst_toronto.csv", index=False)
    print(f"✅ Done! {len(jobs)} jobs saved to 'linkedin_data_analyst_toronto.csv'")
    return jobs

if __name__ == "__main__":
    df = scrape_linkedin_data_analyst_toronto()
    print(df.head())
