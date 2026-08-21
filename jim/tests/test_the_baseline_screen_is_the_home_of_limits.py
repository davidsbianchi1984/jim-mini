"""Every line the Guardian draws around a person lives on one screen.

The reviewer, over the live baseline screen: *round up all the other
settings — remove them from the other menus and put them here if they
belong here. We also need finances where you can set limit ranges with
sliders.*

    asked     where does a person set a limit
    mattered  is there one answer

Three settings qualified as limits living elsewhere: the vigil's
quiet-days (Settings), the sensitivity dial (Bearing — the very dial that
scales the bands this screen shows), and the money guardian's lines, one
of which — the low-balance floor — was not settable at all: a constant in
`jim/money.py` since the guardian arrived. The audit also surfaced a live
defect: both consoles offered a sensitivity level called "direct", which
the server has never accepted — every tap of that option was a 422.

This file pins the round-up, the new floor, and the rule that made the
finance sliders possible at all: a band's slider bounds come from the
metric, not from a unit guess in the screen.
"""

from __future__ import annotations

import pytest
from pathlib import Path

from jim import bands, db, guardian, money
from jim.api import app

REPO = Path(__file__).resolve().parents[2]
BASELINE = (REPO / "app/src/screens/Baseline.tsx").read_text(encoding="utf-8")
SETTINGS = (REPO / "app/src/screens/Settings.tsx").read_text(encoding="utf-8")
BEARING = (REPO / "app/src/screens/Bearing.tsx").read_text(encoding="utf-8")
WATCH = (REPO / "app/src/screens/Watch.tsx").read_text(encoding="utf-8")


# -- the round-up ----------------------------------------------------------

def test_the_limits_live_on_the_baseline_screen():
    for binding in ("api.armVigil(", "api.setSensitivity(",
                    "api.moneySetFloor(", "api.moneySetSavings(",
                    "api.moneySetMandate("):
        assert binding in BASELINE, (
            f"{binding} is not on the baseline screen — the round-up "
            "left a limit living somewhere else")


def test_the_old_homes_gave_them_up():
    assert "VigilPanel" not in SETTINGS, (
        "the vigil still lives in Settings — the round-up moved it, "
        "not copied it")
    assert "api.moneySetSavings(" not in SETTINGS, (
        "the savings goal is still settable from Settings")
    assert "api.setSensitivity(" not in BEARING, (
        "the sensitivity dial still lives on Bearing")


def test_the_mandate_grant_stays_where_permissions_live():
    """The caps are limits and belong on Baseline; the mandate itself is a
    grant of permission and stays in Settings. Moving the grant would have
    put 'may JIM invest at all' next to 'how wide is my heart-rate band',
    which is the confusion this screen exists to end."""
    assert "api.moneySetMandate(" in SETTINGS


# -- the level the server never accepted -----------------------------------

def test_no_console_offers_the_level_the_server_refuses():
    for name, src in (("Baseline", BASELINE), ("Bearing", BEARING),
                      ("Watch", WATCH)):
        assert '"direct"' not in src, (
            f"{name} still offers sensitivity level \"direct\" — the "
            "server accepts cautious/balanced/assertive, and that tap "
            "has been a 422 since the option shipped")
    assert '"assertive"' in BASELINE and '"assertive"' in WATCH


# -- the bounds come with the band -----------------------------------------

def test_every_band_states_its_own_slider():
    for metric, spec in bands.DEFAULTS.items():
        lo, hi, step = spec["slider"]
        assert 0 < lo <= spec["margin"] <= hi, (
            f"{metric}'s default margin sits outside its own slider")
        assert step > 0


def test_the_band_carries_its_bounds_to_the_screen():
    band = bands.band_for("nobody", "heart_rate")
    for key in ("slider_min", "slider_max", "slider_step"):
        assert key in band


def test_the_screen_stopped_guessing_scale_from_the_unit():
    assert "slider_min" in BASELINE
    assert '"°C"' not in BASELINE, (
        "the °C branch is back — bounds come with the band now, and a "
        "unit guess would hand any non-physiological metric a nonsense "
        "range")


# -- the floor, in the owner's hands ---------------------------------------

def _user(client):
    r = client.post("/enroll", json={"display_name": "Vera",
                                     "birthdate": "1979-04-02",
                                     "terms_consent": True})
    assert r.status_code == 201, r.text
    u = r.json()
    client.headers["authorization"] = f"Bearer {u['user_token']}"
    return u


def test_the_floor_was_a_constant_and_is_a_setting(client):
    u = _user(client)
    r = client.get(f"/money/{u['id']}")
    assert r.status_code == 200
    floor = r.json()["floor"]
    assert floor["source"] == "default"
    assert floor["floor"] == money.LOW_FLOOR

    r = client.put(f"/money/{u['id']}/floor", json={"floor": 400})
    assert r.status_code == 200
    assert r.json() == {"floor": 400, "source": "user",
                        "derived": money.LOW_FLOOR}


class _FakeVault:
    """Enough of a vault for add_account's rule 1 — the numbers go to the
    vault or nowhere, and this test brings no numbers anyway."""

    def __init__(self):
        self.sealed: dict[str, str] = {}

    def put(self, key, value):
        self.sealed[key] = value

    def get(self, key):
        return self.sealed.get(key)


def _checking(uid: str) -> dict:
    money.add_account(uid, "checking", "Home Bank", "Main",
                      None, None, None, _FakeVault())
    return money.accounts_for(uid)[0]


def test_the_low_balance_trip_honors_the_owners_floor(client):
    u = _user(client)
    acc = _checking(u["id"])
    money.observe(u["id"], acc["id"], 250.0, None, "en")
    # 250 is above the derived default floor of 100 — quiet.
    assert not [w for w in money.check(u["id"], "en")
                if w["kind"] == "low_balance"]
    money.set_floor(u["id"], 400)
    warnings = [w for w in money.check(u["id"], "en")
                if w["kind"] == "low_balance"]
    assert warnings, (
        "the owner raised their floor above their balance and the "
        "warning did not fire — the trip is still reading the constant")


def test_zero_is_refused_and_null_clears(client):
    u = _user(client)
    r = client.put(f"/money/{u['id']}/floor", json={"floor": 0})
    assert r.status_code == 422
    assert "positive" in r.json()["detail"]

    client.put(f"/money/{u['id']}/floor", json={"floor": 300})
    r = client.put(f"/money/{u['id']}/floor", json={"floor": None})
    assert r.status_code == 200
    assert r.json()["source"] == "default"


def test_the_mandate_engine_respects_the_raised_floor(client):
    """Raising your floor pulls the investing engine's hands back too: the
    cushion it must leave untouched is twice the same floor the warning
    trips on — the owner's own, not the constant."""
    u = _user(client)
    acc = _checking(u["id"])
    money.set_mandate(u["id"], True, 100.0, 500.0, ["index_funds"],
                      "grow slowly, cash first")
    # 1500 liquid over the default floor (cushion 200): the engine has
    # room and proposes.
    out = money.observe(u["id"], acc["id"], 1500.0, None, "en")
    assert out["orders_proposed"], "no proposal even with room to spare"
    # The owner raises the floor to 900 (cushion 1800 > 1500): the same
    # balance is now all cushion, and the engine keeps its hands off.
    money.set_floor(u["id"], 900)
    out = money.observe(u["id"], acc["id"], 1500.0, None, "en")
    assert not out["orders_proposed"], (
        "the engine proposed an order out of money the owner fenced off — "
        "the cushion is still built on the constant")
