"""A value inside a script is not markup, and neither escaper knows both.

0.59.3 shipped a Content-Security-Policy with a nonce and called it the second
line of defence; 0.59.4 made the first line — escaping into HTML — a guard.
This is the third sink, and it is the one where **both of those miss**.

Inside a `<script>` element the HTML parser ends the element at the first
`</script`, whatever the JavaScript quoting says. So a value containing
`</script>` closes the script early and everything after it is parsed as
markup — in the page's own nonced script, which the policy exists to permit.
Neither `json.dumps` nor `html.escape` handles that alone:

    json.dumps    escapes what would end a JS *string*      — not the element
    html.escape   escapes what would open an HTML *tag*     — not a JS string

The composition is the whole helper, and getting it wrong is silent:
`json.dumps("</script>")` looks perfectly escaped.

    asked     is the value a valid JavaScript string
    mattered  can the value end the script element

## What the sweep found

QRME's `_js` composed both. JIM-mini's and PDI's were bare `json.dumps` — a
helper written once and copied into three repositories, where the copy that
drifted is the one whose entire job is to be safe. The same shape 0.59.0 found
in a floor and 0.59.1 in a guard, in a security primitive.

Not currently reachable: every value passing through `_js` in those two
products is a database identifier or a translated constant, and a path segment
cannot carry `</script>` because the slash breaks routing before the page is
built. A latent hole, fixed anyway — the next value somebody escapes with it
is exactly the one it was written for.

## And the consoles, which turned out clean

The same question in TypeScript is `dangerouslySetInnerHTML`, `innerHTML =`,
`document.write`, `eval` and `new Function`. All three consoles have **none of
them**, which is worth keeping rather than rediscovering, so the check below
is a floor rather than a backlog. The linkifier on the community wall was read
too: it splits on `https?://` and gates on `startsWith("http")`, so a
`javascript:` scheme cannot reach an `href`.
"""

from __future__ import annotations

import ast
import inspect
import re
from pathlib import Path

import pytest

from . import ratchets
from jim import landing

#: Payloads a value might carry into an inline script. The first is the one
#: that matters; the rest are here so a "fix" that only special-cases that
#: string fails too.
BREAKOUTS = (
    "</script><script>alert(document.domain)</script>",
    "</SCRIPT ><img src=x onerror=alert(1)>",
    "</script\n>",
    "a\"b\\c\u2028d",
)

#: Sinks that hand a string to the DOM or the parser in the console.
CONSOLE_SINKS = (
    ("dangerouslySetInnerHTML", "React's explicit escape hatch"),
    ("innerHTML", "assigns markup straight into the document"),
    ("outerHTML", "assigns markup straight into the document"),
    ("insertAdjacentHTML", "assigns markup straight into the document"),
    ("document.write", "writes into the parser mid-stream"),
    ("eval(", "runs a string as code"),
    ("new Function(", "runs a string as code"),
)

CONSOLE = (Path(__file__).resolve().parent.parent.parent
           / "app" / "src")


def console_files() -> list[Path]:
    return sorted(p for p in CONSOLE.rglob("*")
                  if p.suffix in (".ts", ".tsx") and "node_modules" not in p.parts)


@pytest.mark.parametrize("payload", BREAKOUTS, ids=lambda p: p[:22])
def test_the_escaper_survives_a_script_breakout(payload):
    """The defect, directly: a value that ends the script element."""
    escaped = landing._js(payload)
    assert "</" not in escaped, (
        f"_js left {escaped[:60]!r} — the HTML parser ends a script element at "
        "`</script` whatever the JavaScript says, so this value closes the "
        "page's own nonced script and everything after it is markup. "
        "json.dumps alone does not do this.")


def test_the_escaper_still_produces_a_javascript_string():
    """The other half. An escaper that mangles the value into something the
    script cannot read is safe and useless — and a page whose script throws
    is a screen that quietly stops working."""
    import json
    for payload in BREAKOUTS + ("plain", "", "ünïcode", "a'b"):
        escaped = landing._js(payload)
        assert escaped.startswith('"') and escaped.endswith('"'), escaped
        # `html.escape` leaves &lt;; the browser un-escapes nothing inside a
        # script, so what the JS sees is the entity text. That is the price of
        # not being able to end the element, and it is the right trade for a
        # value that is a path or an identifier.
        assert json.loads(escaped.replace("&lt;", "<").replace("&gt;", ">")
                          .replace("&amp;", "&").replace("<\\/", "</")) == payload


def test_neither_escaper_is_enough_on_its_own():
    """Why the helper is a composition, stated as a test so nobody simplifies
    it back. Both halves look correct in isolation."""
    import html
    import json
    breakout = BREAKOUTS[0]
    assert "</script" in json.dumps(breakout), (
        "json.dumps has stopped being the unsafe half — check this test still "
        "means what it says")
    only_html = html.escape(breakout, quote=False)
    assert not only_html.startswith('"'), (
        "html.escape alone yields no JavaScript string literal")


def test_every_value_entering_a_script_goes_through_the_escaper():
    """The call sites, not just the helper.

    A correct escaper nobody calls is the same as no escaper. Each inline
    script is a `%`-formatted template; every value substituted into one has
    to arrive escaped.
    """
    source = Path(landing.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    raw = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod)):
            continue
        left = node.left
        name = left.id if isinstance(left, ast.Name) else ""
        if not name.endswith("_JS"):
            continue
        if not isinstance(node.right, ast.Dict):
            continue
        for key, value in zip(node.right.keys, node.right.values):
            src = ast.unparse(value)
            # Each of these is verified by behaviour below, not trusted by
            # name: the first draft allowed `_strings(` while one product's
            # `_strings` was a bare `json.dumps`.
            if src.startswith(("_js(", "_js_literal(", "_strings(")):
                continue
            raw.append(f"{name}[{ast.unparse(key)}] = {src[:50]}")
    assert not raw, (
        "value(s) substituted into an inline script without passing through "
        "_js:\n    " + "\n    ".join(raw)
        + "\n  A string that reaches JavaScript unescaped can end the script "
          "element, and the page's policy permits that script by name.")


@pytest.mark.parametrize("sink,why", CONSOLE_SINKS, ids=lambda v: v.split("(")[0])
def test_no_console_screen_hands_a_string_to_the_parser(sink, why):
    """A floor rather than a backlog: all three consoles have none of these
    today, and the cheapest time to keep it that way is now."""
    found = [f"{p.relative_to(CONSOLE)}:{i}"
             for p in console_files()
             for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1)
             if sink in line and not line.lstrip().startswith("//")]
    assert not found, (
        f"{sink} — {why} — appears in the console:\n    "
        + "\n    ".join(found[:20])
        + "\n  Every screen here renders through React, which escapes what it "
          "interpolates. Reaching past that is a decision worth making on "
          "purpose.")


def test_the_console_sweep_is_reading_the_console():
    """A sweep over an empty directory reports no sinks and a clean bill —
    the shape this session has found in four readers now."""
    seen = len(console_files())
    assert seen >= ratchets.floor("console.source_files"), (
        f"only {seen} console source files found under {CONSOLE} — the sweep "
        "is looking in the wrong place, and every check above passed on "
        "nothing")

def test_the_string_table_is_escaped_the_same_way():
    """The loophole this file nearly shipped with.

    The call-site check above allows `_strings(...)` by name. When it was
    written, PDI's `_strings` was a bare `json.dumps` — so the guard would
    have excused, by name, precisely the defect it exists to catch. A
    whitelist is a claim about behaviour and has to be checked as one.
    """
    table = getattr(landing, "_strings", None)
    if table is None:
        pytest.skip("this product's inline script takes no string table")
    out = table("en", probe=BREAKOUTS[0])
    assert "</" not in out, (
        "the script's string table is not escaped for the element — a "
        "translation containing `</script>` would end the page's own script")


def test_both_helpers_are_built_on_one_primitive():
    """Two helpers escaping for a script is two chances to drift, and they
    had already taken one each. `_js_literal` is the single place that knows
    what ends a script element."""
    for name in ("_js", "_strings"):
        helper = getattr(landing, name, None)
        if helper is None:
            continue
        source = inspect.getsource(helper)
        assert "_js_literal" in source, (
            f"{name} escapes on its own rather than through _js_literal — "
            "which is how the two came to disagree in the first place")
    assert "</" not in landing._js_literal(
        {"a": BREAKOUTS[0], "b": [BREAKOUTS[1]]}), (
        "the primitive itself lets a nested value end the element")
