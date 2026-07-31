"""An installer that reports nothing, and nothing said so.

`errors.ts` sends the launch-time report to an address **compiled into the
bundle** — `__PROBLEM_COLLECTOR__`, defined by `vite.config.ts` from
`process.env.PROBLEM_COLLECTOR`. A build with no address has nowhere to send
and no runtime path that could acquire one, which is a stronger *off by
default* than a flag because it cannot be flipped by a mistake in a later
release.

That is the design, and it is a good one. The defect was one layer further
out: **`desktop-release.yml` never passed the variable to the build.** Three
build steps — macOS signed, Windows signed, unsigned — each carefully
threading its signing certificate through `env:`, and not one of them
mentioning the collector. So every installer this workflow has ever produced
had an empty address, whatever secrets were configured, and error reporting
was inert in every shipped desktop build.

Nothing failed. The define existed. The documentation said to rebuild with the
variable set. The step that does the building dropped it on the floor, and the
only way to notice was to install a build and watch nothing arrive.

`errors.ts` even anticipates the *neighbouring* mistake — it refuses to invent
a product name because "a repo whose vite.config.ts forgot the define would
otherwise file its reports under whichever product this fallback named". The
define was not forgotten. The environment that feeds it was.

So this file checks the whole chain rather than any one link: the source reads
the define, the bundler supplies it from the environment, and **every** step
that runs the packaging command passes it in. The last one is the assertion
that would have caught this, and it is written to cover steps that do not
exist yet — a fourth build step added for a fourth platform fails here until
it is wired.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()
WORKFLOW = REPO / ".github/workflows/desktop-release.yml"

#: The two the bundle cannot be built without. `PROBLEM_TOKEN` is included
#: because a collector that refuses an unauthenticated report is the same
#: silence as no collector at all.
NEEDED = ("PROBLEM_COLLECTOR", "PROBLEM_TOKEN")


def _steps() -> list[dict]:
    spec = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    return [s for job in spec["jobs"].values() for s in job.get("steps", [])]


def _build_steps() -> list[dict]:
    """Every step that actually runs the packaging command.

    Selected by what the step *does*, not by what it is called. Matching on
    the name would let a step called anything else slip past, and the name is
    the part most likely to change.
    """
    return [s for s in _steps() if "npm run dist" in str(s.get("run", ""))]


# --- the chain, one link at a time ------------------------------------------

def test_the_source_reads_a_compiled_in_address():
    src = (REPO / "app/src/errors.ts").read_text(encoding="utf-8")
    assert "__PROBLEM_COLLECTOR__" in src
    assert "__PROBLEM_TOKEN__" in src


def test_the_bundler_supplies_it_from_the_environment():
    cfg = (REPO / "app/vite.config.ts").read_text(encoding="utf-8")
    for name in NEEDED:
        assert f"process.env.{name}" in cfg, (
            f"vite.config.ts does not read {name}, so the define is a "
            "constant and no build could ever set it")


def test_there_are_build_steps_to_check():
    """A guard on the guard. If the packaging command were renamed, the two
    assertions below would pass over an empty list and this file would go
    quietly vacuous — which is the failure it exists to prevent, one level up.
    """
    steps = _build_steps()
    assert len(steps) >= 3, (
        f"only {len(steps)} step(s) run the packaging command — either the "
        "workflow changed shape or this test stopped finding it")


@pytest.mark.parametrize("name", NEEDED)
def test_every_build_step_passes_it_through(name):
    """The assertion that would have caught it.

    Not "some step" — *every* step. The workflow branches three ways on
    signing, and a build is produced by exactly one of them per platform, so
    a variable threaded through two of the three still ships one silent
    platform.
    """
    missing = [s.get("name", "<unnamed>") for s in _build_steps()
               if name not in (s.get("env") or {})]
    assert not missing, (
        f"{name} is not passed to: {', '.join(missing)}.\n"
        "  Those builds compile an empty address into the bundle, so the "
        "installer they produce reports nothing and says nothing about it.")


def test_the_secret_is_read_from_secrets_not_hardcoded():
    """A token pasted into the workflow is a token in the git history."""
    text = WORKFLOW.read_text(encoding="utf-8")
    for name in NEEDED:
        for line in re.findall(rf"^\s*{name}:.*$", text, re.M):
            assert "secrets." in line, (
                f"{name} is set to a literal in the workflow: {line.strip()}")


# --- what an unset secret does ----------------------------------------------

def test_an_unset_secret_still_builds():
    """`off by default` has to survive the wiring.

    Passing an unset secret yields an empty string, which is exactly the state
    the source already treats as *no collector*. So a fork with no secrets
    configured keeps building installers that report nothing — the intended
    behaviour — rather than failing the release.
    """
    src = (REPO / "app/src/errors.ts").read_text(encoding="utf-8")
    assert '!== "undefined" ? __PROBLEM_COLLECTOR__ : ""' in src, (
        "the source no longer falls back to an empty address, so an unset "
        "secret may now break the build rather than disable reporting")


def test_the_docs_tell_you_which_variables_to_set():
    """The instruction and the pipeline agree now. They did not before: the
    docs named the variables, and nothing downstream consumed them."""
    cfg = (REPO / "app/vite.config.ts").read_text(encoding="utf-8")
    assert "PROBLEM_COLLECTOR=" in cfg, (
        "the worked example naming the variables is gone from vite.config.ts")
