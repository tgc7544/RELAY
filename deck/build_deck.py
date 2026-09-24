"""Build the Relay 2026 pitch deck (relay-deck-2026.pptx).

Everything — cards, phone and laptop mockups, the fee donut — is drawn with
python-pptx shapes and text. No images.

    python deck/build_deck.py
"""
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.util import Inches, Pt

OUT = Path(__file__).resolve().parent.parent / "relay-deck-2026.pptx"

# Design system
BG = "0F1A17"
GREEN = "0F6E56"
ORANGE = "D85A30"
WHITE = "FFFFFF"
MUTED = "A0B0AA"
SURFACE = "1A2E28"
EDGE = "2C4A41"  # subtle outline for mockups on the dark background

ARIAL = "Arial"
BLACK = "Arial Black"

W, H = 13.333, 7.5
M = 0.6  # side margin
CW = W - 2 * M  # content width

LEFT, CENTER, RIGHT = PP_ALIGN.LEFT, PP_ALIGN.CENTER, PP_ALIGN.RIGHT
TOP, MIDDLE, BOTTOM = MSO_ANCHOR.TOP, MSO_ANCHOR.MIDDLE, MSO_ANCHOR.BOTTOM


def rgb(hex_):
    return RGBColor.from_string(hex_)


# ---------------------------------------------------------------- primitives

def shape(slide, kind, x, y, w, h, fill=None, line=None, line_w=0.75, radius=None):
    shp = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    shp.shadow.inherit = False
    if fill:
        shp.fill.solid()
        shp.fill.fore_color.rgb = rgb(fill)
    else:
        shp.fill.background()
    if line:
        shp.line.color.rgb = rgb(line)
        shp.line.width = Pt(line_w)
    else:
        shp.line.fill.background()
    if radius is not None and kind == MSO_SHAPE.ROUNDED_RECTANGLE:
        shp.adjustments[0] = min(0.5, radius / min(w, h))
    return shp


def rect(slide, x, y, w, h, fill, **kw):
    return shape(slide, MSO_SHAPE.RECTANGLE, x, y, w, h, fill, **kw)


def card(slide, x, y, w, h, fill=SURFACE, radius=0.1, **kw):
    return shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill, radius=radius, **kw)


def edged_card(slide, x, y, w, h, edge_color, side="left", t=0.05, fill=SURFACE, radius=0.1):
    """Rounded card with a coloured border on one side. The border is an
    identically-rounded shape underneath, so it follows the corner curve."""
    card(slide, x, y, w, h, fill=edge_color, radius=radius)
    if side == "left":
        return card(slide, x + t, y, w - t, h, fill=fill, radius=radius)
    return card(slide, x, y + t, w, h - t, fill=fill, radius=radius)


def circle(slide, x, y, d, fill, **kw):
    return shape(slide, MSO_SHAPE.OVAL, x, y, d, d, fill, **kw)


def _style_run(run, size, color, bold=False, italic=False, font=ARIAL, spc=None):
    f = run.font
    f.name = font
    f.size = Pt(size)
    f.bold = bold
    f.italic = italic
    f.color.rgb = rgb(color)
    if spc is not None:  # letter spacing, in hundredths of a point
        run._r.get_or_add_rPr().set("spc", str(spc))


def fill_frame(tf, paras, anchor=TOP, margin=0.0, wrap=True):
    """paras: list of dicts. Each dict is either a single run
    (text/size/color/...) or has 'runs': [dict, ...] plus paragraph options
    (align, after, line)."""
    tf.word_wrap = wrap
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.vertical_anchor = anchor
    m = Inches(margin) if not isinstance(margin, tuple) else None
    if m is not None:
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = m
    else:
        l, t, r, b = margin
        tf.margin_left, tf.margin_top = Inches(l), Inches(t)
        tf.margin_right, tf.margin_bottom = Inches(r), Inches(b)
    for i, p in enumerate(paras):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        para.alignment = p.get("align", LEFT)
        if "after" in p:
            para.space_after = Pt(p["after"])
        if "before" in p:
            para.space_before = Pt(p["before"])
        if "line" in p:
            para.line_spacing = p["line"]
        if "hang" in p:  # hanging indent: first-line marker, wrapped lines align after it
            ppr = para._p.get_or_add_pPr()
            ppr.set("marL", str(Inches(p["hang"])))
            ppr.set("indent", str(-Inches(p["hang"])))
        for r in p.get("runs", [p]):
            run = para.add_run()
            run.text = r["text"]
            _style_run(run, r["size"], r.get("color", WHITE), r.get("bold", False),
                       r.get("italic", False), r.get("font", ARIAL), r.get("spc"))
            if r.get("link"):
                run.hyperlink.address = r["link"]
    return tf


def textbox(slide, x, y, w, h, paras, anchor=TOP, margin=0.0, wrap=True):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    fill_frame(tb.text_frame, paras, anchor, margin, wrap)
    return tb


def text(slide, x, y, w, h, s, size, color=WHITE, bold=False, italic=False,
         font=ARIAL, align=LEFT, anchor=TOP, spc=None, line=None):
    p = dict(text=s, size=size, color=color, bold=bold, italic=italic,
             font=font, align=align, spc=spc)
    if line:
        p["line"] = line
    return textbox(slide, x, y, w, h, [p], anchor=anchor)


def est_lines(s, width_in, size_pt, factor=0.5):
    """Rough Arial line count for a string wrapped to width_in."""
    per_line = max(1, int(width_in * 72 / (size_pt * factor)))
    lines = 0
    for chunk in s.split("\n"):
        cur = 0
        n = 1
        for word in chunk.split(" "):
            add = len(word) + (1 if cur else 0)
            if cur + add > per_line and cur:
                n += 1
                cur = len(word)
            else:
                cur += add
        lines += n
    return lines


def bubble(slide, x_left, x_right, y, s, size, fill, color, side, max_w, line=None):
    """Chat bubble hugging its text; side='left'|'right'. Returns its height."""
    pad_x, pad_y = 0.14, 0.08
    one_line_w = max(len(line_) for line_ in s.split("\n")) * size * 0.55 / 72
    w = min(max_w, one_line_w + 2 * pad_x + 0.08)
    lines = est_lines(s, w - 2 * pad_x, size, factor=0.55)
    h = lines * size * 1.22 / 72 + 2 * pad_y
    x = x_left if side == "left" else x_right - w
    shp = card(slide, x, y, w, h, fill=fill, radius=0.12, line=line, line_w=0.5)
    fill_frame(shp.text_frame, [dict(text=s, size=size, color=color)],
               anchor=MIDDLE, margin=(pad_x, pad_y, pad_x, pad_y))
    return h


# ------------------------------------------------------------------- chrome

prs = Presentation()
prs.slide_width = Inches(W)
prs.slide_height = Inches(H)
BLANK = prs.slide_layouts[6]


def new_slide():
    slide = prs.slides.add_slide(BLANK)
    n = len(prs.slides)
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = rgb(BG)
    rect(slide, 0, 0, W, 0.05, GREEN)
    text(slide, M, 7.05, 2, 0.25, "Relay", 9, GREEN, bold=True, anchor=MIDDLE)
    text(slide, W - M - 2, 7.05, 2, 0.25, str(n), 9, MUTED, align=RIGHT, anchor=MIDDLE)
    return slide


def headline(slide, s, size=32, y=0.55, h=0.65, color=WHITE, font=ARIAL, bold=True):
    text(slide, M, y, CW, h, s, size, color, bold=bold, font=font, anchor=TOP)


def dot_bullets(slide, x, y, w, items, size=15, gap=0.95, dot=GREEN):
    for i, s in enumerate(items):
        yy = y + i * gap
        circle(slide, x, yy + 0.09, 0.14, dot)
        text(slide, x + 0.35, yy, w - 0.35, gap - 0.1, s, size, WHITE, line=1.1)


# ------------------------------------------------------------------- slides

def slide_cover():
    s = new_slide()
    text(s, M, 2.55, CW, 1.3, "Relay", 72, WHITE, font=BLACK, align=CENTER, anchor=BOTTOM)
    text(s, M, 3.95, CW, 0.5, "The operating system for Caribbean construction.", 20, MUTED,
         align=CENTER)
    text(s, W - M - 2, 6.5, 2, 0.35, "2026", 14, ORANGE, bold=True, align=RIGHT)


def slide_problem_1():
    s = new_slide()
    headline(s, "Caribbean construction is booming.", 36, y=0.6, h=0.7)
    headline(s, "The systems haven't caught up.", 28, y=1.3, h=0.6, color=ORANGE)
    stats = [
        ("$8B+", GREEN, "Regional construction market"),
        ("0", ORANGE, "Central booking platforms in the Caribbean"),
        ("100%", GREEN, "Of coordination happens over WhatsApp and phone calls"),
    ]
    gap = 0.4
    w = (CW - 2 * gap) / 3
    y, h = 2.9, 3.6
    for i, (num, col, label) in enumerate(stats):
        x = M + i * (w + gap)
        card(s, x, y, w, h)
        text(s, x + 0.45, y + 0.7, w - 0.9, 1.2, num, 48, col, bold=True, anchor=BOTTOM)
        text(s, x + 0.45, y + 2.05, w - 0.9, 1.1, label, 12, WHITE, line=1.15)


def slide_problem_2():
    s = new_slide()
    headline(s, "The real cost of fragmentation.", 36, y=0.6, h=0.7)
    items = [
        ("Idle machinery",
         "Equipment sits unused while nearby job sites stall, waiting on phone calls "
         "that haven't been returned."),
        ("Delayed projects",
         "Informal coordination leads to missed deliveries, scheduling conflicts, and "
         "cost overruns."),
        ("Local businesses losing out",
         "International developers import their own equipment because local inventory "
         "is impossible to find and book."),
        ("No business infrastructure",
         "Equipment owners manage their entire operation from memory — no scheduling, "
         "no payment tracking, no reporting."),
    ]
    gap = 0.35
    w = (CW - gap) / 2
    h = 2.0
    y0 = 1.95
    for i, (title, body) in enumerate(items):
        x = M + (i % 2) * (w + gap)
        y = y0 + (i // 2) * (h + gap)
        edged_card(s, x, y, w, h, ORANGE, "left")
        textbox(s, x + 0.45, y + 0.25, w - 0.85, h - 0.5, [
            dict(text=title, size=14, bold=True, color=WHITE, after=8),
            dict(text=body, size=11, color=MUTED, line=1.2),
        ], anchor=MIDDLE)


def slide_insight():
    s = new_slide()
    text(s, M, 0.8, CW, 0.3, "THE INSIGHT", 10, GREEN, bold=True, align=CENTER, spc=400)
    text(s, 1.2, 1.85, W - 2.4, 1.2, "The problem isn't that people won't use technology.",
         32, WHITE, bold=True, align=CENTER, anchor=BOTTOM)
    text(s, 1.2, 3.15, W - 2.4, 0.9, "It's that no technology met them where they already are.",
         26, ORANGE, bold=True, align=CENTER)
    cols = [
        "Contractors are on WhatsApp and SMS all day. Relay makes those conversations productive.",
        "Equipment owners need more than bookings. They need a business.",
    ]
    gap = 0.5
    w = (CW - gap) / 2
    y = 4.85
    for i, body in enumerate(cols):
        x = M + i * (w + gap)
        card(s, x, y, w, 1.45)
        circle(s, x + 0.4, y + 0.6, 0.22, GREEN if i == 0 else ORANGE)
        text(s, x + 0.9, y + 0.2, w - 1.3, 1.05, body, 13, MUTED, anchor=MIDDLE, line=1.2)


def slide_solution():
    s = new_slide()
    headline(s, "Relay.", 48, y=0.45, h=0.95, font=BLACK, bold=False)
    headline(s, "One platform. Two products.", 20, y=1.45, h=0.45, color=ORANGE)
    gap = 0.4
    w = (CW - gap) / 2
    y, h = 2.35, 4.4
    cards = [
        dict(fill=GREEN, label="FOR CONTRACTORS", label_c=WHITE,
             title="Book equipment by text.",
             body="Message what you need. Get options. Confirm. Pay. All in one SMS or "
                  "WhatsApp conversation. No app. No calls. No friction.",
             body_c=WHITE, tag="→ SMS + WhatsApp native", tag_c=WHITE),
        dict(fill=SURFACE, label="FOR EQUIPMENT OWNERS", label_c=GREEN,
             title="A business backend, finally.",
             body="Booking calendar. Payment tracking. Payout history. Utilisation reports. "
                  "Invoice generation. Fleet management. All in one web portal.",
             body_c=MUTED, tag="→ Web portal + mobile", tag_c=GREEN),
    ]
    for i, c in enumerate(cards):
        x = M + i * (w + gap)
        card(s, x, y, w, h, fill=c["fill"], radius=0.14)
        px = x + 0.5
        iw = w - 1.0
        text(s, px, y + 0.5, iw, 0.3, c["label"], 10, c["label_c"], bold=True, spc=300)
        text(s, px, y + 0.95, iw, 0.6, c["title"], 22, WHITE, font=BLACK)
        text(s, px, y + 1.8, iw, 1.6, c["body"], 12, c["body_c"], line=1.3)
        text(s, px, y + h - 0.85, iw, 0.35, c["tag"], 11, c["tag_c"], italic=True)


def slide_how_contractor():
    s = new_slide()
    headline(s, "How a booking happens.", 32, y=0.5)
    text(s, M, 1.12, CW, 0.35, "From first text to confirmed delivery — under 2 minutes.", 14, MUTED)
    steps = [
        ("Text", "Contractor describes what they need in plain English"),
        ("Match", "Relay's AI checks live availability and returns options with pricing"),
        ("Confirm", "Contractor confirms. Payment link sent for 30% deposit."),
        ("Done", "Equipment owner notified automatically by SMS"),
    ]
    gap = 0.6
    w = (CW - 3 * gap) / 4
    cy, d = 1.7, 0.56
    y, h = 2.4, 1.45
    for i, (title, body) in enumerate(steps):
        x = M + i * (w + gap)
        c = circle(s, x + (w - d) / 2, cy, d, GREEN)
        fill_frame(c.text_frame, [dict(text=str(i + 1), size=20, bold=True, align=CENTER)],
                   anchor=MIDDLE)
        card(s, x, y, w, h)
        textbox(s, x + 0.25, y + 0.2, w - 0.5, h - 0.4, [
            dict(text=title, size=14, bold=True, after=4),
            dict(text=body, size=11, color=MUTED, line=1.15),
        ])
        if i < 3:
            shape(s, MSO_SHAPE.RIGHT_ARROW, x + w + 0.15, y + h / 2 - 0.13, gap - 0.3, 0.26, GREEN)

    # Mock SMS thread
    by, bh = 4.15, 2.7
    card(s, M, by, CW, bh, radius=0.12)
    text(s, M + 0.35, by + 0.18, 3, 0.25, "SMS  ·  Relay", 9, MUTED, bold=True, spc=150)
    msgs = [
        ("left", "Need a 20-ton excavator in St Philip, Monday to Wednesday"),
        ("right", "Clarke Equipment available. $850/day. 3 days = $2,550. Deposit $765. "
                  "Delivery address?"),
        ("left", "Sandy Lane construction site"),
        ("right", "Booked. Pay here: relay.co/pay/8821. Owner notified."),
    ]
    yy = by + 0.5
    for side, m in msgs:
        fill, col = (WHITE, BG) if side == "left" else (GREEN, WHITE)
        hh = bubble(s, M + 0.35, M + CW - 0.35, yy, m, 11, fill, col, side, max_w=6.6)
        yy += hh + 0.1


def slide_how_owner():
    s = new_slide()
    headline(s, "What equipment owners get.", 32, y=0.5)
    text(s, M, 1.12, CW, 0.35, "A complete business backend — built around their equipment.",
         14, MUTED)
    tiles = [
        ("Booking Calendar", "See every confirmed, pending, and completed booking at a glance"),
        ("Payment Tracking", "Know exactly what's been paid, what's outstanding, and what Relay "
                             "has transferred"),
        ("Fleet Management", "Add equipment, set availability, update pricing in real time"),
        ("Invoice Generation", "Automatic invoices for every booking, downloadable for accounting"),
        ("Utilisation Reports", "See which machines earn the most and which sit idle"),
        ("Payout History", "Full record of every transfer from Relay to their account"),
    ]
    gap = 0.35
    w = (CW - 2 * gap) / 3
    h = 2.1
    y0 = 1.95
    for i, (title, body) in enumerate(tiles):
        x = M + (i % 3) * (w + gap)
        y = y0 + (i // 3) * (h + gap)
        edged_card(s, x, y, w, h, GREEN, "left")
        text(s, x + 0.4, y + 0.35, 1, 0.3, f"0{i + 1}", 10, GREEN, bold=True, spc=200)
        textbox(s, x + 0.4, y + 0.7, w - 0.75, h - 0.9, [
            dict(text=title, size=13, bold=True, after=6),
            dict(text=body, size=11, color=MUTED, line=1.2),
        ])


def slide_contractor_mockup():
    s = new_slide()
    headline(s, "The contractor experience.", 28, y=0.55, h=0.55)
    text(s, M, 1.12, 6, 0.35, "SMS and WhatsApp — wherever they already are.", 13, MUTED)
    dot_bullets(s, M, 2.55, 5.6, [
        "Responds in plain English — no commands or codes needed",
        "Knows Barbados parishes, terrain, and equipment types",
        "Remembers the conversation — context survives across sessions",
    ], size=16, gap=1.15)

    # Phone
    pw, ph = 3.75, 6.35
    px, py = 8.3, 0.45
    card(s, px, py, pw, ph, fill=SURFACE, radius=0.45, line=WHITE, line_w=1.44)
    # Screen
    sx, sy, sw, sh = px + 0.14, py + 0.14, pw - 0.28, ph - 0.28
    card(s, sx, sy, sw, sh, fill=BG, radius=0.34)
    card(s, px + pw / 2 - 0.55, py + 0.24, 1.1, 0.2, fill=SURFACE, radius=0.1)  # notch
    # Contact header
    circle(s, sx + sw / 2 - 0.22, sy + 0.42, 0.44, GREEN)
    text(s, sx + sw / 2 - 0.22, sy + 0.42, 0.44, 0.44, "R", 14, WHITE, bold=True,
         align=CENTER, anchor=MIDDLE)
    text(s, sx, sy + 0.9, sw, 0.25, "Relay", 11, WHITE, bold=True, align=CENTER)
    text(s, sx, sy + 1.12, sw, 0.2, "Text message · Today 9:41 AM", 8, MUTED, align=CENTER)
    rect(s, sx + 0.2, sy + 1.42, sw - 0.4, 0.01, SURFACE)

    msgs = [
        ("right", "I need a mini excavator in Christ Church next week"),
        ("left", "What dates and how many days?"),
        ("right", "Monday to Thursday"),
        ("left", "Found 2 options:\n1. Clarke Mini 3T — $320/day\n2. Bradshaw Mini 2T — $280/day\n"
                 "Which works?"),
        ("right", "Option 1"),
        ("left", "Booked. Deposit $384 due now: relay.co/pay/4421. Owner notified. "
                 "Calendar invite sent."),
    ]
    yy = sy + 1.58
    for side, m in msgs:
        fill, col = (GREEN, WHITE) if side == "left" else (WHITE, BG)
        hh = bubble(s, sx + 0.18, sx + sw - 0.18, yy, m, 10, fill, col, side, max_w=2.55)
        yy += hh + 0.11
    card(s, px + pw / 2 - 0.6, py + ph - 0.32, 1.2, 0.06, fill=MUTED, radius=0.03)  # home bar


def slide_owner_mockup():
    s = new_slide()
    headline(s, "The owner dashboard.", 28, y=0.55, h=0.55)
    text(s, M, 1.12, 6, 0.35, "Everything they need to run their equipment business.", 13, MUTED)
    dot_bullets(s, M, 2.55, 3.5, [
        "Real-time booking notifications by SMS",
        "Automatic invoices on every confirmed booking",
        "85% payout — Relay takes 10%, owner keeps the rest",
    ], size=15, gap=1.15)

    # Laptop lid + screen
    lx, ly, lw, lh = 4.55, 1.75, 8.2, 4.4
    card(s, lx, ly, lw, lh, fill=SURFACE, radius=0.18, line=EDGE, line_w=1)
    circle(s, lx + lw / 2 - 0.03, ly + 0.06, 0.06, EDGE)  # camera
    x0, y0, sw, sh = lx + 0.16, ly + 0.18, lw - 0.32, lh - 0.34
    rect(s, x0, y0, sw, sh, BG)
    # Base
    shape(s, MSO_SHAPE.TRAPEZOID, lx - 0.35, ly + lh, lw + 0.7, 0.2, EDGE).rotation = 180
    card(s, lx + lw / 2 - 0.7, ly + lh, 1.4, 0.07, fill=SURFACE, radius=0.03)

    # Top bar
    rect(s, x0, y0, sw, 0.45, SURFACE)
    text(s, x0 + 0.25, y0, 2, 0.45, "Relay", 14, GREEN, bold=True, anchor=MIDDLE)
    text(s, x0 + sw - 3.25, y0, 3, 0.45, "Welcome back, Michael", 10, WHITE, align=RIGHT,
         anchor=MIDDLE)

    # Stat cards
    stats = [("Active Bookings", "4", WHITE), ("This Month", "$8,400", GREEN),
             ("Equipment Listed", "7", WHITE), ("Payout Pending", "$2,380", ORANGE)]
    pad, g = 0.22, 0.15
    cw = (sw - 2 * pad - 3 * g) / 4
    cy = y0 + 0.65
    for i, (label, val, col) in enumerate(stats):
        cx = x0 + pad + i * (cw + g)
        card(s, cx, cy, cw, 0.85, radius=0.08)
        text(s, cx + 0.15, cy + 0.12, cw - 0.3, 0.2, label, 8, MUTED)
        text(s, cx + 0.15, cy + 0.36, cw - 0.3, 0.4, val, 18, col, bold=True)

    # Bookings table
    ty = cy + 1.1
    text(s, x0 + pad, ty, 3, 0.25, "Recent bookings", 10, WHITE, bold=True)
    cols = [("Equipment", 1.45), ("Booking Ref", 1.1), ("Dates", 0.85),
            ("Contractor", 1.65), ("Status", 1.05), ("Amount", 0.8)]
    rows = [
        ("20T Excavator", "#REL-4821", "Oct 1-3", "Clarke Construction", "Confirmed", "$2,550"),
        ("Dump Truck 10T", "#REL-4819", "Sep 30", "Bradshaw Ltd", "Completed", "$1,350"),
        ("Generator 50kW", "#REL-4817", "Oct 5-7", "One Construction", "Pending", "$1,080"),
    ]
    status_c = {"Confirmed": GREEN, "Completed": EDGE, "Pending": ORANGE}
    tw = sw - 2 * pad
    scale = (tw - 0.3) / sum(c[1] for c in cols)
    hy = ty + 0.35
    rh = 0.46

    def row_cells(y, values, header=False):
        cx = x0 + pad + 0.15
        for (name, cwid), v in zip(cols, values):
            cwid *= scale
            last = name == "Amount"
            if name == "Status" and not header:
                pill = card(s, cx, y + (rh - 0.24) / 2, 0.82, 0.24, fill=status_c[v], radius=0.12)
                fill_frame(pill.text_frame, [dict(text=v, size=7.5, bold=True, align=CENTER)],
                           anchor=MIDDLE)
            else:
                text(s, cx, y, cwid, rh if not header else 0.3, v,
                     7.5 if header else 9, MUTED if header else WHITE,
                     bold=header or last, align=RIGHT if last else LEFT, anchor=MIDDLE,
                     spc=80 if header else None)
            cx += cwid

    rect(s, x0 + pad, hy, tw, 0.3, SURFACE)
    row_cells(hy, [c[0].upper() for c in cols], header=True)
    for i, r in enumerate(rows):
        y = hy + 0.3 + i * rh
        rect(s, x0 + pad, y, tw, rh, BG if i % 2 == 0 else SURFACE)
        row_cells(y, r)
    # Frame the table so the BG-coloured rows still read as a table
    shape(s, MSO_SHAPE.RECTANGLE, x0 + pad, hy, tw, 0.3 + 3 * rh, None, line=SURFACE, line_w=1)


def slide_traction():
    s = new_slide()
    headline(s, "Built in 21 days.", 36, y=0.5, h=0.7)
    headline(s, "Piloting now with One Construction — largest contractor in Barbados.", 18,
             y=1.25, h=0.4, color=ORANGE)
    live = [
        "AI booking agent responding to real SMS messages",
        "Live equipment database with availability conflict detection",
        "Stripe payment processing — 30% deposit + 70% on completion",
        "Automatic equipment owner SMS notifications",
        "Persistent conversation memory",
        "Deployed 24/7 — Railway hosting, no downtime",
        "buildrelay.co live",
    ]
    nxt = [
        "Owner web portal — in development",
        "WhatsApp Business API — pending approval",
        "WiPay integration — local Caribbean payments",
        "Barbados public launch — Q4 2026",
        "Guyana expansion — in motion",
        "Trades scheduling — Phase 2",
    ]
    gap = 0.4
    w = (CW - gap) / 2
    y, h = 2.0, 4.8
    for i, (title, items, mark, col) in enumerate([
        ("What's live", live, "✓", GREEN), ("What's next", nxt, "→", ORANGE)]):
        x = M + i * (w + gap)
        card(s, x, y, w, h)
        text(s, x + 0.45, y + 0.35, w - 0.9, 0.4, title, 18, WHITE, bold=True)
        paras = [dict(runs=[dict(text=mark + "\t", size=14, color=col, bold=True),
                            dict(text=it, size=13, color=WHITE if i == 0 else MUTED)],
                      after=14, hang=0.35) for it in items]
        textbox(s, x + 0.45, y + 0.95, w - 0.8, h - 1.2, paras)


def slide_market():
    s = new_slide()
    headline(s, "Barbados is the proof of concept.", 32, y=0.5)
    text(s, M, 1.15, CW, 0.4, "The Caribbean is the opportunity.", 18, MUTED)
    markets = [
        ("🇧🇧", "Barbados", "$1.5-2B", "Construction market", "PILOT UNDERWAY", ORANGE, True),
        ("🇬🇾", "Guyana", "$4B+", "Oil boom construction", "EXPANSION IN MOTION", ORANGE, True),
        ("🇹🇹", "Trinidad", "$2B+", "Regional hub", "YEAR 2", MUTED, False),
        ("🇯🇲", "Jamaica", "$3B+", "Tourism + development", "YEAR 2", MUTED, False),
    ]
    gap = 0.3
    w = (CW - 3 * gap) / 4
    y, h = 2.0, 3.35
    for i, (flag, name, val, desc, status, sc, sb) in enumerate(markets):
        x = M + i * (w + gap)
        edged_card(s, x, y, w, h, GREEN, "top")
        px, iw = x + 0.35, w - 0.7
        textbox(s, px, y + 0.4, iw, 0.4, [dict(runs=[
            dict(text=flag + "  ", size=16, color=WHITE),
            dict(text=name, size=16, color=GREEN, bold=True)])])
        text(s, px, y + 0.95, iw, 0.75, val, 36, WHITE, bold=True, anchor=MIDDLE)
        text(s, px, y + 1.75, iw, 0.3, desc, 11, MUTED)
        text(s, px, y + h - 0.7, iw, 0.3, status, 10, sc, bold=sb, spc=150)
    text(s, M, 5.75, CW, 0.45, "Total Caribbean construction market: $8B+", 20, WHITE,
         bold=True, align=CENTER)
    text(s, M, 6.25, CW, 0.35, "Initial addressable marketplace in Barbados: $20-30M annually",
         14, MUTED, align=CENTER)


def slide_business_model():
    s = new_slide()
    headline(s, "Simple. Scalable. High margin.", 32, y=0.5)

    # Fee donut from two block arcs. Angles run clockwise from 3 o'clock;
    # python-pptx scales raw OOXML angle values (60000ths of a degree) by 1/100000.
    d = 3.2
    dx, dy = M + 0.1, 1.75

    def arc(start, end, fill, line=None):
        a = shape(s, MSO_SHAPE.BLOCK_ARC, dx, dy, d, d, fill, line=line, line_w=1)
        a.adjustments[0] = start * 0.6
        a.adjustments[1] = end * 0.6
        a.adjustments[2] = 0.2
        return a

    arc(307.5, 268.5, SURFACE, line=EDGE)  # owner 90%
    arc(271, 305, GREEN)  # Relay 10%
    text(s, dx, dy + d / 2 - 0.45, d, 0.55, "10%", 30, GREEN, bold=True, align=CENTER,
         anchor=BOTTOM)
    text(s, dx, dy + d / 2 + 0.12, d, 0.3, "per booking", 11, MUTED, align=CENTER)

    lx = dx + d + 0.3
    for i, (label, col, edge) in enumerate([("Relay — 10%", GREEN, None),
                                            ("Equipment Owner — 90%", SURFACE, EDGE)]):
        yy = dy + 1.15 + i * 0.6
        card(s, lx, yy + 0.055, 0.24, 0.24, fill=col, radius=0.05, line=edge, line_w=1)
        text(s, lx + 0.36, yy, 2.2, 0.35, label, 12, WHITE, bold=True, anchor=MIDDLE)

    text(s, M, 5.45, 5.9, 0.6,
         "No subscription fees. No listing fees. Pure transaction revenue.", 13, MUTED,
         italic=True)

    years = [
        ("Year 1", "$150,000", GREEN, "Platform revenue — Barbados pilot"),
        ("Year 2", "$500,000", GREEN, "Two markets — Barbados + Guyana"),
        ("Year 3", "$1M+", ORANGE, "Trades vertical live + regional scale"),
    ]
    rx, rw = 7.35, W - M - 7.35
    h, gap = 1.3, 0.25
    y0 = 1.55
    for i, (label, val, col, desc) in enumerate(years):
        y = y0 + i * (h + gap)
        card(s, rx, y, rw, h)
        text(s, rx + 0.4, y + 0.22, 2, 0.25, label.upper(), 10, MUTED, bold=True, spc=200)
        text(s, rx + 0.4, y + 0.45, 2.9, 0.65, val, 32, col, bold=True, anchor=MIDDLE)
        text(s, rx + 3.1, y + 0.2, rw - 3.45, h - 0.4, desc, 11, WHITE, anchor=MIDDLE,
             line=1.2)
    text(s, rx, y0 + 3 * h + 2 * gap + 0.2, rw, 0.3,
         "Based on $20-30M addressable marketplace at 10% fee. Ultra conservative.", 10,
         MUTED, italic=True)


def slide_team():
    s = new_slide()
    headline(s, "Built by people inside the problem.", 32, y=0.5)
    people = [
        ("Chris Corless", "CC", "Co-Founder — Product & Technology",
         "Venture Architect with 20+ years building platforms across music, media, wellness, "
         "and real estate. Built Relay's entire technical stack in 21 days. Based between "
         "Toronto and Barbados."),
        ("James Edghill", "JE", "Co-Founder — Market & Operations",
         "Operates One Construction — one of the largest construction companies in Barbados. "
         "Deep equipment owner network and firsthand knowledge of every coordination problem "
         "Relay solves. First pilot customer."),
    ]
    gap = 0.4
    w = (CW - gap) / 2
    y, h = 1.6, 3.85
    for i, (name, initials, role, bio) in enumerate(people):
        x = M + i * (w + gap)
        edged_card(s, x, y, w, h, GREEN, "top")
        c = circle(s, x + 0.5, y + 0.5, 0.85, GREEN if i == 0 else ORANGE)
        fill_frame(c.text_frame, [dict(text=initials, size=18, font=BLACK, align=CENTER)],
                   anchor=MIDDLE)
        text(s, x + 0.5, y + 1.6, w - 1, 0.5, name, 22, WHITE, font=BLACK)
        text(s, x + 0.5, y + 2.12, w - 1, 0.3, role, 12, GREEN, bold=True)
        text(s, x + 0.5, y + 2.6, w - 1, 1.4, bio, 11, MUTED, line=1.3)
    text(s, M, 5.95, CW, 0.45, "We didn't discover this problem. We're inside it.", 16, ORANGE,
         bold=True, italic=True, align=CENTER)


def slide_close():
    s = new_slide()
    text(s, M, 1.2, CW, 1.3, "Relay", 64, WHITE, font=BLACK, align=CENTER, anchor=BOTTOM)
    text(s, M, 2.65, CW, 0.5, "The operating system for Caribbean construction.", 20, MUTED,
         align=CENTER)
    rect(s, W / 2 - 4, H / 2 - 0.015, 8, 0.03, GREEN)
    text(s, M, 4.45, CW, 0.45, "buildrelay.co", 18, GREEN, bold=True, align=CENTER)
    text(s, M, 4.95, CW, 0.4, "hello@buildrelay.co", 14, WHITE, align=CENTER)


for build in (slide_cover, slide_problem_1, slide_problem_2, slide_insight, slide_solution,
              slide_how_contractor, slide_how_owner, slide_contractor_mockup,
              slide_owner_mockup, slide_traction, slide_market, slide_business_model,
              slide_team, slide_close):
    build()

prs.save(OUT)
print(f"Saved {OUT} ({len(prs.slides)} slides)")
