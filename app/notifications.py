import logging
from typing import Optional

from twilio.rest import Client as TwilioClient

from app.config import (
    DEFAULT_OWNER_PHONE,
    PUBLIC_BASE_URL,
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_SMS_NUMBER,
    TWILIO_WHATSAPP_NUMBER,
)

logger = logging.getLogger("relay")

twilio_client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def from_number_for(phone: str) -> str:
    """Send from the channel the customer is actually on."""
    return TWILIO_WHATSAPP_NUMBER if phone.startswith("whatsapp:") else TWILIO_SMS_NUMBER


def _owner_new_booking_message(booking: dict, equipment_name: str) -> str:
    ref = booking["booking_id"][:8]
    calendar_link = f"{PUBLIC_BASE_URL}/calendar/{booking['booking_id']}"
    return (
        f"New booking request — Ref #{ref}\n\n"
        f"Equipment: {equipment_name}\n"
        f"Dates: {booking['start_date']} to {booking['end_date']}\n"
        f"Delivery: {booking['delivery_location']}\n\n"
        f"Contractor: {booking['contractor_name']} ({booking['contractor_phone']})\n"
        f"Deposit due: ${booking['deposit_amount']:.2f}\n\n"
        f"Calendar: {calendar_link}"
    )


def notify_equipment_owner_of_new_booking(
    booking: dict, equipment_name: str, owner_phone: Optional[str]
) -> bool:
    """Text the equipment owner as soon as a booking is confirmed — same
    moment the contractor gets their confirmation message, not gated on the
    deposit actually being paid. Returns whether a text was actually sent."""
    phone = owner_phone or DEFAULT_OWNER_PHONE
    if not phone:
        logger.warning(
            "No owner_phone on equipment for booking %s and no DEFAULT_OWNER_PHONE set — "
            "skipping owner notification",
            booking["booking_id"],
        )
        return False

    try:
        twilio_client.messages.create(
            from_=from_number_for(phone),
            to=phone,
            body=_owner_new_booking_message(booking, equipment_name),
        )
        return True
    except Exception:
        logger.exception("Failed to notify equipment owner for booking %s", booking["booking_id"])
        return False
