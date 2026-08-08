"""The localizer's reader, held to a number instead of a hope.

0.58.8 audited the route reader and found the three native shells had no floor
at all — the console had one, written when it was the only client, and the
phones were protected only by whatever block guards happened to name routes
they saw. It closed by naming the next reader with the same shape available
and unused: the one that reads the L10n tables.

That reader has the same hole, and worse numbers.

## What the probe found

`test_a_shell_asks_for_a_key_it_has.py` is a good guard with a floor that has
not moved since it was written here. It asserts each shell extracts **at least
ten** localizer calls and holds **at least twenty** table rows, as a canary
against the pattern silently ceasing to match. The tables have since grown to
286, 301 and 312 rows, and the screens to 279, 300 and 312 call sites.

    ten against two hundred and seventy-nine

A floor at a thirtieth of the truth is not holding much. A reader down to a
tenth of its surface walks past it.

## Why the rest of the file does not cover for it

The three checks around it protect the other two readers and not this one:

* `_held` going blind fails loudly — every key a screen asks for stops being
  in the table, and the first test reports hundreds of missing rows.
* `_reached` going blind or going wide fails loudly — the dead-row set moves
  and the backlog reports undecided or stale rows.
* `_asked` going blind is **silent**, because `_reached` falls back to
  `_MENTIONED`, which finds every dotted string literal in the sources
  whether or not a localizer call is in front of it.

Measured rather than argued. Narrowing the call pattern so it matches only
`L10n.t("…")` — no whitespace, lowercase method — is an ordinary-looking tidy
that blinds C# alone, because Windows spells it `L10n.T(`:

    ios      300 call sites
    android  312 call sites
    windows    4 call sites

The dead-row path barely notices, and what it notices it misnames: the only
rows it can still see going quiet are the six in this shell without a dot in
them, because `_MENTIONED` requires one. They surface as *translated rows
nothing asks for* — a backlog complaint. Nothing in that message says the
reader stopped reading. PDI's shells have no dotless keys at all, so there the
same blinding reports nothing whatsoever through that path.

    asked     does every key a screen wants have a row
    mattered  can the reader still see the screens asking

## Two floors, because they fail differently

**Absolute, per shell, on both halves.** Set at roughly four-fifths of what
each reader reaches today. It catches the slow case — a form dropped here, a
suffix there, over several rounds — which no single diff makes obvious.

**A spread across the three shells**, which needs no number chosen by hand.
iOS, Android and Windows are one client written three times: the same screens,
ported by hand, so their tables are near-identical in size. Measured, the
quietest shell sits at 89% of the busiest in this product, 98% in QRME and 77%
in PDI. A shell at 1% of its ports is not a smaller shell.

The console is deliberately not a fourth port here, and the reason is measured
rather than assumed: it holds **675 rows and shares 62 of them** with the
shells. The two vocabularies are separate — `app/src/l10n.ts` is the desktop
frame, the shell tables are the phone screens — so neither a spread rule nor a
superset rule between them would mean anything.

## And the debt the backlog records

`native_dead_keys.txt` carries a per-shell count that has never been compared
across shells. The ratchet asks whether the number is going up; it does not
ask whether one shell is carrying far more of it than its ports. Most of those
rows are not waste — they are screens that exist on three shells and say less
on one. That is exactly a per-shell comparison, and it was sitting in the file
unmade.

This product's record is empty and its ceiling is zero, so the check skips and
says so. It is here for the same reason the floors are: the day a row is
recorded, the comparison exists already.

One-sided on purpose: a shell *below* its ports has paid its debt down, which
is the direction this is all for.
"""

from __future__ import annotations

import collections
import re
from pathlib import Path

import pytest

from . import ratchets
from .test_a_shell_asks_for_a_key_it_has import SHELLS, _asked, _held

#: shell -> (floor under its extracted call sites, floor under its table rows).
#: Measured, then set to about four-fifths — low enough not to trip on
#: ordinary movement, high enough that a reader covering a fraction of the
#: surface cannot pass. Per shell rather than one number, so a shell that
#: genuinely grows can be raised on its own.
FLOORS = {shell: (ratchets.floor(f"l10n.asked.{shell}"),
                  ratchets.floor(f"l10n.held.{shell}"))
          for shell in ("ios", "android", "windows")}

#: How far below the busiest shell the quietest may sit. The three are one
#: client ported three times; see the docstring for the measured spreads.
SPREAD = 0.60

#: How many times its quietest port a shell may carry in recorded dead rows
#: before that is a screen falling behind rather than ordinary unevenness.
DEBT_RATIO = 2.5

#: Below this the ratio is noise — three rows against one is not a signal.
DEBT_FLOOR = 20


def _counts() -> dict[str, tuple[int, int]]:
    return {shell: (len(_asked(shell)), len(_held(shell))) for shell in SHELLS}


def _recorded() -> dict[str, int]:
    path = Path(__file__).resolve().parent / "native_dead_keys.txt"
    rows = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")]
    return dict(collections.Counter(row.split(": ", 1)[0] for row in rows))


@pytest.mark.parametrize("shell", sorted(SHELLS))
def test_every_shell_reader_still_reaches_its_floor(shell):
    """The slow failure: a form at a time, every step looking harmless."""
    asked_floor, held_floor = FLOORS[shell]
    asked, held = len(_asked(shell)), len(_held(shell))
    low = []
    if asked < asked_floor:
        low.append(f"{asked} localizer calls extracted, floor {asked_floor} — "
                   "the call pattern has lost a form it used to see")
    if held < held_floor:
        low.append(f"{held} table rows parsed, floor {held_floor} — the row "
                   "pattern has lost a syntax it used to see")
    assert not low, f"{shell}:\n    " + "\n    ".join(low) + (
        "\n  A shell the audit cannot read is a shell nothing is auditing: "
        "every check in test_a_shell_asks_for_a_key_it_has.py passes on what "
        "this reader hands it.")


def test_no_shell_reader_falls_far_behind_its_ports():
    """The fast failure, caught without a hand-chosen number.

    Three shells, one client, ported by hand from each other. One reader at a
    hundredth of the others is not a smaller shell — it is a pattern that
    stopped matching that shell's language.
    """
    counts = _counts()
    behind = []
    for i, half in enumerate(("localizer calls", "table rows")):
        seen = {shell: pair[i] for shell, pair in counts.items()}
        busiest = max(seen.values())
        behind += [f"{shell}: {n} {half} against {busiest} on the busiest shell"
                   for shell, n in sorted(seen.items())
                   if n < busiest * SPREAD]
    assert not behind, "\n    ".join([""] + behind) + (
        f"\n  Below {SPREAD:.0%} of the busiest shell, this is the reader "
        "breaking rather than the shell shrinking.")


def test_the_floors_are_under_what_is_actually_there():
    """A floor above the truth fails every run and gets lowered until it means
    nothing; one far below it is decoration. Both halves must be reachable
    now, and within sight of what is reached — which is the check the ten in
    the older file would not survive."""
    for shell, (asked_floor, held_floor) in sorted(FLOORS.items()):
        asked, held = len(_asked(shell)), len(_held(shell))
        for name, floor, found in (("asked", asked_floor, asked),
                                   ("held", held_floor, held)):
            assert found >= floor, (
                f"{shell}/{name}: floor {floor} above actual {found}")
            assert floor >= found * 0.5, (
                f"{shell}/{name}: floor {floor} is less than half of {found} "
                "— raise it, or it is not holding anything")


def test_the_shell_table_is_a_reader_and_not_a_hard_coded_list():
    """A guard on this guard. If `SHELLS` ever stops naming the three shells
    the older file walks, these floors hold nothing and say so cheerfully."""
    assert set(FLOORS) == set(SHELLS), (
        f"floors cover {sorted(FLOORS)}, shells are {sorted(SHELLS)}")


def test_no_shell_carries_far_more_untranslated_debt_than_its_ports():
    """The comparison the backlog file had the numbers for and never made.

    Most rows in `native_dead_keys.txt` are not waste — they are a screen that
    exists on three shells and says less on one. The ceiling asks whether the
    number is rising. This asks whether one shell is carrying the debt.
    """
    recorded = _recorded()
    if not recorded or max(recorded.values()) < DEBT_FLOOR:
        pytest.skip("too few recorded rows for a ratio to mean anything")
    quietest = max(min(recorded.values()), 1)
    heavy = [f"{shell}: {n} recorded rows against {quietest} on the quietest "
             "shell" for shell, n in sorted(recorded.items())
             if n > quietest * DEBT_RATIO]
    assert not heavy, "\n    ".join([""] + heavy) + (
        f"\n  Above {DEBT_RATIO:g}× its quietest port, this is a shell whose "
        "screens are falling behind their siblings rather than an uneven "
        "backlog. Wire the screens or split the record.")


def test_a_narrowed_reader_is_caught():
    """The real thing, as a unit.

    Narrowing the call pattern to `L10n.t("…")` — no whitespace, lowercase
    method — blinds C# alone, because Windows spells it `L10n.T(`. It dropped
    Windows from 279 call sites to 4 while its two ports held, and the dead-row
    path saw only the handful of rows in that shell without a dot in them.
    """
    seen = {"ios": 300, "android": 312, "windows": 4}
    busiest = max(seen.values())
    assert [s for s, n in seen.items() if n < busiest * SPREAD] == ["windows"]
    assert seen["windows"] < FLOORS["windows"][0]
