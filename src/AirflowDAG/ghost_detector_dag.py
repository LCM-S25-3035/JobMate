# src/AirflowDAG/ghost_detector_dag.py

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import os
import json
import pandas as pd
from pymongo import MongoClient
from bson.json_util import dumps

# Make sure ghost detection logic is importable
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'streamlit_app')))
from ghost_core import hybrid_detect_ghost_jobs


def fetch_jobs_from_mongo():
    mongo_host = os.getenv("MONGO_URI", "mongodb://mongodb:27017")
    mongo_user = os.getenv("MONGODB_USER")
    mongo_pass = os.getenv("MONGODB_PASSWORD")
    mongo_db = os.getenv("MONGO_DB", "autoapply")
    mongo_collection = os.getenv("MONGO_COLLECTION", "resumes")

    mongo_uri = f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host.split('//')[1]}"

    client = MongoClient(mongo_uri)
    collection = client[mongo_db][mongo_collection]
    jobs = list(collection.find({}))
    if not jobs:
        raise ValueError("No jobs found in MongoDB collection.")

    with open('/tmp/fetched_jobs.json', 'w') as f:
        f.write(dumps(jobs))

    client.close()


def run_ghost_detection():
    with open('/tmp/fetched_jobs.json') as f:
        jobs_data = json.load(f)

    clean_jobs = []
    for j in jobs_data:
        clean_jobs.append({
            'title': j.get('title', ''),
            'company': j.get('company', ''),
            'description': j.get('description', ''),
            'salary': j.get('salary', ''),
            'url': j.get('url', ''),
            'posted_at': j.get('posted_at', datetime.utcnow().isoformat()),
            'contact_email': j.get('contact_email', '')
        })

    results = hybrid_detect_ghost_jobs(clean_jobs)
    df = pd.DataFrame(results)
    df.to_csv('/tmp/ghost_detection_results.csv', index=False)


default_args = {
    'start_date': datetime(2024, 1, 1),
    'catchup': False
}

with DAG(
    dag_id='ghost_job_detector',
    schedule_interval='@daily',
    default_args=default_args,
    description='DAG to detect ghost job postings from MongoDB',
    tags=['ghost_jobs'],
) as dag:

    fetch_task = PythonOperator(
        task_id='fetch_jobs',
        python_callable=fetch_jobs_from_mongo
    )

    detect_task = PythonOperator(
        task_id='detect_ghost_jobs',
        python_callable=run_ghost_detection
    )

    fetch_task >> detect_task
