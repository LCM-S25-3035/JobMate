# fetch_jobs_from_mongo.py

import json
from pymongo import MongoClient

def fetch_latest_jobs(
    uri="mongodb://airflow:airflow@localhost:27017/?authSource=admin",
    db_name="jobmate",
    collection="jobs",
    out_file="../scraped_jobs.json"
):
    try:
        client = MongoClient(uri)
        db = client[db_name]
        jobs = list(db[collection].find({}, {"_id": 0}))

        if not jobs:
            print("⚠️ No jobs found in collection.")
            return

        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)

        print(f"✅ Exported {len(jobs)} job(s) to {out_file}")
    except Exception as e:
        print(f"❌ Failed to fetch jobs: {e}")

if __name__ == "__main__":
    fetch_latest_jobs()
