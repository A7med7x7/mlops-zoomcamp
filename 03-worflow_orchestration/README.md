# NYC Taxi Duration Prediction - MLOps Zoomcamp

This project demonstrates a full MLOps workflow for predicting NYC taxi trip durations using XGBoost, MLflow, Hyperopt, and Airflow.

---

## 1. Environment Setup

### 1.1. Clone the Repository

```sh
git clone https://github.com/YOUR-USERNAME/mlops-zoomcamp.git
cd mlops-zoomcamp/03-worflow_orchestration
```

### 1.2. Create and Activate a Virtual Environment

```sh
python3 -m venv .venv
source .venv/bin/activate
```

### 1.3. Install Dependencies

```sh
pip install -r requirements.txt
```

If you don’t have a `requirements.txt`, use:

```sh
pip install pandas scikit-learn xgboost mlflow hyperopt apache-airflow
```

---

## 2. MLflow Tracking Server

### 2.1. Start MLflow UI

In a new terminal, run:

```sh
mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000
```

- Access the UI at [http://localhost:5000](http://localhost:5000)

---

## 3. Training the Model

### 3.1. Run the Training Script

```sh
python duration-prediction.py --year 2021 --month 1
```

- This will download the data, train the model, and log results to MLflow.

---

## 4. Airflow Orchestration

### 4.1. Initialize Airflow

```sh
export AIRFLOW_HOME=$(pwd)/airflow
airflow db init
```

### 4.2. Create an Airflow User

```sh
airflow users create \
    --username admin \
    --firstname FIRST_NAME \
    --lastname LAST_NAME \
    --role Admin \
    --email admin@example.com \
    --password admin
```

### 4.3. Place the DAG

Create a file `dags/train_duration_model_dag.py` with the following content:

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import sys
sys.path.append('/Users/alghali/Downloads/AI-Compeitions/mlops-zoomcamp/03-worflow_orchestration')
from duration_prediction import run

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
}

with DAG(
    dag_id='train_duration_model',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    tags=['mlops', 'taxi'],
) as dag:

    train_task = PythonOperator(
        task_id='train_model',
        python_callable=run,
        op_kwargs={'year': 2021, 'month': 1},
    )
```

- Adjust the `sys.path.append` to your actual script location if needed.

### 4.4. Start Airflow Webserver and Scheduler

```sh
airflow webserver --port 8080
# In another terminal
airflow scheduler
```

- Access the Airflow UI at [http://localhost:8080](http://localhost:8080)

---

## 5. Running the Pipeline

- In the Airflow UI, trigger the `train_duration_model` DAG.
- Monitor the run and check MLflow for experiment tracking.

---

## 6. Notes

- All experiment runs and artifacts are logged to `mlflow.db` and the `mlruns/` directory.
- You can change the year/month in the script or DAG as needed.
- Make sure all paths are correct for your environment.

---

## 7. Troubleshooting

- **MLflow UI not showing runs?**  
  Ensure you are using the same `mlflow.db` for both logging and the UI.
- **Airflow import errors?**  
  Check that `duration-prediction.py` is in your Python path or adjust `sys.path.append`.
- **Data download issues?**  
  Make sure you have internet access and the URLs are correct.

---

Happy MLOps!