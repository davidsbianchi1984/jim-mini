#!/usr/bin/env python3
"""Generate the Jim Mini *watch* screens — glanceable Apple-Watch faces, one per
capability, in the product's dark-OLED style. Reuses the phone generator's icon
and colour library so both galleries stay identical.
Run: python3 docs/watch/build.py  ->  docs/watch/NN-name.svg"""

from __future__ import annotations

import importlib.util
import os
import random

OUT = os.path.dirname(os.path.abspath(__file__))

# reuse the phone builder's primitives (icons, palette, text/rrect helpers)
_spec = importlib.util.spec_from_file_location(
    "phonebuild", os.path.join(OUT, "..", "screens", "build.py"))
pb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pb)
icon, C, ACCENT, esc, rrect, text = pb.icon, pb.C, pb.ACCENT, pb.esc, pb.rrect, pb.text
A = pb.A

W, H = 236, 300
# case + screen (Apple-Watch rounded square, taller than wide)
CAX, CAY, CAW, CAH = 18, 20, 196, 260
SXX, SYY, SWW, SHH = 30, 32, 172, 236
PADX = 44          # content left inside screen
CW = SWW - 2 * (PADX - SXX)   # content width


def orb(cx, cy, r):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#orb)"/>'
            f'<ellipse cx="{cx-r*0.28}" cy="{cy-r*0.32}" rx="{r*0.28}" ry="{r*0.18}" fill="rgba(255,255,255,0.33)"/>')


def head(num, title, accent="brand"):
    ac = ACCENT.get(accent, C["brandA"])
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" role="img" aria-label="{esc(title)} watch screen">']
    o.append(f'''<defs>
      <linearGradient id="gScr" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{C['scrA']}"/><stop offset="1" stop-color="#05070e"/></linearGradient>
      <linearGradient id="gFrame" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{C['frameA']}"/><stop offset="1" stop-color="{C['frameB']}"/></linearGradient>
      <linearGradient id="gCard" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{C['card']}"/><stop offset="1" stop-color="{C['card2']}"/></linearGradient>
      <linearGradient id="gBrand" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{C['brandA']}"/><stop offset="1" stop-color="{C['brandB']}"/></linearGradient>
      <linearGradient id="gEmer" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ff5b52"/><stop offset="1" stop-color="{C['emer']}"/></linearGradient>
      <linearGradient id="mV" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{C['brandA']}"/><stop offset="1" stop-color="{C['brandB']}"/></linearGradient>
      <linearGradient id="mO" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#f7b731"/><stop offset="1" stop-color="#ff7a45"/></linearGradient>
      <linearGradient id="mG" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#2fd27a"/><stop offset="1" stop-color="#43e08a"/></linearGradient>
      <radialGradient id="orb" cx="34%" cy="30%" r="75%"><stop offset="0" stop-color="#c3b0ff"/><stop offset="42%" stop-color="{C['brandA']}"/><stop offset="80%" stop-color="#2f6cf0"/><stop offset="100%" stop-color="#14204a"/></radialGradient>
    </defs>''')
    # crown + side button on the right
    o.append(rrect(CAX + CAW - 2, 118, 7, 34, 3, "#333c52"))
    o.append(rrect(CAX + CAW - 1, 160, 5, 26, 2, "#2a3145"))
    o.append(rrect(CAX, CAY, CAW, CAH, 60, "url(#gFrame)"))
    o.append(rrect(SXX, SYY, SWW, SHH, 48, "url(#gScr)"))
    o.append(text(SXX + SWW - 14, SYY + 24, "10:09", 11, ac, 700, "end"))
    o.append(text(PADX, SYY + 24, title, 13, C["txt"], 700, spacing=-0.2))
    return o


def dots(active, count):
    o = []
    cx0 = W / 2 - (count - 1) * 5
    for i in range(count):
        c = C["txt"] if i == active else C["t3"]
        o.append(f'<circle cx="{cx0+i*10}" cy="{SYY+SHH-14}" r="{2.6 if i==active else 2}" fill="{c}"/>')
    return o


def close():
    return ["</svg>"]


def tile(x, y, w, h, ic, col, val, lbl):
    c = ACCENT[col]
    return (rrect(x, y, w, h, 13, "url(#gCard)", C["line"], 1)
            + rrect(x + 9, y + 9, 22, 22, 7, A(c, 0.16))
            + icon(ic, x + 20, y + 20, c, 0.62)
            + text(x + 9, y + h - 20, val, 15, C["txt"], 750)
            + text(x + 9, y + h - 7, lbl, 8.5, C["t2"], 500))


def row(x, y, w, ic, col, k, s):
    c = ACCENT[col]
    return (rrect(x, y, w, 40, 12, "url(#gCard)", C["line"], 1)
            + rrect(x + 8, y + 9, 22, 22, 7, A(c, 0.16)) + icon(ic, x + 19, y + 20, c, 0.6)
            + text(x + 38, y + 17, k, 11, C["txt"], 650)
            + text(x + 38, y + 30, s, 9, C["t2"]))


def wbtn(x, y, w, label, kind="brand", h=34):
    fill = "url(#gBrand)" if kind == "brand" else ("url(#gEmer)" if kind == "emer" else "rgba(255,255,255,0.07)")
    st = C["line"] if kind == "ghost" else None
    tcol = C["txt"] if kind == "ghost" else "#fff"
    return (rrect(x, y, w, h, 12, fill, st, 1)
            + text(x + w / 2, y + h / 2 + 4, label, 11.5, tcol, 700, "middle"))


def meter(x, y, w, pct, grad):
    return rrect(x, y, w, 6, 3, "#0d1526", C["line"], 1) + rrect(x, y, max(5, w * pct), 6, 3, f"url(#{grad})")


def wtoggle(x, y, on):
    bg = C["green"] if on else "#2a3450"
    kx = x + 15 if on else x + 2
    return rrect(x, y, 28, 16, 8, bg) + f'<circle cx="{kx+6}" cy="{y+8}" r="6" fill="#fff"/>'


def wring(cx, cy, r, pct, col, sw=8):
    import math
    circ = 2 * math.pi * r
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{A(col,0.13)}" stroke-width="{sw}"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{col}" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-dasharray="{circ*pct:.1f} {circ:.1f}" transform="rotate(-90 {cx} {cy})"/>')


# --------------------------------------------------------------------------- #
def render(s):
    o = head(f"{s['num']:02d}", s["title"], s.get("accent", "brand"))
    cx = W / 2
    y = SYY + 44
    h = s.get("hero")

    if h == "home":
        o.append(orb(cx, y + 30, 26))
        o.append(text(cx, y + 74, "Good morning,", 10.5, C["t2"], 500, "middle"))
        o.append(text(cx, y + 90, "David", 18, "#fff", 750, "middle"))
        o.append(wbtn(PADX, y + 104, CW, "Talk to Jim", "brand", 36))
    elif h == "voice":
        o.append(text(cx, y + 6, "Listening…", 12, C["txt"], 600, "middle"))
        o.append(orb(cx, y + 56, 40))
        for i, rr in enumerate((52, 66)):
            o.append(f'<circle cx="{cx}" cy="{y+56}" r="{rr}" fill="none" stroke="{C["brandA"]}" stroke-width="1" opacity="{0.3-i*0.12:.2f}"/>')
        bars = "".join(f'<rect x="{PADX+12+i*11}" y="{y+128-hh/2}" width="4" height="{hh}" rx="2" fill="url(#gBrand)"/>'
                       for i, hh in enumerate([10, 24, 14, 30, 18, 34, 12, 22, 16, 26, 12]))
        o.append(bars)
    elif h == "wave":
        o.append(orb(cx, y + 40, 30))
        o.append(text(cx, y + 92, "How can I help?", 11, C["t2"], 500, "middle"))
        o.append(wbtn(PADX, y + 104, CW, "Speak", "brand", 34))
    elif h == "health":
        gx, gy, tw, th, g = PADX, y, (CW - 8) / 2, 52, 8
        o.append(tile(gx, gy, tw, th, "heart", "red", "72", "BPM"))
        o.append(tile(gx + tw + g, gy, tw, th, "moon", "violet", "7h45", "SLEEP"))
        o.append(tile(gx, gy + th + g, tw, th, "steps", "green", "8.3k", "STEPS"))
        o.append(tile(gx + tw + g, gy + th + g, tw, th, "leaf", "cyan", "Low", "STRESS"))
    elif h == "hr":
        o.append(text(cx, y + 4, "Heart rate", 11, C["t2"], 500, "middle"))
        o.append(icon("heart", cx, y + 34, C["red"], 1.4))
        o.append(text(cx, y + 74, "72", 40, "#fff", 800, "middle"))
        o.append(text(cx, y + 92, "BPM · resting 60", 9.5, C["t2"], 500, "middle"))
        o.append(pb.spark(PADX, y + 104, CW, 22, [70, 74, 71, 78, 73, 76, 72], C["red"]))
    elif h == "big":
        o.append(icon(s["icon"], cx, y + 28, ACCENT[s["accent"]], 1.5))
        o.append(text(cx, y + 74, s["big"], 34, "#fff", 800, "middle"))
        o.append(text(cx, y + 92, s["biglbl"], 10, C["t2"], 500, "middle"))
        if s.get("meter"):
            o.append(meter(PADX, y + 104, CW, s["meter"][0], s["meter"][1]))
    elif h == "sos":
        o.append(f'<circle cx="{cx}" cy="{y+52}" r="46" fill="url(#gEmer)"/>')
        o.append(f'<circle cx="{cx}" cy="{y+52}" r="58" fill="none" stroke="{C["emer"]}" stroke-width="1.4" opacity=".4"/>')
        o.append(icon("phone", cx, y + 44, "#fff", 1.5))
        o.append(text(cx, y + 74, "Call 911", 12, "#fff", 750, "middle"))
        o.append(text(cx, y + 120, "Hold · shares location", 9.5, C["t2"], 500, "middle"))
    elif h == "cpr":
        o.append(f'<circle cx="{cx}" cy="{y+52}" r="50" fill="none" stroke="{C["red"]}" stroke-width="2" opacity=".55"/>')
        o.append(f'<circle cx="{cx}" cy="{y+52}" r="40" fill="{C["red"]}14"/>')
        o.append(f'<circle cx="{cx+40}" cy="{y+6}" r="6" fill="{C["green"]}"/>')
        o.append(text(cx, y + 30, "PUSH", 9, "#ffb3ba", 700, "middle", 0.5))
        o.append(text(cx, y + 62, "18", 34, "#fff", 800, "middle"))
        o.append(text(cx, y + 78, "110/min · 30:2", 9, C["t2"], 600, "middle"))
        o.append(wbtn(PADX, y + 108, CW, "Start CPR", "emer", 32))
    elif h == "qr":
        random.seed(7)
        qs = 108
        qx, qy = cx - qs / 2, y
        o.append(rrect(qx, qy, qs, qs, 12, "#fff"))
        cell = (qs - 16) / 21
        def finder(r, c):
            res = []
            for i in range(7):
                for j in range(7):
                    if i in (0, 6) or j in (0, 6) or (2 <= i <= 4 and 2 <= j <= 4):
                        res.append(rrect(qx + 8 + (c + j) * cell, qy + 8 + (r + i) * cell, cell, cell, 0, "#0a0f1c"))
            return "".join(res)
        g = []
        for r in range(21):
            for c in range(21):
                if (r < 8 and c < 8) or (r < 8 and c > 12) or (r > 12 and c < 8):
                    continue
                if random.random() > 0.5:
                    g.append(rrect(qx + 8 + c * cell, qy + 8 + r * cell, cell, cell, 0, "#0a0f1c"))
        o.append("".join(g) + finder(0, 0) + finder(0, 14) + finder(14, 0))
        o.append(text(cx, qy + qs + 22, "Medical ID", 12, C["txt"], 650, "middle"))
        o.append(text(cx, qy + qs + 37, "scan to view", 9.5, C["t2"], 500, "middle"))
    elif h == "sensitivity":
        seg = ["Cautious", "Balanced", "Assertive"]
        o.append(text(cx, y + 4, "Sensitivity", 11, C["t2"], 500, "middle"))
        for i, lbl in enumerate(seg):
            on = (i == 1)
            ry = y + 16 + i * 34
            o.append(rrect(PADX, ry, CW, 28, 10, "url(#gBrand)" if on else "#0c1424", None if on else C["line"], 1))
            o.append(text(cx, ry + 18, lbl, 11.5, "#fff" if on else C["t2"], 650, "middle"))
        o.append(text(cx, y + 128, "+40 bpm over baseline", 9.5, C["t2"], 500, "middle"))
    elif h == "alert":
        o.append(f'<circle cx="{cx}" cy="{y+40}" r="34" fill="{ACCENT[s["accent"]]}1e"/>')
        o.append(icon(s["icon"], cx, y + 40, ACCENT[s["accent"]], 1.5))
        o.append(text(cx, y + 92, s["k"], 12.5, C["txt"], 700, "middle"))
        o.append(text(cx, y + 108, s["s"], 9.5, C["t2"], 500, "middle"))
        if s.get("btn"):
            o.append(wbtn(PADX, y + 122, CW, s["btn"][0], s["btn"][1], 32))
    elif h == "prompt":
        o.append(orb(PADX + 14, y + 8, 13))
        o.append(text(PADX + 34, y + 12, "Jim Mini", 11, C["txt"], 700))
        o.append(rrect(PADX, y + 24, CW, 58, 13, "url(#gCard)", C["line"], 1))
        for i, ln in enumerate(s["lines"]):
            o.append(text(PADX + 12, y + 42 + i * 14, ln, 10, C["txt"], 500))
        o.append(rrect(PADX, y + 92, CW / 2 - 4, 32, 11, "url(#gBrand)"))
        o.append(text(PADX + CW / 4, y + 112, "Yes", 11, "#fff", 700, "middle"))
        o.append(rrect(PADX + CW / 2 + 4, y + 92, CW / 2 - 4, 32, 11, "rgba(255,255,255,0.07)", C["line"], 1))
        o.append(text(PADX + CW * 3 / 4, y + 112, "Later", 11, C["txt"], 700, "middle"))
    elif h == "rings":  # activity/goals rings
        for i, (r, col, pct) in enumerate([(40, C["green"], .75), (30, C["brandA"], .6), (20, C["amber"], .55)]):
            circ = 2 * 3.14159 * r
            o.append(f'<circle cx="{cx}" cy="{y+48}" r="{r}" fill="none" stroke="{A(col,0.13)}" stroke-width="9"/>')
            o.append(f'<circle cx="{cx}" cy="{y+48}" r="{r}" fill="none" stroke="{col}" stroke-width="9" '
                     f'stroke-linecap="round" stroke-dasharray="{circ*pct:.1f} {circ:.1f}" transform="rotate(-90 {cx} {y+48})"/>')
        o.append(text(cx, y + 112, "Goals on track", 10.5, C["t2"], 500, "middle"))

    elif h == "breathe":
        o.append(orb(cx, y + 52, 30))
        o.append(f'<circle cx="{cx}" cy="{y+52}" r="44" fill="none" stroke="{C["brandA"]}" stroke-width="1.5" opacity=".4"/>')
        o.append(text(cx, y + 104, "Breathe in", 12, "#c9baff", 600, "middle"))
        o.append(wbtn(PADX, y + 116, CW, "Begin", "brand", 32))
    elif h == "feedback":
        o.append(text(cx, y + 6, "Was that helpful?", 11, C["t2"], 500, "middle"))
        bw = (CW - 8) / 2
        o.append(rrect(PADX, y + 20, bw, 56, 14, A(C["green"], 0.12), C["green"], 1.4))
        o.append(icon("heart", PADX + bw / 2, y + 42, C["green"], 1.1))
        o.append(text(PADX + bw / 2, y + 66, "Yes", 10, C["green"], 700, "middle"))
        o.append(rrect(PADX + bw + 8, y + 20, bw, 56, 14, A(C["red"], 0.12), C["red"], 1.4))
        o.append(icon("warn", PADX + bw + 8 + bw / 2, y + 42, C["red"], 1.1))
        o.append(text(PADX + bw + 8 + bw / 2, y + 66, "No", 10, C["red"], 700, "middle"))
        o.append(text(cx, y + 100, "one tap trains it", 9, C["t2"], 500, "middle"))
    elif h == "journal":
        bars = "".join(f'<rect x="{PADX+8+i*10}" y="{y+56-hh/2}" width="4" height="{hh}" rx="2" fill="{C["violet"]}"/>'
                       for i, hh in enumerate([8, 22, 14, 30, 18, 34, 12, 24, 16, 26, 10, 20, 14]))
        o.append(bars)
        o.append(f'<circle cx="{PADX+14}" cy="{y+88}" r="4" fill="{C["red"]}"/>')
        o.append(text(PADX + 26, y + 92, "0:14  recording", 10, C["t2"], 500))
        o.append(wbtn(PADX, y + 104, CW, "■ Stop", "emer", 32))
    elif h == "coach":
        areas = ["Mind", "Fitness", "Career", "Money", "Bonds", "Growth"]
        xx, yy = PADX, y + 4
        for i, a in enumerate(areas):
            wch = 44
            if xx + wch > SXX + SWW - (PADX - SXX):
                xx = PADX; yy += 26
            on = (i == 0)
            o.append(rrect(xx, yy, wch, 22, 8, "url(#gBrand)" if on else "rgba(255,255,255,0.06)", None if on else C["line"], 1))
            o.append(text(xx + wch / 2, yy + 15, a, 9, "#fff" if on else C["t2"], 600, "middle"))
            xx += wch + 5
        o.append(text(cx, yy + 46, "“What's weighing", 10, C["txt"], 500, "middle"))
        o.append(text(cx, yy + 60, "on you today?”", 10, C["txt"], 500, "middle"))
    elif h == "baseline":
        o.append(wring(cx, y + 52, 40, 0.82, C["green"], 8))
        o.append(text(cx, y + 56, "60", 26, "#fff", 800, "middle"))
        o.append(text(cx, y + 72, "RESTING", 8, C["t2"], 600, "middle", 0.5))
        o.append(text(cx, y + 116, "learning · 40 samples", 9.5, C["t2"], 500, "middle"))
    elif h == "sources":
        items = [("Wearable", True), ("Spending", True), ("Calendar", False)]
        yy = y + 2
        for k, on in items:
            o.append(rrect(PADX, yy, CW, 34, 11, "url(#gCard)", C["line"], 1))
            o.append(text(PADX + 12, yy + 21, k, 11, C["txt"], 600))
            o.append(wtoggle(PADX + CW - 40, yy + 9, on))
            yy += 40
    elif h == "privacy":
        o.append(f'<circle cx="{PADX+6}" cy="{y+6}" r="4" fill="{C["green"]}"/>')
        o.append(text(PADX + 16, y + 10, "chain verified", 9.5, "#7ff0b0", 700))
        rows_ = [("STORED", C["green"], "biometric"), ("READ", C["cyan"], "forecast"), ("ERASED", C["red"], "activity")]
        yy = y + 24
        for v, col, k in rows_:
            o.append(rrect(PADX, yy, 46, 15, 5, A(col, 0.15)))
            o.append(text(PADX + 23, yy + 11, v, 7.5, col, 800, "middle", 0.3))
            o.append(text(PADX + 54, yy + 11, k, 9.5, C["txt"], 500))
            yy += 22
    elif h == "handoff":
        o.append(icon("cross", cx, y + 30, C["red"], 1.4))
        o.append(text(cx, y + 62, "Dr. Rivera, LCSW", 11, C["txt"], 650, "middle"))
        o.append(text(cx, y + 77, "sealed summary", 9, C["t2"], 500, "middle"))
        o.append(wbtn(PADX, y + 96, CW, "Hold to share", "brand", 34))
        o.append(text(cx, y + 140, "revocable anytime", 8.5, C["t2"], 500, "middle"))
    elif h == "offline":
        o.append(f'<circle cx="{cx}" cy="{y+44}" r="34" fill="{C["green"]}1e"/>')
        o.append(icon("shield", cx, y + 44, C["green"], 1.6))
        o.append(text(cx, y + 92, "Nothing leaves", 11.5, C["txt"], 650, "middle"))
        o.append(text(cx, y + 107, "this device", 11.5, C["txt"], 650, "middle"))
        o.append(f'<g transform="translate({cx-14},{y+120})">' + wtoggle(0, 0, True) + '</g>')

    else:  # compact rows
        yy = y
        for r in s.get("rows", []):
            o.append(row(PADX, yy, CW, r[0], r[1], r[2], r[3]))
            yy += 46
        if s.get("btn"):
            o.append(wbtn(PADX, yy, CW, s["btn"][0], s["btn"][1], 32))

    o += dots(s.get("dot", 0), s.get("dots", 4))
    o += close()
    return "".join(o)


SCREENS = [
    dict(num=1, title="Home", hero="home"),
    dict(num=2, title="Talk", hero="wave", accent="brand"),
    dict(num=3, title="Voice", hero="voice", accent="brand"),
    dict(num=4, title="Health", hero="health", accent="red"),
    dict(num=5, title="Heart", hero="hr", accent="red"),
    dict(num=6, title="Rings", hero="rings", accent="green"),
    dict(num=7, title="Briefing", accent="cyan", rows=[
        ("leaf", "cyan", "72° Sunny", "San Francisco"),
        ("bell", "violet", "Meeting 10:30", "Gym 6:00"),
        ("bolt", "amber", "Take breaks", "stay hydrated"),
    ]),
    dict(num=8, title="Streak", hero="big", accent="amber", icon="flame", big="12", biglbl="DAY MEDITATION STREAK"),
    dict(num=9, title="Check-in", accent="pink", rows=[
        ("leaf", "green", "Mood", "how are you? 1–5"),
        ("bolt", "amber", "Energy", "steady today"),
    ], btn=("Log check-in", "brand")),
    dict(num=10, title="Insight", hero="alert", accent="amber", icon="moon",
         k="You slept better", s="7.5h · keep it up"),
    dict(num=11, title="Monitoring", hero="alert", accent="red", icon="heart",
         k="Heart rate high", s="+38 over baseline", btn=("I'm okay", "ghost")),
    dict(num=12, title="Foresight", hero="alert", accent="cyan", icon="lung",
         k="Oxygen slipping", s="97 → 95 → 93%", btn=("Breathe with me", "brand")),
    dict(num=13, title="Emergency", hero="sos", accent="red"),
    dict(num=14, title="CPR", hero="cpr", accent="red"),
    dict(num=15, title="Medical ID", hero="qr", accent="red"),
    dict(num=16, title="Sensitivity", hero="sensitivity"),
    dict(num=17, title="Ambient", hero="prompt", accent="brand",
         lines=["You've retried a few", "times. Want a hand?"]),
    dict(num=18, title="Companion", hero="alert", accent="violet", icon="chat",
         k="How did it go?", s="checking in", btn=("Reply", "brand")),
    dict(num=19, title="Notifications", accent="red", rows=[
        ("heart", "red", "High heart rate", "10 min · 9m ago"),
        ("bell", "violet", "Team meeting", "in 21 min"),
        ("bolt", "brand", "Take a break", "15m ago"),
    ]),
    dict(num=20, title="Devices", rows=[
        ("watch", "cyan", "Apple Watch", "active"),
        ("mic", "violet", "Kitchen console", "on-device"),
        ("link", "teal", "Continue here", "same thread"),
    ]),
    dict(num=21, title="Guardian", hero="big", accent="green", icon="shield",
         big="ON", biglbl="WATCHING · TRANSPARENT RULES"),
    dict(num=22, title="Settings", rows=[
        ("shield", "brand", "Permissions", "sources"),
        ("eye", "cyan", "Privacy & data", "access log"),
        ("bell", "amber", "Notifications", "prioritized"),
    ]),
    # --- newly filled gaps (match the phone gallery) ---
    dict(num=23, title="Breathe", hero="breathe", accent="brand"),
    dict(num=24, title="Feedback", hero="feedback", accent="green"),
    dict(num=25, title="Journal", hero="journal", accent="violet"),
    dict(num=26, title="Coach", hero="coach", accent="brand"),
    dict(num=27, title="Baseline", hero="baseline", accent="green"),
    dict(num=28, title="Sources", hero="sources", accent="cyan"),
    dict(num=29, title="Privacy", hero="privacy", accent="green"),
    dict(num=30, title="Handoff", hero="handoff", accent="red"),
    dict(num=31, title="Offline", hero="offline", accent="green"),
    dict(num=32, title="Conditions", accent="violet", rows=[
        ("brain", "violet", "Anxiety / panic", "detection sensitized"),
        ("heart", "red", "Hypertension", "BP watched"),
        ("plus", "green", "Declare", "adapts to you"),
    ]),
    dict(num=33, title="Style", accent="violet", rows=[
        ("chat", "violet", "Tone: Direct", "short, no sugar-coating"),
        ("person", "brand", "Shapes every reply", "guidance & coach"),
    ]),
    dict(num=34, title="History", accent="cyan", rows=[
        ("bolt", "cyan", "Biometric · 10:02", "HR 110 · resp 22"),
        ("warn", "amber", "Detection", "anxiety · guidance"),
        ("shield", "green", "Guidance", "breathing + reassurance"),
    ]),
]


def main():
    n = 0
    for s in SCREENS:
        slug = s["title"].lower().replace(" & ", "-").replace(" ", "-")
        with open(os.path.join(OUT, f'{s["num"]:02d}-{slug}.svg'), "w") as f:
            f.write(render(s))
        n += 1
    print(f"generated {n} watch screens")


if __name__ == "__main__":
    main()
