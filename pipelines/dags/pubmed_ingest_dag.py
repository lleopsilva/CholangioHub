import json
from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.providers.http.sensors.http import HttpSensor

default_args = {
    "owner": "cholangiohub",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="pubmed_ingest",
    default_args=default_args,
    start_date=datetime(2026, 7, 1),
    schedule_interval="@daily",
    catchup=False,
) as dag:

    wait_for_ingestion_service = HttpSensor(
        task_id="wait_for_ingestion_service",
        http_conn_id="ingestion_service",
        endpoint="/health",
        timeout=60,
        poke_interval=10,
        mode="reschedule",
    )

    trigger_ingest = SimpleHttpOperator(
        task_id="trigger_pubmed_ingest",
        http_conn_id="ingestion_service",
        endpoint="/ingest/pubmed",
        method="POST",
        data=json.dumps({"term": "cholangiocarcinoma", "limit": 10}),
        headers={"Content-Type": "application/json"},
    )

    wait_for_processing_service = HttpSensor(
        task_id="wait_for_processing_service",
        http_conn_id="processing_service",
        endpoint="/health",
        timeout=60,
        poke_interval=10,
        mode="reschedule",
    )

    process_silver = SimpleHttpOperator(
        task_id="process_silver",
        http_conn_id="processing_service",
        endpoint="/process/silver",
        method="POST",
        data=json.dumps({}),
        headers={"Content-Type": "application/json"},
    )

    process_gold = SimpleHttpOperator(
        task_id="process_gold",
        http_conn_id="processing_service",
        endpoint="/process/gold",
        method="POST",
        data=json.dumps({}),
        headers={"Content-Type": "application/json"},
    )

    # Chain tasks explicitly on separate lines to respect line-length rules
    wait_for_ingestion_service >> trigger_ingest
    trigger_ingest >> wait_for_processing_service
    wait_for_processing_service >> process_silver
    process_silver >> process_gold
