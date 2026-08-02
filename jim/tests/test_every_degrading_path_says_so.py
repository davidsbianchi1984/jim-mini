"""One wrapper recorded its degrades. Its sibling said nothing, and that made
the careful one look like the whole answer.

## The finding

`llm.FallbackProvider` is exemplary, and its docstring is where this rule is
written down in this codebase:

    The degrade is recorded on the instance (``answered_by``, ``failure``) so a
    caller can tell the user the truth about who actually answered — **a log
    line the user will never read is not disclosure.**

`cloud.CloudProvider` degrades to the same local stub and did none of it. A
bare `except Exception:`, no record, and — unlike its sibling — not even a log
line. And `generate_for_user` asked for the truth like this:

    if isinstance(provider, FallbackProvider):
        actual, reason = provider.answered_by, provider.failure

So when the cloud gateway was unreachable, `actual` stayed at `intended`, the
model the user had chosen, and `degraded` computed to False. The coach's own
comment beside that field says what the consequence is:

    a silent degrade to the stub under a screen that says Claude is how a
    founder demos canned text to their testers without knowing it

    asked     did the fallback provider degrade
    mattered  did anything degrade

Nothing exercised the cloud path through `generate_for_user`, which is
the whole reason a defect this shape could sit beside a correct implementation
of the same idea.

## What changed

`CloudProvider` now carries `answered_by`/`failure` like its sibling, and the
assembly duck-types on those attributes instead of naming one class — so a
third wrapper added later is covered by construction rather than by somebody
remembering to add a branch.

The sibling product had this defect in both of its wrappers and the same fix
landed there; the difference is that this product had already written the rule
down and applied it once.
"""

from __future__ import annotations

import ast
from pathlib import Path

from jim import cloud, llm


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()


class _DeadClient:
    def generate(self, system, user):
        raise RuntimeError("gateway unreachable")


class _Live:
    """The local fallback: a provider, so it answers with a plain string."""

    def __init__(self, text="stub text"):
        self.text = text

    def generate(self, system, user):
        return self.text


class _LiveClient:
    """The gateway: a *client*, so it answers with the envelope
    `CloudProvider` unwraps. Distinct from `_Live` because conflating the two
    is what made the first draft of this file subscript a string."""

    def __init__(self, text="real answer"):
        self.text = text

    def generate(self, system, user):
        return {"content": self.text}


def test_the_cloud_wrapper_records_its_degrade():
    p = cloud.CloudProvider(_DeadClient(), _Live())
    assert p.generate("s", "u") == "stub text"
    assert p.answered_by == "stub", (
        "the gateway failed, the stub answered, and the wrapper still reports "
        "the greater model — which is what provenance then tells the user")
    assert p.failure and "cloud greater model" in p.failure


def test_the_cloud_wrapper_records_a_success_too():
    """Both branches. Recording only the failure leaves a stale degrade
    describing a later answer that was perfectly good."""
    p = cloud.CloudProvider(_DeadClient(), _Live())
    p.generate("s", "u")
    p._client = _LiveClient("real answer")     # the gateway comes back
    assert p.generate("s", "u") == "real answer"
    assert p.answered_by == cloud.CloudProvider.GREATER_MODEL
    assert p.failure is None


def test_provenance_reports_a_cloud_degrade(monkeypatch):
    """The path that had no test at all, driven end to end.

    Before this round `degraded` came back False here and `provider` came back
    as whatever the user had chosen — a false statement about who wrote the
    text, produced by the branch that only knew about the other wrapper.
    """
    # Built outside the lambda: `get_provider`'s own signature names a
    # parameter `cloud`, which shadows the module of the same name inside the
    # replacement and made the first draft call `None.CloudProvider`.
    degrading = cloud.CloudProvider(_DeadClient(), _Live())
    monkeypatch.setattr(llm, "get_provider",
                        lambda cloud=None, choice=None: degrading)
    # The intended provider is pinned to something that is *not* the stub, and
    # that is the whole discriminating power of this test.
    #
    # Without it the first draft passed while the defect was still in place:
    # the suite pins JIM_LLM=stub, so `intended` was already "stub", and the
    # broken branch — which reports `intended` — produced exactly the answer
    # the fixed branch produces. It asserted the right value for the wrong
    # reason, which is the failure this whole file is named after.
    monkeypatch.setattr(llm, "resolve_choice", lambda choice: "anthropic")
    out = llm.generate_for_user("u1", "system", "user")
    assert out["provider"] == "stub", (
        f"provenance says {out['provider']!r} produced this; the local stub did")
    assert out["degraded"] is True, (
        "the gateway was unreachable and the record calls it an undegraded "
        "answer")
    assert out["reason"], "a degrade with no reason tells the user nothing"


# --- the generalisation -----------------------------------------------------

def _degrading_wrappers() -> list[tuple[str, str, ast.ExceptHandler]]:
    """Every `generate` that answers a provider failure with somebody else's
    text, found structurally rather than by name — because naming the classes
    is exactly what the defective branch did."""
    out = []
    for rel in ("jim/llm.py", "jim/cloud.py"):
        tree = ast.parse((REPO / rel).read_text(encoding="utf-8"))
        for cls in ast.walk(tree):
            if not isinstance(cls, ast.ClassDef):
                continue
            for fn in cls.body:
                if not isinstance(fn, ast.FunctionDef) or fn.name != "generate":
                    continue
                for handler in [n for n in ast.walk(fn)
                                if isinstance(n, ast.ExceptHandler)]:
                    if [n for n in ast.walk(handler) if isinstance(n, ast.Call)
                            and getattr(n.func, "attr", "") == "generate"]:
                        out.append((rel, cls.name, handler))
    return out


def _records_who_answered(handler: ast.ExceptHandler) -> bool:
    """An assignment to `self.answered_by` inside the handler. This codebase
    records on the instance; the sibling product uses a context variable, and
    each check is written against the idiom its own product actually uses."""
    for node in ast.walk(handler):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        for t in targets:
            for part in ast.walk(t):
                if (isinstance(part, ast.Attribute)
                        and part.attr == "answered_by"):
                    return True
    return False


def test_every_wrapper_that_swallows_a_failure_records_who_answered():
    silent = [f"{rel}: {name}.generate (line {h.lineno})"
              for rel, name, h in _degrading_wrappers()
              if not _records_who_answered(h)]
    assert not silent, (
        f"{len(silent)} wrapper(s) answer a provider failure with the local "
        "fallback's text and do not record it, so provenance goes on naming "
        "the provider that was asked:\n    " + "\n    ".join(silent))


def test_the_wrapper_scan_is_finding_wrappers():
    """A guard on the guard: a walk that stopped matching would report no
    silent wrappers and pass on an empty set."""
    found = _degrading_wrappers()
    assert len(found) >= 2, (
        f"only {len(found)} degrading wrapper(s) parsed — this codebase has "
        "two, in llm.FallbackProvider and cloud.CloudProvider")


def test_the_assembly_does_not_name_one_wrapper_class():
    """The defect itself, in the line that caused it.

    `generate_for_user` asked `isinstance(provider, FallbackProvider)`,
    so a wrapper that was not that class reported no degrade however loudly it
    had recorded one.
    """
    src = (REPO / "jim/llm.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
              and n.name == "generate_for_user")
    named = [n for n in ast.walk(fn) if isinstance(n, ast.Call)
             and getattr(n.func, "id", "") == "isinstance"
             and any(getattr(a, "id", "") == "FallbackProvider" for a in n.args)]
    assert not named, (
        "generate_for_user is back to isinstance-checking "
        "FallbackProvider by name, so any other degrading wrapper is reported "
        "as an undegraded answer from the model the user chose")
