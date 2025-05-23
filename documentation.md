# AutoApply Project Documentation

### Project Overview

**AutoApply** is an intelligent, end-to-end platform designed to help users optimize and customize their resumes for specific job opportunities, leveraging AI to maximize their chances of passing Applicant Tracking Systems (ATS) and securing interviews. The system provides two main functionalities:
1. **Tailor Resume for a Specific Job**: Users upload their resume and a job description, and the app analyzes, matches, and suggests improvements to maximize compatibility.
2. **AI Job Recommender**: Users upload their resume, and the app finds and recommends the best-matching job postings from a database, then helps tailor the resume for the selected job.

---

### Main Components

#### 1. **User Interface (Streamlit App)**
- **Entry Point**: `src/streamlit_app/app.py`
  - Presents two main options: tailor resume for a job or find best job matches.
  - Manages navigation and session state.
- **Option 1 Workflow**: Tailor for a specific job
  - `option1.py` → `option1_1.py` (upload resume & job) → analysis & improvement steps → `information_to_user.py` (results) → `improve_skills.py` (improve achievements) → `add_skills.py` (add missing skills) → `customization_cv.py` (final resume download)
- **Option 2 Workflow**: AI job recommender
  - `option2.py` (filter jobs) → `option2_1.py` (upload resume, get matches) → `option2_2.py` (tailor for selected job) → same improvement and download steps as Option 1

#### 2. **Core Logic & Utilities**
- **`utils.py`**: Contains all core logic for:
  - Extracting keywords from resumes using Google Gemini AI.
  - Matching candidate skills to job postings (Jaccard similarity, flexible matching).
  - ATS score evaluation (pre- and post-customization).
  - Resume parsing, job posting parsing, and text normalization.
  - CV generation (Word document).
  - Helper functions for session state, file management, and feedback.

#### 3. **Data Gathering & Processing**
- **`src/data_gathering/`**: Scripts for scraping, extracting, and processing job postings and resumes.
  - MongoDB integration for job data.
  - Skill extraction, experience/education parsing, and data cleaning.

#### 4. **AI Agents**
- **`src/ai_agents/`**: Modular agents for:
  - Resume-job matching.
  - Skill extraction.
  - Resume analysis.
  - Customization and ATS scoring.

#### 5. **Data Insights**
- **`src/data_insights/`**: Jupyter notebooks and scripts for analyzing job market trends, skill gaps, and resume insights.

#### 6. **Workflow Automation**
- **`src/AirflowDAG/`**: Airflow DAGs for automating data pipelines and job scraping.

---

### Key Features

- **AI-Powered Keyword Extraction**: Uses Google Gemini to extract relevant skills and keywords from resumes and job descriptions.
- **ATS Score Evaluation**: Simulates how an ATS would score the resume against a job posting, providing actionable recommendations.
- **Interactive Resume Improvement**: Guides users to rewrite achievements and add missing skills, validating improvements with AI.
- **Job Matching**: Finds best-fit jobs from a database using flexible, AI-driven matching.
- **Resume Customization & Download**: Generates a tailored, ATS-optimized resume in Word format for download.
- **Session Management**: Maintains user progress and state across multiple steps.

---

### File/Module Structure

- `src/streamlit_app/`: Main app and workflow modules.
- `src/streamlit_app/utils.py`: Core logic and AI integration.
- `src/jobposting.py`: Job data extraction and processing.
- `src/data_gathering/`: Data collection and preprocessing scripts.
- `src/ai_agents/`: Modular AI agents for different tasks.
- `src/data_insights/`: Data analysis and visualization.
- `src/AirflowDAG/`: Workflow automation.

---

### How It Works (User Flow)

1. **Start**: User chooses to tailor a resume or find job matches.
2. **Upload**: User uploads resume (and optionally a job description).
3. **Analysis**: AI extracts skills, matches to jobs, and evaluates ATS compatibility.
4. **Feedback**: User receives detailed feedback on strengths, weaknesses, and missing skills.
5. **Improvement**: User rewrites achievements and adds missing skills, with AI validation.
6. **Customization**: Final tailored resume is generated and available for download.
7. **Repeat/Explore**: User can repeat the process for other jobs or resumes.

---

### Technologies Used

- **Python** (Streamlit, Pandas, Pymongo, Google Generative AI, PyPDF, etc.)
- **MongoDB** (Job data storage)
- **Google Gemini** (AI for NLP tasks)
- **Airflow** (Data pipeline automation)
- **Jupyter Notebooks** (Data analysis)
- **PowerBI** (External dashboard for job insights)

---

### External Links

- [Project Board](https://github.com/users/DavidRochaR/projects/5)
- [Master Documentation](https://mylambton.sharepoint.com/:w:/r/sites/CapstoneProject-JobRecommendationandResumeCustomizationSyste/Shared%20Documents/General/Documentation/Master%20Document%20-%20Group4.docx?d=w8e9e02192ab34fe1acfa0c066b9fcf7c&csf=1&web=1&e=8TO6ss)
- [Job Offers Insights Dashboard](https://app.powerbi.com/view?r=eyJrIjoiMTQzMTRkZTYtMTMwNC00M2Y2LWE3NzAtNDJlZWE1ZWViNzc3IiwidCI6ImI2NDE3Y2QwLTFmNzMtNDQ3MS05YTM5LTIwOTUzODIyYTM0YSIsImMiOjN9)
- [Slides](https://mylambton.sharepoint.com/:p:/r/sites/CapstoneProject-JobRecommendationandResumeCustomizationSyste/Shared%20Documents/General/PPT%20Presentations/Master%20Slides.pptx?d=w4eef6074bdf74b878db86659b9db70cf&csf=1&web=1&e=lvFpgy)
- [Weekly Report](https://mylambton.sharepoint.com/:f:/r/sites/CapstoneProject-JobRecommendationandResumeCustomizationSyste/Shared%20Documents/General/Weekly%20Checkin?csf=1&web=1&e=r9bczB)

---