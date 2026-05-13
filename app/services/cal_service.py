# app/services/cal_service.py
import logging
from datetime import datetime, timedelta
import requests
from app.config import CAL_API_KEY, CAL_USERNAME, CAL_EVENT_TYPE_ID

logger = logging.getLogger(__name__)

CAL_BASE_URL = "https://api.cal.com/v2"
CAL_HEADERS = {
    "Authorization": f"Bearer {CAL_API_KEY}",
    "cal-api-version": "2024-06-14",
    "Content-Type": "application/json",
}


def get_available_slots(days_ahead: int = 7) -> list[dict]:
    """
    Fetch available booking slots from Cal.com.
    Returns the next available slots for the configured event type.
    """
    if not CAL_API_KEY:
        # Return mock slots when Cal.com is not configured
        logger.warning("Cal.com not configured — returning mock slots")
        return _get_mock_slots()

    start_time = datetime.utcnow().isoformat() + "Z"
    end_time = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + "Z"

    try:
        response = requests.get(
            f"{CAL_BASE_URL}/slots/available",
            params={
                "startTime": start_time,
                "endTime": end_time,
                "eventTypeId": CAL_EVENT_TYPE_ID,
                "username": CAL_USERNAME,
            },
            headers=CAL_HEADERS,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        slots = []
        for date, times in data.get("slots", {}).items():
            for slot in times[:3]:  # Max 3 slots per day
                slots.append({
                    "date": date,
                    "time": slot.get("time", ""),
                    "display": _format_slot(slot.get("time", ""), date),
                })
            if len(slots) >= 6:  # Return max 6 slots total
                break

        logger.info(f"Retrieved {len(slots)} available slots")
        return slots

    except Exception as e:
        logger.error(f"Cal.com slots fetch failed: {e}")
        return _get_mock_slots()


def create_booking(
    slot_time: str,
    name: str,
    email: str,
    notes: str = "",
) -> dict:
    """
    Create a booking in Cal.com.
    Returns booking details including confirmation ID.
    """
    if not CAL_API_KEY:
        logger.warning("Cal.com not configured — returning mock booking")
        return _get_mock_booking(name, email, slot_time)

    try:
        payload = {
            "start": slot_time,
            "eventTypeId": int(CAL_EVENT_TYPE_ID),
            "attendee": {
                "name": name,
                "email": email,
                "timeZone": "Africa/Lagos",
            },
            "meetingUrl": "https://meet.google.com/generated-link",
        }

        if notes:
            payload["responses"] = {"notes": notes}

        response = requests.post(
            f"{CAL_BASE_URL}/bookings",
            json=payload,
            headers=CAL_HEADERS,
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()

        booking = {
            "booking_id": str(data.get("data", {}).get("id", "unknown")),
            "uid": data.get("data", {}).get("uid", ""),
            "status": data.get("data", {}).get("status", "accepted"),
            "start_time": slot_time,
            "name": name,
            "email": email,
            "meeting_url": data.get("data", {}).get("meetingUrl", ""),
        }

        logger.info(f"Booking created: {booking['booking_id']} for {email}")
        return booking

    except Exception as e:
        logger.error(f"Cal.com booking failed: {e}")
        raise ValueError(f"Booking failed: {str(e)}")


def _format_slot(time_str: str, date: str) -> str:
    """Format a slot time for display to the user."""
    try:
        dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
        return dt.strftime("%A %d %B at %I:%M %p WAT")
    except Exception:
        return f"{date} at {time_str}"


def _get_mock_slots() -> list[dict]:
    """Mock slots for testing without Cal.com configured."""
    base = datetime.utcnow()
    return [
        {
            "date": (base + timedelta(days=1)).strftime("%Y-%m-%d"),
            "time": (base + timedelta(days=1, hours=9)).isoformat() + "Z",
            "display": "Tomorrow at 9:00 AM WAT",
        },
        {
            "date": (base + timedelta(days=1)).strftime("%Y-%m-%d"),
            "time": (base + timedelta(days=1, hours=14)).isoformat() + "Z",
            "display": "Tomorrow at 2:00 PM WAT",
        },
        {
            "date": (base + timedelta(days=2)).strftime("%Y-%m-%d"),
            "time": (base + timedelta(days=2, hours=10)).isoformat() + "Z",
            "display": "In 2 days at 10:00 AM WAT",
        },
    ]


def _get_mock_booking(name: str, email: str, slot_time: str) -> dict:
    """Mock booking for testing without Cal.com configured."""
    return {
        "booking_id": "MOCK-001",
        "uid": "mock-uid-12345",
        "status": "accepted",
        "start_time": slot_time,
        "name": name,
        "email": email,
        "meeting_url": "https://meet.google.com/mock-link",
    }