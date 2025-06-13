from airflow import DAG
import pendulum
from airflow.operators.python import PythonOperator
from datetime import timedelta
import sys
import os

# Add your scripts directory to sys.path so you can import your scraper
sys.path.insert(0, "/opt/airflow/scripts")

from job_scraper import main as run_job_scraper  # Import the main function


default_args = {
    'owner': 'mugilmithran',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='job_scraper_dag',
    default_args=default_args,
    schedule='0 11 * * 1', # Every Monday at 11:00 AM
    start_date=pendulum.datetime(2025, 6, 8),
    catchup=False,
    tags=['job-scraper'],
) as dag:

    scrape_and_upload = PythonOperator(
        task_id='scrape_and_upload_to_mongo',
        python_callable=run_job_scraper,
    )

    scrape_and_upload