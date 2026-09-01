"""The Guardian's walkthrough.

QRME's guide is deliberately faceless; this one is deliberately not, and the
first test is about why. Everything else mirrors QRME — most importantly the
coverage guard, because a walkthrough that can silently fall behind the app
teaches somebody a product that no longer exists.
"""

import pathlib

import pytest

from jim import tutorial


def test_the_guardian_gives_the_tour_rather_than_a_faceless_guide(client):
    """The one place this deliberately differs from QRME.

    QRME's subject is synthetic people, so a guide with a persona would be the
    most convincing one on the platform. JIM-mini has exactly one voice and it
    is not pretending to be anybody — a separate faceless guide would be a
    *second* voice in a product built on there being one, and the first thing
    a new user would learn is that JIM talks to them from two places.
    """
    assert "your Guardian" in tutorial.GUIDE
    assert "same one that watches your signals" in tutorial.GUIDE


def test_every_screen_is_covered_by_a_lesson(client):
    """Add a feature, draw its screen, and the walkthrough fails until
    somebody has said what it is for."""
    root = pathlib.Path(__file__).resolve().parents[2] / "docs" / "screens"
    drawn = {int(p.name.split("-", 1)[0]) for p in root.iterdir()
             if p.suffix in (".svg", ".png")
             and p.name.split("-", 1)[0].isdigit()}
    taught = set()
    for lesson in tutorial.LESSONS:
        taught.update(lesson["screens"])
    missing = sorted(drawn - taught)
    assert not missing, f"screens no lesson explains: {missing}"


def test_no_lesson_points_at_a_screen_that_is_not_there(client):
    root = pathlib.Path(__file__).resolve().parents[2] / "docs" / "screens"
    drawn = {int(p.name.split("-", 1)[0]) for p in root.iterdir()
             if p.suffix in (".svg", ".png")
             and p.name.split("-", 1)[0].isdigit()}
    for lesson in tutorial.LESSONS:
        stale = sorted(set(lesson["screens"]) - drawn)
        assert not stale, f"{lesson['key']} points at missing: {stale}"


def test_it_never_fires_anything_for_you(client):
    """In a product whose actions reach a real person's phone at three in the
    morning, a demonstration that fires for real is not a demonstration."""
    import inspect

    src = inspect.getsource(tutorial)
    for act in ("escalate(", "notify(", "send(", "alarm(", "dispatch("):
        assert act not in src, f"{act!r} reaches the walkthrough"
    for write in ("INSERT INTO", "UPDATE ", "DELETE FROM"):
        for line in src.splitlines():
            if write in line:
                assert "tutorial_progress" in line, line


def test_it_works_with_no_model_configured(client):
    import inspect

    src = inspect.getsource(tutorial)
    for provider in ("llm.", "get_provider", "anthropic", "openai"):
        assert provider not in src
    assert tutorial.outline()["lessons_count"] == len(tutorial.LESSONS)


def test_voice_drops_the_screen_numbers(client):
    """Voice matters more here than in QRME: this is used hands-free, often by
    somebody who is not well."""
    spoken = tutorial.step("mic", "voice")
    written = tutorial.step("mic", "text")
    assert spoken["screens"] == [] and written["screens"]
    assert spoken["title"] == written["title"]
    for lesson in tutorial.LESSONS:
        assert lesson["what"] in tutorial.say(lesson, "voice")["speak"]


def test_it_walks_in_order_and_remembers(client):
    first = client.post("/tutorial/start", json={"learner_id": "u1"}).json()
    assert first["next_lesson"]["key"] == tutorial.LESSONS[0]["key"]
    nxt = client.post("/tutorial/done",
                      json={"learner_id": "u1",
                            "lesson": first["next_lesson"]["key"]}).json()
    assert nxt["done"] == 1
    assert client.get("/tutorial/progress/u1").json()["next_lesson"]["key"] == \
        tutorial.LESSONS[1]["key"]


def test_progress_is_per_step_not_a_cursor(client):
    client.post("/tutorial/start", json={"learner_id": "u2"})
    client.post("/tutorial/done", json={"learner_id": "u2", "lesson": "mic"})
    out = client.get("/tutorial/progress/u2").json()
    assert out["done"] == 1 and out["next_lesson"]["key"] == tutorial.LESSONS[0]["key"]


def test_a_screen_can_ask_which_lesson_it_is(client):
    assert client.get("/tutorial/for-screen/12").json()["key"] == "mic"
    assert client.get("/tutorial/for-screen/9999").status_code == 404


def test_the_outline_is_public_and_chaptered(client):
    out = client.get("/tutorial").json()
    assert [c["chapter"] for c in out["chapters"]] == list(tutorial.CHAPTERS)
    assert out["guide"] == tutorial.GUIDE


def test_an_unknown_step_is_a_404(client):
    assert client.get("/tutorial/steps/nothing").status_code == 404


# -- the questions the other two suites already ask, asked here too -----------


def test_an_unknown_mode_is_refused(client):
    with pytest.raises(tutorial.TutorialError):
        tutorial.step(tutorial.LESSONS[0]["key"], "semaphore")


def test_both_modes_come_from_one_lesson(client):
    """Two hand-written versions would drift, and the spoken one would be
    the one nobody re-read."""
    for lesson in tutorial.LESSONS:
        spoken = tutorial.say(lesson, "voice")["speak"]
        assert lesson["what"] in spoken
        assert lesson["try_it"] in spoken


def test_the_order_introduces_nothing_before_it_exists(client):
    """You are enrolled before you are watched over, and watched over
    before the life layer builds on it. Asserted by chapter order rather
    than by reading."""
    order = [le["chapter"] for le in tutorial.LESSONS]
    assert order == sorted(order, key=lambda c: tutorial.CHAPTERS.index(c))
    assert tutorial.CHAPTERS[0] == "Getting started"


def test_the_walkthrough_writes_nothing_but_progress(client):
    """A tutorial that took a reading or armed an alarm "to show you how"
    would act on somebody's account before they understood what it was."""
    import inspect

    src = inspect.getsource(tutorial)
    for write in ("INSERT INTO", "UPDATE ", "DELETE FROM"):
        for line in src.splitlines():
            if write in line:
                assert "tutorial_progress" in line, (
                    f"the walkthrough writes outside its own progress: {line}")


def test_an_ordinary_question_still_gets_an_answer(client):
    """The walkthrough match must not swallow the help box."""
    out = client.post("/help",
                      json={"question": "where are my medications"}).json()
    assert "walkthrough" not in out
    assert out["answer"].strip()


def test_the_assistant_can_speak_the_tour(client):
    """Voice is a mode on the existing help box rather than a second
    endpoint: a spoken assistant and a written one answering differently is
    two products, and the spoken one would be the one nobody re-read."""
    spoken = client.post("/help", json={"question": "show me around",
                                        "mode": "voice"}).json()
    written = client.post("/help", json={"question": "show me around"}).json()
    assert spoken["walkthrough"]["next_lesson"]["screens"] == []
    assert written["walkthrough"]["next_lesson"]["screens"]
    assert spoken["answer"] and written["answer"]
