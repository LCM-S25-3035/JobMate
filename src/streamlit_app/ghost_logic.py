import streamlit as st
import json
from ghost_job_detector import detect_ghost_jobs  # this is itself – will explain below

# ✅ Fake sample for demonstration; replace with real job ingestion source
def load_sample_jobs():
    return [
        {
            "url": "http://example.com/ghost-job",
            "title": "Remote Data Entry",
            "description": "Earn money quick from home. No experience needed!",
            "salary": 1000000,
            "company": "",
            "contact_email": "",
            "posted_at": "2025-06-09T00:00:00"
        },
        {
            "url": "http://example.com/real-job",
            "title": "Data Scientist",
            "description": "Work with ML models on a great team.",
            "salary": 85000,
            "company": "OpenAI",
            "contact_email": "hr@openai.com",
            "posted_at": "2025-06-01T00:00:00"
        }
    ]

def run():
    st.title("👻 Ghost Job Detector")
    st.write("Run automated analysis to detect fake or ghost job listings.")

    if st.button("Run Ghost Detection"):
        jobs = load_sample_jobs()
        results = detect_ghost_jobs(jobs)
        st.success(f"Analyzed {len(results)} jobs")
        st.dataframe(results)

        ghost_jobs = [j for j in results if j["is_ghost"]]
        st.markdown(f"### 👻 {len(ghost_jobs)} Ghost Jobs Detected")
        st.json(ghost_jobs)
