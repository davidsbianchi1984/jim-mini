"""The helper dock — the pane in the corner of the app.

Mostly the same shape as QRME's, and the interesting tests are the two places
it deliberately differs. JIM-mini has thirty-six watch faces and the watch is a
Pro capability, so the people most in need of a glance without a wrist are
exactly the ones who do not have one.
"""

import inspect
import re

import pytest

from jim import dock
from jim.tests.conftest import as_user, enroll


# -- it shows and it routes; it never acts ------------------------------------

def test_the_dock_writes_nothing_but_where_it_sits(client):
    """A control in a 168px box hovering beside the button that clears an
    escalation is not a convenience — it is a mis-tap during the worst minute
    of somebody's week."""
    src = inspect.getsource(dock)
    written = set(re.findall(r"(?:INSERT INTO|DELETE FROM)\s+(\w+)", src))
    written |= set(re.findall(r"(?<!DO )\bUPDATE\s+(\w+)\s+SET", src))
    assert written <= {"dock_prefs"}, (
        f"the dock writes outside its own preferences: {written}")


def test_every_face_says_it_does_not_act(client):
    user = enroll(client)
    for name in dock.FACES:
        kwargs = {"surface_id": "alm_1"} if name in dock.PER_SURFACE else {}
        assert dock.face(user, name, **kwargs)["acts"] is False
    assert dock.vocabulary()["acts"] is False


def test_every_face_has_a_route_to_a_screen_that_exists(client):
    """A read-only pane whose faces went nowhere would be a dead end."""
    import os

    root = os.path.join(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))), "docs", "screens")
    drawn = {int(f.split("-", 1)[0]) for f in os.listdir(root)
             if f.endswith(".svg") and f.split("-", 1)[0].isdigit()}
    for name in dock.FACES:
        assert dock.route(name)["screen"] in drawn, name


# -- the alarm face is the one that differs from QRME -------------------------

def test_an_active_alarm_opens_the_pane_whatever_it_was_set_to(client):
    """QRME's dock tucks itself away on a surface being broadcast. The same
    rule here would hide the thing a person most needs to see."""
    user = enroll(client)
    dock.configure(user, state="hidden")
    out = dock.opens_as(user, alarm_active=True)
    assert out["state"] == "open" and out["face"] == "alarm"
    assert out["forced"] is True
    assert "alarm is active" in out["why"]


def test_the_preference_is_overridden_rather_than_rewritten(client):
    """The same shape as a capped microphone gain: a preference that was
    overridden is still theirs, and silently rewriting it would mean the
    settings screen and the pane disagreed about what was chosen."""
    user = enroll(client)
    dock.configure(user, state="hidden")
    forced = dock.opens_as(user, alarm_active=True)
    assert forced["wanted"] == "hidden"
    assert dock.settings(user)["state"] == "hidden"      # untouched on disk
    assert dock.opens_as(user, alarm_active=False)["state"] == "hidden"


def test_the_alarm_face_cannot_be_configured_away(client):
    """A pane somebody tidied up months ago is not a decision they made about
    the day it fires."""
    user = enroll(client)
    with pytest.raises(dock.DockError) as exc:
        dock.configure(user, faces=["helper", "vitals"])
    assert "cannot be removed" in str(exc.value)


def test_what_may_never_be_in_the_pane_is_published(client):
    """Still inside every screenshot, and every photo somebody else takes of
    the screen."""
    for key in ("journal", "medical_record", "guidance_text", "family_names"):
        assert key in dock.NEVER
    assert set(dock.vocabulary()["never"]) == set(dock.NEVER)


# -- the corner ----------------------------------------------------------------

def test_the_pane_can_only_sit_at_the_bottom(client):
    assert set(dock.CORNERS) == {"bottom_right", "bottom_left"}
    user = enroll(client)
    with pytest.raises(dock.DockError):
        dock.configure(user, corner="top_left")


def test_it_draws_before_anybody_has_touched_it(client):
    user = enroll(client)
    out = dock.settings(user)
    assert out["set"] is False
    assert out["corner"] == dock.DEFAULT_CORNER
    assert out["state"] == dock.DEFAULT_STATE


def test_a_per_surface_face_refuses_to_guess(client):
    user = enroll(client)
    with pytest.raises(dock.DockError):
        dock.face(user, "alarm")
    assert dock.face(user, "alarm", "alm_1")["surface_id"] == "alm_1"


def test_an_unknown_face_is_refused(client):
    user = enroll(client)
    with pytest.raises(dock.DockError):
        dock.face(user, "nonsense")
    with pytest.raises(dock.DockError):
        dock.configure(user, faces=["nonsense"])


# -- over the wire -------------------------------------------------------------

def test_the_vocabulary_and_routing_table_are_public(client):
    plain = {"authorization": ""}
    assert client.get("/dock/faces", headers=plain).status_code == 200
    r = client.get("/dock/where/alarm", headers=plain)
    assert r.status_code == 200 and r.json()["face"] == "alarm"
    assert client.get("/dock/where/nonsense",
                      headers=plain).status_code == 404


def test_the_pane_itself_is_the_users_own(client):
    mine = enroll(client)
    my_token = client.headers["authorization"].split()[1]
    other = enroll(client, display_name="Rae")
    as_user(client, my_token)

    assert client.get(f"/dock/{other}").status_code == 403
    assert client.put(f"/dock/{other}", json={"state": "open"}).status_code == 403
    assert client.get(f"/dock/{other}/face/vitals").status_code == 403
    assert client.get(f"/dock/{mine}").status_code == 200


def test_moving_it_round_trips_over_http(client):
    user = enroll(client)
    r = client.put(f"/dock/{user}",
                   json={"corner": "bottom_left", "state": "open",
                         "face": "vitals",
                         "faces": ["helper", "alarm", "vitals"]})
    assert r.status_code == 200, r.text
    out = client.get(f"/dock/{user}").json()
    assert out["corner"] == "bottom_left" and out["face"] == "vitals"

    ringing = client.get(f"/dock/{user}?alarm_active=true").json()
    assert ringing["face"] == "alarm" and ringing["forced"] is True


def test_removing_the_alarm_face_over_http_is_a_422(client):
    user = enroll(client)
    r = client.put(f"/dock/{user}", json={"faces": ["helper", "vitals"]})
    assert r.status_code == 422
    assert "cannot be removed" in r.json()["detail"]
