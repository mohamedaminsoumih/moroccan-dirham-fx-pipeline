"""Daily pipeline: Bank Al-Maghrib API → raw JSON → PostgreSQL → dbt.

Runs Monday to Friday at 13:00 (Morocco time), after the transfer
rates are published at 12:30.
"""

from datetime import timedelta

import pendulum
from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import DAG, chain

PROJECT_DIR = "/opt/airflow/project"
DBT = "/home/airflow/dbt_venv/bin/dbt"
DBT_ARGS = (
    f"--project-dir {PROJECT_DIR}/transform " f"--profiles-dir {PROJECT_DIR}/transform"
)

# Re-check the last 7 days: catches late or missing publications.
# Days already saved are skipped, so this costs almost no API calls.
EXTRACT_CMD = (
    f"cd {PROJECT_DIR} && "
    "python -m ingestion.extract_bam "
    "$(date -d '7 days ago' +%F) $(date +%F)"
)

default_args = {
    "owner": "amin",
    "retries": 2,
    "retry_delay": timedelta(minutes=10),
}

with DAG(
    dag_id="bam_exchange_rates_daily",
    description="Bank Al-Maghrib exchange rates: extract, load, transform.",
    schedule="0 13 * * 1-5",
    start_date=pendulum.datetime(2026, 11, 1, tz="Africa/Casablanca"),
    catchup=False,
    max_active_runs=1,  # never 2 runs at once (API rate limit)
    default_args=default_args,
    tags=["bank-al-maghrib", "exchange-rates"],
):
    extract = BashOperator(
        task_id="extract",
        bash_command=EXTRACT_CMD,
    )

    load = BashOperator(
        task_id="load",
        bash_command=f"cd {PROJECT_DIR} && python -m loading.load_bam",
    )

    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=f"{DBT} deps {DBT_ARGS} && {DBT} build {DBT_ARGS}",
    )

    dbt_freshness = BashOperator(
        task_id="dbt_source_freshness",
        bash_command=f"{DBT} source freshness {DBT_ARGS}",
    )

    chain(extract, load, dbt_build, dbt_freshness)
