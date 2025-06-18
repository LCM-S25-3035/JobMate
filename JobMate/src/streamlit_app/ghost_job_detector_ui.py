import streamlit as st
import pymongo
import os
from datetime import datetime, timedelta

def connect_to_mongo():
    """Connect to MongoDB using env vars"""
    mongo_uri = os.getenv("MONGO_URI") or os.getenv("MONGODB_URI")
    if not mongo_uri:
        st.error("Mongo URI not set in environment variables.")
        st.stop()

    db_name = os.getenv("MONGO_DB", "autoapply")
    collection_name = os.getenv("MONGO_COLLECTION", "resumes")

    client = pymongo.MongoClient(mongo_uri)
    db = client[db_name]
    return db[collection_name]

def fetch_jobs(collection, limit=100):
    """Fetch recent jobs from MongoDB collection"""
    try:
        jobs = list(collection.find().sort("date", -1).limit(limit))
    except Exception as e:
        st.error(f"Error fetching jobs: {e}")
        jobs = []
    return jobs

def detect_ghost_jobs(jobs):
    """Detect suspicious or outdated job postings"""
    ghost_jobs = []
    now = datetime.utcnow()
    for job in jobs:
        reasons = []
        if not job.get("description") or len(job["description"]) < 50:
            reasons.append("Missing or very short description")

        post_date = job.get("date")
        if isinstance(post_date, datetime):
            if post_date < now - timedelta(days=90):
                reasons.append("Posted more than 90 days ago")
        else:
            reasons.append("Missing or invalid posting date")

        if reasons:
            job["ghost_reason"] = reasons
            ghost_jobs.append(job)
    return ghost_jobs

def run():
    st.title("🕵️ Ghost Job Detector (Beta)")
    st.markdown("Detect outdated or low-quality job posts stored in MongoDB.")

    with st.spinner("🔌 Connecting to MongoDB..."):
        try:
            collection = connect_to_mongo()
        except Exception as e:
            st.error(f"MongoDB connection failed: {e}")
            return

    with st.spinner("📥 Fetching job data..."):
        jobs = fetch_jobs(collection)
        ghost_jobs = detect_ghost_jobs(jobs)

    st.success(f"Analyzed {len(jobs)} jobs — found {len(ghost_jobs)} ghost job(s).")

    if not ghost_jobs:
        st.info("🎉 No ghost jobs detected.")
        return

    for job in ghost_jobs:
        with st.expander(f"👻 {job.get('title', 'Unknown Title')}"):
            st.write("**Company:**", job.get("company", "N/A"))
            st.write("**Posted on:**", job.get("date", "Unknown"))
            st.write("**Location:**", job.get("location", "N/A"))
            st.write("**Flagged for:**")
            for reason in job.get("ghost_reason", []):
                st.warning(f"- {reason}")
            st.write("**Job Description:**")
            st.code(job.get("description", "No description available"))