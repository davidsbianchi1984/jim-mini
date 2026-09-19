"""The coach is the offline model, and what it lacks it asks for in general
terms — with every sentence that left written down for a person to read.

The loop existed: the offline stack answers from the store, a miss is a
gap, an errand goes and studies it through the sanitiser. What did not exist
was the posture a person actually asked for — *the coach answers me; when it
does not know, it goes and asks a model without taking me along* — because a
coach turn on a configured model sent the question as written, with the
context a coach turn carries, and the sanitiser only knew two names.

    asked     was the brief sanitised
    mattered  can a person read, word for word, everything that went

## What these guards hold

* the posture is its own permit, `asked` rather than assumed, and its
  sentence says what leaves and where to read it;
* the composer takes out every identifier and every exact value — names,
  contacts, links, phones, dates, times, ages, readings, bare numbers — and
  turns the first person into the third; what it took out is kept here and
  is never in the sentence;
* under the permit a question the store can answer reaches no model at all;
* a question the store cannot answer goes out once, in general terms, is
  learned, and the same question never goes out again;
* without the permit the turn goes as written — and is written down;
* every sentence that leaves by either door is on the ledger, and offline
  mode is not opened by the permit;
* there are exactly two doors out that write the ledger, and every other
  place a model is spoken to is named here so a new one is added on purpose.
"""

from __future__ import annotations

import inspect
import pathlib

import pytest

from jim import db, egress, llm, permits, research

from .conftest import enroll


class _Fake:
    """A model on another party's machine, at the provider boundary.

    Carries `answered_by` and `failure` the way the fallback wrapper does,
    so `generate_for_user` and the study path read who answered from the
    record rather than from the choice.
    """

    def __init__(self, name="anthropic"):
        self.answered_by, self.failure = name, None
        self.heard: list[tuple[str, str]] = []

    def generate(self, system, user):
        self.heard.append((system, user))
        return ("Wake-ups in the small hours are common; keep the room dark, "
                "avoid the clock, and get up after twenty minutes awake.")


@pytest.fixture()
def vendor(monkeypatch):
    """A keyed vendor model, chosen — the case where a coach turn would
    have gone out as written."""
    fake = _Fake()
    real = llm.is_configured
    monkeypatch.setattr(llm, "is_configured",
                        lambda n: True if n == "anthropic" else real(n))
    monkeypatch.setattr(llm, "_build",
                        lambda n: fake if n == "anthropic" else llm.StubProvider())
    return fake


def _allow(client, user_id, on=True):
    r = client.put(f"/engaged/{user_id}/permits/{egress.PERMIT}",
                   json={"granted": on})
    assert r.status_code == 200, r.text


def _ask(client, user_id, message, area="personal_growth"):
    r = client.post(f"/coach/{user_id}", json={"area": area,
                                               "message": message})
    assert r.status_code == 200, r.text
    return r.json()


# --------------------------------------------------------------------------
# The permit.
# --------------------------------------------------------------------------

def test_the_posture_is_its_own_yes_and_says_what_leaves():
    spec = permits.AREAS[egress.PERMIT]
    assert spec["standing"] == "asked"
    for word in ("general terms", "name", "number", "date", "log"):
        assert word in spec["says"], word


def test_it_starts_off(client):
    user_id = enroll(client)
    assert permits.granted(user_id, egress.PERMIT) is False


# --------------------------------------------------------------------------
# The composer.
# --------------------------------------------------------------------------

def test_the_composer_takes_out_every_identifier_and_value(client):
    user_id = enroll(client, display_name="Marguerite Dubois",
                     emergency_name="Ana Reyes", emergency_phone="+1 555 0100",
                     contact_consent=True)
    from jim import contacts, life
    life.set_source(user_id, contacts.SOURCE, True)
    r = client.put(f"/contacts/{user_id}", json={"entries": [
        {"name": "Tomasz", "number": "+48 601 234 567"}]})
    assert r.status_code == 200, r.text
    out = egress.compose(user_id, (
        "I'm 54 and I keep waking at 3am; my blood pressure was 150/95 on "
        "2026-09-12 and I take 50mg of metformin. Marguerite here — should "
        "I call Ana or Tomasz at +1 555 0100 or ana@clinic.org, see "
        "https://clinic.example/me, before March 3rd?"))
    s = out["sentence"]
    for private in ("Marguerite", "Ana", "Tomasz", "54", "3am", "150/95",
                    "2026-09-12", "50mg", "555", "clinic.org", "https://",
                    "March"):
        assert private not in s, (private, s)
    for marker in ("[private]", "[age]", "[time]", "[reading]", "[date]",
                   "[amount]", "[phone]", "[email]", "[link]"):
        assert marker in s, (marker, s)
    # The first person is gone; the subject is a person.
    assert " I " not in f" {s} " and "my " not in s.lower().split("their")[0]
    assert "a person" in s and "their" in s
    # What was taken out is kept here — and the names are not, even here.
    took = [k["took"] for k in out["kept"]]
    assert "3am" in took and "150/95" in took and "50mg" in took
    assert not any("Marguerite" in t or "Ana" in t for t in took)
    assert out["redactions"] >= len(out["kept"])


def test_a_general_question_is_left_alone(client):
    user_id = enroll(client)
    out = egress.compose(user_id, "how should a person structure barbell training")
    assert out["sentence"] == "how should a person structure barbell training"
    assert out["redactions"] == 0 and out["kept"] == []


# --------------------------------------------------------------------------
# Under the permit.
# --------------------------------------------------------------------------

def test_what_the_store_knows_reaches_no_model(client, vendor):
    user_id = enroll(client)
    llm.set_choice(user_id, "anthropic")
    _allow(client, user_id)
    body = _ask(client, user_id, "I keep having panic attacks and my pulse races",
                area="mental_health")
    assert body["delivered"] is True
    assert vendor.heard == [], "the store had this; nothing should have gone"
    assert body["provenance"]["asked_outside"] is None
    assert "offline coach" in body["provenance"]["method"]
    assert client.get(f"/egress/{user_id}").json()["count"] == 0


def test_what_the_store_lacks_goes_out_once_in_general_terms(client, vendor):
    user_id = enroll(client, display_name="Marguerite")
    llm.set_choice(user_id, "anthropic")
    _allow(client, user_id)
    question = "what helps Marguerite with a 3am wake-up, I'm 54"
    body = _ask(client, user_id, question)
    assert body["delivered"] is True
    # Exactly one sentence went, and it is not the question as written.
    assert len(vendor.heard) == 1
    framing, sentence = vendor.heard[0]
    assert framing == egress.FRAMING
    assert "Marguerite" not in sentence and "3am" not in sentence
    assert "54" not in sentence and " I" not in f" {sentence}"
    assert "wake-up" in sentence
    # The prompt a coach turn builds — with the person's context — did not.
    assert "Marguerite" not in framing and "check-in" not in framing.lower()
    # It is on the record, word for word, and the person can read it.
    prov = body["provenance"]["asked_outside"]
    assert prov["sentence"] == sentence and prov["left_host"] is True
    assert prov["answered_by"] == "anthropic" and prov["learned"] is True
    page = client.get(f"/egress/{user_id}").json()
    assert page["count"] == 1 and page["left"] == 1
    row = page["sentences"][0]
    assert row["sentence"] == sentence and row["framing"] == framing
    assert row["purpose"] == egress.PURPOSE and row["destination"] == "anthropic"
    assert any(k["took"] == "3am" for k in row["kept"])
    # The answer was learned where the offline coach reads it, and the
    # reply came from there.
    store = client.get(f"/coach/{user_id}/store").json()
    assert any("wake-up" in e["topic"] for e in store["excursions"])
    assert "small hours" in body["content"]
    # The miss is closed, so the study pass will not buy it again either.
    gap = db.connect().execute(
        "SELECT filled FROM gaps WHERE user_id=?", (user_id,)).fetchall()
    assert gap and all(g["filled"] for g in gap)


def test_the_same_gap_is_never_bought_twice(client, vendor):
    user_id = enroll(client)
    llm.set_choice(user_id, "anthropic")
    _allow(client, user_id)
    _ask(client, user_id, "what helps a 3am wake-up")
    _ask(client, user_id, "what helps a 3am wake-up")
    _ask(client, user_id, "remind me what helps with a 3am wake-up")
    assert len(vendor.heard) == 1
    assert client.get(f"/egress/{user_id}").json()["count"] == 1


def test_nobody_worth_asking_is_said_plainly(client):
    """On a machine with no model but the stub, the permit changes nothing
    about what leaves — nothing did — and the reply says so rather than
    learning the built-in helper's description of itself."""
    user_id = enroll(client)
    _allow(client, user_id)
    body = _ask(client, user_id, "what helps a 3am wake-up")
    assert body["delivered"] is True
    assert body["provenance"]["asked_outside"] is None
    assert "study list" in body["content"]
    assert client.get(f"/egress/{user_id}").json()["count"] == 0
    store = client.get(f"/coach/{user_id}/store").json()
    assert store["excursions"] == []


def test_offline_mode_is_not_opened_by_the_permit(client, vendor, monkeypatch):
    monkeypatch.setenv("JIM_OFFLINE", "1")
    user_id = enroll(client)
    llm.set_choice(user_id, "anthropic")
    _allow(client, user_id)
    _ask(client, user_id, "what helps a 3am wake-up")
    assert vendor.heard == []
    page = client.get(f"/egress/{user_id}").json()
    assert page["left"] == 0


# --------------------------------------------------------------------------
# Without the permit, and by the other door.
# --------------------------------------------------------------------------

def test_without_the_permit_the_turn_goes_as_written_and_is_written_down(client, vendor):
    user_id = enroll(client, display_name="Marguerite")
    llm.set_choice(user_id, "anthropic")
    question = "what helps Marguerite with a 3am wake-up"
    body = _ask(client, user_id, question)
    assert body["provenance"]["generated_by"] == "anthropic"
    assert len(vendor.heard) == 1 and vendor.heard[0][1] == question
    page = client.get(f"/egress/{user_id}").json()
    assert page["count"] == 1 and page["permitted"] is False
    row = page["sentences"][0]
    assert row["purpose"] == "coach" and row["sentence"] == question
    assert row["left_host"] is True and row["framing"] == vendor.heard[0][0]


def test_every_excursion_is_on_the_ledger(client):
    user_id = enroll(client, emergency_name="Ana Reyes")
    exc = client.post(f"/excursions/{user_id}", json={
        "topic": "sleep hygiene",
        "question": "can Ana Reyes be woken at 3am?"}).json()
    page = client.get(f"/egress/{user_id}").json()
    assert page["count"] == 1
    row = page["sentences"][0]
    assert row["purpose"] == "excursion" and row["sentence"] == exc["brief"]
    assert "Ana" not in row["sentence"] and "3am" not in row["sentence"]
    assert row["left_host"] is False and row["answered_by"] == "stub"


def test_an_errand_and_a_study_say_which_door_they_went_by(client):
    user_id = enroll(client)
    client.put(f"/engaged/{user_id}/permits/study_on_your_own",
               json={"granted": True})
    client.post(f"/coach/{user_id}", json={"area": "personal_growth",
                                           "message": "what helps a 3am wake-up"})
    client.post(f"/errands/{user_id}")
    client.post(f"/coach/{user_id}/study", json={"topic": "cold plunges"})
    purposes = {r["purpose"] for r in
                client.get(f"/egress/{user_id}").json()["sentences"]}
    assert {"errand", "study"} <= purposes


# --------------------------------------------------------------------------
# The doors.
# --------------------------------------------------------------------------

def test_both_doors_out_write_the_ledger():
    assert "egress.note(" in inspect.getsource(research.excursion)
    assert "egress.note(" in inspect.getsource(llm.generate_for_user)
    assert "egress.compose(" in inspect.getsource(research.excursion)


#: Every other place this product speaks to a provider directly, by file.
#: Each goes out on its own terms and its own module says what leaves;
#: none is the coach. A new one has to be added here on purpose, with a
#: reason, rather than arriving as a third door nobody wrote down.
SPEAKS_DIRECTLY = {
    "appedits.py",   # a drafted app edit, company oversight's own review
    "cloud.py",      # the cloud gateway's own wrapper
    "coach.py",      # the check-in nudge: a fixed sentence, no question
    "guardian.py",   # local guidance on a detection
    "guidance.py",   # the monitoring path's guidance, gated by its own module
    "hands.py",      # the agent's hands, under an engaged session's permits
    "i18n.py",       # translating a sentence already composed
    "llm.py",        # the wrappers themselves
    "research.py",   # the study door, which writes the ledger
}


def test_every_other_place_a_model_is_spoken_to_is_named():
    root = pathlib.Path(llm.__file__).parent
    found = {p.name for p in root.glob("*.py")
             if ".generate(" in p.read_text(encoding="utf-8")}
    assert found <= SPEAKS_DIRECTLY, (
        f"a new place speaks to a model directly: {sorted(found - SPEAKS_DIRECTLY)} — "
        "route it through the ledger or name it above with a reason")
    assert found >= {"research.py", "llm.py"}
