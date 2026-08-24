"""A claim about a platform, made in a file nobody ran on that platform.

`away.ts` says a backgrounded page has its recogniser ended by the browser,
which is true. A later round added the other half — that `getUserMedia` is
different, that an open capture keeps recording while the window is minimised
— and wrote it as a universal in every console that hears.

    asked     was the claim tested
    mattered  was it tested on the platform it was made about

It was not. iOS Safari suspends the whole page the moment you leave it,
capture included, and reports nothing on the way out. A field report walked on
an iPhone, swiped up to the home screen, came back, and found the conversation
had stopped in silence. One of the docstrings making the claim named iOS as
the example that *proves* it — "the same bargain iOS makes with its orange
dot" — which is true of a native iOS application and false of a Safari page,
and is why the belief felt settled enough to copy.

    asked     which of the two ways of hearing was it using
    mattered  does the platform let either of them run out there

## Why this is in all three suites

PDI's console has no microphone and makes the claim nowhere, so this guard
finds nothing there today and passes. That is the point: the claim spread by
being copied between consoles, and the day a capture arrives in the third one
the sentence that comes with it will meet a guard that was already waiting.
The alternative was a row in `guard_divergences.txt`, whose ceiling does not
move up and whose own rule is that a new divergence is a fix that did not
travel. This one can travel.

A comment that overstates what was tested is how the next person stops
testing it.
"""

from pathlib import Path


def _repo() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


APP = _repo() / "app" / "src"

#: The unqualified half of the claim. A file carrying it must say where it
#: does not hold.
CLAIM = "keeps recording while the window is minimised"

#: The sentence that offered the exception as the proof. Banned by its own
#: words rather than by the file it was in, because it was copied.
BACKWARDS = "same bargain iOS makes with its orange dot"


def _sources() -> dict[str, str]:
    """Every TypeScript source in this product's console."""
    return {str(p.relative_to(APP)): p.read_text(encoding="utf-8")
            for p in sorted(APP.rglob("*.ts")) + sorted(APP.rglob("*.tsx"))}


def test_the_reader_can_still_see_this_console():
    """A guard on the guard. Both checks below pass on an empty set, and an
    APP path that stopped resolving would produce exactly that."""
    assert APP.is_dir(), f"{APP} is not a directory — this guard reads nothing"
    assert _sources(), "no TypeScript sources found in this console"


def test_the_claim_about_surviving_names_its_exception():
    """Every file making the claim says where it does not hold."""
    guilty = sorted(name for name, src in _sources().items()
                    if CLAIM in src and "iOS Safari" not in src)
    assert not guilty, (
        "these files claim an open capture survives the window being "
        "minimised without naming the platform where it does not:\n    "
        + "\n    ".join(guilty)
        + "\n  iOS Safari suspends the whole page, capture included. A "
          "console that carries the claim unqualified will be copied from.")


def test_ios_is_not_offered_as_proof_of_the_rule_it_breaks():
    guilty = sorted(name for name, src in _sources().items()
                    if BACKWARDS in src)
    assert not guilty, (
        "these files still offer iOS as the example confirming that a "
        "capture survives a hidden page:\n    " + "\n    ".join(guilty)
        + "\n  The orange dot is what a native iOS application earns. A "
          "Safari page gets suspended instead, which is the opposite fact.")
