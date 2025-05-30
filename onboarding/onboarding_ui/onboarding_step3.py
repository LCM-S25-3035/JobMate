import os
import streamlit as st
import datetime
import pycountry
from onboarding_api.services.resume_service import extract_resume_experience

MAX_DESC_LENGTH = 3000

import streamlit as st
import datetime
from onboarding_api.services.resume_gemini_parser import parse_resume_with_gemini
from .ui_sections import render_experience_fields, render_skills_field

def render_step3() -> bool:
    if "answers" not in st.session_state:
        st.session_state.answers = {}
    if "work_experiences" not in st.session_state:
        st.session_state.work_experiences = [{}]

    st.subheader("Upload Resume")
    uploaded_cv = st.file_uploader("Upload your resume (PDF)", type=["pdf"], key="resume_upload")

    if uploaded_cv:
        st.session_state.resume_uploaded = uploaded_cv
        st.info("Resume uploaded. Click extract to auto-fill experience & skills.")

    if uploaded_cv and st.button("Extract from Resume"):
        try:
            parsed = parse_resume_with_gemini(uploaded_cv)
            fill_session_from_parsed_resume(parsed)
            st.success("✅ Resume parsed and fields populated!")
        except Exception as e:
            st.error(f"❌ Failed to parse resume: {e}")

    render_experience_fields()
    render_skills_field()
    return True

def fill_session_from_parsed_resume(parsed):
    parsed_exps = parsed.get("work_experience", [])
    clean_exps = []
    for exp in parsed_exps:
        try:
            start = datetime.datetime.strptime(exp.get("start_date", "2020-01-01"), "%Y-%m-%d").date()
            end = datetime.datetime.strptime(exp.get("end_date", "2023-01-01"), "%Y-%m-%d").date()
        except ValueError:
            start = datetime.date(2020, 1, 1)
            end = datetime.date(2023, 1, 1)
        clean_exps.append({
            "company": exp.get("company", ""),
            "title": exp.get("title", ""),
            "start_date": start,
            "end_date": end,
            "current": False if exp.get("end_date") else True,
            "country": exp.get("location", "Canada").split(",")[-1].strip(),
            "description": exp.get("description", "")
        })
    st.session_state.work_experiences = clean_exps
    st.session_state.answers["skills"] = ", ".join(parsed.get("skills", []))
    st.session_state.answers["work_experiences"] = clean_exps

# Reference:
# OpenAI 4o, first prompt: 
# for this part, i want to integrate the resume  portion.. i want an option for the user to upload their resume and then i will fill like the job boards like company, title, country, start date, end date, currently working, description box with letter counts (3000) and then the skills sections. 

# OpenAI 4o, last prompt:
# getting error while trying to extract company info from extracted json "AttributeError: 'str' object has no attribute 'get'"