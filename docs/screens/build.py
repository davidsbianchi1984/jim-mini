#!/usr/bin/env python3
"""Generate the Jim Mini app-screen SVGs — one static, full-colour screen per
capability, in the product's dark-OLED style. Run: python3 docs/screens/build.py
Output: docs/screens/NN-name.svg (+ a contact-sheet index.svg)."""

from __future__ import annotations

import html
import math
import os

OUT = os.path.dirname(os.path.abspath(__file__))

# ---- palette (matches the app mockups) ------------------------------------
C = {
    "scrA": "#0e1626", "scrB": "#0a0f1c", "frameA": "#20263a", "frameB": "#0c1020",
    "card": "#182238", "card2": "#1f2b45", "line": "#26314e", "tab": "#0b1220",
    "txt": "#eef1f7", "t2": "#8a94ad", "t3": "#626d88",
    "brandA": "#7c5cff", "brandB": "#3aa0ff",
    "red": "#ff4d5e", "emer": "#ff3b30", "green": "#43e08a", "amber": "#f7b731",
    "cyan": "#38bdf8", "violet": "#a78bfa", "pink": "#f472b6", "teal": "#2dd4bf",
}
ACCENT = {"red": C["red"], "green": C["green"], "amber": C["amber"],
          "cyan": C["cyan"], "violet": C["violet"], "brand": C["brandA"],
          "emer": C["emer"], "pink": C["pink"], "teal": C["teal"]}
FONT = ("-apple-system,BlinkMacSystemFont,'SF Pro Text','Segoe UI',"
        "Roboto,system-ui,sans-serif")

W, H = 320, 660
PX, PY, PW, PH = 10, 12, 300, 636
SX, SY, SW, SH = 20, 22, 280, 616
CX, CW = 34, 252            # content left / width


def esc(s):
    return html.escape(str(s), quote=True)


def A(hexcol, a):
    """hex #rrggbb + alpha 0..1 -> rgba() string. Renderer-agnostic: 8-digit
    hex alpha renders opaque in some SVG converters (e.g. cairosvg); rgba() is
    honoured everywhere."""
    h = hexcol.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{a})"


# --------------------------------------------------------------------------- #
# tiny vector icon set (drawn, not emoji, so it renders identically anywhere)
# --------------------------------------------------------------------------- #
def icon(name, cx, cy, col, s=1.0):
    def sc(v):
        return v * s
    p = f'fill="{col}"'
    st = f'fill="none" stroke="{col}" stroke-width="{1.7*s:.2f}" stroke-linecap="round" stroke-linejoin="round"'
    if name == "heart":
        return (f'<path d="M{cx} {cy+sc(6)} C{cx-sc(9)} {cy-sc(3)},{cx-sc(7)} {cy-sc(9)},{cx} {cy-sc(4)} '
                f'C{cx+sc(7)} {cy-sc(9)},{cx+sc(9)} {cy-sc(3)},{cx} {cy+sc(6)} Z" {p}/>')
    if name == "moon":
        return (f'<path d="M{cx+sc(5)} {cy} a{sc(6)} {sc(6)} 0 1 1 -{sc(7)} -{sc(6)} '
                f'a{sc(8)} {sc(8)} 0 1 0 {sc(7)} {sc(6)} Z" {p}/>')
    if name == "steps":
        return "".join(f'<rect x="{cx-sc(7)+i*sc(5)}" y="{cy+sc(4)-i*sc(3)}" width="{sc(3.2)}" '
                       f'height="{sc(2+i*3)}" rx="1" {p}/>' for i in range(4))
    if name == "brain":
        return (f'<circle cx="{cx-sc(3)}" cy="{cy}" r="{sc(5)}" {st}/>'
                f'<circle cx="{cx+sc(3)}" cy="{cy}" r="{sc(5)}" {st}/>')
    if name == "drop":
        return (f'<path d="M{cx} {cy-sc(7)} C{cx+sc(7)} {cy+sc(1)},{cx+sc(5)} {cy+sc(7)},{cx} {cy+sc(7)} '
                f'C{cx-sc(5)} {cy+sc(7)},{cx-sc(7)} {cy+sc(1)},{cx} {cy-sc(7)} Z" {p}/>')
    if name == "lung":
        return (f'<path d="M{cx} {cy-sc(7)} v{sc(6)}" {st}/>'
                f'<path d="M{cx-sc(1)} {cy-sc(2)} c-{sc(5)} 0 -{sc(6)} {sc(4)} -{sc(5)} {sc(8)} l{sc(4)} 0 v-{sc(9)}" {st}/>'
                f'<path d="M{cx+sc(1)} {cy-sc(2)} c{sc(5)} 0 {sc(6)} {sc(4)} {sc(5)} {sc(8)} l-{sc(4)} 0 v-{sc(9)}" {st}/>')
    if name == "bolt":
        return f'<path d="M{cx+sc(2)} {cy-sc(8)} L{cx-sc(6)} {cy+sc(1)} L{cx} {cy+sc(1)} L{cx-sc(2)} {cy+sc(8)} L{cx+sc(6)} {cy-sc(1)} L{cx} {cy-sc(1)} Z" {p}/>'
    if name == "phone":
        return f'<path d="M{cx-sc(6)} {cy-sc(6)} c0 {sc(9)} {sc(3)} {sc(12)} {sc(12)} {sc(12)} l{sc(0)} -{sc(4)} l-{sc(4)} -{sc(2)} l-{sc(2)} {sc(2)} c-{sc(3)} -{sc(1)} -{sc(4)} -{sc(2)} -{sc(4)} -{sc(4)} l{sc(2)} -{sc(2)} l-{sc(2)} -{sc(4)} Z" {p}/>'
    if name == "shield":
        return f'<path d="M{cx} {cy-sc(8)} l{sc(7)} {sc(3)} v{sc(5)} c0 {sc(5)} -{sc(3)} {sc(7)} -{sc(7)} {sc(9)} c-{sc(4)} -{sc(2)} -{sc(7)} -{sc(4)} -{sc(7)} -{sc(9)} v-{sc(5)} Z" {st}/>'
    if name == "chart":
        return "".join(f'<rect x="{cx-sc(7)+i*sc(5)}" y="{cy+sc(6)-sc([5,9,4,11][i])}" width="{sc(3.2)}" height="{sc([5,9,4,11][i])}" rx="1" {p}/>' for i in range(4))
    if name == "book":
        return (f'<rect x="{cx-sc(7)}" y="{cy-sc(7)}" width="{sc(14)}" height="{sc(14)}" rx="2" {st}/>'
                f'<path d="M{cx} {cy-sc(7)} v{sc(14)}" {st}/>')
    if name == "target":
        return (f'<circle cx="{cx}" cy="{cy}" r="{sc(7.5)}" {st}/>'
                f'<circle cx="{cx}" cy="{cy}" r="{sc(3.5)}" {st}/>'
                f'<circle cx="{cx}" cy="{cy}" r="{sc(0.9)}" {p}/>')
    if name == "chat":
        return f'<path d="M{cx-sc(8)} {cy-sc(6)} h{sc(16)} a2 2 0 0 1 2 2 v{sc(7)} a2 2 0 0 1 -2 2 h-{sc(9)} l-{sc(4)} {sc(4)} v-{sc(4)} h-{sc(3)} a2 2 0 0 1 -2 -2 v-{sc(7)} a2 2 0 0 1 2 -2 Z" {st}/>'
    if name == "mic":
        return (f'<rect x="{cx-sc(3)}" y="{cy-sc(8)}" width="{sc(6)}" height="{sc(11)}" rx="{sc(3)}" {st}/>'
                f'<path d="M{cx-sc(6)} {cy} c0 {sc(5)} {sc(12)} {sc(5)} {sc(12)} 0 M{cx} {cy+sc(5)} v{sc(3)}" {st}/>')
    if name == "gear":
        teeth = "".join(f'<rect x="{cx-sc(1.3)}" y="{cy-sc(9)}" width="{sc(2.6)}" height="{sc(4)}" rx="1" transform="rotate({a} {cx} {cy})" {p}/>' for a in range(0, 360, 45))
        return teeth + f'<circle cx="{cx}" cy="{cy}" r="{sc(4.6)}" {st}/>'
    if name == "person":
        return (f'<circle cx="{cx}" cy="{cy-sc(4)}" r="{sc(3.4)}" {st}/>'
                f'<path d="M{cx-sc(6)} {cy+sc(7)} c0 -{sc(6)} {sc(12)} -{sc(6)} {sc(12)} 0" {st}/>')
    if name == "warn":
        return (f'<path d="M{cx} {cy-sc(8)} L{cx+sc(8)} {cy+sc(6)} H{cx-sc(8)} Z" {st}/>'
                f'<path d="M{cx} {cy-sc(3)} v{sc(4)}" {st}/><circle cx="{cx}" cy="{cy+sc(4)}" r="{sc(0.9)}" {p}/>')
    if name == "plus":
        return f'<path d="M{cx} {cy-sc(7)} v{sc(14)} M{cx-sc(7)} {cy} h{sc(14)}" fill="none" stroke="{col}" stroke-width="{2.4*s:.2f}" stroke-linecap="round"/>'
    if name == "cross":  # medical
        return f'<path d="M{cx} {cy-sc(7)} v{sc(14)} M{cx-sc(7)} {cy} h{sc(14)}" fill="none" stroke="{col}" stroke-width="{3*s:.2f}" stroke-linecap="round"/>'
    if name == "bell":
        return f'<path d="M{cx} {cy-sc(8)} c{sc(5)} 0 {sc(5)} {sc(4)} {sc(5)} {sc(8)} l{sc(2)} {sc(2)} h-{sc(14)} l{sc(2)} -{sc(2)} c0 -{sc(4)} 0 -{sc(8)} {sc(5)} -{sc(8)} M{cx-sc(2)} {cy+sc(6)} c0 {sc(3)} {sc(4)} {sc(3)} {sc(4)} 0" {st}/>'
    if name == "eye":
        return (f'<path d="M{cx-sc(8)} {cy} c{sc(4)} -{sc(6)} {sc(12)} -{sc(6)} {sc(16)} 0 c-{sc(4)} {sc(6)} -{sc(12)} {sc(6)} -{sc(16)} 0 Z" {st}/>'
                f'<circle cx="{cx}" cy="{cy}" r="{sc(2.4)}" {p}/>')
    if name == "watch":
        return (f'<rect x="{cx-sc(5)}" y="{cy-sc(5)}" width="{sc(10)}" height="{sc(10)}" rx="2.5" {st}/>'
                f'<path d="M{cx-sc(2.5)} {cy-sc(5)} v-{sc(3)} h{sc(5)} v{sc(3)} M{cx-sc(2.5)} {cy+sc(5)} v{sc(3)} h{sc(5)} v-{sc(3)}" {st}/>')
    if name == "link":
        return f'<path d="M{cx-sc(2)} {cy+sc(2)} l-{sc(3)} {sc(3)} a{sc(3)} {sc(3)} 0 0 1 -{sc(4)} -{sc(4)} l{sc(3)} -{sc(3)} m{sc(6)} -{sc(2)} l{sc(3)} -{sc(3)} a{sc(3)} {sc(3)} 0 0 1 {sc(4)} {sc(4)} l-{sc(3)} {sc(3)} M{cx-sc(3)} {cy+sc(3)} l{sc(6)} -{sc(6)}" {st}/>'
    if name == "flame":
        return f'<path d="M{cx} {cy-sc(8)} c{sc(5)} {sc(4)} {sc(2)} {sc(6)} {sc(2)} {sc(8)} a{sc(4)} {sc(4)} 0 1 1 -{sc(8)} 0 c0 -{sc(2)} {sc(1)} -{sc(3)} {sc(2)} -{sc(4)} c0 {sc(2)} {sc(2)} {sc(2)} {sc(2)} 0 c0 -{sc(3)} {sc(2)} -{sc(4)} {sc(2)} -{sc(4)} Z" {p}/>'
    if name == "clip":  # clipboard / report
        return (f'<rect x="{cx-sc(6)}" y="{cy-sc(7)}" width="{sc(12)}" height="{sc(15)}" rx="2" {st}/>'
                f'<rect x="{cx-sc(3)}" y="{cy-sc(9)}" width="{sc(6)}" height="{sc(3)}" rx="1" {p}/>'
                f'<path d="M{cx-sc(3)} {cy-sc(1)} h{sc(6)} M{cx-sc(3)} {cy+sc(3)} h{sc(6)}" {st}/>')
    if name == "cloud":
        return f'<path d="M{cx-sc(6)} {cy+sc(4)} a{sc(4)} {sc(4)} 0 0 1 {sc(1)} -{sc(8)} a{sc(5)} {sc(5)} 0 0 1 {sc(10)} {sc(1)} a{sc(3.5)} {sc(3.5)} 0 0 1 -{sc(1)} {sc(7)} Z" {st}/>'
    if name == "leaf":
        return f'<path d="M{cx-sc(6)} {cy+sc(6)} c0 -{sc(9)} {sc(6)} -{sc(13)} {sc(12)} -{sc(12)} c{sc(1)} {sc(6)} -{sc(3)} {sc(12)} -{sc(12)} {sc(12)} Z M{cx-sc(3)} {cy+sc(3)} l{sc(6)} -{sc(6)}" {st}/>'
    # fallback dot
    return f'<circle cx="{cx}" cy="{cy}" r="{sc(4)}" {p}/>'


# --------------------------------------------------------------------------- #
# primitives
# --------------------------------------------------------------------------- #
def rrect(x, y, w, h, r, fill, stroke=None, sw=1):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r}" fill="{fill}"{s}/>'


def text(x, y, s, size, fill, weight=400, anchor="start", spacing=0, mono=False):
    ls = f' letter-spacing="{spacing}"' if spacing else ""
    fam = "ui-monospace,Menlo,monospace" if mono else FONT
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{ls}>{esc(s)}</text>')


def chip(x, y, ic, col):
    bg = A(col, 0.16)
    return (rrect(x, y, 34, 34, 11, bg) + icon(ic, x + 17, y + 17, col, 0.92))


def pill(x, y, label, tone):
    col = {"good": C["green"], "warn": C["amber"], "crit": C["emer"],
           "info": C["cyan"], "brand": C["brandA"]}[tone]
    w = 12 + len(label) * 6.2
    return (rrect(x - w, y - 11, w, 17, 8, A(col, 0.15))
            + text(x - w / 2, y + 1, label, 9.5, col, 700, "middle", 0.4))


def meter(x, y, w, pct, grad):
    return (rrect(x, y, w, 7, 4, "#0d1526", C["line"], 1)
            + rrect(x, y, max(6, w * pct), 7, 4, f"url(#{grad})"))


def spark(x, y, w, h, pts, col):
    n = len(pts)
    lo, hi = min(pts), max(pts)
    rng = (hi - lo) or 1
    coords = []
    for i, v in enumerate(pts):
        px = x + w * i / (n - 1)
        py = y + h - (v - lo) / rng * h
        coords.append(f"{px:.1f},{py:.1f}")
    endx, endy = coords[-1].split(",")
    return (f'<polyline points="{" ".join(coords)}" fill="none" stroke="{col}" '
            f'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<circle cx="{endx}" cy="{endy}" r="3.2" fill="{col}"/>')


def button(x, y, w, label, kind="brand", h=40):
    if kind == "brand":
        fill = "url(#gBrand)"
        tcol = "#fff"
    elif kind == "emer":
        fill = "url(#gEmer)"
        tcol = "#fff"
    else:
        fill = "rgba(255,255,255,0.06)"
        tcol = C["txt"]
    st = C["line"] if kind == "ghost" else None
    return (rrect(x, y, w, h, 13, fill, st, 1)
            + text(x + w / 2, y + h / 2 + 4.5, label, 13, tcol, 700, "middle"))


def toggle(x, y, on):
    bg = C["green"] if on else "#2a3450"
    kx = x + 16 if on else x + 2
    return (rrect(x, y, 34, 20, 10, bg)
            + f'<circle cx="{kx+8}" cy="{y+10}" r="8" fill="#fff"/>')


# --------------------------------------------------------------------------- #
# frame
# --------------------------------------------------------------------------- #
PLATFORM = "ios"          # "ios" | "android"


def _status_icons(xr, y, col):
    o = []
    if PLATFORM == "android":
        o.append(rrect(xr - 9, y - 7, 8, 12, 1.5, "none", col, 1.2))
        o.append(rrect(xr - 7.5, y - 3, 5, 7, 1, col))
        o.append(f'<path d="M{xr-20} {y+5} L{xr-15} {y-4} L{xr-10} {y+5} Z" fill="{col}"/>')
        o.append(f'<path d="M{xr-33} {y+5} L{xr-33} {y-2} L{xr-25} {y+5} Z" fill="{col}"/>')
    else:
        o.append(rrect(xr - 22, y - 6, 20, 11, 3, "none", col, 1.1))
        o.append(rrect(xr - 20, y - 4, 14, 7, 2, col))
        o.append(rrect(xr - 1.4, y - 2.5, 2, 5, 1, col))
        o.append(f'<path d="M{xr-35} {y-1} a6 6 0 0 1 11 0" fill="none" stroke="{col}" stroke-width="1.3"/>')
        o.append(f'<circle cx="{xr-29.5}" cy="{y+3}" r="1.2" fill="{col}"/>')
        for i in range(4):
            o.append(rrect(xr - 52 + i * 4, y + 4 - (i + 1) * 1.9, 2.6, (i + 1) * 1.9, 0.8, col))
    return "".join(o)


def statusbar():
    tcol = C["silver"] if "silver" in C else C["t2"]
    notch = "#05070d"
    o = []
    if PLATFORM == "android":
        o.append(f'<circle cx="{W/2}" cy="{SY+12}" r="4.5" fill="{notch}"/>')
        o.append(f'<circle cx="{W/2}" cy="{SY+12}" r="4.5" fill="none" stroke="{C["line"]}" stroke-width="1"/>')
    else:
        o.append(rrect(W / 2 - 30, SY + 5, 60, 15, 7.5, notch))
    o.append(text(SX + 14, SY + 34, "9:41", 11, tcol, 600))
    o.append(_status_icons(SX + SW - 14, SY + 34, tcol))
    return o


def navbar():
    o = []
    yb = SY + SH - 6
    if PLATFORM == "android":
        cx = W / 2
        o.append(f'<path d="M{cx-34+5} {yb-4.5} L{cx-34-5} {yb} L{cx-34+5} {yb+4.5} Z" fill="none" stroke="rgba(255,255,255,0.5)" stroke-width="1.3" stroke-linejoin="round"/>')
        o.append(f'<circle cx="{cx}" cy="{yb}" r="4.6" fill="none" stroke="rgba(255,255,255,0.5)" stroke-width="1.3"/>')
        o.append(rrect(cx + 34 - 4.6, yb - 4.6, 9.2, 9.2, 1.6, "none", "rgba(255,255,255,0.5)", 1.3))
    else:
        o.append(rrect(W / 2 - 42, yb - 1, 84, 4, 2, "rgba(255,255,255,0.6)"))
    return o


def head(num, title, sub, accent="brand"):
    ac = ACCENT.get(accent, C["brandA"])
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'viewBox="0 0 {W} {H}" role="img" aria-label="{esc(title)} screen">']
    out.append(f'''<defs>
      <linearGradient id="gScr" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="{C['scrA']}"/><stop offset="1" stop-color="{C['scrB']}"/></linearGradient>
      <linearGradient id="gFrame" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stop-color="{C['frameA']}"/><stop offset="1" stop-color="{C['frameB']}"/></linearGradient>
      <linearGradient id="gCard" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="{C['card']}"/><stop offset="1" stop-color="{C['card2']}"/></linearGradient>
      <linearGradient id="gBrand" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0" stop-color="{C['brandA']}"/><stop offset="1" stop-color="{C['brandB']}"/></linearGradient>
      <linearGradient id="gEmer" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#ff5b52"/><stop offset="1" stop-color="{C['emer']}"/></linearGradient>
      <linearGradient id="mV" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{C['brandA']}"/><stop offset="1" stop-color="{C['brandB']}"/></linearGradient>
      <linearGradient id="mO" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#f7b731"/><stop offset="1" stop-color="#ff7a45"/></linearGradient>
      <linearGradient id="mG" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#2fd27a"/><stop offset="1" stop-color="#43e08a"/></linearGradient>
      <radialGradient id="orb" cx="34%" cy="30%" r="75%">
        <stop offset="0" stop-color="#c3b0ff"/><stop offset="42%" stop-color="{C['brandA']}"/>
        <stop offset="80%" stop-color="#2f6cf0"/><stop offset="100%" stop-color="#14204a"/></radialGradient>
    </defs>''')
    out.append(rrect(PX, PY, PW, PH, 40, "url(#gFrame)"))
    out.append(rrect(SX, SY, SW, SH, 31, "url(#gScr)"))
    out += statusbar()
    out.append(text(CX, SY + 66, title, 20, C["txt"], 700, spacing=-0.4))
    if sub:
        out.append(text(CX, SY + 84, sub, 11.5, C["t2"], 400))
    return out


def tabbar(active):
    tabs = [("home", "Home"), ("chat", "Chat"), ("mic", "Voice"),
            ("book", "Memories"), ("person", "Profile")]
    out = [rrect(SX, SY + SH - 52, SW, 52, 0, C["tab"])]
    out.append(f'<rect x="{SX}" y="{SY+SH-52}" width="{SW}" height="1" fill="{C["line"]}"/>')
    step = SW / 5
    for i, (ic, lbl) in enumerate(tabs):
        cx = SX + step * i + step / 2
        on = (i == active)
        col = C["txt"] if on else C["t3"]
        gi = "person" if ic == "home" else ic
        gi = "target" if ic == "home" else gi
        out.append(icon("target" if ic == "home" else ic, cx, SY + SH - 34, col, 0.72))
        out.append(text(cx, SY + SH - 12, lbl, 8.5, col, 600, "middle"))
    return out


def close():
    return ['</svg>']


# --------------------------------------------------------------------------- #
# card stack layout
# --------------------------------------------------------------------------- #
def card_block(y, c):
    """c: dict(icon,color,k,s,pill=(label,tone),metric,extra)  -> (svg, next_y)."""
    h = c.get("h", 52)
    extra = c.get("extra")
    if extra and extra[0] in ("meter", "spark"):
        h = 66
    out = [rrect(CX, y, CW, h, 16, "url(#gCard)", C["line"], 1)]
    tx = CX + 14
    if c.get("icon"):
        out.append(chip(CX + 12, y + (h - 34) / 2 if not extra else y + 9, c["icon"], ACCENT[c["color"]]))
        tx = CX + 56
    ty = y + (26 if extra else h / 2 - 6)
    out.append(text(tx, ty, c["k"], 13, C["txt"], 600))
    if c.get("s"):
        out.append(text(tx, ty + 15, c["s"], 11, C["t2"]))
    if c.get("metric"):
        out.append(text(CX + CW - 14, y + h / 2 + 7, c["metric"], 20, C["txt"], 750, "end"))
    if c.get("pill"):
        out.append(pill(CX + CW - 14, y + 20, c["pill"][0], c["pill"][1]))
    if extra:
        if extra[0] == "meter":
            out.append(meter(tx, y + h - 16, CW - (tx - CX) - 14, extra[1], extra[2]))
        elif extra[0] == "spark":
            out.append(spark(tx, y + h - 30, CW - (tx - CX) - 16, 22, extra[1], ACCENT[extra[2]]))
    return "".join(out), y + h + 10


def orb(cx, cy, r):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#orb)"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="rgba(255,255,255,0.13)" stroke-width="1"/>'
            f'<ellipse cx="{cx-r*0.28}" cy="{cy-r*0.32}" rx="{r*0.28}" ry="{r*0.18}" fill="rgba(255,255,255,0.33)"/>')


def ring(cx, cy, r, pct, col, sw=9):
    circ = 2 * math.pi * r
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{A(col,0.13)}" stroke-width="{sw}"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{col}" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-dasharray="{circ*pct:.1f} {circ:.1f}" '
            f'transform="rotate(-90 {cx} {cy})"/>')


def apple_mark(x, y, s=0.66, col="#0b0b0f"):
    return (f'<g transform="translate({x:.1f},{y:.1f}) scale({s})" fill="{col}">'
            '<path d="M16.365 1.43c0 1.14-.493 2.27-1.177 3.08-.744.9-1.99 1.57-2.987 1.49'
            '-.12-1.15.42-2.35 1.07-3.08.72-.81 2.02-1.47 3.09-1.49z'
            'M20.5 17.06c-.06.14-.94 3.22-3.1 3.25-1.75.02-2.31-1.04-4.31-1.04-2 0-2.62 1.02-4.28 1.06'
            '-2.09.08-3.68-3.29-3.74-3.43-.06-.14-1.62-6.18 1.32-9.03.98-.96 2.36-1.5 3.65-1.5'
            ' 1.75 0 2.82 1.05 4.25 1.05 1.37 0 2.2-1.05 4.28-1.05 1.03 0 2.6.42 3.6 1.66'
            '-3.16 1.73-2.65 6.24.53 8.03z"/></g>')


def google_mark(x, y, s=0.66):
    return (f'<g transform="translate({x:.1f},{y:.1f}) scale({s})">'
            '<path fill="#4285F4" d="M23.06 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h6.2a5.3 5.3 0 0 1-2.3 3.48v2.89h3.72c2.18-2 3.44-4.96 3.44-8.38z"/>'
            '<path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.94-2.91l-3.72-2.89c-1.03.69-2.35 1.1-4.22 1.1-3.25 0-6-2.19-6.98-5.13H1.18v2.98A12 12 0 0 0 12 24z"/>'
            '<path fill="#FBBC05" d="M5.02 14.27a7.2 7.2 0 0 1 0-4.54V6.75H1.18a12 12 0 0 0 0 10.5l3.84-2.98z"/>'
            '<path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.3-3.3C17.95 1.19 15.24 0 12 0A12 12 0 0 0 1.18 6.75l3.84 2.98C6 6.94 8.75 4.75 12 4.75z"/></g>')


def envelope(cx, cy, col):
    return (f'<rect x="{cx-9:.1f}" y="{cy-6:.1f}" width="18" height="13" rx="2.5" fill="none" stroke="{col}" stroke-width="1.7"/>'
            f'<path d="M{cx-8:.1f} {cy-4:.1f} L{cx:.1f} {cy+2:.1f} L{cx+8:.1f} {cy-4:.1f}" fill="none" stroke="{col}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>')


# --------------------------------------------------------------------------- #
# screen definitions
# --------------------------------------------------------------------------- #
def render(spec):
    num = spec["num"]
    out = head(f"{num:02d}", spec["title"], spec.get("sub", ""), spec.get("accent", "brand"))
    y = SY + 100
    hero = spec.get("hero")

    if hero == "welcome":
        out.append(orb(W / 2, y + 44, 34))
        out.append(text(W / 2, y + 104, "Jim Mini", 22, "#fff", 750, "middle"))
        out.append(text(W / 2, y + 124, "Your AI companion. Always here.", 11.5, C["t2"], 400, "middle"))
        y += 150
        for lbl in ("Understands you", "Protects your privacy",
                    "Helps you every day", "Learns what matters"):
            out.append(rrect(CX, y, CW, 40, 13, "url(#gCard)", C["line"], 1))
            out.append(icon("shield", CX + 24, y + 20, C["brandA"], 0.7))
            out.append(text(CX + 44, y + 24, lbl, 12.5, C["txt"], 600))
            y += 48
        out.append(button(CX, y + 4, CW, "Get Started", "brand", 42))

    elif hero == "voice":
        out.append(text(W / 2, y + 6, "Listening…", 15, C["txt"], 600, "middle"))
        out.append(orb(W / 2, y + 92, 66))
        for i, rr in enumerate((80, 96, 110)):
            out.append(f'<circle cx="{W/2}" cy="{y+92}" r="{rr}" fill="none" stroke="{C["brandA"]}" stroke-width="1" opacity="{0.28-i*0.08:.2f}"/>')
        # waveform
        bars = "".join(f'<rect x="{CX+18+i*10}" y="{y+188-h/2}" width="4" height="{h}" rx="2" fill="url(#gBrand)"/>'
                       for i, h in enumerate([10, 22, 34, 18, 40, 26, 14, 30, 20, 36, 12, 24, 16, 28, 10, 20, 32, 14, 24, 12]))
        out.append(bars)
        out.append(f'<circle cx="{W/2}" cy="{y+238}" r="22" fill="url(#gBrand)"/>')
        out.append(icon("mic", W / 2, y + 238, "#fff", 1.0))
        out.append(text(W / 2, y + 280, "Tap to stop", 11.5, C["t2"], 500, "middle"))

    elif hero == "chat":
        out.append(rrect(CX + 70, y, CW - 70, 34, 13, "url(#gBrand)"))
        out.append(text(CX + CW - 14, y + 21, "I'm stressed today.", 11.5, "#fff", 500, "end"))
        y += 46
        out.append(rrect(CX, y, CW - 40, 96, 14, "url(#gCard)", C["line"], 1))
        for i, ln in enumerate(["I noticed your heart rate has", "been elevated for 20 minutes.",
                                 "Would you like a breathing", "exercise, or to talk it through?"]):
            out.append(text(CX + 14, y + 24 + i * 18, ln, 11.5, C["txt"], 400))
        y += 108
        out.append(rrect(CX, y, 118, 30, 10, "rgba(255,255,255,0.06)", C["line"], 1))
        out.append(text(CX + 59, y + 19, "Breathing Exercise", 10.5, C["txt"], 600, "middle"))
        out.append(rrect(CX + 128, y, 70, 30, 10, "rgba(255,255,255,0.06)", C["line"], 1))
        out.append(text(CX + 163, y + 19, "Let's Talk", 10.5, C["txt"], 600, "middle"))
        y += 44
        out.append(rrect(CX, y, CW, 40, 13, "#0c1424", C["line"], 1))
        out.append(text(CX + 14, y + 24, "Type a message…", 11.5, C["t3"]))
        out.append(icon("mic", CX + CW - 20, y + 20, C["t2"], 0.8))

    elif hero == "cpr":
        out.append(f'<circle cx="{W/2}" cy="{y+80}" r="66" fill="none" stroke="{C["red"]}" stroke-width="2" opacity=".5"/>')
        out.append(f'<circle cx="{W/2}" cy="{y+80}" r="52" fill="{C["red"]}14"/>')
        out.append(text(W / 2, y + 46, "PUSH HARD & FAST", 9.5, "#ffb3ba", 700, "middle", 0.4))
        out.append(text(W / 2, y + 92, "18", 44, "#fff", 800, "middle"))
        out.append(text(W / 2, y + 110, "COMPRESSIONS", 9, C["t2"], 600, "middle", 0.6))
        # pace light
        out.append(f'<circle cx="{CX+CW-20}" cy="{y+18}" r="8" fill="{C["green"]}"/>')
        out.append(text(CX + CW - 34, y + 22, "pace", 10, C["t2"], 500, "end"))
        y += 168
        s, y = card_block(y, {"icon": "heart", "color": "red", "k": "110 / min",
                              "s": "30 : 2  ·  compressions to breaths"})
        out.append(s)
        out.append(button(CX, y, CW, "▶  Start compressions", "emer", 42))

    elif hero == "emergency":
        out.append(button(CX, y, CW, "Call 911", "emer", 44))
        y += 56
        for k, s in [("Location shared", "with Maria & responders"),
                     ("Family contacted", "Maria Bianchi"),
                     ("Medical ID surfaced", "for first responders"),
                     ("AI first-aid guidance", "step-by-step")]:
            out.append(rrect(CX, y, CW, 44, 13, "url(#gCard)", C["line"], 1))
            out.append(f'<circle cx="{CX+22}" cy="{y+22}" r="10" fill="{C["green"]}"/>')
            out.append(text(CX + 22, y + 26, "✓", 12, "#04160c", 900, "middle"))
            out.append(text(CX + 42, y + 20, k, 12.5, C["txt"], 600))
            out.append(text(CX + 42, y + 34, s, 10.5, C["t2"]))
            y += 52

    elif hero == "sos":
        out.append(f'<circle cx="{W/2}" cy="{y+70}" r="52" fill="url(#gEmer)"/>')
        out.append(f'<circle cx="{W/2}" cy="{y+70}" r="66" fill="none" stroke="{C["emer"]}" stroke-width="1.5" opacity=".4"/>')
        out.append(icon("phone", W / 2, y + 62, "#fff", 1.5))
        out.append(text(W / 2, y + 92, "Call 911", 13, "#fff", 700, "middle"))
        y += 150
        for ic, k, s in [("person", "Share Location", "Send to contacts"),
                         ("cross", "Medical Information", "View your details"),
                         ("phone", "Contact Family", "Notify contacts"),
                         ("shield", "AI Guidance", "Step-by-step instructions")]:
            s2, y = card_block(y, {"icon": ic, "color": "red", "k": k, "s": s, "h": 50})
            out.append(s2)

    elif hero == "medid":
        # QR
        import random
        random.seed(7)
        qx, qy, qs = W / 2 - 62, y, 124
        out.append(rrect(qx, qy, qs, qs, 14, "#ffffff"))
        cell = (qs - 20) / 21
        def finder(r, c):
            res = []
            for i in range(7):
                for j in range(7):
                    on = i in (0, 6) or j in (0, 6) or (2 <= i <= 4 and 2 <= j <= 4)
                    if on:
                        res.append(rrect(qx + 10 + (c + j) * cell, qy + 10 + (r + i) * cell, cell, cell, 0, "#0a0f1c"))
            return "".join(res)
        grid = []
        for r in range(21):
            for c in range(21):
                if (r < 8 and c < 8) or (r < 8 and c > 12) or (r > 12 and c < 8):
                    continue
                if random.random() > 0.52:
                    grid.append(rrect(qx + 10 + c * cell, qy + 10 + r * cell, cell, cell, 0, "#0a0f1c"))
        out.append("".join(grid) + finder(0, 0) + finder(0, 14) + finder(14, 0))
        out.append(text(W / 2, qy + qs + 18, "jim.app/medical-id/med_rM7…QKyk", 10, C["violet"], 500, "middle"))
        y = qy + qs + 34
        for ic, k, s in [("cross", "David Bianchi · 41", "Known: acute anxiety / panic"),
                         ("heart", "Resting HR 60 bpm", "learned baseline"),
                         ("phone", "Maria Bianchi", "emergency contact")]:
            s2, y = card_block(y, {"icon": ic, "color": "red", "k": k, "s": s, "h": 48})
            out.append(s2)

    elif hero == "sensitivity":
        seg = ["Cautious", "Balanced", "Assertive"]
        out.append(rrect(CX, y, CW, 40, 13, "#0c1424", C["line"], 1))
        sw = (CW - 8) / 3
        for i, lbl in enumerate(seg):
            on = (i == 1)
            if on:
                out.append(rrect(CX + 4 + i * sw, y + 4, sw, 32, 10, "url(#gBrand)"))
            out.append(text(CX + 4 + i * sw + sw / 2, y + 25, lbl, 12, "#fff" if on else C["t2"], 650, "middle"))
        y += 52
        s, y = card_block(y, {"icon": "heart", "color": "red", "k": "Heart-rate trigger",
                              "s": "+40 bpm over your baseline", "extra": ("meter", 0.5, "mV")})
        out.append(s)
        s, y = card_block(y, {"k": "Quiet hours", "s": "No unprompted check-ins", "metric": "22–07"})
        out.append(s)
        s, y = card_block(y, {"icon": "chart", "color": "green", "k": "Learning your baseline",
                              "s": "resting 60 · 40 calm samples", "pill": ("SET", "good")})
        out.append(s)

    elif hero == "feedback":
        out.append(rrect(CX, y, CW, 58, 16, "url(#gCard)", C["line"], 1))
        out.append(text(CX + 14, y + 25, "“Try a 2-minute breathing pause.”", 11.5, C["txt"], 500))
        out.append(text(CX + 14, y + 43, "Was that guidance helpful?", 11, C["t2"]))
        y += 72
        bw = (CW - 12) / 2
        out.append(rrect(CX, y, bw, 74, 16, A(C["green"], 0.12), C["green"], 1.5))
        out.append(icon("heart", CX + bw / 2, y + 30, C["green"], 1.3))
        out.append(text(CX + bw / 2, y + 60, "Helpful", 12, C["green"], 700, "middle"))
        out.append(rrect(CX + bw + 12, y, bw, 74, 16, A(C["red"], 0.12), C["red"], 1.5))
        out.append(icon("warn", CX + bw + 12 + bw / 2, y + 30, C["red"], 1.3))
        out.append(text(CX + bw + 12 + bw / 2, y + 60, "Not for me", 12, C["red"], 700, "middle"))
        y += 88
        s, y = card_block(y, {"icon": "chart", "color": "brand", "k": "Continuous improvement",
                              "s": "one tap trains the guidance"})
        out.append(s)

    elif hero == "tone":
        seg = ["Warm", "Direct", "Playful"]
        out.append(rrect(CX, y, CW, 40, 13, "#0c1424", C["line"], 1))
        sw = (CW - 8) / 3
        for i, lbl in enumerate(seg):
            on = (i == 0)
            if on:
                out.append(rrect(CX + 4 + i * sw, y + 4, sw, 32, 10, "url(#gBrand)"))
            out.append(text(CX + 4 + i * sw + sw / 2, y + 25, lbl, 12, "#fff" if on else C["t2"], 650, "middle"))
        y += 52
        out.append(rrect(CX, y, CW, 60, 16, "url(#gCard)", C["line"], 1))
        out.append(text(CX + 14, y + 24, "Your note to the coach", 12, C["txt"], 600))
        out.append(text(CX + 14, y + 42, "“Keep it short. No sugar-coating.”", 11, C["t2"]))
        y += 72
        s, y = card_block(y, {"icon": "chat", "color": "violet", "k": "Shapes every reply",
                              "s": "guidance & coach prompts adapt"})
        out.append(s)

    elif hero == "timeline":
        events = [("bolt", "cyan", "Biometric sample", "HR 110 · resp 22 · 10:02"),
                  ("warn", "amber", "Detection", "anxiety · guidance"),
                  ("shield", "green", "Guidance delivered", "breathing + reassurance"),
                  ("phone", "red", "Escalation", "contact notified · live help")]
        lx = CX + 16
        out.append(f'<line x1="{lx}" y1="{y+8}" x2="{lx}" y2="{y+8+len(events)*62-40}" stroke="{C["line"]}" stroke-width="2"/>')
        for ic, col, k, s in events:
            c = ACCENT[col]
            out.append(f'<circle cx="{lx}" cy="{y+12}" r="9" fill="{C["scrB"]}" stroke="{c}" stroke-width="2"/>')
            out.append(icon(ic, lx, y + 12, c, 0.5))
            out.append(rrect(lx + 22, y - 6, CW - 38, 44, 12, "url(#gCard)", C["line"], 1))
            out.append(text(lx + 36, y + 12, k, 12, C["txt"], 650))
            out.append(text(lx + 36, y + 27, s, 10, C["t2"]))
            y += 62

    elif hero == "baselinep":
        cx0, cy0, r = W / 2, y + 52, 46
        out.append(ring(cx0, cy0, r, 1.0, C["green"], 9))
        out.append(text(cx0, cy0 + 2, "60", 30, "#fff", 800, "middle"))
        out.append(text(cx0, cy0 + 22, "RESTING HR", 8.5, C["t2"], 600, "middle", 0.6))
        y = cy0 + r + 26
        for ic, col, k, s, pillt in [("heart", "red", "Heart rate", "learned · 40 samples", ("SET", "good")),
                                     ("lung", "cyan", "Respiration", "learning · 3 samples", ("12%", "info")),
                                     ("drop", "violet", "SpO₂", "provisional", ("SEED", "info"))]:
            s2, y = card_block(y, {"icon": ic, "color": col, "k": k, "s": s, "pill": pillt, "h": 48})
            out.append(s2)

    elif hero == "signin":
        out.append(orb(W / 2, y + 44, 36))
        out.append(icon("shield", W / 2, y + 42, "rgba(255,255,255,0.92)", 1.4))
        y += 106
        out.append(text(W / 2, y, "Welcome back", 16, "#fff", 750, "middle"))
        out.append(text(W / 2, y + 20, "Your Guardian is ready", 11, C["t2"], 400, "middle"))
        y += 44
        out.append(rrect(CX, y, CW, 56, 15, "url(#gCard)", C["line"], 1))
        out.append(icon("eye", CX + 30, y + 28, C["brandA"], 1.2))
        out.append(text(CX + 58, y + 24, "Unlock with Face ID", 12.5, C["txt"], 650))
        out.append(text(CX + 58, y + 40, "your data stays on device", 10, C["t2"]))
        y += 72
        out.append(button(CX, y, CW, "Sign In", "brand", 44))
        out.append(button(CX, y + 54, CW, "Emergency access", "ghost", 42))

    elif hero == "endsession":
        out.append(orb(W / 2, y + 40, 32))
        out.append(icon("shield", W / 2, y + 40, "rgba(255,255,255,0.95)", 1.3))
        y += 92
        out.append(text(W / 2, y, "Session ended", 16, "#fff", 750, "middle"))
        out.append(text(W / 2, y + 20, "Guardian keeps watching in the background", 10, C["t2"], 400, "middle"))
        y += 42
        for ic, col, k, s in [("heart", "green", "Resting HR 60 bpm", "calm the whole session"),
                              ("leaf", "green", "Mood logged", "4 / 5 today"),
                              ("shield", "brand", "Still watching", "monitoring never sleeps")]:
            s2, y = card_block(y, {"icon": ic, "color": col, "k": k, "s": s, "h": 48})
            out.append(s2)
        out.append(button(CX, y + 2, CW, "Sign Out", "brand", 42))

    elif hero == "auth":
        out.append(orb(W / 2, y + 36, 30))
        out.append(icon("shield", W / 2, y + 34, "rgba(255,255,255,0.92)", 1.4))
        y += 82
        out.append(text(W / 2, y, "Sign in to Jim Mini", 17, "#fff", 750, "middle", -0.3))
        out.append(text(W / 2, y + 20, "One login for your Guardian", 11, C["t2"], 400, "middle"))
        y += 42
        out.append(rrect(CX, y, CW, 46, 13, "#ffffff"))
        out.append(apple_mark(CX + 30, y + 12))
        out.append(text(W / 2 + 10, y + 28, "Continue with Apple", 13, "#0b0b0f", 650, "middle"))
        y += 54
        out.append(rrect(CX, y, CW, 46, 13, "#ffffff"))
        out.append(google_mark(CX + 31, y + 15))
        out.append(text(W / 2 + 10, y + 28, "Continue with Google", 13, "#1f1f1f", 650, "middle"))
        y += 54
        out.append(rrect(CX, y, CW, 46, 13, "rgba(255,255,255,0.06)", C["line"], 1))
        out.append(envelope(CX + 41, y + 23, C["brandA"]))
        out.append(text(W / 2 + 10, y + 28, "Continue with Email", 13, C["txt"], 650, "middle"))
        y += 62
        out.append(text(W / 2, y, "Your vault unlocks with Face ID after sign-in.", 9.5, C["t3"], 500, "middle"))
        out.append(text(W / 2, y + 16, "By continuing you agree to the Terms & Privacy Policy.", 9, C["t3"], 500, "middle"))

    elif hero == "consent":
        out.append(text(CX, y, "Jim only uses what you allow — change it anytime.", 10.5, C["t2"]))
        y += 26
        rows = [("bell", "brand", "Notifications", "check-ins & alerts", "on"),
                ("heart", "red", "Health & Motion", "sensitize known conditions", "on"),
                ("cross", "green", "Emergency access", "reach help when it matters", "on"),
                ("eye", "cyan", "Location", "guidance where you are", "off")]
        for ic, col, k, s, st in rows:
            out.append(rrect(CX, y, CW, 58, 15, "url(#gCard)", C["line"], 1))
            out.append(chip(CX + 12, y + 12, ic, ACCENT[col]))
            out.append(text(CX + 58, y + 25, k, 12.5, C["txt"], 650))
            out.append(text(CX + 58, y + 41, s, 10.5, C["t2"]))
            on = st == "on"
            tx = CX + CW - 48
            out.append(rrect(tx, y + 19, 40, 22, 11, C["green"] if on else C["tab"], None if on else C["line"], 1))
            out.append(f'<circle cx="{tx + (28 if on else 12)}" cy="{y+30}" r="8.5" fill="#fff"/>')
            y += 66
        out.append(button(CX, y + 2, CW, "Continue", "brand", 44))

    elif hero == "aboutyou":
        out.append(text(CX, y, "The more Jim understands, the better it guides.", 10.5, C["t2"]))
        y += 24
        out.append(rrect(CX, y, CW, 54, 14, "url(#gCard)", C["line"], 1))
        out.append(f'<circle cx="{CX+28}" cy="{y+27}" r="16" fill="{A(C["brandA"],0.20)}" stroke="{C["brandA"]}" stroke-width="1.2"/>')
        out.append(text(CX + 28, y + 32, "M", 15, C["brandA"], 800, "middle"))
        out.append(text(CX + 54, y + 24, "Maria Bianchi", 13, C["txt"], 650))
        out.append(text(CX + 54, y + 40, "42 · San Francisco", 10.5, C["t2"]))
        y += 66

        def tags(label, items, col):
            nonlocal y
            out.append(text(CX, y, label, 9.5, C["t3"], 700, "start", 0.6))
            y += 18
            tx = CX
            for ic, lab in items:
                w = 30 + len(lab) * 6.4
                if tx + w > CX + CW:
                    tx = CX
                    y += 34
                out.append(rrect(tx, y, w, 27, 13, A(col, 0.12), col, 1))
                out.append(icon(ic, tx + 15, y + 13.5, col, 0.58))
                out.append(text(tx + 26, y + 17, lab, 10.5, C["txt"], 600))
                tx += w + 8
            y += 40
        tags("KNOWN CONDITIONS", [("heart", "Hypertension"), ("drop", "Type 2 diabetes"),
                                  ("brain", "Anxiety")], C["red"])
        tags("WHAT MATTERS MOST", [("heart", "Family"), ("leaf", "Calm"),
                                   ("target", "Fitness"), ("book", "Learning")], C["teal"])
        out.append(button(CX, y + 2, CW, "Continue", "brand", 44))

    elif hero == "contacts":
        out.append(text(CX, y, "Who Jim can reach — and who it will alert.", 10.5, C["t2"]))
        y += 24
        people = [("A", "Alex Bianchi", "Spouse · lives with you", "Primary", "good", "green"),
                  ("C", "Dr. Chen", "Cardiologist", "On call", "info", "cyan")]
        for initial, name, rel, tag, tone, col in people:
            out.append(rrect(CX, y, CW, 60, 15, "url(#gCard)", C["line"], 1))
            out.append(f'<circle cx="{CX+30}" cy="{y+30}" r="17" fill="{A(C[col],0.20)}" stroke="{C[col]}" stroke-width="1.2"/>')
            out.append(text(CX + 30, y + 35, initial, 15, C[col], 800, "middle"))
            out.append(text(CX + 58, y + 26, name, 12.5, C["txt"], 650))
            out.append(text(CX + 58, y + 42, rel, 10.5, C["t2"]))
            out.append(pill(CX + CW - 14, y + 26, tag, tone))
            y += 70
        out.append(f'<rect x="{CX}" y="{y}" width="{CW}" height="46" rx="14" fill="none" stroke="{C["line"]}" stroke-width="1.4" stroke-dasharray="5 4"/>')
        out.append(icon("plus", CX + 32, y + 23, C["brandA"], 0.8))
        out.append(text(CX + 52, y + 28, "Add emergency contact", 12, C["brandA"], 650))
        y += 60
        out.append(button(CX, y, CW, "Continue", "brand", 44))

    elif hero == "ready":
        out.append(orb(W / 2, y + 40, 34))
        out.append(f'<path d="M{W/2-11} {y+40} l7 8 14 -16" fill="none" stroke="#fff" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/>')
        y += 100
        out.append(text(W / 2, y, "You're protected", 18, "#fff", 750, "middle", -0.3))
        out.append(text(W / 2, y + 21, "Jim is watching over you now.", 11, C["t2"], 400, "middle"))
        y += 44
        for ic, col, k, s in [("person", "brand", "Profile ready", "Jim knows what matters to you"),
                              ("heart", "red", "Conditions sensitized", "earlier, gentler detection"),
                              ("cross", "green", "Contacts added", "2 people Jim can reach"),
                              ("shield", "cyan", "Guardian on", "monitoring never sleeps")]:
            s2, y = card_block(y, {"icon": ic, "color": col, "k": k, "s": s, "h": 48})
            out.append(s2)
        out.append(button(CX, y + 2, CW, "Enter Jim Mini", "brand", 44))

    else:  # generic stacked cards
        for c in spec["cards"]:
            s, y = card_block(y, c)
            out.append(s)
        if spec.get("button"):
            out.append(button(CX, y, CW, spec["button"][0], spec["button"][1], 42))

    out += tabbar(spec.get("tab", 0))
    out += navbar()
    out += close()
    return "".join(out)


SCREENS = [
    dict(num=1, title="Welcome", sub="Onboarding & consent", hero="welcome", accent="brand"),
    dict(num=2, title="Home", sub="Tuesday, May 14", tab=0, cards=[
        dict(icon="leaf", color="green", k="Mood: Calm", s="last check-in 2h ago", pill=("GOOD", "good")),
        dict(icon="heart", color="red", k="Heart rate", s="updated 2m ago", metric="72"),
        dict(icon="chat", color="brand", k="Talk to Jim", s="voice or text, anytime"),
        dict(icon="bell", color="amber", k="Today", s="Team meeting · Gym · Call Mom"),
    ]),
    dict(num=3, title="Chat", sub="Jim Mini · Online", hero="chat", tab=1),
    dict(num=4, title="Voice", sub="Hands-free conversation", hero="voice", tab=2),
    dict(num=5, title="Daily Briefing", sub="May 14", tab=0, cards=[
        dict(icon="leaf", color="cyan", k="Weather", s="San Francisco · Sunny", metric="72°"),
        dict(icon="bell", color="violet", k="Your schedule", s="Meeting 10:30 · Gym 6:00"),
        dict(icon="moon", color="brand", k="Sleep", s="7h 45m · good", pill=("RESTED", "good")),
        dict(icon="bolt", color="amber", k="Top suggestion", s="Busy day — take breaks, hydrate"),
    ]),
    dict(num=6, title="Health", sub="Today", tab=0, accent="red", cards=[
        dict(icon="heart", color="red", k="Heart rate", s="72 bpm", extra=("spark", [70, 74, 71, 78, 73, 76, 72], "red")),
        dict(icon="moon", color="violet", k="Sleep", s="7h 45m", metric="●●●"),
        dict(icon="steps", color="green", k="Steps", s="today", metric="8,342"),
        dict(icon="lung", color="cyan", k="Blood oxygen", s="SpO₂", metric="98%"),
    ]),
    dict(num=7, title="Memories", sub="What matters to you", tab=3, cards=[
        dict(icon="leaf", color="green", k="You started keto", s="Apr 20", pill=("HEALTH", "good")),
        dict(icon="bolt", color="red", k="Bought a Tesla", s="Mar 15"),
        dict(icon="heart", color="pink", k="Daughter's birthday", s="September 4"),
        dict(icon="bell", color="cyan", k="Prefers meetings after 10 AM", s="Jan 25"),
    ]),
    dict(num=8, title="Profile", sub="Your AI profile", tab=4, cards=[
        dict(icon="person", color="brand", k="David Bianchi", s="Analytical, curious, driven", pill=("87%", "brand")),
        dict(icon="chat", color="cyan", k="Communication style", s="Direct, clear, encouraging"),
        dict(icon="target", color="green", k="6 active goals", s="across 5 life areas"),
        dict(icon="heart", color="pink", k="Family", s="Wife · 1 daughter"),
    ]),
    dict(num=9, title="Goals", sub="Active & completed", tab=4, cards=[
        dict(icon="target", color="green", k="Fitness", s="Work out 4×/week", extra=("meter", 0.75, "mG")),
        dict(icon="bolt", color="brand", k="Career", s="Launch new app", extra=("meter", 0.6, "mV")),
        dict(icon="leaf", color="cyan", k="Mental wellness", s="Meditate daily", extra=("meter", 0.4, "mV")),
        dict(icon="chart", color="amber", k="Finance", s="Save $10,000", extra=("meter", 0.55, "mO")),
    ]),
    dict(num=10, title="Finance", sub="Overview", tab=0, accent="amber", cards=[
        dict(icon="chart", color="green", k="Net worth", s="+5.3% this month", metric="$128k"),
        dict(icon="bolt", color="amber", k="Spending", s="−8.7% vs last month", metric="$3,240"),
        dict(icon="warn", color="amber", k="Spending accelerating", s="last 3 buys 2.1× prior", pill=("HEADS-UP", "warn")),
        dict(icon="bell", color="cyan", k="Upcoming bills", s="Electricity $120 · Internet $60"),
    ]),
    dict(num=11, title="Emergency", sub="One tap to help", hero="sos", accent="red", tab=0),
    dict(num=12, title="Settings", sub="Privacy & preferences", tab=4, cards=[
        dict(icon="shield", color="brand", k="Permissions", s="Connected sources"),
        dict(icon="eye", color="cyan", k="Memory & data", s="Access log · export · delete"),
        dict(icon="mic", color="violet", k="Voice & audio", s="Wake word, pacing cues"),
        dict(icon="bell", color="amber", k="Notifications", s="Smart, prioritized"),
    ]),
    # --- Guardian / health ---
    dict(num=13, title="Live Monitoring", sub="Detect → guide → escalate", tab=0, accent="cyan", cards=[
        dict(icon="heart", color="red", k="Heart rate", s="+38 over baseline", extra=("spark", [60, 64, 70, 82, 96, 104, 110], "red")),
        dict(icon="lung", color="cyan", k="Respiration", s="22 / min", pill=("ELEVATED", "warn")),
        dict(icon="shield", color="green", k="Guardian", s="watching · rules are transparent", pill=("ON", "good")),
        dict(icon="watch", color="violet", k="Source", s="smart watch · real-time"),
    ]),
    dict(num=14, title="CPR Coach", sub="Cardiac arrest · keep going", hero="cpr", accent="red", tab=0),
    dict(num=15, title="Emergency", sub="Coordinated response", hero="emergency", accent="red", tab=0),
    dict(num=16, title="Medical ID", sub="Scannable on a locked phone", hero="medid", accent="red", tab=4),
    dict(num=17, title="Foresight", sub="Caught before it happens", tab=0, accent="cyan", cards=[
        dict(icon="lung", color="cyan", k="Blood oxygen slipping", s="97 → 95 → 93%", extra=("spark", [97, 95, 93], "cyan")),
        dict(icon="moon", color="violet", k="Sleep debt building", s="6.0 · 5.5 · 5.0 h", extra=("meter", 0.72, "mO")),
        dict(icon="leaf", color="amber", k="Mood sliding", s="5 → 4 → 3 over 3 check-ins", pill=("HEADS-UP", "warn")),
    ]),
    dict(num=18, title="Guardian Sensitivity", sub="How readily Jim steps in", hero="sensitivity", tab=4),
    dict(num=19, title="Known Conditions", sub="Sensitized detection", tab=4, cards=[
        dict(icon="brain", color="violet", k="Acute anxiety / panic", s="HR threshold lowered", pill=("DECLARED", "brand")),
        dict(icon="heart", color="red", k="Hypertension", s="BP watched closely"),
        dict(icon="plus", color="green", k="Declare a condition", s="detection adapts to you"),
    ]),
    dict(num=20, title="Providers", sub="When AI reaches its limit", tab=0, accent="teal", cards=[
        dict(icon="cross", color="red", k="Bay Area Cardiology", s="medical · 0.8 mi", pill=("OPEN", "good")),
        dict(icon="brain", color="violet", k="Dr. Rivera, LCSW", s="mental health · telehealth"),
        dict(icon="link", color="cyan", k="Consented handoff", s="session summary, revocable"),
    ]),
    # --- life layer ---
    dict(num=21, title="Habits", sub="Streaks & milestones", tab=3, cards=[
        dict(icon="flame", color="amber", k="Meditate", s="12-day streak", pill=("🔥 12", "warn")),
        dict(icon="steps", color="green", k="Morning walk", s="30-day milestone", pill=("30", "good")),
        dict(icon="drop", color="cyan", k="Hydrate", s="7-day streak", extra=("meter", 0.7, "mG")),
    ]),
    dict(num=22, title="Check-in", sub="Mood & energy", tab=0, accent="pink", cards=[
        dict(icon="leaf", color="green", k="How's your mood?", s="1 low · 5 great", metric="4"),
        dict(icon="bolt", color="amber", k="Energy", s="steady today", metric="3"),
        dict(icon="chat", color="brand", k="Add a note", s="a worrying note runs the crisis check"),
    ], button=("Save check-in", "brand")),
    dict(num=23, title="Journal", sub="Private, vaulted", tab=3, cards=[
        dict(icon="book", color="violet", k="A quiet day", s="today · sealed in your vault"),
        dict(icon="book", color="cyan", k="Interview nerves", s="yesterday"),
        dict(icon="shield", color="green", k="Runs the crisis pipeline", s="crisis language still escalates"),
    ], button=("New entry", "brand")),
    dict(num=24, title="Life Coach", sub="24/7 across your life", tab=1, cards=[
        dict(icon="brain", color="violet", k="Mental health", s="grounded in recent check-ins"),
        dict(icon="chart", color="green", k="Health & fitness", s="tied to your goals"),
        dict(icon="bolt", color="brand", k="Career", s="interview prep ready"),
        dict(icon="heart", color="pink", k="Relationships", s="communication tips"),
    ]),
    dict(num=25, title="Insights", sub="Proactive nudges", tab=0, cards=[
        dict(icon="warn", color="amber", k="High spending alert", s="above your usual", pill=("ALERT", "warn")),
        dict(icon="moon", color="green", k="You slept better", s="7.5h · keep it up", pill=("PRAISE", "good")),
        dict(icon="bolt", color="brand", k="Interview prep", s="want a practice round?"),
        dict(icon="leaf", color="cyan", k="Mindful break?", s="a 2-minute pause can help"),
    ]),
    dict(num=26, title="Companion", sub="An ambient hello", tab=0, accent="violet", cards=[
        dict(icon="leaf", color="green", k="Grounded in your day", s="latest mood, goals, personality"),
        dict(icon="chat", color="brand", k="“How did the meeting go?”", s="reaches out first — never on a schedule"),
    ], button=("Say hi back", "brand")),
    dict(num=27, title="Ambient Jump-in", sub="Before you ask", tab=0, accent="brand", cards=[
        dict(icon="warn", color="amber", k="You've retried this a few times", s="fixing the car · 50 min"),
        dict(icon="chat", color="brand", k="“Want a hand?”", s="frustration signals detected"),
    ], button=("Yes, help me", "brand")),
    # --- data / system ---
    dict(num=28, title="Connected Sources", sub="AI only sees what you allow", tab=4, cards=[
        dict(icon="watch", color="cyan", k="Wearable", s="heart rate, sleep", pill=("ON", "good")),
        dict(icon="chart", color="amber", k="Spending", s="transactions", pill=("ON", "good")),
        dict(icon="bell", color="violet", k="Calendar", s="events", pill=("OFF", "crit")),
        dict(icon="person", color="brand", k="Messages", s="not connected", pill=("OFF", "crit")),
    ]),
    dict(num=29, title="Privacy & Data", sub="No raw data leaves your vault", tab=4, accent="green", cards=[
        dict(icon="eye", color="cyan", k="Who accessed my data", s="stored · read · erased", pill=("CHAIN OK", "good")),
        dict(icon="cloud", color="violet", k="Contribute to the model", s="preview before it leaves", pill=("OFF", "crit")),
        dict(icon="shield", color="green", k="Export my data", s="everything, anytime"),
        dict(icon="warn", color="red", k="Delete my data", s="erased locally & in the vault"),
    ]),
    dict(num=30, title="Devices", sub="Where Jim lives", tab=4, cards=[
        dict(icon="watch", color="cyan", k="Apple Watch", s="wearable · Bluetooth", pill=("ACTIVE", "good")),
        dict(icon="mic", color="violet", k="Kitchen console", s="stationary · on-device LLM"),
        dict(icon="bolt", color="brand", k="Helper bot", s="autonomous · relayed"),
        dict(icon="plus", color="green", k="Add a device", s="wearable, stationary, robot"),
    ]),
    dict(num=31, title="Continue", sub="Pick up where you left off", tab=0, accent="teal", cards=[
        dict(icon="link", color="teal", k="Conversation with a specialist", s="started on your phone"),
        dict(icon="chat", color="brand", k="“…let's keep going.”", s="same thread, same memory"),
        dict(icon="watch", color="cyan", k="Now on: Kitchen console", s="cross-product continuity"),
    ], button=("Resume here", "brand")),
    dict(num=32, title="Notifications", sub="Smart & prioritized", tab=0, cards=[
        dict(icon="heart", color="red", k="High heart rate", s="elevated for 10 min · 9m ago", pill=("NOW", "crit")),
        dict(icon="bell", color="violet", k="Upcoming event", s="Team meeting in 21 min"),
        dict(icon="bolt", color="brand", k="Jim suggestion", s="Take a 5-min break · 15m ago"),
    ]),
    dict(num=33, title="Progress Report", sub="Your month at a glance", tab=4, accent="green", cards=[
        dict(icon="leaf", color="green", k="Avg mood", s="up from last month", metric="4.1"),
        dict(icon="target", color="brand", k="Goals on track", s="of 6", metric="4"),
        dict(icon="flame", color="amber", k="Longest streak", s="meditation", metric="30d"),
        dict(icon="shield", color="cyan", k="Escalations", s="all resolved", metric="2"),
    ]),
    dict(num=34, title="Model & Cloud", sub="Greater model, opt-in", tab=4, accent="violet", cards=[
        dict(icon="cloud", color="violet", k="Cloud model", s="claude-fable-5 · local fallback", pill=("ON", "good")),
        dict(icon="shield", color="green", k="Offline mode", s="fully on-host, nothing leaves", pill=("READY", "good")),
        dict(icon="eye", color="cyan", k="Contribution preview", s="exactly what would be shared"),
    ]),
    # --- newly filled gaps ---
    dict(num=35, title="Rate Guidance", sub="Continuous improvement", hero="feedback", accent="green", tab=0),
    dict(num=36, title="Counselor Style", sub="Adapt the coach to you", hero="tone", accent="violet", tab=4),
    dict(num=37, title="History", sub="Detect → guide → escalate", hero="timeline", accent="cyan", tab=3),
    dict(num=38, title="Baseline", sub="Learning your normal", hero="baselinep", accent="green", tab=0),
    dict(num=39, title="Tandem Specialist", sub="Delegated guidance", tab=0, accent="teal", cards=[
        dict(icon="brain", color="violet", k="QRME anxiety specialist", s="a synthetic profile, over HTTP", pill=("TANDEM", "brand")),
        dict(icon="shield", color="green", k="Runs QRME's moderation", s="reply checked before it's shown"),
        dict(icon="link", color="teal", k="Falls back to local", s="standalone guidance if offline"),
        dict(icon="person", color="cyan", k="Age- & status-checked", s="never a minor to an adult profile"),
    ]),
    # ---- session lifecycle (sign-in → … → sign-out) ----
    dict(num=40, title="Sign In", sub="Welcome back", hero="signin", accent="brand", tab=0),
    dict(num=41, title="End Session", sub="Guardian keeps watching", hero="endsession", accent="green", tab=0),
    dict(num=42, title="Log In", sub="Apple, Google or email", hero="auth", accent="brand", tab=0),
    dict(num=43, title="Permissions", sub="What Jim can access", hero="consent", accent="brand", tab=0),
    dict(num=44, title="About You", sub="Help Jim understand you", hero="aboutyou", accent="cyan", tab=0),
    dict(num=45, title="Emergency Contacts", sub="Who Jim reaches in a crisis", hero="contacts", accent="red", tab=0),
    dict(num=46, title="All Set", sub="You're protected", hero="ready", accent="green", tab=0),
]


def main():
    global PLATFORM
    total = 0
    for plat, sub in (("ios", ""), ("android", "android")):
        PLATFORM = plat
        outdir = OUT if not sub else os.path.join(OUT, sub)
        os.makedirs(outdir, exist_ok=True)
        for s in SCREENS:
            slug = s["title"].lower().replace(" & ", "-").replace(" ", "-")
            fn = f'{s["num"]:02d}-{slug}.svg'
            with open(os.path.join(outdir, fn), "w") as f:
                f.write(render(s))
            total += 1
    PLATFORM = "ios"
    print(f"generated {total} screens ({total // 2} × 2 platforms)")
    return []


if __name__ == "__main__":
    main()
