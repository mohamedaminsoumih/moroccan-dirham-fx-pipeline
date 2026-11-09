"""PostgreSQL connection helpers."""

import os
from pathlib import Path
from typing import LiteralString, cast

import psycopg
from dotenv import load_dotenv

load_dotenv()


def get_connection() -> psycopg.Connection:
    """Open a connection using the settings in .env.

    autocommit=True: each `with conn.transaction()` block is committed
    on its own, so one bad file doesn't cancel the others.
    """
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", ""),
        user=os.getenv("POSTGRES_USER", ""),
        password=os.getenv("POSTGRES_PASSWORD", ""),
        autocommit=True,
    )


def run_sql_file(conn: psycopg.Connection, path: Path) -> None:
    """Execute all the statements of a .sql file from this project.

    The cast is safe: the file is part of the code, not user input.
    """
    query = cast(LiteralString, path.read_text(encoding="utf-8"))
    conn.execute(query)
