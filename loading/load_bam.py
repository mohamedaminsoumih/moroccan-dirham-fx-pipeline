"""Load raw Bank Al-Maghrib JSON files into PostgreSQL (raw.bam_rates).

Each file is loaded in its own transaction. Old rows for the same
endpoint and date are deleted first, so running it twice is safe.

Usage:
    python -m loading.load_bam
"""

import json
from pathlib import Path

import psycopg
from psycopg.types.json import Jsonb

from ingestion.config import PROJECT_ROOT, RAW_DIR, get_logger
from loading.db import get_connection, run_sql_file

log = get_logger(__name__)

DDL_FILE = PROJECT_ROOT / "sql" / "create_raw_tables.sql"

DELETE_SQL = """
    DELETE FROM raw.bam_rates
    WHERE endpoint = %s AND rate_date = %s
"""

INSERT_SQL = """
    INSERT INTO raw.bam_rates
        (endpoint, rate_date, payload, extracted_at, source_file)
    VALUES (%s, %s, %s, %s, %s)
"""


def load_file(conn: psycopg.Connection, path: Path) -> int:
    """Replace the rows of one endpoint/date with the content of one file."""
    data = json.loads(path.read_text(encoding="utf-8"))
    endpoint, day = data["endpoint"], data["date"]
    source_file = str(path.relative_to(PROJECT_ROOT))

    records = [
        (endpoint, day, Jsonb(row), data["extracted_at"], source_file)
        for row in data["rows"]
    ]

    with conn.transaction():
        conn.execute(DELETE_SQL, (endpoint, day))
        with conn.cursor() as cur:
            cur.executemany(INSERT_SQL, records)

    return len(records)


def main() -> None:
    files = sorted(RAW_DIR.glob("*/*.json"))
    log.info("Found %s raw files", len(files))

    with get_connection() as conn:
        run_sql_file(conn, DDL_FILE)
        total = sum(load_file(conn, path) for path in files)

    log.info("Done. %s rows loaded into raw.bam_rates", total)


if __name__ == "__main__":
    main()
