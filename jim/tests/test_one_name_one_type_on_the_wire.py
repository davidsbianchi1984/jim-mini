"""One wire name, one meaning — and the type checker nobody was running.

`spoken` meant three things in this ecosystem at once:

* `guardian.guide_first_aid` → the CPR playbook steps read aloud, a **string
  list**;
* `presence.deepen` → the model's rewritten line, a **string**;
* `presence.say` → whether the beat was said out loud, a **boolean**.

The Windows client had already forked it into three records, each with its own
`JsonPropertyName("spoken")`, and nothing about that forking looked wrong to
anybody reading one record at a time. TypeScript could not fork it, because
`PresenceSpoken extends PresenceBeat` there — so the collision surfaced as

    Interface 'PresenceSpoken' incorrectly extends interface 'PresenceBeat'.
      Types of property 'spoken' are incompatible.
        Type 'boolean' is not assignable to type 'string'.

and sat on `main`, because **no suite in any of these three repositories ran
`tsc`**. The one tool able to see the problem was the one tool nobody had
wired up.

    asked     do the clients compile
    mattered  does anybody ever run the compiler

## The two guards here

`test_the_console_typechecks` runs `tsc --noEmit`. It costs about six seconds
and it is the direct fix: this defect cannot reach `main` again without
somebody deleting this test.

`test_no_wire_name_carries_two_types` is the general shape. It reads every
`JsonPropertyName` in the Windows client — the only file in this codebase
where the whole wire surface is declared with its types — and records names
that carry more than one. The record is ratcheted.

## Why the Windows client is the source of truth

Not because it is more correct, but because it is the most *complete
statement*. Swift decodes into structs spread across a file, Kotlin parses
`JSONObject` by hand, and TypeScript interfaces are erased at runtime. C#
records with `JsonPropertyName` are the one place a reader can see every wire
name and its type together, which is what makes the collision countable.
"""

import pathlib
import re
import shutil
import subprocess
import collections

import pytest
from . import ratchets

REPO = pathlib.Path(__file__).resolve().parents[2]
WINDOWS_CLIENT = REPO / "native/windows/ApiClient.cs"
RECORD = pathlib.Path(__file__).resolve().parent / "wire_name_collisions.txt"
CONSOLE = REPO / "app"


def _declared() -> dict[str, set[str]]:
    """Every wire name in the Windows client, and the types it is given."""
    src = WINDOWS_CLIENT.read_text(encoding="utf-8")
    pairs = re.findall(
        r'JsonPropertyName\("([\w_]+)"\)\]\s+([\w\[\]\?<>,\s]+?)\s+\w+[,)]', src)
    by: dict[str, set[str]] = collections.defaultdict(set)
    for name, typ in pairs:
        by[name].add(typ.strip().rstrip("?"))
    return by


def _colliding() -> dict[str, list[str]]:
    return {n: sorted(t) for n, t in _declared().items() if len(t) > 1}


def _recorded() -> set[str]:
    return {line.strip() for line in RECORD.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")}


# --- the type checker, actually run ----------------------------------------

def test_the_console_typechecks():
    """The direct fix. `tsc` was the only thing that could see `spoken`, and
    no suite ran it — so the error sat on `main` through several releases.

    Skipped rather than failed when node is absent: a developer without a
    toolchain should not be told their Python change broke the console. CI has
    node, and that is where this has to bite.
    """
    if not shutil.which("npx") or not (CONSOLE / "node_modules").exists():
        pytest.skip("no node toolchain here — this check belongs to CI")
    done = subprocess.run(["npx", "--no-install", "tsc", "--noEmit"],
                          cwd=CONSOLE, capture_output=True, text=True,
                          timeout=300)
    assert done.returncode == 0, (
        "the console does not typecheck:\n" + (done.stdout or done.stderr))


# --- one name, one type ------------------------------------------------------

def test_no_wire_name_carries_two_types():
    """A field name is the one piece of an API a reader carries from route to
    route. A name that changes meaning between them is the reader being misled
    by the thing they were told to rely on."""
    loose = {n: t for n, t in _colliding().items() if n not in _recorded()}
    assert not loose, "\n    ".join(
        [""] + [f"{n} is {' and '.join(t)}" for n, t in sorted(loose.items())]
    ) + ("\n  Give each meaning its own name — the way `spoken` became "
         "`spoken_steps`, `deepened_line` and `spoken` — or record it, but "
         "recording is ratcheted.")


def test_the_record_only_shrinks():
    ceiling = int(re.search(r"^# ceiling: (\d+)$",
                            RECORD.read_text(encoding="utf-8"), re.M).group(1))
    assert len(_recorded()) <= ceiling, (
        f"{len(_recorded())} collisions recorded, above the {ceiling} ceiling")


def test_no_recorded_name_has_been_fixed_without_striking_it():
    """A record naming a name that no longer collides makes the next reader
    trust the list less, and hides the fact that somebody did the work."""
    stale = sorted(_recorded() - set(_colliding()))
    assert not stale, (
        "these no longer collide and are still recorded:\n    "
        + "\n    ".join(stale) + "\n  Strike them.")


# --- the scan has to be able to see, and to fail ----------------------------

def test_the_scan_reads_the_whole_wire_surface():
    """A regex rewrite that matched nothing would report this product
    collision-free, which is the most flattering possible way to be broken."""
    assert len(_declared()) >= ratchets.floor("wire.declared"), (
        f"only {len(_declared())} wire name(s) parsed out of the Windows "
        f"client — the extractor has stopped matching")


def test_the_scan_would_catch_a_new_collision():
    """Driven against the shape `spoken` had, so the check is known to fire
    rather than assumed to."""
    src = '''
    public record A([property: JsonPropertyName("thing")] string Thing);
    public record B([property: JsonPropertyName("thing")] bool Thing);
    '''
    pairs = re.findall(
        r'JsonPropertyName\("([\w_]+)"\)\]\s+([\w\[\]\?<>,\s]+?)\s+\w+[,)]', src)
    by: dict[str, set[str]] = collections.defaultdict(set)
    for name, typ in pairs:
        by[name].add(typ.strip())
    assert by["thing"] == {"string", "bool"}, by
