"""The condition the autonomy was granted under.

An engaged session acts without asking first. That is a deliberate choice, and
it is defensible for exactly one reason: everything it does is listed with the
way back beside it. Take the trail away and what is left is an assistant with
somebody's credential and no brakes.

    asked     can it be undone
    mattered  can it be undone *by the person it happened to*

So this file checks the promise at three depths, because it can fail at each
one separately and the first two look identical from the outside:

**The registry declares it.** Every acting row carries an `undo` spec or an
`irreversible` reason, and never neither. A row with neither is not a smaller
feature — it is an act that lands on the trail as un-takeable-back with no
sentence saying why, which reads to a person as a bug in the undo button.

**The inverse resolves.** An `undo` naming a route this app does not serve
would build fine, store fine, sit on the trail looking reversible, and fail on
the one press that mattered.

**It actually round-trips.** The two shapes — `remove` and `replace` — are
driven end to end through the real app, because a stored inverse is a claim
and running it is the only thing that makes it true.

## Why `replace` reads before it writes

The value an act overwrites is gone the moment it is overwritten. There is no
way to invert a `PUT` after the fact, so the prior state is read first, and the
act only becomes reversible if that read succeeded. A design that built the
inverse afterwards would produce a trail whose undo buttons restore whatever
the value happens to be now — which is not an undo, it is a no-op wearing one.
"""

from __future__ import annotations

import pytest

from jim import db, engaged
from jim.api import app

from . import clientpaths
from .conftest import enroll, user_header

DOORS = {(method, route.path)
         for route in clientpaths.all_routes(app)
         for method in (getattr(route, "methods", None) or ())}


def _acting() -> list[dict]:
    return [tool for tool in engaged.TOOLS if tool["acts"]]


def test_every_acting_tool_declares_a_way_back_or_says_why_not():
    """Neither is not an option.

    `undo` and `irreversible` are the two honest answers. A row with neither
    is a change that appears on the trail with a disabled button and no
    explanation — indistinguishable, to the person reading it, from the undo
    being broken.
    """
    silent = [tool["name"] for tool in _acting()
              if "undo" not in tool and "irreversible" not in tool]
    assert not silent, (
        "these acts neither declare an inverse nor say why they have "
        f"none: {silent}")


def test_no_acting_tool_claims_both():
    """Both is a contradiction the trail cannot render. `_act_row` reports
    `reversible` from one column and `irreversible_because` from the other,
    and a row carrying both would come back saying it can be taken back and
    also that it left the app."""
    confused = [tool["name"] for tool in _acting()
                if "undo" in tool and "irreversible" in tool]
    assert not confused, f"these acts claim both: {confused}"


def test_every_reason_for_irreversibility_has_a_sentence():
    """`irreversible` holds a refusal key, and the key has to resolve —
    otherwise the trail shows a person a machine identifier where an
    explanation belongs."""
    for tool in _acting():
        reason = tool.get("irreversible")
        if reason is not None:
            assert reason in engaged.REFUSALS, (
                f"{tool['name']} is irreversible for the reason {reason!r}, "
                "which has no sentence in REFUSALS")


def test_every_inverse_resolves_to_a_route_this_app_serves():
    """A stored inverse is a promise made at act time and kept much later.

    A `remove` route that does not exist stores cleanly, sits on the trail
    looking reversible, and fails on the one press somebody cared about. The
    `replace` half is checked the same way through its `before` read.
    """
    missing = []
    for tool in _acting():
        spec = tool.get("undo")
        if spec is None:
            continue
        if spec["kind"] == "remove":
            if tuple(spec["route"]) not in DOORS:
                missing.append(f"{tool['name']} undo: "
                               f"{spec['route'][0]} {spec['route'][1]}")
        else:
            if tuple(spec["before"]) not in DOORS:
                missing.append(f"{tool['name']} before-read: "
                               f"{spec['before'][0]} {spec['before'][1]}")
    assert not missing, (
        "these inverses name doors this app does not serve:\n    "
        + "\n    ".join(missing))


def test_every_replace_reads_before_it_writes():
    """The prior value is gone once it is overwritten.

    A `replace` with no `before` could only build its inverse from the value
    it just wrote — an undo that restores what is already there. `fields` is
    checked too: an empty one produces an inverse with an empty body, which
    replays as a validation error at the moment somebody presses it.
    """
    for tool in _acting():
        spec = tool.get("undo")
        if spec is None or spec["kind"] != "replace":
            continue
        assert spec.get("before"), (
            f"{tool['name']} replaces a value with nothing read first")
        assert spec.get("fields"), (
            f"{tool['name']} restores no fields, so its inverse has an "
            "empty body")


def test_every_remove_knows_where_the_id_comes_from():
    for tool in _acting():
        spec = tool.get("undo")
        if spec is None or spec["kind"] != "remove":
            continue
        slots = set(engaged._PLACEHOLDER.findall(spec["route"][1]))
        slots.discard("user_id")
        named = set(spec.get("path_from", {}))
        assert slots == named, (
            f"{tool['name']}'s inverse needs {sorted(slots)} and is told "
            f"where to find {sorted(named)}")


# --------------------------------------------------------------------------- #
# Driven, because a stored inverse is a claim
# --------------------------------------------------------------------------- #

class _Scripted:
    """A model that says what the test needs said, in order.

    `answered_by` is not decoration. `llm.generate_for_user` duck-types on it
    to report who actually produced the words, and a provider without it
    resolves to whatever the *deployment* would have used — which in a test
    run with no key is the stub. An engaged turn refuses to act on a stub
    answer (see `engaged.converse`), so a scripted model that did not say it
    was an online one would be refused before it could say anything, and
    every driven test here would pass through a code path no user meets.
    """

    answered_by = "claude"
    failure = None

    def __init__(self, lines):
        self.lines = list(lines)

    def generate(self, system, user):
        return self.lines.pop(0) if self.lines else "Done."


@pytest.fixture()
def engaged_user(client, monkeypatch):
    uid = enroll(client)
    token = client.headers["authorization"].removeprefix("Bearer ")
    client.post(f"/engaged/{uid}", json={"area": "personal_growth"})
    return uid, token


def _script(monkeypatch, *lines):
    """Install a model that says these things, in this order.

    One instance, closed over — `llm.generate_for_user` asks for a provider on
    every step of the loop, and handing it a fresh `_Scripted` each time would
    replay line one six times over. The first draft of this helper did exactly
    that and produced six journal entries from a two-line script, which is a
    tidy demonstration of why a driven test is worth more than a stored claim.
    """
    from jim import llm
    provider = _Scripted(lines)
    monkeypatch.setattr(llm, "get_provider",
                        lambda cloud=None, choice=None: provider)


def test_a_created_row_is_removed_by_its_inverse(client, engaged_user,
                                                 monkeypatch):
    """`remove`, driven: the act creates, the trail offers, the undo deletes.

    Through the app's own doors both ways — the undo replays a request, so
    the token, the plan and the refusal translation all still apply to it.
    """
    uid, _token = engaged_user
    _script(monkeypatch,
            'CALL write_journal {"text": "a thing I wrote"}',
            "Written.")
    turn = client.post(f"/engaged/{uid}/turn",
                       json={"message": "write that down"})
    assert turn.status_code == 200, turn.text
    assert len(client.get(f"/journal/{uid}").json()) == 1

    trail = client.get(f"/engaged/{uid}/acts").json()
    assert [a["tool"] for a in trail] == ["write_journal"]
    assert trail[0]["reversible"] is True

    undone = client.post(f"/engaged/{uid}/acts/{trail[0]['id']}/undo")
    assert undone.status_code == 200, undone.text
    assert client.get(f"/journal/{uid}").json() == []
    assert client.get(f"/engaged/{uid}/acts").json()[0]["undone_at"]


def test_an_overwritten_setting_comes_back(client, engaged_user, monkeypatch):
    """`replace`, driven: the value it overwrote, not the value it wrote."""
    uid, _token = engaged_user
    before = client.get(f"/presence/{uid}/bearing").json()["bearing"]
    _script(monkeypatch,
            'CALL set_bearing {"bearing": "professional"}',
            "Switched.")
    client.post(f"/engaged/{uid}/turn", json={"message": "keep it formal"})
    assert client.get(f"/presence/{uid}/bearing").json()["bearing"] \
        == "professional"

    act = [a for a in client.get(f"/engaged/{uid}/acts").json()
           if a["tool"] == "set_bearing"][0]
    assert client.post(f"/engaged/{uid}/acts/{act['id']}/undo").status_code \
        == 200
    assert client.get(f"/presence/{uid}/bearing").json()["bearing"] == before


def test_the_same_act_cannot_be_taken_back_twice(client, engaged_user,
                                                 monkeypatch):
    """The second press is a refusal, not a second delete.

    Without the check the replay would run again against a row that is gone,
    which is a 404 the trail would report as "undo failed" — telling somebody
    their undo did not work when it had already worked.
    """
    uid, _token = engaged_user
    _script(monkeypatch, 'CALL write_journal {"text": "x"}', "Done.")
    client.post(f"/engaged/{uid}/turn", json={"message": "note that"})
    act = client.get(f"/engaged/{uid}/acts").json()[0]
    assert client.post(f"/engaged/{uid}/acts/{act['id']}/undo").status_code \
        == 200
    again = client.post(f"/engaged/{uid}/acts/{act['id']}/undo")
    assert again.status_code == 409
    assert again.json()["refusal"] == "engaged.already_undone"


def test_one_persons_act_is_not_another_persons_to_undo(client, monkeypatch):
    """The trail is scoped to the user in the path, not to the act's own row.

    An act id is a uuid, so this is not the likeliest attack — but the lookup
    that ignored the user would also let a second account's session list and
    reverse the first's, and that is a different-sized failure entirely.
    """
    first = enroll(client)
    first_token = client.headers["authorization"].removeprefix("Bearer ")
    client.post(f"/engaged/{first}", json={"area": "personal_growth"})
    _script(monkeypatch, 'CALL write_journal {"text": "mine"}', "Done.")
    client.post(f"/engaged/{first}/turn", json={"message": "note it"})
    act = client.get(f"/engaged/{first}/acts").json()[0]

    second = enroll(client)          # becomes the client's default caller
    denied = client.post(f"/engaged/{second}/acts/{act['id']}/undo")
    assert denied.status_code == 404
    assert denied.json()["refusal"] == "engaged.no_such_act"

    # And the first person's row is untouched.
    client.headers["authorization"] = f"Bearer {first_token}"
    assert client.get(f"/engaged/{first}/acts").json()[0]["undone_at"] is None


def test_reaching_a_specialist_is_recorded_as_something_that_cannot_be_undone(
        client, engaged_user, monkeypatch):
    """The honest third state.

    `ask_specialist` sends the person's own words outside this product. The
    trail says so in words rather than filing it beside a journal entry that
    deletes cleanly, because a data structure that treats the two the same is
    a data structure telling a lie.
    """
    uid, _token = engaged_user
    row = engaged.tool("ask_specialist")
    assert "undo" not in row and row["irreversible"] == "engaged.cannot_unsay"

    # Recorded through the same path an act takes, without needing a QRME
    # tandem standing up: what is under test is the trail, not the bridge.
    engaged._record_act(engaged.current(uid)["id"], uid, {
        "tool": "ask_specialist", "status": 200, "undo": None,
        "irreversible": row["irreversible"],
    })
    listed = client.get(f"/engaged/{uid}/acts").json()[0]
    assert listed["reversible"] is False
    assert listed["irreversible_because"] == "engaged.cannot_unsay"
    refused = client.post(f"/engaged/{uid}/acts/{listed['id']}/undo")
    assert refused.status_code == 409
    assert refused.json()["refusal"] == "engaged.cannot_be_undone"


def test_a_failed_act_leaves_nothing_on_the_trail(client, engaged_user,
                                                  monkeypatch):
    """Only a call that succeeded is something to take back.

    Recording a refused write would put a row on the trail whose undo deletes
    something that was never created — at best a 404, at worst somebody
    else's row of the same shape.
    """
    uid, _token = engaged_user
    _script(monkeypatch,
            'CALL move_goal {"goal_id": "gol_nothing", "progress": 1}',
            "That goal is not there.")
    client.post(f"/engaged/{uid}/turn", json={"message": "finish my goal"})
    assert client.get(f"/engaged/{uid}/acts").json() == []


def test_the_trail_survives_the_session_it_was_made_in(client, engaged_user,
                                                       monkeypatch):
    """`GET /engaged/{id}/acts` reads the account, not the open engagement.

    The thing somebody wants to take back is usually noticed afterwards, and
    a trail that emptied on sign-off would be a trail available exactly while
    nobody needed it.
    """
    uid, _token = engaged_user
    _script(monkeypatch, 'CALL write_journal {"text": "before"}', "Done.")
    client.post(f"/engaged/{uid}/turn", json={"message": "note it"})
    client.post(f"/engaged/{uid}/sign-off", json={"topics": []})
    assert client.get(f"/engaged/{uid}").json()["engaged"] is False

    trail = client.get(f"/engaged/{uid}/acts").json()
    assert len(trail) == 1 and trail[0]["reversible"] is True
    assert client.post(f"/engaged/{uid}/acts/{trail[0]['id']}/undo") \
        .status_code == 200


def test_a_session_cannot_change_more_than_its_ceiling(client, engaged_user,
                                                       monkeypatch):
    """A blast radius, not a cost ceiling.

    Somebody skimming an undo trail of four hundred rows is not reviewing
    anything, and a trail nobody reviews is the condition the autonomy was
    granted under, quietly withdrawn.
    """
    uid, _token = engaged_user
    monkeypatch.setattr(engaged, "ACTS_PER_ENGAGEMENT", 1)
    _script(monkeypatch,
            'CALL write_journal {"text": "one"}',
            'CALL write_journal {"text": "two"}',
            "Done.")
    turn = client.post(f"/engaged/{uid}/turn", json={"message": "note twice"})
    assert turn.json()["stopped"] == "engaged.acted_enough"
    assert len(client.get(f"/journal/{uid}").json()) == 1
