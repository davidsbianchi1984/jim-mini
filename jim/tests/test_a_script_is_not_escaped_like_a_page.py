"""A script is not escaped like a page.

`_js_literal` builds the JSON and JavaScript string literals this product's
landing pages drop inside a `<script>` element — including the translated
string table. It called `html.escape`, which is the right tool for a page and
the wrong one for a script: **a browser does not decode HTML entities inside a
script element**, so escaping there protects nothing and corrupts the value.

    asked     is the value escaped
    mattered  is it escaped for the place it lands

`Terms & Conditions` reached the reader as `Terms &amp; Conditions`, in every
language that ships.

The page was safe, but by accident rather than by its own mechanism. Its
docstring named the real hazard correctly — a literal `</script` ends the
element whatever the JavaScript quoting says — and the line written to stop
it, `.replace("</", "<\\/")`, sat *after* an `html.escape` that had already
turned `<` into `&lt;`. It never matched anything and never could.

These hold both halves: the value survives intact, and nothing that reaches
the page can close the script element.
"""

import json

import pytest

from jim.landing import _js_literal


ROUND_TRIP = [
    "Terms & Conditions",
    "a < b",
    "1 > 0 && true",
    "O'Brien",
    'she said "hello"',
    "naïve café — Ω",
    "back\\slash",
    "</script><img src=x onerror=alert(1)>",
    "line break",
    "para break",
]


@pytest.mark.parametrize("value", ROUND_TRIP)
def test_the_value_survives_the_journey(value):
    """What the reader sees is what was given. A JS string literal is also a
    JSON string, so parsing it back is the question the browser asks."""
    assert json.loads(_js_literal(value)) == value


@pytest.mark.parametrize("value", ROUND_TRIP)
def test_nothing_in_it_can_be_read_as_markup(value):
    """No character an HTML parser treats as a tag reaches the page."""
    for char in "<>&":
        assert char not in _js_literal(value), f"{char!r} reached the page raw"


def test_a_whole_table_survives_it_too():
    """`_js_literal` takes any JSON value, and what it is mostly given is the
    translated string table — which is where `&` lives in ordinary prose."""
    table = {"terms": "Terms & Conditions", "cmp": "a < b",
             "quote": 'she said "hi"', "accent": "café"}
    assert json.loads(_js_literal(table)) == table
    for char in "<>&":
        assert char not in _js_literal(table)


@pytest.mark.parametrize("value", ROUND_TRIP)
def test_no_javascript_line_terminator_survives(value):
    """U+2028 and U+2029 end a string literal in JavaScript, and
    `ensure_ascii=False` leaves them raw — a value carrying one produced a
    page that did not parse."""
    out = _js_literal(value)
    assert " " not in out and " " not in out
