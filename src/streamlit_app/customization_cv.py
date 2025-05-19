import json
import streamlit as st
import pandas as pd
import google.generativeai as genai
from io import BytesIO
import numpy as np
import re
from utils import get_resume_dir, join_all_resume_json, generate_cv,resume_promt_summary,ats_score_evaluation_post
import os

var_back_to_job_seleccion = "⬅️ Back to Job Selection"

def run():
    st.markdown("<h1 style='text-align: center; font-size: 50px;'>Customization CV - Download CV</h1>", unsafe_allow_html=True)
    
    updated_resume_path = os.path.join(get_resume_dir(), "resume_updated.json")
    with open(updated_resume_path, "r", encoding="utf-8") as file_load:
        resume_update = json.load(file_load)

    user_answers_path  = os.path.join(get_resume_dir(), "resume_user_answers.json")
    if os.path.exists(user_answers_path ):
        with open(user_answers_path , "r", encoding="utf-8") as file_load:
            user_answers_list = json.load(file_load)
    else:
        user_answers_list = []


    user_answers = {}
    for entry in user_answers_list:
        job_key = entry["job_key"]
        achievement = entry["achievement"]
        
        if job_key not in user_answers:
            user_answers[job_key] = [] 
        
        user_answers[job_key].append(achievement) 

    # Update file path
    resume_final_path = os.path.join(get_resume_dir(), "resume_final_experience.json")

    if not user_answers:
        with open(resume_final_path, "w", encoding="utf-8") as file:
            json.dump(resume_update, file, indent=4, ensure_ascii=False)
    else:
        for experience in resume_update["work_experience"]:
            job_key = experience["key"]

            if job_key in user_answers: 
                if "achievement" not in experience:
                    experience["achievement"] = []

                for achievement in user_answers[job_key]:
                    if achievement not in experience["achievement"]:
                        experience["achievement"].append(achievement)

        with open(resume_final_path, "w", encoding="utf-8") as file:
            json.dump(resume_update, file, indent=4, ensure_ascii=False)
    
    resume_promt_summary()
    join_all_resume_json()
    generate_cv()

    resume_word_path = os.path.join(get_resume_dir(), "resume_final_to_word.json")
    with open(resume_word_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    user_name = data.get('personal_information', {}).get('name', 'Unknown').strip()
    user_name = " ".join(user_name.title().split())
    output_path = f"output/{user_name}_customization.docx" 

    # Check if customized cv is generated 
    if not os.path.exists(output_path):
        st.error(f"Fail to generate Customized Word CV at: {output_path}")
        st.stop()

    ats_score_evaluation_post()
    
    st.write(f"## Your customization was complete")

    ats_pre_path = os.path.join(get_resume_dir(), "ats_score_evaluation_pre.json")
    with open(ats_pre_path, "r", encoding="utf-8") as file_load:
        evaluation_pre = json.load(file_load)

    ats_post_path  = os.path.join(get_resume_dir(), "ats_score_evaluation_post.json")
    with open(ats_post_path , "r", encoding="utf-8") as file_load:
        evaluation_post = json.load(file_load)

    st.write(f"### Your ATS score Before: {evaluation_pre['ats_score']}")
    st.write(f"### Your ATS score After: {evaluation_post['ats_score']}")
    st.write(f"""## Your Customized Resume is Ready!
                  This resume has been tailored to match the job posting by aligning relevant skills, keywords, and action-oriented language to improve your ATS Score.
                  📄 You will receive the resume in an editable Word format, so you can make final formatting adjustments or add any personal touches before submitting your application.
             """)
    
    # Read the file in binary mode
    with open(output_path, "rb") as file:
        file_bytes = file.read()

    # Download button
    if st.download_button(
        label="📥 Download personalized CV",
        data=file_bytes,
        file_name="customization_cv.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"):

        st.write(f"### OKEY")
        # st.session_state.page = "Home"
        # if "app_initialized" in st.session_state:
        #     del st.session_state.app_initialized
        # st.rerun()
        
    # Download the word file
    if st.button("🏠 Back to Home"):
        
        st.session_state.page = "Home"
        if "app_initialized" in st.session_state:
            del st.session_state.app_initialized
        st.rerun()