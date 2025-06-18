# File: src/AirflowDAG/dags/job_pipeline_dag.py

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

from AirflowDAG.utils.scrape_glassdoor import scrape_glassdoor
from AirflowDAG.utils.scrape_jobspy import scrape_jobspy
from AirflowDAG.utils.concat_clean import Cocatenate_clean_data
from AirflowDAG.utils.translate_jobs import translate_jobs
from AirflowDAG.utils.extract_skills import extract_skills
from AirflowDAG.utils.load_to_mongo import load_to_mongo
from AirflowDAG.utils.ghost_job_detector import detect_ghost_jobs

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

dag = DAG(
    'job_pipeline',
    default_args=default_args,
    description='A DAG to orchestrate job scraping, cleaning, enrichment and storage',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
)

# Define tasks
scrape_glassdoor_task = PythonOperator(
    task_id='scrape_glassdoor',
    python_callable=scrape_glassdoor,
    dag=dag,
)

scrape_jobspy_task = PythonOperator(
    task_id='scrape_jobspy',
    python_callable=scrape_jobspy,
    dag=dag,
)

concat_clean_task = PythonOperator(
    task_id='Cocatenate_clean_data',
    python_callable=Cocatenate_clean_data,
    dag=dag,
)

translate_jobs_task = PythonOperator(
    task_id='translate_jobs',
    python_callable=translate_jobs,
    dag=dag,
)

extract_skills_task = PythonOperator(
    task_id='extract_skills',
    python_callable=extract_skills,
    dag=dag,
)

load_to_mongo_task = PythonOperator(
    task_id='load_to_mongo',
    python_callable=load_to_mongo,
    dag=dag,
)

detect_ghost_jobs_task = PythonOperator(
    task_id='detect_ghost_jobs',
    python_callable=detect_ghost_jobs,
    dag=dag,
)

# Define task dependencies
[scrape_glassdoor_task, scrape_jobspy_task] >> concat_clean_task
concat_clean_task >> translate_jobs_task >> extract_skills_task >> load_to_mongo_task >> detect_ghost_jobs_task
