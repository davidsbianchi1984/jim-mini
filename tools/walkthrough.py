"""Drive every road of the guardian, and photograph it driven.

The sibling's 3.0.0 gate, applied here: pick any road — the vitals,
the check-in, the journal, the coach, the lookout, the emergency
tools, the circle, the memory — and drive it to the end without
finding a wall. Same booted backend and built console the camera
uses; every verdict line carries the status that actually came back,
and where a body's fields are refused, the product's own validation
sentence is the report.
"""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO))

import shoot_screens as camera

OUT = REPO / "docs" / "walkthrough"


def call(method, path, body=None, token=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(camera.BASE + path, data=data,
                                 method=method)
    req.add_header("content-type", "application/json")
    if token:
        req.add_header("authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode() or "{}")
        except Exception:
            return e.code, {}
    except Exception as e:
        return 0, {"error": str(e)}


rows: list[tuple[str, str, bool]] = []


def step(road, note, ok, detail=None):
    rows.append((road, note, ok))
    line = ("  ok  " if ok else "  WALL") + f"  {road}: {note}"
    if detail and not ok:
        line += f"  << {json.dumps(detail)[:220]}"
    print(line)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    camera.build_console()
    proc = camera.start_backend()
    session = camera.enrol()
    uid, tok = session["userId"], session["userToken"]
    try:
        # 1 · Vitals: the drip channel, a reading, the baseline.
        s, ch = call("GET", f"/watch/channel/{uid}", token=tok)
        step("vitals", f"the drip channel mints ({s})", s == 200, ch)
        from urllib.parse import urlparse
        raw = (ch or {}).get("drip_url") or (ch or {}).get("url") or ""
        drip = urlparse(raw).path if raw else ""
        if drip:
            s, r = call("POST", drip,
                        {"heart_rate": 62, "blood_oxygen": 98})
            step("vitals", f"a reading lands ({s})", s in (200, 201), r)
        s, b = call("GET", f"/baseline/{uid}", token=tok)
        step("vitals", f"the baseline answers ({s})", s == 200, b)

        # 2 · Check-in
        s, r = call("POST", f"/checkin/{uid}",
                    {"mood": 4, "energy": 3,
                     "note": "Walked the whole map today."}, tok)
        step("check-in", f"logged ({s})", s in (200, 201), r)

        # 3 · Journal
        s, r = call("POST", f"/journal/{uid}",
                    {"text": "The walkthrough wrote this."}, tok)
        if s == 422:
            s, r = call("POST", f"/journal/{uid}",
                        {"entry": "The walkthrough wrote this."}, tok)
        step("journal", f"an entry lands ({s})", s in (200, 201), r)

        # 4 · Coach — offline, and it still answers.
        s, r = call("POST", f"/coach/{uid}",
                    {"area": "health_fitness",
                     "message": "I slept badly. What should I watch?"},
                    tok)
        said = bool((r or {}).get("reply") or (r or {}).get("answer")
                    or (r or {}).get("message"))
        step("coach", f"a grounded answer with the network cut ({s})",
             s in (200, 201) and said, r if s not in (200, 201) else None)

        # 5 · Lookout — offline: the honest failure is the feature.
        s, r = call("POST", f"/lookout/{uid}",
                    {"url": "https://example.org/page"}, tok)
        step("lookout", f"a page is watched, or refused by name ({s})",
             s in (200, 201, 422), r)

        # 6 · Emergency tools: the Medical ID mints and reads back.
        s, r = call("POST", f"/medical-id/qr/{uid}", token=tok)
        minted = s in (200, 201)
        step("emergency", f"the Medical ID mints ({s})", minted, r)
        if minted and (r or {}).get("token"):
            s, m = call("GET", f"/medical-id/{r['token']}")
            step("emergency", f"a finder can read it ({s})", s == 200, m)

        # 7 · The circle — by mutual invitation, so a second person
        # enrols through the same front door and is invited by id.
        import urllib.request as _u
        body2 = json.dumps({"display_name": "Rosa", "birthdate":
                            "1986-01-01", "terms_consent": True,
                            "resting_heart_rate": 62,
                            "plan": "pro"}).encode()
        req2 = _u.Request(camera.BASE + "/enroll", data=body2,
                          headers={"content-type": "application/json"})
        with _u.urlopen(req2, timeout=20) as ans:
            rosa = json.load(ans)
        s, r = call("POST", f"/circle/{uid}/contacts",
                    {"other_id": rosa["id"]}, tok)
        step("circle", f"an invitation goes out ({s})",
             s in (200, 201), r)

        # 8 · The memory shelf
        s, r = call("GET", f"/memory/{uid}", token=tok)
        step("memory", f"the shelf answers ({s})", s == 200, r)

        # 9 · Matters
        s, r = call("GET", "/v1/problems", token=tok)
        step("matters", f"the problems record answers ({s})", s == 200, r)

        # 10 · Devices and monitors
        s, r = call("GET", f"/devices/{uid}", token=tok)
        step("devices", f"the device page answers ({s})", s == 200, r)

        # The photographs: driven states, phone scale.
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(
                executable_path="/opt/pw-browsers/chromium")
            page = browser.new_page(viewport=camera.VIEWPORT,
                                    device_scale_factor=2)
            page.goto(camera.BASE + "/", wait_until="networkidle")
            page.evaluate("s => localStorage.setItem('jim.session', s)",
                          json.dumps(session))
            page.reload(wait_until="networkidle")
            for tab, name in (("home", "01-home"),
                              ("monitor", "02-monitor"),
                              ("checkin", "03-checkin"),
                              ("coach", "04-coach"),
                              ("careteam", "05-careteam"),
                              ("channel", "06-channel")):
                try:
                    if camera.open_tab(page, tab):
                        camera.answer_the_notice(page)
                        time.sleep(1.2)
                        page.screenshot(path=str(OUT / f"{name}.png"))
                        step("photo", f"{name} photographed", True)
                    else:
                        step("photo", f"{tab} tab did not open", False)
                except Exception as e:
                    step("photo", f"{tab}: {e}", False)
            browser.close()
    finally:
        proc.terminate()

    walls = [r for r in rows if not r[2]]
    print()
    print(f"{len(rows)} steps, {len(walls)} wall(s)")
    return 1 if walls else 0


if __name__ == "__main__":
    raise SystemExit(main())
