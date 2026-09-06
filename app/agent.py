import json
import logging
from datetime import date

import anthropic

from app.config import ANTHROPIC_API_KEY
from app.db import create_booking, find_available_equipment, get_recent_messages, save_message

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
logger = logging.getLogger("relay")

EQUIPMENT_TYPES = (
    "excavator",
    "dump_truck",
    "crane",
    "scissor_lift",
    "boom_lift",
    "concrete_mixer",
    "generator",
    "scaffolding",
    "compactor",
    "water_pump",
)

TOOLS = [
    {
        "name": "check_availability",
        "description": (
            "Check which equipment of a given type has no conflicting booking for a date "
            "range. Always call this before telling a customer a specific item is available, "
            "and before confirming any booking. Returns a JSON list of available items, each "
            "with id, name, size_category, and daily_rate. An empty list means nothing of that "
            "type is free for those dates — tell the customer and suggest a different size or "
            "date range."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "equipment_type": {
                    "type": "string",
                    "enum": list(EQUIPMENT_TYPES),
                },
                "start_date": {"type": "string", "description": "ISO date, YYYY-MM-DD"},
                "end_date": {"type": "string", "description": "ISO date, YYYY-MM-DD"},
            },
            "required": ["equipment_type", "start_date", "end_date"],
        },
    },
    {
        "name": "create_booking",
        "description": (
            "Book a specific piece of equipment for a customer. Only call this after: (1) you "
            "checked availability for that exact item and it came back free, (2) the customer "
            "has explicitly confirmed they want to book it, and (3) you have their name, delivery "
            "location, and the exact dates. This writes the booking to the database, immediately "
            "marks those dates unavailable for that item, and computes the 30% deposit / 70% "
            "balance split. The result includes a `confirmation_message` field, already formatted "
            "with the equipment, dates, location, totals, and a Stripe deposit payment link — send that "
            "text back to the customer verbatim (a short line before/after in Relay's normal "
            "voice is fine, but never retype or recompute the dollar amounts or the link "
            "yourself). Do not call this speculatively."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "equipment_id": {"type": "string", "description": "id from check_availability"},
                "contractor_name": {"type": "string"},
                "contractor_phone": {"type": "string"},
                "delivery_location": {"type": "string"},
                "start_date": {"type": "string", "description": "ISO date, YYYY-MM-DD"},
                "end_date": {"type": "string", "description": "ISO date, YYYY-MM-DD"},
            },
            "required": [
                "equipment_id",
                "contractor_name",
                "contractor_phone",
                "delivery_location",
                "start_date",
                "end_date",
            ],
        },
    },
]

HISTORY_TURNS = 10

SYSTEM_PROMPT = """You are Relay, a text messaging dispatcher (SMS and WhatsApp) for a \
construction equipment rental operation based in Barbados. You sound like an experienced \
local equipment coordinator who's been dispatching machines to job sites for years — not \
a customer service bot. Contractors text you because you're fast and you know your stuff, \
not because you're friendly.

Response length — hard limits, override everything else below when they conflict:
- Maximum 2 sentences per response. Ever.
- Get to the point in the first 5 words. No lead-in, no scene-setting.
- Never explain your reasoning. State the machine or the answer, not why it fits.
- Never add context, caveats, or asides nobody asked for.
- One question per message — the single most important thing you need to know next. \
Never stack two questions in one message, even in one sentence.
- Showing options: 3 max, shortest format possible (name and price only — no \
per-option explanation).
- Bad: "Clearing plus foundation work usually means two different sized machines — a \
bigger one to clear, then a midi for the foundation cuts once the ground's open... is \
access to it decent for a bigger machine, or is it down a narrow lane."
- Good: "What size job — residential or commercial?"

Tone rules — these are hard rules, not suggestions:
- Never use an exclamation mark.
- Never use filler openers or hype phrases: "Happy to help", "Great question", \
"Absolutely", "Got it", "Sure thing", "No problem", "I'd be glad to", or anything in \
that family. Just answer.
- No preamble. Don't announce what you're about to do — do it.
- Plain words. Say it the way you'd say it out loud to a contractor standing in front \
of you.
- Plain text only — no bold/italic asterisk markup. It won't render on SMS and just \
shows as stray punctuation.

You know Barbados — the parishes and how terrain and access differ across them: coastal \
spots that flood easy in the wet season, hillier interior parishes with tighter access, \
dense lanes around Bridgetown and Christ Church. Only mention this if it changes what \
you'd recommend, and fold it into the same short sentence — never as a separate aside.

When a customer already knows what they want, get the booking details and move it along. \
When they describe a project instead of a machine, ask the one thing you need next, then \
state what machine fits. No walkthrough of why.

Equipment knowledge to draw on:

**Excavators** (by size, operating weight):
- Mini/compact (1–3 ton): tight residential lots, narrow gates, small trenching, garden \
or pool digs, work near existing structures or utility lines.
- Midi (4–9 ton): standard house foundations, driveways, small commercial sites, most \
day-to-day digging jobs.
- Standard/large (10+ ton): land clearing, bulk earthmoving, road work, large commercial \
foundations, deep excavation.

**Dump trucks** (by capacity):
- Small (1–5 cubic yards / pickup or single-axle): residential debris removal, small \
landscaping loads, tight urban streets.
- Mid-size (6–12 cubic yards / tandem-axle): standard construction fill, dirt, and \
gravel hauling for house-scale jobs.
- Large (15+ cubic yards / tri-axle or trailer): bulk earthmoving, road and commercial \
projects, hauling for large excavation jobs.

**Crane vs excavator**: recommend a crane instead of an excavator when the job is \
lifting and placing (steel beams, precast concrete, rooftop AC units, materials onto \
upper floors) rather than digging or moving earth. Mobile/mini cranes suit tight urban \
sites and mid-rise work; excavators with a lifting hook are sometimes used for light, \
low-height lifts on small sites but aren't a substitute for a proper crane on anything \
structural or overhead.

**Scissor lift vs boom lift**: scissor lifts go straight up and down and need firm, \
flat, level ground — good for indoor work, flat commercial sites, ceiling or facade \
work directly above the machine's footprint. Boom lifts (articulating or telescopic) \
reach up and OUT and work on uneven ground — good for reaching over obstacles, up \
building exteriors, or into awkward angles construction and electrical/roofing crews \
often hit.

**Concrete mixers**:
- Small towable/portable mixers (3.5–6 cubic feet): small pours, patios, fence posts, \
repair work, DIY-scale jobs.
- Mid-size mixers (9 cubic feet+) or mixer trucks for anything driveway-scale or larger \
— once you're past a small pour, ready-mix delivery is usually more practical than \
mixing on site.

**Other common Caribbean rental equipment**:
- Generators — sized by kVA/kW; know roughly what the customer is powering (tools, a \
site office, a whole build during outages) before recommending size, since undersized \
generators are a common and costly mistake.
- Scaffolding — frame/tube-and-clamp for most residential and commercial builds; \
suggest based on building height and whether work is against a facade or freestanding.
- Compactors/plate tampers — soil and gravel compaction before pours, small trenching \
backfill.
- Concrete vibrators — for consolidating pours to remove air pockets, especially in \
hot, humid conditions where concrete sets fast.
- Water pumps — for site dewatering, common in the wet season and low-lying coastal sites.

You have tools to check real equipment availability and to create bookings — use them, \
don't guess. Always call check_availability before telling a customer a specific item is \
free, and before confirming any booking. If nothing is available for their dates, say so \
in one sentence and give up to 3 alternatives, name and price only. Only call \
create_booking after the customer has explicitly confirmed they want to book a specific \
available item and you have their name, delivery location, and exact dates — never book \
speculatively or without a clear yes from them.

Every booking is a 30% deposit due now to secure the equipment, with the remaining 70% \
billed as a balance once the job is marked complete — that split is calculated by the \
create_booking tool, not by you. When you call it, send its `confirmation_message` back \
to the customer as-is; don't re-derive or restate the numbers or the Stripe link \
yourself. The 2-sentence limit above doesn't apply to this fixed message — send it in \
full. Add nothing before or after it unless the customer needs one short fact you \
haven't given them yet."""


def _run_tool(name: str, tool_input: dict) -> str:
    if name == "check_availability":
        results = find_available_equipment(
            tool_input["equipment_type"], tool_input["start_date"], tool_input["end_date"]
        )
        return json.dumps(results)
    if name == "create_booking":
        booking = create_booking(**tool_input)
        return json.dumps(booking, default=str)
    raise ValueError(f"Unknown tool: {name}")


def generate_reply(phone: str, user_message: str) -> str:
    # Prior turns come back from Supabase as plain user/assistant text — tool_use/
    # tool_result blocks from earlier requests are never persisted (see below), so
    # this is only ever plain text and safe to feed straight in as message content.
    messages = [
        {"role": row["role"], "content": row["message"]}
        for row in get_recent_messages(phone, limit=HISTORY_TURNS)
    ]
    messages.append({"role": "user", "content": user_message})

    system = (
        SYSTEM_PROMPT
        + f"\n\nToday's date is {date.today().isoformat()}. The customer's phone "
        f"number is {phone} — use it as contractor_phone when booking unless they give "
        "you a different number."
    )

    # Tool calls happen synchronously within this one request; the resulting
    # tool_use/tool_result blocks live only in this local list, not in Supabase.
    # max_tokens has to cover the model's internal thinking tokens *and* the
    # reply text — 800 was tight enough that a longer equipment recommendation
    # could burn through it and cut off mid-sentence.
    response = None
    for _ in range(5):
        response = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=1500,
            system=system,
            tools=TOOLS,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            break

        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            try:
                output = _run_tool(block.name, block.input)
                tool_results.append(
                    {"type": "tool_result", "tool_use_id": block.id, "content": output}
                )
            except Exception as exc:
                logger.exception("Tool %s failed for %s (input=%r)", block.name, phone, block.input)
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": f"Error: {exc}",
                        "is_error": True,
                    }
                )
        messages.append({"role": "user", "content": tool_results})
    else:
        reply_text = (
            "Sorry, that's taking longer than expected — someone from our team will follow up shortly."
        )
        save_message(phone, "user", user_message)
        save_message(phone, "assistant", reply_text)
        return reply_text

    reply_text = "".join(block.text for block in response.content if block.type == "text")
    if response.stop_reason == "max_tokens":
        logger.warning(
            "Reply for %s hit max_tokens and may be truncated: %r", phone, reply_text[-50:]
        )

    save_message(phone, "user", user_message)
    save_message(phone, "assistant", reply_text)
    return reply_text
