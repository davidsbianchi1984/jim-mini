""""Help us improve": product feedback on the app itself — open to anyone,
private per submitter, with a public aggregate tally. Distinct from the
guidance feedback loop keyed to a user."""

from jim.tests.conftest import enroll, as_user


def test_anyone_can_submit_and_it_tallies(client):
    # No auth header — an anonymous visitor can still be heard.
    r = client.post("/improve", json={"category": "idea",
                                       "message": "a family dashboard widget"})
    assert r.status_code == 201, r.text
    assert r.json()["status"] == "received"

    client.post("/improve", json={"category": "bug", "message": "watch sync stalls"})

    state = client.get("/improve").json()
    assert state["total"] == 2
    assert state["tally"]["idea"] == 1
    assert state["tally"]["bug"] == 1
    # An anonymous caller sees the tally but none of the words.
    assert state["mine"] == []


def test_bad_category_and_rating_and_message_refused(client):
    assert client.post("/improve", json={"category": "rant",
                                         "message": "x"}).status_code == 422
    assert client.post("/improve", json={"category": "idea",
                                         "message": "   "}).status_code == 422
    assert client.post("/improve", json={"category": "idea", "message": "ok",
                                         "rating": 9}).status_code == 422
    assert client.post("/improve", json={"category": "praise", "message": "love it",
                                         "rating": 5}).status_code == 201


def test_authenticated_submitter_sees_only_their_own(client):
    enroll(client)   # sets the client's default user token
    client.post("/improve", json={"category": "improvement",
                                  "message": "bigger buttons on the watch",
                                  "rating": 4})
    state = client.get("/improve").json()
    assert len(state["mine"]) == 1
    assert state["mine"][0]["message"] == "bigger buttons on the watch"
    assert state["mine"][0]["status"] == "received"


def test_two_users_dont_see_each_others_words(client):
    a = enroll(client, display_name="Ada")
    a_token = client.headers["authorization"].split()[1]
    client.post("/improve", json={"category": "idea", "message": "ada's idea"})

    b = enroll(client, display_name="Ben")   # switches the default caller to Ben
    b_token = client.headers["authorization"].split()[1]
    client.post("/improve", json={"category": "bug", "message": "ben's bug"})

    as_user(client, b_token)
    ben_view = client.get("/improve").json()
    assert [m["message"] for m in ben_view["mine"]] == ["ben's bug"]
    assert ben_view["total"] == 2          # tally spans everyone

    as_user(client, a_token)
    ada_view = client.get("/improve").json()
    assert [m["message"] for m in ada_view["mine"]] == ["ada's idea"]
    assert ada_view["total"] == 2
