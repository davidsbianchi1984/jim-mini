"""FIG. 2 boxes 222–226: the community layer, as a door rather than a copy.

P001's spec describes community inside the guidance product — "interact with
others, view and create content" (222), "process user content for moderation,
distribution" (224), "store user content for incorporation into community
interaction" (226) — and [0020] promises "our chat engines, your local events,
and forums in all languages".

All of it exists in QRME, and the two products are built to run in tandem. So
JIM shows the door: QRME's rooms and places, in the user's language, with the
health data staying on this side of it.
"""

from jim.tests.conftest import enroll


def test_standalone_jim_says_where_the_community_lives(client):
    user = enroll(client)
    r = client.get(f"/community/{user}")
    assert r.status_code == 409
    detail = r.json()["detail"]
    assert "JIM_QRME_URL" in detail and "QRME" in detail


def test_the_rooms_and_places_come_through_the_tandem(make_tandem):
    tc = make_tandem()
    user = enroll(tc)
    body = tc.get(f"/community/{user}").json()

    topics = {room["topic"] for room in body["rooms"]}
    assert "Night shift, still awake" in topics
    assert {"chat", "voice"} <= {room["channel"] for room in body["rooms"]}
    # Every room carries a URL a client can actually open.
    assert all(room["url"] is None or room["url"].endswith(room["id"])
               for room in body["rooms"])

    # "local events" — the places QRME's listings actually claim.
    assert {"Bend, OR", "Portland, OR"} == {p["locality"] for p in body["places"]}

    # "in all languages" — JIM knows what this user reads.
    assert body["language"]


def test_locality_filters_the_places(make_tandem):
    tc = make_tandem()
    user = enroll(tc)
    body = tc.get(f"/community/{user}", params={"locality": "bend"}).json()
    assert [p["locality"] for p in body["places"]] == ["Bend, OR"]


def test_the_posture_is_stated(make_tandem):
    """The whole reason this is a door: a private health guardian must not
    grow a second social network, and must not carry health data into one.

    **Stated, and only stated.** This reads literals back out of the dict that
    hardcodes them, so it can tell you the fields are present and their
    spelling has not drifted, and it can tell you nothing at all about whether
    the product keeps its word. It was called *stated and kept* for several
    releases, which is worse than useless: a name like that is why nobody went
    looking. Whether it is kept is
    `test_the_posture_is_stated_and_nothing_keeps_it.py`, which takes the
    action and counts the rows.
    """
    tc = make_tandem()
    user = enroll(tc)
    body = tc.get(f"/community/{user}").json()
    posture = body["posture"]
    assert posture["mirrored_here"] is False
    assert posture["posts_on_your_behalf"] is False
    assert posture["health_data_shared"] is False
    # And what it does keep, which a block of refusals used not to mention.
    assert posture["records"]
    assert "community lives in QRME" in body["note"]


def test_an_unreachable_qrme_is_a_quiet_screen(make_tandem, monkeypatch):
    from jim.tests.conftest import FakeQRME
    monkeypatch.setattr(FakeQRME, "get",
                        lambda self, path, headers=None: (_ for _ in ()).throw(
                            ConnectionError("community down")))
    tc = make_tandem()
    user = enroll(tc)
    body = tc.get(f"/community/{user}").json()
    assert body["rooms"] == [] and body["places"] == []


def test_opening_a_door_records_the_fact_and_nothing_inside(make_tandem):
    tc = make_tandem()
    user = enroll(tc)
    out = tc.post(f"/community/{user}/visits", json={"room_id": "rm_night"}).json()
    assert out["noted"] is True
    assert "nothing from inside" in out["stored"]

    visits = tc.get(f"/community/{user}/visits").json()
    assert visits[0]["room_id"] == "rm_night" and visits[0]["where"] == "qrme"
    # It lands on the user's own timeline like every other Guardian event.
    assert any(e["type"] == "community_room_opened"
               for e in tc.get(f"/events/{user}").json())
