import os
from dotenv import load_dotenv
from jobspy import scrape_jobs
import pandas as pd
from pymongo import MongoClient
import datetime

def convert_dates(record):
    for key, value in record.items():
        if isinstance(value, datetime.date) and not isinstance(value, datetime.datetime):
            # Convert date to datetime at midnight
            record[key] = datetime.datetime.combine(value, datetime.time.min)
    return record

def main():
    # Load environment variables from .env file
    load_dotenv()

    # Read MongoDB connection details from environment variables
    mongo_uri = os.getenv("MONGODB_URI")
    mongo_db = os.getenv("MONGO_DB")
    mongo_collection = os.getenv("MONGO_COLLECTION")

    if not all([mongo_uri, mongo_db, mongo_collection]):
        raise ValueError("MongoDB environment variables (MONGODB_URI, MONGO_DB, MONGO_COLLECTION) must be set in .env")

    # Establish connection to MongoDB
    client = MongoClient(mongo_uri)
    db = client[mongo_db]
    collection = db[mongo_collection]

    # Define job search parameters
    job_titles = ["Data Scientist", "Data Analyst"]
    locations = ["usa", "canada"]
    job_types = ["fulltime", "parttime"]

    all_jobs = []

    # Scrape jobs from Indeed and LinkedIn
    for title in job_titles:
        for location in locations:
            for jt in job_types:
                try:
                    jobs = scrape_jobs(
                        site_name=["indeed", "linkedin"],
                        search_term=title,
                        location=location,
                        results_wanted=100,
                        job_type=jt
                    )
                    print(f"Fetched {len(jobs)} jobs for '{title}' in {location} ({jt})")
                    if not jobs.empty:
                        all_jobs.append(jobs)
                except Exception as e:
                    print(f"Error scraping '{title}' in {location} ({jt}): {e}")

    # Exit if no jobs were scraped
    if not all_jobs:
        print("No jobs scraped. Exiting.")
        return

    # Combine all scraped job DataFrames into one
    df = pd.concat(all_jobs, ignore_index=True)

    # Drop duplicate jobs if 'id' column exists, else drop full duplicates
    if 'id' in df.columns:
        df.drop_duplicates(subset=["id", "title", "company"], inplace=True)
    else:
        df.drop_duplicates(inplace=True)

    # Convert DataFrame to list of dictionaries for MongoDB insertion
    job_dicts = df.to_dict(orient="records")

    # Convert any datetime.date to datetime.datetime for MongoDB compatibility
    job_dicts = [convert_dates(job) for job in job_dicts]

    # Clear existing jobs in the collection to avoid duplication
    collection.delete_many({})
    print(f"Deleted existing jobs in collection '{mongo_collection}'.")

    # Insert scraped jobs into MongoDB
    if job_dicts:
        collection.insert_many(job_dicts)
        print(f"Inserted {len(job_dicts)} new job postings into MongoDB collection '{mongo_collection}'.")
    else:
        print("No job postings to insert.")

if __name__ == "__main__":
    main()