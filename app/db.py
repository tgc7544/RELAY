from datetime import date, datetime, timezone
from typing import Optional

from supabase import Client, create_client

from app.config import PUBLIC_BASE_URL, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_URL
from app.notifications import notify_equipment_owner_of_new_booking
from app.payments import create_payment_link, split_deposit

# supabase-py wants the project's base URL, but SUPABASE_URL sometimes gets
# set to the REST endpoint (.../rest/v1) copied straight from the Supabase
# dashboard's API settings page — normalize it either way.
_BASE_URL = SUPABASE_URL.rstrip("/").removesuffix("/rest/v1")

supabase: Client = create_client(_BASE_URL, SUPABASE_SERVICE_ROLE_KEY)

ACTIVE_BOOKING_STATUSES = ("pending", "confirmed")


class BookingNotFound(Exception):
    pass


class BookingAlreadyCompleted(Exception):
    pass


def find_available_equipment(equipment_type: str, start_date: str, end_date: str) -> list[dict]:
    """Equipment of the given type with no pending/confirmed booking overlapping the date range."""
    equipment = (
        supabase.table("equipment")
        .select("*")
        .eq("type", equipment_type)
        .eq("active", True)
        .execute()
        .data
    )
    if not equipment:
        return []

    equipment_ids = [item["id"] for item in equipment]
    overlapping = (
        supabase.table("bookings")
        .select("equipment_id")
        .in_("equipment_id", equipment_ids)
        .in_("status", ACTIVE_BOOKING_STATUSES)
        .lte("start_date", end_date)
        .gte("end_date", start_date)
        .execute()
        .data
    )
    booked_ids = {row["equipment_id"] for row in overlapping}
    return [item for item in equipment if item["id"] not in booked_ids]


def get_recent_messages(phone_number: str, limit: int = 10) -> list[dict]:
    """Last `limit` conversation turns for this number, oldest first."""
    rows = (
        supabase.table("conversations")
        .select("role, message")
        .eq("phone_number", phone_number)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
        .data
    )
    return list(reversed(rows))


def save_message(phone_number: str, role: str, message: str) -> None:
    supabase.table("conversations").insert(
        {"phone_number": phone_number, "role": role, "message": message}
    ).execute()


def create_booking(
    equipment_id: str,
    contractor_name: str,
    contractor_phone: str,
    delivery_location: str,
    start_date: str,
    end_date: str,
) -> dict:
    equipment = supabase.table("equipment").select("*").eq("id", equipment_id).execute().data
    if not equipment:
        raise ValueError(f"Unknown equipment_id: {equipment_id}")
    equipment = equipment[0]

    days = (date.fromisoformat(end_date) - date.fromisoformat(start_date)).days + 1
    total_amount = round(equipment["daily_rate"] * days, 2)
    deposit_amount, balance_amount = split_deposit(total_amount)

    # Insert first — the payment link's description includes the booking
    # reference, which only exists once the row (and its generated id) does.
    booking = (
        supabase.table("bookings")
        .insert(
            {
                "equipment_id": equipment_id,
                "contractor_name": contractor_name,
                "contractor_phone": contractor_phone,
                "delivery_location": delivery_location,
                "start_date": start_date,
                "end_date": end_date,
                "status": "confirmed",
                "total_amount": total_amount,
                "deposit_amount": deposit_amount,
                "balance_amount": balance_amount,
            }
        )
        .execute()
        .data[0]
    )

    ref = booking["booking_id"][:8]
    try:
        deposit_link = create_payment_link(
            deposit_amount,
            product_name=f"{equipment['name']} — deposit (Ref #{ref})",
            booking_id=booking["booking_id"],
            payment_type="deposit",
        )
    except Exception:
        # Don't leave a "confirmed" booking with no usable payment link — it
        # would block real availability for these dates forever with no way
        # to ever pay it off. Roll back so the customer can just try again.
        supabase.table("bookings").delete().eq("booking_id", booking["booking_id"]).execute()
        raise

    tracking_link = f"{PUBLIC_BASE_URL}/track/{booking['booking_id']}"
    calendar_link = f"{PUBLIC_BASE_URL}/calendar/{booking['booking_id']}"

    booking["confirmation_message"] = (
        f"Booking Confirmed — Ref #{ref}\n\n"
        f"Equipment: {equipment['name']}\n"
        f"Dates: {start_date} to {end_date} ({days} day{'s' if days != 1 else ''})\n"
        f"Location: {delivery_location}\n\n"
        f"Total: ${total_amount:.2f}\n"
        f"Deposit due now (30%): ${deposit_amount:.2f}\n"
        f"Balance due on completion (70%): ${balance_amount:.2f}\n\n"
        f"Pay your deposit to secure the booking:\n{deposit_link}\n\n"
        f"Track your delivery:\n{tracking_link}\n\n"
        f"Add to calendar:\n{calendar_link}\n\n"
        "We'll send the balance invoice with a new payment link once the job is marked complete."
    )

    # Notify the owner the moment the booking is confirmed — same moment the
    # contractor gets their confirmation message, not gated on the deposit
    # actually being paid.
    booking["owner_notified"] = notify_equipment_owner_of_new_booking(
        booking, equipment["name"], equipment.get("owner_phone")
    )
    return booking


def complete_booking(booking_id: str) -> dict:
    booking = (
        supabase.table("bookings").select("*, equipment(name)").eq("booking_id", booking_id).execute().data
    )
    if not booking:
        raise BookingNotFound(f"Unknown booking_id: {booking_id}")
    booking = booking[0]
    if booking["status"] == "completed":
        raise BookingAlreadyCompleted(f"Booking {booking_id} is already marked completed")

    balance_amount = booking["balance_amount"]
    ref = booking["booking_id"][:8]
    equipment_name = booking["equipment"]["name"] if booking.get("equipment") else "your equipment"
    # Get the payment link working before flipping status — if Stripe fails,
    # the booking should stay "confirmed" so this can just be retried later,
    # rather than getting stuck "completed" with no way to bill the balance.
    balance_link = create_payment_link(
        balance_amount,
        product_name=f"{equipment_name} — balance (Ref #{ref})",
        booking_id=booking["booking_id"],
        payment_type="balance",
    )

    supabase.table("bookings").update({"status": "completed"}).eq("booking_id", booking_id).execute()
    booking["status"] = "completed"

    booking["completion_message"] = (
        f"Job Complete — Ref #{ref}\n\n"
        f"{equipment_name} rental ({booking['start_date']} to {booking['end_date']}) is now marked complete.\n\n"
        f"Balance due: ${balance_amount:.2f}\n\n"
        f"Pay here:\n{balance_link}\n\n"
        "Thanks for booking with Relay!"
    )
    return booking


def get_booking_for_tracking(booking_id: str) -> dict:
    booking = (
        supabase.table("bookings")
        .select("*, equipment(name, type, size_category)")
        .eq("booking_id", booking_id)
        .execute()
        .data
    )
    if not booking:
        raise BookingNotFound(f"Unknown booking_id: {booking_id}")
    return booking[0]


def mark_payment_paid(booking_id: str, payment_type: str) -> Optional[dict]:
    """Record a Stripe payment as received. Returns the updated booking, or
    None if this booking/leg was already marked paid (idempotent — Stripe
    retries webhook deliveries, so a duplicate event must be a no-op)."""
    if payment_type not in ("deposit", "balance"):
        raise ValueError(f"Unknown payment_type: {payment_type}")

    booking = supabase.table("bookings").select("*").eq("booking_id", booking_id).execute().data
    if not booking:
        raise BookingNotFound(f"Unknown booking_id: {booking_id}")
    booking = booking[0]

    paid_field = f"{payment_type}_paid"
    if booking[paid_field]:
        return None

    supabase.table("bookings").update(
        {paid_field: True, f"{payment_type}_paid_at": datetime.now(timezone.utc).isoformat()}
    ).eq("booking_id", booking_id).execute()

    # Re-fetch with equipment embedded — the owner notification needs the
    # equipment name and owner_phone, which a bare update response won't have.
    return (
        supabase.table("bookings")
        .select("*, equipment(name, owner_phone)")
        .eq("booking_id", booking_id)
        .execute()
        .data[0]
    )
