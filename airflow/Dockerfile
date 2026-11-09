FROM apache/airflow:3.3.2-python3.12

# Libraries used by our ingestion and loading code
RUN pip install --no-cache-dir \
    "python-dotenv>=1.0,<2" \
    "psycopg[binary]>=3.2,<4"

# dbt in its own virtual environment,
# so its dependencies don't conflict with Airflow's
RUN python -m venv /home/airflow/dbt_venv \
 && /home/airflow/dbt_venv/bin/pip install --no-cache-dir \
    "dbt-core==1.12.6" \
    "dbt-postgres==1.11.0"
