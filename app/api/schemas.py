# app/api/schemas.py
from pydantic import BaseModel, Field


class MessageRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    session_id: str | None = Field(default=None)


class MessageResponse(BaseModel):
    response: str
    session_id: str
    tools_used: list[str]
    booking_confirmed: bool | None


class SessionResponse(BaseModel):
    session_id: str
    message: str = "New session started. How can I help you today?"


class HealthResponse(BaseModel):
    status: str
    env: str