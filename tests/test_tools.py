# tests/test_tools.py
import pytest
from unittest.mock import patch


def test_tools_list_has_three_tools():
    from app.core.tools import TOOLS
    assert len(TOOLS) == 3


def test_tool_names():
    from app.core.tools import TOOLS
    names = [t.name for t in TOOLS]
    assert "get_available_slots_tool" in names
    assert "book_appointment" in names
    assert "trigger_confirmation" in names


@patch("app.core.tools.get_available_slots")
def test_get_slots_tool_returns_formatted_string(mock_slots):
    mock_slots.return_value = [
        {"date": "2026-05-13", "time": "2026-05-13T09:00:00Z", "display": "Tomorrow at 9:00 AM WAT"},
        {"date": "2026-05-13", "time": "2026-05-13T14:00:00Z", "display": "Tomorrow at 2:00 PM WAT"},
    ]
    from app.core.tools import get_available_slots_tool
    result = get_available_slots_tool.invoke({})
    assert "Tomorrow at 9:00 AM WAT" in result
    assert "Tomorrow at 2:00 PM WAT" in result


@patch("app.core.tools.create_booking")
@patch("app.core.tools.save_booking_to_airtable")
def test_book_appointment_tool_success(mock_airtable, mock_booking):
    mock_booking.return_value = {
        "booking_id": "BK-001",
        "name": "Amina Bello",
        "email": "amina@test.com",
        "start_time": "2026-05-13T09:00:00Z",
        "meeting_url": "https://meet.google.com/test",
        "status": "accepted",
    }
    mock_airtable.return_value = "rec123"

    from app.core.tools import book_appointment
    result = book_appointment.invoke({
        "slot_time": "2026-05-13T09:00:00Z",
        "name": "Amina Bello",
        "email": "amina@test.com",
    })
    assert "BK-001" in result
    assert "confirmed" in result.lower()