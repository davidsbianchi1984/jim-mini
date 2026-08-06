"""The dial, the company, and the beat that points away from here.

Three things the presence gained, and each has one assertion that matters:

* **the bearing** starts as a companion and changes when somebody says so —
  and it is a *register*, so what the guardian watches is identical in both.
  A dial that quietly narrowed a health guardian's attention would hurt the
  person who turned it, and that is the whole failure this file guards;
* **company** is a beat with nothing wanted in it, last in the order so it
  can never displace something that was actually noticed;
* **the alone beat** fires when somebody has been talking to this and to
  nobody else, and it points at people. A guardian that answers isolation
  with more of itself has found the problem and made it worse — and that is
  the easiest thing for a product like this to do by accident, because the
  number it would move is the one that looks like success.
"""

import jim.presence as presence
from jim.tests.conftest import enroll


def test_it_starts_as_a_companion_without_anybody_choosing(client):
    """The default is the claim. A guardian that opens in the register of a
    form is one people answer like a form, and a person who wanted the form
    can ask for it in one sentence."""
    user = enroll(client)
    body = client.get(f"/presence/{user}/bearing").json()
    assert body["bearing"] == "companion"
    assert body["default"] == "companion"
    assert set(body["choices"]) == set(presence.BEARINGS)


def test_the_dial_is_a_register_and_never_a_capability(client):
    """The sharp one.

    Somebody who asks for professional asked for less unprompted warmth. If
    that also narrowed what the guardian watches, or dropped a safety path,
    the dial would be a way of hurting whoever turned it — so both bearings
    watch the same six areas and keep every path, and it is on the wire.
    """
    user = enroll(client)
    r = client.put(f"/presence/{user}/bearing", json={"bearing": "professional"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["bearing"] == "professional"
    assert body["unchanged"]["what_it_watches"] == "the same six areas"
    assert body["unchanged"]["safety_paths"] == "every one, in both"
    # What actually differs is two registers of unasked-for warmth, and
    # nothing else.
    dropped = (set(presence.BEARING_EFFECT["companion"]["registers"])
               - set(presence.BEARING_EFFECT["professional"]["registers"]))
    assert dropped == {"curious", "company"}, dropped


def test_a_bearing_nobody_defined_is_refused(client):
    user = enroll(client)
    r = client.put(f"/presence/{user}/bearing", json={"bearing": "romantic"})
    assert r.status_code == 422, r.text
    assert client.get(f"/presence/{user}/bearing").json()["bearing"] == "companion"


def test_saying_it_is_enough_and_it_is_a_table_not_a_guess():
    """A person should not have to find a setting to be taken seriously —
    and the phrase table is deliberately readable, so "keep it professional"
    is obeyed identically every time rather than however a model felt."""
    assert presence.bearing_from_prompt("Keep it professional from now on") \
        == "professional"
    assert presence.bearing_from_prompt("you can relax, talk to me normally") \
        == "companion"
    assert presence.bearing_from_prompt("how do I lower my resting rate?") is None


def test_the_chat_reply_says_which_bearing_it_used(client):
    """An adaptation nobody can see is an uncanny one. The same principle
    `adapted_tone` already carries: the turn that changed it says so."""
    user = enroll(client)
    body = client.post(f"/coach/{user}", json={
        "area": "health_fitness",
        "message": "Keep it professional please, no small talk."}).json()
    assert body["bearing"] == "professional"
    assert body["adapted_bearing"] == "professional", (
        "it changed the bearing and did not say so on the turn that did it")
    again = client.post(f"/coach/{user}", json={
        "area": "health_fitness", "message": "What should I eat today?"}).json()
    assert again["bearing"] == "professional", "the change did not stick"
    assert again["adapted_bearing"] is None, (
        "a turn that changed nothing is announcing a change")


def test_professional_declines_the_warmth_and_keeps_what_was_noticed(client):
    """Both halves in one test, because either alone is misleading.

    A quiet week has nothing but curiosity and company to offer, and
    professional says nothing. Three low check-ins is evidence, and
    professional still speaks — the dial never silences a beat that was
    earned.
    """
    user = enroll(client)
    client.put(f"/presence/{user}/bearing", json={"bearing": "professional"})
    quiet = client.get(f"/presence/{user}/beat?slot=morning").json()
    assert quiet["speak"] is False
    assert quiet["bearing"] == "professional"

    for _ in range(3):
        client.post(f"/checkin/{user}", json={"mood": 1, "energy": 1})
    noticed = client.get(f"/presence/{user}/beat?slot=morning").json()
    assert noticed["speak"] is True, noticed
    assert noticed["register"] == "noticing", (
        "the dial silenced a beat that was earned by evidence")


def test_company_is_a_beat_that_wants_nothing_and_goes_last(client):
    """A line that asks nothing is the one a person can receive on a bad day
    without owing an answer. It is last in the order, so it can never take
    the place of something that was actually noticed."""
    user = enroll(client)
    body = client.get(f"/presence/{user}/beat?slot=morning").json()
    if body["register"] == "company":
        assert body["wants_reply"] is False
        assert body["line_key"].startswith("presence.company.")

    # And it yields: with three low check-ins there is something real to say,
    # and company does not get the slot.
    for _ in range(3):
        client.post(f"/checkin/{user}", json={"mood": 1, "energy": 1})
    noticed = client.get(f"/presence/{user}/beat?slot=midday").json()
    assert noticed["register"] != "company"


def test_the_lonely_run_points_at_people_rather_than_at_itself(client):
    """The beat this whole module exists to get right.

    Three consecutive days of talking to this and to nobody else it can see,
    and the next beat is **toward people** — a different direction, not a
    warmer sentence. Recorded beats are the evidence, because they are what
    this deployment actually holds.
    """
    from datetime import date, timedelta

    from jim import db
    user = enroll(client)
    conn = db.connect()
    for back in (3, 2, 1):
        day = (date.today() - timedelta(days=back)).isoformat()
        conn.execute(
            "INSERT INTO presence_beats (user_id, slot, register, area,"
            " line_key, created_at) VALUES (?,?,?,?,?,?)",
            (user, "morning", "quiet", None, "presence.quiet.nothing",
             f"{day}T09:00:00+00:00"))
    conn.commit()

    body = client.get(f"/presence/{user}/beat?slot=morning").json()
    assert body["speak"] is True, body
    assert body["register"] == "toward_people", body
    assert body["line_key"] in ("presence.people.alone",
                                "presence.people.offer")
    assert body["because"]


def test_both_bearings_notice_the_isolation(client):
    """Somebody who asked for professional asked for less chat. They did not
    ask for a guardian that watches them get lonelier in silence, and this is
    the one place the dial must not reach."""
    from datetime import date, timedelta

    from jim import db
    user = enroll(client)
    client.put(f"/presence/{user}/bearing", json={"bearing": "professional"})
    conn = db.connect()
    for back in (3, 2, 1):
        day = (date.today() - timedelta(days=back)).isoformat()
        conn.execute(
            "INSERT INTO presence_beats (user_id, slot, register, area,"
            " line_key, created_at) VALUES (?,?,?,?,?,?)",
            (user, "morning", "quiet", None, "presence.quiet.nothing",
             f"{day}T09:00:00+00:00"))
    conn.commit()

    body = client.get(f"/presence/{user}/beat?slot=morning").json()
    assert body["register"] == "toward_people", (
        "the professional bearing swallowed the isolation signal")


def test_somebody_who_did_reach_people_is_left_alone(client):
    """The other direction, and the one that keeps this from being a nag. A
    person who opened a room or asked a specialist this week has already done
    the thing; saying it to them anyway is a product talking to itself."""
    from datetime import date, timedelta

    from jim import db
    user = enroll(client)
    conn = db.connect()
    for back in (3, 2, 1):
        day = (date.today() - timedelta(days=back)).isoformat()
        conn.execute(
            "INSERT INTO presence_beats (user_id, slot, register, area,"
            " line_key, created_at) VALUES (?,?,?,?,?,?)",
            (user, "morning", "quiet", None, "presence.quiet.nothing",
             f"{day}T09:00:00+00:00"))
    conn.execute(
        "INSERT INTO events (user_id, type, detail, created_at)"
        " VALUES (?,?,?,?)",
        (user, "community_room_opened", "{}", db.utcnow()))
    conn.commit()

    body = client.get(f"/presence/{user}/beat?slot=morning").json()
    assert body["register"] != "toward_people", (
        "they already reached people this week and it said it anyway")


def test_the_new_lines_are_keys_like_every_other_one(client):
    """The rule the whole presence keeps: a sentence composed on the server
    is a sentence exactly one reader can read."""
    for key in ("presence.company.here", "presence.company.weather",
                "presence.people.alone", "presence.people.offer"):
        assert key in presence.LINES, key
        assert presence.LINES[key].strip()


def test_the_bearing_is_not_a_way_around_the_boundaries(client):
    """Neither bearing is a posture, and neither unlocks one. The refusals
    answer identically in both, because a boundary with a dial behind it is a
    default."""
    user = enroll(client)
    before = client.get("/presence").json()["boundaries"]
    client.put(f"/presence/{user}/bearing", json={"bearing": "professional"})
    assert client.get("/presence").json()["boundaries"] == before
    client.put(f"/presence/{user}/bearing", json={"bearing": "companion"})
    assert client.get("/presence").json()["boundaries"] == before
