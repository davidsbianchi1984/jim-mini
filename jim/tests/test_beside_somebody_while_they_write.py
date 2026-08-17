"""Beside somebody while they write, and not recording them.

The field ask, verbatim: *as you're typing out a sales page to a customer, or
writing a strategy doc, to just jump in and say hey you forgot about this, or
here's maybe another idea, or you should consider this, I can do this thing to
help.*

    asked     can it answer about a draft
    mattered  does it notice the thing they would have wanted noticing

## What these guards hold

* it never writes — not the draft, not a remark, not a count. What somebody is
  drafting for a customer is the most commercially sensitive text they own,
  and the honest way to be trusted with it is to have nowhere to put it;
* it never leaves the device. No provider, no socket, and a guard on the
  imports rather than a promise in a docstring;
* it stays quiet when it has nothing, and says why — a companion with a remark
  on every paragraph is a paperclip;
* every remark carries its evidence, and a store entry carries where it came
  from, because *something I read* and *something a paid model said once* are
  different claims;
* it never offers a door that does not exist;
* and it does not decide. Remarks come back; applying one is the person's own
  act, and nothing here can change a word of what they wrote.
"""

from __future__ import annotations

import ast
import inspect
import pathlib

from jim import alongside

from .conftest import enroll

# Long enough to be worth an opinion, and about something the pack and the
# goals below can both have a view on.
DRAFT = """
Our spring campaign puts the new range in front of buyers who already
know us. The page opens on the guarantee, then the price, then a short
line about delivery windows and what happens when one slips. We are
leaning on the customer stories we gathered in March, and closing with
the trial offer that worked last year, because repeat buyers respond to
it and it costs us very little to run again this quarter.
"""


def _goal(client, user_id, title, area="career"):
    r = client.post(f"/goals/{user_id}", json={"area": area, "title": title})
    assert r.status_code in (200, 201), r.text
    return r.json()


# --------------------------------------------------------------------------
# The thing itself.
# --------------------------------------------------------------------------

def test_it_notices_something_of_theirs_the_page_never_mentions(client):
    """*Hey, you forgot about this* — and the thing it names is theirs, out of
    their own records, rather than an invention that sounds plausible."""
    user_id = enroll(client)
    _goal(client, user_id, "move the wholesale accounts onto annual terms")

    out = client.post(f"/alongside/{user_id}", json={"draft": DRAFT}).json()
    forgot = [r for r in out["remarks"] if r["kind"] == "forgot"]
    assert forgot, "an active goal the draft never touches went unremarked"
    assert "wholesale" in forgot[0]["says"]


def test_a_goal_the_draft_already_covers_is_not_remarked_on(client):
    """The failure that matters is being told you forgot a thing that is in
    your second paragraph. Missing a remark costs nothing; a wrong one costs
    the next right one."""
    user_id = enroll(client)
    _goal(client, user_id, "lean on the customer stories from March")

    out = client.post(f"/alongside/{user_id}", json={"draft": DRAFT}).json()
    said = [r["says"] for r in out["remarks"]]
    assert "lean on the customer stories from March" not in said


def test_every_remark_says_what_it_came_from(client):
    """*You forgot about this* with nothing under it is a guess wearing a
    suggestion's clothes."""
    user_id = enroll(client)
    _goal(client, user_id, "move the wholesale accounts onto annual terms")

    out = client.post(f"/alongside/{user_id}", json={"draft": DRAFT}).json()
    assert out["remarks"]
    for remark in out["remarks"]:
        assert remark["because"], f"{remark['says']} arrived with no evidence"
        assert remark["kind"] in alongside.KINDS


def test_it_says_nothing_rather_than_something(client):
    """Silence is a real answer, and it carries its reason — an empty list
    with no reason leaves a person unable to tell *nothing to add* from *it
    did not run*."""
    user_id = enroll(client)
    out = client.post(f"/alongside/{user_id}",
                      json={"draft": "a few words"}).json()
    assert out["remarks"] == []
    assert out["quiet_because"]


def test_the_margin_holds_three_remarks_at_most(client):
    """A margin full of remarks is a margin nobody reads, and the fourth-best
    thing this could say was never worth the first three being ignored."""
    user_id = enroll(client)
    for n in range(8):
        _goal(client, user_id, f"a separate unmentioned objective number {n}")

    out = client.post(f"/alongside/{user_id}", json={"draft": DRAFT}).json()
    assert len(out["remarks"]) <= 3


def test_an_offer_names_a_door_this_product_has(client):
    """An offer to do something unbuilt is worse than silence: a promise made
    by a screen on behalf of code nobody wrote."""
    user_id = enroll(client)
    draft = ("We should rehearse the interview questions before the hiring "
             "panel meets, because the candidate deserves a consistent set "
             "and our own answers about the role are still vague in places "
             "that a customer would notice immediately.")
    out = client.post(f"/alongside/{user_id}", json={"draft": draft}).json()
    for remark in out["remarks"]:
        if remark["kind"] == "offer":
            assert remark["door"] in ("drills", "letter")


# --------------------------------------------------------------------------
# What it must never do.
# --------------------------------------------------------------------------

def _imported() -> set[str]:
    """Every module `alongside` imports, by name.

    Read from the syntax rather than by searching the text: the first version
    of these two guards matched their own docstring, which explains what the
    module does not do and therefore contains every word it must not use. A
    guard that its own prose can fail is a guard nobody can write plainly.
    """
    tree = ast.parse(pathlib.Path(alongside.__file__).read_text(
        encoding="utf-8"))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            names |= {a.name for a in node.names}
            if node.module:
                names.add(node.module.split(".")[0])
    return names


def test_the_draft_is_read_and_dropped():
    """Not in a table, not in a log, not as an embedding. That is the whole
    difference between something sitting beside somebody and something
    recording them — and it holds because there is nothing here to write
    with."""
    assert "db" not in _imported(), (
        "a module handed what somebody is writing for a customer has reached "
        "for the database")
    calls = {node.func.attr for node in ast.walk(
        ast.parse(pathlib.Path(alongside.__file__).read_text(
            encoding="utf-8")))
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)}
    for write in ("execute", "commit", "write", "append_log"):
        assert write not in calls, f"`{write}` is called on a draft's path"


def test_nothing_here_reaches_the_network():
    """A guard on the imports, the same rule `jim/pipeline.py` holds — for a
    draft rather than a question."""
    reached = _imported() & {"llm", "requests", "urllib", "httpx", "socket",
                             "http", "cloud", "scrape", "research"}
    assert not reached, (
        f"{sorted(reached)} in a module that reads what somebody is drafting")


def test_it_cannot_change_a_word_of_what_they_wrote(client):
    """It does not decide. Remarks come back and applying one is the person's
    own act — there is no path here that edits or replaces a draft."""
    user_id = enroll(client)
    _goal(client, user_id, "move the wholesale accounts onto annual terms")
    out = client.post(f"/alongside/{user_id}", json={"draft": DRAFT}).json()
    assert set(out) == {"remarks", "quiet_because"}
    for remark in out["remarks"]:
        assert "replacement" not in remark and "edit" not in remark


def test_it_is_not_watching_a_screen():
    """It reads a draft handed to it in a request somebody made. A guardian
    that reads whatever is in front of you, continuously, is a different thing
    with a different consent — and this is where that stays true."""
    assert "draft" in inspect.signature(alongside.read).parameters
    source = inspect.getsource(alongside)
    for ambient in ("screenshot", "capture", "poll", "watch_screen"):
        assert ambient not in source


def test_the_route_creates_nothing(client):
    """A 200 rather than a 201, because nothing was created — and a client
    reading the status should not be told otherwise."""
    user_id = enroll(client)
    r = client.post(f"/alongside/{user_id}", json={"draft": DRAFT})
    assert r.status_code == 200, r.text


def test_it_belongs_to_the_person_whose_records_it_reads(client):
    """The remarks are built from somebody's own goals and store, so the
    route is theirs and nobody else's."""
    user_id = enroll(client)
    del client.headers["authorization"]
    r = client.post(f"/alongside/{user_id}", json={"draft": DRAFT})
    assert r.status_code in (401, 403, 404), r.text
