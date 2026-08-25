"""An aid on the call, and the notice that goes out before anything listens.

`jim/mic.py` refuses a speaker call in as many words — *they were never asked
and could not revoke it* — and that refusal is right about the case it names:
a person who was never told. This is the other case. The far side is told, out
loud, on the line, and then staying on it is theirs to decide.

    asked     may the agent be on this call
    mattered  does the other person know it is

## Notice, not permission

Nothing here waits for the far side to answer. There is no consent flow, no
state for *they objected*, and no prompt — the notice plays and hanging up is
the remedy, exactly as it is on every support line anybody has ever called.

What is enforced instead is **ordering**, and these guards are about that: a
call that started hearing before it spoke is the failure this exists to make
impossible.

## The words are the ones people already know

Deliberately the support-line script rather than a careful new sentence.
Somebody hearing it does not have to work out what it means or what they can
do about it: they have heard it a hundred times, they know something is
listening, and they know the remedy is to hang up. A better sentence nobody
recognises is a worse notice.

What this product adds is that it is said in a language the far side might
actually speak — picked from the dialling code, and said in more than one
where the mix is known — and that nothing listens until it has gone out.
"""

from __future__ import annotations

import inspect

import pytest

from jim import oncall

from .conftest import enroll


def _open(client, user_id, route="speaker", recording=False, number=None):
    r = client.post(f"/calls/{user_id}",
                    json={"route": route, "recording": recording,
                          "number": number})
    assert r.status_code == 201, r.text
    return r.json()


# --------------------------------------------------------------------------
# Ordering: the notice, then anything else.
# --------------------------------------------------------------------------

def test_a_new_call_is_not_listening(client):
    """It starts in the one state where it cannot hear anything, and says so
    rather than leaving a client to assume either way."""
    user_id = enroll(client)
    call = _open(client, user_id)
    assert call["listening"] is False
    assert call["notices"]


def test_nothing_listens_until_the_notice_has_gone_out(client):
    """The whole round. A call that heard something before it announced
    itself is the failure this module exists to prevent."""
    user_id = enroll(client)
    call = _open(client, user_id)

    refused = client.post(f"/calls/{user_id}/{call['id']}/heard")
    assert refused.status_code == 409, refused.text
    assert "not been told" in refused.text

    client.post(f"/calls/{user_id}/{call['id']}/announced")
    allowed = client.post(f"/calls/{user_id}/{call['id']}/heard")
    assert allowed.status_code == 200, allowed.text


def test_the_only_door_to_listening_is_the_one_that_checks(client):
    """One function, and every path through it — the argument
    `offline.allow` makes for sockets and `oncall.may_listen` makes here."""
    from jim import api
    source = inspect.getsource(api)
    assert "oncall.may_listen(" in source
    assert "announced_at" not in source, (
        "a route is reading the announcement state itself instead of asking "
        "`may_listen`; that is a second opinion about the one rule here")


def test_no_argument_skips_the_notice():
    """Crude on purpose. Every reason to bypass an announcement for one call
    sounds reasonable at the time — a test that needs it quiet, a demo, a
    trusted contact — and the sum of them is a product that stopped
    announcing."""
    assert list(inspect.signature(oncall.may_listen).parameters) == ["call_id"]
    assert "announced_at" in inspect.getsource(oncall.may_listen)


def test_the_refusal_says_what_to_play(client):
    """A refusal that says *you have not announced* and stops there leaves
    somebody hunting for the words. It carries them."""
    user_id = enroll(client)
    call = _open(client, user_id)
    refused = client.post(f"/calls/{user_id}/{call['id']}/heard")
    assert refused.json()["detail"]["say"] == call["said"]


# --------------------------------------------------------------------------
# The sentence itself.
# --------------------------------------------------------------------------

def test_the_notice_is_the_one_people_have_already_heard():
    """A better sentence nobody recognises is a worse notice. Somebody who
    has called a support line knows what this means and what to do about
    it."""
    assert oncall.NOTICE == ("This call may be monitored or recorded to "
                             "better assist you.")


def test_the_caller_cannot_hand_in_its_own_sentence(client):
    """Composed here, never accepted from a client: nothing gets to decide
    what the far side is told."""
    assert "notice" not in inspect.signature(oncall.open).parameters
    user_id = enroll(client)
    call = _open(client, user_id)
    assert [part["words"] for part in call["notices"]] == [
        oncall.notice_for(lang) for lang in call["spoken_in"]]


def test_the_words_that_went_out_are_what_is_kept(client):
    """Not a flag saying *announced*. The sentence, so what somebody was told
    is answerable later by a person who was not on the call."""
    user_id = enroll(client)
    call = _open(client, user_id, recording=True, number="+34 91 555 0000")
    client.post(f"/calls/{user_id}/{call['id']}/announced")
    row = client.get(f"/calls/{user_id}").json()[0]
    assert row["said"] == oncall.notice_for("es")
    assert row["announced_at"]


def test_the_call_refusal_arrives_in_the_readers_language(client):
    """Including the notice inside it: an English sentence in a Portuguese
    frame is the mixed refusal `i18n.Term` exists to prevent."""
    user_id = enroll(client)
    # Through the route rather than the module: the stored preference is what
    # `refusal_language` reads, and setting it any other way would test the
    # table instead of the path a person actually takes to choose.
    assert client.put(f"/language/{user_id}",
                      json={"language": "pt"}).status_code in (200, 201)
    call = _open(client, user_id)
    refused = client.post(f"/calls/{user_id}/{call['id']}/heard")
    body = refused.json()
    assert "não foi informada" in body["message"]
    # The script beside it is *not* translated into the reader's language: it
    # is spoken to somebody else, and that somebody is why it was composed in
    # theirs. A refusal that helpfully translated it would hand the caller
    # words nobody on the line can use.
    assert body["detail"]["say"] == call["said"]


# --------------------------------------------------------------------------
# Said in a language the far side might actually understand.
# --------------------------------------------------------------------------

@pytest.mark.parametrize("number,language", [
    ("+34 91 555 0000", "es"),      # Spain
    ("+33 1 45 55 00 00", "fr"),    # France
    ("+81 3 5555 0000", "ja"),      # Japan
    ("+1 202 555 0000", "en"),      # Washington DC
    ("+1 514 555 0000", "fr"),      # Montréal — inside +1, and not English
    ("+1 787 555 0000", "es"),      # Puerto Rico — likewise
])
def test_the_notice_is_said_in_the_far_sides_likely_language(
        client, number, language):
    """The person who has to understand this is the one on the other end, so
    the caller's own language is the wrong default. The dialling code is the
    only clue a call gives before anybody speaks — and +1 is shared by two
    countries and three languages, which is why the area code matters."""
    user_id = enroll(client)
    call = _open(client, user_id, number=number)
    assert call["spoken_in"][0] == language
    assert call["notices"][0]["words"] == oncall.notice_for(language)


def test_the_guess_says_what_it_was_guessed_from(client):
    """A guess presented as knowledge is worse than a guess. The clue is what
    makes it correctable by somebody who knows better."""
    user_id = enroll(client)
    assert _open(client, user_id, number="+39 06 555 0000")["language_from"] \
        == "+39"
    assert "no number" in _open(client, user_id)["language_from"]


def test_it_is_said_in_every_language_where_the_mix_is_known(client):
    """Picking one language for a country that plainly has two is a coin toss
    with somebody's understanding, and being wrong means the notice was
    noise. Saying it twice costs a few seconds."""
    user_id = enroll(client)
    swiss = _open(client, user_id, number="+41 44 555 0000")
    assert swiss["spoken_in"] == ["de", "fr", "it"]
    assert len(swiss["notices"]) == 3

    quebec = _open(client, user_id, number="+1 514 555 0000")
    assert quebec["spoken_in"] == ["fr", "en"]


def test_english_carries_spanish_with_it(client):
    """What a support line in the United States actually does, and the case
    an unknown number falls back to."""
    user_id = enroll(client)
    assert _open(client, user_id, number="+1 202 555 0000")["spoken_in"] \
        == ["en", "es"]
    assert _open(client, user_id)["spoken_in"] == ["en", "es"]


def test_with_no_clue_it_falls_back_rather_than_guessing(client):
    """An unknown dialling code is not a reason to say nothing, and not a
    reason to invent a language. It uses the caller's and says so."""
    user_id = enroll(client)
    call = _open(client, user_id, number="+999 555 0000")
    assert call["spoken_in"] == ["en", "es"]
    assert "not one this product has a language for" in call["language_from"]


def test_the_number_is_read_and_dropped(client):
    """It is the clue, not a record. Nothing comes back carrying it and
    nothing stores it — see the module note on the far side having no account
    here."""
    user_id = enroll(client)
    number = "+34 91 555 0000"
    call = _open(client, user_id, number=number)
    assert "555" not in str(call)
    row = client.get(f"/calls/{user_id}").json()[0]
    assert "555" not in str(row)


# --------------------------------------------------------------------------
# The far side, who has no account here.
# --------------------------------------------------------------------------

def test_nothing_about_the_other_person_is_stored():
    """They have no account here and never will. What is kept is that a
    notice was given, when, and in what words — the one fact they would ever
    want established."""
    from jim import db
    columns = {r[1] for r in db.connect().execute(
        "PRAGMA table_info(assisted_calls)").fetchall()}
    for theirs in ("number", "caller", "contact", "them", "transcript",
                   "voiceprint", "far_side", "dialled", "msisdn"):
        assert theirs not in columns


def test_a_private_route_is_refused_here(client):
    """This module is for calls somebody else can hear. On an earpiece there
    is nobody to announce to, and `jim/mic.py` already covers lending the
    agent a second microphone there."""
    user_id = enroll(client)
    r = client.post(f"/calls/{user_id}",
                    json={"route": "earpiece", "recording": False})
    assert r.status_code == 422, r.text


def test_mic_still_refuses_the_unannounced_speaker_call():
    """This round adds the path that refusal was waiting for. It does not
    weaken it: a speaker call with nobody told is still refused there.

    The sentence moved into `i18n.SPEAKER_ROUTE_REFUSED` when the refusal
    was templated, so this follows it: the handover still raises through
    that constant, and the constant still says why."""
    from jim import i18n, mic
    source = inspect.getsource(mic.handover)
    assert "PRIVATE_ROUTES" in source
    assert "SPEAKER_ROUTE_REFUSED" in source
    assert "were never asked" in i18n.SPEAKER_ROUTE_REFUSED


def test_a_call_that_never_announced_stays_in_the_history(client):
    """It is the evidence that the ordering held — and a history that quietly
    dropped it would be a history that only ever shows compliance."""
    user_id = enroll(client)
    call = _open(client, user_id)
    client.delete(f"/calls/{user_id}/{call['id']}")
    rows = client.get(f"/calls/{user_id}").json()
    assert [r["id"] for r in rows] == [call["id"]]
    assert rows[0]["listened"] is False


@pytest.mark.parametrize("route", oncall.SHARED_ROUTES)
def test_every_shared_route_announces(client, route):
    user_id = enroll(client)
    assert _open(client, user_id, route=route)["notices"]
