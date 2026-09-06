import stripe

from app.config import STRIPE_SECRET_KEY

stripe.api_key = STRIPE_SECRET_KEY

DEPOSIT_RATE = 0.30
CURRENCY = "bbd"


def split_deposit(total_amount: float) -> tuple[float, float]:
    """(deposit, balance) for a total, deposit = 30% rounded to cents, balance = remainder."""
    deposit = round(total_amount * DEPOSIT_RATE, 2)
    balance = round(total_amount - deposit, 2)
    return deposit, balance


def create_payment_link(
    amount: float, product_name: str, booking_id: str, payment_type: str
) -> str:
    """A one-off Stripe Payment Link for `amount`, tagged with booking_id/payment_type
    so the webhook can find its way back to the right booking and payment leg."""
    link = stripe.PaymentLink.create(
        line_items=[
            {
                "price_data": {
                    "currency": CURRENCY,
                    "product_data": {"name": product_name},
                    "unit_amount": round(amount * 100),
                },
                "quantity": 1,
            }
        ],
        metadata={"booking_id": booking_id, "payment_type": payment_type},
        payment_intent_data={"metadata": {"booking_id": booking_id, "payment_type": payment_type}},
    )
    return link.url
