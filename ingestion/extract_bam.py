"""Extract Bank Al-Maghrib exchange rates into the raw layer.

Usage:
    python -m ingestion.extract_bam                         # today
    python -m ingestion.extract_bam 2026-11-05              # one day
    python -m ingestion.extract_bam 2026-10-01 2026-11-05   # date range
"""

import argparse
import sys
import time
from datetime import date

from ingestion.bam_client import fetch_rates
from ingestion.config import (
    BAM_API_KEY,
    BAM_ENDPOINTS,
    SECONDS_BETWEEN_CALLS,
    get_logger,
)
from ingestion.dates import business_days
from ingestion.storage import is_already_saved, save_raw

log = get_logger(__name__)


def parse_args() -> tuple[date, date]:
    parser = argparse.ArgumentParser(description="Extract BAM exchange rates.")
    parser.add_argument(
        "start",
        nargs="?",
        type=date.fromisoformat,
        default=date.today(),
    )
    parser.add_argument("end", nargs="?", type=date.fromisoformat)
    args = parser.parse_args()
    return args.start, args.end or args.start


def extract(start: date, end: date) -> None:
    counts = {"saved": 0, "empty": 0, "skipped": 0}
    first_call = True

    for day in business_days(start, end):
        for endpoint in BAM_ENDPOINTS:
            if is_already_saved(endpoint, day):
                log.info("%s %s: already saved, skipping", endpoint, day)
                counts["skipped"] += 1
                continue

            if not first_call:
                time.sleep(SECONDS_BETWEEN_CALLS)
            first_call = False

            rows = fetch_rates(endpoint, day)

            if not rows and day >= date.today():
                # Not published yet: don't save, so the next run retries
                log.info("%s %s: not published yet, will retry", endpoint, day)
                counts["empty"] += 1
                continue

            save_raw(endpoint, day, rows)

            if rows:
                log.info("%s %s: %s rows saved", endpoint, day, len(rows))
                counts["saved"] += 1
            else:
                log.info("%s %s: no rates published (holiday?)", endpoint, day)
                counts["empty"] += 1

    log.info("Done. %s", counts)


def main() -> None:
    if not BAM_API_KEY:
        sys.exit("BAM_API_KEY is missing. Add it to the .env file.")

    start, end = parse_args()
    log.info("Extracting Bank Al-Maghrib rates from %s to %s", start, end)
    extract(start, end)


if __name__ == "__main__":
    main()
