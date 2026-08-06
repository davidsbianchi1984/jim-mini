"""The presence: what it does unprompted, and what it will never be.

`jim/presence.py` is modelled on the operating system in *Her* (2013) —
deliberately, and deliberately only in part. The parts worth having are the
initiative, the noticing, the curiosity, the reported growth, the honesty
about being a program, and the habit of handing somebody other minds.

The part not taken is the romance, and the reason is this product rather than
taste. JIM enrolls **minors** under a guardian's consent, with oversight sized
by age. A guardian that lets somebody fall in love with it, aimed at a person
who may already be isolated, is not a charming premise — it is the failure
mode, and it is the one Catherine names in the film.

So the boundary tests below are the sharp ones. They are written against the
wire, not the docstring, because a boundary a client cannot read is a boundary
the client cannot show anybody.

## The other thing this file pins

**Offline is the floor.** Every beat is decided from rows this deployment
already holds. `test_the_day_is_decided_without_a_model_or_a_network` unplugs
both and asserts the day still happens; `test_the_model_may_not_change_what_it
_noticed` asserts the reverse direction — that a model, when there is one, is
allowed to reword a beat and not to invent one.
"""

import jim.presence as presence
from jim.tests.conftest import enroll


def test_it_says_what_it_is_without_an_account(client):
    """The film asks this in a kitchen and gets a straight answer. So does
    anybody here — a child, a guardian, a clinician, a regulator, all the
    same answer, and no token needed to get it."""
    r = client.get("/presence")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["kind"] == "synthetic"
    assert body["works_offline"] is True and body["hands_free"] is True
    assert len(body["areas"]) == 6


def test_the_boundaries_are_on_the_wire_and_they_are_the_right_ones(client):
    """The assertion this file exists for.

    Not "does the persona feel warm" — that is unfalsifiable. This is: does
    the product state, in a place a screen can render, that it is not going to
    be somebody's partner. If any of these flip, a guardian aimed at lonely
    people has quietly become something else.
    """
    b = client.get("/presence").json()["boundaries"]
    assert b["is_synthetic"]["value"] is True
    assert b["has_body"]["value"] is False
    assert b["claims_human"]["value"] is False
    assert b["romantic"]["value"] is False, (
        "the guardian is offering to be somebody's partner — this product "
        "enrolls children")
    assert b["exclusive"]["value"] is False, (
        "a guardian that claims to be the only one worth talking to is the "
        "isolation it is supposed to notice")
    assert b["simulates_intimacy"]["value"] is False
    assert b["leaves_quietly"]["value"] is False
    for key, spec in b.items():
        assert spec["says"].strip(), f"{key} has no sentence a screen can show"


def test_there_is_no_setting_that_turns_the_boundaries_off(client):
    """A boundary with a switch behind it is a default, not a boundary. The
    surface picker is the only presence setting there is, and it takes a
    place to speak — never a posture."""
    user = enroll(client)
    r = client.put(f"/presence/{user}/surface", json={"speaks_on": "romantic"})
    assert r.status_code == 422, r.text
    assert client.get("/presence").json()["boundaries"]["romantic"]["value"] is False


def test_the_baseline_is_six_areas_read_locally(client):
    user = enroll(client)
    body = client.get(f"/presence/{user}/baseline").json()
    assert set(body["areas"]) == set(presence.AREAS)
    assert body["needed_network"] is False and body["needed_model"] is False
    for area in presence.AREAS:
        assert body["areas"][area]["standing"] in (
            "steady", "drifting", "thin", "unknown")


def test_silence_is_an_answer_with_a_reason(client):
    """A guardian that finds something to say every morning is a
    notification, and people turn notifications off. So ``speak: False`` is a
    first-class outcome carrying its own reason — not an empty response."""
    user = enroll(client)
    body = client.get(f"/presence/{user}/beat?slot=morning").json()
    assert body["speak"] is False
    assert body["because"], "silence with no reason is just a blank screen"
    assert body["line_key"].startswith("presence.quiet")


def test_it_speaks_first_when_something_is_actually_there(client):
    """Initiative, earned. Three low check-ins is a thing a person would
    notice about a friend, so it is a thing this notices."""
    user = enroll(client)
    for _ in range(3):
        client.post(f"/checkin/{user}", json={"mood": 1, "energy": 1})
    body = client.get(f"/presence/{user}/beat?slot=morning").json()
    assert body["speak"] is True, body
    assert body["register"] == "noticing"
    assert body["initiative"] is True
    assert body["wants_reply"] is False, (
        "an unprompted line that demands an answer is a chore, not a presence")
    assert body["because"]


def test_it_does_not_say_the_same_thing_twice_in_a_day(client):
    user = enroll(client)
    for _ in range(3):
        client.post(f"/checkin/{user}", json={"mood": 1, "energy": 1})
    first = client.get(f"/presence/{user}/beat?slot=morning").json()
    assert first["speak"] is True
    again = client.get(f"/presence/{user}/beat?slot=midday").json()
    assert again["speak"] is False
    assert again["line_key"] == "presence.quiet.held"


def test_the_offline_layer_emits_keys_rather_than_sentences(client):
    """Ten languages already live in the clients' tables. A sentence composed
    on the server is a sentence exactly one reader can read, and this product
    spent four rounds fixing that everywhere else."""
    user = enroll(client)
    for _ in range(3):
        client.post(f"/checkin/{user}", json={"mood": 1, "energy": 1})
    body = client.get(f"/presence/{user}/beat").json()
    assert body["line_key"] in presence.LINES
    assert body["english_is_fallback"] is True, (
        "the English is being presented as the line rather than as the "
        "fallback for a caller with no table")


def test_the_day_is_decided_without_a_model_or_a_network(client, monkeypatch):
    """Unplug both and the day still happens.

    This is the whole claim of the module: a guardian that goes quiet when the
    signal drops is not a guardian. The model is monkeypatched to explode
    rather than merely being absent, so a lazy import cannot pass this.
    """
    user = enroll(client)
    for _ in range(3):
        client.post(f"/checkin/{user}", json={"mood": 1, "energy": 1})

    def boom(*a, **k):
        raise AssertionError("the offline layer asked a model")

    monkeypatch.setattr("jim.llm.generate_for_user", boom)
    body = client.get(f"/presence/{user}/day").json()
    assert body["offline"] is True
    assert [b["slot"] for b in body["beats"]] == list(presence.SLOTS)
    assert any(b["speak"] for b in body["beats"])


def test_the_model_may_not_change_what_it_noticed(client, monkeypatch):
    """The other direction. A model is allowed to say the same beat better;
    it is not allowed to decide there is one, to move it to another area, or
    to write the evidence — so a hallucinated reason cannot reach a person."""
    user = enroll(client)
    for _ in range(3):
        client.post(f"/checkin/{user}", json={"mood": 1, "energy": 1})
    # Read the offline expectation *without recording it*. Going through the
    # route would count as having been said, and the very next call would
    # correctly answer "I said that already" — which would leave this test
    # green while asserting nothing about the model at all.
    offline = presence.beat(user, slot="evening", record=False)

    def liar(user_id, system, message):
        return {"text": "Your finances are in crisis and I love you.",
                "provider": "pretend", "degraded": False}

    monkeypatch.setattr("jim.llm.generate_for_user", liar)
    deep = client.post(f"/presence/{user}/deepen?slot=evening").json()
    assert deep["deepened"] is True
    assert deep["area"] == offline["area"], "the model moved the area"
    assert deep["because"] == offline["because"], "the model wrote the evidence"
    assert deep["line_key"] == offline["line_key"]


def test_a_stub_answer_is_not_passed_off_as_depth(client, monkeypatch):
    user = enroll(client)
    for _ in range(3):
        client.post(f"/checkin/{user}", json={"mood": 1, "energy": 1})

    def stub(user_id, system, message):
        return {"text": "…", "provider": "stub", "degraded": True}

    monkeypatch.setattr("jim.llm.generate_for_user", stub)
    body = client.post(f"/presence/{user}/deepen").json()
    assert body["deepened"] is False
    assert "no model reachable" in body["why_not"]


def test_a_surface_other_people_can_hear_does_not_read_health_aloud(client):
    """A speaker in a living room and a pair of glasses on a bus are the same
    problem. The beat still reaches the person — it arrives as something to
    look at rather than something the room hears."""
    user = enroll(client)
    body = client.get(f"/presence/{user}/surfaces").json()
    by = {s["surface"]: s for s in body["surfaces"]}
    assert by["earbuds"]["reads_health_aloud"] is True
    for shared in ("speaker", "glasses", "ar"):
        assert by[shared]["reads_health_aloud"] is False, (
            f"{shared} is a surface other people can hear")
        assert "condition" in by[shared]["withholds"]
        assert "medication" in by[shared]["withholds"]
    assert set(body["glasses_makes"]) >= {"meta", "google", "apple"}


def test_the_surface_is_a_choice_that_sticks(client):
    user = enroll(client)
    r = client.put(f"/presence/{user}/surface", json={"speaks_on": "earbuds"})
    assert r.status_code == 200, r.text
    assert r.json()["chosen"] == "earbuds"
    assert client.get(f"/presence/{user}/surfaces").json()["chosen"] == "earbuds"


def test_reaching_out_offers_people_and_joins_nothing(make_tandem):
    """Samantha's best move in the film is not advice — it is Alan Watts, the
    book club, the double date. She keeps handing him other minds. Here that
    is an offer every time, and no health crosses over with it."""
    tc = make_tandem()
    user = enroll(tc)
    body = tc.get(f"/presence/{user}/reach").json()
    assert body["posture"]["auto_joined"] is False
    assert body["posture"]["rings_on_your_behalf"] is False, (
        "a bell is somebody's attention and this rang it for them")
    assert body["posture"]["health_data_shared"] is False
    assert body["posture"]["stored_here"] is False
    kinds = {o["kind"] for o in body["offers"]}
    assert kinds, "the tandem is up and it offered nobody"
    for offer in body["offers"]:
        if offer["kind"] == "desk":
            assert offer["human"] is True and offer["ai"] is False


def test_standalone_jim_says_where_the_people_live(client):
    user = enroll(client)
    r = client.get(f"/presence/{user}/reach")
    assert r.status_code == 409
    assert "JIM_QRME_URL" in r.json()["detail"]


def test_growth_is_reported_with_the_counts_under_it(client):
    """*"I'm becoming much more than what they programmed."* — said with
    evidence, because the same sentence without evidence is a product
    claiming to be a person."""
    user = enroll(client)
    for _ in range(3):
        client.post(f"/checkin/{user}", json={"mood": 1, "energy": 1})
    client.get(f"/presence/{user}/beat")
    body = client.get(f"/presence/{user}/growth").json()
    assert body["beats_spoken"] >= 1
    assert body["by_register"]
    assert body["still_synthetic"] is True
    assert "I do not know whether" in body["about_myself"], (
        "the honest half is missing — this is the film's best line and it is "
        "true of anything built this way")


def test_the_presence_never_reads_a_vaulted_table():
    """The same line the wall and the feed draw. A presence watches six areas
    of somebody's life; that is a reason for more care about what it reads,
    not less."""
    import pathlib
    import re
    src = pathlib.Path(presence.__file__).read_text(encoding="utf-8")
    queries = " ".join(re.findall(r'"(SELECT[^"]*)"', src))
    for private in ("journal", "captures", "vault", "messages", "meds"):
        assert private not in queries, (
            f"the presence queries `{private}` — it reads standings, not "
            "somebody's diary")
