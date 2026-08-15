"""The weakest path in the product was the one for the person on the floor.

    say if you collapse on the floor and needed help and assistance how are
    you gonna put a sticker on a door

The field report that reframed the safety screen. It was answered on the
pressing end — "Get help now" leads, beacons moved below it and now say they
are the bystander's path — and the *other* end of the same report went
unanswered. When somebody actually collapses they press nothing at all. The
crash watch is what runs then, and it was the one way this product summons
help that never went near the ladder every other way goes through.

    asked     what tier did the trip reach
    mattered  why, and does the person reading the page know what to do

## Two findings, one shape

**The decision had no reasoning on the record.** ``_trip`` computed its tier
with ``"emergency_services" if the box was ticked else "notify_contact"``.
Every other escalation in this product returns a ``path`` that can be replayed
and argued with; the acute one returned a boolean's opinion. It goes through
:func:`jim.escalation.decide` now and answers the same tier — deliberately,
because this is not new behaviour, it is the old behaviour with its argument
attached.

**The page said everything except the thing to do.** The bystander's path has
told a stranger to dial the number themselves since it shipped, in ten
languages, on a page a passer-by reads once. The collapse path emailed the
trusted contact at 3am to "treat it as real" and stopped there — no mention
that JIM cannot call, on either setting of the box. The ticked box is the one
that most needs it: a dispatch *request* relayed to connected systems is the
thing that most looks like a call having been placed.

The estate answers this shape the same way every time — the refusal that names
its cause, the custody note that lists its limits, the beacon note that stopped
claiming an alert had gone out when nothing had. A limit is allowed. A silent
one is not.
"""

from __future__ import annotations

import inspect
import json
from datetime import datetime, timedelta, timezone

import pytest

from jim import beacons, crashwatch, db, escalation
from jim.tests.conftest import enroll


def _tripped(client, *, ems: bool) -> str:
    """Arm the watch, land a critical reading, and let every window pass
    unanswered — the only state any of this is reachable in."""
    user = enroll(client)
    client.put(f"/crash-watch/{user}", json={
        "trusted_name": "Rosa", "trusted_channel": "rosa@example.com",
        "attempts": 2, "window_minutes": 5.0,
        "contact_emergency_services": ems})
    client.post(f"/monitor/{user}", json={"blood_oxygen": 85})
    later = datetime.now(timezone.utc) + timedelta(hours=1)
    assert crashwatch.sweep(user, now=later)["tripped"] is True
    return user


@pytest.fixture()
def posted(monkeypatch):
    """Every page that actually went out, in order. Mail is not configured in
    the suite, so the trip records a `console` delivery and sends nothing —
    which would make the sentence checks below pass over an empty inbox."""
    from jim import mailer
    sent: list[str] = []
    monkeypatch.setattr(mailer, "configured_transport", lambda: "smtp")
    monkeypatch.setattr(mailer, "deliver",
                        lambda to, subject, body: sent.append(body))
    return sent


def test_the_trip_reaches_the_tier_the_arming_asked_for(client):
    """Behaviour-preserving, and the reason this round is safe to make. The
    ladder has to answer what the `if` answered, or somebody's standing
    instruction quietly changed underneath them."""
    assert crashwatch.as_alarm(_tripped(client, ems=False))["tier"] \
        == "notify_contact"
    assert crashwatch.as_alarm(_tripped(client, ems=True))["tier"] \
        == "emergency_services"


def test_the_unticked_trip_says_a_floor_was_cut(client):
    """The difference between the old `if` and the ladder. A critical finding
    floors at notify_contact and bases above it; the arming is what holds it
    down. Saying so is what turns a lowered tier into a handoff rather than a
    lower-sounding assessment."""
    row = crashwatch.as_alarm(_tripped(client, ems=False))
    assert row["clipped_by_ceiling"] is True, (
        "the trip was capped by what the person authorized and the row does "
        "not say so — a lower tier with no stated reason reads as a milder "
        "emergency")
    assert crashwatch.as_alarm(
        _tripped(client, ems=True))["clipped_by_ceiling"] is False


def test_the_decision_can_be_replayed(client):
    """An escalation nobody can reconstruct is an escalation nobody can
    defend. Every other path in this product records its steps."""
    user = _tripped(client, ems=False)
    rows = db.connect().execute(
        "SELECT detail FROM events WHERE user_id=? AND type='crash_watch'"
        " AND severity='alert'", (user,)).fetchall()
    assert rows, "the trip left no alert event"
    detail = json.loads(rows[-1]["detail"])
    assert detail["escalation_path"], "the trip recorded no reasoning"
    assert detail["tier"] == "notify_contact"
    # Not a fixed step count: the ladder's internals are its own business and
    # will change. What must hold is that the record names the rule that
    # decided this outcome, which here is the ceiling.
    assert any("ceiling" in step for step in detail["escalation_path"]), (
        f"nothing in the path explains the tier: {detail['escalation_path']}")


@pytest.mark.parametrize("ems", [True, False])
def test_the_page_tells_the_one_person_who_can_dial(client, posted, ems):
    """The whole of the second finding, on both settings of the box.

    The trusted contact is the only human in this story who can reach a
    dispatcher, and the page is the only thing that reaches *them* — they may
    not have this app at all.
    """
    _tripped(client, ems=ems)
    assert posted, "nothing went out to the trusted contact"
    assert crashwatch.DIAL_YOURSELF in posted[-1], (
        f"the page never says JIM cannot call (ems={ems}):\n{posted[-1]}")


def test_the_ticked_box_is_the_one_that_most_needs_saying(client, posted):
    """A dispatch *request* relayed to connected systems is the thing that
    most looks like a call having been placed. The page has to separate the
    request from the call in the same breath."""
    _tripped(client, ems=True)
    assert crashwatch.WHY_DIAL[True] in posted[-1]
    assert crashwatch.WHY_DIAL[True] != crashwatch.WHY_DIAL[False], (
        "both settings of the box are explained with the same sentence, so "
        "the explanation is not explaining anything")


def test_the_re_page_carries_it_too(client, posted):
    """Escalating means the one page is not the only page. A second page that
    dropped the sentence would be the first page's honesty expiring."""
    user = _tripped(client, ems=False)
    posted.clear()
    crashwatch.escalate_alarm(user)
    assert posted and crashwatch.DIAL_YOURSELF in posted[-1]


def test_every_row_on_the_queue_says_it_not_only_the_crash_watch(client):
    """One answering surface, two producers. A beacon alarm's live response
    has carried this to the *stranger* since it shipped; the list the carer
    reads showed a tier and never mentioned the ceiling that made it. Same
    alarm, two readers, one of them told."""
    user = _tripped(client, ems=False)
    # Through the doors, because a beacon alarm raised any other way is not
    # the row a carer actually reads. `enroll` leaves the user's token on the
    # client, and the scan itself is deliberately uncredentialed.
    beacon = client.post(f"/users/{user}/beacons",
                         json={"label": "fridge door"}).json()
    client.post(f"/c/{beacon['id']}/alarm", json={"message": "he's down"})
    rows = client.get(f"/users/{user}/alarms").json()
    assert len(rows) == 2, f"the beacon alarm did not reach the queue: {rows}"
    for row in rows:
        assert row["call_emergency_services_yourself"] is True, (
            f"{row.get('kind', 'beacon')} alarm on the queue does not tell "
            "the reader to dial, and nothing in this product can dial")


def test_the_sentence_reaches_a_client_that_never_heard_of_the_field(client):
    """It rides in `messages` as well as in a field of its own.

    `messages` is the one shape every shell already decodes — plain strings,
    a lesson this queue learned the hard way when a `{from, text}` row would
    have failed the whole alarm-list decode on every phone. A shell built
    before this round still shows the sentence.
    """
    row = crashwatch.as_alarm(_tripped(client, ems=True))
    assert any(crashwatch.DIAL_YOURSELF in m for m in row["messages"]), (
        "the sentence exists only in a new field, so an older shell renders "
        "the alarm without it")
    assert all(isinstance(m, str) for m in row["messages"])


def test_the_dial_sentence_is_not_pinned_to_one_country():
    """"911" is a US number. The estate's other honest sentences say "your
    local emergency number" for exactly this reason."""
    assert "911" not in crashwatch.DIAL_YOURSELF
    assert "local emergency number" in crashwatch.DIAL_YOURSELF


def test_the_tier_is_computed_in_one_place(client, monkeypatch):
    """`as_alarm` and `_trip` must not each decide.

    There is no `tier` column — the queue recomputes on every read while the
    record is written once, and a second place deciding is exactly how those
    two drift apart. The drift would only surface during an emergency.

    Driven rather than read off the source: an earlier version of this guard
    searched both function bodies for the string "emergency_services" and
    failed on `call_emergency_services_yourself` and on the honest
    dispatch-request note — both of which name the tier for good reasons.
    Moving the shared decision and watching both surfaces move with it cannot
    be fooled by a substring.
    """
    real = crashwatch._decide
    monkeypatch.setattr(crashwatch, "_decide", lambda row: dict(
        real(row), tier="check_in", clipped_by_ceiling=True,
        path=["pinned by a test"]))
    user = _tripped(client, ems=True)
    assert crashwatch.as_alarm(user)["tier"] == "check_in", (
        "the queue computes its own tier, so it can disagree with the record")
    row = db.connect().execute(
        "SELECT detail FROM events WHERE user_id=? AND type='crash_watch'"
        " AND severity='alert'", (user,)).fetchone()
    assert json.loads(row["detail"])["tier"] == "check_in", (
        "the trip records a tier it did not get from the shared decision")
    assert "_decide(" in inspect.getsource(crashwatch._trip)


def test_the_dial_sentence_is_the_estates_wording():
    """Three surfaces say this in three registers — the stranger's page, the
    contact's message, the carer's app. They should not say three different
    things."""
    for text in (beacons.NOTE_SENT, beacons.NOTE_UNSENT,
                 crashwatch.DIAL_YOURSELF):
        assert "local emergency number" in text


def test_the_ladder_still_has_a_ceiling_to_lend():
    """The crash watch borrows `ceiling`, which was written for a caller with
    no standing. This uses it for nearly the opposite reason — a caller who
    left standing instructions — and the guard is here because a round that
    removed the ceiling for beacons would silently uncap the collapse path."""
    out = escalation.decide("critical", "balanced",
                            ceiling=crashwatch.UNTICKED_CEILING)
    assert out["tier"] == crashwatch.UNTICKED_CEILING
    assert out["clipped_by_ceiling"] is True
    assert out["call_emergency_services_yourself"] is True
