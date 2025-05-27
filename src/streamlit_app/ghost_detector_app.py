# ghost_detector_app.py

import streamlit as st
import json
import pandas as pd
import re
from ghost_job_detector import detect_ghost_jobs
from docx import Document
import fitz  # PyMuPDF

def extract_keywords(text):
    return set(re.findall(r"\b[a-zA-Z]{3,}\b", text.lower()))

def simple_ats_score(resume_text, job_desc):
    resume_keywords = extract_keywords(resume_text)
    job_keywords = extract_keywords(job_desc)
    if not job_keywords:
        return 0
    match_count = len(resume_keywords & job_keywords)
    return round(match_count / len(job_keywords), 2)

def read_resume(uploaded_file):
    if uploaded_file.name.endswith(".txt"):
        return uploaded_file.read().decode("utf-8")
    elif uploaded_file.name.endswith(".docx"):
        doc = Document(uploaded_file)
        return "\n".join(p.text for p in doc.paragraphs)
    elif uploaded_file.name.endswith(".pdf"):
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as pdf:
            return "\n".join(page.get_text() for page in pdf)
    else:
        return ""

st.set_page_config(page_title="Jobmate ATS + Ghost Detection", layout="wide")
st.title("💼 Jobmate - Job Matcher with Ghost Job Detection")

resume = st.file_uploader("📄 Upload your resume (.txt, .docx, .pdf)", type=["txt", "docx", "pdf"])
job_file = st.file_uploader("📄 Upload scraped_jobs.json", type=["json"])

if resume and job_file:
    resume_text = read_resume(resume)
    jobs = json.load(job_file)

    # Handle empty or bad job format
    if not isinstance(jobs, list) or not jobs:
        st.error("❌ The job file must be a JSON array of job listings.")
        st.stop()

    ghost_results = detect_ghost_jobs(jobs)
    ghost_map = {r["url"]: r["is_ghost"] for r in ghost_results}

    enriched = []
    for job in jobs:
        ats_score = simple_ats_score(resume_text, job.get("description", ""))
        enriched.append({
            "title": job.get("title", "N/A"),
            "company": job.get("company", "N/A"),
            "location": job.get("location", "Unknown"),
            "url": job.get("url", "#"),
            "ats_score": ats_score,
            "is_ghost": ghost_map.get(job.get("url", ""), False)
        })

    df = pd.DataFrame(enriched)

    # Ghost job % display
    total_jobs = len(df)
    ghost_jobs = df["is_ghost"].sum()
    ghost_pct = round((ghost_jobs / total_jobs) * 100, 1) if total_jobs > 0 else 0.0
    st.metric(label="🚨 % of Potential Ghost Jobs", value=f"{ghost_pct}%")

    # Sort by ATS score
    df = df.sort_values(by="ats_score", ascending=False)

    st.subheader("🎯 Matched Job Listings")

    for _, row in df.iterrows():
        bg_color = "#f8d7da" if row["is_ghost"] else "#d4edda"
        text_color = "#721c24" if row["is_ghost"] else "#155724"

        st.markdown(
            f"""
            <div style="background-color:{bg_color}; padding:14px; margin-bottom:10px; border-radius:6px;
                        color:{text_color}; font-family:sans-serif">
                <div style="font-size:18px;"><strong>{row['title']}</strong> at <strong>{row['company']}</strong> — {row['location']}</div>
                <div style="margin-top:4px;">🔗 <a href="{row['url']}" target="_blank">{row['url']}</a></div>
                <div style="margin-top:4px;">🧠 <strong>ATS Score:</strong> {row['ats_score']*100:.1f}%</div>
                <div style="margin-top:4px;">{'🚨 <strong>Possible Ghost Listing</strong>' if row['is_ghost'] else '✅ Legit Job'}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Results", data=csv, file_name="matched_jobs.csv", mime="text/csv")

else:
    st.info("Upload both your resume and job listings to begin.")
