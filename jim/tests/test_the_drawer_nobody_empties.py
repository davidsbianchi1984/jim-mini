"""The drawer nobody empties.

## The finding

Task #110 gave all three native shells content-free error capture, and it did
that part well: `record` templates the route, drops the message, keeps the day
and not the time, and redacts on the way *in* so the buffer never holds
something that would later have to be scrubbed.

Then nothing sent it anywhere.

Nine shells across three products recorded failures into a fifty-row buffer
that filled up and rolled over. Only the desktop console — `app/src/errors.ts`
— ever had the second half. The tell was sitting in the model the whole time:
every shell declares a `sent` field documented as *"how much of `count` has
already been reported"*, and nothing in any of them ever read it, because
nothing ever reported. The comment described behaviour that was not in the
file.

    asked     is the failure recorded without recording anything private
    mattered  does the failure reach anybody

Per shell, never as a union: the console having both halves is exactly what
made this invisible for four releases. "Error reporting works" was true of one
client out of four, per product.

## What this checks

For each named shell — not for "the native directory" — that the sending half
exists and is wired: a report builder, a watermark that advances by amount, a
collector address that is empty by default, a notice gate, and a call at
launch. The address and the notice are checked as hard as the sender is,
because a sender with a baked-in address and no notice is a worse defect than
no sender at all.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()

#: (shell, its problems module, its launch file, the call the launch makes)
SHELLS = (
    ("ios", "native/ios/Sources/Problems.swift", "native/ios/Sources/JimGuardianApp.swift",
     "Problems.send("),
    ("android", "native/android/app/src/main/java/app/jim/guardian/Problems.kt", "native/android/app/src/main/java/app/jim/guardian/MainActivity.kt", "Problems.send("),
    ("windows", "native/windows/Problems.cs", "native/windows/App.xaml.cs",
     "Problems.Send("),
)

#: What every shell's sending half has to have, by the name it goes by there.
#: Named per language rather than searched for loosely: "does the file contain
#: the word send" is the kind of question that passes on a comment.
REQUIRED = {
    "ios": ["static func report(appVersion", "static func markReported(",
            "static func collectorUrl(", "static func noticeAnswered(",
            "static func send(", "URLSession"],
    "android": ["fun report(appVersion", "fun markReported(",
                "fun collectorUrl(", "fun noticeAnswered(", "fun send(",
                "HttpURLConnection"],
    "windows": ["Report(string", "MarkReported(", "CollectorUrl(",
                "NoticeAnswered(", "Send(", "HttpClient"],
}


def _code(path: Path) -> str:
    """Source with comments and doc comments stripped.

    Every one of these functions is *described* in the comment above it, so a
    check that searched the whole file would be satisfied by the prose
    explaining the thing rather than the thing. That has happened repeatedly in
    this audit, including inside guards written to prevent it.
    """
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"^\s*(///|//|\*)[^\n]*$", "", text, flags=re.M)


@pytest.mark.parametrize("shell,module,launch,call", SHELLS)
def test_the_shell_can_send_what_it_records(shell, module, launch, call):
    code = _code(REPO / module)
    missing = [name for name in REQUIRED[shell] if name not in code]
    assert not missing, (
        f"{shell}'s Problems module records failures and cannot report them. "
        f"Missing: {', '.join(missing)}.\n"
        "  Its `sent` field is documented as how much of `count` has already "
        "been reported — a description of a send that does not exist. The "
        "buffer fills to fifty rows and rolls over, and nobody ever learns "
        "the app is broken.")


@pytest.mark.parametrize("shell,module,launch,call", SHELLS)
def test_the_shell_actually_calls_it(shell, module, launch, call):
    """A function nothing calls is the same as no function.

    This is the check that separates this round from the one that wrote the
    recorder: that one added `record` *and* called it from `ApiClient`. The
    sending half is only real if a launch reaches it.
    """
    code = _code(REPO / launch)
    assert call in code, (
        f"{shell} has a sender and never calls it — {launch} does not reach "
        f"{call.rstrip('(')}. The buffer still only fills.")


@pytest.mark.parametrize("shell,module,launch,call", SHELLS)
def test_nothing_leaves_before_somebody_has_been_asked(shell, module, launch,
                                                       call):
    """The gate, checked as hard as the sender.

    A shell that posts before anybody has been told is a worse defect than one
    that posts nothing, and it would satisfy every check above. So the notice
    is asserted to be *upstream of the request*: the send path must consult it
    before it opens a socket, and the switch must not be the only gate — a
    switch defaulting to on is a decision made on somebody's behalf.

    The first version of this used `.index()` for both positions. Deleting the
    gate outright — the exact break it was written for — raised `ValueError`
    instead of failing, so the guard reported an error rather than the finding,
    and a reader would have gone looking for a broken test. That is the audit's
    shape inside the guard again: it answered "is the gate early" when what
    mattered was "is there a gate".
    """
    code = _code(REPO / module)
    body = code[code.lower().index("sendoutcome"):].lower()
    request = min((body.index(m) for m in
                   ("urlsession", "httpurlconnection", "httpclient")
                   if m in body), default=None)
    assert request is not None, (
        f"{shell}'s send path opens no request at all — there is nothing here "
        "for a notice to gate")
    gate = body.find("noticeanswered")
    assert gate != -1, (
        f"{shell} posts without ever consulting the notice. Nothing may leave "
        "the device before somebody has been told what is in a report and "
        "chosen. A send with no notice is worse than no send.")
    assert gate < request, (
        f"{shell} opens its request before it checks whether anybody has been "
        "told. The gate has to come first or it is not a gate.")


@pytest.mark.parametrize("shell,module,launch,call", SHELLS)
def test_the_address_is_empty_until_a_release_stamps_one(shell, module, launch,
                                                         call):
    """An install with nowhere to send is the default, and the stronger one.

    A flag can be switched on by a later mistake; a missing address cannot,
    because there is nothing to switch on. The literal check is for a hard-coded
    `https://` in the module — an address written into the source is one no
    build can decline to ship.
    """
    code = _code(REPO / module)
    baked = re.findall(r'"https?://[^"]+"', code)
    assert not baked, (
        f"{shell}'s Problems module has an address written into the source: "
        f"{baked}. It must come from the build, so a build that does not "
        "stamp one reports nowhere.")


def test_every_shell_names_its_own_product():
    """`unknown` is a source the gateway refuses.

    These modules are otherwise identical across the three repositories, so a
    copy that kept the wrong name would file this product's failures under
    another product's — and every count would look plausible. The gateway
    cannot catch it: `qrme` is a source it accepts.
    """
    expected = REPO.name.lower()
    aliases = {"qrme": "qrme", "jim-mini": "jim-mini", "pdi": "pdi"}
    want = aliases.get(expected, expected)
    for shell, module, _, _ in SHELLS:
        code = _code(REPO / module)
        found = re.search(r'(?:source|SOURCE|Source)\s*(?:=|:)\s*"([\w-]+)"',
                          code)
        assert found, f"{shell} does not declare which product it is"
        assert found.group(1) == want, (
            f"{shell} reports its failures as {found.group(1)!r}, but this "
            f"repository is {want!r}. The gateway accepts both names, so this "
            "would silently file one app's bugs under the other's.")


def test_the_watermark_advances_by_amount_and_not_by_a_flag():
    """A row goes on counting while the request is in flight.

    Marking a row "sent" as a boolean drops every occurrence that happened
    during the send — invisibly, and more often the worse the bug is, because a
    failure that fires constantly is the one most likely to fire again mid-post.
    """
    for shell, module, _, _ in SHELLS:
        code = _code(REPO / module)
        mark = code[code.lower().index("markreported"):][:1200]
        assert re.search(r"sent\s*\+|\+\s*n\b|Sent \+=|sent\", .*\+", mark,
                         re.I), (
            f"{shell} does not advance its watermark by the amount reported. "
            "A flag here loses every failure that happens mid-send.")


# --- the notice surface, per shell -----------------------------------------
#
# (shell, the file holding the card, the screen that must call it)
NOTICE = (
    ("ios", "native/ios/Sources/Views/ProblemReportingCard.swift",
     "native/ios/Sources/Views/CustodyView.swift", "ProblemReportingCard()"),
    ("android", "native/android/app/src/main/java/app/jim/guardian/ui/Screens.kt", "native/android/app/src/main/java/app/jim/guardian/ui/Screens.kt", "ProblemReportingCard()"),
    ("windows", "native/windows/Views/CustodyPage.xaml.cs", "native/windows/Views/CustodyPage.xaml", "ProblemsExplain"),
)


@pytest.mark.parametrize("shell,card,host,call", NOTICE)
def test_the_notice_exists_and_is_reachable(shell, card, host, call):
    """A gate with no way to answer it is a feature nobody chose.

    The sending half shipped answering `awaitingNotice` on every launch —
    the safe direction to be wrong in, and still wrong. This asserts both
    halves per shell: the card exists, and a screen somebody can reach
    actually calls it.
    """
    body = _code(REPO / card)
    assert "answerNotice" in body or "AnswerNotice" in body, (
        f"{shell}'s reporting card never answers the notice, so the gate it "
        "exists to open stays shut")
    assert call in _code(REPO / host), (
        f"{shell} has a notice card that no screen shows. The sender will go "
        "on answering awaiting-notice forever.")


@pytest.mark.parametrize("shell,card,host,call", NOTICE)
def test_the_notice_shows_the_report_rather_than_describing_it(shell, card,
                                                               host, call):
    """The preview has to be built by the same call the sender posts.

    A card that prints a hand-written summary of what a report contains is
    asking somebody to take our word for it, and it drifts the first time the
    payload changes — silently, and in the direction of a promise nobody is
    keeping. So the screen calls `report()`, the function `send` posts.

        asked     does the notice describe what is sent
        mattered  does the notice show what is sent
    """
    body = _code(REPO / card)
    assert ("Problems.report(" in body or "Problems.Report(" in body), (
        f"{shell}'s card does not build its preview from the report the "
        "sender posts, so the two can disagree and only one of them is true")


@pytest.mark.parametrize("shell,card,host,call", NOTICE)
def test_neither_answer_is_the_pre_picked_one(shell, card, host, call):
    """Both answers exist, and neither is painted as the expected one.

    A notice with a bright Yes and a grey No has made the choice already, and
    that is not consent — it is a layout that looks like consent.

    Scoped to the two answer elements themselves. The first version searched
    the whole file for a brand colour and failed on a button belonging to a
    different card three sections up, which is this audit's shape occurring
    inside a check about consent:

        asked     does this file mention the brand colour anywhere
        mattered  do the two answers differ in emphasis
    """
    body = _code(REPO / card) + _code(REPO / host)
    for wording in ("Send counts", "Do not send"):
        assert wording in body, (
            f"{shell}'s card is missing the {wording!r} answer")

    # Everything on the line that declares each answer — the style it is given
    # and nothing belonging to anything else.
    lines = body.splitlines()
    marks = [i for i, line in enumerate(lines)
             if "Send counts" in line or "Do not send" in line
             or "ProblemsYes" in line or "ProblemsNo" in line]
    # Two lines, not one: Swift puts the style on a wrapped modifier below the
    # label, and a one-line window missed exactly the injection this test was
    # written for — the styling sat on the next line and the guard passed.
    answers = [line for i in marks for line in lines[i:i + 2]]
    assert answers, f"{shell}: could not locate the answer controls"
    painted = [line.strip() for line in answers
               if re.search(r"BrandABrush|borderedProminent|Background=", line)]
    assert not painted, (
        f"{shell} paints one answer differently from the other:\n    "
        + "\n    ".join(painted)
        + "\n  Neither answer may be the pre-picked one.")
