"""QRME's agent-lights lesson, applied on arrival rather than re-learned.

The sibling widget shipped with "keep the last face; a blip must not
blank it" — and a failed *first* fetch had no last face to keep, so the
widget vanished silently, and a field report said so. The Guardian's
lights arrive with the fix built in; this file pins it the way QRME's
guard does, including the reachability check that guard only gained
after an injected early `return null` sailed past a presence check.

    asked     does the widget survive a fetch error
    mattered  does it survive the FIRST fetch error
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
WIDGET = (REPO / "app/src/GuardianLights.tsx").read_text(encoding="utf-8")
L10N = (REPO / "app/src/l10n.ts").read_text(encoding="utf-8")

LANGS = ("en", "es", "fr", "de", "pt", "it", "ja", "zh", "hi", "ar")


def test_the_widget_is_mounted_in_the_shell():
    app = (REPO / "app/src/App.tsx").read_text(encoding="utf-8")
    assert "<GuardianLights />" in app, (
        "the Guardian lights are no longer part of the shell")


def test_a_failed_first_fetch_leaves_a_dot_not_a_blank():
    m = re.search(r"if \(!glance\) \{(.*?)\n  \}", WIDGET, re.S)
    assert m, "GuardianLights no longer has a no-glance branch to check"
    branch = m.group(1)
    assert "wl-dot-off" in branch, (
        "the no-glance branch renders nothing — a first fetch that fails "
        "removes the widget from every screen, silently")
    nulls = re.findall(r"^\s*(.*return null.*)$", branch, re.M)
    assert len(nulls) == 1 and "!unreachable" in nulls[0], (
        "the no-glance branch returns null on a path other than the "
        "guarded one — the unlit dot is written but unreachable:\n    "
        + "\n    ".join(nulls))


def test_the_failure_is_tracked_not_swallowed():
    assert "setUnreachable(true)" in WIDGET


def test_the_dot_retries_when_pressed():
    m = re.search(r"if \(!glance\) \{(.*?)\n  \}", WIDGET, re.S)
    assert m and re.search(r"onClick=\{load\}", m.group(1))


def test_every_word_it_shows_is_on_the_table():
    for key in ("lights.title", "lights.alarms", "lights.vigil",
                "lights.crash", "lights.quiet", "lights.asking",
                "lights.alarm", "lights.show", "lights.hide",
                "lights.unreachable"):
        block = re.search(rf'"{re.escape(key)}":\s*\{{(.*?)\n  \}}', L10N, re.S)
        assert block, f"{key} is not on the console's table"
        for lang in LANGS:
            assert re.search(rf"\b{lang}:", block.group(1)), (
                f"{key} has no {lang} translation")


def test_a_glance_opens_no_new_door():
    """The widget reads through bindings other screens already call —
    alarms, the vigil, the crash watch — so the route audit is untouched
    and there is nothing new for the shells to owe a door for."""
    for binding in ("api.alarms(", "api.getVigil(", "api.crashWatch("):
        assert binding in WIDGET
    assert not re.search(r"req[<(]", WIDGET), (
        "the widget calls the transport directly — that is a new door")
