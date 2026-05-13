# app/services/notification_service.py
import logging
import requests
from app.config import (
    N8N_BOOKING_WEBHOOK_URL,
    AIRTABLE_API_KEY,
    AIRTABLE_BASE_ID,
    AIRTABLE_TABLE_NAME,
)
from datetime import datetime

logger = logging.getLogger(__name__)


def trigger_booking_webhook(booking: dict, notes: str = "") -> bool:
    """
    Notify n8n about a confirmed booking.
    n8n then sends the confirmation email and updates Airtable.
    Returns True if webhook was triggered successfully.
    """
    if not N8N_BOOKING_WEBHOOK_URL:
        logger.warning("n8n webhook not configured — skipping notification")
        return False

    payload = {
        "booking_id": booking.get("booking_id"),
        "name": booking.get("name"),
        "email": booking.get("email"),
        "start_time": booking.get("start_time"),
        "meeting_url": booking.get("meeting_url"),
        "status": booking.get("status"),
        "notes": notes,
        "triggered_at": datetime.utcnow().isoformat(),
    }

    try:
        response = requests.post(
            N8N_BOOKING_WEBHOOK_URL,
            json=payload,
            timeout=10,
        )
        response.raise_for_status()
        logger.info(f"n8n webhook triggered for booking {booking.get('booking_id')}")
        return True
    except Exception as e:
        logger.error(f"n8n webhook failed: {e}")
        return False


def save_booking_to_airtable(booking: dict, notes: str = "") -> str:
    """Save confirmed booking to Airtable appointments table."""
    if not AIRTABLE_API_KEY:
        logger.warning("Airtable not configured — skipping save")
        return "not_configured"

    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "fields": {
            "Name": booking.get("name", ""),
            "Email": booking.get("email", ""),
            "Booking ID": booking.get("booking_id", ""),
            "Start Time": booking.get("start_time", "")[:10],
            "Status": "Confirmed",
            "Meeting URL": booking.get("meeting_url", ""),
            "Notes": notes,
        }
    }

    try:
        response = requests.post(
            url, json=payload, headers=headers, timeout=10
        )
        if response.status_code != 200:
            logger.error(f"Airtable error: {response.text}")
            return "save_failed"

        record_id = response.json().get("id", "unknown")
        logger.info(f"Booking saved to Airtable: {record_id}")
        return record_id

    except Exception as e:
        logger.error(f"Airtable save failed: {e}")
        return "save_failed"