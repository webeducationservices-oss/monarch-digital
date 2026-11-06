#!/usr/bin/env python3
"""Render illustrative restaurant software screens (sample data, fictional restaurant).

These are generic examples of the kind of software Monarch builds. They are NOT
screenshots of any client's app. Output: images/rebrand/mock-<name>.webp

  python3 _build/mockups.py            # render all
  python3 _build/mockups.py host lms   # render some
"""
import os
import subprocess
import sys
import tempfile

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from icons import icon  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "images", "rebrand")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
FONTS = "file://" + os.path.join(ROOT, "fonts")
os.makedirs(OUT, exist_ok=True)

CSS = f"""
@font-face{{font-family:Inter;src:url('{FONTS}/inter-400.woff2');font-weight:400}}
@font-face{{font-family:Inter;src:url('{FONTS}/inter-500.woff2');font-weight:500}}
@font-face{{font-family:Inter;src:url('{FONTS}/inter-600.woff2');font-weight:600}}
@font-face{{font-family:Inter;src:url('{FONTS}/inter-700.woff2');font-weight:700}}
@font-face{{font-family:Montserrat;src:url('{FONTS}/montserrat-700.woff2');font-weight:700}}
@font-face{{font-family:Montserrat;src:url('{FONTS}/montserrat-800.woff2');font-weight:800}}
:root{{--ink:#1F1F1F;--ink2:#2A2A2A;--muted:#6B7280;--line:#E8E3D8;--cream:#FAF8F3;--card:#FFFFFF;
--gold:#D4A843;--gold-d:#A9822C;--gold-soft:#F7EDD3;--teal:#2EC4B6;--teal-d:#17988C;--teal-soft:#DDF4F1;
--red:#D25A4E;--red-soft:#FBE5E2;--amber:#E39B2D;--amber-soft:#FCEFD8;--violet:#8B7CF6}}
*{{box-sizing:border-box}}
body{{margin:0;font-family:Inter,Arial,sans-serif;color:var(--ink);background:var(--cream);overflow:hidden;-webkit-font-smoothing:antialiased}}
svg{{width:18px;height:18px;flex:none}}
.app{{display:grid;grid-template-columns:224px 1fr;height:100vh}}
.side{{background:var(--ink);color:#c9c9c9;padding:22px 14px;display:flex;flex-direction:column;gap:4px}}
.brand{{display:flex;align-items:center;gap:10px;color:#fff;font-family:Montserrat;font-weight:800;font-size:17px;margin:0 6px 26px}}
.mark{{width:32px;height:32px;border-radius:9px;background:linear-gradient(135deg,var(--gold),var(--gold-d));display:grid;place-items:center;color:var(--ink);font-size:15px}}
.nav{{display:flex;align-items:center;gap:11px;padding:10px 12px;border-radius:9px;font-size:14px;font-weight:500}}
.nav.on{{background:rgba(212,168,67,.15);color:var(--gold)}}
.side .foot{{margin-top:auto;font-size:12px;color:#8b8b8b;padding:10px 12px;border-top:1px solid #333}}
.main{{display:flex;flex-direction:column;min-width:0}}
.top{{height:66px;background:#fff;border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:space-between;padding:0 28px;gap:16px}}
.top h1{{font-family:Montserrat;font-weight:700;font-size:20px;margin:0}}
.top .sub{{font-size:13px;color:var(--muted);margin-top:2px}}
.pill{{display:inline-flex;align-items:center;gap:6px;padding:6px 12px;border-radius:999px;font-size:12.5px;font-weight:600;white-space:nowrap}}
.p-gold{{background:var(--gold-soft);color:var(--gold-d)}} .p-teal{{background:var(--teal-soft);color:var(--teal-d)}}
.p-red{{background:var(--red-soft);color:var(--red)}} .p-amber{{background:var(--amber-soft);color:#A86A10}}
.p-ink{{background:var(--ink);color:#fff}} .p-line{{border:1px solid var(--line);color:var(--muted);background:#fff}}
.btn{{display:inline-flex;align-items:center;gap:8px;padding:10px 16px;border-radius:10px;font-weight:600;font-size:13.5px;background:var(--ink);color:#fff}}
.btn.gold{{background:var(--gold);color:var(--ink)}} .btn.ghost{{background:#fff;color:var(--ink);border:1px solid var(--line)}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:14px}}
.h{{font-family:Montserrat;font-weight:700}}
.muted{{color:var(--muted)}} .small{{font-size:12.5px}}
.row{{display:flex;align-items:center;gap:10px}}
.illus{{position:fixed;right:14px;bottom:10px;font-size:11px;color:#9a958a;letter-spacing:.3px}}
"""


def page(body, extra_css="", dark=False):
    bg = "#121212" if dark else "var(--cream)"
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}body{{background:{bg}}}{extra_css}</style></head>
<body>{body}<div class="illus">Illustrative screen &middot; sample data</div></body></html>"""


def sidebar(active):
    items = [("home", "Today"), ("calendar", "Reservations"), ("map", "Floor"), ("users", "Team"),
             ("clock", "Schedule"), ("file-text", "Academy"), ("zap", "Assistant"), ("database", "Reports")]
    links = "".join(
        f'<div class="nav{" on" if label == active else ""}">{icon(i)}<span>{label}</span></div>'
        for i, label in items)
    return f"""<aside class="side"><div class="brand"><div class="mark">C</div>Cedar &amp; Salt</div>{links}
<div class="foot">Dinner service &middot; Friday</div></aside>"""


# ---------------------------------------------------------------- host stand
def host():
    tables = [
        # (x, y, w, h, label, seats, state, info, round)
        (40, 40, 92, 92, "1", 2, "seated", "38m", True), (160, 40, 92, 92, "2", 2, "open", "", True),
        (280, 40, 92, 92, "3", 2, "reserved", "7:45", True), (400, 40, 92, 92, "4", 2, "seated", "12m", True),
        (40, 180, 150, 96, "10", 4, "seated", "51m", False), (220, 180, 150, 96, "11", 4, "check", "Check", False),
        (400, 180, 150, 96, "12", 4, "open", "", False), (40, 320, 150, 96, "14", 4, "seated", "22m", False),
        (220, 320, 150, 96, "15", 6, "reserved", "8:00", False), (400, 320, 150, 96, "16", 4, "bus", "Bus", False),
        (40, 460, 330, 100, "21 + 22", 8, "hold", "Combined", False), (400, 460, 150, 100, "23", 4, "seated", "6m", False),
        (588, 40, 112, 520, "Bar", 12, "bar", "9 seated", False),
    ]
    colors = {"seated": ("#FFF8E8", "var(--gold)", "var(--gold-d)"), "open": ("#fff", "var(--teal)", "var(--teal-d)"),
              "reserved": ("#F4F2EE", "#B9B2A4", "#7d776b"), "check": ("#FFF1E1", "var(--amber)", "#A86A10"),
              "bus": ("#FBE9E7", "var(--red)", "var(--red)"), "hold": ("#EAF7F5", "var(--teal)", "var(--teal-d)"),
              "bar": ("#F6F4EF", "#CFC7B6", "#6b6558")}
    tiles = ""
    for x, y, w, h, label, seats, state, info, rnd in tables:
        bg, border, fg = colors[state]
        radius = "50%" if rnd else "14px"
        tiles += f"""<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;border-radius:{radius};
background:{bg};border:2.5px solid {border};display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px">
<div class="h" style="font-size:18px;color:var(--ink)">{label}</div><div class="small" style="color:{fg};font-weight:600">{info or str(seats) + " seats"}</div></div>"""
    wait = [("Maya R.", 2, "15 min", "9 min", "teal"), ("The Patel party", 5, "35 min", "21 min", "gold"),
            ("Luis P.", 3, "20 min", "4 min", "teal"), ("Grace K.", 2, "15 min", "1 min", "teal")]
    wl = "".join(f"""<div style="display:flex;align-items:center;justify-content:space-between;padding:14px 0;border-bottom:1px solid var(--line)">
<div><div style="font-weight:600;font-size:14.5px">{n} <span class="muted" style="font-weight:500">&middot; {p}</span></div>
<div class="small muted">Quoted {q} &middot; waiting {e}</div></div>
<div class="pill p-{c}">{icon("message-circle")}Table ready</div></div>""" for n, p, q, e, c in wait)
    body = f"""<div class="app">{sidebar("Floor")}<div class="main">
<div class="top"><div><h1>Host Stand</h1><div class="sub">Friday &middot; 7:15 PM &middot; 86 covers booked</div></div>
<div class="row"><span class="pill p-teal">{icon("check-circle")}Pacing 12 of 15 per 15 min</span>
<span class="pill p-line">{icon("clock")}Preview: 8:00 PM</span><span class="btn gold">{icon("users")}Seat walk-in</span></div></div>
<div style="display:grid;grid-template-columns:1fr 380px;gap:22px;padding:22px 28px;flex:1;min-height:0">
<div class="card" style="position:relative;padding:0;overflow:hidden">
<div style="position:absolute;left:24px;top:16px;right:24px;display:flex;gap:16px" class="small muted">
<span class="row" style="gap:6px"><i style="width:10px;height:10px;border-radius:3px;background:var(--gold)"></i>Seated</span>
<span class="row" style="gap:6px"><i style="width:10px;height:10px;border-radius:3px;background:var(--teal)"></i>Open</span>
<span class="row" style="gap:6px"><i style="width:10px;height:10px;border-radius:3px;background:#B9B2A4"></i>Reserved</span>
<span class="row" style="gap:6px"><i style="width:10px;height:10px;border-radius:3px;background:var(--amber)"></i>Check dropped</span>
<span class="row" style="gap:6px"><i style="width:10px;height:10px;border-radius:3px;background:var(--red)"></i>Needs bussing</span></div>
<div style="position:absolute;left:34px;top:54px;width:760px;height:600px">{tiles}</div></div>
<div style="display:flex;flex-direction:column;gap:18px;min-height:0">
<div class="card" style="padding:18px 20px"><div class="row" style="justify-content:space-between">
<div class="h" style="font-size:16px">Waitlist</div><span class="pill p-gold">4 parties &middot; 12 guests</span></div>{wl}</div>
<div class="card" style="padding:18px 20px"><div class="h" style="font-size:16px;margin-bottom:10px">Suggested for Grace K. (2)</div>
<div class="row" style="justify-content:space-between;padding:8px 0"><span><b>Table 2</b> <span class="muted small">window, server Ava</span></span><span class="pill p-teal">Best fit</span></div>
<div class="row" style="justify-content:space-between;padding:8px 0"><span><b>Table 12</b> <span class="muted small">opens in ~6 min</span></span><span class="pill p-line">Option</span></div></div>
</div></div></div></div>"""
    return page(body), (1440, 780)


# ---------------------------------------------------------------- schedule
def schedule():
    days = ["Mon 10", "Tue 11", "Wed 12", "Thu 13", "Fri 14", "Sat 15", "Sun 16"]
    groups = {
        "Kitchen": [("Daniel T.", "Sous", ["2-10", "2-10", "", "2-10", "2-11", "2-11", ""]),
                    ("Rosa M.", "Line", ["", "3-10", "3-10", "3-10", "3-11", "3-11", "11-7"]),
                    ("Kenji A.", "Prep", ["8-4", "8-4", "8-4", "", "8-4", "8-4", ""])],
        "Dining room": [("Ava L.", "Server", ["", "4-11", "4-11", "4-11", "4-12", "4-12", ""]),
                        ("Marcus B.", "Server", ["4-10", "", "4-10", "4-11", "4-12", "11-5", "11-5"]),
                        ("Priya S.", "Host", ["", "", "4-10", "4-10", "4-11", "4-11", "10-4"])],
        "Bar": [("Jordan W.", "Bartender", ["4-12", "4-12", "", "", "4-1", "4-1", "12-8"]),
                ("Elena F.", "Barback", ["", "", "5-12", "5-12", "5-1", "5-1", ""])],
    }
    head = "".join(f'<div class="h" style="font-size:13px;padding:10px 8px;text-align:center">{d}</div>' for d in days)
    rows = ""
    tone = {"Kitchen": "gold", "Dining room": "teal", "Bar": "amber"}
    for g, people in groups.items():
        rows += f'<div style="grid-column:1/-1;padding:12px 14px 6px" class="small muted"><b style="color:var(--ink)">{g}</b> &middot; scheduler assigned</div>'
        for name, role, shifts in people:
            rows += f'<div style="padding:10px 14px;border-top:1px solid var(--line)"><div style="font-weight:600;font-size:14px">{name}</div><div class="small muted">{role}</div></div>'
            for s in shifts:
                cell = f'<span class="pill p-{tone[g]}" style="width:100%;justify-content:center">{s}</span>' if s else ""
                rows += f'<div style="padding:10px 6px;border-top:1px solid var(--line);display:flex;align-items:center">{cell}</div>'
    cover = ["ok", "ok", "ok", "ok", "low", "ok", "ok"]
    covbar = "".join(
        f'<div style="padding:8px 6px"><div style="height:8px;border-radius:6px;background:{"var(--teal)" if c == "ok" else "var(--amber)"}"></div>'
        f'<div class="small" style="text-align:center;margin-top:5px;color:{"var(--teal-d)" if c == "ok" else "#A86A10"}">{"Covered" if c == "ok" else "1 short"}</div></div>'
        for c in cover)
    body = f"""<div class="app">{sidebar("Schedule")}<div class="main">
<div class="top"><div><h1>Week of November 10</h1><div class="sub">Draft built from the book, minimums, and last 8 weeks</div></div>
<div class="row"><span class="pill p-gold">{icon("clock")}312 hours &middot; 27.4% of forecast sales</span>
<span class="pill p-amber">{icon("alert-triangle")}1 part-timer over 29 hrs</span>
<span class="btn gold">{icon("send")}Publish and text staff</span></div></div>
<div style="padding:22px 28px;flex:1;min-height:0"><div class="card" style="overflow:hidden">
<div style="display:grid;grid-template-columns:190px repeat(7,1fr);background:#FBFAF6;border-bottom:1px solid var(--line)">
<div class="small muted" style="padding:10px 14px">Team</div>{head}</div>
<div style="display:grid;grid-template-columns:190px repeat(7,1fr)">{rows}
<div style="padding:10px 14px;border-top:1px solid var(--line)" class="small muted"><b style="color:var(--ink)">Coverage</b></div>{covbar}</div>
</div>
<div class="row" style="margin-top:16px;gap:12px"><span class="pill p-line">{icon("refresh")}2 swap requests waiting</span>
<span class="pill p-line">{icon("calendar")}3 time-off requests approved</span><span class="pill p-teal">{icon("check-circle")}No split shifts</span></div>
</div></div></div>"""
    return page(body), (1440, 860)


# ---------------------------------------------------------------- kitchen display
def kitchen():
    tickets = [("12", "4", "6:12", "ok", ["Burrata", "Crudo", "2 Ribeye MR", "Halibut"], "Shellfish"),
               ("4", "2", "9:40", "ok", ["Gnocchi", "Short rib"], ""),
               ("15", "6", "13:05", "warn", ["2 Wedge", "Oysters", "3 Ribeye", "Duck"], "Tree nuts"),
               ("10", "4", "17:22", "late", ["Chicken", "2 Halibut", "Risotto"], ""),
               ("23", "4", "2:30", "ok", ["Crudo", "Burrata"], "Gluten"),
               ("Bar 7", "2", "4:51", "ok", ["Fries", "Burger"], "")]
    tone = {"ok": ("var(--teal)", "#0F2E2B"), "warn": ("var(--amber)", "#33240B"), "late": ("var(--red)", "#341613")}
    cards = ""
    for t, guests, clock, state, items, allergy in tickets:
        c, bg = tone[state]
        alg = f'<div class="pill" style="background:#3A1714;color:#FF9C8F;margin-top:10px">{icon("alert-triangle")}{allergy}</div>' if allergy else ""
        lis = "".join(f'<div style="padding:7px 0;border-bottom:1px solid #2c2c2c;font-size:15px">{i}</div>' for i in items)
        cards += f"""<div style="background:#1C1C1C;border:1px solid #2E2E2E;border-radius:14px;overflow:hidden">
<div style="background:{bg};border-bottom:3px solid {c};padding:14px 16px;display:flex;justify-content:space-between;align-items:center">
<div><div class="h" style="color:#fff;font-size:20px">{t if t.startswith("Bar") else "Table " + t}</div><div class="small" style="color:#a9a9a9">{guests} guests</div></div>
<div class="h" style="color:{c};font-size:24px">{clock}</div></div><div style="padding:8px 16px 16px;color:#e9e9e9">{lis}{alg}</div></div>"""
    bars = [6, 9, 12, 14, 11, 15, 13, 8]
    pace = "".join(
        f'<div style="display:flex;flex-direction:column;align-items:center;gap:6px;flex:1"><div style="height:{b * 6}px;width:26px;border-radius:6px 6px 0 0;background:{"var(--gold)" if b < 15 else "var(--amber)"}"></div>'
        f'<div class="small" style="color:#8f8f8f">{t}</div></div>'
        for b, t in zip(bars, ["6:30", "6:45", "7:00", "7:15", "7:30", "7:45", "8:00", "8:15"]))
    body = f"""<div style="padding:22px 28px;height:100vh;display:flex;flex-direction:column;gap:18px">
<div class="row" style="justify-content:space-between"><div class="row" style="gap:14px"><div class="mark" style="width:38px;height:38px">C</div>
<div><div class="h" style="color:#fff;font-size:22px">Kitchen Display</div><div class="small" style="color:#9a9a9a">Expo &middot; Friday dinner</div></div></div>
<div class="row"><span class="pill" style="background:#1E3A37;color:#7DE3D8">{icon("users")}4 tables arriving in 30 min</span>
<span class="pill" style="background:#3A2E14;color:#F1CE7A">{icon("clock")}Avg ticket 11:48</span></div></div>
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;flex:1;min-height:0">{cards}</div>
<div style="background:#1C1C1C;border:1px solid #2E2E2E;border-radius:14px;padding:16px 20px">
<div class="row" style="justify-content:space-between;margin-bottom:10px"><div class="h" style="color:#fff;font-size:15px">Pacing: covers per 15 minutes</div>
<span class="small" style="color:#9a9a9a">Cap 15</span></div>
<div style="position:relative;display:flex;align-items:flex-end;gap:10px;height:120px">
<div style="position:absolute;left:0;right:0;bottom:{15 * 6 + 22}px;border-top:2px dashed #E39B2D"></div>{pace}</div></div></div>"""
    return page(body, dark=True), (1440, 900)


# ---------------------------------------------------------------- training academy (LMS)
def lms():
    days = "".join(
        f'<div style="display:flex;flex-direction:column;align-items:center;gap:6px">'
        f'<div style="width:42px;height:42px;border-radius:50%;display:grid;place-items:center;font-weight:700;'
        f'background:{"var(--teal)" if d < 4 else ("var(--gold)" if d == 4 else "#EFECE5")};color:{"#fff" if d <= 4 else "#9a958a"}">'
        f'{icon("check") if d < 4 else (str(d) if d == 4 else icon("lock"))}</div><div class="small muted">Day {d}</div></div>'
        for d in range(1, 11))
    lessons = [("Menu: starters and raw bar", "12 dishes &middot; allergens included", "done"),
               ("Wine service basics", "Video and practice script", "done"),
               ("Allergen protocol", "Ring the chef, mark the ticket, confirm at drop", "now"),
               ("Daily quiz", "10 questions &middot; pass at 80%", "next")]
    ls = "".join(f"""<div class="row" style="justify-content:space-between;padding:14px 0;border-bottom:1px solid var(--line)">
<div class="row" style="gap:14px"><div style="width:36px;height:36px;border-radius:10px;display:grid;place-items:center;
background:{"var(--teal-soft)" if s == "done" else ("var(--gold-soft)" if s == "now" else "#F2EFE8")};color:{"var(--teal-d)" if s == "done" else ("var(--gold-d)" if s == "now" else "#9a958a")}">
{icon("check-circle" if s == "done" else ("play" if s == "now" else "file-text"))}</div>
<div><div style="font-weight:600;font-size:14.5px">{t}</div><div class="small muted">{d}</div></div></div>
<span class="pill {"p-teal" if s == "done" else ("p-gold" if s == "now" else "p-line")}">{"Complete" if s == "done" else ("In progress" if s == "now" else "Up next")}</span></div>""" for t, d, s in lessons)
    roles = ["Server", "Host", "Bartender", "Back waiter", "Line cook", "Prep cook", "Dishwasher", "Shift lead"]
    rl = "".join(f'<div class="nav{" on" if r == "Server" else ""}" style="padding:9px 12px">{icon("bookmark")}<span>{r}</span></div>' for r in roles)
    body = f"""<div class="app"><aside class="side"><div class="brand"><div class="mark">C</div>Academy</div>
<div class="small" style="color:#8b8b8b;margin:0 12px 8px;letter-spacing:.5px">ROLE ACADEMIES</div>{rl}
<div class="foot">English &middot; <span style="color:var(--gold)">Espa&ntilde;ol</span></div></aside><div class="main">
<div class="top"><div><h1>Server Academy &middot; Day 4 of 10</h1><div class="sub">Trainee: Noah G. &middot; Trainer: Ava L.</div></div>
<div class="row"><span class="pill p-teal">{icon("check-circle")}Handbook v3 signed</span><span class="pill p-line">{icon("globe")}EN / ES</span></div></div>
<div style="padding:24px 28px;display:grid;grid-template-columns:1fr 360px;gap:22px;flex:1;min-height:0">
<div style="display:flex;flex-direction:column;gap:20px;min-width:0">
<div class="card" style="padding:22px 26px"><div class="h" style="font-size:15px;margin-bottom:16px">Progress</div>
<div style="display:flex;justify-content:space-between">{days}</div></div>
<div class="card" style="padding:18px 26px"><div class="h" style="font-size:15px;margin-bottom:4px">Today's lessons</div>{ls}</div></div>
<div style="display:flex;flex-direction:column;gap:20px">
<div class="card" style="padding:22px;text-align:center"><div class="small muted">Day 3 quiz</div>
<div class="h" style="font-size:46px;color:var(--teal-d);margin:6px 0">92%</div><div class="small muted">Passed &middot; 2 attempts</div></div>
<div class="card" style="padding:22px"><div class="h" style="font-size:15px;margin-bottom:12px">Trainer sign-off</div>
<div class="row" style="justify-content:space-between;padding:8px 0"><span>Day 3 floor practice</span><span class="pill p-teal">Signed</span></div>
<div class="row" style="justify-content:space-between;padding:8px 0"><span>Day 4 table walk</span><span class="pill p-amber">Waiting</span></div>
<div class="btn gold" style="margin-top:14px;justify-content:center;width:100%">{icon("edit")}Sign off Day 4</div></div>
<div class="card" style="padding:18px 22px"><div class="small muted">Opens next</div><div style="font-weight:600;margin-top:4px">Day 5: Section running and pacing</div></div>
</div></div></div></div>"""
    return page(body), (1440, 760)


# ---------------------------------------------------------------- AI assistant
def ai():
    body = f"""<div class="app">{sidebar("Assistant")}<div class="main">
<div class="top"><div><h1>Assistant</h1><div class="sub">Reads live availability, the book, and last month's reports</div></div>
<span class="pill p-teal">{icon("shield")}A person confirms anything that books, publishes, or sends</span></div>
<div style="padding:26px 28px;display:flex;flex-direction:column;gap:18px;flex:1;min-height:0;max-width:1060px">
<div style="align-self:flex-end;background:var(--ink);color:#fff;padding:14px 18px;border-radius:16px 16px 4px 16px;font-size:15px;max-width:560px">
Can we seat a party of 6 at 7:30 on Friday?</div>
<div class="card" style="padding:20px 22px;max-width:760px;border-radius:16px 16px 16px 4px">
<div class="row" style="gap:10px;margin-bottom:10px"><div class="mark" style="width:28px;height:28px;font-size:13px">{icon("zap")}</div><b>Assistant</b></div>
<div style="font-size:15px;line-height:1.6">Yes. Tables 21 and 22 can combine for 6 at 7:30. Pacing stays at 13 of 15 covers for that window.
Server section 3 has Ava, who has two tables seating at 7:15.</div>
<div style="display:flex;gap:12px;margin-top:14px"><div class="card" style="padding:12px 16px;flex:1;background:#FBFAF6">
<div class="small muted">Proposed hold</div><div style="font-weight:600">Fri 7:30 &middot; 6 guests &middot; Tables 21 + 22</div></div></div>
<div class="row" style="margin-top:14px"><span class="btn gold">{icon("check")}Confirm hold</span><span class="btn ghost">Change time</span>
<span class="small muted" style="margin-left:6px">Nothing is booked until you confirm.</span></div></div>
<div style="align-self:flex-end;background:var(--ink);color:#fff;padding:14px 18px;border-radius:16px 16px 4px 16px;font-size:15px;max-width:560px">
Which nights ran over our labor target last month?</div>
<div class="card" style="padding:20px 22px;max-width:760px;border-radius:16px 16px 16px 4px">
<div class="row" style="gap:10px;margin-bottom:10px"><div class="mark" style="width:28px;height:28px;font-size:13px">{icon("zap")}</div><b>Assistant</b></div>
<div style="font-size:15px;line-height:1.6;margin-bottom:12px">Three Mondays and one rainy Thursday. Each had a full floor schedule against light covers.</div>
<div style="display:grid;grid-template-columns:1.2fr 1fr 1fr 1fr;font-size:14px;border:1px solid var(--line);border-radius:10px;overflow:hidden">
<div style="padding:9px 12px;background:#FBFAF6" class="small muted">Night</div><div style="padding:9px 12px;background:#FBFAF6" class="small muted">Covers</div>
<div style="padding:9px 12px;background:#FBFAF6" class="small muted">Labor %</div><div style="padding:9px 12px;background:#FBFAF6" class="small muted">Target</div>
<div style="padding:9px 12px;border-top:1px solid var(--line)">Mon, Oct 6</div><div style="padding:9px 12px;border-top:1px solid var(--line)">58</div><div style="padding:9px 12px;border-top:1px solid var(--line);color:var(--red);font-weight:600">36%</div><div style="padding:9px 12px;border-top:1px solid var(--line)">28%</div>
<div style="padding:9px 12px;border-top:1px solid var(--line)">Thu, Oct 16</div><div style="padding:9px 12px;border-top:1px solid var(--line)">71</div><div style="padding:9px 12px;border-top:1px solid var(--line);color:var(--red);font-weight:600">33%</div><div style="padding:9px 12px;border-top:1px solid var(--line)">28%</div></div>
<div class="row" style="margin-top:14px"><span class="pill p-gold">{icon("calendar")}Draft a lighter Monday template?</span></div></div>
</div></div></div>"""
    return page(body), (1440, 900)


# ---------------------------------------------------------------- AI assessment report
def report():
    scores = [("Operations", 68, "amber"), ("Team and training", 61, "amber"), ("Guest experience", 80, "teal"),
              ("Marketing", 70, "gold"), ("Reviews and reputation", 84, "teal"), ("Website", 58, "red")]
    col = {"amber": "var(--amber)", "teal": "var(--teal)", "gold": "var(--gold)", "red": "var(--red)"}
    bars = "".join(f"""<div style="padding:11px 0"><div class="row" style="justify-content:space-between;margin-bottom:7px">
<span style="font-weight:600;font-size:14.5px">{n}</span><span class="h" style="font-size:15px">{s}</span></div>
<div style="height:9px;border-radius:9px;background:#EFECE5"><div style="height:9px;border-radius:9px;width:{s}%;background:{col[c]}"></div></div></div>""" for n, s, c in scores)
    findings = [("alert-triangle", "red", "Menu is a PDF", "Hard to read on phones and invisible to search. 64% of your site visits are mobile."),
                ("star", "teal", "Reviews praise the food, flag the wait", "4.6 stars from 512 reviews. 2 of the 5 newest mention slow Friday service."),
                ("users", "amber", "Training lives in shadow shifts", "No written path for new servers. Turnover hits Friday pacing first."),
                ("calendar", "gold", "Reservations link is buried", "Booking sits in the footer. Put it in the header and on Google.")]
    fl = "".join(f"""<div class="row" style="align-items:flex-start;gap:14px;padding:13px 0;border-bottom:1px solid var(--line)">
<div style="width:36px;height:36px;border-radius:10px;display:grid;place-items:center;background:var(--{c}-soft);color:{col[c]}">{icon(i)}</div>
<div><div style="font-weight:600;font-size:14.5px">{t}</div><div class="small muted" style="margin-top:2px;line-height:1.5">{d}</div></div></div>""" for i, c, t, d in findings)
    body = f"""<div style="height:100vh;display:flex;flex-direction:column">
<div class="top"><div class="row" style="gap:14px"><div class="mark" style="width:36px;height:36px">{icon("zap")}</div>
<div><h1>AI Restaurant Assessment</h1><div class="sub">Cedar &amp; Salt &middot; answers, Google listing, and website reviewed</div></div></div>
<span class="pill p-gold">{icon("mail")}Report emailed &middot; Christy follows up</span></div>
<div style="padding:24px 28px;display:grid;grid-template-columns:330px 1fr 1fr;gap:22px;flex:1;min-height:0">
<div class="card" style="padding:26px;display:flex;flex-direction:column;align-items:center;text-align:center">
<div class="small muted" style="letter-spacing:.5px">OVERALL</div>
<div style="width:190px;height:190px;border-radius:50%;margin:16px 0;background:conic-gradient(var(--gold) 0 72%,#EFECE5 72% 100%);display:grid;place-items:center">
<div style="width:150px;height:150px;border-radius:50%;background:#fff;display:grid;place-items:center"><div><div class="h" style="font-size:52px">72</div><div class="small muted">of 100</div></div></div></div>
<div style="font-weight:600">Strong food and reviews.</div><div class="small muted" style="margin-top:4px;line-height:1.5">Biggest gains: training, website, and Friday pacing.</div></div>
<div class="card" style="padding:20px 24px"><div class="h" style="font-size:16px;margin-bottom:6px">Scores</div>{bars}</div>
<div class="card" style="padding:20px 24px"><div class="h" style="font-size:16px;margin-bottom:2px">Top findings</div>{fl}
<div class="h" style="font-size:14px;margin:16px 0 8px">Quick wins in 30 days</div>
<div class="small" style="line-height:1.7">Move the menu to a real web page &middot; Add booking to the header &middot; Reply to recent reviews</div></div>
</div></div>"""
    return page(body), (1440, 720)


# ---------------------------------------------------------------- server tablet guest brief
def brief():
    body = f"""<div style="height:100vh;display:flex;flex-direction:column;background:var(--cream)">
<div class="top"><div><h1>Table 14 &middot; Party of 4</h1><div class="sub">Seated 7:02 PM &middot; Section 3 &middot; Ava</div></div>
<span class="pill p-gold">{icon("heart")}Anniversary tonight</span></div>
<div style="padding:22px 26px;display:grid;grid-template-columns:1fr 1fr;gap:18px;flex:1;min-height:0">
<div style="display:flex;flex-direction:column;gap:18px">
<div class="card" style="padding:20px 22px;border:2px solid var(--red);background:#FFF8F7"><div class="row" style="gap:10px;color:var(--red)">{icon("alert-triangle")}<span class="h" style="font-size:16px">Allergies first</span></div>
<div style="margin-top:12px;font-size:15.5px;line-height:1.7"><b>Sarah W.</b> &middot; tree nuts (severe)<br><b>Tom W.</b> &middot; no shellfish</div>
<div class="small muted" style="margin-top:8px">Kitchen already flagged on the ticket.</div></div>
<div class="card" style="padding:20px 22px"><div class="h" style="font-size:16px;margin-bottom:10px">Preferences</div>
<div class="row" style="flex-wrap:wrap;gap:8px"><span class="pill p-line">Sparkling water</span><span class="pill p-line">Cabernet</span>
<span class="pill p-line">Booth if possible</span><span class="pill p-line">Medium rare</span></div></div></div>
<div style="display:flex;flex-direction:column;gap:18px">
<div class="card" style="padding:20px 22px"><div class="row" style="gap:10px;margin-bottom:10px"><div class="mark" style="width:28px;height:28px;font-size:13px">{icon("zap")}</div><span class="h" style="font-size:16px">Suggested greeting</span></div>
<div style="font-size:15.5px;line-height:1.7;font-style:italic">"Happy anniversary, Sarah and Tom. Welcome back. The halibut you loved in October is on again tonight."</div></div>
<div class="card" style="padding:20px 22px"><div class="h" style="font-size:16px;margin-bottom:10px">Visit history</div>
<div class="row" style="justify-content:space-between;padding:6px 0"><span>Visits</span><b>6th</b></div>
<div class="row" style="justify-content:space-between;padding:6px 0"><span>Last visit</span><b>Oct 18 &middot; halibut, Cabernet</b></div>
<div class="row" style="justify-content:space-between;padding:6px 0"><span>Server notes</span><b>Likes a slower pace</b></div>
<div class="btn ghost" style="margin-top:12px">{icon("edit")}Add a note to their file</div></div></div></div></div>"""
    return page(body), (1180, 820)


# ---------------------------------------------------------------- guest booking (phone)
def booking():
    times = [("5:30", "open"), ("6:00", "open"), ("6:30", "full"), ("7:00", "full"), ("7:15", "open"), ("7:30", "open"),
             ("8:00", "full"), ("8:30", "open"), ("9:00", "open")]
    slots = "".join(
        f'<div style="padding:12px 0;border-radius:10px;text-align:center;font-weight:600;font-size:14.5px;'
        f'{"background:var(--ink);color:#fff" if t == "7:15" else ("background:#fff;border:1px solid var(--line)" if s == "open" else "background:#F1EEE7;color:#B8B1A3;text-decoration:line-through")}">{t}</div>'
        for t, s in times)
    days = "".join(
        f'<div style="flex:1;padding:10px 0;border-radius:12px;text-align:center;{"background:var(--gold);color:var(--ink)" if d == "14" else "background:#fff;border:1px solid var(--line)"}">'
        f'<div class="small" style="opacity:.75">{w}</div><div class="h" style="font-size:17px">{d}</div></div>'
        for w, d in [("Thu", "13"), ("Fri", "14"), ("Sat", "15"), ("Sun", "16")])
    body = f"""<div style="height:100vh;display:flex;flex-direction:column;background:var(--cream)">
<div style="background:var(--ink);color:#fff;padding:48px 22px 22px"><div class="row" style="gap:12px"><div class="mark">C</div>
<div><div class="h" style="font-size:19px">Cedar &amp; Salt</div><div class="small" style="color:#b5b5b5">Book a table</div></div></div></div>
<div style="padding:20px 20px;display:flex;flex-direction:column;gap:18px">
<div><div class="small muted" style="margin-bottom:8px">Date</div><div class="row" style="gap:8px">{days}</div></div>
<div><div class="small muted" style="margin-bottom:8px">Party size</div><div class="row" style="justify-content:space-between;background:#fff;border:1px solid var(--line);border-radius:12px;padding:12px 16px">
<span style="font-weight:600">2 guests</span>{icon("users")}</div></div>
<div><div class="small muted" style="margin-bottom:8px">Time</div><div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px">{slots}</div></div>
<div class="card" style="padding:14px 16px;background:var(--teal-soft);border-color:#BFE9E4"><div style="font-weight:600;color:var(--teal-d);font-size:14px">7:00 is full</div>
<div class="small" style="color:#2F6F69;margin-top:2px">Join the waitlist and we'll text you if a table opens.</div></div>
<div class="btn gold" style="justify-content:center;padding:15px">Confirm Friday at 7:15</div>
<div class="small muted" style="text-align:center">Reminder sent 8 hours before, never overnight.</div></div></div>"""
    return page(body), (390, 844)


# ---------------------------------------------------------------- marketing dashboard
def marketing():
    pts = [32, 36, 35, 41, 44, 43, 49, 53, 51, 58, 62, 66]
    w, h = 560, 170
    step = w / (len(pts) - 1)
    path = " ".join(f"{'M' if i == 0 else 'L'}{i * step:.1f},{h - p * 2.2:.1f}" for i, p in enumerate(pts))
    reviews = [("5", "Best short rib in town and the staff remembered our anniversary.", "AI draft ready", "gold"),
               ("4", "Great food, the wait on Friday was long even with a reservation.", "Needs your approval", "amber"),
               ("5", "Loved the patio. Will be back for brunch.", "Replied", "teal")]
    rv = "".join(f"""<div style="padding:12px 0;border-bottom:1px solid var(--line)"><div class="row" style="justify-content:space-between">
<span class="row" style="gap:4px;color:var(--gold)">{icon("star") * int(s)}</span><span class="pill p-{c}">{st}</span></div>
<div class="small" style="margin-top:6px;line-height:1.5">"{t}"</div></div>""" for s, t, st, c in reviews)
    body = f"""<div class="app">{sidebar("Reports")}<div class="main">
<div class="top"><div><h1>Marketing</h1><div class="sub">Last 30 days &middot; tied to covers and check average</div></div>
<span class="btn gold">{icon("edit")}New campaign</span></div>
<div style="padding:22px 28px;display:flex;flex-direction:column;gap:20px;flex:1;min-height:0">
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:18px">
<div class="card" style="padding:18px 20px"><div class="small muted">Google rating</div><div class="h" style="font-size:30px;margin-top:4px">4.6</div><div class="small" style="color:var(--teal-d)">512 reviews &middot; +23 this month</div></div>
<div class="card" style="padding:18px 20px"><div class="small muted">Search views</div><div class="h" style="font-size:30px;margin-top:4px">18.4k</div><div class="small" style="color:var(--teal-d)">Up 22%</div></div>
<div class="card" style="padding:18px 20px"><div class="small muted">Online bookings</div><div class="h" style="font-size:30px;margin-top:4px">614</div><div class="small" style="color:var(--teal-d)">Up 11%</div></div>
<div class="card" style="padding:18px 20px"><div class="small muted">Email open rate</div><div class="h" style="font-size:30px;margin-top:4px">41%</div><div class="small muted">Fall menu launch</div></div></div>
<div style="display:grid;grid-template-columns:1.25fr 1fr;gap:20px;flex:1;min-height:0">
<div class="card" style="padding:20px 24px"><div class="row" style="justify-content:space-between"><div class="h" style="font-size:16px">Search visibility</div><span class="pill p-teal">{icon("search")}Restaurants near me</span></div>
<svg viewBox="0 0 {w} {h}" style="width:100%;height:220px;margin-top:16px"><path d="{path}" fill="none" stroke="#D4A843" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
<path d="{path} L{w},{h} L0,{h} Z" fill="rgba(212,168,67,.12)"/></svg>
<div class="row" style="gap:10px;margin-top:10px"><span class="pill p-line">{icon("calendar")}3 posts scheduled</span><span class="pill p-line">{icon("mail")}Holiday parties email in draft</span></div></div>
<div class="card" style="padding:20px 24px"><div class="h" style="font-size:16px">New reviews</div>{rv}</div></div></div></div></div>"""
    return page(body), (1440, 900)


SCREENS = {"host": host, "schedule": schedule, "kitchen": kitchen, "lms": lms, "ai": ai,
           "report": report, "brief": brief, "booking": booking, "marketing": marketing}


def render(name):
    html, (w, h) = SCREENS[name]()
    # Headless Chrome will not lay out narrower than about 500px, so phone screens are pinned
    # to their real width inside a wider window and cropped back afterwards.
    win_w = w
    if w < 500:
        win_w = 520
        html = html.replace("</head>", f"<style>html,body{{width:{w}px!important;min-width:{w}px}}.illus{{left:14px;right:auto}}</style></head>", 1)
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as fh:
        fh.write(html)
        src = fh.name
    png = os.path.join(tempfile.gettempdir(), f"mock-{name}.png")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files",
                    f"--force-device-scale-factor=2", f"--window-size={win_w},{h}", f"--screenshot={png}",
                    "--virtual-time-budget=1500", f"file://{src}"],
                   check=True, capture_output=True)
    img = Image.open(png).convert("RGB")
    if win_w != w:
        img = img.crop((0, 0, w * 2, img.size[1]))
    target_w = 1800 if w > 1000 else 780
    if img.size[0] > target_w:
        img = img.resize((target_w, int(img.size[1] * target_w / img.size[0])), Image.LANCZOS)
    out = os.path.join(OUT, f"mock-{name}.webp")
    img.save(out, "WEBP", quality=84, method=6)
    os.unlink(src)
    return out, img.size


if __name__ == "__main__":
    for n in (sys.argv[1:] or SCREENS):
        path, size = render(n)
        print(f"{n}: {os.path.relpath(path, ROOT)} {size[0]}x{size[1]}")
