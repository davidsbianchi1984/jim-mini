"""The Guardian does not answer herself.

Field report from a coach conversation: "when I'm in the chat sphere with
coach while it's talking, it's listening at the same time, but it seems
to be picking up its own voice and triggering itself and not letting it
finish."

    asked     did somebody interrupt
    mattered  was it a person, or the speaker on the table

The open microphone is not the defect — it is what makes interrupting a
turn, and a field report asked for that. The defect is what came back
through it: on a phone speaker, echo cancellation thins the Guardian's
voice without silencing it, and the transcriber turned that leakage into
the person's next turn. So the reply hushed itself mid-sentence and
answered a sentence it had just said.

Two answers, and the second is the certain one. The energy bar goes up
while she speaks, so a speaker across the table stops reading as a voice
while a person inches from the microphone still does. And whatever
survives that is checked against her own words: the standing ear already
refused to testify about itself, and now the conversation does too.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SPEECH = (REPO / "app/src/speech.ts").read_text(encoding="utf-8")

_RUNNER = """
const ts = require("typescript");
const fs = require("fs");
const src = fs.readFileSync("src/echo.ts", "utf8");
const js = ts.transpileModule(src, {
  compilerOptions: { module: ts.ModuleKind.CommonJS },
}).outputText;
const mod = { exports: {} };
new Function("exports", "module", js)(mod.exports, mod);
const pairs = JSON.parse(fs.readFileSync(0, "utf8"));
console.log(JSON.stringify(pairs.map(([h, s]) => mod.exports.isEcho(h, s))));
"""


def _echo(*pairs: tuple[str, str]) -> list[bool]:
    proc = subprocess.run(
        ["node", "-e", _RUNNER], cwd=REPO / "app",
        input=json.dumps([list(p) for p in pairs]),
        capture_output=True, text=True)
    assert proc.returncode == 0, f"the echo rule will not run:\n{proc.stderr}"
    return json.loads(proc.stdout)


SAID = ("Let's take this one step at a time. Sit down somewhere "
        "comfortable, and tell me what happened this morning.")


# -- the rule, run for real --------------------------------------------------

def test_her_own_sentence_coming_back_is_not_a_turn():
    [got] = _echo(("sit down somewhere comfortable and tell me what happened",
                   SAID))
    assert got is True, (
        "the Guardian's own words came back through the room and were "
        "taken for the person's answer — this is the defect itself")


def test_a_fragment_of_her_own_sentence_is_not_a_turn():
    [got] = _echo(("one step at a time", SAID))
    assert got is True


def test_a_person_answering_is_a_turn():
    [got] = _echo(("I fell in the kitchen and my hip hurts", SAID))
    assert got is False, (
        "a real answer was thrown away as an echo — the conversation "
        "would go deaf to the person it is for")


def test_a_short_interruption_is_always_a_turn():
    """"yes", "no", "stop", "wait" are exactly the interruptions worth
    having, and every one of their words appears in some paragraph."""
    for short in ("stop", "no", "wait", "yes"):
        [got] = _echo((short, SAID))
        assert got is False, f"{short!r} was mistaken for the room"


def test_a_person_who_says_two_of_her_words_still_gets_a_turn():
    [got] = _echo(("this morning I could not stand up on my own", SAID))
    assert got is False


def test_nothing_said_means_nothing_to_echo():
    [got] = _echo(("anything at all here", ""))
    assert got is False, (
        "with no reply in flight there is no echo to find — a silent "
        "Guardian must never swallow a turn")


# -- both halves are wired into the conversation -----------------------------

def test_the_bar_goes_up_while_she_speaks():
    assert "BARGE_PEAK" in SPEECH, (
        "the energy gate uses one threshold whether or not the Guardian "
        "is speaking, so her own voice reads as somebody talking")
    assert re.search(r"const bar = speakingNow\(\) \? BARGE_PEAK : 6;",
                     SPEECH), (
        "the raised bar is no longer tied to the Guardian speaking")


def test_both_listening_paths_check_her_words():
    """The record-and-send path has an analyser; the device recogniser has
    none at all, so it needs this more, not less."""
    assert SPEECH.count("echoOfTheGuardian(") >= 3, (
        "one of the two listening paths still submits whatever it hears "
        "while the Guardian is speaking")


def test_an_echo_is_reported_as_quiet_not_as_a_failure():
    """"nothing was heard" is what a standing conversation treats as a
    pause — it re-opens the microphone and waits. An error would end the
    conversation over the room being a room."""
    for m in re.finditer(r"echoOfTheGuardian\(\w+\)\) \{\s*\n\s*(\w+)\(",
                         SPEECH):
        assert m.group(1) == "onError", m.group(0)
    assert re.search(r"echoOfTheGuardian\(\w+\)\) \{\s*\n"
                     r'\s*onError\("nothing was heard in that"\);', SPEECH), (
        "an echo is reported as something other than quiet")


def test_the_rule_lives_where_it_can_be_run():
    assert (REPO / "app/src/echo.ts").exists()
    src = (REPO / "app/src/echo.ts").read_text(encoding="utf-8")
    # Statements, not the word: this file's own header explains why it
    # has none, and a guard that trips over the explanation is a guard
    # that reads text rather than code.
    assert not re.search(r"^\s*import\s", src, re.M), (
        "echo.ts grew an import, so the guard above can no longer "
        "transpile and run it — the rule would be pinned by regex again")
