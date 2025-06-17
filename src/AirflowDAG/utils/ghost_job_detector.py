from pymongo import MongoClient
import os

def detect_ghost_jobs():
    mongo_uri = os.environ.get("MONGO_URI")
    db_name = os.environ.get("MONGODB_DB", "job_automation")
    collection_name = os.environ.get("MONGODB_COLLECTION", "jobs")

    if not mongo_uri:
        raise ValueError("MONGO_URI not set")

    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    ghost_jobs = collection.find({"description": {"$regex": ".*ghost.*", "$options": "i"}})

    count = 0
    for job in ghost_jobs:
        count += 1
        print(f"[GHOST JOB DETECTED] ID: {job.get('_id')} | Title: {job.get('title')}")

    print(f"[SUMMARY] Total ghost jobs found: {count}")