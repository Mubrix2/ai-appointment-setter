# app/core/tools.py
import logging
from langchain_core.tools import tool
from app.services.cal_service import get_available_slots, create_booking
from app.services.notification_service import (
    trigger_booking_webhook,
    save_booking_to_airtable,
)

logger = logging.getLogger(__name__)


@tool
def get_available_slots_tool() -> str:
    """
    Fetch available appointment slots from the calendar.
    Call this when the user is ready to see booking options.
    Returns a formatted list of available times.
    """
    try:
        slots = get_available_slots(days_ahead=7)
        if not slots:
            return "No available slots found in the next 7 days. Please contact us directly."

        formatted = "Here are the available slots:\n\n"
        for i, slot in enumerate(slots, 1):
            formatted += f"{i}. {slot['display']}\n"
        formatted += "\nWhich slot works best for you?"

        # Store slot data for booking (attach to response)
        return formatted + f"\n\n[SLOTS_DATA:{slots}]"

    except Exception as e:
        logger.error(f"get_available_slots_tool failed: {e}")
        return "I had trouble fetching available slots. Please try again."


@tool
def book_appointment(
    slot_time: str,
    name: str,
    email: str,
    notes: str = "",
) -> str:
    """
    Book an appointment slot for the user.
    Call this after the user has confirmed their chosen slot,
    and you have collected their name and email.

    Args:
        slot_time: The ISO format time of the chosen slot
        name: Full name of the person booking
        email: Email address for confirmation
        notes: Optional notes about what they want to discuss
    """
    try:
        booking = create_booking(
            slot_time=slot_time,
            name=name,
            email=email,
            notes=notes,
        )

        # Save to Airtable
        save_booking_to_airtable(booking, notes=notes)

        return (
            f"✅ Booking confirmed!\n\n"
            f"**Booking ID:** {booking['booking_id']}\n"
            f"**Name:** {booking['name']}\n"
            f"**Email:** {booking['email']}\n"
            f"**Time:** {booking['start_time']}\n"
            f"**Meeting Link:** {booking['meeting_url']}\n\n"
            f"[BOOKING_CONFIRMED:{booking}]"
        )

    except Exception as e:
        logger.error(f"book_appointment tool failed: {e}")
        return f"I was unable to complete the booking. Please try again or contact us directly."


@tool
def trigger_confirmation(
    booking_id: str,
    name: str,
    email: str,
    start_time: str,
    meeting_url: str = "",
    notes: str = "",
) -> str:
    """
    Trigger the confirmation workflow after a successful booking.
    This sends the confirmation email and updates the CRM.
    Always call this after a successful book_appointment call.

    Args:
        booking_id: The confirmed booking ID
        name: Name of the person booked
        email: Their email address
        start_time: The booked time slot
        meeting_url: The meeting link if available
        notes: Any notes about the booking
    """
    booking = {
        "booking_id": booking_id,
        "name": name,
        "email": email,
        "start_time": start_time,
        "meeting_url": meeting_url,
    }

    success = trigger_booking_webhook(booking, notes=notes)

    if success:
        return "Confirmation email sent and CRM updated successfully."
    else:
        return "Booking confirmed. Confirmation email will be sent shortly."


TOOLS = [get_available_slots_tool, book_appointment, trigger_confirmation]