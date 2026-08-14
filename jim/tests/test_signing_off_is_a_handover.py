"""Leaving does not mean going unwatched.

An engaged session is the online model. It is expensive, it needs a network,
and a person cannot stay in one. So the interesting moment is not opening one —
it is the moment they leave, because that is where a product either keeps
looking after somebody or quietly stops.

    asked     did the session close cleanly
    mattered  is anybody still watching afterwards

`engaged.sign_off` does three things, and this file checks each of them
separately because they fail separately:

**The session closes.** One open engagement per person, ever, so a sign-off
that did not close would leave two sessions competing for one transcript.

**What it was about is deposited.** Into `jim/pipeline.py` — the same store
the offline stack predicts from, and the same path a paid coach turn already
takes. A conversation that vanished at sign-off would be the second half of
this feature missing while the first half looked finished.

**What they named becomes a standing watch.** Carried into every offline coach
answer, and raised unprompted by `presence.beat`. This is the half a person
actually notices: they said *keep an eye on my sleep* on their way out, and
tomorrow morning something asks about their sleep.

## The paywall that would have stranded somebody

`/engaged/*` is a paid capability, and the first version of the gate covered
the whole prefix — including sign-off. A plan that lapsed mid-session would
have left the session open forever, undeposited, with the handover never made
and no way to end it. `jim/tiers.py` has a paragraph about a paywall in front
of an alarm; this is the same shape one floor down, and the exemption is
checked here rather than trusted to the comment.
"""

from __future__ import annotations

import pytest

from jim import coach, engaged, presence, tiers
from jim.api import app

from .conftest import enroll


class _Scripted:
    """A model standing in for an online one — see the note in
    `test_every_act_can_be_taken_back.py` on why `answered_by` is load-bearing
    rather than decoration."""

    answered_by = "claude"
    failure = None

    def __init__(self, lines):
        self.lines = list(lines)

    def generate(self, system, user):
        return self.lines.pop(0) if self.lines else "Done."


def _script(monkeypatch, *lines):
    from jim import llm
    provider = _Scripted(lines)
    monkeypatch.setattr(llm, "get_provider",
                        lambda cloud=None, choice=None: provider)


@pytest.fixture()
def talked(client, monkeypatch):
    """Somebody who engaged, said something, and is about to leave."""
    uid = enroll(client)
    client.post(f"/engaged/{uid}", json={"area": "mental_health"})
    _script(monkeypatch, "I hear you. Third bad night is worth naming.")
    client.post(f"/engaged/{uid}/turn",
                json={"message": "I have not slept properly in three nights"})
    return uid


def test_signing_off_closes_the_session(client, talked):
    out = client.post(f"/engaged/{talked}/sign-off", json={"topics": []})
    assert out.status_code == 200, out.text
    assert out.json()["signed_off"] is True
    assert client.get(f"/engaged/{talked}").json()["engaged"] is False


def test_a_closed_session_cannot_be_spoken_into(client, talked):
    """Refused rather than silently reopened.

    Reopening on the next message would make sign-off meaningless — the
    handover would fire and then the session it handed over would carry on.
    """
    client.post(f"/engaged/{talked}/sign-off", json={"topics": []})
    refused = client.post(f"/engaged/{talked}/turn", json={"message": "hi"})
    assert refused.status_code == 409
    assert refused.json()["refusal"] == "engaged.not_engaged"


def test_engaging_twice_is_the_same_session(client):
    """"Engaged" is a state somebody is in, not a resource they accumulate.

    A console that reopens on every mount, or a phone coming back from the
    background, must not leave a trail of half-sessions each holding part of
    one conversation.
    """
    uid = enroll(client)
    first = client.post(f"/engaged/{uid}", json={"area": "personal_growth"})
    second = client.post(f"/engaged/{uid}", json={"area": "career"})
    assert first.json()["id"] == second.json()["id"]


def test_what_the_session_was_about_reaches_the_offline_store(client, talked,
                                                              monkeypatch):
    """The deposit, through `pipeline` — the same door a paid coach turn uses.

    Without it the online model's work would be bought once and thrown away,
    which is exactly what `pipeline.deposit` was written to stop.
    """
    seen = []
    from jim import pipeline
    real = pipeline.deposit
    monkeypatch.setattr(pipeline, "deposit",
                        lambda *a, **k: (seen.append(a), real(*a, **k))[1])
    out = client.post(f"/engaged/{talked}/sign-off", json={"topics": []})
    assert out.json()["deposited"] == 1
    assert seen and seen[0][0] == talked
    assert "slept" in seen[0][2]


def test_a_store_that_refuses_the_deposit_does_not_cost_a_sign_off(
        client, talked, monkeypatch):
    """The session is already closed when the deposit runs, and on purpose.

    Somebody leaving must be able to leave. A handover that could fail closed
    would make the exit depend on a subsystem the person cannot see and did
    not ask about.
    """
    from jim import pipeline
    monkeypatch.setattr(pipeline, "deposit",
                        lambda *a, **k: (_ for _ in ()).throw(RuntimeError()))
    out = client.post(f"/engaged/{talked}/sign-off", json={"topics": []})
    assert out.status_code == 200
    assert out.json()["deposited"] == 0
    assert client.get(f"/engaged/{talked}").json()["engaged"] is False


def test_what_they_named_becomes_a_standing_watch(client, talked):
    out = client.post(f"/engaged/{talked}/sign-off",
                      json={"topics": ["my sleep", "the new job"]})
    kept = [w["topic"] for w in out.json()["watches"]]
    assert kept == ["my sleep", "the new job"]
    assert [w["topic"] for w in
            client.get(f"/engaged/{talked}/watches").json()] == kept


def test_the_offline_coach_is_carrying_them(client, talked):
    """The handover made concrete.

    `coach._context` builds what the offline model is told before it answers.
    A watch that lived in a table and never reached this string would be a
    promise kept in a database and nowhere a person could feel it.
    """
    client.post(f"/engaged/{talked}/sign-off", json={"topics": ["my sleep"]})
    context = coach._context(talked)
    assert "keep an eye on these" in context
    assert "my sleep" in context


def test_the_guardian_raises_it_unprompted(client, talked):
    """And says it out loud, without being asked.

    `presence.beat` is the unprompted half of this product. A standing watch
    that only surfaced when somebody happened to open the coach would be a
    watch they had to remember to check — which is the opposite of the thing
    they asked for on their way out.
    """
    client.post(f"/engaged/{talked}/sign-off", json={"topics": ["my sleep"]})
    beat = presence.beat(talked, "morning", record=False)
    assert beat["speak"] is True
    assert beat["line_key"] == "presence.nudge.watching"
    assert "my sleep" in beat["english"]


def test_a_watch_is_never_read_aloud_on_a_shared_surface():
    """It is the person's own sentence about whatever was on their mind.

    Money, a diagnosis, somebody they live with. There is no category that
    covers "anything they might have said", so this line is not spoken in
    company at all — `carries` returns everything for it, which is how the
    surface picker withholds it.
    """
    carried = presence.carries("presence.nudge.watching")
    assert set(carried) == set(presence.NOT_ALOUD_IN_COMPANY)


def test_the_same_thing_is_not_watched_twice(client):
    uid = enroll(client)
    client.post(f"/engaged/{uid}/watches", json={"topic": "my sleep"})
    client.post(f"/engaged/{uid}/watches", json={"topic": "My Sleep"})
    assert len(client.get(f"/engaged/{uid}/watches").json()) == 1


def test_the_watch_list_has_a_ceiling(client, monkeypatch):
    """A Guardian watching for forty things is watching for nothing.

    The point of the list is that it changes what gets raised, and a list
    long enough to contain everything changes nothing.
    """
    uid = enroll(client)
    monkeypatch.setattr(engaged, "WATCH_CEILING", 2)
    for topic in ("one", "two"):
        assert client.post(f"/engaged/{uid}/watches",
                           json={"topic": topic}).status_code == 201
    full = client.post(f"/engaged/{uid}/watches", json={"topic": "three"})
    assert full.status_code == 409
    assert full.json()["refusal"] == "engaged.watching_enough"


def test_a_watch_can_be_taken_off_the_list(client):
    uid = enroll(client)
    made = client.post(f"/engaged/{uid}/watches", json={"topic": "my sleep"})
    assert client.delete(
        f"/engaged/{uid}/watches/{made.json()['id']}").status_code == 200
    assert client.get(f"/engaged/{uid}/watches").json() == []
    assert coach._context(uid).count("keep an eye") == 0


def test_one_persons_watches_are_not_another_persons(client):
    first = enroll(client)
    client.post(f"/engaged/{first}/watches", json={"topic": "mine"})
    made = client.get(f"/engaged/{first}/watches").json()[0]
    second = enroll(client)          # becomes the client's default caller
    assert client.get(f"/engaged/{second}/watches").json() == []
    denied = client.delete(f"/engaged/{second}/watches/{made['id']}")
    assert denied.status_code == 404


# --------------------------------------------------------------------------- #
# The paywall that would have stranded somebody
# --------------------------------------------------------------------------- #

def test_a_lapsed_plan_can_still_sign_off_and_still_undo():
    """Read off the gate table rather than driven, because what is under test
    is the rule and not one account's state.

    Opening a session and speaking into it are a paid capability, and that is
    a fair thing to charge for. The exit is not the product, and neither is
    the way back out of a change somebody did not want.
    """
    assert tiers.capability_for("POST", "/engaged/usr_1") == "synthetic_agents"
    assert tiers.capability_for("POST", "/engaged/usr_1/turn") \
        == "synthetic_agents"
    assert tiers.capability_for("POST", "/engaged/usr_1/sign-off") is None
    assert tiers.capability_for("POST",
                                "/engaged/usr_1/acts/act_1/undo") is None


def test_the_reach_is_readable_without_a_plan_or_a_token(client):
    """How somebody decides whether to open one at all.

    Behind the paywall it would be a list of what a feature *would* be
    allowed to touch, shown only to people who had already bought it.
    """
    assert tiers.capability_for("GET", "/engaged/reach") is None
    out = client.get("/engaged/reach", headers={})
    assert out.status_code == 200
    can = out.json()["can"]
    assert len(can) == len(engaged.TOOLS)
    assert any(row["acts"] for row in can) and any(not row["acts"]
                                                  for row in can)


def test_an_offline_turn_says_so_instead_of_answering(client, monkeypatch):
    """The one place this surface may not degrade gracefully.

    `coach.reply` degrades well: when the stub answers, the offline pipeline
    takes over and produces something genuinely useful. That is right for a
    screen whose job is to *say* something.

    This screen's job is to *do* something, and the stub cannot ask for a
    tool. Left to fall through, an engaged session on a box with no key would
    answer in canned prose, take no action, and look exactly like one that
    had considered the request and decided against it.

        asked     did the turn come back with text
        mattered  did the model that can act answer it
    """
    uid = enroll(client)
    client.post(f"/engaged/{uid}", json={"area": "personal_growth"})

    from jim import llm
    monkeypatch.setattr(llm, "get_provider",
                        lambda cloud=None, choice=None: llm.StubProvider())
    monkeypatch.setattr(llm, "get_choice", lambda _uid: "claude")

    turn = client.post(f"/engaged/{uid}/turn",
                       json={"message": "set me a goal about sleep"})
    assert turn.status_code == 200, turn.text
    body = turn.json()
    assert body["stopped"] == "engaged.needs_the_online_model"
    assert body["reply"] == ""
    assert body["did"] == []
    # And nothing was changed, which is the half the sentence promises.
    assert client.get(f"/goals/{uid}").json() == []
    # The session is still open — this is a turn that could not be served,
    # not a session that ended.
    assert client.get(f"/engaged/{uid}").json()["engaged"] is True


def test_the_stop_it_reports_has_a_sentence_a_person_can_read(client):
    """Every `stopped` key an engaged turn can carry resolves to words.

    The console renders `refusal.{stopped}`; a key with no sentence is a
    machine identifier shown where an explanation belongs.
    """
    for key in ("engaged.needs_the_online_model", "engaged.too_many_steps",
                "engaged.acted_enough"):
        assert key in engaged.REFUSALS, f"{key} has no sentence"


def test_the_reach_says_which_of_it_cannot_be_taken_back(client):
    """One bullet per tool, with the honest distinction on it.

    "read your journal" and "send your words to somebody outside this app"
    rendered as two identical lines is how a list stops being consent.
    """
    can = client.get("/engaged/reach").json()["can"]
    forever = [row for row in can if row["irreversible_because"]]
    assert [row["name"] for row in forever] == ["ask_specialist"]
    assert all(row["reversible"] for row in can
               if row["acts"] and not row["irreversible_because"])
