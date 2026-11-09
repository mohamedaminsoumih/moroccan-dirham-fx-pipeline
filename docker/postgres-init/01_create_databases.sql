-- Runs only the first time PostgreSQL starts (empty data volume).
-- Creates the databases used by Airflow and Metabase for their own settings.

CREATE DATABASE airflow;
CREATE DATABASE metabase;
