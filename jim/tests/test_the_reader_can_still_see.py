"""The instrument, not the code: can each reader still see?

0.58.7 found a missing brace by auditing a reader rather than the thing it
read, and closed by naming the general case: **a blind instrument is
indistinguishable from a clean repository.** Every guard in this estate has a
reader. The route audit's is the oldest and the most load-bearing — six other
files ask `clientpaths` what each client calls, and a route table read short
narrows all of them at once, silently, in the safe direction.

## What the probe found

The console *is* protected — an explicit floor under its extracted calls,
written when the console was the only client. The three native shells have
**no floor at all.** Their protection is incidental: a scatter of per-block
and per-form tests written by earlier rounds that happen to name routes those
readers see. Blinding QRME's iOS `request(` form drops it 430 → 11 call sites,
and what fails there is a handful of block guards — not one of them saying
*the iOS reader has stopped reading*. A narrowing that misses the blocks those
tests happen to cover passes in silence, and the same shape holds here.

    asked     do the clients call every route
    mattered  can the reader still see the clients

## Two floors, because they fail differently

**An absolute floor per client.** Set at roughly four-fifths of what each
reader sees today. It catches the slow case — a reader narrowed over several
rounds until it covers a fraction of the surface — which no single diff would
make obvious.

**A spread check across the three native shells.** iOS, Android and Windows
are one client written three times — the same screens, the same routes, ported
by hand. When one drops far below the other two while they hold, that is the
reader breaking and not the shell shrinking, and it needs no number chosen by
hand to say so.

The console is deliberately outside that comparison, and the reason is
measured rather than assumed: JIM-mini's console extracts 251 call sites
against 114 on each phone, and PDI's 121 against 35. Those consoles carry
surface the phones do not, so a spread rule spanning all four would have to be
loosened until it caught nothing. The absolute floor is what holds the console.

The floors would let all readers drift down together; the spread would let all
three shells break together. Neither happens by accident.

## The floors are ratchets, not targets

They record what the reader reaches today. Raising one when a client grows is
ordinary; lowering one is a deliberate edit that shows up in a diff, and the
only honest reason to do it is a client that genuinely got smaller.
"""

from __future__ import annotations

from jim.api import app

from . import clientpaths, ratchets

#: (language, the floor under its extracted call sites). Measured, then set
#: to about four-fifths — low enough not to trip on ordinary movement, high
#: enough that a reader covering a fraction of the surface cannot pass.
FLOORS = tuple(
    (lang, ratchets.floor(f"route.calls.{lang.name}"))
    for lang in (clientpaths.CONSOLE, clientpaths.IOS,
                 clientpaths.ANDROID, clientpaths.WINDOWS))

#: The route table's own floor. `all_routes` walks FastAPI's included-router
#: wrappers; the flat `app.routes` showed 8 of 409 once, and the first version
#: of the doorless audit reported zero on that basis and passed.
ROUTE_FLOOR = ratchets.floor("route.table")

#: How far below the busiest shell the quietest may sit. The three are one
#: client ported three times, so a reader seeing a third of what its ports
#: see is a reader that broke.
SPREAD = 0.55


#: The three shells are ports of one another, so their counts are comparable.
#: The console is not a fourth port; see the docstring.
SHELLS = (clientpaths.IOS, clientpaths.ANDROID, clientpaths.WINDOWS)


def _seen() -> dict[str, int]:
    return {lang.name: len(clientpaths.calls(lang)) for lang in SHELLS}


def test_every_client_reader_still_reaches_its_floor():
    """The slow failure: a reader narrowed a form at a time until it covers a
    fraction of the surface, with every individual step looking harmless."""
    low = []
    for lang, floor in FLOORS:
        found = len(clientpaths.calls(lang))
        if found < floor:
            low.append(f"{lang.name}: {found} call sites extracted, floor "
                       f"{floor} — the reader is missing a form it used to see")
    assert not low, "\n    ".join([""] + low) + (
        "\n  A client the audit cannot read is a client nothing is auditing.")


def test_no_shell_reader_falls_far_behind_its_ports():
    """The fast failure, caught without a hand-chosen number.

    Three shells, one client, ported by hand from each other. One reader at a
    third of the others is not a smaller shell.
    """
    seen = _seen()
    busiest = max(seen.values())
    behind = [f"{name}: {n} against {busiest} on the busiest client"
              for name, n in sorted(seen.items())
              if n < busiest * SPREAD]
    assert not behind, "\n    ".join([""] + behind) + (
        f"\n  Below {SPREAD:.0%} of the busiest shell, this is the reader "
        "breaking rather than the shell shrinking.")


def test_the_route_table_is_read_whole():
    """`app.routes` is not the route table. It showed 8 of 409 once, and the
    audit built on it reported a clean bill."""
    routed = clientpaths.all_routes(app)
    assert len(routed) >= ROUTE_FLOOR, (
        f"only {len(routed)} routes found, floor {ROUTE_FLOOR} — the walk over "
        "the included routers is not reaching them")


def test_the_floors_are_under_what_is_actually_there():
    """A floor set above the truth fails every run and gets lowered until it
    means nothing; one set far below it is decoration. This keeps the table
    honest about being a ratchet — every floor must be reachable now, and
    within sight of what is reached."""
    for lang, floor in FLOORS:
        found = len(clientpaths.calls(lang))
        assert found >= floor, f"{lang.name}: floor {floor} above actual {found}"
        assert floor >= found * 0.5, (
            f"{lang.name}: floor {floor} is less than half of {found} — "
            "raise it, or it is not holding anything")


def test_a_narrowed_reader_is_caught(monkeypatch):
    """The real thing, as a unit, measured next door: QRME's iOS reader with
    its `request(` form dropped fell from 430 call sites to 11, and no floor
    anywhere said so."""
    seen = {"ios": 11, "android": 431, "windows": 431}
    busiest = max(seen.values())
    behind = [n for n, v in seen.items() if v < busiest * SPREAD]
    assert behind == ["ios"]
    assert seen["ios"] < dict((l.name, f) for l, f in FLOORS)["ios"]
