diff --git a/README.md b/README.md
index 6c947ef..219aaec 100644
--- a/README.md
+++ b/README.md
@@ -1,7 +1,147 @@
-Created the draft presentation on research paper .
+# AutoApply
 
-- **Project Board Link:** [GitHub Board Capstone Project AutoApply](https://github.com/users/DavidRochaR/projects/5)
-- **Documentation Link:** [Master document](https://mylambton.sharepoint.com/:w:/r/sites/CapstoneProject-JobRecommendationandResumeCustomizationSyste/Shared%20Documents/General/Documentation/Master%20Document%20-%20Group4.docx?d=w8e9e02192ab34fe1acfa0c066b9fcf7c&csf=1&web=1&e=8TO6ss)
-- **Job Offers Insights:** [Dashboard Link](https://app.powerbi.com/view?r=eyJrIjoiMTQzMTRkZTYtMTMwNC00M2Y2LWE3NzAtNDJlZWE1ZWViNzc3IiwidCI6ImI2NDE3Y2QwLTFmNzMtNDQ3MS05YTM5LTIwOTUzODIyYTM0YSIsImMiOjN9)
-- **PPT Presentation Group 4:** [Slides](https://mylambton.sharepoint.com/:p:/r/sites/CapstoneProject-JobRecommendationandResumeCustomizationSyste/Shared%20Documents/General/PPT%20Presentations/Master%20Slides.pptx?d=w4eef6074bdf74b878db86659b9db70cf&csf=1&web=1&e=lvFpgy)
-- **Weekly Check-in Link:** [Weekly Report](https://mylambton.sharepoint.com/:f:/r/sites/CapstoneProject-JobRecommendationandResumeCustomizationSyste/Shared%20Documents/General/Weekly%20Checkin?csf=1&web=1&e=r9bczB)
+AutoApply is a resume/job matching and analysis platform powered by AI. It processes resumes and job descriptions, evaluates compatibility, and manages data using MongoDB, Streamlit, and Apache Airflow.
+
+## Features
+- Upload and analyze resumes and job descriptions (PDF)
+- Extract and evaluate skills, experience, and compatibility
+- Store and manage resumes in MongoDB
+- Orchestrate data pipelines with Apache Airflow
+- Modern UI with Streamlit
+
+---
+
+## Prerequisites
+- [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/)
+- (Optional) Python 3.9+ for local development
+
+---
+
+## 1. Clone the Repository
+```bash
+git clone <your-repo-url>
+cd AutoApply
+```
+
+---
+
+## 2. Create Environment Variables
+
+Create a `.env` file in the **project root** (not inside `src/`). Example:
+
+```env
+# MongoDB
+MONGODB_URI=mongodb://airflow:airflow@mongodb:27017/autoapply?authSource=admin
+MONGODB_DB=autoapply
+MONGODB_COLLECTION=resumes
+
+# Gemini API Key
+GEMINI_API_KEY=your_gemini_api_key_here
+
+# Airflow/Postgres (defaults)
+POSTGRES_USER=airflow
+POSTGRES_PASSWORD=airflow
+POSTGRES_DB=airflow
+
+# Streamlit
+ENVIRONMENT=development
+DEBUG=True
+LOG_LEVEL=INFO
+```
+
+> **Replace** `your_gemini_api_key_here` with your actual Gemini API key.
+
+---
+
+## 3. Build and Start the Project
+
+```bash
+docker-compose up -d --build
+```
+
+This will start:
+- MongoDB (database)
+- Postgres (for Airflow)
+- Apache Airflow (webserver and scheduler)
+- Streamlit app (web interface)
+
+---
+
+## 4. Access the Applications
+
+- **Streamlit App:** [http://localhost:8501](http://localhost:8501)
+- **Apache Airflow:** [http://localhost:8080](http://localhost:8080)
+  - Username: `airflow`
+  - Password: `airflow`
+- **MongoDB:** [localhost:27017](mongodb://localhost:27017) (use a MongoDB client)
+
+---
+
+## 5. Upload and Analyze Resumes
+- Go to the Streamlit app
+- Upload your resume and job description (PDF)
+- View compatibility analysis and manage resumes in the database
+
+---
+
+## 6. Stopping the Project
+```bash
+docker-compose down
+```
+
+To remove all data (including database volumes):
+```bash
+docker-compose down -v
+```
+
+---
+
+## 7. Troubleshooting
+- Ensure your `.env` file is in the project root
+- Check container logs with `docker-compose logs <service>`
+- If you change environment variables, restart the containers
+
+---
+
+## 8. Project Structure
+```
+AutoApply/
+├── src/                  # Source code (Streamlit, utils, etc.)
+├── resume/               # Resume data (mounted in container)
+├── data/                 # Data files
+├── logs/                 # Airflow logs
+├── plugins/              # Airflow plugins
+├── Dockerfile.streamlit  # Streamlit Dockerfile
+├── docker-compose.yml    # Docker Compose config
+├── .env                  # Environment variables
+└── README.md             # This file
+```
+
+---
+
+## 9. Environment Variables Reference
+| Variable              | Description                        |
+|-----------------------|------------------------------------|
+| MONGODB_URI           | MongoDB connection string           |
+| MONGODB_DB            | MongoDB database name               |
+| MONGODB_COLLECTION    | MongoDB collection name             |
+| GEMINI_API_KEY        | Gemini API key                      |
+| POSTGRES_USER         | Airflow/Postgres user               |
+| POSTGRES_PASSWORD     | Airflow/Postgres password           |
+| POSTGRES_DB           | Airflow/Postgres database           |
+| ENVIRONMENT           | App environment (development/prod)  |
+| DEBUG                 | Debug mode (True/False)             |
+| LOG_LEVEL             | Logging level (INFO/DEBUG/WARN)     |
+
+---
+
+## 10. Useful Commands
+- View logs: `docker-compose logs <service>`
+- Rebuild containers: `docker-compose up -d --build`
+- Stop all: `docker-compose down`
+- Remove all data: `docker-compose down -v`
+
+---
+
+## License
+MIT
diff --git a/src/streamlit_app/app.py b/src/streamlit_app/app.py
index 3cacf60..7bdbc0b 100644
--- a/src/streamlit_app/app.py
+++ b/src/streamlit_app/app.py
@@ -21,19 +21,22 @@ st.markdown("""
     </style>
 """, unsafe_allow_html=True)
 
-def delete_folders():
-    "Delete the 'resume' and 'output' folders if they exist."
-    folders_to_delete = ["resume", "output"]
-
-    for folder in folders_to_delete:
-        if os.path.exists(folder):
-            shutil.rmtree(folder)
-            print(f"Deleted folder: {folder}")
-        os.makedirs(folder, exist_ok=True)
+def ensure_folders_exist():
+    """Ensure that required folders exist."""
+    # Get the absolute path to the project root
+    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
+    
+    # Define the folders to create
+    folders = ["resume", "output", "data", "parquet"]
+    
+    for folder in folders:
+        folder_path = os.path.join(project_root, folder)
+        os.makedirs(folder_path, exist_ok=True)
+        print(f"Ensured folder exists: {folder_path}")
 
 if "app_initialized" not in st.session_state:
     st.session_state.app_initialized = True  
-    delete_folders()
+    ensure_folders_exist()
 
 
 # Initialize session state
diff --git a/src/streamlit_app/option1_1.py b/src/streamlit_app/option1_1.py
index ac1df22..77f822b 100644
--- a/src/streamlit_app/option1_1.py
+++ b/src/streamlit_app/option1_1.py
@@ -3,6 +3,7 @@ import streamlit as st
 from utils import extract_cv_information, extract_job_posting_information,resume_education_info_personal,resume_delete_experience_not_related, validate_with_gemini, ats_score_evaluation_pre,export_match_and_missing_skills
 import json
 import time
+import os
 
 def run():
     st.markdown("<h1 style='text-align: center; font-size: 50px;'>Tailor my resume for a specific job opportunity</h1>", unsafe_allow_html=True)
@@ -19,33 +20,86 @@ def run():
     uploaded_job = st.file_uploader("Please upload your PDF Job Description", type=["pdf"])
 
     if ((uploaded_cv is not None) and (uploaded_job is not None)):
-        extract_cv_information(uploaded_cv)
-        extract_job_posting_information(uploaded_job)
-        ats_score_evaluation_pre()
-        export_match_and_missing_skills()
-        resume_education_info_personal()
-        resume_delete_experience_not_related()
+        try:
+            # Get the absolute path to the project root
+            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
+            st.write(f"Project root: {project_root}")
+            
+            # Create resume directory if it doesn't exist
+            resume_dir = os.path.join(project_root, "resume")
+            os.makedirs(resume_dir, exist_ok=True)
+            st.write(f"Resume directory: {resume_dir}")
+            
+            # Save uploaded files
+            cv_path = os.path.join(resume_dir, "uploaded_cv.pdf")
+            job_path = os.path.join(resume_dir, "uploaded_job.pdf")
+            
+            with open(cv_path, "wb") as f:
+                f.write(uploaded_cv.getbuffer())
+            with open(job_path, "wb") as f:
+                f.write(uploaded_job.getbuffer())
+            
+            st.write("Files saved successfully")
+            
+            # Process the files
+            st.write("Processing CV...")
+            extract_cv_information(uploaded_cv)
+            st.write("Processing job posting...")
+            extract_job_posting_information(uploaded_job)
+            st.write("Evaluating ATS score...")
+            ats_score_evaluation_pre()
+            st.write("Exporting skills...")
+            export_match_and_missing_skills()
+            st.write("Processing education info...")
+            resume_education_info_personal()
+            st.write("Filtering experience...")
+            resume_delete_experience_not_related()
 
-        # Check if all achievements are empty
-        # Load the resume data
-        file_path = "resume/resume_delete_experience_not_relate.json"
-        with open(file_path, "r", encoding="utf-8") as file_load:
-            filter_to_continue = json.load(file_load)
+            # Check if all achievements are empty
+            file_path = os.path.join(resume_dir, "resume_delete_experience_not_relate.json")
+            st.write(f"Looking for file at: {file_path}")
+            
+            if not os.path.exists(file_path):
+                st.error(f"Error: Could not find the processed resume file at {file_path}")
+                st.write("Directory contents:")
+                for file in os.listdir(resume_dir):
+                    st.write(f"- {file}")
+                return
+                
+            try:
+                with open(file_path, "r", encoding="utf-8") as file_load:
+                    filter_to_continue = json.load(file_load)
+            except json.JSONDecodeError as e:
+                st.error(f"Error reading JSON file: {str(e)}")
+                st.write("Directory contents:")
+                for file in os.listdir(resume_dir):
+                    st.write(f"- {file}")
+                return
 
-        if all(not experience["achievement"] for experience in filter_to_continue["work_experience"]):
-            print("entro line 46")
-            st.warning(
-                "⚠️ Sorry, none of your experiences match the job posting. "
-                "We recommend rewriting your achievements to better highlight relevant skills and trying again. "
-                "Click below to return to the home page."
-            )
-            if st.button("🏠 Back to Home"):
-                st.session_state.page = "Home"
-                if "app_initialized" in st.session_state:
-                    del st.session_state.app_initialized
-                st.rerun()
-        
-        else:
+            if not filter_to_continue.get("work_experience"):
+                st.warning(
+                    "⚠️ No work experience found in the processed resume. "
+                    "Please check your resume format and try again."
+                )
+                if st.button("🏠 Back to Home"):
+                    st.session_state.page = "Home"
+                    if "app_initialized" in st.session_state:
+                        del st.session_state.app_initialized
+                    st.rerun()
+                return
+
+            if all(not experience.get("achievement") for experience in filter_to_continue["work_experience"]):
+                st.warning(
+                    "⚠️ Sorry, none of your experiences match the job posting. "
+                    "We recommend rewriting your achievements to better highlight relevant skills and trying again. "
+                    "Click below to return to the home page."
+                )
+                if st.button("🏠 Back to Home"):
+                    st.session_state.page = "Home"
+                    if "app_initialized" in st.session_state:
+                        del st.session_state.app_initialized
+                    st.rerun()
+                return
             
             # Initialize session state if it doesn't exist
             if "achievements_pass" not in st.session_state:
@@ -54,34 +108,46 @@ def run():
             if "achievements_do_not_pass" not in st.session_state:
                 st.session_state.achievements_do_not_pass = []
 
-            # Load the resume data
-            file_path = "resume/resume_delete_experience_not_relate.json"
-
-            with open(file_path, "r", encoding="utf-8") as file_load:
-                resume_data = json.load(file_load)
-
-            work_experience = resume_data.get("work_experience", [])
+            work_experience = filter_to_continue.get("work_experience", [])
 
             st.write(f"## Evaluating work experience")
          
             # Process achievements and validate them
             for job in work_experience:
-                st.write(f"### Evaluating achievements for: {job['job_title']} in {job['company']}")
+                st.write(f"### Evaluating achievements for: {job.get('job_title', 'Unknown')} in {job.get('company', 'Unknown')}")
                 
-                for achievement in job["achievement"]:
-                    is_valid, feedback = validate_with_gemini(job['job_title'], achievement)
+                for achievement in job.get("achievement", []):
+                    is_valid, feedback = validate_with_gemini(job.get('job_title', ''), achievement)
 
                     if is_valid:
                         st.session_state.achievements_pass.append(
-                            {"job_title": job['job_title'], "achievement": achievement, "company":job['company'], "key":job['key'] }
+                            {
+                                "job_title": job.get('job_title', ''),
+                                "achievement": achievement,
+                                "company": job.get('company', ''),
+                                "key": job.get('key', '')
+                            }
                         )
                     else:
                         st.session_state.achievements_do_not_pass.append(
-                            {"job_title": job['job_title'], "achievement": achievement, "feedback": feedback,  "company":job['company'], "key":job['key']}
+                            {
+                                "job_title": job.get('job_title', ''),
+                                "achievement": achievement,
+                                "feedback": feedback,
+                                "company": job.get('company', ''),
+                                "key": job.get('key', '')
+                            }
                         )
                     time.sleep(0.2)
 
             st.session_state.page = "information_to_user"
             if st.button("View Compatibility Analysis"):
                 st.write(st.session_state.page)
-                st.rerun()
\ No newline at end of file
+                st.rerun()
+                
+        except Exception as e:
+            st.error(f"An error occurred: {str(e)}")
+            st.error(f"Current working directory: {os.getcwd()}")
+            st.error(f"Resume directory: {resume_dir}")
+            import traceback
+            st.error(f"Traceback: {traceback.format_exc()}")
\ No newline at end of file
diff --git a/src/streamlit_app/option2.py b/src/streamlit_app/option2.py
index b942b80..f6cb2be 100644
--- a/src/streamlit_app/option2.py
+++ b/src/streamlit_app/option2.py
@@ -1,101 +1,40 @@
 import streamlit as st
 import pandas as pd
-import pymongo
+from pymongo import MongoClient
+import json
 import os
 
 def run():
-    st.markdown("""
-        <h1 style='text-align: center; font-size: 50px;'>Find the Best Job Matches</h1>
-        <p style='text-align: center; font-size: 20px;'>Use the filters to narrow down job postings and let our AI recommend the best options.</p>
-    """, unsafe_allow_html=True)
-
-    # MongoDB Connection
-    MONGO_URI = st.secrets["api_keys"]["MONGODB_URI"]
-    MONGO_DB_NAME = st.secrets["api_keys"]["MONGODB_NAME"]
-    MONGO_JOBS_COLLECTION = st.secrets["api_keys"]["MONGODB_JOBS_COLLECTION"]
-
-    client_mongo = pymongo.MongoClient(MONGO_URI)
-    db = client_mongo[MONGO_DB_NAME]
-    collection = db[MONGO_JOBS_COLLECTION]
-
-    # Ruta al archivo local
-    parquet_file = "parquet/jobs_data.parquet"
-
-    # Si existe el archivo .parquet, lo cargamos desde allí
-    if os.path.exists(parquet_file):
-        df = pd.read_parquet(parquet_file)
-    else:
-        # Load jobs from MongoDB
-        jobs_data = list(collection.find({}))  # Retrieve everything
-        df = pd.DataFrame(jobs_data)
-        df["_id"] = df["_id"].astype(str)
-
-    # Convert to DataFrame
-    df = df.rename(columns={"_id": "Job ID", "Title": "Job Title", "Provincia": "Province", "Keyword": "Category"})
- 
-    # Fill NaN values
-    df["Category"] = df["Category"].fillna("Not Determined")
-    df["Province"] = df["Province"].fillna("Unknown")
-    
-    # Normalize text format
-    df["Category"] = df["Category"].str.title()
-    df["Province"] = df["Province"].str.title()
+    st.markdown("<h1 style='text-align: center; font-size: 50px;'>Resume Database</h1>", unsafe_allow_html=True)
+    st.write("Here you can view and manage the resumes in the database.")
     
-    # Extract unique categories and cities
-    category_options = ["All"] + sorted(df["Category"].unique().tolist())
-    city_options = ["All"] + sorted(df["Province"].unique().tolist())
-
-    # Sidebar Filters
-    st.sidebar.header("🔍 Filter Jobs")
+    try:
+        # Get MongoDB connection details from secrets
+        MONGO_URI = st.secrets["database"]["MONGODB_URI"]
+        MONGO_DB = st.secrets["database"]["MONGODB_DB"]
+        MONGO_COLLECTION = st.secrets["database"]["MONGODB_COLLECTION"]
         
-    selected_city = st.sidebar.selectbox("Select Province", city_options)
-    selected_category = st.sidebar.selectbox("Select Category", category_options)
-
-    # Apply Filters
-    filtered_df = df.copy()
-
-    if selected_city != "All":
-        filtered_df = filtered_df[filtered_df["Province"] == selected_city]
-
-    if selected_category != "All":
-        filtered_df = filtered_df[filtered_df["Category"] == selected_category]
-
-    # Pagination
-    total_rows = len(filtered_df)
-    rows_per_page = 20
-
-    if total_rows == 0:
-        st.warning("No jobs found matching your filters.")
-        return
-    elif total_rows <= rows_per_page:
-        total_pages = 1
-        page_number = 1  # Show all jobs on a single page
-    else:
-        total_pages = (total_rows // rows_per_page) + (1 if total_rows % rows_per_page > 0 else 0)
-        page_number = st.sidebar.slider("Page", 1, total_pages, 1)
-
-    start_idx = (page_number - 1) * rows_per_page
-    end_idx = start_idx + rows_per_page
-
-    st.write(f"Showing {start_idx + 1} - {min(end_idx, total_rows)} of {total_rows} jobs")
-
-    # Display paginated DataFrame
-    st.dataframe(filtered_df.iloc[start_idx:end_idx].drop(columns=["key_word_app","key_words_app"]))
-
-    # Job Selection
-    print(filtered_df.shape)
-
-    # Run AI Job Recommender
-    if st.button("🤖 Find Best Job Matches with AI Recommender"):
-        st.session_state['filtered_jobs'] = filtered_df
-        st.session_state.page = "Option2_1"
-        st.session_state.control = False
-        st.rerun()
-
-    # Back to Home
-    if st.button("⬅️ Back to Home"):
-        st.session_state.page = "Home"
-        if "app_initialized" in st.session_state:
-            del st.session_state.app_initialized
-        st.rerun()
+        # Connect to MongoDB
+        client = MongoClient(MONGO_URI)
+        db = client[MONGO_DB]
+        collection = db[MONGO_COLLECTION]
+        
+        # Get all resumes
+        resumes = list(collection.find())
+        
+        if not resumes:
+            st.warning("No resumes found in the database.")
+            return
+            
+        # Convert to DataFrame for display
+        df = pd.DataFrame(resumes)
+        
+        # Display the data
+        st.dataframe(df)
+        
+    except Exception as e:
+        st.error(f"An error occurred: {str(e)}")
+        st.error("Please make sure MongoDB is running and the connection details are correct.")
+        import traceback
+        st.error(f"Traceback: {traceback.format_exc()}")
 
diff --git a/src/streamlit_app/utils.py b/src/streamlit_app/utils.py
index 37b9bee..1b1d0ca 100644
--- a/src/streamlit_app/utils.py
+++ b/src/streamlit_app/utils.py
@@ -7,16 +7,51 @@ from io import BytesIO
 import re
 import string
 import time
+import os
+from datetime import datetime
+from nltk.corpus import stopwords
+from nltk.stem import WordNetLemmatizer
+from docx import Document
+from docx.shared import Pt, Inches
+from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
+from docx.oxml import OxmlElement
+from docx.oxml.ns import qn
+from docx.enum.style import WD_STYLE_TYPE
+from pymongo import MongoClient
+# Configure Gemini API
+your_api_key = os.getenv('GEMINI_API_KEY')
+if not your_api_key:
+    raise ValueError("GEMINI_API_KEY environment variable is not set")
 
-your_api_key = st.secrets["api_keys"]["GEMINI_API_KEY"]
+genai.configure(api_key=your_api_key)
 model_gemini = "models/gemini-2.0-flash"
 clean_json = "```json\n"
 
+def get_project_root():
+    """Get the absolute path to the project root directory."""
+    return os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
+
+def get_resume_dir():
+    """Get the absolute path to the resume directory."""
+    resume_dir = os.path.join(get_project_root(), "resume")
+    os.makedirs(resume_dir, exist_ok=True)
+    return resume_dir
+
+def save_resume_json(resume_json):
+    MONGODB_URI = st.secrets["database"]["MONGODB_URI"]
+    MONGODB_DB = st.secrets["database"]["MONGODB_DB"]
+    MONGODB_COLLECTION = st.secrets["database"]["MONGODB_COLLECTION"]
+
+    client = MongoClient(MONGODB_URI)
+    db = client[MONGODB_DB]
+    collection = db[MONGODB_COLLECTION]
+    collection.insert_one(resume_json)
+
 def extract_keywords_with_gemini():
 
     with open("resume/resume.json", "r", encoding="utf-8") as file:
         resume_json = json.load(file)
-
+    save_resume_json(resume_json)
     validation_prompt = f"""You are a resume keyword extractor.
 
 Given the following resume content, extract up to 25 relevant keywords that best represent this candidate's profile. Each keyword should be 1 to 3 words long, and focus on:
@@ -203,10 +238,10 @@ def ats_score_evaluation_pre():
     6. **Do NOT infer** technologies, skills, or synonyms not explicitly mentioned in the job posting.
     7. A skill only counts as matched if it appears clearly in the resume (in the skills section, summary, or experience).
     8. Be precise with terms:
-    - “GitHub Actions” may match “GitHub CI/CD” if clearly implied.
-    - “AWS Lambda” ≠ “Lambda”. AWS services must be explicitly named.
-    - Distinguish between “GitHub” (version control) and “GitHub Actions” (CI/CD).
-    9. Even if the ATS score is high, always include a **“recommendations”** section with:
+    - "GitHub Actions" may match "GitHub CI/CD" if clearly implied.
+    - "AWS Lambda" ≠ "Lambda". AWS services must be explicitly named.
+    - Distinguish between "GitHub" (version control) and "GitHub Actions" (CI/CD).
+    9. Even if the ATS score is high, always include a **"recommendations"** section with:
     - Suggestions for improvement.
     - Gaps or partial matches.
     - Phrasing tips for clearer alignment.
@@ -217,7 +252,7 @@ def ats_score_evaluation_pre():
 
     - Convert all terms to lowercase.
     - Remove special characters (parentheses, commas, etc.).
-    - Do not group terms (e.g., use “AWS Lambda”, “AWS SNS”, not “AWS (Lambda, SNS)”).
+    - Do not group terms (e.g., use "AWS Lambda", "AWS SNS", not "AWS (Lambda, SNS)").
     - Do not duplicate items.
     - Match only if the context in the resume supports it clearly.
 
@@ -358,7 +393,7 @@ def ats_score_evaluation_post():
     previous_missing_context = f"""
     ======= CONTEXT: ITEMS PREVIOUSLY MISSING =======
     Please re-evaluate the following missing items. 
-    IMPORTANT: Do NOT mark a skill or keyword as “matched” unless it is clearly and explicitly present in the resume text (summary, skills, or experience). Do NOT infer based on related terms or assumptions. Re-evaluate previously missing items strictly.
+    IMPORTANT: Do NOT mark a skill or keyword as "matched" unless it is clearly and explicitly present in the resume text (summary, skills, or experience). Do NOT infer based on related terms or assumptions. Re-evaluate previously missing items strictly.
 
     Previously missing technical skills: {ats_pre.get("missing_technical_skills", [])}
     Previously missing soft skills: {ats_pre.get("missing_soft_skills", [])}
@@ -383,11 +418,11 @@ def ats_score_evaluation_post():
         - "GitHub Actions" may match "GitHub CI/CD" if clearly implied.
         - AWS-specific services must be explicitly named (e.g., "AWS Lambda" ≠ just "Lambda").
         - Clearly distinguish between general terms like "GitHub" (version control) and specific tools like "GitHub Actions" (CI/CD).
-        5. Even if the ATS score is high, **always include a “Recommendations” section**. These should:
+        5. Even if the ATS score is high, **always include a "Recommendations" section**. These should:
         - Highlight areas that could be improved or better emphasized.
         - Indicate any gaps or partial matches in experience or responsibilities.
         - Suggest improvements in phrasing or contextualization (e.g., how to frame "client-facing" experience).
-        6. If something is only partially covered (e.g., “responsibility alignment: partial”), explain why.
+        6. If something is only partially covered (e.g., "responsibility alignment: partial"), explain why.
 
 
         ## Matching Rules (Strict and Normalized):
@@ -684,8 +719,7 @@ def resume_skills():
 
 
 def resume_education_info_personal():
-
-    input_filepath = f"resume/resume.json"
+    input_filepath = os.path.join(get_resume_dir(), "resume.json")
     with open(input_filepath, "r", encoding="utf-8") as file_load:
        original_cv = json.load(file_load)
     
@@ -694,8 +728,7 @@ def resume_education_info_personal():
         "education": original_cv.get("education", {})
     }
 
-
-    output_filepath = f"resume/resume_education_info_personal.json"
+    output_filepath = os.path.join(get_resume_dir(), "resume_education_info_personal.json")
     with open(output_filepath, "w", encoding="utf-8") as file_save:
         json.dump(output_file, file_save, ensure_ascii=False, indent=4)
         print(f"Output saved to '{output_filepath}'.")
@@ -751,7 +784,7 @@ def resume_promt_summary():
     - Focus on highlighting relevant experience, skills, and qualifications.
     - Ensure clarity, coherence, and alignment with the job offer.
     - The response must be in JSON format only, without any explanations or additional text.
-    - Rewrite the professional summary to align with the job posting’s focus on contributing to projects that support long-term sustainability and global investment strategies. Use clear, action-oriented language, and highlight relevant skills or experience that demonstrate the candidate’s ability to contribute to sustainable initiatives or global impact.
+    - Rewrite the professional summary to align with the job posting's focus on contributing to projects that support long-term sustainability and global investment strategies. Use clear, action-oriented language, and highlight relevant skills or experience that demonstrate the candidate's ability to contribute to sustainable initiatives or global impact.
 
     **Output Format:**
     {
@@ -777,45 +810,87 @@ def resume_promt_summary():
 
 
 def resume_delete_experience_not_related():
+    try:
+        input_filepath = os.path.join(get_resume_dir(), "resume.json")
+        with open(input_filepath, "r", encoding="utf-8") as file_load:
+            resume = json.load(file_load)
+        
+        job_experience = {"work_experience": resume.get("work_experience", [])}
+        
+        input_filepath = os.path.join(get_resume_dir(), "job_posting.json")
+        with open(input_filepath, "r", encoding="utf-8") as file_load:
+            job_offer = json.load(file_load)
+        
+        system_instructions = """
+        You are an HR specialist skilled in processing and analyzing resumes. Your task is to analyze each achievement in the work experience section and remove those that are not relevant to the given job offer.
 
-    input_filepath = f"resume/resume.json"
-    with open(input_filepath, "r", encoding="utf-8") as file_load:
-       resume = json.load(file_load)
-    
-    job_experience = {"work_experience":resume.get("work_experience", {})}
-    
-    input_filepath = f"resume/job_posting.json"
-    with open(input_filepath, "r", encoding="utf-8") as file_load:
-       job_offer = json.load(file_load)
-    
-    system_instructions = """
-    You are an HR specialist skilled in processing and analyzing resumes. Your task is to analyze each achievement in the work experience section and remove those that are not relevant to the given job offer.
-
-    **Instructions:**
-    - Use only the information available in the resume. Do not infer or add any details that are not explicitly mentioned.
-    - Evaluate each achievement individually and determine if the experience and skills it describes align with the job posting.
-    - Remove achievements that are not relevant to the job offer.
-    - Maintain the original JSON format, ensuring that only the non-relevant achievements are removed.
-    - Do not provide any explanations or extra text, only return the modified JSON.
+        **Instructions:**
+        - Use only the information available in the resume. Do not infer or add any details that are not explicitly mentioned.
+        - Evaluate each achievement individually and determine if the experience and skills it describes align with the job posting.
+        - Remove achievements that are not relevant to the job offer.
+        - Maintain the original JSON format, ensuring that only the non-relevant achievements are removed.
+        - Do not provide any explanations or extra text, only return the modified JSON.
 
-    **Output Format:**
-    (Same as input, but with non-relevant achievements removed)
-    """
+        **Output Format:**
+        {
+            "work_experience": [
+                {
+                    "job_title": "string",
+                    "company": "string",
+                    "location": "string",
+                    "start_date": "string",
+                    "end_date": "string",
+                    "key": "string",
+                    "achievement": ["string"]
+                }
+            ]
+        }
+        """
 
-    genai.configure(api_key = your_api_key)
-    model = genai.GenerativeModel(
-    model_gemini,
-    system_instruction=system_instructions,
-    )
+        genai.configure(api_key=your_api_key)
+        model = genai.GenerativeModel(
+            model_gemini,
+            system_instruction=system_instructions,
+            generation_config={
+                "temperature": 0.0,
+                "top_p": 1.0,
+                "top_k": 1,
+                "max_output_tokens": 1024
+            }
+        )
 
-    response = model.generate_content(f"The work experience seccion to analyze is {job_experience} and the job offer is {job_offer}")
-    cleaned_response = response.text.strip(clean_json).strip("```").replace("\n", "")
-    json_file = json.loads(cleaned_response)
-    # Save the result to the output file
-    output_filepath = f"resume/resume_delete_experience_not_relate.json"
-    with open(output_filepath, "w", encoding="utf-8") as file_save:
-        json.dump(json_file, file_save, ensure_ascii=False, indent=4)
-        print(f"Output saved to '{output_filepath}'.")
+        response = model.generate_content(f"The work experience section to analyze is {job_experience} and the job offer is {job_offer}")
+        
+        # Clean and parse the response
+        response_text = response.text.strip()
+        if response_text.startswith("```"):
+            response_text = response_text.split("```")[1]
+            if response_text.startswith("json"):
+                response_text = response_text[4:]
+        response_text = response_text.strip()
+        
+        try:
+            json_file = json.loads(response_text)
+        except json.JSONDecodeError as e:
+            print(f"Error parsing JSON response: {e}")
+            print(f"Raw response: {response_text}")
+            # Fallback to original work experience if JSON parsing fails
+            json_file = job_experience
+        
+        # Save the result to the output file
+        output_filepath = os.path.join(get_resume_dir(), "resume_delete_experience_not_relate.json")
+        with open(output_filepath, "w", encoding="utf-8") as file_save:
+            json.dump(json_file, file_save, ensure_ascii=False, indent=4)
+            print(f"Output saved to '{output_filepath}'")
+            
+    except Exception as e:
+        print(f"Error in resume_delete_experience_not_related: {str(e)}")
+        # Create a minimal valid JSON structure if something goes wrong
+        fallback_json = {"work_experience": []}
+        output_filepath = os.path.join(get_resume_dir(), "resume_delete_experience_not_relate.json")
+        with open(output_filepath, "w", encoding="utf-8") as file_save:
+            json.dump(fallback_json, file_save, ensure_ascii=False, indent=4)
+            print(f"Created fallback file at '{output_filepath}'")
 
 
 def customize_cv() -> dict:
@@ -1018,11 +1093,13 @@ def extract_cv_information(uploaded_pdf):
 
     json_file = json.loads(cleaned_response)
     # Save the result to the output file
-    output_filepath = "resume/resume.json"
+    output_filepath = os.path.join(get_resume_dir(), "resume.json")
     with open(output_filepath, "w", encoding="utf-8") as file_save:
         json.dump(json_file, file_save, ensure_ascii=False, indent=4)
         print(f"Output saved to '{output_filepath}'.")
 
+    save_resume_json(json_file)
+
 def extract_job_posting_information(uploaded_job):
     # Read the PDF content using pypdf
     pdf_reader = PdfReader(BytesIO(uploaded_job.getvalue()))
@@ -1143,8 +1220,21 @@ def extract_job_posting_information(uploaded_job):
     response = model.generate_content(f"The job posting to analyze is {pdf_text}")
     cleaned_response = response.text.strip(clean_json).strip("```").replace("\n", "")
 
-    json_file = json.loads(cleaned_response)
-    output_filepath = f"resume/job_posting.json"
+    # Defensive check for empty response
+    if not cleaned_response:
+        print("cleaned_response is empty!")
+        st.error("O resultado do processamento do job está vazio. Verifique o upload ou tente novamente.")
+        return None
+
+    try:
+        json_file = json.loads(cleaned_response)
+    except json.JSONDecodeError as e:
+        print(f"JSON decode error: {e}")
+        print(f"cleaned_response: {cleaned_response}")
+        st.error("Erro ao processar o job description. O formato retornado não é JSON válido.")
+        return None
+
+    output_filepath = os.path.join(get_resume_dir(), "job_posting.json")
     with open(output_filepath, "w", encoding="utf-8") as file_save:
         json.dump(json_file, file_save, ensure_ascii=False, indent=4)
         print(f"Output saved to '{output_filepath}'.")
@@ -1270,7 +1360,7 @@ def extract_job_posting_information_from_str(uploaded_job):
 
     json_file = json.loads(cleaned_response)
 
-    output_filepath = f"resume/job_posting.json"
+    output_filepath = os.path.join(get_resume_dir(), "job_posting.json")
     with open(output_filepath, "w", encoding="utf-8") as file_save:
         json.dump(json_file, file_save, ensure_ascii=False, indent=4)
         print(f"Output saved to '{output_filepath}'.")
@@ -1369,17 +1459,6 @@ def skills_missing():
 # (OpenAI, ChatGPT o1, first prompt, 2025): I have this template in Word, this Json, both have the same keys, guide me to make a code that reeplace the information in the template with the info in Json
 # (Claude, 3.5 Sonnet, last prompt, 2025): The template is not filling completly good, help me to correct the format
 
-import re
-import json
-import os
-from docx import Document
-from docx.shared import Pt, Inches
-from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
-from docx.enum.style import WD_STYLE_TYPE
-from docx.oxml.ns import qn
-from docx.oxml import OxmlElement
-# from docx2pdf import convert
-
 def split_into_sentences(text):
     print("split_into_sentences line", 839)
     """Splits the text into sentences using punctuation."""
