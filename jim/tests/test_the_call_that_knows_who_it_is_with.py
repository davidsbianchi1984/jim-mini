"""A call with a name on it, learned from a book the person filled in.

The field ask, in its own words: *the person they may be talking to may
already be in their friends list, and an agent monitoring you making a phone
call outbound will know who you're calling the moment you're calling, so all
of that can be set up as it's happening.* And the case that carries it: *your
user is on the phone with their mom, who doesn't have her own agent, and the
mother gives them a date and time to be somewhere — so the user doesn't
forget, it was being monitored and saved and stored under mom in the
calendar.*

    asked     who is on the other end of this call
    mattered  did we learn it from something this person already had

## What these guards hold

* recognition reads **this person's own book** and nothing else — no
  directory, no other person's contacts, and nothing a call carried in;
* the far side's number is still never stored, and a call matching nobody
  leaves exactly as little behind as it did before any of this existed;
* the book hands back names, never numbers;
* the guardians' link opens at dial time where everything already permitted
  it, and a call that cannot open one carries on without one — a phone call
  is not the place to raise an error about a permit;
* what a call leaves behind is a thing to be done at a time, and there is
  nowhere to put anything else;
* and nothing is heard before the notice, which the appointment path is
  bound by too.
"""

from __future__ import annotations

import inspect
from datetime import datetime, timedelta, timezone

import pytest

from jim import contacts, db, liaison, life, oncall, permits

from .conftest import enroll

MOM = "+1 555 010 2233"


def _soon() -> str:
    """A time the schedule will still accept tomorrow.

    A date typed into a test is in the future only until that date arrives;
    `schedule.book` refuses a moment that has passed, so a literal here is a
    guard with an expiry on it. This one is always a week out.
    """
    return (datetime.now(timezone.utc) + timedelta(days=7)).replace(
        hour=14, minute=30, second=0, microsecond=0).isoformat()


def _with_mom(client, granted=True):
    """One enrolled person who let the agent see their phone's contacts, and
    whose book has their mother in it with no guardian on the other end —
    which is most of anybody's address book."""
    user_id = enroll(client)
    head = {"authorization": client.headers["authorization"]}
    if granted:
        life.set_source(user_id, contacts.SOURCE, True)
        contacts.sync(user_id, [{"name": "Mom", "number": MOM}])
    return user_id, head


# --------------------------------------------------------------------------
# It is recognised from a book the person filled in, or not at all.
# --------------------------------------------------------------------------

def test_a_number_in_the_book_puts_a_name_on_the_call(client):
    user_id, _ = _with_mom(client)
    call = oncall.open(user_id, "speaker", number=MOM)
    assert call["with_name"] == "Mom"


def test_the_shape_it_was_written_in_does_not_decide(client):
    """`+1 555 010 2233` and `(555) 010-2233` are the same person, because
    the way somebody wrote a number down is not a fact about who they are."""
    user_id, _ = _with_mom(client)
    for written in ("(555) 010-2233", "555.010.2233", "+1-555-010-2233"):
        assert oncall.open(user_id, "speaker",
                           number=written)["with_name"] == "Mom"


def test_a_stranger_is_still_a_stranger(client):
    """The ordinary case: most numbers anybody rings are in nobody's book,
    and the call keeps exactly what it kept before this module existed."""
    user_id, _ = _with_mom(client)
    call = oncall.open(user_id, "speaker", number="+1 555 999 0000")
    assert call["with_name"] is None
    assert db.connect().execute(
        "SELECT contact_id FROM assisted_calls WHERE id=?",
        (call["id"],)).fetchone()["contact_id"] is None


def test_one_persons_book_does_not_answer_for_another(client):
    """The rule the whole module rests on. A directory everybody shares is
    the thing this deliberately is not."""
    _, _ = _with_mom(client)
    stranger = enroll(client)
    assert contacts.whose(stranger, MOM) is None
    assert oncall.open(stranger, "speaker", number=MOM)["with_name"] is None


def test_nothing_a_call_carried_is_written_into_the_book(client):
    """Recognition never grows the book. A number that rang somebody is read
    and dropped — the asymmetry this module is built on."""
    user_id, _ = _with_mom(client)
    before = len(contacts.book(user_id))
    oncall.open(user_id, "speaker", number="+1 555 999 0000")
    assert len(contacts.book(user_id)) == before


def test_the_far_sides_number_is_still_not_stored(client):
    """`assisted_calls` says no number is kept, and that stays true: what the
    row gained is the id of one of this person's own contacts."""
    user_id, _ = _with_mom(client)
    call = oncall.open(user_id, "speaker", number=MOM)
    row = dict(db.connect().execute(
        "SELECT * FROM assisted_calls WHERE id=?", (call["id"],)).fetchone())
    for value in row.values():
        assert "0102233" not in str(value or "")


def test_the_book_hands_back_names_and_not_numbers(client):
    """A book that returns its numbers on every read ends up in a log, a
    screenshot and a support ticket. Nothing here needs to display them."""
    user_id, _ = _with_mom(client)
    for row in contacts.book(user_id):
        assert "digits" not in row
        for value in row.values():
            assert "0102233" not in str(value or "")


def test_a_removed_contact_stops_naming_old_calls(client):
    """The name is read at the last moment rather than frozen onto the call,
    so removing somebody does not leave their name in a table nobody is
    looking at."""
    user_id, _ = _with_mom(client)
    oncall.open(user_id, "speaker", number=MOM)
    assert oncall.history(user_id)[0]["with_name"] == "Mom"
    contacts.sync(user_id, [])
    assert oncall.history(user_id)[0]["with_name"] is None


# --------------------------------------------------------------------------
# The guardians find each other at dial time, where everything already said
# they may.
# --------------------------------------------------------------------------

def _two_who_know_each_other(client):
    a = enroll(client)
    a_head = {"authorization": client.headers["authorization"]}
    b = enroll(client)
    b_head = {"authorization": client.headers["authorization"]}
    client.post(f"/circle/{b}/contacts", json={"other_id": a}, headers=b_head)
    client.post(f"/circle/{a}/contacts", json={"other_id": b}, headers=a_head)
    for who, head in ((a, a_head), (b, b_head)):
        client.put(f"/engaged/{who}/permits/{liaison.PERMIT}",
                   json={"granted": True}, headers=head)
    life.set_source(a, contacts.SOURCE, True)
    contacts.sync(a, [{"name": "Sam", "number": MOM, "jim_user_id": b}])
    return a, b


def test_the_link_opens_the_moment_the_call_does(client):
    """*All of that can be set up as it's happening* — rather than waiting
    for somebody to remember to press something mid-conversation."""
    a, b = _two_who_know_each_other(client)
    call = oncall.open(a, "speaker", number=MOM)
    assert call["liaison"], "no link opened at dial time"
    assert liaison.summary(call["liaison"], a)["with"] == b


def test_a_contact_with_no_guardian_opens_nothing(client):
    """Mom's case, and most of the book's. There is nothing on the other end
    to link to, and that is not a failure."""
    user_id, _ = _with_mom(client)
    assert oncall.open(user_id, "speaker", number=MOM)["liaison"] is None


def test_a_permit_that_is_off_does_not_break_the_call(client):
    """A phone call is not the place to raise an error about a permit. The
    link does not open, the call carries on, and the person can turn it on
    afterwards and open one by hand."""
    a, _ = _two_who_know_each_other(client)
    a_head = {"authorization": client.headers["authorization"]}
    permits.set_grant(a, liaison.PERMIT, False)
    call = oncall.open(a, "speaker", number=MOM)
    assert call["liaison"] is None
    assert call["with_name"] == "Sam"


def test_dial_time_does_not_invent_a_second_gate(client):
    """`liaison.open` already refuses a link that is not mutual or not
    permitted, so this catches its refusals rather than re-testing them —
    two copies of one rule is how the two drift apart."""
    source = inspect.getsource(oncall._link_at_dial_time)
    assert "liaison.open(" in source
    assert "_mutual" not in source, (
        "dial time is checking mutuality itself instead of letting "
        "`liaison.open` be the one place that decides it")


def test_the_link_is_not_labelled_with_the_contacts_name(client):
    """What one person calls their mother is not a label to hand to somebody
    else's guardian — and the far side reads their own half of this link."""
    a, b = _two_who_know_each_other(client)
    call = oncall.open(a, "speaker", number=MOM)
    assert "Sam" not in liaison.summary(call["liaison"], b)["about"]


# --------------------------------------------------------------------------
# What the call leaves behind is a thing to be done, and nothing else.
# --------------------------------------------------------------------------

def test_the_appointment_is_what_survives_the_call(client):
    """The mom case, end to end: she names a time, and what is kept is the
    appointment rather than the conversation."""
    user_id, _ = _with_mom(client)
    call = oncall.open(user_id, "speaker", number=MOM)
    oncall.announced(call["id"])
    made = oncall.remember(call["id"], "Take Mom to the eye clinic",
                           _soon())
    assert made["from_name"] == "Mom"
    assert oncall.left_behind(user_id, call["id"])[0]["title"] == (
        "Take Mom to the eye clinic")


def test_it_lands_in_the_calendar_everything_else_reads(client):
    """Not a private list of call outcomes — the appointment goes where the
    person's appointments already are, or it is a reminder they never see."""
    from jim import schedule
    user_id, _ = _with_mom(client)
    call = oncall.open(user_id, "speaker", number=MOM)
    oncall.announced(call["id"])
    oncall.remember(call["id"], "Eye clinic", _soon())
    assert [a["title"] for a in schedule.upcoming(user_id)] == ["Eye clinic"]


def test_nothing_is_booked_from_a_call_that_never_announced(client):
    """The ordering `may_listen` enforces reaches here too: a call that never
    told the far side it was listening cannot have heard a date."""
    user_id, _ = _with_mom(client)
    call = oncall.open(user_id, "speaker", number=MOM)
    with pytest.raises(oncall.NotAnnounced):
        oncall.remember(call["id"], "Eye clinic", _soon())


def test_there_is_nowhere_to_put_what_was_said(client):
    """The rule this half is built on. A column for the conversation would be
    the beginning of a different product, and the guard is the same one
    `test_two_guardians_working_together` makes about the link."""
    columns = {r[1] for r in db.connect().execute(
        "PRAGMA table_info(appointments)").fetchall()}
    for theirs in ("transcript", "summary", "audio", "recording", "said"):
        assert theirs not in columns
    call_columns = {r[1] for r in db.connect().execute(
        "PRAGMA table_info(assisted_calls)").fetchall()}
    assert "number" not in call_columns
    assert "transcript" not in call_columns


# --------------------------------------------------------------------------
# The grant, which is the part that is mostly about other people.
# --------------------------------------------------------------------------

def test_nothing_sees_the_book_until_somebody_grants_it(client):
    """Off until turned on, like anything that reaches people who did not
    choose it. `jim/monitors.py` makes the same argument about a hall
    camera; an address book is the same shape and a larger number of
    strangers."""
    user_id, _ = _with_mom(client, granted=False)
    with pytest.raises(contacts.NotGranted):
        contacts.sync(user_id, [{"name": "Mom", "number": MOM}])
    with pytest.raises(contacts.NotGranted):
        contacts.book(user_id)


def test_an_ungranted_call_simply_has_no_name_on_it(client):
    """A phone call is not the place to raise about a grant. Without it the
    call carries what it always carried, which is nobody's name."""
    user_id, _ = _with_mom(client, granted=False)
    assert oncall.open(user_id, "speaker", number=MOM)["with_name"] is None


def test_withdrawing_the_grant_drops_the_book(client):
    """Not "stop syncing" — drop it. A copy kept after somebody said stop is
    the entire objection to holding other people's details, and it has to be
    true rather than intended."""
    user_id, _ = _with_mom(client)
    assert contacts.book(user_id)
    life.set_source(user_id, contacts.SOURCE, False)
    assert db.connect().execute(
        "SELECT COUNT(*) AS n FROM contacts WHERE user_id=?",
        (user_id,)).fetchone()["n"] == 0


def test_one_switch_does_it_and_not_two(client):
    """The person turns off what the agent may see, and the book goes. They
    do not also have to find a second control that empties it."""
    source = inspect.getsource(life.set_source)
    assert "contacts.withdrawn(" in source


def test_a_sync_replaces_rather_than_merges(client):
    """The device's book is the truth. A merge quietly keeps people somebody
    deleted from their phone months ago — the copy-left-behind problem in
    slow motion."""
    user_id, _ = _with_mom(client)
    contacts.sync(user_id, [{"name": "Dad", "number": "+1 555 010 9999"}])
    assert [c["name"] for c in contacts.book(user_id)] == ["Dad"]


def test_half_a_row_is_skipped_and_the_rest_still_lands(client):
    """Every real address book has rows with no number and numbers with no
    name. Refusing the whole sync over one would leave somebody with no book
    at all."""
    user_id, _ = _with_mom(client)
    out = contacts.sync(user_id, [
        {"name": "Mom", "number": MOM},
        {"name": "No number"},
        {"number": "+1 555 010 4444"},
    ])
    assert out == {"held": 1, "skipped": 2, "sealed": False}


def test_one_function_is_the_only_door_to_the_book():
    """The argument `monitors.may_sense` makes for a camera and
    `oncall.may_listen` makes for a call.

    Asked as *before it touches anything*, rather than *within the first 900
    characters*. The window version passed for two releases and then failed on
    a round that only made `sync`'s docstring longer — it was measuring prose,
    and a guard that a paragraph can break is a guard that a paragraph can
    also satisfy.
    """
    source = inspect.getsource(contacts)
    touches = ("_rows(", "db.connect()", "_clear(")
    for reader in ("def book", "def sync"):
        body = source[source.index(reader):]
        body = body[:body.index("\ndef ", 1)] if "\ndef " in body[1:] else body
        assert "allowed(user_id)" in body, (
            f"`{reader}` reads the book without asking `allowed`")
        door = body.index("allowed(user_id)")
        first = min((body.index(t) for t in touches if t in body),
                    default=len(body))
        assert door < first, (
            f"`{reader}` touches the book before asking `allowed`")
