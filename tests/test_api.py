# tests/test_api.py
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import create_app

client = TestClient(create_app())


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_session():
    response = client.post("/api/v1/chat/session")
    assert response.status_code == 201
    data = response.json()
    assert "session_id" in data
    assert len(data["session_id"]) > 0


def test_empty_message_rejected():
    response = client.post(
        "/api/v1/chat/message",
        json={"message": ""},
    )
    assert response.status_code == 422


@patch("app.api.routes.chat.process_message")
def test_send_message_success(mock_process):
    mock_process.return_value = {
        "response": "Hello! I am Alex. How can I help you today?",
        "session_id": "test-session-123",
        "tools_used": [],
        "booking_confirmed": None,
    }
    response = client.post(
        "/api/v1/chat/message",
        json={"message": "Hello"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "Alex" in data["response"]
    assert data["session_id"] == "test-session-123"


@patch("app.api.routes.chat.process_message")
def test_booking_confirmed_flag(mock_process):
    mock_process.return_value = {
        "response": "Your appointment is confirmed!",
        "session_id": "test-session-456",
        "tools_used": ["book_appointment", "trigger_confirmation"],
        "booking_confirmed": True,
    }
    response = client.post(
        "/api/v1/chat/message",
        json={"message": "Yes book it", "session_id": "test-session-456"},
    )
    assert response.status_code == 200
    assert response.json()["booking_confirmed"] is True