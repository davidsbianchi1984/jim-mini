"""The held screen's buttons match the wire, and the doors exist.

Three console finds from one walk of the app, each a promise the shell
made that the server or the navigation did not keep:

1. The quick-allow buttons sent source names the ``Source`` enum
   rejects — "Allow mail" and "Allow photos" answered 422 on every
   press. A button that always refuses is a broken promise with a
   label, so the list is held to the enum by a standing test.
2. The permits screen rendered under its tab and appeared in no menu —
   reachable only through the assistant's chip rail. Every rendered tab
   must now have a door somewhere a person can press it.
3. Enrollment could refuse *after* creating the user and *before*
   creating the membership — an unknown language or plan left an
   account every capability gate read as "visitor". A refusal must
   leave nothing behind, and activation (a click on an emailed link,
   nobody standing there to hand a 422 to) coerces a bad parked plan to
   the default instead of stranding the account.
"""

from __future__ import annotations

import json
import re
from typing import get_args

from jim import accounts, db, models, tiers

from jim.tests.conftest import enroll
from jim.tests.test_accounts import _capture_mail, _code_from, _signup
from jim.tests.test_the_refusal_names_the_field_on_the_form import REPO

APP = (REPO / "app/src/App.tsx").read_text(encoding="utf-8")
HELD = (REPO / "app/src/screens/Held.tsx").read_text(encoding="utf-8")
TALK = (REPO / "app/src/screens/Talk.tsx").read_text(encoding="utf-8")


# -- 1. the buttons match the wire ------------------------------------------

def test_every_quick_allow_button_names_a_source_the_wire_accepts():
    """The list the buttons are drawn from, held to the enum the route
    validates with — the drift this guards against already shipped once
    ("mail", "photos")."""
    lists = re.findall(r"\[((?:\s*\"[a-z_]+\",?)+)\s*\]\.map\(\(s\)", HELD)
    assert lists, "the quick-allow row moved; update this parser with it"
    allowed = set(get_args(models.Source))
    for found in lists:
        names = re.findall(r"\"([a-z_]+)\"", found)
        strangers = [n for n in names if n not in allowed]
        assert not strangers, (
            f"quick-allow button(s) {strangers} send names the Source enum "
            f"rejects — every press is a 422; the wire accepts {sorted(allowed)}")


# -- 2. the doors exist ------------------------------------------------------

def _rendered_tabs() -> set[str]:
    return set(re.findall(r"\{tab === \"([a-z]+)\"", APP))


def _nav_ids() -> set[str]:
    return set(re.findall(r"\{ id: \"([a-z]+)\", icon:", APP))


def _rail_ids() -> set[str]:
    return set(re.findall(r"\{ id: \"([a-z]+)\", icon:", TALK))


def test_every_rendered_screen_has_a_door():
    """A screen only the assistant can open is a screen most people never
    learn exists — the permits card was one until this round. Every tab
    the main pane renders must be pressable from the sidebar menu or the
    assistant's chip rail."""
    doorless = _rendered_tabs() - _nav_ids() - _rail_ids()
    assert not doorless, (
        f"screen(s) {sorted(doorless)} render under a tab nothing opens — "
        "add a NAV entry (App.tsx), a rail chip (Talk.tsx), or a documented "
        "door here")


def test_every_door_opens_a_screen_that_exists():
    """The other direction: a menu entry or chip whose tab nothing
    renders is a door into a wall. `watch` is the one exception — it is
    a place rather than a pane, opened whole-viewport through the URL
    hash, and the hash door is asserted rather than assumed."""
    ghosts = (_nav_ids() | _rail_ids()) - _rendered_tabs() - {"watch"}
    assert not ghosts, f"door(s) {sorted(ghosts)} open no rendered tab"
    assert "#watch" in APP, "the watch hash door left App.tsx"


def test_the_permits_screen_has_its_own_menu_entry():
    assert "permits" in _nav_ids(), (
        "the permits screen is rail-only again — a screen about what the "
        "assistant may change must not be a screen only the assistant opens")
    assert '"nav.permits"' in (REPO / "app/src/l10n.ts").read_text(
        encoding="utf-8")


# -- 3. a refusal leaves nothing behind -------------------------------------

def _user_count() -> int:
    return db.connect().execute("SELECT COUNT(*) AS n FROM users").fetchone()["n"]


def test_a_refused_language_creates_no_user(client):
    before = _user_count()
    r = client.post("/enroll", json={
        "display_name": "Sam", "birthdate": "1990-01-01",
        "terms_consent": True, "language": "tlh"})
    assert r.status_code == 422, r.text
    assert _user_count() == before, (
        "the refusal left a half-enrolled user behind — created before the "
        "language was checked, refused before the membership existed")


def test_a_refused_plan_creates_no_user(client):
    before = _user_count()
    r = client.post("/enroll", json={
        "display_name": "Sam", "birthdate": "1990-01-01",
        "terms_consent": True, "plan": "premium"})
    assert r.status_code == 422, r.text
    assert "premium" not in tiers.PLANS
    assert _user_count() == before


def test_signup_refuses_an_unknown_plan_while_somebody_is_there(client,
                                                                monkeypatch):
    """Checked at signup, where the person is present to correct it —
    not at /verify-email, where the failure used to strand a created
    user with no membership."""
    _capture_mail(monkeypatch)
    r = client.post("/signup", json={
        "email": "dana@example.test", "password": "hunter2-hunter2",
        "display_name": "Dana", "birthdate": "1990-09-14",
        "terms_consent": True, "plan": "premium"})
    assert r.status_code == 422, r.text


def test_a_legacy_parked_plan_still_activates_on_the_default(client,
                                                             monkeypatch):
    """Payloads parked before /signup validated plans — and the OAuth
    door's free-form enroll dict — still activate: the unknown plan
    falls to the default rather than raising between the user's creation
    and their membership."""
    sent = _capture_mail(monkeypatch)
    assert _signup(client).status_code == 201
    conn = db.connect()
    row = conn.execute("SELECT id, pending_profile FROM accounts WHERE"
                       " email=?", ("dana@example.test",)).fetchone()
    parked = json.loads(row["pending_profile"])
    parked["plan"] = "premium"
    conn.execute("UPDATE accounts SET pending_profile=? WHERE id=?",
                 (json.dumps(parked), row["id"]))
    conn.commit()
    r = client.post("/verify-email", json={
        "email": "dana@example.test", "code": _code_from(sent[0])})
    assert r.status_code == 200, r.text
    assert r.json()["membership"]["plan"] == tiers.DEFAULT_PLAN


def test_an_ordinary_enrollment_is_never_planless(client):
    uid = enroll(client)
    assert tiers.plan_of(uid) != "visitor", (
        "an enrollment completed and left no membership — every capability "
        "gate reads this account as a visitor")
