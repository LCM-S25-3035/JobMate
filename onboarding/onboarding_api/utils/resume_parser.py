import streamlit as st
from onboarding_api.services.resume_service import extract_resume_experience

def render_resume_upload_section(user_id: str, region: str, key: str = "resume_upload") -> list:
    """
    UI-facing logic to wrap the upload input widget and calls the parser (frontend trigger).
    """
    st.subheader("Upload Resume")
    uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"], key=key)

    if uploaded_file:
        with st.spinner("Extracting experience from resume..."):
            try:
                parsed_experiences = extract_resume_experience(uploaded_file, user_id, region)
                st.success("Resume uploaded and parsed successfully!")
                return parsed_experiences
            except Exception as e:
                st.error(f"Error parsing resume: {e}")
    return []

# Reference: 
# OpenAI 4o: can i use this as a standalone function? coz this can be used everywhere for every interface not only for our step3_resume.py.. for step3_resume.py, i want a pure FE. 