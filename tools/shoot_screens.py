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
REVIEWER = "shots-reviewer"

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
    # The database in a directory of its own: the assistant's box hides the
    # database's directory inside its walls, and a database sitting bare in
    # /tmp would hide /tmp — including the workrooms — and refuse the box.
    Path("/tmp/jim-shots").mkdir(exist_ok=True)
    env["JIM_DB"] = "/tmp/jim-shots/jim.db"
    env["JIM_OFFLINE"] = "1"
    # The deployment's reviewer token, so the oversight desk can be opened
    # and photographed with something on it. A harness value, never a real
    # one: the database it guards is deleted at the top of every run.
    env["JIM_ADMIN_TOKEN"] = REVIEWER
    env.setdefault("JIM_WORKROOMS", "/tmp/jim-shots-rooms")
    Path("/tmp/jim-shots/jim.db").unlink(missing_ok=True)
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


def _door(path: str, body: dict, token: str) -> dict:
    request = urllib.request.Request(
        BASE + path, data=json.dumps(body).encode(),
        headers={"content-type": "application/json",
                 "authorization": f"Bearer {token}"})
    with urllib.request.urlopen(request, timeout=600) as answer:
        return json.load(answer)


#: A change the coding assistant might draft: one comment line, in a file
#: whose tests the box will find by name (`test_vigil.py`), so the run is
#: real and short.
DRAFT = """A note above the vigil's own words, and nothing else.

--- a/jim/vigil.py
+++ b/jim/vigil.py
@@ -1,2 +1,3 @@
+# Photographed for the gallery: the box tried this line.
 \"\"\"The vigil — the alarm that fires when the signals *stop*.
 
"""


def furnish(session: dict) -> None:
    """What the desks hold when they are photographed, put there through
    the product's own doors — never by writing rows.

    The moderated mailbox receives two letters, so the Correspondence
    screen shows threads held for a person rather than an empty tray. A
    drafted app edit is filed and tried in the assistant's box, so the
    Oversight desk shows a diff with the box's outcome beside it — a real
    run inside four walls, on this machine, at the moment of the capture.
    On a host that cannot raise the walls the edit is filed untried and
    the desk says so, which is also true.
    """
    uid, token = session["userId"], session["userToken"]
    for letter in (
        {"from_addr": "dr.okafor@clinic.example", "subject": "Your bloodwork",
         "body": "David — your panel came back and everything is where we "
                 "hoped. Keep the evening walks. Book the follow-up for "
                 "November when you can."},
        {"from_addr": "maria@example.test", "subject": "Sunday",
         "body": "Are you still coming for lunch on Sunday? Mum is asking "
                 "whether to make the big pot."},
    ):
        _door(f"/mail/{uid}/receive", letter, token)
    edit = _door(f"/appedits/{uid}", {
        "title": "A note above the vigil", "description":
        "One comment line at the top of jim/vigil.py, so the gallery shows "
        "an edit the box has tried.", "target": "jim/vigil.py",
        "patch": DRAFT}, token)
    try:
        _door(f"/appedits/{uid}/{edit['id']}/box", {}, token)
    except Exception as exc:  # noqa: BLE001 — the desk shows an untried edit then
        print(f"  ? the box did not try the draft ({type(exc).__name__}); "
              "the desk shows it untried")


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



#: Where a recipe starts when there is no session yet — the screens a
#: person meets before the console has anybody in it.
SIGNED_OUT = "signed-out"

#: Screens that are not a tab.
#:
#: Every capture until now came from pressing a nav tab, so every screen
#: that lives *inside* one — behind a card, a button, a mode switch —
#: stayed a drawing. Not because anybody decided it should: because the
#: camera had no way to get there, and a drawing is what fills a gap
#: nobody can photograph.
#:
#:     asked     can this camera reach every tab
#:     mattered  can it reach every screen
#:
#: A recipe is: the number, the file stem, where to start, what a person
#: presses to get there, and how this knows it arrived. `proof` is a
#: selector that exists on the screen being asked for and nowhere on the
#: way to it — the same refusal `open_tab` makes. A recipe whose proof
#: does not appear writes nothing and says so, because a wrong screen
#: filed under a right number is worse than a gap.
INSIDE: tuple[tuple[str, str, str, tuple[str, ...], str], ...] = (
    ("9", "sign-in", SIGNED_OUT, (), ".tabs .tab.active"),
    ("10", "log-in", SIGNED_OUT, (".tabs .tab:nth-child(2)",),
     ".tabs .tab:nth-child(2).active"),
    # The Studio is not a nav tile. It is reached the way a person reaches
    # it: from the Talk screen's rail, by the chip that names it.
    # The coach, out loud: a question asked, the answer read aloud, and the
    # sphere up while it speaks. The synthesiser is silenced by the harness
    # (see `main`), not the state — the console is in its speaking state,
    # drawn by its own code, with no sound coming out of a headless browser.
    ("14", "coach-out-loud", "coach",
     (("textarea", "How do I keep my heart rate steady on a long walk?"),
      "button.primary", "text=🔊 Read it aloud"),
     ".voice-orb-veil"),
    # The oversight desk with the reviewer token typed and the queue opened:
    # the edit `furnish` filed, with what the box made of it beside the diff.
    ("45", "oversight", "oversight",
     (("input[type=password]", REVIEWER), "text=Open the queue"),
     "text=In the box:"),
    ("40", "widgets", "engaged", ('.talk-chip[data-go="studio"]',),
     '[data-screen="40"]'),
)


def answer_the_notice(page) -> None:
    """Answer the problem-reporting consent card, if it is asking.

    It opens over everything on a browser that has never answered it, and
    it is answered once at the start of a run. `open_inside` then clears
    `localStorage` to reach the signed-out screens — which is exactly the
    state the notice keys off, so it came back, and every capture after
    the first signed-out recipe carried it. The Studio's page came back
    with the whole card sitting above the heading.

        asked     was the notice answered
        mattered  is it still answered when this shot is taken

    Idempotent: on a browser that has already answered, nothing matches
    and this does nothing.
    """
    for label in ("That's fine", "No thanks", "Yes, send them"):
        button = page.query_selector(f"text={label}")
        if button:
            button.click()
            page.wait_for_timeout(400)
            return


def tuck_the_widgets(page) -> None:
    """Minimise the floating widgets, the way a person does.

    The second half of the same repair as `answer_the_notice`: the
    minimise is remembered per browser, `localStorage.clear()` forgets it,
    and the Studio's page came back with the Guardian's lights open across
    the code box. Each console spells the control differently — `.wl-min`
    on the lights, `.vl-min` in the vault, `.uw-min` on the task window —
    so this asks for all of them and a console with none finds nothing.

    Pressed, not hidden: the widget carries its own minimise control,
    which is what a person does with it, so what is photographed stays a
    state the product can actually be in.
    """
    for control in (".wl-min", ".vl-min", ".uw-min"):
        minimise = page.query_selector(control)
        if minimise:
            minimise.evaluate("el => el.click()")
            page.wait_for_timeout(200)


def open_inside(page, session, start, presses, proof) -> bool:
    """Reach a screen that is not a tab, and refuse to lie about it."""
    if start == SIGNED_OUT:
        page.goto(CONSOLE, wait_until="networkidle")
        page.evaluate("() => localStorage.clear()")
        page.goto(CONSOLE, wait_until="networkidle")
    else:
        page.evaluate("s => localStorage.setItem('jim.session', s)",
                      json.dumps(session))
        if not open_tab(page, start):
            print(f"  ? could not open the {start} tab")
            return False
        # A signed-out recipe earlier in this run cleared
        # `localStorage`, so the consent notice may be asking again and
        # the widgets may have forgotten they were tucked away.
        answer_the_notice(page)
        tuck_the_widgets(page)
    page.wait_for_timeout(900)
    if not follow(page, presses):
        return False
    # The proof is what the recipe came for: bring it into view, so a
    # screen taller than the phone is photographed at the part that
    # matters rather than at its top. The console scrolls inside its own
    # frame, so a full-page capture alone does not reach it.
    landed = page.query_selector(proof)
    if landed is not None:
        landed.scroll_into_view_if_needed()
        page.wait_for_timeout(300)
    page.wait_for_timeout(600)
    return page.query_selector(proof) is not None


#: Things that are painted past the right edge on purpose.
#:
#: `past_the_edge` exists to catch content clipped away by accident, and
#: the phone's tab bar is off-edge by design. Reported every run against
#: every screen, it would bury the one row that mattered — which is how a
#: check with a false positive per capture stops being read at all.
#:
#:     asked     is anything drawn past the edge
#:     mattered  is anything drawn past it that did not mean to be
#:
#: Each row names the reason, so a rule that stops being deliberate stops
#: being exempt. The element and everything inside it is skipped.
EDGE_EXEMPT = (
    ("nav",
     "the phone bar keeps its row and scrolls sideways: twenty-four tiles "
     "at a readable icon size do not fit across a phone, and squeezing "
     "them to fit is how the mark became unreadable in the first place. "
     "The tiles past the edge are the ones a thumb scrolls to."),
)

def past_the_edge(page) -> list[str]:
    """Everything this viewport draws to the right of its own right edge.

    A page can overflow horizontally in two unrelated ways, and only one of
    them is visible to `document.scrollWidth`. When the document itself is
    the scroll container, too-wide content widens the document and the
    number goes up. When the too-wide content sits inside an element with
    its own `overflow`, the scroll container absorbs it: the document stays
    exactly as wide as the window, the number says the page fits, and the
    right-hand end of whatever is inside is simply clipped away.

    The front door was the second kind. `.onboarding` scrolls vertically,
    so it is a scroll container, so a card 74px too wide for a 390px phone
    cost the Sign in button its right half while every width this harness
    knew how to ask about answered "fits".

        asked     is the document wider than the window
        mattered  is anything drawn past the window's edge

    So this asks the second question of every element on the page and names
    the ones that answer yes, per capture, for every screen — not just the
    one that happened to be caught by eye. A rectangle is measured where it
    was actually painted, which is the only place a person meets it.
    """
    return page.evaluate("""(skip) => {
      const edge = document.documentElement.clientWidth;
      const over = [];
      for (const el of document.querySelectorAll('body *')) {
        const style = getComputedStyle(el);
        if (style.visibility === 'hidden' || style.display === 'none') continue;
        const box = el.getBoundingClientRect();
        if (box.width === 0 || box.height === 0) continue;
        // A fixed float parked off-screen on purpose is not this bug, and
        // neither is something scrolled sideways by a person: only what is
        // painted past the edge while the page sits at its own origin.
        if (box.right <= edge + 1) continue;
        if (skip.some((sel) => el.closest(sel))) continue;
        const name = el.tagName.toLowerCase()
          + (el.id ? '#' + el.id : '')
          + (el.className && typeof el.className === 'string'
             ? '.' + el.className.trim().split(/\\s+/).join('.') : '');
        over.push(name + ' +' + Math.round(box.right - edge) + 'px');
      }
      // The outermost offender is the one to fix; its children overflow
      // because it does. Report the first few, deepest last.
      return over.slice(0, 6);
    }""", [s for s, _why in EDGE_EXEMPT])


#: Screens that are a card on a screen, not a screen of their own.
#:
#: The census lets one component own several numbers — `Coach 14,24,82`,
#: `Baseline 38,81` — because a component draws more than one thing a
#: person meets. The tab captures the whole page; these are the parts of
#: it the gallery numbers separately, and until now every one of them was
#: a drawing for the same reason the non-tab screens were: the camera
#: could photograph a page and nothing smaller.
#:
#:     asked     can the camera reach every page
#:     mattered  can it reach everything the gallery numbers
#:
#: The element is found by `data-screen="<number>"` on the element that
#: owns it — the same shape as the `data-tab` the nav has always carried,
#: and for the same reason: a marker in the markup is a thing the camera
#: and the reader can both check, where a CSS selector guessed from
#: outside is a thing that silently starts matching the wrong card. A
#: recipe whose element is not on the page writes nothing and says so.
ELEMENTS: tuple[tuple[str, str, str, tuple[str, ...]], ...] = (
    ("34", "what-this-tab-wont-do", "feed", ()),
    ("36", "what-it-will-not-be", "presence", ()),
    ("19", "journal-new-entry", "journal", ()),
    ("15", "which-model-answers", "settings", ()),
    ("22", "what-went-wrong", "settings", ()),
    ("8", "baseline-metrics", "baseline", ()),
    # `jim/conditions.py`: an extreme rate with *slow* breathing is
    # cardiac until proven otherwise — 200 bpm at respiration 10 clears
    # `hr >= max(180, resting + 100)` with `slow_breath`, and the
    # first-aid guidance that comes back is what draws the pace circle.
    # The numbers are the rule's, not a guess: change the rule and this
    # recipe stops reaching the screen and says so.
    ("4", "cpr-coach", "monitor",
     (("input[type=number]", 200), ("input[type=number] >> nth=1", 10),
      "button.primary")),
)


def shoot_element(page, session, number, start, presses) -> bool:
    """Photograph one card, and refuse to photograph the wrong one."""
    page.evaluate("s => localStorage.setItem('jim.session', s)",
                  json.dumps(session))
    if not open_tab(page, start):
        print(f"  ? could not open the {start} tab")
        return False
    answer_the_notice(page)
    tuck_the_widgets(page)
    if not follow(page, presses):
        return False
    page.wait_for_timeout(600)
    return page.query_selector(f'[data-screen="{number}"]') is not None


def follow(page, steps) -> bool:
    """Do what a person does to get there: press, or type and then press.

    A step is a selector to press, or `(selector, value)` to fill. Filling
    needs `input()` dispatched the way React listens for it — setting
    `.value` alone updates the DOM node and leaves the component's state
    where it was, so the form submits its defaults and the screen the
    recipe asked for never appears.

        asked     is the field showing the number
        mattered  does the component know the number changed
    """
    for step in steps:
        if isinstance(step, tuple):
            selector, value = step
            field = page.query_selector(selector)
            if field is None:
                print(f"  ? nothing matched {selector}")
                return False
            field.fill(str(value))
            page.wait_for_timeout(200)
            continue
        target = page.query_selector(step)
        if target is None:
            print(f"  ? nothing matched {step}")
            return False
        target.evaluate("el => el.click()")
        page.wait_for_timeout(700)
    return True


#: What the shell floats over every screen, hidden while a card sits for
#: its portrait.
#:
#: An element screenshot is a crop of the rendered page, not a render of
#: the element alone, so anything painted over that rectangle lands in the
#: picture — and all of this is `position: fixed`, which means it is
#: painted over every rectangle. The first card shot came back with the
#: Guardian's lights across one corner and the task window across another.
#:
#:     asked     is the card in the picture
#:     mattered  is anything else in it
#:
#: Hiding it here is not hiding it from the gallery: every one of these is
#: photographed on all twenty-seven page captures, which is where a reader
#: meets them. What a card portrait is *for* is the card.
FURNITURE = (".help-fab", ".help-panel", ".watch-lights", ".wl-dot",
             ".underway", ".uw-dot", ".footsteps",
             # The specialist's sphere, and the veil it stands behind.
             # A detection with guidance opens it and speaks; when the
             # browser refuses the audio without a fresh gesture it holds,
             # veil and all, waiting for a tap. That is a real state and
             # it is photographed on the Monitor page itself — but it is
             # drawn over the whole viewport, so a portrait of the card
             # underneath came back as a blurred veil and nothing else.
             ".voice-orb-veil")

_HIDE = "jim-camera-hide"


def hide_furniture(page) -> None:
    page.evaluate(
        """(sel) => {
          const style = document.createElement('style');
          style.id = 'jim-camera-hide';
          style.textContent = sel.join(',') + '{visibility:hidden!important}';
          document.head.appendChild(style);
        }""", list(FURNITURE))


def show_furniture(page) -> None:
    page.evaluate(
        """() => {
          const style = document.getElementById('jim-camera-hide');
          if (style) style.remove();
        }""")


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
        furnish(session)
        with sync_playwright() as play:
            browser = play.chromium.launch(
                executable_path="/opt/pw-browsers/chromium")
            page = browser.new_page(viewport=VIEWPORT,
                                    device_scale_factor=SCALE)
            # A headless browser has no voice. `say()` falls back to the
            # device's synthesiser and waits for it to finish; this one
            # never does, so the coach stays in its speaking state for the
            # camera — the product's own state, only silent.
            page.add_init_script("""
              Object.defineProperty(window, 'speechSynthesis', { value: {
                _on: false,
                speak() { this._on = true; },
                cancel() { this._on = false; },
                get speaking() { return this._on; },
                pending: false, paused: false,
                getVoices() { return []; },
                addEventListener() {}, removeEventListener() {},
              }});
            """)
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
                for offender in past_the_edge(page):
                    print(f"      past the right edge: {offender}")

            # The screens that are not tabs. Same refusal: a recipe whose
            # proof does not appear writes nothing.
            for number, stem, start, presses, proof in INSIDE:
                if not open_inside(page, session, start, presses, proof):
                    print(f"  ! {number}-{stem}: never reached — "
                          "nothing written")
                    continue
                page.evaluate("window.scrollTo(0, 0)")
                page.wait_for_timeout(250)
                target = OUT / f"{number}-{stem}.png"
                page.screenshot(path=str(target), full_page=True)
                written += 1
                print(f"  {target.name}")
                for offender in past_the_edge(page):
                    print(f"      past the right edge: {offender}")
            # The cards. Same refusal as the screens: a recipe whose
            # element is not on the page writes nothing.
            for number, stem, start, presses in ELEMENTS:
                if not shoot_element(page, session, number, start, presses):
                    print(f"  ! {number}-{stem}: never reached — "
                          "nothing written")
                    continue
                el = page.query_selector(f'[data-screen="{number}"]')
                el.scroll_into_view_if_needed()
                page.wait_for_timeout(250)
                target = OUT / f"{number}-{stem}.png"
                hide_furniture(page)
                el.screenshot(path=str(target))
                show_furniture(page)
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
    "presence", "feed", "channel", "capabilities", "permits", "held",
    "access", "settings", "mail",
]


if __name__ == "__main__":
    main(numbered(TABS))
