"""A route the backend made public, in a client that made it private.

QRME's copy of this file found three such routes there. This is the same
question asked of JIM, and the answer is worse, because of who is holding the
phone.

## The finding

`relay_guidance` states its own audience in one sentence:

    What to tell whoever is waiting. **Public: the person standing over a
    colleague has no account and needs an answer in ninety seconds.**

Three things were true of that route and false of the product:

1. The console binding sent a credential — `alarmGuidance(alarmId, body,
   token)` — so a route written for somebody with no account could only be
   called by somebody with one.
2. Its only caller was `Attending.tsx`, behind `if (!session.userId) return
   <Onboarding />`. `Attending` is the **Guardian's** side of an alarm: the
   person watching from a desk, deciding whether to escalate. Not the person
   on the floor.
3. The surface the passer-by actually reaches — `GET /c/{id}`, the page a
   camera app opens when somebody scans a sticker — raised the alarm, showed
   the Medical ID, and stopped. The one route written for them was on a screen
   they will never see.

So the ninety seconds the docstring is counting were spent by somebody who
could not get to the thing being counted.

## Why the door is a server-rendered page and not a console screen

QRME's public doors belong in its console: the person contesting a synthetic
profile of themselves is at a keyboard, following a link out of a takedown
notice. JIM's does not. `landing.py` says who this reader is, and it was right
before this round found the gap:

    It opens inside a camera app's in-app browser, on cellular, from a cold
    start, possibly by somebody kneeling next to a person on the floor.

That person is not going to install an app. The guidance box now renders on
that page, after the alarm, from the alarm id the alarm's own response
carries — one document, no second request to be legible.

It renders **outside** the Medical ID block, deliberately. A minor's beacon
opens no clinical stage to anybody, so `medical_id` comes back null and the
old code returned early at exactly that point. Somebody kneeling over a child
needs to know what to do more than anyone, not less.

## What this file does not claim

It is not an authentication audit. It names one route and asks one question
about it, and checks that the route is still public before asking — so that a
future decision to gate it fails here loudly rather than leaving a page that
always 401s in front of somebody in a hurry.
"""

from __future__ import annotations

import re
from pathlib import Path

from jim.api import app

from . import clientpaths


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()

#: The route, and the phrase in its docstring that makes it public.
PUBLIC_ROUTE = "POST /alarms/{alarm_id}/guidance"
PUBLIC_BECAUSE = "has no account"


def test_the_public_route_is_still_a_route():
    """A guard on the guard. Everything below searches for a string; if the
    route is renamed, every check would pass by finding nothing to fail on."""
    routed = {f"{m} {r.path}"
              for r in clientpaths.all_routes(app)
              for m in (r.methods or set()) - {"HEAD", "OPTIONS"}}
    assert PUBLIC_ROUTE in routed, (
        f"{PUBLIC_ROUTE} is not a route any more, so the checks below are "
        "vacuous")


def test_the_backend_still_means_it_to_be_public():
    """The premise, checked rather than assumed.

    Gating this route later would be a legitimate decision. What must not
    happen is the decision being made without the beacon page's guidance box
    — which sends no credential — quietly becoming a 401 in front of somebody
    kneeling on a floor.
    """
    text = (REPO / "jim" / "api.py").read_text(encoding="utf-8")
    body = text[text.index("def relay_guidance"):]
    body = body[:body.index("\n    @app.")]
    assert PUBLIC_BECAUSE in body, (
        "relay_guidance no longer documents itself as public — if that is "
        "deliberate, the guidance box on the scanned beacon page is now a "
        "form that cannot be submitted by the person it is for")
    for guard in ("_user_or_404", "auth.principal", "auth.require",
                  "Depends("):
        assert guard not in body, (
            f"relay_guidance now uses {guard}: the route is no longer public, "
            "and the beacon page in front of it is misleading")


def test_the_scanned_page_carries_the_guidance():
    """The door for the person the route was written for.

    Not the console. They scanned a sticker; this is the only surface they
    will see.
    """
    page = (REPO / "jim" / "landing.py").read_text(encoding="utf-8")
    # Comments stripped, because this file's own docstring quotes the route
    # path and a match against prose would be the false positive this audit
    # has now made six times.
    code = re.sub(r"^\s*#[^\n]*$", "", page, flags=re.M)
    assert "/guidance" in code, (
        "the scanned beacon page does not call the guidance route — the "
        "person standing over somebody has no other surface")
    assert "%(guidance)s" in code or "'/alarms/'" in code, (
        "the guidance endpoint is not being built from a relative prefix; an "
        "absolute URL baked from JIM_PUBLIC_URL breaks every scan on a LAN, "
        "which is the failure landing.py was written to avoid")


def test_the_guidance_is_offered_for_a_minors_beacon_too():
    """The specific line this round nearly got wrong.

    `alarm()` returns `medical_id: None` for a minor — no clinical stage, to
    anyone — and the page's renderer used to `return` at exactly that point.
    Adding the guidance box after it would have given a first-aid prompt to
    everybody except the person kneeling over a child.
    """
    page = (REPO / "jim" / "landing.py").read_text(encoding="utf-8")
    script = page[page.index("_ALARM_JS"):]
    medical = script.find("var m=j.medical_id")
    ask = script.find("ask(j.alarm)")
    # `find`, not `index`: a missing call should fail with the reason rather
    # than a ValueError from the test's own string arithmetic. The first
    # version used `index` and the injection test reported a crash.
    assert medical != -1, "the alarm renderer no longer reads medical_id"
    assert ask != -1, (
        "the scanned beacon page never calls ask(j.alarm) — the guidance box "
        "is not being rendered after the alarm at all")
    assert ask > medical, "the guidance call moved above the Medical ID block"
    between = script[medical:ask]
    assert "if(!m)return" not in between, (
        "the renderer returns early when there is no Medical ID, so a minor's "
        "beacon shows no guidance — which is the one case where the person "
        "holding the phone is least likely to know what to do")


def test_the_console_binding_sends_no_credential():
    """A public route with a private binding is unreachable by its own user.

    The console keeps this call — a Guardian watching an alarm from a desk
    wants the same answer — but it must not require what the route does not.
    """
    api = (REPO / "app" / "src" / "api.ts").read_text(encoding="utf-8")
    binding = api[api.index("alarmGuidance:"):]
    binding = binding[:binding.index("\n  ", binding.index("req<"))]
    assert "token" not in binding, (
        "the console's alarmGuidance binding sends a credential to a route "
        "whose docstring says its caller has none:\n" + binding)
