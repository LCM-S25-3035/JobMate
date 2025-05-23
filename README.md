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
| ENVIRONMENT           | App environment (development/prod)  |
| DEBUG                 | Debug mode (True/False)             |
| LOG_LEVEL             | Logging level (INFO/DEBUG/WARN)     |

---

## 10. Useful Commands
- View logs: `docker-compose logs <service>`
- Rebuild containers: `docker-compose up -d --build`
- Stop all: `docker-compose down`
- Remove all data: `docker-compose down -v`

---

## License
MIT
