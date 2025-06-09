from airflow import DAG 
from airflow.operators.python import PythonOperator
from datetime import datetime 
import sys 
#03-worflow_orchestration/training_pipeline //Users/alghali/Downloads/AI-Compeitions/mlops-zoomcamp/03-worflow_orchestration/dags/training_pipeline/duration-prediction.py
from training_pipeline.duration_prediction import run 

sys.path.append("/Users/alghali/Downloads/AI-Compeitions/mlops-zoomcamp/03-worflow_orchestration")
 
default_args=  {
    'owner' : 'ahmed alghali',
    'start_date' : datetime(2025,6,9)
}

with DAG(
    dag_id= 'train_duration_model',
    default_args = default_args,
    catchup = False,
    tags = ['mlops', 'taxi']
    
) as dag: 
    train_task = PythonOperator(
        task_id = 'train_model',
        python_callable=run,
        op_kwargs={'year': 2021, 'month': 1}
    )
    