"""The answer begins before it ends.

Field report, twice in one week: "still a long delay while waiting for a
response." The wait had two legs — the model writing the whole answer,
then the voice service synthesising the whole answer — and the second
leg was paid in full before a single word was heard.

    asked     when does the answer start being heard
    mattered  does the wait grow with the length of the answer

`say()` now cuts the reply at sentence ends (`spokenPieces`) and
pipelines: the first sentence is synthesised alone — small, so it comes
back fast — and every later piece is fetched while the one before it
plays. The splitter is executed here through node, not pinned by regex:
a function that decides what reaches the voice service should be tested
by running it.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SPEECH = (REPO / "app/src/speech.ts").read_text(encoding="utf-8")

_RUNNER = """
const ts = require("typescript");
const fs = require("fs");
const src = fs.readFileSync("src/pieces.ts", "utf8");
const js = ts.transpileModule(src, {
  compilerOptions: { module: ts.ModuleKind.CommonJS },
}).outputText;
const mod = { exports: {} };
new Function("exports", "module", js)(mod.exports, mod);
const texts = JSON.parse(fs.readFileSync(0, "utf8"));
console.log(JSON.stringify(texts.map((t) => mod.exports.spokenPieces(t))));
"""


def _pieces(*texts: str) -> list[list[str]]:
    proc = subprocess.run(
        ["node", "-e", _RUNNER], cwd=REPO / "app", input=json.dumps(texts),
        capture_output=True, text=True)
    assert proc.returncode == 0, (
        f"the splitter will not run:\n{proc.stderr}")
    return json.loads(proc.stdout)


# -- the splitter, run for real ----------------------------------------------

def test_a_short_reply_is_one_piece_unchanged():
    [(piece,)] = [tuple(p) for p in _pieces("Take the aspirin now.")]
    assert piece == "Take the aspirin now."


def test_the_first_sentence_rides_alone_and_nothing_is_lost():
    text = ("Sit down somewhere comfortable first. " * 1).strip() + " " + \
        " ".join(f"Then step {i} follows as planned." for i in range(1, 9))
    [pieces] = _pieces(text)
    assert pieces[0] == "Sit down somewhere comfortable first.", (
        "the first piece must be the first sentence alone — it is the one "
        "somebody is waiting on")
    assert len(pieces) >= 2
    assert " ".join(pieces) == text, "no word may be lost or invented"


def test_a_decimal_is_not_a_sentence_end():
    [pieces] = _pieces("The window is 2.5 seconds now. Try it again.")
    assert pieces[0] == "The window is 2.5 seconds now."


def test_a_title_is_not_a_sentence_end():
    [pieces] = _pieces("Dr. Alvarez called back. Rest today.")
    assert pieces[0] == "Dr. Alvarez called back."


def test_a_long_answer_is_a_few_requests_not_thirty():
    text = " ".join(f"Sentence number {i} of this answer." for i in range(30))
    [pieces] = _pieces(text)
    assert 1 < len(pieces) <= 8, (
        "grouping is the point: thirty sentences must not become thirty "
        "round trips to the voice service")
    assert " ".join(pieces) == text


def test_empty_says_nothing():
    [pieces] = _pieces("   ")
    assert pieces == []


# -- the pipeline in say() ---------------------------------------------------

def test_say_speaks_in_pieces_and_prefetches():
    assert "spokenPieces(text)" in SPEECH, (
        "say() no longer cuts the reply — the whole answer is one request "
        "again, and the wait grows with its length")
    assert "clip(pieces[i + 1])" in SPEECH, (
        "the next piece must be fetched while the current one plays — "
        "without the prefetch the pauses between sentences are the same "
        "wait, paid in instalments")


def test_hush_cancels_the_run_between_pieces():
    assert "sayRun++" in SPEECH and "run !== sayRun" in SPEECH, (
        "hush() must end the pipeline: a reply somebody cut off must not "
        "keep speaking its remaining pieces")


def test_the_gap_between_pieces_still_reads_as_speaking():
    assert "midReply" in SPEECH
    assert "|| midReply" in SPEECH, (
        "speakingNow() must cover the moment between two pieces — audio "
        "ended, next clip in flight — or the standing ear can catch the "
        "Guardian's own voice and submit it as something heard")


def test_a_failed_piece_falls_to_the_device_for_the_remainder():
    assert 'pieces.slice(i).join(" ")' in SPEECH, (
        "a piece the service fails must hand the REST of the answer to the "
        "device's own voice — going quiet mid-reply is the wrong failure")
