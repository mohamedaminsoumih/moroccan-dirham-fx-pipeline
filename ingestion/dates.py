"""Date helpers."""

from collections.abc import Iterator
from datetime import date, timedelta


def business_days(start: date, end: date) -> Iterator[date]:
    """Yield Monday to Friday dates (no rates are published on weekends)."""
    day = start
    while day <= end:
        if day.weekday() < 5:  # 0 = Monday ... 4 = Friday
            yield day
        day += timedelta(days=1)
