"""One product, one way of addressing the reader.

German and Spanish both distinguish a formal *you* from an informal one, and
that choice is a claim about the relationship — not a synonym. This estate
made both claims at once. A German reader met *Sie* on the desktop console
and *du* on the phone, and both registers inside each of those tables; JIM
addressed the same person formally in German and informally in Spanish.

    asked     is the string translated
    mattered  who does it think it is talking to

The decision is informal — *du* and *tú* — taken because every phone shell
already leaned that way and because these are personal products: a guardian
on somebody's wrist, somebody's own profile.

This counts the rows still written formally and holds the number down. It
never moves up: a new formal row is a screen addressing the reader in the
register the rest of the product does not use.

## What is deliberately not counted

**Spanish `su` / `sus`.** Ambiguous between formal-*your* and third-person
*their* or *its*, and in this estate the overwhelming majority are the
latter — *la bóveda relee cada página según su horario* is the vault's own
schedule, and *te dio un lugar en su transmisión* already addresses the
reader informally. Counting them produced 327 rows where the truth was 23,
and a conversion driven off that number would have corrupted every sentence
about somebody else.

**Spanish `ustedes` as a plural.** *Entre ustedes dos* stays. In Latin
American Spanish `ustedes` is the ordinary plural *you* regardless of
register — Spain's `vosotros` is the regional form — so rewriting it would
narrow the audience rather than warm the tone.
**German `Sie` at the start of a sentence.** `sie` is *she*/*they*/*it* and
capitalises like any word does when a sentence opens with it, so a row can
read as formal address while being entirely third person. *Sie zu erstellen
gewährt nichts* is *to create **it** grants nothing*, about a standing
instruction; *Sie authentifiziert sich mit dem Token* is the counterparty,
not the reader. Rewriting either would break the German rather than warm it.
These are counted — a detector that guessed would be worse — so a table's
floor is not always zero, and the rows behind a floor that will not move are
listed in the ledger beside it.
"""

from __future__ import annotations

import re
from pathlib import Path

#: Formal address in German. Capitalised on purpose: `sie` is *she*/*they*
#: and `ihr` is *her*/*their*; only the capitalised forms are the polite
#: second person, outside a sentence-initial position that German prose in
#: these tables does not produce for the lowercase senses.
DE_FORMAL = re.compile(r'\b(Sie|Ihnen|Ihre[rmns]?|Ihr)\b')

#: Formal address in Spanish. `usted`/`ustedes` only — see the docstring for
#: why `su`/`sus` is not here.
ES_FORMAL = re.compile(r'\b(usted|Usted)\b')

#: How each client stores one language's string.
SHAPES = {
    ".ts": r'{lang}:\s*"((?:[^"\\]|\\.)*)"',
    ".kt": r'"{lang}"\s+to\s+"((?:[^"\\]|\\.)*)"',
    ".swift": r'"{lang}":\s*"((?:[^"\\]|\\.)*)"',
    ".cs": r'\["{lang}"\]\s*=\s*"((?:[^"\\]|\\.)*)"',
}


def _repo() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo()
LEDGER = Path(__file__).with_name("formal_register.txt")


def _tables() -> list[Path]:
    out = [REPO / "app" / "src" / "l10n.ts"]
    out += sorted(REPO.glob("native/**/L10n.kt"))
    out += sorted(REPO.glob("native/**/L10n.swift"))
    out += sorted(REPO.glob("native/**/L10n.cs"))
    return [p for p in out if p.exists()]


def rows(path: Path, lang: str) -> list[str]:
    shape = SHAPES.get(path.suffix)
    if not shape:
        return []
    return re.findall(shape.format(lang=lang),
                      path.read_text(encoding="utf-8"))


def counted() -> dict[str, int]:
    """{table: formal rows} across both languages."""
    out = {}
    for path in _tables():
        n = sum(1 for r in rows(path, "de") if DE_FORMAL.search(r))
        n += sum(1 for r in rows(path, "es") if ES_FORMAL.search(r))
        out[str(path.relative_to(REPO))] = n
    return out


def _ceilings() -> dict[str, int]:
    out = {}
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        table, n = line.rsplit(" ", 1)
        out[table.strip()] = int(n)
    return out


def test_no_table_gains_a_formal_row():
    """The ratchet. A row written formally is a screen addressing the reader
    in a register the rest of the product does not use."""
    now, ceiling = counted(), _ceilings()
    over = {t: (n, ceiling.get(t)) for t, n in now.items()
            if ceiling.get(t) is not None and n > ceiling[t]}
    assert not over, (
        "formal rows above the recorded ceiling — the register is informal "
        "(du / tú):\n    "
        + "\n    ".join(f"{t}: {n}, recorded {c}" for t, (n, c) in over.items()))


def test_every_table_is_recorded():
    """A table nobody counted is a table the ratchet does not hold."""
    missing = sorted(set(counted()) - set(_ceilings()))
    assert not missing, f"tables missing from the ledger: {missing}"


def test_the_ledger_names_no_table_that_is_gone():
    """The other direction: a row for a file that moved is a number nothing
    measures."""
    stale = sorted(set(_ceilings()) - set(counted()))
    assert not stale, f"ledger rows for tables that no longer exist: {stale}"


def test_spanish_is_already_informal():
    """Spanish was 23 rows, not the 327 a `su`/`sus` count reported, and it
    is finished. The three that remain are `ustedes` as a plural, which is
    the ordinary Latin American form and not a register at all."""
    left = []
    for path in _tables():
        for r in rows(path, "es"):
            if ES_FORMAL.search(r):
                left.append((str(path.relative_to(REPO)), r[:60]))
    assert not left, f"formal Spanish returned: {left}"
