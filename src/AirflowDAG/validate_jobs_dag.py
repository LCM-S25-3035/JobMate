# src/AirflowDAG/validate_jobs_dag.py

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

def validate_jobs_collection():
    mongo_uri = os.getenv("MONGO_URI", "mongodb://mongodb:27017")
    db_name = os.getenv("MONGO_DB", "jobmate")
    collection_name = os.getenv("MONGO_COLLECTION", "jobs")
    report_lines = []

    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    jobs = list(collection.find())
    report_lines.append(f"✅ Total jobs found: {len(jobs)}")

    if not jobs:
        raise ValueError("❌ No documents found in the 'jobs' collection.")

    required_fields = ["title", "company", "description"]
    missing_summary = {field: 0 for field in required_fields}

    for job in jobs:
        for field in required_fields:
            if not job.get(field):
                missing_summary[field] += 1

    for field, count in missing_summary.items():
        report_lines.append(f"⚠️ Jobs missing '{field}': {count}")

    sample = jobs[0]
    report_lines.append("\n🧪 Sample Job:\n" + str(sample))

    with open("/tmp/mongo_jobs_validation.log", "w") as f:
        f.write("\n".join(report_lines))

    print("\n".join(report_lines))
    client.close()

default_args = {
    'start_date': datetime(2024, 1, 1),
    'catchup': False
}

with DAG(
    dag_id="validate_jobs_collection",
    schedule_interval=None,
    default_args=default_args,
    description="Checks MongoDB jobs collection for data integrity",
    tags=["mongo", "validation"],
) as dag:
    
    validate_task = PythonOperator(
        task_id="validate_jobs",
        python_callable=validate_jobs_collection
    )
