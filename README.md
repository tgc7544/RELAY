# Relay

**Book construction equipment by text.**

Relay is an AI booking agent for Caribbean contractors. Instead of coordinating equipment rentals over scattered WhatsApp threads and phone calls, a contractor just texts what they need — Relay checks live availability, confirms a price, sends a payment link, and notifies the equipment owner. No app required.

Live landing page: **[buildrelay.co](https://buildrelay.co)**

## The problem

Caribbean construction coordination happens almost entirely over fragmented WhatsApp and phone calls — there's no central platform for booking equipment. Machines sit idle while nearby job sites stall, trades get booked inefficiently, and deliveries slip. It's a large, entirely solvable problem: Barbados alone has a construction market north of $1.5B and zero dedicated coordination platforms.

## How it works

1. **Text** — a contractor describes what they need in plain language over WhatsApp or SMS.
2. **Match** — Relay checks live equipment availability and returns options with pricing.
3. **Confirm** — the contractor confirms and gets a Stripe payment link for the deposit.
4. **Notify** — the equipment owner is automatically notified by SMS.

Real conversation, real booking, real payment — no app needed.

## What's in this repo

| Path | What it is |
|---|---|
| [`app/`](app) | FastAPI backend — the WhatsApp/SMS AI agent (Twilio + Claude + Supabase + Stripe) that powers the actual product |
| [`mobile-app/`](mobile-app) | Mobile web app demo (React + Vite) — a phone-width UI for the contractor and equipment-owner experience |
| [`relay-web/`](relay-web) | Desktop web app demo (React + Vite) — the same experience laid out for a full browser viewport |
| [`supabase/`](supabase) | SQL schema, seed data, and RLS policies for the shared Supabase project |

Both `mobile-app/` and `relay-web/` talk to the same live Supabase project, so a booking made in one shows up in the other immediately. The backend agent in `app/` uses the same database via its own service-role connection.

## Running locally

### Backend (WhatsApp/SMS booking agent)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in Twilio, Anthropic, Supabase, and Stripe keys
uvicorn app.main:app --reload --port 8000
```

Twilio needs a public URL to deliver webhooks to your local server (e.g. `ngrok http 8000`) — set that URL as `PUBLIC_BASE_URL` in `.env` and as the WhatsApp/SMS webhook in your Twilio console.

### Mobile app demo

```bash
cd mobile-app
npm install
# create .env with VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY
npm run dev
```

### Web app demo

```bash
cd relay-web
npm install
# create .env with VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY
npm run dev
```

Both frontends only need the Supabase project URL and anon key — see `supabase/schema.sql` and `supabase/seed.sql` to set up your own project.

## Team

Built for the **Future Caribbean Buildathon 2026** by:

- **Chris Corless** — Venture Architect
- **James Edghill** — Industry Partner & Lead Investor, operates One Construction, the largest construction company in Barbados
