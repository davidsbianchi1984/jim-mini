"""A workflow that fires only on `main` cannot inform the merge into `main`.

0.60.2 found `native.yml` red for a hundred and twenty-three consecutive runs.
Nothing was wrong with what it ran — three real toolchains, three real
compilers, and every error it named turned out to be a real defect. What was
wrong was *when*. Its trigger was:

    on:
      pull_request:
      push:
        branches: [main]

Releases here are fast-forward merges, so no pull request is ever opened; and
a push to `main` is what happens *after* somebody has decided to ship. Both
halves fired only where the answer could no longer change anything.

Then `ci.yml` turned out to carry the identical trigger, and to have been red
for twenty-nine consecutive runs, on four guards that shell out to node — the
JSX-text extractor could not import `typescript`, because the job that runs
pytest never installed the app's `node_modules`. Same shape, one workflow
along: a suite green on a developer's machine and red where it actually runs,
reported into a log nothing read.

    asked     does the workflow pass
    mattered  can the workflow's answer still change the decision

Two products, two workflows, a hundred and fifty-two red runs between them,
and no human or machine step in the loop ever opened one. That is not a
failure of attention that trying harder fixes. It is a wiring fault, and the
wiring is in a file this suite can read.

## What this checks, and what it deliberately does not

A workflow gates a change when it is expected to fail a branch *before* that
branch is merged. For those, a `push:` trigger with no branch filter is the
only shape that fires where the answer matters.

Not every workflow gates. Three here do not, and each says so in its own
header:

  - `e2e.yml` boots three containers and is deliberately post-merge
  - `desktop-release.yml` fires on a release tag, which only exists after

Those are named in `POST_MERGE` below. Naming one is a decision with a
reason, which is the point: the failure this guard exists for was nobody
having made the decision at all.

## Why the assertion is on the trigger and not on the result

A guard that read the *runs* would need the network, a token, and a live
GitHub. This reads the checked-in trigger, which is the thing that was wrong
and the thing a change can get wrong again. It cannot tell whether a workflow
is passing; it can tell whether a failure would arrive in time to matter.

Confirmed by injection: restoring `branches: [main]` under `push` in
`ci.yml` fails `test_a_gating_workflow_fires_before_the_merge` naming that
file, and removing the `push:` key entirely fails it with the other message.
"""

from __future__ import annotations

import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parent.parent.parent
WORKFLOWS = REPO / ".github" / "workflows"

# Workflows that are meant to run after the decision, each for a reason
# written into its own header. Membership here is the deliberate exception —
# the thing whose absence let a hundred and fifty-two red runs go unread.
POST_MERGE = {
    "desktop-release.yml",      # fires on a release tag, which post-dates the cut
    "release-integrity.yml",    # reads the body a tag published, so likewise
    "release-bodies-sweep.yml", # sweeps published bodies on a schedule
}


def _files() -> list[pathlib.Path]:
    return sorted(p for p in WORKFLOWS.glob("*.yml"))


def _on_block(text: str) -> str:
    """The `on:` mapping, as written.

    Read by indentation rather than with a YAML parser: the point of this
    guard is the file as a person edits it, and a parser would also accept
    `on` spelled as the YAML boolean `true`, which is a real footgun and one
    this reader would rather show than normalise away.
    """
    lines = text.split("\n")
    start = next((i for i, l in enumerate(lines)
                  if re.match(r"^on:\s*$", l) or re.match(r"^on:\s+\S", l)), None)
    if start is None:
        return ""
    out = [lines[start]]
    for l in lines[start + 1:]:
        if l and not l[0].isspace():
            break
        out.append(l)
    return "\n".join(out)


def _push_branches(on: str) -> list[str] | None:
    """The branch filter under `push:`, or None when there is no filter.

    Returns `[]` when there is no `push:` key at all, which is a different
    answer from "fires on every branch" and is reported differently.
    """
    m = re.search(r"^\s{2}push:\s*$", on, re.M)
    if not m:
        if re.search(r"^\s{2}push:\s+\S", on, re.M):
            return None
        return []
    tail = on[m.end():]
    stop = re.search(r"^\s{2}\S", tail, re.M)
    body = tail[: stop.start()] if stop else tail
    b = re.search(r"branches:\s*\[([^\]]*)\]", body)
    if not b:
        b = re.search(r"branches:\s*\n((?:\s+-\s*\S+\n?)+)", body)
        if not b:
            return None
        return [x.strip("- \t") for x in b.group(1).strip().split("\n")]
    return [x.strip().strip("'\"") for x in b.group(1).split(",") if x.strip()]


def test_the_reader_finds_the_workflows_at_all():
    """A sweep that reads nothing agrees with everything — and this whole
    guard exists because something that reported nothing was believed."""
    files = _files()
    assert len(files) >= 3, [p.name for p in files]
    for p in files:
        assert _on_block(p.read_text(encoding="utf-8")), (
            f"{p.name}: no `on:` block found — the reader has stopped matching")


def test_a_gating_workflow_fires_before_the_merge():
    """The whole finding, as one assertion."""
    blind = []
    for p in _files():
        if p.name in POST_MERGE:
            continue
        branches = _push_branches(_on_block(p.read_text(encoding="utf-8")))
        if branches == []:
            blind.append(f"{p.name}: no `push:` trigger — this can only fire "
                         f"on a pull request, and releases here are "
                         f"fast-forward merges that open none")
        elif branches:
            blind.append(f"{p.name}: `push` restricted to {branches} — a "
                         f"branch is merged into {branches[0]} before this "
                         f"ever runs, so its answer arrives too late to be "
                         f"one")
    assert not blind, (
        "these workflows cannot fail a branch before it is merged:\n    "
        + "\n    ".join(blind)
        + "\n  Drop the branch filter, or name the file in POST_MERGE with a "
          "reason in its own header.")


def test_every_named_exception_still_exists():
    """A `POST_MERGE` entry for a deleted workflow is a hole with a name on
    it: the next file to take that name inherits the exemption."""
    names = {p.name for p in _files()}
    stale = sorted(POST_MERGE - names)
    assert not stale, (
        f"POST_MERGE names workflows that are gone: {stale} — strike them, or "
        f"the exemption outlives the decision that granted it")


def test_the_python_suite_runs_where_it_is_checked():
    """The other half of 0.60.2's second finding.

    Two guards in this suite shell out to `node app/scripts/jsx-text.mjs`,
    which imports `typescript` from the app's own `node_modules`. The job that
    runs pytest has to install them, or those guards fail on the runner and
    pass everywhere else — which is what they did, for twenty-nine runs.
    """
    ci = (WORKFLOWS / "ci.yml").read_text(encoding="utf-8")
    # The invocation, not the mention: this file names the script in its own
    # prose, and a reader that counted prose would count itself.
    invokes = re.compile(r'"node"\s*,\s*"scripts/jsx-text\.mjs"')
    shells_out = [p.name for p in sorted((REPO / "jim" / "tests").glob("test_*.py"))
                  if invokes.search(p.read_text(encoding="utf-8"))]
    if not shells_out:
        return
    test_job = ci[ci.index("  test:"):]
    stop = re.search(r"^  \w+:", test_job[len("  test:"):], re.M)
    if stop:
        test_job = test_job[: stop.start() + len("  test:")]
    assert "setup-node" in test_job and "npm ci" in test_job, (
        f"{len(shells_out)} guard(s) shell out to the JSX-text extractor "
        f"({', '.join(shells_out)}), and the job that runs them installs no "
        f"node dependencies — the extractor cannot import `typescript` and "
        f"every one of them fails on the runner while passing locally")
