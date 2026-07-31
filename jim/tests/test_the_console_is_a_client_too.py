"""Every route is reachable **from the console** — or is on the list.

`test_every_route_has_a_door.py` asks whether every route is reachable from
*a* client, and `clientpaths.doorless` answers it over the union of four
surfaces: the console and the iOS, Android and Windows shells.

That union is the flaw. A route only the phone calls counts as doored, so the
union backlog reads 69 while the console alone cannot reach **109**
routes. The guard was answering *some client can reach this*, which was true,
rather than *this client can reach this*, which was not.

That is the same shape as every other defect this audit has produced: a
checker answering a question slightly to the left of the one that matters,
and passing. In QRME the gap turned out to be the entire seller's side of the
product — post a licence offer, see who holds one, revoke it, read what it
earned, ask to be paid — all present on the phone, all absent from the desk.

So this file asks the console's question on its own. The union guard stays —
a route no client anywhere calls is still worse — and this one sits beside it
with a snapshot of its own: **109 at the start, and it must not grow.**

The obvious objection is that a phone-only capability is a legitimate design
choice, and it is: a camera roll has no business on a desktop. That is what
the snapshot is for. Deferring a route means adding a line to it, which takes
a deliberate edit and shows up in a diff — the difference between a decision
and an oversight being whether anybody made it.
"""

from __future__ import annotations

from pathlib import Path

from jim.api import app

from . import clientpaths

SNAPSHOT = Path(__file__).resolve().parent / "console_doorless.txt"

#: What it was when this guard was written, so the direction of travel is a
#: fact in the file rather than a claim in a commit message.
STARTED_AT = 109


def _recorded() -> list[str]:
    return [line.strip() for line in
            SNAPSHOT.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_the_console_backlog_matches_the_record():
    """Both directions, for the same reason the union guard checks both.

    A route that has gained a console door is as much a change to report as
    one that has lost it, and a file only checked for growth becomes a list
    of things that were true once.
    """
    actual = clientpaths.doorless(app, surfaces=(clientpaths.CONSOLE,))
    recorded = _recorded()

    appeared = sorted(set(actual) - set(recorded))
    resolved = sorted(set(recorded) - set(actual))

    problems = []
    if appeared:
        problems.append(
            f"{len(appeared)} route(s) the console cannot reach:\n    "
            + "\n    ".join(appeared)
            + "\n  (build the door, or record it here with the reason)")
    if resolved:
        problems.append(
            f"{len(resolved)} route(s) now have a console door — strike them "
            f"from {SNAPSHOT.name}:\n    " + "\n    ".join(resolved))
    assert not problems, "\n\n".join(problems)


def test_the_backlog_only_shrinks():
    """A ratchet, because the union guard already proved a backlog can sit
    at a number for a long time without anybody choosing that number.

    It is not zero and does not have to be. What it must not do is grow: the
    file is allowed to be edited downward and upward both, but an upward edit
    that takes it past where it started is the gap reopening.
    """
    assert len(_recorded()) <= STARTED_AT, (
        f"the console backlog is {len(_recorded())}, above the {STARTED_AT} "
        "it started at — routes are being added faster than doors")


def test_the_union_is_still_wider_than_the_console():
    """A guard on the guard, and on the premise.

    If these two ever returned the same list, one of them would be redundant
    — and the likelier cause is an extractor that stopped reading the native
    shells, not a console that caught up. This fails loudly in that case
    rather than quietly agreeing with itself.
    """
    console = clientpaths.doorless(app, surfaces=(clientpaths.CONSOLE,))
    union = clientpaths.doorless(app)
    assert len(union) < len(console), (
        f"the union backlog ({len(union)}) is no smaller than the console's "
        f"({len(console)}) — either every console gap is now a gap "
        "everywhere, or the native extractors have stopped finding calls")


def test_each_native_shell_is_still_being_read():
    """The count that would collapse first if a native extractor broke.

    The union guard's liveness check counts *console* call sites, so a
    silently-dead Swift or Kotlin pattern would not move it — the console
    alone covers most routes. It would move this one, and it would move it to
    zero.

    The floor is low because the three products' shells differ by a factor of
    three in size — PDI's whole API is thirty-four bindings. It is a check
    against *nothing*, not a target.
    """
    for lang in clientpaths.NATIVE:
        made = clientpaths.calls(lang)
        assert len(made) > 20, (
            f"only {len(made)} call sites extracted from the {lang.name} "
            "shell — its patterns have stopped matching, which would make "
            "the union backlog look better than it is")
