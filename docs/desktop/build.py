#!/usr/bin/env python3
"""Generate the Jim Mini **desktop** app SVGs — wide, multi-panel dashboard views
of the Guardian personal-guidance system, in the product's dark-OLED style with
its guardian-green identity accent. A sidebar-nav desktop window per view,
complementing the mobile app in docs/screens/ and the watch in docs/watch/.

Reuses the mobile generator's icon + colour library so the galleries stay one
system. Run: python3 docs/desktop/build.py  ->  docs/desktop/NN-name.svg
"""

from __future__ import annotations

import importlib.util
import os

OUT = os.path.dirname(os.path.abspath(__file__))

PLATFORM_D = "macos"          # "macos" | "windows"

_spec = importlib.util.spec_from_file_location(
    "jimmobile", os.path.join(OUT, "..", "screens", "build.py"))
pb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pb)
icon, C, ACCENT, A = pb.icon, pb.C, pb.ACCENT, pb.A
rrect, text, pill, chip, button, ring, spark, esc = (
    pb.rrect, pb.text, pb.pill, pb.chip, pb.button, pb.ring, pb.spark, pb.esc)

ACC = C["green"]          # guardian-green identity accent

W, H = 1280, 820
WIN_X, WIN_Y, WIN_W, WIN_H = 24, 24, 1232, 772
TOPBAR_H = 54
SIDE_W = 216
CONTENT_X = WIN_X + SIDE_W
CONTENT_Y = WIN_Y + TOPBAR_H
CONTENT_W = WIN_W - SIDE_W
CONTENT_H = WIN_H - TOPBAR_H
PAD = 28
IX = CONTENT_X + PAD
IY = CONTENT_Y + PAD
IW = CONTENT_W - 2 * PAD

NAV = [("target", "Overview"), ("heart", "Monitoring"), ("chart", "Health"),
       ("cross", "Emergency"), ("brain", "Coach"), ("watch", "Devices"),
       ("shield", "Privacy")]


def status_dot(x, y, label, tone):
    col = {"on": C["green"], "off": C["t3"], "avail": C["amber"], "crit": C["red"]}[tone]
    w = 14 + len(label) * 6.0
    return (rrect(x - w, y - 9, w, 16, 8, A(col, 0.14))
            + f'<circle cx="{x-w+9}" cy="{y-1}" r="3" fill="{col}"/>'
            + text(x - w + 16, y + 3, label, 9, col, 700, "start", 0.5))


def defs():
    return f'''<defs>
      <linearGradient id="gPage" x1="0" y1="0" x2="0.4" y2="1">
        <stop offset="0" stop-color="#0a1120"/><stop offset="1" stop-color="#070b16"/></linearGradient>
      <linearGradient id="gScr" x1="0" y1="0" x2="0.5" y2="1">
        <stop offset="0" stop-color="{C['scrA']}"/><stop offset="1" stop-color="{C['scrB']}"/></linearGradient>
      <linearGradient id="gSide" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#141d31"/><stop offset="1" stop-color="#0b1120"/></linearGradient>
      <linearGradient id="gCard" x1="0" y1="0" x2="0.4" y2="1">
        <stop offset="0" stop-color="{C['card']}"/><stop offset="1" stop-color="{C['card2']}"/></linearGradient>
      <linearGradient id="gBrand" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0" stop-color="{C['brandA']}"/><stop offset="1" stop-color="{C['brandB']}"/></linearGradient>
      <linearGradient id="gEmer" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ff5b52"/><stop offset="1" stop-color="{C['emer']}"/></linearGradient>
      <linearGradient id="mV" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{C['brandA']}"/><stop offset="1" stop-color="{C['brandB']}"/></linearGradient>
      <linearGradient id="mG" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#2fd27a"/><stop offset="1" stop-color="{C['green']}"/></linearGradient>
      <linearGradient id="mO" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{C['amber']}"/><stop offset="1" stop-color="#ff7a45"/></linearGradient>
      <radialGradient id="orb" cx="34%" cy="30%" r="75%">
        <stop offset="0" stop-color="#c3b0ff"/><stop offset="42%" stop-color="{C['brandA']}"/>
        <stop offset="80%" stop-color="#2f6cf0"/><stop offset="100%" stop-color="#14204a"/></radialGradient>
    </defs>'''


def frame(title, active):
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" role="img" aria-label="Jim Mini — {esc(title)}">']
    o.append(defs())
    o.append(rrect(0, 0, W, H, 0, "url(#gPage)"))
    o.append(f'<rect x="{WIN_X}" y="{WIN_Y}" width="{WIN_W}" height="{WIN_H}" rx="{10 if PLATFORM_D == "windows" else 18}" '
             f'fill="url(#gScr)" stroke="{C["line"]}" stroke-width="1"/>')
    o.append(rrect(WIN_X, WIN_Y, SIDE_W, WIN_H, 18, "url(#gSide)"))
    o.append(rrect(WIN_X + SIDE_W - 18, WIN_Y, 18, WIN_H, 0, "url(#gScr)"))
    o.append(f'<line x1="{CONTENT_X}" y1="{WIN_Y}" x2="{CONTENT_X}" y2="{WIN_Y+WIN_H}" stroke="{C["line"]}" stroke-width="1"/>')
    o.append(f'<line x1="{CONTENT_X}" y1="{CONTENT_Y}" x2="{WIN_X+WIN_W}" y2="{CONTENT_Y}" stroke="{C["line"]}" stroke-width="1"/>')
    if PLATFORM_D == "windows":
        _bx = WIN_X + WIN_W - 22
        o.append(f'<line x1="{_bx-70}" y1="{WIN_Y+28}" x2="{_bx-59}" y2="{WIN_Y+28}" stroke="{C["t2"]}" stroke-width="1.3"/>')
        o.append(rrect(_bx - 41, WIN_Y + 22, 11, 11, 1.5, "none", C["t2"], 1.3))
        o.append(f'<path d="M{_bx-11} {WIN_Y+22} l11 11 M{_bx} {WIN_Y+22} l-11 11" stroke="{C["t2"]}" stroke-width="1.3" stroke-linecap="round"/>')
    else:
        for i, col in enumerate(("#ff5f57", "#febc2e", "#28c840")):
            o.append(f'<circle cx="{WIN_X+22+i*18}" cy="{WIN_Y+27}" r="5.5" fill="{col}" opacity="0.9"/>')
    o.append(f'<circle cx="{WIN_X+96}" cy="{WIN_Y+27}" r="11" fill="url(#orb)"/>')
    o.append(icon("shield", WIN_X + 96, WIN_Y + 27, "rgba(255,255,255,0.95)", 0.5))
    o.append(text(WIN_X + 114, WIN_Y + 25, "JIM", 14, C["txt"], 800, spacing=0.5))
    o.append(text(WIN_X + 114, WIN_Y + 39, "Guardian guidance", 8.5, C["t3"], 500))
    o.append(text(CONTENT_X + PAD, WIN_Y + 33, title, 15, C["txt"], 700, spacing=-0.2))
    rx = WIN_X + WIN_W - 24 - (86 if PLATFORM_D == 'windows' else 0)
    o.append(icon("gear", rx - 10, WIN_Y + 27, C["t2"], 0.8))
    o.append(status_dot(rx - 34, WIN_Y + 31, "Guardian on", "on"))
    o.append(f'<circle cx="{rx-34-92}" cy="{WIN_Y+27}" r="13" fill="url(#orb)"/>')
    o.append(icon("person", rx - 34 - 92, WIN_Y + 27, "rgba(255,255,255,0.9)", 0.6))
    ny = CONTENT_Y + 18
    for ic, lbl in NAV:
        on = (lbl == active)
        if on:
            o.append(rrect(WIN_X + 12, ny - 4, SIDE_W - 24, 38, 10, A(ACC, 0.16)))
            o.append(rrect(WIN_X + 12, ny - 4, 3, 38, 2, ACC))
        col = ACC if on else C["t2"]
        o.append(icon(ic, WIN_X + 34, ny + 15, col, 0.72))
        o.append(text(WIN_X + 54, ny + 20, lbl, 12.5, C["txt"] if on else C["t2"], 650 if on else 500))
        ny += 46
    o.append(f'<line x1="{WIN_X+16}" y1="{WIN_Y+WIN_H-70}" x2="{WIN_X+SIDE_W-16}" y2="{WIN_Y+WIN_H-70}" stroke="{C["line"]}" stroke-width="1"/>')
    o.append(rrect(WIN_X + 16, WIN_Y + WIN_H - 56, SIDE_W - 32, 40, 10, "rgba(255,255,255,0.04)", C["line"], 1))
    o.append(icon("shield", WIN_X + 34, WIN_Y + WIN_H - 36, ACC, 0.66))
    o.append(text(WIN_X + 52, WIN_Y + WIN_H - 40, "Watching", 10.5, C["txt"], 650))
    o.append(text(WIN_X + 52, WIN_Y + WIN_H - 27, "rules are transparent", 8.5, C["t3"], 500))
    return o


def close():
    return ['</svg>']


def panel(x, y, w, h, title, right=None):
    o = [rrect(x, y, w, h, 14, "url(#gCard)", C["line"], 1)]
    if title:
        o.append(text(x + 18, y + 27, title, 12.5, C["txt"], 700))
    if right:
        o.append(text(x + w - 18, y + 27, right, 10, C["t3"], 600, "end"))
    return o


def tile(x, y, w, h, label, value, sub, col, ic, pillt=None):
    o = [rrect(x, y, w, h, 14, "url(#gCard)", C["line"], 1)]
    o.append(text(x + 18, y + 28, label, 11, C["t2"], 600))
    sz = 27 if len(value) <= 6 else 21
    o.append(text(x + 18, y + 62, value, sz, col, 800))
    o.append(text(x + 18, y + 80, sub, 9.5, C["t3"], 500))
    o.append(chip(x + w - 48, y + 14, ic, col))
    if pillt:
        o.append(pill(x + w - 16, y + h - 14, pillt[0], pillt[1]))
    return o


def areachart(x, y, w, h, pts, col, base=None):
    n = len(pts)
    lo, hi = min(pts), max(pts)
    if base is not None:
        lo = min(lo, base)
        hi = max(hi, base)
    pad = 0.12 * (hi - lo)
    lo -= pad
    rng = (hi - lo) or 1
    coords = [(x + w * i / (n - 1), y + h - (v - lo) / rng * h) for i, v in enumerate(pts)]
    line = " ".join(f"{a:.1f},{b:.1f}" for a, b in coords)
    o = []
    for gy in range(1, 4):
        yy = y + h * gy / 4
        o.append(f'<line x1="{x}" y1="{yy:.1f}" x2="{x+w}" y2="{yy:.1f}" stroke="{A(C["line"],0.5)}" stroke-width="1"/>')
    if base is not None:
        by = y + h - (base - lo) / rng * h
        o.append(f'<line x1="{x}" y1="{by:.1f}" x2="{x+w}" y2="{by:.1f}" stroke="{A(C["t3"],0.9)}" stroke-width="1" stroke-dasharray="4 4"/>')
        o.append(text(x + w - 2, by - 5, "baseline", 8.5, C["t3"], 500, "end"))
    o.append(f'<polygon points="{x},{y+h} {line} {x+w},{y+h}" fill="{A(col,0.13)}"/>')
    o.append(f'<polyline points="{line}" fill="none" stroke="{col}" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>')
    ex, ey = coords[-1]
    o.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="4" fill="{col}"/>')
    return "".join(o)


def table(x, y, w, cols, rows, rowh=36):
    o = []
    cx = x
    for label, frac, align in cols:
        cw = w * frac
        ax = cx + 10 if align == "start" else (cx + cw - 10 if align == "end" else cx + cw / 2)
        o.append(text(ax, y + 12, label, 9.5, C["t3"], 700, align, 0.4))
        cx += cw
    o.append(f'<line x1="{x}" y1="{y+22}" x2="{x+w}" y2="{y+22}" stroke="{C["line"]}" stroke-width="1"/>')
    yy = y + 22
    for row in rows:
        cx = x
        for (label, frac, align), cell in zip(cols, row):
            cw = w * frac
            ax = cx + 10 if align == "start" else (cx + cw - 10 if align == "end" else cx + cw / 2)
            if isinstance(cell, tuple):
                txt, tcol, twt = cell
                o.append(text(ax, yy + 24, txt, 10.5, tcol, twt, align))
            else:
                o.append(text(ax, yy + 24, cell, 10.5, C["txt"], 500, align))
            cx += cw
        yy += rowh
        o.append(f'<line x1="{x}" y1="{yy}" x2="{x+w}" y2="{yy}" stroke="{A(C["line"],0.45)}" stroke-width="1"/>')
    return "".join(o)


def goalbar(x, y, w, label, pct, val, col):
    o = [text(x, y, label, 11.5, C["txt"], 600),
         text(x + w, y, val, 11, col, 700, "end"),
         rrect(x, y + 8, w, 7, 4, "#0d1526", C["line"], 1),
         rrect(x, y + 8, max(8, w * pct), 7, 4, col)]
    return "".join(o)


# --------------------------------------------------------------------------- #
# views
# --------------------------------------------------------------------------- #
def v_overview():
    o = []
    tw = (IW - 3 * 20) / 4
    tiles = [("Heart rate", "72", "bpm · resting", C["red"], "heart"),
             ("Mood", "Calm", "4 / 5 today", C["green"], "leaf"),
             ("Sleep", "7h 45m", "good last night", C["violet"], "moon"),
             ("Guardian", "ON", "watching", C["green"], "shield")]
    for i, (lbl, val, sub, col, ic) in enumerate(tiles):
        o += tile(IX + i * (tw + 20), IY, tw, 96, lbl, val, sub, col, ic)
    y2 = IY + 96 + 22
    lw = IW * 0.64
    rw = IW - lw - 20
    ph = 268
    o += panel(IX, y2, lw, ph, "Heart rate — today", right="resting 60")
    o.append(areachart(IX + 20, y2 + 52, lw - 40, ph - 96,
                       [62, 64, 61, 70, 66, 72, 68, 74, 71, 69, 73, 72], C["red"], base=60))
    o += panel(IX + lw + 20, y2, rw, ph, "Baseline")
    bcx = IX + lw + 20 + rw / 2
    o.append(ring(bcx, y2 + 118, 58, 1.0, C["green"], 11))
    o.append(text(bcx, y2 + 116, "60", 34, "#fff", 800, "middle"))
    o.append(text(bcx, y2 + 138, "RESTING HR", 9, C["t2"], 600, "middle", 0.6))
    o.append(text(bcx, y2 + ph - 40, "learned from 40 calm samples", 9.5, C["t2"], 500, "middle"))
    o.append(status_dot(bcx + 34, y2 + ph - 20, "SET", "on"))
    y3 = y2 + ph + 22
    bh = CONTENT_Y + CONTENT_H - PAD - y3
    o += panel(IX, y3, lw, bh, "Recent guardian events", right="detect → guide → escalate")
    rows = [[("BIOMETRIC", C["cyan"], 700), "HR 78 · resp 16 · calm", ("10:12", C["t2"], 500)],
            [("CHECK-IN", C["green"], 700), "Mood 4 · energy 3", ("09:40", C["t2"], 500)],
            [("GUIDANCE", C["brandA"], 700), "Suggested a mindful break", ("08:20", C["t2"], 500)],
            [("FORESIGHT", C["amber"], 700), "Sleep debt building — heads-up", ("07:05", C["t2"], 500)]]
    o.append(table(IX + 18, y3 + 44, lw - 36,
                   [("TYPE", 0.22, "start"), ("DETAIL", 0.64, "start"), ("WHEN", 0.14, "end")], rows, rowh=32))
    o += panel(IX + lw + 20, y3, rw, bh, "Today")
    ty = y3 + 44
    for ic, col, k, s in [("bell", "violet", "Team meeting", "10:30"),
                          ("flame", "amber", "Gym", "6:00 PM"),
                          ("heart", "pink", "Call Mom", "evening")]:
        o.append(rrect(IX + lw + 38, ty, rw - 36, 46, 11, "rgba(255,255,255,0.03)", C["line"], 1))
        o.append(chip(IX + lw + 48, ty + 6, ic, ACCENT[col]))
        o.append(text(IX + lw + 92, ty + 21, k, 11.5, C["txt"], 650))
        o.append(text(IX + lw + 92, ty + 35, s, 9.5, C["t2"], 500))
        ty += 54
    return o


def v_monitoring():
    o = []
    tw = (IW - 3 * 20) / 4
    tiles = [("Heart rate", "110", "+38 over baseline", C["red"], "heart", ("ELEVATED", "warn")),
             ("Respiration", "22", "per minute", C["cyan"], "lung", ("ELEVATED", "warn")),
             ("Blood oxygen", "96%", "SpO₂", C["cyan"], "drop", None),
             ("Stress", "High", "detected now", C["red"], "bolt", ("ALERT", "crit"))]
    for i, (lbl, val, sub, col, ic, pt) in enumerate(tiles):
        o += tile(IX + i * (tw + 20), IY, tw, 96, lbl, val, sub, col, ic, pt)
    y2 = IY + 96 + 22
    lw = IW * 0.6
    rw = IW - lw - 20
    hh = CONTENT_Y + CONTENT_H - PAD - y2
    o += panel(IX, y2, lw, hh, "Heart rate — live", right="rising")
    o.append(areachart(IX + 20, y2 + 52, lw - 40, 220,
                       [60, 64, 70, 78, 88, 96, 104, 108, 110], C["red"], base=60))
    o.append(rrect(IX + 24, y2 + 300, lw - 48, 46, 11, A(C["red"], 0.09), C["red"], 1))
    o.append(icon("warn", IX + 46, y2 + 323, C["red"], 0.85))
    o.append(text(IX + 68, y2 + 320, "Anxiety pattern detected", 11.5, C["txt"], 650))
    o.append(text(IX + 68, y2 + 335, "guidance offered · monitoring continues", 9.5, C["t2"], 500))
    o += panel(IX + lw + 20, y2, rw, hh, "Detect → guide → escalate")
    lx = IX + lw + 20 + 30
    events = [("bolt", "cyan", "Biometric sample", "HR 110 · resp 22 · 10:02"),
              ("warn", "amber", "Detection", "anxiety · guidance"),
              ("shield", "green", "Guidance delivered", "breathing + reassurance"),
              ("phone", "red", "Escalation ready", "contact on standby")]
    ey = y2 + 60
    o.append(f'<line x1="{lx}" y1="{ey+8}" x2="{lx}" y2="{ey+8+len(events)*72-56}" stroke="{C["line"]}" stroke-width="2"/>')
    for ic, col, k, s in events:
        c = ACCENT[col]
        o.append(f'<circle cx="{lx}" cy="{ey+12}" r="11" fill="{C["scrB"]}" stroke="{c}" stroke-width="2"/>')
        o.append(icon(ic, lx, ey + 12, c, 0.6))
        o.append(rrect(lx + 26, ey - 6, rw - 88, 52, 12, "rgba(255,255,255,0.03)", C["line"], 1))
        o.append(text(lx + 44, ey + 12, k, 12, C["txt"], 700))
        o.append(text(lx + 44, ey + 28, s, 9.5, C["t2"], 500))
        ey += 72
    return o


def v_health():
    o = []
    tw = (IW - 3 * 20) / 4
    tiles = [("Heart rate", "72", "bpm", C["red"], "heart"),
             ("Sleep", "7h 45m", "last night", C["violet"], "moon"),
             ("Steps", "8,342", "today", C["green"], "steps"),
             ("Blood oxygen", "98%", "SpO₂", C["cyan"], "drop")]
    for i, (lbl, val, sub, col, ic) in enumerate(tiles):
        o += tile(IX + i * (tw + 20), IY, tw, 96, lbl, val, sub, col, ic)
    y2 = IY + 96 + 22
    lw = IW * 0.62
    rw = IW - lw - 20
    ph = 236
    o += panel(IX, y2, lw, ph, "Resting heart rate — 14 days", right="stable")
    o.append(areachart(IX + 20, y2 + 52, lw - 40, ph - 84,
                       [61, 60, 62, 59, 60, 61, 60, 62, 60, 59, 61, 60, 60, 60], C["green"], base=60))
    o += panel(IX + lw + 20, y2, rw, ph, "This month")
    my = y2 + 52
    for k, val, col in [("Avg mood", "4.1 ↑", C["green"]), ("Goals on track", "4 / 6", C["brandA"]),
                        ("Longest streak", "30 d", C["amber"]), ("Escalations", "2 · resolved", C["cyan"])]:
        o.append(text(IX + lw + 38, my, k, 11, C["t2"], 600))
        o.append(text(IX + lw + 20 + rw - 18, my, val, 12.5, col, 750, "end"))
        my += 42
    y3 = y2 + ph + 22
    bh = CONTENT_Y + CONTENT_H - PAD - y3
    o += panel(IX, y3, IW, bh, "Foresight", right="caught before it happens")
    cw = (IW - 36) / 3
    fore = [("lung", "cyan", "Blood oxygen slipping", "97 → 95 → 93%", [97, 95, 93]),
            ("moon", "violet", "Sleep debt building", "6.0 · 5.5 · 5.0 h", [6.0, 5.5, 5.0]),
            ("leaf", "amber", "Mood sliding", "5 → 4 → 3", [5, 4, 3])]
    for i, (ic, col, k, s, pts) in enumerate(fore):
        fx = IX + 18 + i * cw
        c = ACCENT[col]
        o.append(rrect(fx, y3 + 44, cw - 16, bh - 64, 12, "rgba(255,255,255,0.03)", C["line"], 1))
        o.append(chip(fx + 12, y3 + 56, ic, c))
        o.append(text(fx + 56, y3 + 70, k, 11, C["txt"], 650))
        o.append(text(fx + 56, y3 + 85, s, 9.5, C["t2"], 500))
        o.append(spark(fx + 16, y3 + 104, cw - 48, 30, pts, c))
    return o


def v_emergency():
    o = []
    lw = IW * 0.54
    rw = IW - lw - 20
    hh = CONTENT_H - 2 * PAD
    o += panel(IX, IY, lw, hh, "Emergency response", right="one coordinated action")
    o.append(button(IX + 24, IY + 48, lw - 48, "Call 911", "emer", 46))
    ry = IY + 112
    for k, s in [("Location shared", "with Maria & responders"),
                 ("Family contacted", "Maria Bianchi"),
                 ("Medical ID surfaced", "for first responders"),
                 ("AI first-aid guidance", "step-by-step, hands-free")]:
        o.append(rrect(IX + 24, ry, lw - 48, 52, 12, "rgba(255,255,255,0.03)", C["line"], 1))
        o.append(f'<circle cx="{IX+50}" cy="{ry+26}" r="12" fill="{C["green"]}"/>')
        o.append(text(IX + 50, ry + 30, "✓", 13, "#04160c", 900, "middle"))
        o.append(text(IX + 72, ry + 22, k, 12, C["txt"], 650))
        o.append(text(IX + 72, ry + 38, s, 10, C["t2"], 500))
        ry += 60
    # right: medical ID + providers
    o += panel(IX + lw + 20, IY, rw, 210, "Medical ID", right="scannable when locked")
    dx = IX + lw + 38
    dw = rw - 36
    for ic, col, k, s in [("cross", "red", "David Bianchi · 41", "Known: acute anxiety / panic"),
                          ("heart", "red", "Resting HR 60 bpm", "learned baseline"),
                          ("phone", "red", "Maria Bianchi", "emergency contact")]:
        o.append(rrect(dx, IY + 46 + [0, 54, 108][["cross", "heart", "phone"].index(ic)], dw, 46, 11, "rgba(255,255,255,0.03)", C["line"], 1))
    yy = IY + 46
    for ic, k, s in [("cross", "David Bianchi · 41", "Known: acute anxiety / panic"),
                     ("heart", "Resting HR 60 bpm", "learned baseline"),
                     ("phone", "Maria Bianchi", "emergency contact")]:
        o.append(chip(dx + 10, yy + 6, ic, C["red"]))
        o.append(text(dx + 54, yy + 22, k, 11.5, C["txt"], 650))
        o.append(text(dx + 54, yy + 37, s, 9.5, C["t2"], 500))
        yy += 54
    o += panel(IX + lw + 20, IY + 232, rw, hh - 232, "Providers", right="when AI reaches its limit")
    py = IY + 232 + 46
    for ic, col, k, s, st in [("cross", "red", "Bay Area Cardiology", "medical · 0.8 mi", ("OPEN", "on")),
                             ("brain", "violet", "Dr. Rivera, LCSW", "mental health · telehealth", None),
                             ("link", "cyan", "Consented handoff", "session summary, revocable", None)]:
        o.append(rrect(dx, py, dw, 52, 11, "rgba(255,255,255,0.03)", C["line"], 1))
        o.append(chip(dx + 10, py + 9, ic, ACCENT[col]))
        o.append(text(dx + 54, py + 23, k, 11.5, C["txt"], 650))
        o.append(text(dx + 54, py + 39, s, 9.5, C["t2"], 500))
        if st:
            o.append(status_dot(dx + dw - 14, py + 26, st[0], st[1]))
        py += 60
    return o


def v_coach():
    o = []
    lw = IW * 0.5
    rw = IW - lw - 20
    hh = CONTENT_H - 2 * PAD
    o += panel(IX, IY, lw, 260, "Life coach", right="24/7 across your life")
    ay = IY + 46
    for ic, col, k, s in [("brain", "violet", "Mental health", "grounded in recent check-ins"),
                          ("chart", "green", "Health & fitness", "tied to your goals"),
                          ("bolt", "brand", "Career", "interview prep ready"),
                          ("heart", "pink", "Relationships", "communication tips")]:
        o.append(rrect(IX + 24, ay, lw - 48, 44, 11, "rgba(255,255,255,0.03)", C["line"], 1))
        o.append(chip(IX + 34, ay + 5, ic, ACCENT[col]))
        o.append(text(IX + 78, ay + 20, k, 11.5, C["txt"], 650))
        o.append(text(IX + 78, ay + 34, s, 9.5, C["t2"], 500))
        ay += 52
    o += panel(IX, IY + 282, lw, hh - 282, "Goals")
    gy = IY + 282 + 52
    for lbl, pct, val, grad in [("Fitness · work out 4×/week", 0.75, "75%", C["green"]),
                                ("Career · launch new app", 0.6, "60%", C["brandA"]),
                                ("Wellness · meditate daily", 0.4, "40%", C["cyan"]),
                                ("Finance · save $10,000", 0.55, "55%", C["amber"])]:
        o.append(goalbar(IX + 24, gy, lw - 48, lbl, pct, val, grad))
        gy += 40
    # right: insights + habits
    o += panel(IX + lw + 20, IY, rw, 236, "Insights", right="proactive nudges")
    iy = IY + 46
    for ic, col, k, s, pt in [("warn", "amber", "High spending alert", "above your usual", ("ALERT", "warn")),
                             ("moon", "green", "You slept better", "7.5h · keep it up", ("PRAISE", "good")),
                             ("bolt", "brand", "Interview prep", "want a practice round?", None)]:
        o.append(rrect(IX + lw + 38, iy, rw - 36, 52, 11, "rgba(255,255,255,0.03)", C["line"], 1))
        o.append(chip(IX + lw + 50, iy + 9, ic, ACCENT[col]))
        o.append(text(IX + lw + 94, iy + 23, k, 11.5, C["txt"], 650))
        o.append(text(IX + lw + 94, iy + 39, s, 9.5, C["t2"], 500))
        if pt:
            o.append(pill(IX + lw + 20 + rw - 16, iy + 24, pt[0], pt[1]))
        iy += 60
    o += panel(IX + lw + 20, IY + 258, rw, hh - 258, "Habits", right="streaks")
    hy = IY + 258 + 46
    for ic, col, k, s, streak in [("flame", "amber", "Meditate", "daily", "🔥 12"),
                                  ("steps", "green", "Morning walk", "milestone", "30"),
                                  ("drop", "cyan", "Hydrate", "on track", "7")]:
        o.append(rrect(IX + lw + 38, hy, rw - 36, 46, 11, "rgba(255,255,255,0.03)", C["line"], 1))
        o.append(chip(IX + lw + 50, hy + 6, ic, ACCENT[col]))
        o.append(text(IX + lw + 94, hy + 21, k, 11.5, C["txt"], 650))
        o.append(text(IX + lw + 94, hy + 35, s, 9.5, C["t2"], 500))
        o.append(pill(IX + lw + 20 + rw - 16, hy + 23, streak, "warn"))
        hy += 54
    return o


def v_privacy():
    o = []
    lw = (IW - 20) / 2
    hh = CONTENT_H - 2 * PAD
    o += panel(IX, IY, lw, hh, "Connected sources", right="AI only sees what you allow")
    dx = IX + 20
    dw = lw - 40

    def togrow(y, ic, label, sub, on):
        r = [rrect(dx, y, dw, 48, 11, "rgba(255,255,255,0.03)", C["line"], 1)]
        r.append(chip(dx + 10, y + 7, ic, ACC if on else C["t3"]))
        r.append(text(dx + 54, y + 23, label, 11.5, C["txt"], 650))
        r.append(text(dx + 54, y + 38, sub, 9.5, C["t2"], 500))
        bg = C["green"] if on else "#2a3450"
        kx = dx + dw - 40 + 16 if on else dx + dw - 40 + 2
        r.append(rrect(dx + dw - 42, y + 14, 34, 20, 10, bg))
        r.append(f'<circle cx="{kx+8}" cy="{y+24}" r="8" fill="#fff"/>')
        return r
    ty = IY + 46
    for ic, lbl, sub, on in [("watch", "Wearable", "heart rate, sleep", True),
                             ("chart", "Spending", "transactions", True),
                             ("bell", "Calendar", "events", False),
                             ("chat", "Messages", "not connected", False)]:
        o += togrow(ty, ic, lbl, sub, on)
        ty += 56
    o.append(rrect(dx, ty + 6, dw, 46, 11, A(C["green"], 0.08), C["green"], 1))
    o.append(icon("eye", dx + 24, ty + 29, C["green"], 0.85))
    o.append(text(dx + 46, ty + 25, "Who accessed my data", 11.5, C["txt"], 650))
    o.append(text(dx + 46, ty + 40, "stored · read · erased — chain OK", 9.5, C["t2"], 500))
    # right: devices + model/cloud
    o += panel(IX + lw + 20, IY, lw, 260, "Devices", right="where Jim lives")
    ex = IX + lw + 20 + 20
    ew = lw - 40
    ey = IY + 46
    for ic, k, s, st in [("watch", "Apple Watch", "wearable · Bluetooth", ("ACTIVE", "on")),
                         ("mic", "Kitchen console", "on-device LLM", ("ON", "on")),
                         ("bolt", "Helper bot", "autonomous · relayed", ("IDLE", "avail"))]:
        o.append(rrect(ex, ey, ew, 52, 11, "rgba(255,255,255,0.03)", C["line"], 1))
        o.append(chip(ex + 10, ey + 9, ic, ACC))
        o.append(text(ex + 54, ey + 23, k, 11.5, C["txt"], 650))
        o.append(text(ex + 54, ey + 39, s, 9.5, C["t2"], 500))
        o.append(status_dot(ex + ew - 14, ey + 26, st[0], st[1]))
        ey += 60
    o += panel(IX + lw + 20, IY + 282, lw, hh - 282, "Model & cloud", right="greater model, opt-in")
    my = IY + 282 + 46
    for ic, col, k, s, st in [("cloud", "violet", "Cloud model", "local fallback", ("ON", "on")),
                             ("shield", "green", "Offline mode", "nothing leaves this device", ("READY", "on")),
                             ("eye", "cyan", "Contribution preview", "exactly what would be shared", None)]:
        o.append(rrect(ex, my, ew, 52, 11, "rgba(255,255,255,0.03)", C["line"], 1))
        o.append(chip(ex + 10, my + 9, ic, ACCENT[col]))
        o.append(text(ex + 54, my + 23, k, 11.5, C["txt"], 650))
        o.append(text(ex + 54, my + 39, s, 9.5, C["t2"], 500))
        if st:
            o.append(status_dot(ex + ew - 14, my + 26, st[0], st[1]))
        my += 60
    return o


VIEWS = [
    (1, "Overview", "Overview", v_overview),
    (2, "Live Monitoring", "Monitoring", v_monitoring),
    (3, "Health", "Health", v_health),
    (4, "Emergency & Guardian", "Emergency", v_emergency),
    (5, "Coach & Life", "Coach", v_coach),
    (6, "Privacy & Data", "Privacy", v_privacy),
]


def render(title, nav, fn):
    o = frame(title, nav)
    o += fn()
    o += close()
    return "".join(o)


def main():
    global PLATFORM_D
    total = 0
    for plat, sub in (("macos", ""), ("windows", "windows")):
        PLATFORM_D = plat
        outdir = OUT if not sub else os.path.join(OUT, sub)
        os.makedirs(outdir, exist_ok=True)
        for num, title, nav, fn in VIEWS:
            slug = title.lower().replace(" & ", "-").replace(" ", "-")
            with open(os.path.join(outdir, f"{num:02d}-{slug}.svg"), "w") as f:
                f.write(render(title, nav, fn))
            total += 1
    PLATFORM_D = "macos"
    print(f"generated {total} desktop screens ({len(VIEWS)} × 2 platforms)")


if __name__ == "__main__":
    main()
