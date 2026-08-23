"""The Guardian answering an interruption knows where it was cut off.

    asked     did they interrupt
    mattered  how much had they heard when they did

A voice screen plays a reply piece by piece, and speaking over it hushes
the rest. What the person is left holding is a PREFIX. The turn that
followed was built as though the whole answer had landed, so the Guardian
carried on from a place nobody arrived at, or took as read a caveat that
never left the speaker.

QRME's room learned this first and learned it on a transcript, which is a
different problem: a room turn is replayed from history, so the fact is
stored on the interrupted message. A coach turn is generated from the
CURRENT message — there is no assistant turn to annotate — so the fact
rides the request and is stored nowhere. That is not a shortcut. A stored
interruption would be replayed tomorrow, and the Guardian would apologise
for a paragraph the person had long since forgotten cutting off.

Optional on the wire and ignorable: absent means nothing was interrupted,
which is the ordinary turn, and every native shell keeps working unchanged.
"""

from __future__ import annotations

from pathlib import Path

from jim import coach, llm

from jim.tests.conftest import enroll

APP = Path(__file__).resolve().parents[2] / "app" / "src"
SPEECH = (APP / "speech.ts").read_text(encoding="utf-8")


def _spy(monkeypatch, seen: dict):
    def capture(user_id, system, message, cloud=None):
        seen["system"] = system
        seen["message"] = message
        return {"text": "ok", "provider": "anthropic", "degraded": False,
                "reason": None, "grounded": False, "drew_on": []}

    monkeypatch.setattr(llm, "generate_for_user", capture)


def test_an_ordinary_turn_says_nothing_about_being_interrupted(
        client, monkeypatch):
    """Most turns are not interruptions, and a prompt that mentions one
    anyway invites the model to apologise for something that never
    happened."""
    uid = enroll(client)
    seen: dict = {}
    _spy(monkeypatch, seen)
    r = client.post(f"/coach/{uid}",
                    json={"area": "general", "message": "how do I sleep"})
    assert r.status_code == 200, r.text
    assert "spoke over" not in seen["system"]


def test_the_prompt_says_how_far_they_got(client, monkeypatch):
    """Read at the model, not at the field: a value accepted by the route
    and never handed to the prompt changes nothing about the answer."""
    uid = enroll(client)
    seen: dict = {}
    _spy(monkeypatch, seen)
    r = client.post(f"/coach/{uid}", json={
        "area": "general",
        "message": "no, the other one",
        "cut_off_heard": "The first thing I would try is a fixed wake time"})
    assert r.status_code == 200, r.text
    assert "spoke over your last answer" in seen["system"]
    assert "a fixed wake time" in seen["system"], (
        "the prompt says it was interrupted and not where, so the Guardian "
        "cannot tell which part reached them")
    assert "never reached them" in seen["system"]


def test_it_is_context_rather_than_an_instruction_to_start_over(client,
                                                                monkeypatch):
    """The reply is meant to answer the NEW question. Told to repeat or
    apologise, the Guardian spends the turn on the last one — which is
    exactly what the person interrupted to stop."""
    uid = enroll(client)
    seen: dict = {}
    _spy(monkeypatch, seen)
    client.post(f"/coach/{uid}", json={
        "area": "general", "message": "different question",
        "cut_off_heard": "As I was saying"})
    said = seen["system"]
    assert "Answer what they" in said
    for wrong in ("apolog", "start over", "repeat what you"):
        assert wrong not in said.lower(), wrong


def test_whitespace_is_not_an_interruption(client, monkeypatch):
    """A client that sends the field always, empty when there was nothing
    to report, is describing an ordinary turn."""
    uid = enroll(client)
    seen: dict = {}
    _spy(monkeypatch, seen)
    client.post(f"/coach/{uid}", json={
        "area": "general", "message": "hello", "cut_off_heard": "   "})
    assert "spoke over" not in seen["system"]


def test_the_fact_is_not_stored(client, monkeypatch):
    """It is true of one turn. Kept, it would be replayed into every later
    prompt, and the Guardian would keep accounting for an interruption
    nobody remembers making."""
    uid = enroll(client)
    seen: dict = {}
    _spy(monkeypatch, seen)
    client.post(f"/coach/{uid}", json={
        "area": "general", "message": "first",
        "cut_off_heard": "MARKERWORDXYZ"})
    client.post(f"/coach/{uid}", json={"area": "general", "message": "second"})
    assert "MARKERWORDXYZ" not in seen["system"]

    from jim import db
    rows = db.connect().execute(
        "SELECT content FROM coach_messages WHERE user_id=?", (uid,)).fetchall()
    assert rows, "the turn was not recorded at all"
    assert not any("MARKERWORDXYZ" in (r["content"] or "") for r in rows)


def test_the_console_counts_the_piece_in_the_air_as_heard():
    """A piece that started playing reached the person — at least its
    opening words. Counted as unheard, the Guardian would re-say a
    sentence they had already had enough of, which is the interruption
    ignored in a politer costume."""
    body = SPEECH[SPEECH.index("export async function say("):]
    body = body[:body.index("\n/** The device's own voice")]
    play = body.index("await audio.play();")
    before = body[:play]
    assert "piecesOut = i + 1;" in before, (
        "the piece being played is counted only after play() resolves, so "
        "the piece somebody heard themselves interrupt is reported unheard"
    )


def test_the_count_survives_the_hush_that_reports_it():
    """`hush()` is what an interruption calls. Resetting the count there
    would wipe the only evidence the interruption exists to carry, and the
    whole feature would report an empty string forever."""
    hush = SPEECH[SPEECH.index("export function hush()"):]
    hush = hush[:hush.index("\n}") + 2]
    assert "piecesOut" not in hush and "piecesSaid" not in hush, (
        "hush() clears the heard-so-far count, so nothing is left to report"
    )
    start = SPEECH[SPEECH.index("export async function say("):]
    assert "piecesOut = 0;" in start[:start.index("for (let i = 0;")], (
        "a new reply does not reset the count, so it reports the last one"
    )


# -- and the four screens that can be interrupted --------------------------
#
# The backend reading a field nobody sends is the same shape of nothing as a
# binding nobody calls. Every screen that holds a standing voice conversation
# has to capture the interruption and spend it, so each is read here by name
# rather than trusted to a shared helper existing.

VOICE_SCREENS = ["Checkin", "Coach", "Monitor", "Talk"]
TYPED_TOO = ["Coach", "Talk"]


def _screen(name: str) -> str:
    return (APP / "screens" / f"{name}.tsx").read_text(encoding="utf-8")


def test_every_voice_screen_captures_the_interruption():
    """Captured where the barge-in happens, which is also the only place
    the answer still exists to be measured."""
    for name in VOICE_SCREENS:
        src = _screen(name)
        assert "hushAndReport()" in src, name
        # The stop must go through the reporting call rather than a bare
        # hush beside it: a screen that calls `hush()` on the barge-in path
        # has already thrown the count away by the time it asks for it.
        heard = src.index("hushAndReport()")
        assert "cutOff.current" in src[max(0, heard - 200):heard + 60], name


def test_every_voice_screen_sends_what_it_captured():
    """A capture the request never carries is a capture that changed
    nothing — the failure this whole file is about, one layer up."""
    for name in VOICE_SCREENS:
        src = _screen(name)
        assert "cut_off_heard: cut" in src, name


def test_the_interruption_is_spent_rather_than_kept():
    """It is a fact about one turn. Left in the ref it would ride the next
    question too, and the Guardian would account for a paragraph nobody
    had cut off."""
    for name in VOICE_SCREENS:
        src = _screen(name)
        assert 'cutOff.current = "";' in src, name


def test_typing_interrupts_too():
    """Somebody who watched an answer head off in the wrong direction and
    typed rather than spoke wanted the same thing the speaker wanted. On
    the screens with a text box, sending must stop the voice."""
    for name in TYPED_TOO:
        src = _screen(name)
        assert "cutOff.current || hushAndReport()" in src, (
            f"{name}: a typed question does not stop the reply it "
            "interrupts, so the Guardian talks over the new one"
        )
