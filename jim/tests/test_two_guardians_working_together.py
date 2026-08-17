"""Two guardians talking to each other, quietly, on behalf of two people.

The field ask, in its own words: *both parties have profiles and both could be
using them simultaneously, and then those two collaborate together — capable
of collaborating silently in the background. They may not be able to share
information through the line like the users can with their voice, but they
know both parties' IDs, and can reach out to each other in other ways than the
phone, via online.*

    asked     can two guardians work together
    mattered  is each one still working for its own person

## What these guards hold

* the link forms only where both people already had the other stored, which is
  what stops a stranger's guardian reaching yours;
* it is never spoken on the line — it carries what one guardian told the
  other, over the network, and nothing of the call itself;
* each person can read their **own** guardian's half afterwards, and only
  theirs. Two agents negotiating on a channel neither human can inspect are
  two principals with counsel who never report back;
* nothing is said across it without the permit, which is `asked`;
* the link closes when the call does, unless a task **both sides agreed to**
  is holding it open — one person cannot extend a channel to somebody else's
  guardian on their own say-so, though either can end it alone;
* and a closed link stays in the list, because what two guardians did on
  somebody's behalf is not something to tidy away.
"""

from __future__ import annotations

import inspect

import pytest

from jim import circle, liaison, permits

from .conftest import enroll, user_header


def _two(client):
    """Two enrolled people, mutual contacts, both letting their guardian
    speak. Mutual through the real path: one direction is an invitation and
    the second is what makes them contacts."""
    a = enroll(client)
    a_head = {"authorization": client.headers["authorization"]}
    b = enroll(client)
    b_head = {"authorization": client.headers["authorization"]}

    client.post(f"/circle/{b}/contacts", json={"other_id": a},
                headers=b_head)
    client.post(f"/circle/{a}/contacts", json={"other_id": b},
                headers=a_head)
    for who, head in ((a, a_head), (b, b_head)):
        client.put(f"/engaged/{who}/permits/{liaison.PERMIT}",
                   json={"granted": True}, headers=head)
    return a, a_head, b, b_head


def _open(client, a, a_head, b, about="the wage conversation"):
    r = client.post(f"/liaisons/{a}", json={"other_id": b, "about": about},
                    headers=a_head)
    assert r.status_code == 201, r.text
    return r.json()


# --------------------------------------------------------------------------
# It forms only where both sides already knew each other.
# --------------------------------------------------------------------------

def test_one_sided_contact_reaches_nothing(client):
    """The rule this module is built on. The alternative is a stranger's
    guardian calling yours on the strength of having your number."""
    a = enroll(client)
    a_head = {"authorization": client.headers["authorization"]}
    b = enroll(client)
    client.post(f"/circle/{a}/contacts", json={"other_id": b},
               headers=a_head)
    client.put(f"/engaged/{a}/permits/{liaison.PERMIT}",
               json={"granted": True}, headers=a_head)

    r = client.post(f"/liaisons/{a}", json={"other_id": b}, headers=a_head)
    assert r.status_code == 409, r.text
    assert "each other's contacts" in r.text


def test_mutual_contacts_can_open_one(client):
    a, a_head, b, _ = _two(client)
    link = _open(client, a, a_head, b)
    assert link["running"] is True
    assert link["with"] == b


def test_the_gate_is_the_one_the_circle_already_had(client):
    """`circle._mutual` is the check, not a second graph built here: an
    invitation is one direction, two make contacts, and either side deleting
    theirs closes the door for both."""
    assert "circle._mutual" in inspect.getsource(liaison.open)


def test_nothing_is_said_without_the_permit(client):
    """Saying things about somebody to another person's guardian is `asked`,
    never assumed by opening a session."""
    a, a_head, b, b_head = _two(client)
    link = _open(client, a, a_head, b)
    client.put(f"/engaged/{a}/permits/{liaison.PERMIT}",
               json={"granted": False}, headers=a_head)

    r = client.post(f"/liaisons/{a}/{link['id']}/said",
                    json={"body": "he is underpaid for the role"},
                    headers=a_head)
    assert r.status_code == 403, r.text


# --------------------------------------------------------------------------
# Silent, and readable afterwards by the person it works for.
# --------------------------------------------------------------------------

def test_each_person_reads_their_own_guardians_half(client):
    """*What my agent disclosed* is a thing somebody is entitled to. *What
    yours told mine* is not theirs to read."""
    a, a_head, b, b_head = _two(client)
    link = _open(client, a, a_head, b)
    client.post(f"/liaisons/{a}/{link['id']}/said",
                json={"body": "he has been at the same rate for three years"},
                headers=a_head)
    client.post(f"/liaisons/{b}/{link['id']}/said",
                json={"body": "the budget review lands in April"},
                headers=b_head)

    mine = client.get(f"/liaisons/{a}/{link['id']}", headers=a_head).json()
    assert mine["said_by_mine"] == [
        "he has been at the same rate for three years"]
    assert mine["said_to_mine"] == ["the budget review lands in April"]

    theirs = client.get(f"/liaisons/{b}/{link['id']}", headers=b_head).json()
    assert theirs["said_by_mine"] == ["the budget review lands in April"]


def test_a_stranger_cannot_read_a_link(client):
    a, a_head, b, _ = _two(client)
    link = _open(client, a, a_head, b)
    outsider = enroll(client)
    head = {"authorization": client.headers["authorization"]}
    r = client.get(f"/liaisons/{outsider}/{link['id']}", headers=head)
    assert r.status_code == 403, r.text


def test_the_link_carries_no_audio_and_no_transcript():
    """It is never spoken on the line. What it holds is what one guardian
    told the other, and a column for the call itself would be the beginning
    of a different product."""
    from jim import db
    columns = {r[1] for r in db.connect().execute(
        "PRAGMA table_info(liaisons)").fetchall()}
    for theirs in ("audio", "transcript", "recording", "call_audio"):
        assert theirs not in columns


# --------------------------------------------------------------------------
# It lives as long as the work does.
# --------------------------------------------------------------------------

def test_a_link_with_no_task_closes_with_the_call(client):
    """Two guardians that had nothing to finish do not stay in touch."""
    a, a_head, b, _ = _two(client)
    link = _open(client, a, a_head, b)
    out = client.delete(f"/liaisons/{a}/{link['id']}?why=call_ended",
                        headers=a_head).json()
    assert out["running"] is False
    assert out["ended_because"] == "call_ended"


def test_a_task_both_agreed_keeps_it_open_past_the_call(client):
    """What extends the link is not an agreement to stay connected. It is a
    piece of work with an end in it — that both sides said yes to."""
    a, a_head, b, b_head = _two(client)
    link = _open(client, a, a_head, b)
    client.put(f"/liaisons/{a}/{link['id']}/task",
               json={"task": "send the revised figures by Friday"},
               headers=a_head)
    agreed = client.put(f"/liaisons/{b}/{link['id']}/agreed",
                        headers=b_head).json()
    assert agreed["holds_it_open"] is True

    out = client.delete(f"/liaisons/{a}/{link['id']}?why=call_ended",
                        headers=a_head).json()
    assert out["running"] is True
    assert out["task"] == "send the revised figures by Friday"


def test_one_side_alone_cannot_keep_the_link_open(client):
    """The rule the first version of this got wrong.

    A task was one column, written by either party, and the call ending
    checked only that it was set — so one person could hold a channel to
    somebody else's guardian open past the conversation that justified it, on
    their own say-so. That is the same shape as the one-sided contact this
    module refuses at the door, and refusing a stranger there while allowing
    this is the door mattering less than it looks.
    """
    a, a_head, b, _ = _two(client)
    link = _open(client, a, a_head, b)
    named = client.put(f"/liaisons/{a}/{link['id']}/task",
                       json={"task": "send the revised figures by Friday"},
                       headers=a_head).json()
    # Proposing is this side's own yes, and only that.
    assert named["you_agreed"] is True
    assert named["they_agreed"] is False
    assert named["holds_it_open"] is False

    out = client.delete(f"/liaisons/{a}/{link['id']}?why=call_ended",
                        headers=a_head).json()
    assert out["running"] is False, "one person extended it alone"
    assert out["ended_because"] == "call_ended"


def test_the_proposed_task_is_not_lost_when_the_call_ends_it(client):
    """A task nobody agreed to is still real work somebody proposed. It stays
    on the link to be read; it just was not holding anything open."""
    a, a_head, b, _ = _two(client)
    link = _open(client, a, a_head, b)
    client.put(f"/liaisons/{a}/{link['id']}/task",
               json={"task": "send the revised figures"}, headers=a_head)
    out = client.delete(f"/liaisons/{a}/{link['id']}?why=call_ended",
                        headers=a_head).json()
    assert out["task"] == "send the revised figures"


def test_re_wording_the_task_drops_the_other_sides_agreement(client):
    """Agreeing to *book the venue* is not agreeing to *run the wedding*.

    The agreement is recorded against the wording, so this falls out of the
    key rather than depending on somebody remembering to clear a flag.
    """
    a, a_head, b, b_head = _two(client)
    link = _open(client, a, a_head, b)
    client.put(f"/liaisons/{a}/{link['id']}/task",
               json={"task": "book the venue"}, headers=a_head)
    client.put(f"/liaisons/{b}/{link['id']}/agreed", headers=b_head)

    widened = client.put(f"/liaisons/{a}/{link['id']}/task",
                         json={"task": "run the whole wedding"},
                         headers=a_head).json()
    assert widened["they_agreed"] is False
    assert widened["holds_it_open"] is False

    out = client.delete(f"/liaisons/{a}/{link['id']}?why=call_ended",
                        headers=a_head).json()
    assert out["running"] is False


def test_there_is_nothing_to_agree_to_before_a_task_is_named(client):
    """*Nothing here to agree to* and *that link is gone* are different
    things to be told."""
    a, a_head, b, b_head = _two(client)
    link = _open(client, a, a_head, b)
    r = client.put(f"/liaisons/{b}/{link['id']}/agreed", headers=b_head)
    assert r.status_code == 422, r.text
    assert "names the work first" in r.text


@pytest.mark.parametrize("call", ("task", "agreed"))
def test_a_closed_link_answers_the_same_way_everywhere(client, call):
    """One status for one condition.

    `say` answered 404 for a closed link from the day it was written. When
    naming a task and agreeing to one gained the same check they inherited
    their route's 422 — which is the status for *you did not say what the
    task is*, a different thing entirely, and the status is all a reader has
    to tell them apart.

    Naming a task on a closed link used to do something worse than answer the
    wrong number: the update said `AND ended_at IS NULL`, so it quietly
    changed nothing and handed back a summary that looked like success.
    """
    a, a_head, b, _ = _two(client)
    link = _open(client, a, a_head, b)
    client.delete(f"/liaisons/{a}/{link['id']}?why=stopped", headers=a_head)

    r = client.put(f"/liaisons/{a}/{link['id']}/{call}",
                   json={"task": "send the figures"}, headers=a_head)
    assert r.status_code == 404, r.text
    assert "closed" in r.text


def test_the_closed_refusal_is_its_own_type():
    """A subclass rather than a new exception, so a route that has not been
    taught the difference still catches it as `NoSuchLink`."""
    assert issubclass(liaison.Closed, liaison.NoSuchLink)


def test_agreeing_takes_no_wording_of_its_own():
    """A second party passing their own text would be proposing, not
    agreeing — and the link could then be held open by two sentences that
    only looked like one agreement."""
    assert "task" not in inspect.signature(liaison.agree).parameters


def test_a_stranger_cannot_agree_to_somebody_elses_task(client):
    a, a_head, b, _ = _two(client)
    link = _open(client, a, a_head, b)
    client.put(f"/liaisons/{a}/{link['id']}/task",
               json={"task": "send the figures"}, headers=a_head)
    outsider = enroll(client)
    head = {"authorization": client.headers["authorization"]}
    r = client.put(f"/liaisons/{outsider}/{link['id']}/agreed", headers=head)
    assert r.status_code == 403, r.text


def test_a_person_can_always_stop_it(client):
    """A task you can see is a task you can end early — the difference
    between a link that dies when the work is done and one you can kill
    because you changed your mind."""
    a, a_head, b, _ = _two(client)
    link = _open(client, a, a_head, b)
    client.put(f"/liaisons/{a}/{link['id']}/task",
               json={"task": "send the revised figures"}, headers=a_head)

    out = client.delete(f"/liaisons/{a}/{link['id']}?why=stopped",
                        headers=a_head).json()
    assert out["running"] is False
    assert out["ended_because"] == "stopped"


def test_the_call_ending_cannot_close_what_the_task_holds():
    """Checked rather than trusted: the whole point of the task is that the
    call ending is not the end of it — and the whole point of the agreement
    is that one person's task is not enough to reach that."""
    source = inspect.getsource(liaison.close)
    assert 'why == "call_ended"' in source
    assert 'row["task"]' in source
    assert "_both_agreed(row)" in source


def test_neither_side_can_write_the_others_agreement(client):
    """The guard under the rule. Agreement is a row per side, so the only
    way to reach both is for both to have said so — there is no path that
    writes somebody else's."""
    a, a_head, b, b_head = _two(client)
    link = _open(client, a, a_head, b)
    client.put(f"/liaisons/{a}/{link['id']}/task",
               json={"task": "send the figures"}, headers=a_head)
    # a proposes, a agrees again, a agrees once more: still one side.
    client.put(f"/liaisons/{a}/{link['id']}/agreed", headers=a_head)
    out = client.put(f"/liaisons/{a}/{link['id']}/agreed",
                     headers=a_head).json()
    assert out["holds_it_open"] is False

    from jim import db
    rows = db.connect().execute(
        "SELECT user_id FROM liaison_task_agreed WHERE link_id=?",
        (link["id"],)).fetchall()
    assert [r["user_id"] for r in rows] == [a]


def test_nothing_is_said_across_a_closed_link(client):
    a, a_head, b, _ = _two(client)
    link = _open(client, a, a_head, b)
    client.delete(f"/liaisons/{a}/{link['id']}?why=stopped", headers=a_head)
    r = client.post(f"/liaisons/{a}/{link['id']}/said",
                    json={"body": "one more thing"}, headers=a_head)
    assert r.status_code == 404, r.text


# --------------------------------------------------------------------------
# What is still running.
# --------------------------------------------------------------------------

def test_the_list_answers_which_are_still_going(client):
    """The question the task window asks about everything else this product
    runs, and each row says why it is still open."""
    a, a_head, b, _ = _two(client)
    kept = _open(client, a, a_head, b, about="the wage conversation")
    client.put(f"/liaisons/{a}/{kept['id']}/task",
               json={"task": "send the revised figures"}, headers=a_head)
    done = _open(client, a, a_head, b, about="the school run")
    client.delete(f"/liaisons/{a}/{done['id']}?why=call_ended",
                  headers=a_head)

    rows = client.get(f"/liaisons/{a}", headers=a_head).json()
    assert [r["running"] for r in rows] == [True, False], "open ones first"
    assert rows[0]["task"] == "send the revised figures"


def test_a_closed_link_is_not_tidied_away(client):
    """What two guardians did on somebody's behalf is not something to
    delete."""
    a, a_head, b, _ = _two(client)
    link = _open(client, a, a_head, b)
    client.delete(f"/liaisons/{a}/{link['id']}?why=call_ended",
                  headers=a_head)
    rows = client.get(f"/liaisons/{a}", headers=a_head).json()
    assert [r["id"] for r in rows] == [link["id"]]


@pytest.mark.parametrize("ending", liaison.ENDINGS)
def test_every_ending_is_a_word_somebody_can_read(ending):
    """*The call ended* and *somebody stopped it* are different things to
    read months later, so the column carries words rather than a flag."""
    assert ending and ending.replace("_", "").isalpha()
