from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
import subprocess

# Function to run external Python scripts
def run_script(script_path):
    subprocess.run(["python", script_path], check=True)

# Define the DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
}

dag = DAG(
    'job_data_pipeline',
    default_args=default_args,
    description='A DAG to orchestrate job scraping, cleaning, enrichment and storage',
    schedule_interval='@daily',  # Can be changed to manual or hourly
    catchup=False
)

# Define tasks
scrape_glassdoor = PythonOperator(
    task_id='scrape_glassdoor',
    python_callable=run_script,
    op_args=['src/data_gathering/GlassdoorDataGathering.py'],
    dag=dag
)

scrape_jobspy = PythonOperator(
    task_id='scrape_jobspy',
    python_callable=run_script,
    op_args=['src/data_gathering/JobSpy.py'],
    dag=dag
)


clean_data = PythonOperator(
    task_id='Cocatenate_clean_data',
    python_callable=run_script,
    op_args=['src/data_gathering/conc_clean.py'],
    dag=dag
)

translate_jobs = PythonOperator(
    task_id='translate_jobs',
    python_callable=run_script,
    op_args=['src/data_gathering/trans.py'],
    dag=dag
)

extract_skills = PythonOperator(
    task_id='extract_skills',
    python_callable=run_script,
    op_args=['src/data_gathering/job-description-skill-extract.py'],
    dag=dag
)

load_to_mongo = PythonOperator(
    task_id='load_to_mongo',
    python_callable=run_script,
    op_args=['src/data_gathering/load_jobs.py'],
    dag=dag
)

# Set dependencies
[scrape_glassdoor, scrape_jobspy] >> clean_data >> translate_jobs >> extract_skills >> load_to_mongo
