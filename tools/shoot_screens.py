"""Photograph the console — the real one, running, not a drawing of it.

## Why this exists

`docs/screens/` filled up with hand-drawn SVG mockups of every surface, and
the README gallery presented them as what the product looks like. They were
illustrations. The owner's words, in the sibling product, on finding a
faceless mannequin in the gallery:

    "those screens you will never see that you have created. They never
     rendered that way. Only actual snapshots of what the application
     looks like."

He is right, and the failure is worse than cosmetic: a drawing captioned as
a product is a claim about the product. Asked to *grab* screens, the answer
was to draw them — the difference between a photograph and a painting,
presented as if it were the former.

    asked     show the product on the front page
    mattered  show the product, not a picture of what it was meant to be

So this harness does the honest thing. It starts the real backend, serves
the real built console from it, enrols a real account through the real
door, walks the real tabs, and photographs what the browser actually shows.

## What it does NOT do

It does not invent. A surface that will not render — because it needs a
device, a camera, a second person in a room — is left alone rather than
mocked up. An empty state photographed honestly is worth more than a
populated one that never existed.

## The check that makes it evidence

The sibling's version of this navigated by URL hash, which this console
does not use for tabs either: `App.tsx` holds the tab in `useState` and the
only thing that moves it is a press in the sidebar. A harness that
navigates by a mechanism the product does not have fails silently and
writes confident, wrong files — worse than the drawings it replaces,
because a drawing is obviously a drawing and this looks like evidence.

So it presses the real sidebar button and then **checks** that the item the
console marks `active` is the one it asked for. If it is not, nothing is
written. A missing screen is a gap somebody notices; a wrong screen is a
gap nobody notices.

Run it with ``python tools/shoot_screens.py`` from the repository root.
It builds the console first, and that is not a convenience.

The build requirement used to live in this sentence and nowhere else — the
harness served whatever was already in ``app/dist`` and never looked at how
old it was. So a gallery could be re-shot to show a stylesheet fix, and
photograph a bundle from four days earlier, and every capture would look
exactly as convincing as one that showed the fix. It happened: a round that
replaced drawings with photographs *because a drawing is obviously a drawing
and this looks like evidence* shot its evidence against a stale build.

    asked     is the console built
    mattered  is the console built from what is on disk now

A prose requirement is a requirement somebody skips. This one is a step.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PORT = int(os.environ.get("SHOT_PORT", "8098"))
BASE = f"http://localhost:{PORT}"
CONSOLE = f"{BASE}/app/"
OUT = REPO / "docs" / "screens"

#: A viewport that shows the console the way its own people meet it: a
#: phone, because that is what somebody carrying a Guardian is holding.
#: Doubled so the capture is legible when GitHub scales it into a gallery.
VIEWPORT = {"width": 430, "height": 932}
SCALE = 2


def build_console() -> None:
    """`npm run build`, every run, before anything is photographed.

    Not conditional on a timestamp comparison: a source file can be older
    than the bundle and still not be in it — a dependency bump, an aborted
    build, a file restored from git. The build is a few seconds and the
    thing it protects is whether these pictures mean anything.
    """
    app = REPO / "app"
    print("building the console…", flush=True)
    done = subprocess.run(["npm", "run", "build"], cwd=app,
                          capture_output=True, text=True)
    if done.returncode != 0:
        raise SystemExit(
            "the console did not build, so there is nothing honest to "
            f"photograph:\n{done.stdout[-2000:]}\n{done.stderr[-2000:]}")


def start_backend() -> subprocess.Popen:
    env = dict(os.environ)
    env["JIM_DB"] = "/tmp/jim-shots.db"
    env["JIM_OFFLINE"] = "1"
    Path("/tmp/jim-shots.db").unlink(missing_ok=True)
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "jim.api:create_app",
         "--factory", "--port", str(PORT)],
        cwd=REPO, env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(80):
        try:
            with urllib.request.urlopen(BASE + "/health", timeout=2):
                return proc
        except Exception:
            time.sleep(0.5)
    proc.terminate()
    raise SystemExit("the backend never came up")


def enrol() -> dict:
    """One account, through the product's own front door.

    Not by writing rows: a harness that has to reach around the enrolment
    it is photographing is a harness that will one day photograph a screen
    the real flow cannot reach.
    """
    body = json.dumps({
        "display_name": "David", "birthdate": "1984-01-01",
        "terms_consent": True, "resting_heart_rate": 60, "plan": "pro",
    }).encode()
    request = urllib.request.Request(
        BASE + "/enroll", data=body,
        headers={"content-type": "application/json"})
    with urllib.request.urlopen(request, timeout=20) as answer:
        out = json.load(answer)
    return {"userId": out["id"], "userToken": out["user_token"],
            "displayName": out.get("display_name", "David")}


def open_tab(page, tab: str) -> bool:
    """Reach a tab the way a person does, and refuse to lie about it."""
    page.goto(CONSOLE, wait_until="networkidle")
    page.wait_for_timeout(700)
    page.evaluate("window.scrollTo(0, 0)")
    target = page.query_selector(f'.nav-item[data-tab="{tab}"]')
    if target is None:
        return False
    # `el.click()`, not Playwright's — at phone width the help button floats
    # over the tail of the sidebar, and Playwright refuses a click it can
    # see something else intercepting. That refusal is right for a test of
    # reachability and wrong for a camera: the press this dispatches is the
    # real button's real handler, and the check below still proves the
    # console actually moved.
    target.evaluate("el => el.click()")
    page.wait_for_timeout(1200)
    active = page.query_selector(".nav-item.active")
    return bool(active and active.get_attribute("data-tab") == tab)



def census() -> dict[str, int]:
    """Which screen number each console surface is, per `ui_screens.txt`.

    The captures are filed under the census's numbers so that a photograph
    replaces the drawing that stood for the same surface, rather than
    landing beside it under a number somebody invented.

    The sibling's version of this harness described that intent in a
    comment and then numbered its output 1, 2, 3 in the order the tabs
    happened to be listed — so `home`, which its census calls screen 5, was
    written as `1-home.png`, claiming to be the Welcome screen.

        asked     photograph every surface
        mattered  file each photograph under the surface it is of

    A comment that says what the author meant while the code does something
    else is worse than no comment, because the next reader trusts it. So
    the census is read here rather than described.
    """
    rows: dict[str, int] = {}
    path = REPO / "jim" / "tests" / "ui_screens.txt"
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        parts = line.split()
        if len(parts) >= 2 and parts[1].split(",")[0].isdigit():
            rows[parts[0]] = int(parts[1].split(",")[0])
    return rows


def components() -> dict[str, str]:
    """The component each tab renders, read off `App.tsx` rather than
    written down here — a second list would drift from the first."""
    import re
    source = (REPO / "app" / "src" / "App.tsx").read_text(encoding="utf-8")
    return {tab: name for tab, name in
            re.findall(r'tab === "([a-z]+)" && <([A-Z][A-Za-z]*)', source)}


#: Where a surface has several drawings, which one the photograph stands
#: in for. The census lists *every* drawing of a surface, so its first
#: number is not always the one the tab actually shows — `Coach` is
#: `14,24,82`, and 14 is the CPR pacer, which is a face on the watch and
#: not the coach screen. Filing the photograph of the coach under the CPR
#: drawing would be a wrong claim made silently, so the two cases where
#: the order does not answer the question are answered here, by name.
#:
#: Everything else takes the first number, which is right for it.
STANDS_IN_FOR = {
    "Coach": 24,      # Life Coach, not 14 (CPR) or 82 (Coach, Out Loud)
    "Baseline": 81,   # Your Baseline — the tab; 38 is the learning story
}


def numbered(tabs: list[str]) -> list[tuple[str, str, str]]:
    """(census number, tab, stem) for every tab the census knows.

    A tab whose component the census does not carry is skipped loudly
    rather than given a number nobody agreed on.
    """
    seen, by_tab = census(), components()
    out = []
    for tab in tabs:
        component = by_tab.get(tab)
        number = STANDS_IN_FOR.get(component or "") or seen.get(component or "")
        if number is None:
            print(f"  ? {tab} ({component or 'no component'}): not in the "
                  "census — no number to file it under")
            continue
        out.append((f"{number:03d}", tab, tab))
    return out


def main(shots: list[tuple[str, str, str]]) -> None:
    """``shots`` is (screen number, tab id, filename stem)."""
    from playwright.sync_api import sync_playwright

    build_console()
    proc = start_backend()
    written = 0
    try:
        session = enrol()
        with sync_playwright() as play:
            browser = play.chromium.launch(
                executable_path="/opt/pw-browsers/chromium")
            page = browser.new_page(viewport=VIEWPORT,
                                    device_scale_factor=SCALE)
            page.goto(CONSOLE, wait_until="networkidle")
            page.evaluate("s => localStorage.setItem('jim.session', s)",
                          json.dumps(session))
            # Reload, so the console has actually read that session.
            #
            # The sweeps below look for things only a signed-in console
            # draws — the consent card, the lights widget. Setting
            # localStorage does not re-render the page that is already on
            # screen, so without this the browser is still showing the
            # signed-out onboarding, both sweeps find nothing, and every
            # capture afterwards carries an unanswered consent card and a
            # widget nobody minimised.
            #
            #     asked     is the session set
            #     mattered  is the console showing the session
            page.goto(CONSOLE, wait_until="networkidle")
            page.wait_for_timeout(1500)
            # The problem-reporting consent card opens over everything on a
            # browser that has never answered it — which is every fresh
            # browser, and so every capture taken after it. It is a real
            # screen a real person meets before any byte leaves, so it is
            # photographed on its own and then answered, rather than
            # hidden to get at the ones behind it.
            #
            # Its number comes from the census like every other screen's.
            # It was hard-coded once, and when this harness was carried to
            # a third product the number came with it — filing that
            # product's consent card under a number belonging to another
            # one. `ProblemNotice` is the component that draws it in all
            # three; the census says which screen that is in each.
            notice = census().get("ProblemNotice")
            for label in ("That's fine", "No thanks", "Yes, send them"):
                button = page.query_selector(f"text={label}")
                if button:
                    if notice is not None:
                        page.screenshot(path=str(
                            OUT / f"{notice:03d}-before-anything-is-sent.png"))
                    button.click()
                    page.wait_for_timeout(400)
                    break
            # Each console spells this control differently — `.wl-min` on
            # the lights widget, `.vl-min` in the vault, `.uw-min` on the
            # task window — so the sweep asks for all of them and a console
            # that has none simply finds nothing.
            #
            # The task window earns its place on this list the hard way. It
            # is *meant* to float over everything running, and at the phone
            # width these captures use it came to rest on the Hands
            # screen's move checkboxes: the controls that card exists to
            # offer. Clearing the tab bar fixed the half of that which was
            # a bug; a fixed float covers page content at some scroll
            # position no matter where it sits, and that half is the
            # feature. So the gallery minimises it, the way a person does.
            #
            # It is pressed, not hidden: the widget carries its own
            # minimise control, which is what a person does with it, and
            # the state is remembered per browser so one press carries
            # across every reload. What is photographed stays a state the
            # product can actually be in.
            for control in (".wl-min", ".vl-min", ".uw-min"):
                minimise = page.query_selector(control)
                if minimise:
                    minimise.evaluate("el => el.click()")
                    page.wait_for_timeout(200)
            for number, tab, stem in shots:
                if not open_tab(page, tab):
                    print(f"  ! {tab}: never reached — nothing written")
                    continue
                page.evaluate("window.scrollTo(0, 0)")
                page.wait_for_timeout(250)
                target = OUT / f"{number}-{stem}.png"
                page.screenshot(path=str(target), full_page=True)
                written += 1
                print(f"  {target.name}")
            browser.close()
    finally:
        proc.terminate()
    print(f"{written} screen(s) photographed")


#: Every tab the shell routes to, in the shell's own order. `watch` is not
#: here: it is not a pane but a place that takes the whole viewport, and it
#: has a gallery of its own under `docs/watch/` that is drawn rather than
#: photographed on purpose — those are the watch faces themselves.
TABS = [
    "home", "monitor", "safety", "baseline", "meds", "careteam",
    "selfprofile", "coach", "engaged", "wellness", "checkin", "journal",
    "aims", "wards", "attending", "reach", "hands", "bearing", "community",
    "presence", "feed", "channel", "permits", "held", "access", "settings",
]


if __name__ == "__main__":
    main(numbered(TABS))
