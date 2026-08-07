"""The feed tab: QRME's stream, through the door that already exists.

`jim/community.py` opens with the argument this file is another instance of.
P001's spec promises JIM users forums, local events and community, and all of
it exists in QRME — moderation, rooms, desks, ten languages. Building a second
version inside a private health guardian would duplicate a moderation stack
that is hard to get right once, and put somebody's medical timeline and their
public watching in the same database.

So the feed is a door. This file asserts the three things that makes true.

## It cannot post, by construction

Not "does not" — **cannot**. There is no write route on this side and no
binding in the client. Publishing happens in QRME under the user's own QRME
identity, which is the entire reason for showing a door rather than building
a room. `test_there_is_no_way_to_post_from_here` reads the route table rather
than trusting the intention.

## It passes QRME's promises through rather than restating them

Three fields in every page are QRME's word to the person on the other end:

    plays      whether footage plays without being asked for
    entering   what walking into a live room does
    ringing    what pressing a bell does, and to whom

`plays` is the sharpest. QRME sets it false for anything it does not host, so
that scrolling past a card makes no request to another company's server —
`qrme/db.py` has said so about `post_videos` since long before a feed existed.
If JIM recomputed that flag there would be two implementations of one promise,
and the second one would be wrong the first time QRME changed its mind.

## It carries no health data, in either direction

The posture block is on the wire, not in a comment: nothing mirrored here,
nothing posted on the user's behalf, no health data shared, and **nothing
about what was watched stored on this side**. The last one is new with this
surface: a feed is the one place a guardian could quietly learn a great deal
about somebody by watching them watch.
"""

from jim.tests.conftest import enroll


def test_standalone_jim_says_where_the_feed_lives(client):
    """No tandem, no feed — and the refusal names the door rather than
    failing blankly."""
    user = enroll(client)
    r = client.get(f"/community/{user}/feed")
    assert r.status_code == 409
    detail = r.json()["detail"]
    assert "JIM_QRME_URL" in detail and "QRME" in detail


def test_the_cards_come_through_the_tandem(make_tandem):
    tc = make_tandem()
    user = enroll(tc)
    body = tc.get(f"/community/{user}/feed").json()
    kinds = [i["kind"] for i in body["items"]]
    assert {"video", "offsite", "room", "desk"} <= set(kinds), kinds
    # JIM knows what this user reads; QRME does not.
    assert body["language"]


def test_the_play_flag_is_qrmes_and_is_not_recomputed(make_tandem):
    """The assertion that matters most.

    QRME decides what plays. If this ever comes through true for an off-site
    card, JIM has started making a promise it does not own — and the person
    scrolling is announcing themselves to a company they never chose.
    """
    tc = make_tandem()
    user = enroll(tc)
    items = {i["kind"]: i for i in
             tc.get(f"/community/{user}/feed").json()["items"]}
    assert items["video"]["plays"] is True
    assert items["offsite"]["plays"] is False, (
        "an off-site card came through playable — JIM is overriding QRME's "
        "promise about footage it does not hold")
    assert "src" not in items["offsite"]


def test_a_room_and_a_desk_keep_the_sentence_that_warns_you(make_tandem):
    """Both reach a human being, so both say what the press does before it is
    pressed. Passed through whole rather than reworded here."""
    tc = make_tandem()
    user = enroll(tc)
    items = {i["kind"]: i for i in
             tc.get(f"/community/{user}/feed").json()["items"]}
    assert "puts you in the room" in items["room"]["entering"]
    assert "reaches a person" in items["desk"]["ringing"]
    assert items["desk"]["human"] is True and items["desk"]["ai"] is False


def test_the_shop_behind_a_desk_comes_with_it(make_tandem):
    tc = make_tandem()
    user = enroll(tc)
    desk = next(i for i in tc.get(f"/community/{user}/feed").json()["items"]
                if i["kind"] == "desk")
    assert desk["shop"]["offerings"], desk["shop"]


def test_the_posture_is_stated(make_tandem):
    """Stated, and only stated — every assertion below reads back a literal
    from the dict that hardcodes it. Whether any of it is *kept* is
    `test_the_posture_is_stated_and_nothing_keeps_it.py`, which snapshots
    every table, reads the feed, and looks at what grew."""
    tc = make_tandem()
    user = enroll(tc)
    body = tc.get(f"/community/{user}/feed").json()
    posture = body["posture"]
    assert posture["mirrored_here"] is False
    assert posture["posts_on_your_behalf"] is False
    assert posture["can_post_from_jim"] is False
    assert posture["health_data_shared"] is False
    assert posture["watching_stored_here"] is False, (
        "a feed is the one surface where a guardian could learn a great deal "
        "by watching somebody watch")
    # The record it does keep. A block of five refusals that never mentions
    # the one thing it writes lets a true sentence be read wider than it is.
    assert posture["records"]
    assert "QRME" in body["note"]


def test_there_is_no_way_to_post_from_here(make_tandem):
    """Read the route table rather than trusting the intention. A write route
    that appeared here later would be the whole argument undone."""
    tc = make_tandem()
    paths = {getattr(r, "path", "") for r in tc.app.routes}
    writable = [p for p in paths if p.startswith("/community/") and "feed" in p]
    assert writable == ["/community/{user_id}/feed"], writable
    for route in tc.app.routes:
        if getattr(route, "path", "") == "/community/{user_id}/feed":
            assert set(route.methods) <= {"GET", "HEAD"}, (
                f"the feed door accepts {route.methods} — publishing belongs "
                "in QRME, under the user's own QRME identity")


def test_an_unreachable_qrme_is_a_quiet_screen(make_tandem, monkeypatch):
    """Every shelf in this client returns empty on failure rather than an
    error page, and a feed that cannot load should be a quiet screen.

    The transport is what fails, not the method: a first draft of this patched
    `QRMEClient.feed` itself, which replaced the very try/except it was meant
    to exercise and asserted nothing at all.
    """
    tc = make_tandem()
    user = enroll(tc)
    transport = tc.app.state.qrme._client

    def boom(path, headers=None):
        raise RuntimeError("network down")

    monkeypatch.setattr(transport, "get", boom)
    r = tc.get(f"/community/{user}/feed")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["items"] == [] and body["cursor"] is None
    # And the posture still says what it says, because it is JIM's to state
    # whether or not QRME answered.
    assert body["posture"]["can_post_from_jim"] is False
