"""Save raw API responses as JSON files (raw layer)."""

import json
from datetime import date, datetime
from pathlib import Path

from ingestion.config import RAW_DIR


def raw_file_path(endpoint: str, day: date) -> Path:
    return RAW_DIR / endpoint / f"{day.isoformat()}.json"


def is_already_saved(endpoint: str, day: date) -> bool:
    return raw_file_path(endpoint, day).exists()


def save_raw(endpoint: str, day: date, rows: list[dict]) -> Path:
    """Write the rows, plus metadata about the extraction."""
    path = raw_file_path(endpoint, day)
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "source": "bank_al_maghrib",
        "endpoint": endpoint,
        "date": day.isoformat(),
        "extracted_at": datetime.now().isoformat(timespec="seconds"),
        "row_count": len(rows),
        "rows": rows,
    }
    content = json.dumps(payload, ensure_ascii=False, indent=2)
    path.write_text(content, encoding="utf-8")
    return path
