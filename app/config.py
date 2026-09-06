import os

from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID = os.environ["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN = os.environ["TWILIO_AUTH_TOKEN"]
TWILIO_WHATSAPP_NUMBER = os.environ["TWILIO_WHATSAPP_NUMBER"]
TWILIO_SMS_NUMBER = os.environ["TWILIO_SMS_NUMBER"]

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

# Shared secret for the internal /bookings/{id}/complete endpoint — not a
# customer-facing credential, just guards who can trigger an outbound
# completion message and mark a booking done.
ADMIN_API_KEY = os.environ["ADMIN_API_KEY"]

# Public URL this server is reachable at — used to build the tracking link
# sent to customers. Update this whenever the ngrok URL changes, or once
# this moves to permanent hosting (Railway etc.) it stops changing at all.
PUBLIC_BASE_URL = os.environ.get("PUBLIC_BASE_URL", "http://localhost:8000")
