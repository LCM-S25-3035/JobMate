import streamlit as st
import pymongo
from datetime import datetime

# MongoDB Setup
client = pymongo.MongoClient("mongodb+srv://joycemur:adminPassword@cluster0.xg9ol8l.mongodb.net/")
db = client["TESTJOB"]
users_collection = db["users"]
resumes_collection = db["resumes"]
jobs_collection = db["job_posts"]

# Helper Functions
def validate_user(username, password, role):
    user = users_collection.find_one({
        "username": username.strip().lower(),
        "password": password.strip(),
        "role": role.strip().lower()
    })
    return user is not None

def recruiter_dashboard():
    st.title("Recruiter Dashboard")
    

    # Post a job button
    if st.button("➕ Post a Job"):
        st.session_state["page"] = "job_post"
        st.rerun()

    st.sidebar.header("🔍 Filter Candidates")
    selected_job = st.sidebar.selectbox("Select Job Posting", ["All"] + sorted(resumes_collection.distinct("job_title")))
    min_score = st.sidebar.slider("Minimum ATS Score", 0, 100, 50)

    query = {"ats_score": {"$gte": min_score}}
    if selected_job != "All":
        query["job_title"] = selected_job

    candidates = list(resumes_collection.find(query))
    st.markdown(f"### 👥 Total Applicants: {len(candidates)}")

    if not candidates:
        st.info("No applicants yet.")
        if jobs_collection.count_documents({}) == 0:
            st.warning("You haven't posted any jobs yet.")
            if st.button("📢 Post your first job"):
                st.session_state["page"] = "job_post"
                st.rerun()
        else:
            st.success("You have job posts. Waiting for applicants...")
    else:
        for c in candidates:
            with st.expander(f"{c.get('name', 'Unnamed')} - ATS Score: {c.get('ats_score', 'N/A')}"):
                st.write(f"**Email:** {c.get('email')}")
                st.write(f"**Applied Job:** {c.get('job_title')}")
                st.write(f"**Skills:** {', '.join(c.get('skills', []))}")
                st.write(f"**Experience:** {c.get('experience', 'N/A')} years")

# Your Posted Jobs

    st.markdown("---")
    st.subheader("📄 Your Job Posts")

    posted_jobs = list(jobs_collection.find({
        "recruiter_id": st.session_state["logged_in_user"]
    }).sort("posted_at", -1))

    if not posted_jobs:
        st.info("You haven’t posted any jobs yet.")
    else:
        for job in posted_jobs:
            with st.expander(f"{job.get('title', 'Untitled')} at {job.get('company', 'Unknown')}"):
                st.write(f"**Location:** {job.get('location')}")
                st.write(f"**Experience Level:** {job.get('experience_level')}")
                st.write(f"**Skills:** {', '.join(job.get('skills', []) or [])}")
                st.write(f"**Status:** {job.get('status')}")
                st.write(f"**Deadline:** {job.get('deadline')}")
                st.write(f"**Posted At:** {job.get('posted_at').strftime('%Y-%m-%d %H:%M:%S')}")
            
            
def job_post_page():
    st.title("📝 Post a New Job - JobMate")
    if "logged_in_user" not in st.session_state or st.session_state.get("role", "").lower() != "recruiter":
        st.warning("Please log in as a recruiter to post jobs.")
        return

    with st.form("post_job_form"):
        job_title = st.text_input("Job Title")
        company = st.text_input("Company Name")
        location = st.text_input("Location")
        description = st.text_area("Job Description")
        skills_input = st.text_input("Skills (comma-separated)")
        experience_level = st.selectbox("Experience Level", ["Entry-level", "Mid-level", "Senior-level"])
        deadline = st.date_input("Deadline")
        status = st.selectbox("Status", ["Active", "Draft"])

        submit = st.form_submit_button("Post Job")
        if submit:
            skills = [s.strip() for s in skills_input.split(",") if s.strip()]
            jobs_collection.insert_one({
                "recruiter_id": st.session_state["logged_in_user"],
                "title": job_title,
                "company": company,
                "location": location,
                "description": description,
                "skills": skills,
                "experience_level": experience_level,
                "deadline": str(deadline),
                "status": status,
                "posted_at": datetime.utcnow()
            })
            st.success("✅ Job posted successfully!")

    # Show outside the form
    st.markdown("---")
    if st.button("🏠 Back to Dashboard"):
        st.session_state["page"] = "recruiter_dash"
        st.rerun()

# ---- ROUTER ----
if st.session_state.get("page") == "recruiter_dash":
    recruiter_dashboard()
    st.stop()
elif st.session_state.get("page") == "job_post":
    job_post_page()
    st.stop()

# ---- LOGIN UI ----
st.title("Welcome to JobMate")
menu = st.sidebar.selectbox("Login or Sign Up", ["Login"])
role = st.sidebar.selectbox("Are you the...", ["Recruiter"])  # Limit for now

if menu == "Login":
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Log In"):
        if validate_user(username, password, role):
            st.session_state["logged_in_user"] = username
            st.session_state["role"] = role
            st.session_state["page"] = "recruiter_dash"
            st.rerun()
        else:
            st.error("❌ Invalid credentials or role.")
