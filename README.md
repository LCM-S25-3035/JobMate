
# JobMate 
## Auto Apply 2.0: Powered by JobMate

JobMate is a two-sided recruitment platform designed to streamline hiring for recruiters while supporting applicants with ATS-friendly resume optimization. Built on the foundational work of the AutoApply app, which focused on AI-based job recommendations and resume tailoring, JobMate extends functionality to include full recruiter-side tools and end-to-end applicant management.

### How the Previous App Worked :

# AutoApply

AutoApply is a resume/job matching and analysis platform powered by AI. It processes resumes and job descriptions, evaluates compatibility, and manages data using MongoDB, Streamlit, and Apache Airflow.

## Features
- Upload and analyze resumes and job descriptions (PDF)
- Extract and evaluate skills, experience, and compatibility
- Store and manage resumes in MongoDB
- Orchestrate data pipelines with Apache Airflow
- Modern UI with Streamlit

---

## Prerequisites
- [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/)
- (Optional) Python 3.9+ for local development
- Get Google Gemini API Key (https://ai.google.dev/gemini-api/docs/api-key)

---

## 1. Clone the Repository
```bash
git clone <your-repo-url>
cd AutoApply
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

---

## 8. Project Structure
```
AutoApply/
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

---

## 9. Environment Variables Reference
| Variable              | Description                        |
|-----------------------|------------------------------------|
| MONGODB_URI           | MongoDB connection string           |
| MONGODB_DB            | MongoDB database name               |
| MONGODB_COLLECTION    | MongoDB collection name             |
| GEMINI_API_KEY        | Gemini API key                      |
| POSTGRES_USER         | Airflow/Postgres user               |
| POSTGRES_PASSWORD     | Airflow/Postgres password           |
| POSTGRES_DB           | Airflow/Postgres database           |
| SONAR_TOKEN           | SonarQube authentication token      |
| SONAR_PROJECT_KEY     | SonarQube project key identifier    |
| ENVIRONMENT           | App environment (development/prod)  |
| DEBUG                 | Debug mode (True/False)             |
| LOG_LEVEL             | Logging level (INFO/DEBUG/WARN)     |

---

## 10. Code Quality with SonarQube

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
MIT
