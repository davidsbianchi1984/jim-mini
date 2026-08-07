"""The posture blocks say what this product will not do. Nothing checked.

Every tandem surface in JIM ships a `posture` block — `mirrored_here`,
`posts_on_your_behalf`, `health_data_shared`, `watching_stored_here`,
`auto_joined`, `rings_on_your_behalf`, `stored_here`. They are the product's
promises to somebody handing a health guardian a bridge into a public
platform, and they are the reason the bridge is defensible at all.

Every one of them is a **hardcoded literal in the response dict**. And the
test that guarded them — `test_the_posture_is_stated_and_kept` — asserted
this:

    assert posture["watching_stored_here"] is False

which reads the literal back out of the dict that hardcodes it. It cannot
fail. Add a line tomorrow that files every card somebody scrolls past and
that assertion stays green, because the literal never changes. The test is
named *stated and kept* and only ever checked **stated**.

The file already knew the right technique and used it exactly once, on the
claim below it: `test_there_is_no_way_to_post_from_here` reads the route
table instead of trusting the intention. This file is that technique applied
to the rest of them.

## How you check an absence

You cannot compute "I did not do X" from doing nothing, so the check has to
be made from outside: **snapshot every table, take the action, and see what
grew**. :func:`writes_only_to` is that, and it is deliberately whole-database
rather than a named-table check — a claim about what is stored has to be
falsified by a row appearing *anywhere*, including in a table invented after
this test was written.
"""

import pytest

from jim import db
from jim.tests.conftest import enroll


def _row_counts() -> dict[str, int]:
    """Every table and how full it is.

    Read from `sqlite_master` rather than a hand-kept list: a claim about what
    this product stores must be falsified by a row landing in a table nobody
    thought to add here, which is exactly the table a later round would add.
    """
    conn = db.connect()
    names = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' "
        "AND name NOT LIKE 'sqlite_%'").fetchall()]
    return {n: conn.execute(f"SELECT COUNT(*) FROM {n}").fetchone()[0]
            for n in names}


def writes_only_to(allowed: set[str], action) -> dict[str, int]:
    """Run `action` and return every table that grew, failing on any that is
    not named in `allowed`."""
    before = _row_counts()
    action()
    after = _row_counts()
    grew = {n: after[n] - before.get(n, 0)
            for n in after if after[n] > before.get(n, 0)}
    unexpected = {n: d for n, d in grew.items() if n not in allowed}
    assert not unexpected, (
        f"rows landed in {sorted(unexpected)} — the posture claims nothing is "
        f"stored here, and something was")
    return grew


# --- the feed: "nothing you watch is stored in JIM" -------------------------

def test_reading_the_feed_stores_nothing_anywhere(make_tandem):
    """The claim the whole bridge rests on, checked from outside the claim.

    A feed is the one surface where a guardian could learn a great deal about
    somebody by watching them watch — which is why the posture says it does
    not, and why saying so was never enough.
    """
    tc = make_tandem()
    user = enroll(tc)
    writes_only_to(set(), lambda: [tc.get(f"/community/{user}/feed")
                                   for _ in range(3)])


def test_reading_the_community_door_stores_nothing_anywhere(make_tandem):
    tc = make_tandem()
    user = enroll(tc)
    writes_only_to(set(), lambda: tc.get(f"/community/{user}"))


def test_the_posture_names_what_it_does_keep(make_tandem):
    """Saying only what you do *not* do is how a true sentence misleads.

    Opening a community room **is** recorded — `community_room_opened`, with
    the room's id, on the user's own timeline — and the presence reads those
    rows to notice somebody has been talking to nothing but this program. That
    is a defensible record and a useful one. What is not defensible is a
    posture block that lists five refusals and never mentions it, leaving
    "nothing you watch is stored in JIM" to be read wider than it is true.
    """
    tc = make_tandem()
    user = enroll(tc)
    posture = tc.get(f"/community/{user}/feed").json()["posture"]
    assert "records" in posture, (
        "the posture lists what it refuses and never what it keeps — a reader "
        "has no way to learn about the visit record except by being surprised")
    kept = posture["records"]
    assert kept, "an empty list here is the same silence with a field on it"
    assert any("room" in str(k).lower() for k in kept), kept


def test_opening_a_room_writes_the_fact_and_nothing_from_inside(make_tandem):
    """The record that does exist, pinned to its own narrow shape. The fact
    that a door was opened is a fact about this user's week. What was said
    behind it belongs to the room, and to QRME."""
    tc = make_tandem()
    user = enroll(tc)
    grew = writes_only_to(
        {"events"},
        lambda: tc.post(f"/community/{user}/visits",
                        json={"room_id": "room-1"}))
    assert grew == {"events": 1}, grew

    row = db.connect().execute(
        "SELECT type, detail FROM events WHERE user_id=? "
        "ORDER BY rowid DESC LIMIT 1", (user,)).fetchone()
    assert row["type"] == "community_room_opened"
    for leak in ("message", "body", "said", "transcript", "content"):
        assert leak not in (row["detail"] or "").lower(), row["detail"]


# --- the route table, with the verb this time -------------------------------

def test_there_is_no_write_route_on_the_bridge(make_tandem):
    """The verb-blind guard, fixed.

    `test_there_is_no_way_to_post_from_here` collected **paths** and asserted
    the set was `["/community/{user_id}/feed"]`. A `POST` to that same path
    produces the same string, so the one test in the file that read the route
    table instead of the docstring still could not see the thing it was named
    for. `.methods` was on every route object the whole time.
    """
    tc = make_tandem()
    writes = {(m, getattr(r, "path", ""))
              for r in tc.app.routes
              for m in (getattr(r, "methods", None) or set())
              if getattr(r, "path", "").startswith("/community/")
              and m not in ("GET", "HEAD", "OPTIONS")}
    assert writes == {("POST", "/community/{user_id}/visits")}, (
        f"a write route appeared on the bridge: {sorted(writes)} — publishing "
        "happens in QRME under the user's own identity, which is the entire "
        "reason this is a door rather than a room")


# --- reaching out: four claims, none of them previously checked -------------

def test_reaching_out_joins_nothing_and_stores_nothing(make_tandem):
    """`auto_joined`, `rings_on_your_behalf`, `stored_here` — three literals
    in a dict, and now three assertions about behaviour. A bell is somebody
    else's attention; ringing one on a user's behalf spends a stranger's time
    on a guess this program made."""
    tc = make_tandem()
    user = enroll(tc)
    writes_only_to(set(), lambda: tc.get(f"/presence/{user}/reach"))


def test_the_offers_carry_an_area_and_never_a_condition(make_tandem):
    """`health_data_shared: false`, checked against the offers themselves.

    This is the surface whose whole purpose is to suggest people, which is
    exactly where it would have been easiest to loosen — "somebody who also
    has trouble sleeping" is a better recommendation and a disclosure the
    user never made.
    """
    tc = make_tandem()
    user = enroll(tc)
    for _ in range(3):
        tc.post(f"/checkin/{user}", json={"mood": 1, "energy": 1})
    body = tc.get(f"/presence/{user}/reach").json()
    blob = str(body).lower()
    for leak in ("mood", "checkin", "check-in", "medication", "diagnos",
                 "condition", "vital", "resting rate"):
        assert leak not in blob, (
            f"the word {leak!r} crossed into an offer — the offer names an "
            f"area, never a condition")


# --- the shape of the guard itself ------------------------------------------

def test_the_helper_would_actually_catch_a_write(make_tandem):
    """A guard nobody has seen fail is a guard nobody should trust.

    This writes a row deliberately and asserts `writes_only_to` notices —
    without it, every test above would pass just as happily if `_row_counts`
    were quietly returning an empty dict.
    """
    tc = make_tandem()
    user = enroll(tc)
    with pytest.raises(AssertionError, match="the posture claims nothing"):
        writes_only_to(set(), lambda: tc.post(f"/community/{user}/visits",
                                              json={"room_id": "room-x"}))


def test_the_snapshot_can_see_every_table():
    """And that it is reading the real schema rather than a short list that
    silently stopped covering the tables added after it was written."""
    counts = _row_counts()
    for expected in ("users", "events", "presence_beats", "presence_surface",
                     "presence_bearing"):
        assert expected in counts, f"{expected} is invisible to the snapshot"
