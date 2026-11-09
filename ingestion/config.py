"""Project settings, read once from the environment (.env file)."""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Bank Al-Maghrib API
BAM_API_KEY = os.getenv("BAM_API_KEY", "")
BAM_BASE_URL = "https://api.centralbankofmorocco.ma/cours/Version1/api"
BAM_ENDPOINTS = ["CoursBBE", "CoursVirement"]  # banknote rates, transfer rates

# Free plan rate limit
SECONDS_BETWEEN_CALLS = 15
MAX_RETRIES = 3

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "bam"


def get_logger(name: str) -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-7s  %(name)s  %(message)s",
    )
    return logging.getLogger(name)
