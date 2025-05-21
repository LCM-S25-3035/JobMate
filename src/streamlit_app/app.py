import streamlit as st
import os

st.set_page_config(page_title="AutoApply App", layout="wide")

# --- Styling ---
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

# --- Folder Setup ---
def ensure_folders_exist():
    """Ensure required folders exist relative to project root."""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    folders = ["resume", "output", "data", "parquet"]
    
    for folder in folders:
        folder_path = os.path.join(project_root, folder)
        os.makedirs(folder_path, exist_ok=True)
        print(f"✅ Ensured folder exists: {folder_path}")

# Only run once
if "app_initialized" not in st.session_state:
    ensure_folders_exist()
    st.session_state.app_initialized = True

# --- Navigation State ---
if "page" not in st.session_state:
    st.session_state.page = "Home" 

def go_to_page(page_name):
    st.session_state.page = page_name
    st.rerun()

# --- Routing ---
def load_page(page_name):
    try:
        __import__(page_name)
        getattr(__import__(page_name), 'run')()
    except Exception as e:
        st.error(f"❌ Failed to load page '{page_name}': {e}")

# --- Main Page Logic ---
if st.session_state.page == "Home":
    st.markdown("<h1>Welcome to AutoApply App</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 24px; text-align: center;'>Your all-in-one solution for enhancing and customizing your resume to secure your dream job!</p>", unsafe_allow_html=True)
    
    st.write("")  
    option = st.radio("What would you like to do?", [
        "Option 1: Tailor my resume for a specific job",
        "Option 2: Find the best job matches with our AI recommender"
    ], index=None, key="paso_0")
    
    if option == "Option 1: Tailor my resume for a specific job":
        go_to_page("Option1")

    elif option == "Option 2: Find the best job matches with our AI recommender":
        go_to_page("Option2")

# Page mapping
else:
    page_map = {
        "Option1": "option1",
        "Option1_1": "option1_1",
        "Option1_2": "option1_2",
        "Option1_4": "option1_4",
        "Option2": "option2",
        "Option2_1": "option2_1",
        "Option2_2": "option2_2",
        "add_skills": "add_skills",
        "improve_skills": "improve_skills",
        "information_to_user": "information_to_user",
        "customization_cv": "customization_cv",
    }

    page_key = st.session_state.page
    if page_key in page_map:
        load_page(page_map[page_key])
    else:
        st.error(f"🚫 Unknown page: {page_key}")