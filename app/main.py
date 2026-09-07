import logging
from datetime import date as date_cls
from datetime import datetime, timedelta, timezone
from html import escape

import stripe
from fastapi import FastAPI, Form, Header, HTTPException, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, Response
from icalendar import Calendar, Event
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse

from app.agent import generate_reply
from app.config import ADMIN_API_KEY, STRIPE_WEBHOOK_SECRET, TWILIO_AUTH_TOKEN
from app.db import (
    BookingAlreadyCompleted,
    BookingNotFound,
    complete_booking,
    get_booking_for_tracking,
    mark_payment_paid,
    save_message,
)
from app.notifications import from_number_for, twilio_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("relay")

app = FastAPI(title="Relay")
validator = RequestValidator(TWILIO_AUTH_TOKEN)


@app.get("/health")
def health():
    return {"status": "ok"}


async def _handle_inbound_message(request: Request, channel: str, body: str, from_: str) -> PlainTextResponse:
    signature = request.headers.get("X-Twilio-Signature", "")
    url = str(request.url)
    form = await request.form()
    if not validator.validate(url, dict(form), signature):
        raise HTTPException(status_code=403, detail="Invalid Twilio signature")

    logger.info("Inbound %s message from %s: %s", channel, from_, body)

    reply_text = generate_reply(from_, body)

    twiml = MessagingResponse()
    twiml.message(reply_text)
    return PlainTextResponse(str(twiml), media_type="application/xml")


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(
    request: Request,
    Body: str = Form(...),
    From: str = Form(...),
):
    return await _handle_inbound_message(request, "WhatsApp", Body, From)


@app.post("/webhook/sms")
async def sms_webhook(
    request: Request,
    Body: str = Form(...),
    From: str = Form(...),
):
    return await _handle_inbound_message(request, "SMS", Body, From)


@app.post("/bookings/{booking_id}/complete")
async def mark_booking_complete(booking_id: str, x_admin_key: str = Header(None)):
    if x_admin_key != ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid admin key")

    try:
        booking = complete_booking(booking_id)
    except BookingNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except BookingAlreadyCompleted as exc:
        raise HTTPException(status_code=409, detail=str(exc))

    message = booking["completion_message"]
    phone = booking["contractor_phone"]

    try:
        twilio_client.messages.create(from_=from_number_for(phone), to=phone, body=message)
        message_sent = True
    except Exception:
        logger.exception("Failed to send completion message for booking %s", booking_id)
        message_sent = False

    save_message(phone, "assistant", message)

    return {"booking_id": booking_id, "status": "completed", "message_sent": message_sent}


_STATUS_COPY = {
    "pending": ("Pending", "Your booking request is being processed."),
    "confirmed": ("Confirmed", "Your equipment is booked and scheduled for delivery."),
    "completed": ("Completed", "This rental has been completed."),
}


def _render_tracking_page(booking: dict) -> str:
    ref = booking["booking_id"][:8]
    equipment = booking.get("equipment") or {}
    equipment_name = escape(equipment.get("name") or "Equipment")
    status_label, status_note = _STATUS_COPY.get(booking["status"], (booking["status"].title(), ""))

    def paid_badge(paid: bool) -> str:
        return "Paid" if paid else "Not yet paid"

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Track your delivery — Ref #{ref}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          background: #f5f5f4; color: #1c1917; margin: 0; padding: 24px 16px; }}
  .card {{ max-width: 480px; margin: 0 auto; background: #fff; border-radius: 12px;
           padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
  h1 {{ font-size: 18px; margin: 0 0 4px; }}
  .ref {{ color: #78716c; font-size: 13px; margin-bottom: 20px; }}
  .status {{ display: inline-block; padding: 6px 12px; border-radius: 999px;
             background: #ecfccb; color: #365314; font-weight: 600; font-size: 14px;
             margin-bottom: 8px; }}
  .status-note {{ color: #57534e; font-size: 14px; margin-bottom: 20px; }}
  .row {{ display: flex; justify-content: space-between; padding: 10px 0;
          border-top: 1px solid #f0efee; font-size: 14px; }}
  .row span:first-child {{ color: #78716c; }}
  .placeholder {{ margin-top: 20px; padding: 12px 14px; background: #fafaf9;
                  border-radius: 8px; font-size: 13px; color: #78716c; }}
</style>
</head>
<body>
  <div class="card">
    <h1>{equipment_name}</h1>
    <div class="ref">Booking Ref #{ref}</div>
    <div class="status">{escape(status_label)}</div>
    <div class="status-note">{escape(status_note)}</div>

    <div class="row"><span>Dates</span><span>{escape(booking["start_date"])} to {escape(booking["end_date"])}</span></div>
    <div class="row"><span>Delivery location</span><span>{escape(booking["delivery_location"] or "")}</span></div>
    <div class="row"><span>Deposit</span><span>{paid_badge(booking["deposit_paid"])}</span></div>
    <div class="row"><span>Balance</span><span>{paid_badge(booking["balance_paid"])}</span></div>

    <div class="placeholder">
      Live delivery tracking (dispatch status, driver ETA) isn't available yet —
      this page will show real-time updates here once that's wired up. For now,
      this reflects your current booking status.
    </div>
  </div>
</body>
</html>"""


@app.get("/track/{booking_id}", response_class=HTMLResponse)
async def track_booking(booking_id: str):
    try:
        booking = get_booking_for_tracking(booking_id)
    except BookingNotFound:
        raise HTTPException(status_code=404, detail="Booking not found")
    return _render_tracking_page(booking)


def _build_ics(booking: dict) -> bytes:
    ref = booking["booking_id"][:8]
    equipment_name = (booking.get("equipment") or {}).get("name") or "Equipment"

    cal = Calendar()
    cal.add("prodid", "-//Relay//Booking Calendar//EN")
    cal.add("version", "2.0")

    event = Event()
    event.add("summary", f"{equipment_name} — Ref #{ref}")
    start = date_cls.fromisoformat(booking["start_date"])
    end = date_cls.fromisoformat(booking["end_date"])
    event.add("dtstart", start)
    event.add("dtend", end + timedelta(days=1))  # DTEND is exclusive for all-day events
    event.add("location", booking["delivery_location"] or "")
    event.add(
        "description",
        f"Contractor: {booking['contractor_name']}\n"
        f"Phone: {booking['contractor_phone']}\n"
        f"Equipment: {equipment_name}\n"
        f"Deposit: ${booking['deposit_amount']:.2f}",
    )
    event.add("uid", f"{booking['booking_id']}@relay")
    event.add("dtstamp", datetime.now(timezone.utc))
    cal.add_component(event)
    return cal.to_ical()


@app.get("/calendar/{booking_id}")
async def booking_calendar(booking_id: str):
    try:
        booking = get_booking_for_tracking(booking_id)
    except BookingNotFound:
        raise HTTPException(status_code=404, detail="Booking not found")

    ref = booking["booking_id"][:8]
    return Response(
        content=_build_ics(booking),
        media_type="text/calendar",
        headers={"Content-Disposition": f'attachment; filename="booking-{ref}.ics"'},
    )


@app.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    signature = request.headers.get("stripe-signature", "")

    try:
        event = stripe.Webhook.construct_event(payload, signature, STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.SignatureVerificationError):
        raise HTTPException(status_code=400, detail="Invalid Stripe signature")

    if event["type"] != "checkout.session.completed":
        return {"status": "ignored", "type": event["type"]}

    # StripeObject isn't a real dict (its .get() raises on purpose) — convert
    # once so the rest of this handler can use plain dict access.
    session = event["data"]["object"].to_dict()
    metadata = session.get("metadata") or {}
    booking_id = metadata.get("booking_id")
    payment_type = metadata.get("payment_type")

    if not booking_id or not payment_type:
        logger.error("Stripe checkout.session.completed missing booking metadata: %s", session.get("id"))
        return {"status": "ignored", "reason": "missing metadata"}

    try:
        booking = mark_payment_paid(booking_id, payment_type)
    except BookingNotFound:
        logger.error("Stripe webhook referenced unknown booking_id: %s", booking_id)
        return {"status": "ignored", "reason": "unknown booking"}

    if booking is None:
        logger.info("Payment already recorded for booking %s (%s) — duplicate webhook", booking_id, payment_type)
        return {"status": "already_recorded"}

    logger.info("Recorded %s payment for booking %s", payment_type, booking_id)

    # The equipment owner is already notified when the booking is first
    # confirmed (see create_booking) — this handler just records payment.
    return {
        "status": "recorded",
        "booking_id": booking_id,
        "payment_type": payment_type,
    }
