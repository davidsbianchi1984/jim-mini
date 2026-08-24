"""A recorded field stops being recordable the day a form asks for it.

`jim/tests/field_labels_unmapped.txt` records 99 request-model fields that keep
their identifiers in a 422, and gives a good reason:

    These are the rest: enum members a control sets, ids a client fills in
    from the resource it is already looking at, and flags a switch owns. A 422
    naming one of them is a client bug rather than something a person
    mistyped.

Every word of that is a claim about **the screens**, and nothing in this
repository was reading the screens. The ceiling stops the list growing; it is
silent about a field already on the list that a screen quietly grew an input
for. The record would go on shrinking, every test would stay green, and the
field would sit there being typed into a box by a person and named by an
identifier in the refusal underneath it.

That is not hypothetical. QRME's copy of this record carried `weight` and
`aspect` while its blend screen had been asking for both — under localized
labels, in ten languages — since the screen was localized. And PDI's copy
says in its own header that a 0.46.4 sweep found **forty** rows with a control
on a form and no label beside it. Both were found by somebody looking. This is
the looking, kept.

## How a form asking for something is recognised

Two conditions, and the AND is the whole guard:

* the field is **bound to a form control** — the `value` or the `onChange`
  target of an `<input>`, `<textarea>` or `<select>`;
* the field is **a key in an object literal** in the same screen, which is
  what being sent in a request body looks like from the source.

Either half alone is noise. Screens are full of object literals — inline
styles, component state, table rows — and control bindings alone match local
UI state that never leaves the browser. A field that is both is one a person
fills in and this API then validates, which is exactly the population
`_FIELD_LABELS` exists for.
"""

from __future__ import annotations

import re
from pathlib import Path

from jim import i18n
from jim.tests.test_the_refusal_names_the_field_on_the_form import REPO, _declared
from . import ratchets

SCREENS = REPO / "app/src/screens"


def _controls(src: str) -> str:
    """Every form control's opening tag, run together.

    Taken as tags rather than lines because a control's `value` and its
    `onChange` are routinely three lines apart, and the binding is a property
    of the tag rather than of any one line of it.
    """
    return " ".join(re.findall(r'<(?:input|textarea|select)\b[^>]*>', src, re.S))


def _body_keys(src: str) -> set[str]:
    """Every object-literal key in the file.

    Deliberately not narrowed to the argument of an `api.*` call. A screen
    builds its payload in pieces, and following that would be a parser. The
    narrowing that matters is the AND with :func:`_controls`, not this half.
    """
    return set(re.findall(r'^\s*(\w+):\s', src, re.M))


def _asked_for() -> dict[str, set[str]]:
    """Field → the screens whose forms ask a person for it."""
    out: dict[str, set[str]] = {}
    fields = _declared()
    for path in sorted(SCREENS.rglob("*.tsx")):
        src = path.read_text(encoding="utf-8")
        controls, keys = _controls(src), _body_keys(src)
        for field in fields:
            if field not in keys:
                continue
            bound = re.escape(field)
            if (re.search(rf'value=\{{[^}}]*\b{bound}\b', controls)
                    or re.search(rf'onChange=\{{[^}}]*\b{bound}\b', controls)):
                out.setdefault(field, set()).add(path.name)
    return out


# --- the rule ---------------------------------------------------------------

def test_a_field_a_form_asks_for_has_the_label_the_form_shows():
    """A field here is one a person is typing into a box right now.

    Whatever was true of it when it was recorded — that a control set it, that
    a client filled it in from the row it was looking at — stopped being true
    the day a screen grew an input for it, and the refusal became the one
    place in the product that calls it by a name the person cannot see
    anywhere.
    """
    unlabelled = {f: sorted(where) for f, where in _asked_for().items()
                  if f not in i18n._FIELD_LABELS}
    assert not unlabelled, "\n    ".join(
        [""] + [f"{f} — asked for by {', '.join(w)}, and the refusal that "
                f"names it has no label for it" for f, w in
                sorted(unlabelled.items())]
    ) + ("\n  A recorded field stops being recordable when a form starts "
         "asking for it. Give it the label the form shows.")


# --- the scan has to be able to see, and to fail ----------------------------

def test_the_scan_can_still_see_the_forms():
    """A guard nobody has watched fail is a guard nobody should trust, and a
    scan of an entire console reporting nothing is far likelier to be broken
    than to be good news — which is what a rewrite of either regex produces.
    """
    controls = sum(len(_controls(p.read_text(encoding="utf-8")))
                   for p in SCREENS.rglob("*.tsx"))
    assert controls > 6_000, (
        f"the control extractor matched {controls} character(s) across every "
        f"screen — it has stopped seeing form controls")
    assert len(_asked_for()) >= ratchets.floor("form.asked_for"), (
        f"only {len(_asked_for())} field(s) read as form-bound and sent — the "
        f"AND has stopped matching and this guard is checking nothing")


def test_the_scan_would_catch_the_next_one():
    """Driven against the shape of the ones QRME's copy found, so the check is
    known to fire rather than assumed to."""
    src = '''
      const out = await api.createThing({
        anonymity: draft.anonymity,
      });
      <input value={draft.anonymity}
             onChange={(e) => setDraft({ anonymity: e.target.value })} />
    '''
    assert "anonymity" in _body_keys(src)
    assert re.search(r'value=\{[^}]*\banonymity\b', _controls(src))
    assert "anonymity" not in i18n._FIELD_LABELS, (
        "this example field was labelled since the test was written — pick "
        "another unlabelled one, or the check proves nothing")


# --- driven -----------------------------------------------------------------

def test_a_money_field_a_person_types_is_named_the_way_the_form_names_it():
    """`account_number` — a box on the Settings money form, and the most
    consequential kind of field to hand back as an identifier. Somebody who
    has just typed their bank details into a health guardian and got it wrong
    is owed a refusal that names what they typed."""
    said = i18n.validation_message(
        [{"loc": ["body", "account_number"], "msg": "Field required"}], "de")
    assert "account_number" not in said, said
    assert "Kontonummer" in said, said
