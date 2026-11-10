"""HTTP client for the Bank Al-Maghrib exchange rates API."""

import time
from datetime import date

import requests

from ingestion.config import BAM_API_KEY, BAM_BASE_URL, MAX_RETRIES, get_logger

log = get_logger(__name__)

# Network problems worth retrying (internet drop, slow server)
RETRYABLE_ERRORS = (requests.ConnectionError, requests.Timeout)


def fetch_rates(endpoint: str, day: date) -> list[dict]:
    """Return the rates of one endpoint for one day.

    Retries with a longer wait each time when the rate limit (HTTP 429)
    is hit or the network fails.
    """
    url = f"{BAM_BASE_URL}/{endpoint}"
    headers = {"Ocp-Apim-Subscription-Key": BAM_API_KEY}
    params = {"date": day.isoformat()}

    for attempt in range(1, MAX_RETRIES + 1):
        wait = 60 * attempt  # 60s, then 120s, then 180s

        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
        except RETRYABLE_ERRORS as error:
            log.warning(
                "%s %s: network error (%s), waiting %ss (attempt %s/%s)",
                endpoint,
                day,
                type(error).__name__,
                wait,
                attempt,
                MAX_RETRIES,
            )
            time.sleep(wait)
            continue

        if response.status_code == 429:
            log.warning(
                "%s %s: rate limit hit, waiting %ss (attempt %s/%s)",
                endpoint,
                day,
                wait,
                attempt,
                MAX_RETRIES,
            )
            time.sleep(wait)
            continue

        response.raise_for_status()  # stops on any other error (401, 500...)
        return response.json()

    raise RuntimeError(f"{endpoint} {day}: failed after {MAX_RETRIES} attempts")
