import streamlit as st
import pandas as pd

# -----------------------------
# Page Setup
# -----------------------------
st.set_page_config(page_title="JobMate - Applicant Dashboard", layout="wide")
st.sidebar.title("Applicant Navigation")
menu = st.sidebar.radio("Go to", [
    "📊 Dashboard",
    "📄 Resume Optimizer",
    "📝 Cover Letter Generator",
    "📈 ATS Scoring",
    "🤖 AutoApply",
    "📌 Application Tracker",
    "⚙️ Profile Settings"
])

# -----------------------------
# Page: Dashboard
# -----------------------------
if menu == "📊 Dashboard":
    st.title("📊 Applicant Dashboard")
    st.subheader("🔍 Recommended Jobs")

    jobs = pd.DataFrame({
        "Job Title": ["Data Analyst", "AI Engineer", "Data Engineer"],
        "Company": ["Company A", "Company B", "Company C"],
        "Match Score": [88, 91, 77],
        "Status": ["Not Applied", "Applied", "Not Applied"]
    })
    st.dataframe(jobs)

    if st.button("Auto-Apply to Matches > 85"):
        st.success("✅ Auto-applied to 2 matching jobs!")

# -----------------------------
# Page: Resume Optimizer
# -----------------------------
elif menu == "📄 Resume Optimizer":
    st.title("📄 Resume Optimizer")
    resume = st.file_uploader("Upload your resume (.pdf or .docx)", type=["pdf", "docx"])
    if resume:
        st.success("Resume uploaded.")
        st.metric("Optimization Score", "76%")
        st.markdown("### Suggestions:")
        st.markdown("- Add keywords: `Python`, `Pandas`, `ETL`")
        st.markdown("- Improve formatting and consistency.")
        st.progress(76)

# -----------------------------
# Page: Cover Letter Generator
# -----------------------------
elif menu == "📝 Cover Letter Generator":
    st.title("📝 Cover Letter Generator")
    job_title = st.text_input("Target Job Title", "Data Analyst")
    company = st.text_input("Company Name", "Company A")

    if st.button("Generate"):
        letter = f"""
Dear Hiring Manager at {company},

I am writing to express my interest in the {job_title} position. With my skills and passion for data, I believe I am an excellent fit for your team.

Sincerely,
[Your Name]
"""
        st.text_area("Generated Cover Letter", letter, height=250)

# -----------------------------
# Page: ATS Scoring
# -----------------------------
elif menu == "📈 ATS Scoring":
    st.title("📈 ATS Score")
    resume_file = st.file_uploader("Upload Resume", key="resume_ats")
    job_desc = st.text_area("Paste Job Description")

    if resume_file and job_desc:
        st.info("Analyzing match between resume and job description...")
        st.metric("ATS Score", "82%")

# -----------------------------
# Page: AutoApply
# -----------------------------
elif menu == "🤖 AutoApply":
    st.title("🤖 AutoApply Settings")
    enabled = st.checkbox("Enable AutoApply", value=True)
    threshold = st.slider("Minimum Match Score", 50, 100, 85)

    if st.button("Save AutoApply Settings"):
        st.success(f"AutoApply enabled with threshold: {threshold}%")

# -----------------------------
# Page: Application Tracker
# -----------------------------
elif menu == "📌 Application Tracker":
    st.title("📌 Application Tracker")
    tracker = pd.DataFrame({
        "Job Title": ["Data Analyst", "AI Engineer"],
        "Company": ["Company A", "Company B"],
        "Status": ["Interview", "Submitted"],
        "Applied On": ["2025-05-22", "2025-05-23"]
    })
    st.dataframe(tracker)

# -----------------------------
# Page: Profile Settings
# -----------------------------
elif menu == "⚙️ Profile Settings":
    st.title("⚙️ Profile Settings")
    st.text_input("Full Name")
    st.text_input("Email")
    st.file_uploader("Upload Profile Photo", type=["png", "jpg"])
    st.button("Save Settings")
