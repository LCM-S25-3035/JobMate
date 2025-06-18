import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RESUME_DIR = BASE_DIR / "resume"
PARQUET_DIR = BASE_DIR / "parquet"

# MongoDB Configuration
MONGODB_CONFIG = {
    "uri": os.getenv("MONGODB_URI"),
    "db_name": os.getenv("MONGODB_NAME", "jobsDB"),
    "jobs_collection": os.getenv("MONGODB_JOBS_COLLECTION", "jobsCollection")
}

# Google Gemini Configuration
GEMINI_CONFIG = {
    "api_key": os.getenv("GEMINI_API_KEY"),
    "model": os.getenv("GEMINI_MODEL", "models/gemini-2.0-flash")
}

# AI Model Configuration
AI_CONFIG = {
    "embedding_model": os.getenv("EMBEDDING_MODEL", "all-mpnet-base-v2")
}

# File Paths
FILE_PATHS = {
    "parquet_file": os.getenv("PARQUET_FILE_PATH", str(PARQUET_DIR / "jobs_data.parquet")),
    "resume_json": os.getenv("RESUME_JSON_PATH", str(RESUME_DIR / "resume.json")),
    "resume_final": os.getenv("RESUME_FINAL_PATH", str(RESUME_DIR / "resume_final_to_word.json"))
}

# Application Configuration
APP_CONFIG = {
    "environment": os.getenv("ENVIRONMENT", "development"),
    "debug": os.getenv("DEBUG", "True").lower() == "true",
    "log_level": os.getenv("LOG_LEVEL", "INFO")
}

# Airflow Configuration
AIRFLOW_CONFIG = {
    "home": os.getenv("AIRFLOW_HOME"),
    "db_conn": os.getenv("AIRFLOW_DB_CONN")
}

def validate_config():
    """Validate required environment variables are set."""
    required_vars = {
        "MONGODB_URI": MONGODB_CONFIG["uri"],
        "GEMINI_API_KEY": GEMINI_CONFIG["api_key"]
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    if missing_vars:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )