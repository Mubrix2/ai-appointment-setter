# app/api/routes/chat.py
import logging
from fastapi import APIRouter, HTTPException, status
from app.api.schemas import MessageRequest, MessageResponse, SessionResponse
from app.services.chat_service import process_message, start_new_session

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post(
    "/session",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a new appointment booking session",
)
async def create_session():
    """Create a new conversation session."""
    session_id = start_new_session()
    return SessionResponse(session_id=session_id)


@router.post(
    "/message",
    response_model=MessageResponse,
    summary="Send a message to the appointment agent",
)
async def send_message(request: MessageRequest):
    """
    Send a message and receive a response from the AI appointment agent.
    Include session_id to continue an existing conversation.
    """
    try:
        result = process_message(
            message=request.message,
            session_id=request.session_id,
        )
        return MessageResponse(
            response=result["response"],
            session_id=result["session_id"],
            tools_used=result["tools_used"],
            booking_confirmed=result.get("booking_confirmed"),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Message processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message. Please try again.",
        )