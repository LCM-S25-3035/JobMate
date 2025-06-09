# ghost_job_detector_ui.py

import streamlit as st
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from ghost_job_detector import detect_ghost_jobs

def load_jobs():
    load_dotenv()
    uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    client = MongoClient(uri)
    db = client["your_db_name"]         # <-- REPLACE with your actual DB name
    collection = db["your_collection"]  # <-- REPLACE with your actual collection name
    return list(collection.find())

def run():
    st.title("👻 Ghost Job Detector")

    if st.button("Run Detector"):
        try:
            jobs = load_jobs()
            if not jobs:
                st.warning("No job records found in the database.")
                return

            results = detect_ghost_jobs(jobs)
            results = sorted(results, key=lambda x: x["score"], reverse=True)

            for job in results:
                st.subheader(f"🔗 {job['url']}")
                st.write(f"🏢 Company: {job['company']}")
                st.write(f"🧪 Ghost Score: {job['score']}")
                st.progress(min(job["score"], 1.0))
                if job["is_ghost"]:
                    st.error("🚨 This is likely a ghost job.")
                else:
                    st.success("✅ This job seems legit.")
                st.markdown("---")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
