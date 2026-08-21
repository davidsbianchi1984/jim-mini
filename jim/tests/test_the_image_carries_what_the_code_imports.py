"""The image carries what the code imports.

Field report, as a 502 on the beta box: the jim container crash-looped on
``import httpx`` in `jim/engaged.py`. httpx sat only in the dev extra —
every test run had it because the test client depends on it, and every
earlier image had it because some other dependency dragged it along, until
a rebuild resolved versions where nothing did. The suite was green, the
deploy was down.

    asked     does the code import it
    mattered  does the image the code ships in install it

So the rule becomes a test: every third-party module imported at module
scope anywhere in `jim/` must be a declared main dependency. Module scope
is the class that kills boot — a lazy import inside a function (torch,
peft, transformers in the finetune module) degrades a feature and says
so, which is a different and acceptable failure.
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

#: Import name -> the distribution that provides it, where they differ.
#: Extend this map when a new dependency's import name is not its dist
#: name — the test fails loudly rather than guessing.
_DIST_OF = {
    "zoneinfo": None,  # stdlib on 3.9+; listed for older greps' sake
}


def _declared() -> set[str]:
    text = (REPO / "pyproject.toml").read_text(encoding="utf-8")
    block = re.search(r"^dependencies = \[(.*?)^\]", text, re.S | re.M)
    assert block, "pyproject.toml has no dependencies block"
    return {re.match(r"[A-Za-z0-9_.-]+", d).group(0).lower().replace("-", "_")
            for d in re.findall(r'"([^"]+)"', block.group(1))}


def _module_scope_imports() -> dict[str, set[str]]:
    """Third-party top-level imports per file, stdlib and local dropped."""
    out: dict[str, set[str]] = {}
    for path in sorted((REPO / "jim").glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        names: set[str] = set()
        for node in tree.body:  # module scope only — the boot-killing class
            if isinstance(node, ast.Import):
                names |= {alias.name.split(".")[0] for alias in node.names}
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                if node.module:
                    names.add(node.module.split(".")[0])
        names -= set(sys.stdlib_module_names)
        names -= {"jim"}
        if names:
            out[path.name] = names
    return out


def test_every_module_scope_import_is_a_declared_dependency():
    declared = _declared()
    strangers = []
    for fname, names in _module_scope_imports().items():
        for name in sorted(names):
            dist = _DIST_OF.get(name, name)
            if dist is None:
                continue
            if dist.lower().replace("-", "_") not in declared:
                strangers.append(f"{fname}: import {name}")
    assert not strangers, (
        "module-scope import(s) the image does not install — the suite "
        "passes and the container crash-loops, which is how httpx was "
        "field-reported:\n    " + "\n    ".join(strangers)
        + "\n  Declare it in pyproject [project] dependencies (or move "
        "the import inside the function that needs it, if the feature "
        "honestly degrades without it).")


def test_the_dev_extra_holds_no_runtime_import():
    """The other half of the httpx defect: a module the server imports
    must never *also* be declared only-dev, because that is the exact
    arrangement that made every test green while the box crash-looped."""
    text = (REPO / "pyproject.toml").read_text(encoding="utf-8")
    dev = re.search(r'dev = \[(.*?)\]', text, re.S)
    assert dev, "pyproject.toml has no dev extra"
    dev_names = {re.match(r"[A-Za-z0-9_.-]+", d).group(0).lower()
                 .replace("-", "_")
                 for d in re.findall(r'"([^"]+)"', dev.group(1))}
    runtime = set().union(*_module_scope_imports().values())
    runtime = {n.lower().replace("-", "_") for n in runtime}
    declared = _declared()
    both = sorted(dev_names & runtime - declared)
    assert not both, (
        f"runtime import(s) living only in the dev extra: {both}")
