"""Everything this guardian has running, in one place.

The field ask, said twice: *users will always have that task window — which
agent is running, which tasks are still running.*

    asked     which agent is running, and which tasks are still going
    mattered  can somebody see all of it without knowing where to look

Every piece was answerable and none of it together: links had a list, the
monitor roster had its own, the mic knew about channel 2, the call table knew
about calls, and the engagement table knew whether an agent was mid-session.
Five readers, five screens, and no answer to *what is my guardian doing right
now* — the question you ask precisely when you do not know where to look.

## What these guards hold

* the window gathers all five, so a person reads one thing rather than five;
* it reports what is **still going**, and an errand — which opens, studies and
  finishes inside one call — is reported as what it did today instead, because
  a window whose job is to be believed about what is running must not list
  something finished as running;
* today's errands are counted against the same day boundary as the budget
  beside them, so the list and the count cannot disagree;
* a proposed task and an agreed one read differently, because only one of them
  survives the call;
* it composes no prose. `kind` and `why` are closed sets a shell says in the
  reader's language, and the only free text is what the person wrote
  themselves;
* and it is a reader. A window over everything that could also act on
  everything would be the widest door in the product.
"""

from __future__ import annotations

import inspect

from jim import errands, liaison, underway

from .conftest import enroll


def _two(client):
    """Two enrolled people, mutual contacts, both letting their guardian
    speak — the same real path the liaison round uses."""
    a = enroll(client)
    a_head = {"authorization": client.headers["authorization"]}
    b = enroll(client)
    b_head = {"authorization": client.headers["authorization"]}
    client.post(f"/circle/{b}/contacts", json={"other_id": a}, headers=b_head)
    client.post(f"/circle/{a}/contacts", json={"other_id": b}, headers=a_head)
    for who, head in ((a, a_head), (b, b_head)):
        client.put(f"/engaged/{who}/permits/{liaison.PERMIT}",
                   json={"granted": True}, headers=head)
    return a, a_head, b, b_head


def _window(client, uid, head) -> dict:
    r = client.get(f"/underway/{uid}", headers=head)
    assert r.status_code == 200, r.text
    return r.json()


def _kinds(win) -> list[str]:
    return [row["kind"] for row in win["underway"]]


# --------------------------------------------------------------------------
# Nothing running is an answer, and it is stated rather than implied.
# --------------------------------------------------------------------------

def test_a_quiet_guardian_says_so(client):
    """*Nothing is running* is the answer a person most wants stated plainly.
    Four shells each deriving it from an empty list is how one of them ends
    up showing a bare heading over nothing."""
    uid = enroll(client)
    head = {"authorization": client.headers["authorization"]}
    win = _window(client, uid, head)
    assert win["quiet"] is True
    assert win["underway"] == []


def test_quiet_is_false_the_moment_anything_is_running(client):
    a, a_head, b, _ = _two(client)
    client.post(f"/liaisons/{a}", json={"other_id": b}, headers=a_head)
    assert _window(client, a, a_head)["quiet"] is False


# --------------------------------------------------------------------------
# It gathers what was scattered.
# --------------------------------------------------------------------------

def test_the_open_link_is_in_the_window(client):
    a, a_head, b, _ = _two(client)
    client.post(f"/liaisons/{a}", json={"other_id": b, "about": "the wage talk"},
                headers=a_head)
    win = _window(client, a, a_head)
    assert "liaison" in _kinds(win)
    row = next(r for r in win["underway"] if r["kind"] == "liaison")
    assert row["words"] == "the wage talk"


def test_a_closed_link_leaves_the_window(client):
    """The list is what is still going. The link itself is not tidied away —
    `GET /liaisons` still has it — but it has stopped running."""
    a, a_head, b, _ = _two(client)
    link = client.post(f"/liaisons/{a}", json={"other_id": b},
                       headers=a_head).json()
    client.delete(f"/liaisons/{a}/{link['id']}?why=stopped", headers=a_head)

    assert "liaison" not in _kinds(_window(client, a, a_head))
    assert [r["id"] for r in client.get(f"/liaisons/{a}",
                                        headers=a_head).json()] == [link["id"]]


def test_the_agent_mid_session_is_the_literal_which_agent_is_running(client):
    uid = enroll(client)
    head = {"authorization": client.headers["authorization"]}
    r = client.post(f"/engaged/{uid}", json={"area": "health_fitness"},
                    headers=head)
    assert r.status_code in (200, 201), r.text

    win = _window(client, uid, head)
    assert "engaged" in _kinds(win)
    row = next(r for r in win["underway"] if r["kind"] == "engaged")
    assert row["term"] == "health_fitness"


def test_a_switched_on_monitor_is_running_and_an_off_one_is_not(client):
    """The roster is where the whole list lives, off rows included. This
    window is what is sensing."""
    uid = enroll(client)
    head = {"authorization": client.headers["authorization"]}
    roster = client.get(f"/monitors/{uid}", headers=head).json()
    off = next(m for m in roster if not m["on"] and not m["catches_others"])

    assert off["name"] not in [r["term"] for r in
                               _window(client, uid, head)["underway"]]
    r = client.put(f"/monitors/{uid}/{off['name']}", json={}, headers=head)
    assert r.status_code == 200, r.text
    assert off["name"] in [r["term"] for r in
                           _window(client, uid, head)["underway"]]


def test_a_live_call_is_in_the_window_and_says_whether_it_announced(client):
    """`not_announced` is not a footnote. That is the one state in which
    nothing is allowed to listen, so showing it the same as any other live
    call would report listening that is not happening."""
    uid = enroll(client)
    head = {"authorization": client.headers["authorization"]}
    call = client.post(f"/calls/{uid}", json={"route": "speaker"},
                       headers=head).json()

    row = next(r for r in _window(client, uid, head)["underway"]
               if r["kind"] == "call")
    assert row["why"] == "not_announced"

    client.post(f"/calls/{uid}/{call['id']}/announced", headers=head)
    row = next(r for r in _window(client, uid, head)["underway"]
               if r["kind"] == "call")
    assert row["why"] == "announced"


def test_an_ended_call_leaves_the_window(client):
    uid = enroll(client)
    head = {"authorization": client.headers["authorization"]}
    call = client.post(f"/calls/{uid}", json={"route": "speaker"},
                       headers=head).json()
    client.delete(f"/calls/{uid}/{call['id']}", headers=head)
    assert "call" not in _kinds(_window(client, uid, head))


# --------------------------------------------------------------------------
# A proposed task and an agreed one are different things to see.
# --------------------------------------------------------------------------

def test_a_proposed_task_reads_differently_from_an_agreed_one(client):
    """Only one of them survives the call, and somebody reading this window
    to decide whether the link will still be here is owed the difference."""
    a, a_head, b, b_head = _two(client)
    link = client.post(f"/liaisons/{a}", json={"other_id": b},
                       headers=a_head).json()
    client.put(f"/liaisons/{a}/{link['id']}/task",
               json={"task": "send the revised figures"}, headers=a_head)

    row = next(r for r in _window(client, a, a_head)["underway"]
               if r["kind"] == "liaison")
    assert row["why"] == "proposed"
    assert row["words"] == "send the revised figures"

    client.put(f"/liaisons/{b}/{link['id']}/agreed", headers=b_head)
    row = next(r for r in _window(client, a, a_head)["underway"]
               if r["kind"] == "liaison")
    assert row["why"] == "agreed"


# --------------------------------------------------------------------------
# What is running, and what merely happened.
# --------------------------------------------------------------------------

def test_an_errand_is_never_reported_as_running(client):
    """An errand opens, studies and finishes before the call returns. A
    window whose whole job is to be believed about what is running must not
    list something already finished as running."""
    assert "errand" not in underway.KINDS
    source = inspect.getsource(underway.window)
    assert '"today"' in source


def test_todays_errands_and_the_budget_share_a_day_boundary(client):
    """The list and the count beside it cannot be allowed to disagree about
    when today started, so they are spelled the same way."""
    assert "substr(opened_at, 1, 10)" in inspect.getsource(errands.spent_today)
    assert 'db.utcnow()[:10]' in inspect.getsource(underway._errands_today)


def test_the_slice_of_todays_errands_cannot_miss_one(client):
    """Asking the ledger for `DAILY` rows is exactly enough, and not by luck:
    no more than `DAILY` errands can open in a day, so the newest `DAILY`
    rows necessarily contain every one of today's."""
    assert "limit=errands.DAILY" in inspect.getsource(underway._errands_today)


def test_the_window_carries_what_is_left_to_spend(client):
    """A person seeing nothing studied should be able to tell *there was
    nothing worth studying* from *it has spent everything it may spend*."""
    uid = enroll(client)
    head = {"authorization": client.headers["authorization"]}
    win = _window(client, uid, head)
    assert win["spend"] == {"spent_today": 0, "daily": errands.DAILY,
                            "permitted": False}
    assert win["today"] == []


# --------------------------------------------------------------------------
# It composes no prose, and it opens no doors.
# --------------------------------------------------------------------------

def test_every_kind_and_reason_is_a_word_a_shell_can_translate():
    """Closed sets, so a client branches on them and says them in the
    reader's language. An English sentence composed here would arrive in
    English on a Portuguese screen."""
    for word in underway.KINDS + underway.WHYS:
        assert word and word.replace("_", "").isalpha(), word


def test_no_row_carries_a_sentence_this_module_wrote(client):
    """The two text fields are kept apart on purpose: `term` is one of the
    product's own vocabulary words, `words` is what the person wrote. Neither
    is prose from here."""
    a, a_head, b, _ = _two(client)
    client.post(f"/liaisons/{a}", json={"other_id": b, "about": "the wage talk"},
                headers=a_head)
    client.post(f"/calls/{a}", json={"route": "speaker"}, headers=a_head)

    for row in _window(client, a, a_head)["underway"]:
        assert row["kind"] in underway.KINDS
        assert row["why"] in underway.WHYS
        # A sentence would have spaces in it and would not be the person's.
        if row["term"] is not None:
            assert " " not in row["term"], row["term"]


def test_the_window_only_reads(client):
    """A window over everything that could also act on everything would be
    the widest door in the product. One route, and it is a GET."""
    from jim.api import app
    methods = {m for r in app.routes
               if getattr(r, "path", None) == "/underway/{user_id}"
               for m in r.methods}
    assert methods == {"GET"}


def test_it_is_one_read_rather_than_one_per_screen(client):
    """The point of the round. Five sources, gathered where the rule about
    what counts as running is written once."""
    source = inspect.getsource(underway.window)
    for gathered in ("_engaged", "_liaisons", "_calls", "_listening",
                     "_monitors"):
        assert gathered in source


def test_a_stranger_cannot_read_somebody_elses_window(client):
    a, _, _, _ = _two(client)
    outsider = enroll(client)
    head = {"authorization": client.headers["authorization"]}
    r = client.get(f"/underway/{a}", headers=head)
    assert r.status_code == 403, r.text
