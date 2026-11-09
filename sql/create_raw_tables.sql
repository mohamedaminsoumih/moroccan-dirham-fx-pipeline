-- Raw layer: data stored exactly as received from the source.
-- Each API row is kept as JSON; cleaning happens later in dbt.

CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.bam_rates (
    endpoint      TEXT       NOT NULL,  -- CoursBBE or CoursVirement
    rate_date     DATE       NOT NULL,  -- day the rates are for
    payload       JSONB      NOT NULL,  -- one row of the API response
    extracted_at  TIMESTAMP  NOT NULL,  -- when the API was called
    source_file   TEXT       NOT NULL,  -- JSON file it came from
    loaded_at     TIMESTAMP  NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_bam_rates_endpoint_date
    ON raw.bam_rates (endpoint, rate_date);
