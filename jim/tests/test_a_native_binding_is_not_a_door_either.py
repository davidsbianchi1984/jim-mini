"""`test_a_binding_is_not_a_door.py`, for the other three clients.

That file exists because `clientpaths.doorless` counts **call sites**, so a
function written in `api.ts` and wired to no screen takes its route off the
backlog whether or not anything ever calls it. Its own docstring puts the cost
plainly:

    A round that adds thirty bindings and five screens will report thirty
    doors and have built five.

It checks `app/src/api.ts`. There are four clients, and the other three have
`ApiClient.swift`, `ApiClient.kt` and `ApiClient.cs` — files of exactly the
same kind, with exactly the same property, and nothing has ever looked at
them.

This is the third time in this audit that a guard turned out to cover one
surface of four. The union guard did it, the door guard did it, and now the
binding guard. The lesson is not that somebody was careless; it is that
"client" reads as singular when you are writing the check and there are four
of them when somebody runs the app.

## What it found on its first run

Eight bindings across the three products, and three of them are the same
shape — a shell that carries the act which **creates** a power and not the act
which **ends** it:

* **QRME, iOS.** `SignatureView` lists your signing credentials and calls
  nothing to revoke one. A signing credential signs documents as you. The
  screen that shows you a credential on a device you no longer hold offers no
  way to take it away.

* **JIM-mini, iOS.** `FamilyView` calls `enrollChild`, `children`,
  `childOverview`, `guardianWatch` and `setFamilyControls`. It does not call
  `unlinkChild`. A guardian can begin watching a child from a phone and cannot
  stop — and a guardian link is a surveillance relationship that outlives the
  reason for it: children grow up, custody changes, households end.

* **PDI, Android and Windows.** `robotKeys` reads what a bound robot has put
  into the vault. Written in both shells, called in neither.

The rest were `health` and `setBase` — genuinely unused plumbing rather than a
capability with no door, and recorded rather than deleted, because the next
shell that needs a backend-URL field will want `setBase` there.
"""

from __future__ import annotations

import re
from pathlib import Path


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()
SNAPSHOT = Path(__file__).resolve().parent / "unused_native_bindings.txt"

#: Where it stood when this guard was written.
STARTED_AT = 3


def _swift() -> list[str]:
    api = REPO / "native/ios/Sources/ApiClient.swift"
    if not api.exists():
        return []
    names = set(re.findall(r"^\s{4}func (\w+)\(", api.read_text(encoding="utf-8"), re.M))
    callers = "\n".join(
        p.read_text(encoding="utf-8", errors="ignore")
        for p in (REPO / "native/ios").rglob("*.swift") if p != api)
    return [f"ios.{n}" for n in sorted(names)
            if not re.search(rf"\.{n}\s*\(", callers)]


def _kotlin() -> list[str]:
    found = list((REPO / "native/android").rglob("ApiClient.kt"))
    if not found:
        return []
    api = found[0]
    names = set(re.findall(r"^\s{4}(?:suspend )?fun (\w+)\(",
                           api.read_text(encoding="utf-8"), re.M))
    callers = "\n".join(
        p.read_text(encoding="utf-8", errors="ignore")
        for p in (REPO / "native/android").rglob("*.kt") if p != api)
    return [f"android.{n}" for n in sorted(names)
            if not re.search(rf"\.{n}\s*\(", callers)]


def _csharp() -> list[str]:
    api = REPO / "native/windows/ApiClient.cs"
    if not api.exists():
        return []
    names = set(re.findall(r"^\s{4}public (?:async )?Task[^\s]*\s+(\w+)\(",
                           api.read_text(encoding="utf-8"), re.M))
    callers = "\n".join(
        p.read_text(encoding="utf-8", errors="ignore")
        for p in (REPO / "native/windows").rglob("*.cs") if p != api)
    return [f"windows.{n}" for n in sorted(names)
            if not re.search(rf"\.{n}\s*\(", callers)]


def _unused() -> list[str]:
    return sorted(_swift() + _kotlin() + _csharp())


def _rows() -> list[str]:
    return [line.strip() for line in
            SNAPSHOT.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")]


def _recorded() -> list[str]:
    """The binding names, without the reasons that now sit beside them."""
    return [row.split(" — ", 1)[0].strip() for row in _rows()]


def test_every_recorded_binding_says_why_it_is_recorded():
    """The reasons for these used to live in this file's module docstring —
    true, careful, and one file away from the list they explained. A record
    whose justification is somewhere else reads, at the place somebody actually
    looks, as an unexplained backlog.

        asked     is the exemption explained
        mattered  is it explained where the exemption is
    """
    bare = [row for row in _rows() if " — " not in row or
            len(row.split(" — ", 1)[1].strip()) < 20]
    assert not bare, (
        f"{len(bare)} recorded binding(s) carry no reason on the row:\n    "
        + "\n    ".join(bare)
        + "\n  Write why it is here, after an em dash, or strike it.")


def test_the_unused_native_bindings_match_the_record():
    """Both directions. A binding that has *gained* a caller is as much a
    change to report as one that has lost it."""
    actual, recorded = set(_unused()), set(_recorded())
    appeared, resolved = sorted(actual - recorded), sorted(recorded - actual)

    problems = []
    if appeared:
        problems.append(
            f"{len(appeared)} native binding(s) nothing calls:\n    "
            + "\n    ".join(appeared)
            + "\n  (wire it to a screen, or record it here — but note that "
              "its route is being counted as doored either way)")
    if resolved:
        problems.append(
            f"{len(resolved)} native binding(s) now have a caller — strike "
            f"them from {SNAPSHOT.name}:\n    " + "\n    ".join(resolved))
    assert not problems, "\n\n".join(problems)


def test_it_only_shrinks():
    assert len(_recorded()) <= STARTED_AT, (
        f"{len(_recorded())} unused native bindings, above the {STARTED_AT} "
        "this guard started at — bindings are being written faster than the "
        "screens that call them, which is what inflates the door count")


def test_the_extractors_are_reading_something():
    """A guard on the guard, and it is not decorative: this file's whole job
    is to report an *absence*, and an extractor that finds no functions at all
    reports a beautiful zero.

    Five false positives in this audit have come from a pattern that quietly
    stopped matching. This one fails loudly instead.
    """
    api = REPO / "native/ios/Sources/ApiClient.swift"
    if api.exists():
        n = len(re.findall(r"^\s{4}func (\w+)\(",
                           api.read_text(encoding="utf-8"), re.M))
        assert n > 20, (
            f"only {n} Swift bindings found — the pattern has stopped "
            "matching, so an empty result here would mean nothing")


def test_the_shell_can_end_what_it_can_begin():
    """The specific shape this guard was written after finding.

    A screen that creates a standing relationship — a signing credential, a
    guardian's link to a child — and cannot end it leaves the person who made
    it dependent on a surface they may not have. It is the same asymmetry the
    phone guard found one level up, where the shells carried the profile
    owner's half of governance and not the objector's.
    """
    ios = REPO / "native/ios/Sources"
    if not ios.exists():
        return
    # **Excluding ApiClient.swift.** The first version of this did not, and
    # passed — by matching each binding's own definition. That is the sixth
    # time in this audit that a check has been satisfied by the thing it was
    # meant to look past: four extractors, one guard written to catch them,
    # and now this. The pattern is always the same shape — searching a body
    # of text for a name, in a corpus that contains the declaration of the
    # name.
    api = ios / "ApiClient.swift"
    text = "\n".join(p.read_text(encoding="utf-8", errors="ignore")
                     for p in ios.rglob("*.swift") if p != api)
    pairs = [
        ("enrollChild(", "unlinkChild(",
         "iOS links a child to a guardian and cannot unlink one — a "
         "surveillance relationship that outlives the reason for it: "
         "children grow up, custody changes, households end"),
    ]
    broken = [why for begin, end, why in pairs
              if begin in text and end not in text]
    assert not broken, "\n  ".join(broken)
