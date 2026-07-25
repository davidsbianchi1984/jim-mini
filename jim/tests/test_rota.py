"""The rota, and reaching the person it picks.

The relay's whole reason to exist is the night shift, so the tests that matter
most here are the ones about 2am:

* **A shift that crosses midnight is the normal case, not the edge case.** The
  naive ``start <= now <= end`` test is false for every minute of an 18:00–06:00
  shift, so most of what follows is that shift, checked from both sides of
  midnight and on the days either side of it.
* **A page that reached nobody must never look like one that reached
  somebody.** That is the failure the notification channel exists to end.
* **Incident scope survives the trip out of the building.** A webhook is the
  easiest place in the system to turn an incident into a health record.
"""

import hashlib
import hmac
import json
from datetime import datetime, timezone

import pytest

from jim import notify, relay, rota

NIGHT = json.dumps([
    {"name": "Dana Okafor", "role": "on-call", "days": "mon-fri",
     "from": "18:00", "to": "06:00"},
    {"name": "Ash Bell", "role": "day supervisor", "days": "mon-fri",
     "from": "06:00", "to": "18:00"},
])


def at(s):
    """A site-local moment. 2026-07-20 is a Monday."""
    return datetime.fromisoformat(s).replace(tzinfo=timezone.utc)


def _auth(tok):
    return {"Authorization": f"Bearer {tok}"}


class _Webhook:
    def __init__(self, status=200, boom=None):
        self.status, self.boom, self.calls = status, boom, []

    def post(self, url, data, headers):
        if self.boom:
            raise self.boom
        self.calls.append({"url": url, "body": json.loads(data),
                           "headers": headers})
        return type("R", (), {"status_code": self.status})()


# --- shifts ---------------------------------------------------------------

def test_a_night_shift_is_on_at_2am(monkeypatch):
    """The test the old flat list could never pass, and the hour the whole
    feature exists for."""
    monkeypatch.setenv("JIM_SITE_ROTA", NIGHT)
    # Tuesday 02:00 — Monday's 18:00-06:00 shift is still running.
    assert [p["name"] for p in rota.on_now(at("2026-07-21T02:00"))] \
        == ["Dana Okafor"]


def test_a_night_shift_is_on_at_2300_the_evening_before(monkeypatch):
    monkeypatch.setenv("JIM_SITE_ROTA", NIGHT)
    assert [p["name"] for p in rota.on_now(at("2026-07-20T23:00"))] \
        == ["Dana Okafor"]


def test_the_day_person_is_on_at_noon(monkeypatch):
    monkeypatch.setenv("JIM_SITE_ROTA", NIGHT)
    assert [p["name"] for p in rota.on_now(at("2026-07-20T12:00"))] \
        == ["Ash Bell"]


def test_a_wrapping_shift_belongs_to_the_day_it_started(monkeypatch):
    """Saturday 02:00 is Friday's night worker, still on the floor. Attributing
    the after-midnight half to *today* would ask whether Saturday is rostered
    — it is not — and leave the person actually in the building unpaged."""
    monkeypatch.setenv("JIM_SITE_ROTA", NIGHT)
    # Saturday 02:00 — mon-fri covers Friday, so Friday's night shift holds.
    assert [p["name"] for p in rota.on_now(at("2026-07-25T02:00"))] \
        == ["Dana Okafor"]
    # Sunday 02:00 — Saturday is not a rostered day, so nobody started.
    assert rota.on_now(at("2026-07-26T02:00")) == []


def test_a_gap_in_the_rota_is_visible_rather_than_papered_over(monkeypatch):
    """Nobody rostered must not quietly become 'the first name on the list',
    or a gap looks like one person being oddly popular at 4am."""
    monkeypatch.setenv("JIM_SITE_ROTA", NIGHT)
    sunday_4am = at("2026-07-26T04:00")
    names, anybody = rota.order(sunday_4am)

    assert anybody is False
    assert names == ["Dana Okafor", "Ash Bell"]   # still woken, in order
    d = rota.describe(sunday_4am)
    assert d["anybody_on_shift"] is False
    assert "nobody is rostered" in d["note"]


def test_on_shift_comes_first_and_everyone_else_still_follows(monkeypatch):
    monkeypatch.setenv("JIM_SITE_ROTA", NIGHT)
    names, anybody = rota.order(at("2026-07-21T02:00"))
    assert anybody is True
    assert names == ["Dana Okafor", "Ash Bell"]


def test_a_plain_roster_still_works_and_still_means_always_on(monkeypatch):
    """The old configuration must not change meaning under the new module."""
    monkeypatch.delenv("JIM_SITE_ROTA", raising=False)
    monkeypatch.setenv("JIM_SITE_ROSTER", "night-tech,supervisor")
    assert relay.roster() == ["night-tech", "supervisor"]
    assert [p["name"] for p in rota.on_now(at("2026-07-21T03:00"))] \
        == ["night-tech", "supervisor"]


def test_day_ranges_lists_and_wrapping_weeks_all_parse(monkeypatch):
    monkeypatch.setenv("JIM_SITE_ROTA", json.dumps([
        {"name": "Weekend", "days": "sat,sun"},
        {"name": "Wrapped", "days": "fri-mon"},
        {"name": "Always"},
    ]))
    names = [e["name"] for e in rota.entries()]
    assert names == ["Weekend", "Wrapped", "Always"]
    sunday = at("2026-07-26T10:00")
    assert [p["name"] for p in rota.on_now(sunday)] \
        == ["Weekend", "Wrapped", "Always"]
    wednesday = at("2026-07-22T10:00")
    assert [p["name"] for p in rota.on_now(wednesday)] == ["Always"]


def test_an_unreadable_rota_fails_at_read_time_not_at_3am(monkeypatch):
    monkeypatch.setenv("JIM_SITE_ROTA", "{not json")
    with pytest.raises(rota.RotaError):
        rota.entries()
    monkeypatch.setenv("JIM_SITE_ROTA", json.dumps([{"role": "on-call"}]))
    with pytest.raises(rota.RotaError):
        rota.entries()
    monkeypatch.setenv("JIM_SITE_ROTA", json.dumps([
        {"name": "X", "days": "funday"}]))
    with pytest.raises(rota.RotaError):
        rota.entries()


def test_an_unknown_timezone_is_named_rather_than_silently_utc(monkeypatch):
    """Falling back to UTC without saying so would page the wrong person by
    the size of the offset — and correctly for part of the year in some
    zones, which is worse than never working."""
    monkeypatch.setenv("JIM_SITE_ROTA", NIGHT)
    monkeypatch.setenv("JIM_SITE_TZ", "Mars/Olympus")
    assert rota.tz_is_valid() is False
    assert "wrong person" in rota.problem()


def test_a_real_timezone_shifts_the_boundary(monkeypatch):
    """A rota written in local time and evaluated in UTC is off by the
    offset — this is the bug JIM_SITE_TZ exists to prevent."""
    monkeypatch.setenv("JIM_SITE_ROTA", NIGHT)
    monkeypatch.setenv("JIM_SITE_TZ", "America/Los_Angeles")
    # 2026-07-21T12:00Z is 05:00 Tuesday in Los Angeles — Monday's night
    # shift, still running. Read the same instant in UTC and it is noon on a
    # Tuesday: firmly the day person. One instant, two answers, and only the
    # site's own clock gives the right one.
    assert [p["name"] for p in rota.on_now(at("2026-07-21T12:00"))] \
        == ["Dana Okafor"]
    monkeypatch.setenv("JIM_SITE_TZ", "UTC")
    assert [p["name"] for p in rota.on_now(at("2026-07-21T12:00"))] \
        == ["Ash Bell"]


# --- reaching them --------------------------------------------------------

def _site(client):
    from jim.tests.test_beacons import _adult, _place
    u = _adult(client, name="Lone Worker")
    b = _place(client, u["id"], u["user_token"], label="plant room",
               kind="site")
    a = client.post(f"/c/{b['id']}/alarm",
                    json={"message": "man down in the pump room"}).json()
    return u, b, a


def test_an_escalation_actually_sends_something(client, monkeypatch):
    """Before this, 'notified' meant a row saying somebody had been notified,
    and nothing had left the building."""
    monkeypatch.setenv("JIM_SITE_ROTA", NIGHT)
    monkeypatch.setenv("JIM_NOTIFY_URL", "https://pager.example/hook")
    u, _b, a = _site(client)
    hook = _Webhook()

    out = relay.escalate(u["id"], a["alarm"], http=hook)
    assert out["reached_somebody"] is True
    assert out["page"]["state"] == "sent"
    assert "unreached_note" not in out
    assert len(hook.calls) == 1
    assert hook.calls[0]["body"]["envelope"] == "jim-page/v1"
    assert hook.calls[0]["body"]["responder"] == out["notified"]


def test_an_unreachable_responder_says_so_and_asks_to_move_on(client,
                                                              monkeypatch):
    """'Waiting on a human' and 'waiting on a human who was never told' need
    different next moves — the second should escalate now, not after a
    timeout."""
    monkeypatch.setenv("JIM_SITE_ROTA", NIGHT)
    monkeypatch.setenv("JIM_NOTIFY_URL", "https://pager.example/hook")
    u, _b, a = _site(client)

    out = relay.escalate(u["id"], a["alarm"],
                         http=_Webhook(boom=OSError("connection refused")))
    assert out["reached_somebody"] is False
    assert out["page"]["state"] == "failed"
    assert out["unreached_note"] == notify.UNREACHED
    assert out["escalate_again_now"] is True
    # …and the alarm is untouched. A page is not an acceptance.
    assert out["awaiting"].startswith("acceptance")


def test_no_channel_queues_rather_than_pretending(client, monkeypatch):
    monkeypatch.setenv("JIM_SITE_ROTA", NIGHT)
    monkeypatch.delenv("JIM_NOTIFY_URL", raising=False)
    u, _b, a = _site(client)

    out = relay.escalate(u["id"], a["alarm"])
    assert out["page"]["state"] == "queued"
    assert out["reached_somebody"] is False
    assert notify.channel()["configured"] is False


def test_the_page_carries_the_incident_and_not_the_person(client, monkeypatch):
    """The line that makes a workplace deployment acceptable, checked where it
    is easiest to lose: a payload leaving the building."""
    monkeypatch.setenv("JIM_SITE_ROTA", NIGHT)
    monkeypatch.setenv("JIM_NOTIFY_URL", "https://pager.example/hook")
    u, _b, a = _site(client)
    hook = _Webhook()
    relay.escalate(u["id"], a["alarm"], http=hook)

    body = json.dumps(hook.calls[0]["body"]).lower()
    for leak in ("lone worker", "1970-04-02", "+15555550123", "kin",
                 "resting", "pump room", "man down"):
        assert leak not in body, f"the page leaked {leak!r}"
    assert hook.calls[0]["body"]["scope"] == "incident"
    assert hook.calls[0]["body"]["finder_words_withheld"] is True
    assert hook.calls[0]["body"]["site_label"] == "plant room"


def test_a_page_says_whether_the_rota_was_actually_covering(client,
                                                            monkeypatch):
    """A page sent because the rota ran dry is a guess, and the person it
    wakes has no other way to know that."""
    monkeypatch.setenv("JIM_SITE_ROTA", NIGHT)
    monkeypatch.setenv("JIM_NOTIFY_URL", "https://pager.example/hook")
    u, _b, a = _site(client)
    hook = _Webhook()

    class _Sunday:
        """Freeze the relay at 04:00 on a Sunday — a gap in this rota."""
        def __enter__(self):
            self._real = rota.now
            rota.now = lambda: at("2026-07-26T04:00")
            return self

        def __exit__(self, *exc):
            rota.now = self._real

    with _Sunday():
        out = relay.escalate(u["id"], a["alarm"], http=hook)

    assert out["on_shift"] is False
    assert hook.calls[0]["body"]["on_shift"] is False


def test_a_page_is_signed_when_a_secret_is_set(client, monkeypatch):
    monkeypatch.setenv("JIM_SITE_ROTA", NIGHT)
    monkeypatch.setenv("JIM_NOTIFY_URL", "https://pager.example/hook")
    monkeypatch.setenv("JIM_NOTIFY_SECRET", "s3cret")
    u, _b, a = _site(client)
    hook = _Webhook()
    relay.escalate(u["id"], a["alarm"], http=hook)

    call = hook.calls[0]
    body = json.dumps(call["body"], sort_keys=True)
    expected = hmac.new(b"s3cret",
                        f"{call['headers']['X-JIM-Timestamp']}.{body}".encode(),
                        hashlib.sha256).hexdigest()
    assert call["headers"]["X-JIM-Signature"] == f"sha256={expected}"
    assert "pager.example" not in json.dumps(notify.channel())


def test_undelivered_pages_are_listable(client, monkeypatch):
    monkeypatch.setenv("JIM_SITE_ROTA", NIGHT)
    monkeypatch.delenv("JIM_NOTIFY_URL", raising=False)
    u, _b, a = _site(client)
    out = relay.escalate(u["id"], a["alarm"])

    r = client.get(f"/users/{u['id']}/pages?undelivered_only=true",
                   headers=_auth(u["user_token"])).json()
    assert [p["id"] for p in r] == [out["page"]["id"]]


def test_the_rota_endpoint_answers_who_would_be_paged_now(client, monkeypatch):
    """Answerable in the afternoon rather than discovered at 3am."""
    monkeypatch.setenv("JIM_SITE_ROTA", NIGHT)
    body = client.get("/relay/rota").json()
    assert body["configured"] is True
    assert [s["name"] for s in body["shifts"]] == ["Dana Okafor", "Ash Bell"]
    assert body["shifts"][0]["crosses_midnight"] is True
    assert body["shifts"][1]["crosses_midnight"] is False
    assert set(body["escalation_order"]) == {"Dana Okafor", "Ash Bell"}


def test_the_relay_still_cannot_reach_emergency_services(client, monkeypatch):
    """A notification channel is not a siren. Wiring one up must not have
    quietly raised the ceiling."""
    monkeypatch.setenv("JIM_SITE_ROTA", NIGHT)
    monkeypatch.setenv("JIM_NOTIFY_URL", "https://pager.example/hook")
    u, _b, a = _site(client)
    hook = _Webhook()

    for _ in range(2):
        relay.escalate(u["id"], a["alarm"], http=hook)
    out = relay.escalate(u["id"], a["alarm"], http=hook)
    assert out["exhausted"] is True
    assert out["call_emergency_services_yourself"] is True
    assert client.get("/relay/roster").json()["ceiling"] == "notify_contact"


# --- a config typo must not take down the escalation path ------------------

def test_an_unreadable_rota_does_not_break_escalation(client, monkeypatch):
    """The defect this guards: RotaError's own docstring says "raised at load,
    never at 3am" — but nothing reads the rota at start-up, so one typo
    (`funday` for `sunday`) propagated out of relay.roster() and turned
    POST …/escalate into a 500. A configuration mistake took down the one path
    whose entire job is getting somebody help, and only once an alarm had
    already been raised."""
    monkeypatch.setenv("JIM_SITE_ROTA", '[{"name": "Dana", "days": "funday"}]')
    monkeypatch.setenv("JIM_SITE_ROSTER", "night-tech,supervisor")
    u, _b, a = _site(client)

    out = relay.escalate(u["id"], a["alarm"])
    assert out is not None
    assert out["notified"] == "night-tech"      # fell back to the flat names
    assert "rota_error" in out                  # and said so, loudly
    assert "funday" in out["rota_error"]
    assert "nobody's shifts are being honoured" in out["rota_error"]


def test_an_unreadable_rota_still_answers_the_roster_endpoint(client,
                                                              monkeypatch):
    monkeypatch.setenv("JIM_SITE_ROTA", "{not json")
    monkeypatch.delenv("JIM_SITE_ROSTER", raising=False)
    body = client.get("/relay/roster").json()

    assert body["roster"] == list(relay.DEFAULT_ROSTER)
    assert "the default roster" in body["warning"]


def test_the_validation_endpoint_stays_strict(client, monkeypatch):
    """Degrading on the live path is right; degrading on the surface an
    operator uses to *check* their rota would hide the very thing they came
    to find."""
    monkeypatch.setenv("JIM_SITE_ROTA", '[{"name": "Dana", "days": "funday"}]')
    r = client.get("/relay/rota")
    assert r.status_code == 422
    assert "funday" in r.json()["detail"]


def test_read_never_raises_on_anything(monkeypatch):
    for bad in ("{not json", '{"name":"x"}', '[{"role":"on-call"}]',
                '[{"name":"x","days":"funday"}]',
                '[{"name":"x","from":"twenty past"}]', '["just a string"]'):
        monkeypatch.setenv("JIM_SITE_ROTA", bad)
        rows, err = rota.read()
        assert rows == [] and err, bad
        assert rota.order()[0] == []           # and the callers stay quiet
        assert rota.on_now() == []
