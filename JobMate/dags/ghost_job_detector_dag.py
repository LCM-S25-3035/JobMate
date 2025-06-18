from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pymongo
import os

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def get_mongo_collection():
    mongo_uri = os.getenv("MONGO_URI") or os.getenv("MONGODB_URI")
    client = pymongo.MongoClient(mongo_uri)
    db = client[os.getenv("MONGO_DB", "autoapply")]
    return db[os.getenv("MONGO_COLLECTION", "resumes")]

def fetch_jobs(**context):
    collection = get_mongo_collection()
    jobs = list(collection.find().sort("date", -1).limit(100))
    context['ti'].xcom_push(key='jobs', value=jobs)

def detect_ghost_jobs(**context):
    jobs = context['ti'].xcom_pull(key='jobs', task_ids='fetch_jobs')
    ghost_jobs = []
    now = datetime.utcnow()

    for job in jobs:
        reasons = []
        if not job.get("description") or len(job["description"]) < 50:
            reasons.append("Short or missing description")
        if "date" in job and isinstance(job["date"], datetime):
            if job["date"] < now - timedelta(days=90):
                reasons.append("Posted over 90 days ago")
        else:
            reasons.append("Missing/invalid date")

        if reasons:
            job["ghost_reasons"] = reasons
            ghost_jobs.append(job)

    for g in ghost_jobs:
        print(f"[GHOST] {g.get('title', 'Untitled')} @ {g.get('company', 'Unknown')} — Reasons: {g['ghost_reasons']}")

with DAG(
    'ghost_job_detector',
    default_args=default_args,
    description='Detect ghost jobs from MongoDB',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['jobs', 'mongodb', 'ghost'],
) as dag:

    t1 = PythonOperator(
        task_id='fetch_jobs',
        python_callable=fetch_jobs,
        provide_context=True,
    )

    t2 = PythonOperator(
        task_id='detect_ghost_jobs',
        python_callable=detect_ghost_jobs,
        provide_context=True,
    )

    t1 >> t2
