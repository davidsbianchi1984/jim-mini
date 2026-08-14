"""What an engaged session may touch, checked against the app's own routes.

`jim/engaged.py` gives a model the caller's own credential and a loop. That is
a design decision with exactly one thing standing behind it: :data:`TOOLS`, a
written list of the doors it may go through. Everything in this file exists
because a list is only a guarantee if something reads it.

    asked     does the agent have the owner's authority
    mattered  does it have the owner's intent

Four questions, and each has a way of being answered wrongly that would look
fine in review:

**Does every row resolve to a real route?** A row naming a path that does not
exist is not a smaller reach — it is a tool that fails at the moment somebody
needs it, with a refusal key that says nothing about why.

**Is every writing row behind this user's own door?** A write the agent can
make on a route that does not demand the user's token is a write anybody's
session could make on anybody's records. Reads are checked differently and
deliberately: the user in the path is bound by `call` and is never the model's
to name, so a public read is not a leak — but a public *write* is.

**Is the carve-out real?** :data:`NEVER` names the emergency paths, the money
paths and the doors that end an account. Those are refused by absence rather
than by a check, which is the strongest form and the easiest to erode: one row
added in a hurry and nothing anywhere would have noticed.

**Is it still told nothing about the host?** The obvious way to make an agent
more capable is to tell it more about the machine, and on this machine that is
a map of somebody's medication cabinet and clinical captures.
"""

from __future__ import annotations

import re

import pytest

from jim import engaged
from jim.api import app

from . import clientpaths

#: Route templates the app actually serves, as (method, path).
DOORS = {(method, route.path)
         for route in clientpaths.all_routes(app)
         for method in (getattr(route, "methods", None) or ())}


def _paths_for(method: str) -> set[str]:
    return {path for m, path in DOORS if m == method}


def test_every_tool_resolves_to_a_route_this_app_serves():
    """The list is not prose.

    A row is a method and a path template, and both are matched against the
    route table rather than eyeballed. A typo here does not shrink the reach —
    it produces a tool that refuses at the moment somebody is relying on it.
    """
    missing = [f"{tool['name']}: {tool['route'][0]} {tool['route'][1]}"
               for tool in engaged.TOOLS
               if tuple(tool["route"]) not in DOORS]
    assert not missing, (
        "these tools name doors this app does not serve:\n    "
        + "\n    ".join(missing))


def test_every_acting_tool_goes_through_this_users_own_door():
    """A write must be on a route that carries the user in its path.

    `call` substitutes `user_id` from the session and drops one the model
    supplied, so a route templated on `{user_id}` cannot be pointed at
    somebody else. A writing row on a route without it would be a write with
    no such binding — and the binding is the whole of what keeps one person's
    session out of another person's records.

    Reads are exempt on purpose and only here: `read_specialists` is a
    catalogue, and a catalogue is the same for everybody.
    """
    loose = [f"{tool['name']}: {tool['route'][1]}"
             for tool in engaged.TOOLS
             if tool["acts"] and "{user_id}" not in tool["route"][1]]
    assert not loose, (
        "these tools change something through a door that does not name the "
        "user in its path, so nothing binds the write to whoever is "
        "driving:\n    " + "\n    ".join(loose))


def test_the_agent_cannot_reach_the_paths_that_are_never_its_to_reach():
    """The carve-out, read against the registry rather than trusted.

    Emergencies, escalation, the vigil, the crash watch, money movement,
    erasure, membership, another person's rows. Absence is how these are
    refused, and absence is exactly the kind of guarantee that survives review
    and does not survive a busy afternoon.
    """
    reached = []
    for tool in engaged.TOOLS:
        path = tool["route"][1]
        for forbidden in engaged.NEVER:
            if path.startswith(forbidden):
                reached.append(f"{tool['name']}: {path} (under {forbidden})")
    assert not reached, (
        "these tools reach paths no engaged session may ever reach:\n    "
        + "\n    ".join(reached))


def test_the_carve_out_names_paths_this_app_actually_has():
    """A guard on the guard.

    `NEVER` refuses by prefix, and a prefix that matches nothing refuses
    nothing. A renamed route would leave its entry here looking like a
    protection and behaving like a comment — which is the failure this whole
    file is written against, one level up.
    """
    served = {path for _method, path in DOORS}
    dead = [prefix for prefix in engaged.NEVER
            if not any(p.startswith(prefix) for p in served)]
    assert not dead, (
        "these entries in NEVER match no route this app serves, so they "
        "protect nothing:\n    " + "\n    ".join(dead)
        + "\n  A route was renamed, or the entry was always a guess.")


def test_no_tool_is_named_twice_and_every_name_is_callable():
    """Two rows under one name means one of them is unreachable and nobody
    can tell which. `is_a_tool` is also the gate `call` uses, so a name the
    pattern rejects is a row that ships and cannot be invoked."""
    names = [tool["name"] for tool in engaged.TOOLS]
    assert len(names) == len(set(names)), (
        f"duplicate tool names: "
        f"{sorted({n for n in names if names.count(n) > 1})}")
    unreachable = [n for n in names if not engaged.is_a_tool(n)]
    assert not unreachable, (
        f"these rows cannot be called through `call`: {unreachable}")


def test_an_engaged_session_is_told_nothing_about_the_host():
    """`SYSTEM` is the whole of what it knows about where it runs.

    Named for its own subject rather than for the property, because the
    sibling product's Studio agent carries a guard asking the same question
    of a different agent. Two files under one name would have registered
    across the three suites as a *shared* guard PDI was missing — and PDI has
    no agent for it to be missing on.

    And the `says` lines are read too, because the leak is as likely to
    arrive in prose written for a person as in the prompt written for the
    model — the console renders those sentences, and a model that has read a
    page can read a sentence.
    """
    leaks = engaged.mentions_the_host(engaged.SYSTEM)
    assert not leaks, (
        f"the system prompt tells the agent where it is running: {leaks}")
    for tool in engaged.TOOLS:
        said = engaged.mentions_the_host(tool["says"])
        assert not said, (
            f"the sentence for {tool['name']} names the host: {said}")


def test_the_leak_guard_can_actually_see_a_leak():
    """A guard on the guard. A `HOST_WORDS` that matched nothing would make
    every check above pass on a prompt naming the machine outright."""
    assert engaged.mentions_the_host(
        "the database is at /var/lib/jim.db on localhost"), (
        "the host-word reader found nothing in a sentence that is nothing "
        "but host words — the check above is vacuous")


def test_the_model_is_never_asked_whose_records_these_are():
    """`call` binds the user from the session, and drops one the model named.

    The prompt says so, and this asserts the code does. A model that could
    supply a `user_id` would be one prompt injection away from reading
    somebody else's medication cabinet, and the prompt is a document written
    on a page the model may itself be reading.
    """
    session_bound = engaged._fill("/goals/{user_id}", "usr_mine",
                                  {"user_id": "usr_theirs"})
    assert session_bound == "/goals/usr_mine", (
        "the path was built from something other than the session's user")

    # And through `call`, where the model's arguments actually arrive.
    calls: list[tuple] = []

    def watch(app, method, path, body, headers):
        calls.append((method, path, body))
        return 200, {}

    real, engaged._request = engaged._request, watch
    try:
        engaged.call("read_goals", {"user_id": "usr_theirs"}, app=app,
                     user_id="usr_mine", authorization=None)
    finally:
        engaged._request = real
    assert calls == [("GET", "/goals/usr_mine", None)], (
        f"a user named by the model reached the request: {calls}")


@pytest.mark.parametrize("bad", ["delete_profile", "raise_alarm", "",
                                 "read_page; DROP", "READ_GOALS", "a" * 60])
def test_a_name_that_is_not_on_the_list_never_reaches_a_route(bad):
    """Membership, not interpolation.

    The lookup is `name in tool_names()`, so a model that invents
    `delete_profile` gets a refusal rather than a request. This is the one
    behaviour that makes the list above a boundary rather than a suggestion.
    """
    assert not engaged.is_a_tool(bad)
    with pytest.raises(engaged.EngagedError):
        engaged.call(bad, {}, app=app, user_id="usr_1", authorization=None)


def test_a_reply_that_merely_mentions_a_tool_is_not_a_tool_call():
    """Prose is prose.

    An agent that acts on a sentence it merely appears in is one that acts on
    a sentence somebody else wrote into a journal it was reading — and this
    agent reads journals.
    """
    assert engaged.wants_a_tool("I could CALL set_goal for you if you like") \
        is None
    assert engaged.wants_a_tool("Sure, here is what I found.") is None
    assert engaged.wants_a_tool('CALL read_goals {}') == ("read_goals", {})


def test_a_call_whose_arguments_do_not_parse_is_refused_not_guessed():
    """Unreadable arguments are a refusal, never a guess.

    Falling back to `{}` would turn *set this goal to whatever I meant* into
    *set this goal*, which is the failure mode where an agent does something
    adjacent to what was asked and reports success.
    """
    with pytest.raises(engaged.EngagedError):
        engaged.wants_a_tool('CALL set_goal {not json}')


def test_arguments_that_are_not_an_object_are_read_as_prose():
    """A line whose arguments are not `{...}` is not a call at all.

    `_CALL` requires braces, so `CALL set_goal ["a list"]` matches nothing and
    comes back as None — the reply is treated as something the model said
    rather than something it asked for. That is the safe direction: a shape
    the protocol does not describe should stop being a tool call, not become
    a tool call with improvised arguments.
    """
    assert engaged.wants_a_tool('CALL set_goal ["a list"]') is None


def test_every_refusal_the_module_raises_has_a_sentence():
    """A key with no row in `REFUSALS` answers 409 with a generic sentence,
    which is how a specific failure becomes an unactionable one. Read out of
    the source rather than enumerated, so a refusal added later is covered."""
    import inspect
    raised = set(re.findall(r'EngagedError\("([a-z_.]+)"\)',
                            inspect.getsource(engaged)))
    assert raised, "no refusals found in the module — the reader has drifted"
    unwritten = sorted(raised - set(engaged.REFUSALS))
    assert not unwritten, (
        f"these refusals have no sentence: {unwritten}")
