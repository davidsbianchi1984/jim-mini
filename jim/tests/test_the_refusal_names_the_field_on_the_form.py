"""The refusal was a sentence, in the reader's language, naming a field they
could not see.

## The finding

An earlier round took the 422 from `[{"type":"missing",...}]` to one sentence a
person can read, in their own language. It stopped one step short, and said so
in its own docstring:

    Mapping those names to the labels a form actually shows — *"Nome de
    exibição"* rather than `display_name` — is a per-client table this does not
    have, and is recorded as the remaining gap rather than guessed at.

So a person mistyping the sign-up form was told:

    display_name — Field required

while the form beside it said **Profile name**, and had said it in ten
languages since the console was localized.

    asked     is the refusal a sentence in the reader's language
    mattered  does it name the field the reader can see

## Where the table lives, and why

Server-side, beside the sentence, for the reason the sentence is composed there
at all: nine clients rendering it is nine chances to render it differently, and
six of those are in languages with no test runner in this repository.

Wording is ported from the console's own labels where one exists —
`onb.profile.name`, `onb.persona`, `onb.email`, `onb.password` — so the
sentence and the form agree by construction rather than by somebody keeping
them in step.

There is no mechanical mapping for the rest. The console's rows are keyed by
screen, not by field, and a name-match across them returns `title` → *"A
profile depicts me"*, which is a heading on the objection pane. Guessing is
what the docstring above declined to do, and this table does not.

## The fallback is the identifier, on purpose

A field with no row keeps its API name. That is not a placeholder for a better
answer: an identifier a reader can match to the form in front of them beats a
word invented for them, and it is the same reasoning
`refusals_untranslated.txt` uses to keep `QRME_ADMIN_TOKEN` in English.
"""

from __future__ import annotations

import ast
import re
import pathlib
from pathlib import Path

import pytest

from jim import i18n
from . import ratchets


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()
RECORD = Path(__file__).resolve().parent / "field_labels_unmapped.txt"


def _declared() -> set[str]:
    """Every request-model field this product declares.

    Read from `models.py` **and** `routers/*.py`. The first draft read
    `models.py` alone and reported 168 fields; the account models — `email`,
    `password`, the whole sign-up form, which is the most person-facing surface
    there is — live in `routers/accounts.py` and were not among them.

        asked     is every field in the models file mapped or recorded
        mattered  is every field a person can be shown

    ## What counts as a field

    Request models only, and that is a correction rather than a narrowing.
    The first version took every annotated class attribute in the package,
    which is a different set: a frozen dataclass in a domain module — the
    privilege roster's rows, the monitor roster's rows — declares `holds`,
    `placing`, `catches_others` the same way, and none of those is a field
    anybody types into. Labelling them would fill the table with words no
    form ever shows, which is the opposite of what this guard is for.

    A request model is a `BaseModel`, directly or through another one of
    this product's models, and that is what is followed here.
    """
    base = REPO / "jim"
    files = sorted(base.glob("*.py")) + sorted((base / "routers").glob("*.py"))
    trees = [ast.parse(f.read_text(encoding="utf-8")) for f in files]

    # Which classes are request models, following inheritance through the
    # product's own models — `EnrollChild(Enroll)` is a form too.
    models: set[str] = set()
    classes: list[ast.ClassDef] = [node for tree in trees
                                   for node in ast.walk(tree)
                                   if isinstance(node, ast.ClassDef)]
    changed = True
    while changed:
        changed = False
        for node in classes:
            if node.name in models:
                continue
            bases = {b.id for b in node.bases if isinstance(b, ast.Name)}
            bases |= {b.attr for b in node.bases if isinstance(b, ast.Attribute)}
            if "BaseModel" in bases or bases & models:
                models.add(node.name)
                changed = True

    out: set[str] = set()
    for node in classes:
        if node.name not in models:
            continue
        for st in node.body:
            if isinstance(st, ast.AnnAssign) and isinstance(st.target, ast.Name):
                out.add(st.target.id)
    return out


def _recorded() -> set[str]:
    return {line.strip() for line in
            RECORD.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")}


def test_the_field_scan_is_finding_fields():
    """A guard on the guard: a walk that stopped matching would report every
    field mapped by finding none of them."""
    found = _declared()
    assert len(found) >= ratchets.floor("form.declared_fields"), (
        f"only {len(found)} request-model field(s) parsed — this product "
        "declares more than two hundred, and the checks below would pass on "
        "almost nothing")


def test_every_field_is_labelled_or_recorded():
    """A field that is neither is one a person can meet as an identifier with
    nobody having decided that was the right answer."""
    loose = sorted(_declared() - set(i18n._FIELD_LABELS) - _recorded())
    assert not loose, (
        f"{len(loose)} field(s) have no label and are not recorded:\n    "
        + "\n    ".join(loose)
        + "\n  Give it the label the form shows, or record it — but recording "
          "is ratcheted.")


def test_no_label_names_a_field_this_product_does_not_have():
    """A label for a field nothing declares is a label nothing will ever show.

    This is not hypothetical: the table's first draft carried `grantee_name`,
    which is the sibling vault product's bequest field, copied across while
    working in both repositories in one sitting. It would have sat here
    translated into ten languages, correct, and unreachable.
    """
    orphans = sorted(set(i18n._FIELD_LABELS) - _declared())
    assert not orphans, (
        "these labels name fields no request model declares:\n    "
        + "\n    ".join(orphans))


def test_no_recorded_field_is_also_labelled():
    """The record is what is *not* done. A field in both lists means one of
    them is lying, and the ratchet is counting work that is finished."""
    both = sorted(_recorded() & set(i18n._FIELD_LABELS))
    assert not both, (
        "these fields are labelled and also recorded as unlabelled:\n    "
        + "\n    ".join(both))


def test_the_record_only_shrinks():
    ceiling = int(re.search(r"^# ceiling: (\d+)$",
                            RECORD.read_text(encoding="utf-8"), re.M).group(1))
    assert len(_recorded()) <= ceiling, (
        f"{len(_recorded())} unlabelled fields, above the {ceiling} recorded")


@pytest.mark.parametrize("field", sorted(i18n._FIELD_LABELS))
def test_every_label_is_in_every_language(field):
    """Ten languages, or the row answers seven readers in English while
    claiming to be the label they can see."""
    row = i18n._FIELD_LABELS[field]
    missing = [c for c in i18n.SUPPORTED if c not in row]
    assert not missing, f"{field} is missing {', '.join(missing)}"


# --- driven -----------------------------------------------------------------

def test_the_sentence_names_the_label_not_the_identifier():
    """The defect, driven. Before this round: `display_name — Field required`."""
    said = i18n.validation_message(
        [{"loc": ["body", "display_name"], "msg": "Field required"}], "pt")
    assert "display_name" not in said, said
    assert "Nome do perfil" in said, said


def test_an_unlabelled_field_keeps_its_identifier():
    """The fallback, which is a decision rather than a gap."""
    said = i18n.validation_message(
        [{"loc": ["body", "aging_enabled"], "msg": "Field required"}], "pt")
    assert "aging_enabled" in said, said


def test_the_label_follows_the_reader_not_the_deployment():
    langs = {c: i18n.field_label("display_name", c) for c in ("en", "ja", "ar")}
    assert len(set(langs.values())) == 3, langs


def test_a_language_the_product_does_not_speak_falls_back_to_english():
    assert i18n.field_label("display_name", "sv") == "Profile name"


def test_the_where_marker_is_still_dropped():
    """`body` is not a field and never was. The label lookup runs after the
    marker is stripped, so a table row named `body` could never be reached —
    and a check that only asserted the label appears would not have noticed."""
    said = i18n.validation_message(
        [{"loc": ["body", "persona"], "msg": "Field required"}], "en")
    assert not said.startswith("body"), said


def test_the_shared_vocabulary_matches_the_sibling_products():
    """One wording across three products.

    These rows were ported from QRME's table rather than written again. Three
    wordings of "Profile name" is three things to keep right, and the drift
    shows up first in the language nobody here reads — which is the same
    reasoning that put the accountless screen's strings on one table.
    """
    # The three products are separate repositories and are not always checked
    # out together, so this skips rather than fails when QRME is absent — but
    # it has to actually *find* it when it is there. The first draft looked
    # only at `REPO.parent`, and these repos sit under different roots, so it
    # skipped every run: a check that never runs is not a check.
    sibling = next(
        (p for p in (REPO.parent / "QRME" / "qrme" / "i18n.py",
                     pathlib.Path("/home/user/QRME/qrme/i18n.py"),
                     REPO.parent / "qrme" / "qrme" / "i18n.py")
         if p.exists()), None)
    if sibling is None:
        pytest.skip("QRME is not checked out beside this product")
    text = sibling.read_text(encoding="utf-8")
    drifted = []
    for field, row in sorted(i18n._FIELD_LABELS.items()):
        m = re.search(rf"^    {re.escape(repr(field))}: \{{(.*)\}},$", text, re.M)
        if not m:
            continue                      # this product's own field
        theirs = dict(re.findall(r"'(\w+)': '((?:[^'\\]|\\.)*)'", m.group(1)))
        for lang, ours in row.items():
            if lang in theirs and theirs[lang] != ours:
                drifted.append(f"{field}[{lang}]: {ours!r} here, {theirs[lang]!r} there")
    assert not drifted, (
        "the shared field vocabulary has drifted between products:\n    "
        + "\n    ".join(drifted))
