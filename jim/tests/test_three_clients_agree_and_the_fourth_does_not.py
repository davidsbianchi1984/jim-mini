"""Three clients do the thing. The fourth is the one somebody is holding.

Four clients written at different times will drift, and the drift that
matters is not the loud kind. It is a treatment applied in three of them
and skipped in the fourth — because every review of the three that agree
comes back clean, and the odd one out is only reached by whoever owns that
device. Two field faults in one week were exactly this, in opposite
directions: the console was the only client that did not trim a pasted
key, and then iOS was the only one that trimmed spaces without newlines.

    asked     does this client handle the input
    mattered  does it handle it the way the other three do

The claim is presence, not correctness. A pattern matching does not prove
the client handles the input well; it proves the client does the same kind
of thing its siblings do. Asymmetry is the signal worth failing on — a
treatment three clients thought necessary is one the fourth needs a reason
to skip, and "nobody noticed" is not a reason.

See `client_symmetry.txt` for the manifest and how to add to it.
"""
from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    raise AssertionError("no repo root above " + str(here))


REPO = _repo_root()
MANIFEST = Path(__file__).resolve().parent / "client_symmetry.txt"
CLIENTS = ("console", "ios", "android", "windows")


def _rows() -> list[tuple[str, str, str, str]]:
    out = []
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split(" | ")]
        assert len(parts) == 4, f"malformed row: {line}"
        out.append(tuple(parts))  # type: ignore[arg-type]
    return out


def _by_treatment() -> dict[str, dict[str, tuple[str, str]]]:
    grouped: dict[str, dict[str, tuple[str, str]]] = defaultdict(dict)
    for treatment, client, path, pattern in _rows():
        assert client in CLIENTS, f"unknown client {client!r}"
        assert client not in grouped[treatment], (
            f"{treatment!r} names {client} twice")
        grouped[treatment][client] = (path, pattern)
    return grouped


def _present(path_glob: str, pattern: str) -> tuple[bool, list[Path]]:
    """Does `pattern` appear in any file `path_glob` resolves to?

    Returns the files looked at as well, because "no file matched the
    glob" and "the files matched and the pattern did not" are different
    failures and the message has to say which.
    """
    paths = sorted(REPO.glob(path_glob)) if any(c in path_glob for c in "*?[") \
        else ([REPO / path_glob] if (REPO / path_glob).exists() else [])
    rx = re.compile(pattern)
    return any(rx.search(p.read_text(encoding="utf-8", errors="replace"))
               for p in paths), paths


def test_every_treatment_names_all_four_clients():
    """A guard on the guard, and the sharper half of the pair.

    A treatment written for three clients is not a partial entry — it is
    the defect this file exists to find, recorded as if it were the
    intent. Refusing the manifest means the missing client has to be
    faced when the row is written rather than when somebody's phone
    fails, and it stops the obvious way to quiet a failure below: delete
    the row that fails.
    """
    problems = []
    for treatment, rows in _by_treatment().items():
        missing = [c for c in CLIENTS if c not in rows]
        if missing:
            problems.append(f"{treatment!r} names no {', '.join(missing)} row")
    assert not problems, (
        "every treatment must say what all four clients do:\n    "
        + "\n    ".join(problems)
        + "\n  A treatment written for three clients is the bug, not the entry."
    )


def test_the_symmetry_manifest_says_how_many_it_carries():
    """The header count against the rows, the same pairing the other
    manifests in this suite carry — `shared_guards.txt` had drifted eight
    behind before one of these was written for it."""
    head = MANIFEST.read_text(encoding="utf-8").splitlines()[0]
    stated = int(re.search(r"^# status: manifest — (\d+) treatment", head).group(1))
    assert stated == len(_by_treatment()), (
        f"client_symmetry.txt says {stated} treatments and carries "
        f"{len(_by_treatment())}")


def test_the_manifest_points_at_files_that_exist():
    """A row whose glob matches nothing would report the treatment absent
    from that client for as long as the path stayed wrong, and a moved
    file is a likelier cause of that than a removed treatment. Told
    apart here so the failure below always means what it says."""
    problems = []
    for treatment, rows in _by_treatment().items():
        for client, (path_glob, _) in rows.items():
            _, paths = _present(path_glob, "")
            if not paths:
                problems.append(
                    f"{client}: {path_glob} matches no file "
                    f"(treatment: {treatment!r})")
    assert not problems, (
        "the manifest points at files the tree does not have — a path "
        "that moved, not a treatment that went:\n    " + "\n    ".join(problems))


def test_no_client_is_the_odd_one_out():
    """The check itself: what three clients do, the fourth does too.

    Reported per treatment with the odd client named, because that is the
    whole finding — knowing *which* one diverged is the difference between
    a fix and a search. A treatment absent from every client is reported
    separately: that is a stale manifest, not a client bug, and reading it
    as four failures would bury the one case that is really three.
    """
    absent_everywhere, odd = [], []
    for treatment, rows in _by_treatment().items():
        have = {c: _present(*rows[c])[0] for c in CLIENTS}
        missing = [c for c, ok in have.items() if not ok]
        if len(missing) == len(CLIENTS):
            absent_everywhere.append(treatment)
        elif missing:
            odd.append((treatment, missing,
                        [c for c in CLIENTS if c not in missing]))

    assert not absent_everywhere, (
        "no client shows these treatments, so the manifest is describing a "
        "tree that no longer exists rather than finding a gap:\n    "
        + "\n    ".join(repr(t) for t in absent_everywhere))

    assert not odd, "\n".join(
        f"{', '.join(have)} do this and {', '.join(missing)} does not:\n"
        f"    {treatment}\n"
        f"    The agreement of the others is what makes this one invisible — "
        f"it reviews clean everywhere except the device it breaks on. Either "
        f"apply it there, or change that client's row to what it really does "
        f"so the divergence is on the record."
        for treatment, missing, have in odd)
