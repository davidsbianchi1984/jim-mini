"""A screen may describe an accountless door. It may not *be* one and lie.

QRME's copy of this idea started as: *no gated surface may say "you do not
need an account"*. That caught its real defect — `Contest.tsx` carried the
objection form itself, with the promise attached, on a tab requiring exactly
what the promise disclaimed.

Ported here unchanged it would fire on four screens, and all four are correct:

    Safety.tsx     the beacon "needs no account and sees only what you chose
                   to put on the card"
    Reach.tsx      "Raising from a scanned code takes no account"
    Settings.tsx   device speech is "no account needed"
    (PDI) Carriers the carrier scan page "needs no account"

Every one is an **owner being told what their own beacon does for a stranger**,
and the stranger-facing page it describes genuinely exists and is genuinely
public. Settings' is a third meaning altogether: no *third-party* account.

So the check is not "does this surface make the claim". It is:

    does this surface make the claim **and** carry the call the claim is
    about?

Claim plus call, behind the gate, is the defect: the thing being promised is
right here, and the promise is false for anybody who believes it. Claim alone
is a description of somewhere else, which is what a beacon owner needs to
read.

That distinction is the whole point of this file. A guard that cannot draw it
would flag three correct screens, and this audit has now caught seven checkers
answering a question slightly to the left of the one that mattered — adding an
eighth to catch the seventh would be a poor trade.
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
SRC = REPO / "app" / "src"

#: Bindings whose route is public *because its caller has no account*. Not
#: every uncredentialed binding — only the ones written for a stranger.
PUBLIC_BINDINGS = ("alarmGuidance",)

CLAIM = re.compile(
    r"no account|without an account|takes no account|needs no account",
    re.I)


def _prose(path: Path) -> str:
    """Source with comments stripped.

    Not optional. `Attending.tsx` carries a comment reading *"the person it
    was written for has no account"* directly above its `alarmGuidance` call —
    claim and call on one surface, which is exactly the pattern below. It is a
    comment explaining the round that put it there, read by nobody using the
    app. Matching it would be the eighth false positive in this audit and the
    third inside a guard written to prevent one.
    """
    text = path.read_text(encoding="utf-8")
    code = re.sub(r"/\*.*?\*/|//[^\n]*|\{/\*.*?\*/\}", "", text, flags=re.S)
    # And the English behind every key this screen looks up.
    #
    # The tripwire below anticipated this day and has now been removed: the
    # console grew `l10n.ts`, so a claim made through a key would otherwise be
    # invisible to every check in this file — including on a screen that also
    # carries the door, which is the whole defect this file exists to catch.
    #
    #     asked     does this screen's file contain the claim
    #     mattered  does this screen make the claim
    return "\n".join([code] + [_english()[k] for k in
                               _LOOKUP.findall(code) if k in _english()])


_LOOKUP = re.compile(r'\b(?:t|tr|L)\(\s*"([\w.]+)"')


def _english() -> dict[str, str]:
    """Every key's English, from the console's table. Empty if there is none."""
    table = SRC / "l10n.ts"
    if not table.exists():
        return {}
    text = table.read_text(encoding="utf-8")
    out: dict[str, str] = {}
    for key, row in re.findall(r'^  "([\w.]+)":\s*\{(.*?)^  \},', text,
                               re.S | re.M):
        hit = re.search(r'\ben:\s*"((?:[^"\\]|\\.)*)"', row)
        if hit:
            out[key] = hit.group(1)
    return out


def _gated_screens() -> list[Path]:
    """Everything App.tsx renders only after `session.userId` exists."""
    app = (SRC / "App.tsx").read_text(encoding="utf-8")
    assert "if (!session.userId)" in app, (
        "App.tsx's session gate has moved — this file no longer knows which "
        "screens are behind it")
    return sorted((SRC / "screens").glob("*.tsx"))


def test_no_gated_screen_both_promises_and_carries():
    broken = []
    for path in _gated_screens():
        code = _prose(path)
        if not CLAIM.search(code):
            continue
        called = [b for b in PUBLIC_BINDINGS if re.search(rf"\b{b}\s*\(", code)]
        if called:
            broken.append(f"{path.name}: claims no account and calls "
                          f"{', '.join(called)}")
    assert not broken, (
        "these screens promise that no account is needed and carry the very "
        "thing they are promising about, behind the sign-in gate:\n    "
        + "\n    ".join(broken)
        + "\n  Move the door to a surface a stranger can reach, or stop making "
          "the promise on this one.")


def test_the_check_does_not_fire_on_a_description():
    """A positive control, because a guard that passes on everything and a
    guard that discriminates look identical from a green suite.

    These three screens make the claim and must not be flagged. If a future
    edit makes this test fail, the check above has stopped telling a
    description apart from an offer, and it will start costing people time on
    correct code.
    """
    describing = ["Safety.tsx", "Reach.tsx", "Settings.tsx"]
    present = {p.name for p in _gated_screens()}
    missing = [n for n in describing if n not in present]
    assert not missing, f"these screens have been renamed or removed: {missing}"

    for name in describing:
        code = _prose(SRC / "screens" / name)
        assert CLAIM.search(code), (
            f"{name} no longer makes a no-account claim — this control is "
            "now vacuous, so remove it or point it at a screen that does")
        called = [b for b in PUBLIC_BINDINGS if re.search(rf"\b{b}\s*\(", code)]
        assert not called, (
            f"{name} has started calling {called} while telling the reader no "
            "account is needed. That is the real defect, not a false positive "
            "— check whether a stranger can reach this screen before relaxing "
            "anything here.")


def test_the_public_bindings_are_real():
    """A guard on the guard: a renamed binding would make every check above
    search for a string that occurs nowhere and pass."""
    api = (SRC / "api.ts").read_text(encoding="utf-8")
    missing = [b for b in PUBLIC_BINDINGS if f"{b}:" not in api]
    assert not missing, (
        f"these bindings are not in api.ts any more: {missing} — the checks "
        "above are searching for names that no longer exist")


def test_the_public_binding_still_sends_no_credential():
    """The premise underneath all of it.

    `alarmGuidance` is in this file's list because its route is public for the
    person standing over somebody. If it grows a token parameter again, the
    route stops being reachable by that person and the claim on the beacon
    page becomes the thing this file exists to catch.
    """
    api = (SRC / "api.ts").read_text(encoding="utf-8")
    binding = api[api.index("alarmGuidance:"):]
    binding = binding[:binding.index("\n  ", binding.index("req<"))]
    assert "token" not in binding, (
        "alarmGuidance sends a credential again:\n" + binding)
