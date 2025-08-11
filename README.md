# JobMate

## Auto Apply 2.0: Powered by JobMate

JobMate is a two-sided recruitment platform designed to streamline hiring for recruiters while supporting applicants with ATS-friendly resume optimization. Built on the foundational work of the AutoApply app, which focused on AI-based job recommendations and resume tailoring, JobMate extends functionality to include full recruiter-side tools and end-to-end applicant management.

## How the Previous App Worked: AutoApply

AutoApply is a resume/job matching and analysis platform powered by AI. It processes resumes and job descriptions, evaluates compatibility, and manages data using MongoDB, Streamlit, and Apache Airflow.

## Features

- Upload and analyze resumes and job descriptions (PDF)
- Extract and evaluate skills, experience, and compatibility
- Store and manage resumes in MongoDB
- Orchestrate data pipelines with Apache Airflow
- Modern UI with Streamlit

---
# New Features in JobMate

### Applicant Features
- **ATS Compatibility Scoring** – Evaluates resume alignment with job descriptions and provides actionable recommendations.
- **Resume Optimization** – AI-powered tailoring to improve match scores based on job requirements.
- **Cover Letter Generation** – Creates personalized, ATS-friendly cover letters matched to tailored resumes.
- **Ghost Job Detection** – Identifies fake or inactive job postings to protect applicants.
- **AI-Powered Interview Questions Generator** – Generates interview questions based on skills and job descriptions.

### Recruiter Features
- **Job Posting Management** – Create, update, pause, and remove job postings.
- **Candidate Management System** – Update applicant status in the recruitment pipeline (Talent Journey).
- **AI Salary & Skills Recommendation** – Suggests competitive salaries and in-demand skills.
- **AI-Powered Interview Question Generation** – Generates role-specific interview questions with scoring rubrics.

### Job Auto Application Feature

- **L.i.n.k.e.dIn E@sy @pply Automat0n** – Autom@tes the E.a.s.y_@pply process, reducing manual form-filling.
- **G.l.a.s.s.door Q.u.i.c.k @pply Automat0n** – Autom@tes Glass_door applications with smart job filtering.
- **Multi-Step Form Handling** – Navigates and completes multi-page application flows with file uploads and questions.
- **Application Tracking** – Saves applied job details (title, date, URL) to CSV.


## Prerequisites

- [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/)
- (Optional) Python 3.9+ for local development
- Get Google Gemini API Key (https://ai.google.dev/gemini-api/docs/api-key)

---

## 1. Clone the Repository

```bash
git clone <your-repo-url>
cd JobMate
```

---

## 2. Create Environment Variables

Create a `.env` file in the **project root** (not inside `src/`). Example:

```env
# MongoDB
MONGODB_URI=mongodb://airflow:airflow@mongodb:27017/autoapply?authSource=admin
MONGODB_DB=autoapply
MONGODB_COLLECTION=resumes

# Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Airflow/Postgres (defaults)
POSTGRES_USER=airflow
POSTGRES_PASSWORD=airflow
POSTGRES_DB=airflow

# SonarQube
SONAR_TOKEN=your_sonarqube_token_here
SONAR_PROJECT_KEY=JobMate

# Streamlit
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO
```

> **Replace** `your_gemini_api_key_here` with your actual Gemini API key.

---

## 3. Build and Start the Project

```bash
docker-compose up -d --build
```

This will start:

- MongoDB (database)
- Postgres (for Airflow)
- Apache Airflow (webserver and scheduler)
- Streamlit app (web interface)

---

## 4. Access the Applications

- **Streamlit App:** [http://localhost:8501](http://localhost:8501)
- **Apache Airflow:** [http://localhost:8080](http://localhost:8080)
  - Username: `airflow`
  - Password: `airflow`
- **MongoDB:** [localhost:27017](mongodb://localhost:27017) (use a MongoDB client)

---
## 5. Upload and Analyze Resumes

- Go to the Streamlit app
- Upload your resume and job description (PDF)
- View compatibility analysis and manage resumes in the database

---

## 6. Stopping the Project

```bash
docker-compose down
```

To remove all data (including database volumes):

```bash
docker-compose down -v
```
---

## 7. Troubleshooting

- Ensure your `.env` file is in the project root
- Check container logs with `docker-compose logs <service>`
- If you change environment variables, restart the containers

## 8. For L.i.n.k.e.dIn Aut0_Apply

- This automation runs as a standalone Python script and should be executed in a Python-compatible IDE (e.g., VS Code, PyCharm).
- pip install -r requirements.txt
- Have have a fully completed L1nked1n profile with CV and Phone number attached
- Ensure you have a chrome browser, and updated
- To activate the script run: python app.py 
- Enter credentials, job title and location
- For every succesful application, a csv for application tracking is automatically saved on the same folder
---

```bash
flowchart TD
    A[Start Script] --> B[User Inputs LinkedIn Credentials, Job Title, Location]
    B --> C[Log in to LinkedIn]
    C --> D[Go to Jobs Page & Apply Easy Apply Filter]
    D --> E[Load All Job Cards on Page]
    E --> F{Already Applied?}
    F -- Yes --> G[Skip Job]
    F -- No --> H{Easy Apply Available?}
    H -- No --> G
    H -- Yes --> I[Start Application Modal]
    I --> J[Click Next / Review / Submit]
    J --> K{Page Progresses?}
    K -- No --> L[Discard Application & Close Modal]
    K -- Yes --> M[Submit Application]
    M --> N[Log Success to CSV]
    N --> O[Move to Next Job]
    O --> E
```

## 9. For Glass_d0or Aut0_apply

- This automation runs as a standalone Python script and should be executed in a Python-compatible IDE (e.g., VS Code, PyCharm).
- pip install -r requirements.txt
- Have a fully completed Glass_d0or profile with CV and Phone number attached
- Most updated chrome browser is also required
- Set up a proxy account with Bright Data
  -Obtain host and port details, install ssl certificate and activate
  - Put in the proxy details in setup_proxy.py       
- Open the config.json and update with your credentials and search preferences 
- To activate the script run: python runner.py 
- For every succesful application, a csv for application tracking is automatically saved on the same folder
```bash
flowchart TD
    A1[Start Script] --> B1[User Inputs Glassdoor Credentials, Job Title, Location]
    B1 --> C1[Log in to Glassdoor]
    C1 --> D1[Enable Easy Apply Filter]
    D1 --> E1[Load Job Cards]
    E1 --> F1{Already Applied?}
    F1 -- Yes --> G1[Skip Job]
    F1 -- No --> H1[Open Job Application Page]
    H1 --> I1[Fill Out Application Form]
    I1 --> J1[Upload Resume & Documents]
    J1 --> K1[Answer Screening Questions]
    K1 --> L1[Review Application]
    L1 --> M1[Submit Application]
    M1 --> N1[Log Success to CSV]
    N1 --> O1[Move to Next Job]
    O1 --> E1
```

---

## 10. Project Structure

```
JobMate/
├── src/                  # Source code (Streamlit, utils, etc.)
├── resume/               # Resume data (mounted in container)
├── data/                 # Data files
├── logs/                 # Airflow logs
├── plugins/              # Airflow plugins
├── Dockerfile.streamlit  # Streamlit Dockerfile
├── docker-compose.yml    # Docker Compose config
├── sonar-project.properties # SonarQube configuration
├── run-sonar.sh         # SonarQube scanner script
├── .env                  # Environment variables
└── README.md             # This file
```

## 11. Environment Variables Reference

| Variable           | Description                        |
| ------------------ | ---------------------------------- |
| MONGODB_URI        | MongoDB connection string          |
| MONGODB_DB         | MongoDB database name              |
| MONGODB_COLLECTION | MongoDB collection name            |
| GEMINI_API_KEY     | Gemini API key                     |
| POSTGRES_USER      | Airflow/Postgres user              |
| POSTGRES_PASSWORD  | Airflow/Postgres password          |
| POSTGRES_DB        | Airflow/Postgres database          |
| SONAR_TOKEN        | SonarQube authentication token     |
| SONAR_PROJECT_KEY  | SonarQube project key identifier   |
| ENVIRONMENT        | App environment (development/prod) |
| DEBUG              | Debug mode (True/False)            |
| LOG_LEVEL          | Logging level (INFO/DEBUG/WARN)    |

---

## 12. Code Quality with SonarQube

This project includes SonarQube integration for code quality analysis. SonarQube helps identify bugs, code smells, and security vulnerabilities in your code.

To run a SonarQube analysis:

```bash
docker-compose run --rm sonar-scanner
```

The analysis results will be available on your SonarQube server at:
`https://sonarqube.nunchisolucoes.com/dashboard?id=JobMate`

For configuration details, see `sonar-project.properties` file. The scanner uses environment variables from your `.env` file.

## 11. Useful Commands

- View logs: `docker-compose logs <service>`
- Rebuild containers: `docker-compose up -d --build`
- Stop all: `docker-compose down`
- Remove all data: `docker-compose down -v`
- Run SonarQube analysis: `docker-compose run --rm sonar-scanner`

---

## License
This project is solely for personal or educational purposes only

## Authors
- Jennylynne Dominguez  
- Ricardo Tassio Dantas Da Silva  
- Bo Yang  
- Chaw Su Su Thin  
- Joyce Ann Murillo  
- Mugilmithran Kathiravan  
- Johan Rodriguez Rodriguez  
- Andres Felipe Santa Lozano  
- Hazel Portia Elaine Santos 

## Acknowledgements

This project was developed in faithful completion of:<br>
**Big Data Capstone Project**<br>
Lambton College, Mississauga<br>
**Course:** 2025S-T3_BDM 3035_01  <br>
**Professor:** Bhavik Gandhi



