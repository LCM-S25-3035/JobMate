import streamlit as st
import os
import shutil

st.set_page_config(page_title="AutoApply App", layout="wide")

# CSS for styling
st.markdown("""
    <style>     
        h1 {
            font-size: 60px !important;
            text-align: center !important;
            color: #FF5733 !important;
        }
        p {
            font-size: 20px !important;
            text-align: left !important;
        }
    </style>
""", unsafe_allow_html=True)

def ensure_folders_exist():
    """Ensure that required folders exist."""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    folders = ["resume", "output", "data", "parquet"]
    for folder in folders:
        folder_path = os.path.join(project_root, folder)
        os.makedirs(folder_path, exist_ok=True)

if "app_initialized" not in st.session_state:
    st.session_state.app_initialized = True  
    ensure_folders_exist()

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "Home" 

def go_to_page(page_name):
    st.session_state.page = page_name
    st.rerun()

if st.session_state.page == "Home":
    st.markdown("<h1 style='font-size: 60px; text-align: center; color: #FF5733;'>Welcome to AutoApply App</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 24px; text-align: center;'>Your all-in-one solution for enhancing and customizing your resume to secure your dream job!</p>", unsafe_allow_html=True)
    st.write("")  

    option = st.radio("What would you like to do?", [
        "Option 1: Tailor my resume for a specific job",
        "Option 2: Find the best job matches with our AI recommender",
        "Option 3: Detect Ghost Jobs (Beta)"
    ], index=None, key="paso_0")

    if option == "Option 1: Tailor my resume for a specific job":
        go_to_page("Option1")

    elif option == "Option 2: Find the best job matches with our AI recommender":
        go_to_page("Option2")

    elif option == "Option 3: Detect Ghost Jobs (Beta)":
        go_to_page("GhostJobDetector")

elif st.session_state.page == "Option1":
    import option1
    option1.run()

elif st.session_state.page == "Option1_1":
    import option1_1
    option1_1.run()

elif st.session_state.page == "Option1_2":
    import option1_2
    option1_2.run()

elif st.session_state.page == "Option1_4":
    import option1_4
    option1_4.run()

elif st.session_state.page == "improve_skills":
    import improve_skills
    improve_skills.run()

elif st.session_state.page == "information_to_user":
    import information_to_user
    information_to_user.run()

elif st.session_state.page == "Option2":
    import option2
    option2.run()

elif st.session_state.page == "Option2_1":
    import option2_1
    option2_1.run()

elif st.session_state.page == "Option2_2":
    import option2_2
    option2_2.run()

elif st.session_state.page == "add_skills":
    import add_skills
    add_skills.run()

elif st.session_state.page == "customization_cv":
    import customization_cv
    customization_cv.run()

elif st.session_state.page == "GhostJobDetector":
    import ghost_job_detector_ui
    ghost_job_detector_ui.run()
