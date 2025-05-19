# option1.py
import streamlit as st
from utils import extract_cv_information, extract_job_posting_information,resume_education_info_personal,resume_delete_experience_not_related, validate_with_gemini, ats_score_evaluation_pre,export_match_and_missing_skills
import json
import time
import os
import glob

def run():
    st.markdown("<h1 style='text-align: center; font-size: 50px;'>Tailor my resume for a specific job opportunity</h1>", unsafe_allow_html=True)
    st.write("Here you can upload your resume and customize it for a job opportunity.")
    
    st.write("")
    
    uploaded_cv = None
    uploaded_cv = st.file_uploader("Please upload your PDF Resume", type=["pdf"])

    st.write("")

    uploaded_job = None
    uploaded_job = st.file_uploader("Please upload your PDF Job Description", type=["pdf"])

    if ((uploaded_cv is not None) and (uploaded_job is not None)):
        try:
            # Get the absolute path to the project root
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
            st.write(f"Project root: {project_root}")
            
            # Create resume directory if it doesn't exist
            resume_dir = os.path.join(project_root, "resume")
            os.makedirs(resume_dir, exist_ok=True)
            st.write(f"Resume directory: {resume_dir}")

            # Clean up old resume JSONs before saving new files
            for old_file in glob.glob(os.path.join(resume_dir, "*.json")):
                os.remove(old_file)
                print(f"Deleted old resume file: {old_file}")

            
            # Save uploaded files
            cv_path = os.path.join(resume_dir, "uploaded_cv.pdf")
            job_path = os.path.join(resume_dir, "uploaded_job.pdf")
            
            with open(cv_path, "wb") as f:
                f.write(uploaded_cv.getbuffer())
            with open(job_path, "wb") as f:
                f.write(uploaded_job.getbuffer())
            
            st.write("Files saved successfully")
            
            # Process the files
            st.write("Processing CV...")
            extract_cv_information(uploaded_cv)
            resume_path = os.path.join(resume_dir, "resume.json")
            if os.path.exists(resume_path):
                st.success(f"resume.json exists at: {resume_path}")
                st.write("Resume folder contents:")
                for f in os.listdir(resume_dir):
                    st.write("•", f)
            else:
                st.error(f"resume.json was NOT created at: {resume_path}")
                st.stop()

            st.write("Processing job posting...")
            extract_job_posting_information(uploaded_job)
            st.write("Evaluating ATS score...")
            ats_score_evaluation_pre()
            st.write("Exporting skills...")
            export_match_and_missing_skills()
            st.write("Processing education info...")
            resume_education_info_personal()
            st.write("Filtering experience...")
            resume_delete_experience_not_related()

            # Check if all achievements are empty
            file_path = os.path.join(resume_dir, "resume_delete_experience_not_relate.json")
            st.write(f"Looking for file at: {file_path}")
            
            if not os.path.exists(file_path):
                st.error(f"Error: Could not find the processed resume file at {file_path}")
                st.write("Directory contents:")
                for file in os.listdir(resume_dir):
                    st.write(f"- {file}")
                return
                
            try:
                with open(file_path, "r", encoding="utf-8") as file_load:
                    filter_to_continue = json.load(file_load)
            except json.JSONDecodeError as e:
                st.error(f"Error reading JSON file: {str(e)}")
                st.write("Directory contents:")
                for file in os.listdir(resume_dir):
                    st.write(f"- {file}")
                return

            if not filter_to_continue.get("work_experience"):
                st.warning(
                    "⚠️ No work experience found in the processed resume. "
                    "Please check your resume format and try again."
                )
                if st.button("🏠 Back to Home"):
                    st.session_state.page = "Home"
                    if "app_initialized" in st.session_state:
                        del st.session_state.app_initialized
                    st.rerun()
                return

            if all(not experience.get("achievement") for experience in filter_to_continue["work_experience"]):
                st.warning(
                    "⚠️ Sorry, none of your experiences match the job posting. "
                    "We recommend rewriting your achievements to better highlight relevant skills and trying again. "
                    "Click below to return to the home page."
                )
                if st.button("🏠 Back to Home"):
                    st.session_state.page = "Home"
                    if "app_initialized" in st.session_state:
                        del st.session_state.app_initialized
                    st.rerun()
                return
            
            # Initialize session state if it doesn't exist
            if "achievements_pass" not in st.session_state:
                st.session_state.achievements_pass = []

            if "achievements_do_not_pass" not in st.session_state:
                st.session_state.achievements_do_not_pass = []

            work_experience = filter_to_continue.get("work_experience", [])

            st.write(f"## Evaluating work experience")
         
            # Process achievements and validate them
            for job in work_experience:
                st.write(f"### Evaluating achievements for: {job.get('job_title', 'Unknown')} in {job.get('company', 'Unknown')}")
                
                for achievement in job.get("achievement", []):
                    is_valid, feedback = validate_with_gemini(job.get('job_title', ''), achievement)

                    if is_valid:
                        st.session_state.achievements_pass.append(
                            {
                                "job_title": job.get('job_title', ''),
                                "achievement": achievement,
                                "company": job.get('company', ''),
                                "key": job.get('key', '')
                            }
                        )
                    else:
                        st.session_state.achievements_do_not_pass.append(
                            {
                                "job_title": job.get('job_title', ''),
                                "achievement": achievement,
                                "feedback": feedback,
                                "company": job.get('company', ''),
                                "key": job.get('key', '')
                            }
                        )
                    time.sleep(0.2)

            st.session_state.page = "information_to_user"
            if st.button("View Compatibility Analysis"):
                st.write(st.session_state.page)
                st.rerun()
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.error(f"Current working directory: {os.getcwd()}")
            st.error(f"Resume directory: {resume_dir}")
            import traceback
            st.error(f"Traceback: {traceback.format_exc()}")