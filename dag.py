import requests
from bs4 import BeautifulSoup
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import os
from google_drive_downloader import GoogleDriveDownloader as gdd
from dvc.api import make_checkpoint, commit
import subprocess

# Define sources and data paths
sources = ['https://www.dawn.com/', 'https://www.bbc.com/']
google_drive_file_id = '1smA1d0VUOrWufEeAYE1y_xbSENZY0Pul'

# Function to extract data from websites
def extract(data_path):
    try:
        extracted_data = []
        for source in sources:
            reqs = requests.get(source)
            reqs.raise_for_status()  # Raise exception for HTTP errors
            soup = BeautifulSoup(reqs.text, 'html.parser')
            for article in soup.find_all('article'):
                title = article.find('h3').text.strip()
                description = article.find('p').text.strip()
                extracted_data.append({'source': source, 'title': title, 'description': description})
        return extracted_data
    except Exception as e:
        print(f"Error during data extraction: {e}")
        raise e  # Reraise the exception to Airflow for task failure

# Function to preprocess and clean data
def transform(data_path, **kwargs):
    try:
        ti = kwargs['ti']
        extracted_data = ti.xcom_pull(task_ids='extract_data')
        df = pd.DataFrame(extracted_data)
        return df
    except Exception as e:
        print(f"Error during data transformation: {e}")
        raise e

# Function to store data on Google Drive and track versions with DVC
def store_and_version_data(data_path, google_drive_file_id, **kwargs):
    try:
        ti = kwargs['ti']
        df = ti.xcom_pull(task_ids='transform_data')

        # Store data as CSV on Google Drive
        file_name = 'processed_data.csv'
        df.to_csv(os.path.join(data_path, file_name), index=False)
        gdd.download_file_from_google_drive(file_id=google_drive_file_id, dest_path=os.path.join(data_path, file_name))

        # Version control with DVC
        make_checkpoint(data_path, data_path)
        commit(data_path, file_name, push=True)
    except Exception as e:
        print(f"Error during data storage and versioning: {e}")
        raise e

# Define the task to track changes with DVC
def dvc_add(data_path):
    try:
        subprocess.run(["dvc", "add", os.path.join(data_path, "processed_data.csv")], check=True)
        print("Data added with DVC")
    except subprocess.CalledProcessError as e:
        print(f"Error during DVC add operation: {e}")
        raise e

# Define the task to commit and push the DVC file hash to GitHub
def git_commit_push(checkpoint_path):
    try:
        subprocess.run(["git", "add", os.path.join(checkpoint_path, "processed_data.csv.dvc")], check=True)
        subprocess.run(["git", "commit", "-m", "Update DVC files"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("DVC file pushed to GitHub")
    except subprocess.CalledProcessError as e:
        print(f"Error during Git commit and push: {e}")
        raise e

# Define the task to push data to DVC remote
def dvc_push():
    try:
        subprocess.run(["dvc", "commit"], check=True)
        subprocess.run(["dvc", "push"], check=True)
        print("Data pushed to remote DVC storage")
    except subprocess.CalledProcessError as e:
        print(f"Error during DVC commit and push: {e}")
        raise e

# Default arguments for the Airflow DAG
default_args = {
    'owner': 'Hasham',
    'start_date': datetime(2024, 2, 2),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the Airflow DAG
dag = DAG(
    'mlops_dag',
    default_args=default_args,
    description='Automate data extraction, transformation, and storage with Apache Airflow',
    schedule_interval='@daily',  
)

# Define tasks for each step in the workflow
task_extract = PythonOperator(
    task_id='extract_data',
    python_callable=extract,
    op_kwargs={'data_path': data_path},
    dag=dag,
)

task_transform = PythonOperator(
    task_id='transform_data',
    python_callable=transform,
    op_kwargs={'data_path': data_path},
    provide_context=True,
    dag=dag,
)

task_store_and_version = PythonOperator(
    task_id='store_and_version_data',
    python_callable=store_and_version_data,
    op_kwargs={'data_path': data_path, 'google_drive_file_id': google_drive_file_id},
    provide_context=True,
    dag=dag,
)

task_dvc_add = PythonOperator(
    task_id='dvc_add',
    python_callable=dvc_add,
    op_kwargs={'data_path': data_path},
    dag=dag,
)

task_git_commit_push = PythonOperator(
    task_id='git_commit_push',
    python_callable=git_commit_push,
    op_kwargs={'checkpoint_path': data_path},
    dag=dag,
)

task_dvc_push = PythonOperator(
    task_id='dvc_push',
    python_callable=dvc_push,
    dag=dag,
)

# Define task dependencies
task_extract >> task_transform >> task_store_and_version >> task_dvc_add >> task_git_commit_push >> task_dvc_push
