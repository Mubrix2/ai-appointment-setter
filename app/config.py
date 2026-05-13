# app/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _require(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(f"Required env variable '{key}' is not set.")
    return value


# LLM
GROQ_API_KEY: str = _require("GROQ_API_KEY")
LLM_MODEL: str = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")

# Cal.com
CAL_API_KEY: str = os.getenv("CAL_API_KEY", "")
CAL_USERNAME: str = os.getenv("CAL_USERNAME", "")
CAL_EVENT_TYPE_ID: str = os.getenv("CAL_EVENT_TYPE_ID", "")

# n8n
N8N_BOOKING_WEBHOOK_URL: str = os.getenv("N8N_BOOKING_WEBHOOK_URL", "")

# Airtable
AIRTABLE_API_KEY: str = os.getenv("AIRTABLE_API_KEY", "")
AIRTABLE_BASE_ID: str = os.getenv("AIRTABLE_BASE_ID", "")
AIRTABLE_TABLE_NAME: str = os.getenv("AIRTABLE_TABLE_NAME", "Appointments")

# App
APP_ENV: str = os.getenv("APP_ENV", "development")