# app/services/chat_service.py
import logging
import uuid
from app.core.agent import chat

logger = logging.getLogger(__name__)


def process_message(message: str, session_id: str | None = None) -> dict:
    """Process a user message through the appointment agent."""
    if not message.strip():
        raise ValueError("Message cannot be empty")

    if not session_id:
        session_id = str(uuid.uuid4())
        logger.info(f"New appointment session: {session_id}")

    return chat(message=message, session_id=session_id)


def start_new_session() -> str:
    session_id = str(uuid.uuid4())
    logger.info(f"New session created: {session_id}")
    return session_id