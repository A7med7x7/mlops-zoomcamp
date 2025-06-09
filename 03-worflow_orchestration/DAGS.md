## 4.3. Introduction to Airflow DAGs: Placing and Understanding Your First DAG

### What is an Airflow DAG?

An **Airflow DAG** (Directed Acyclic Graph) is a Python script that defines a workflow as a set of tasks and their dependencies. Each DAG describes how to run your data pipeline, when to run it, and what steps (tasks) are involved.

---

### Basic Airflow DAG Syntax

A minimal Airflow DAG looks like this:

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def my_task():
    print("Hello from Airflow!")

with DAG(
    dag_id="my_first_dag",
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,  # Set to a cron string for scheduling
    catchup=False,
) as dag:
    task = PythonOperator(
        task_id="print_hello",
        python_callable=my_task,
    )
```

- **DAG**: The workflow definition.
- **Task**: A unit of work (here, a Python function).
- **Operators**: Define what each task does (e.g., `PythonOperator` runs Python code).

---

### How to Place Your DAG

1. **Find your Airflow DAGs folder**  
   By default, this is `$AIRFLOW_HOME/dags/`.  
   If you followed earlier steps, it’s likely at `mlops-zoomcamp/03-worflow_orchestration/airflow/dags/`.

2. **Create a new Python file**  
   For example:  
   ```
   mlops-zoomcamp/03-worflow_orchestration/airflow/dags/train_duration_model_dag.py
   ```

3. **Paste the following DAG code**  
   This DAG will run your taxi duration training script for a given year and month:

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
       schedule_interval=None,  # Set to a cron string for scheduling
       catchup=False,
       tags=['mlops', 'taxi'],
   ) as dag:

       train_task = PythonOperator(
           task_id='train_model',
           python_callable=run,
           op_kwargs={'year': 2021, 'month': 1},  # Change as needed
       )
   ```

   - **`sys.path.append(...)`**: Ensures Airflow can import your script.
   - **`python_callable=run`**: Calls your training function.
   - **`op_kwargs`**: Passes arguments to your function.

---

### How to Run Your DAG

1. **Start Airflow webserver and scheduler**  
   ```sh
   airflow webserver --port 8080
   # In another terminal
   airflow scheduler
   ```

2. **Open the Airflow UI**  
   Go to [http://localhost:8080](http://localhost:8080) in your browser.

3. **Find and trigger your DAG**  
   - Look for `train_duration_model` in the list.
   - Turn it on and click the "play" button to trigger a run.

---

### Tips

- You can schedule your DAG by changing `schedule_interval` (e.g., `"@daily"`).
- You can add more tasks and dependencies by defining more operators and using `task1 >> task2` syntax.
- For more advanced workflows, see the [Airflow documentation](https://airflow.apache.org/docs/).

---

**Congratulations!**  
You’ve now learned how to create, place, and run your first Airflow DAG for ML workflows.
