"""A 422 is a list, and no client could show a person a list.

## The finding

0.30.0 put every refusal this product raises into the reader's language.
0.30.1 caught the one it had missed — `RequestValidationError`, the 422 a
mistyped form produces, which went out past the handler carrying pydantic's
`input` key — and translated its `msg` too.

Nobody looked at what a client does with the result. `detail` on a 422 is a
*list* of rows, and every one of this product's four client families rendered
it by a path written for a string:

* the console called `JSON.stringify` on it, so the note under the form read
  `[{"type":"missing","loc":["body","display_name"],"msg":"Field required"}]`;
* Android's `JSONObject.optString("detail")` coerces a `JSONArray` through
  `toString()`, producing the same thing;
* iOS asked for `as? String`, got `nil`, and fell back to `HTTP 422`;
* Windows called `GetString()` on an array element, which throws, was caught,
  and fell back to `HTTP 422`.

        asked     is the refusal translated
        mattered  is the refusal a sentence

The `msg` translated in 0.30.1 was correct, arrived, and was never read by
anybody: it sat inside a JSON blob, or was discarded for a status code. Two of
the four families showed the person *less* than before their language was
considered at all.

## What this checks

The sentence is composed on the server (`i18n.validation_message`) rather than
in each client, for the reason the refusal handler is one handler: four
renderings of one thing are four chances to render it differently, and three of
these have no test runner in this repository.

So the driven half below holds the server to composing it, translating it, and
— the part that matters most — putting nothing in it that is not already in
the rows. The structural half holds each client to *reading* it, which is all a
source-level check can honestly claim; see
`test_native_shells_record_nothing_private.py` for the same limit stated the
same way.

## What is still not right

The field name in the sentence is the API's name — `terms_consent`, not the
label the form shows. It is joined with an em dash rather than declined into
the sentence, so nothing reads as half-translated, but a person looking at a
field captioned *"Nome de exibição"* is told about `terms_consent`. Mapping the
two needs a per-client table that does not exist. Written down here rather than
guessed at.
"""

from __future__ import annotations

import json
import pathlib
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from jim import i18n
from jim.api import create_app


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()


@pytest.fixture()
def client():
    return TestClient(create_app())


# --- driven: what the server sends ------------------------------------------

def test_a_mistyped_form_answers_with_a_sentence(client):
    """The defect, directly. Before this, `message` did not exist and the only
    human-readable thing in the body was buried in a list."""
    refused = client.post("/enroll", json={"display_name": "A"})
    assert refused.status_code == 422
    said = refused.json().get("message")
    assert isinstance(said, str) and said.strip(), (
        "a 422 carries no `message`, so every client is back to rendering the "
        f"`detail` list: {refused.text[:200]}")
    assert not said.lstrip().startswith(("[", "{")), (
        f"the sentence is still a serialised structure: {said[:120]}")
    assert "terms_consent" in said and "Field required" in said


def test_the_rows_are_still_there(client):
    """`detail` keeps its shape.

    It is the FastAPI contract, a machine reading this API has every right to
    the rows, and the driven tests in this suite read them. A sentence that
    replaced them would fix one client family by breaking every other caller.
    """
    body = client.post("/enroll", json={"display_name": "A"}).json()
    assert isinstance(body["detail"], list) and body["detail"]
    for row in body["detail"]:
        assert set(row) == {"type", "loc", "msg"}, (
            f"a row grew a key: {sorted(row)}")


def test_the_sentence_says_no_more_than_the_rows(client):
    """The whole reason 0.30.1 existed, applied to the thing it added.

    A sentence composed from the rows can only leak by composing from
    something else. Every word of it must be traceable to a `loc` part or a
    `msg`, and the value that failed must not appear — which is exactly what
    went wrong the first time, when pydantic's `input` key handed the entire
    submitted body back.
    """
    secret = "a-medication-name-nobody-should-see"
    refused = client.post("/enroll", json={
        "terms_consent": {"nested": secret}})
    assert refused.status_code == 422
    body = refused.json()
    assert secret not in json.dumps(body), (
        "the submitted value came back — in the sentence, the rows, or both")

    accounted = set()
    for row in body["detail"]:
        accounted.update(str(p) for p in row["loc"])
        accounted.add(row["msg"])
    # ...and the field labels, which are constants in `i18n._FIELD_LABELS`.
    #
    # 0.40.8 gave the sentence a third source: the label the form shows, so a
    # person reads "Nome do perfil" where the API says `display_name`. That is
    # a real weakening of the rule this test enforces, and this test is what
    # caught it — the rule is mechanical on purpose, so that nothing has to
    # reason about whether a given source happens to be safe.
    #
    # Widened by *naming* the new source rather than by relaxing the match:
    # a constant table cannot carry a submitted value, and
    # `test_no_label_is_built_from_anything_but_a_constant` holds it to that.
    # The rule still forbids the thing it was written for — composing the
    # sentence from the body.
    accounted.update(v for row in i18n._FIELD_LABELS.values()
                     for v in row.values())
    for piece in re.split(r" — |; ", body["message"]):
        assert piece in accounted or piece.split(".")[-1] in accounted, (
            f"{piece!r} is in the sentence and in none of the rows, so the "
            "sentence is composed from something other than the rows")


@pytest.mark.parametrize("language", ["pt", "es", "ja"])
def test_the_sentence_arrives_in_the_readers_language(client, language):
    refused = client.post("/enroll", json={"display_name": "A"},
                          headers={"accept-language": language})
    said = refused.json()["message"]
    assert "Field required" not in said, (
        f"the sentence is English for a {language} reader: {said}")
    assert i18n.tr_refusal("Field required", language) in said


def test_an_unlabelled_field_keeps_its_identifier_and_that_is_deliberate(client):
    """Half in one language and half in another is the failure
    `refusals_untranslated.txt` will not record its way out of.

    `terms_consent` is a checkbox a switch owns, not a field anybody types, so
    0.40.8 left it out of `_FIELD_LABELS` and it still arrives as the API's
    name for it — the same string in every language. It is joined with an em dash rather than declined into the
    sentence, so it reads as an identifier rather than as a word somebody
    forgot to translate.
    """
    said = client.post("/enroll", json={"display_name": "A"},
                       headers={"accept-language": "pt"}).json()["message"]
    assert "terms_consent — " in said


def test_a_body_that_is_not_an_object_still_says_something(client):
    """`loc` is `["body"]` alone here — no field to name. The sentence must not
    come out as a bare em dash with nothing on either side of it."""
    refused = client.post("/enroll", content=b"not json",
                          headers={"content-type": "application/json"})
    assert refused.status_code == 422
    said = refused.json()["message"]
    assert said.strip() and not said.strip().startswith("—"), (
        f"a bodiless 422 composed {said!r}")


def test_an_unrecognised_field_name_is_readable_in_the_sentence():
    """`validation_detail` substitutes a placeholder where a caller's own key
    would be echoed. It is the one 'field name' that is prose, so it is the one
    that has to be translated when it lands in the sentence."""
    rows = i18n.validation_detail(
        [{"type": "extra_forbidden", "loc": ["body", "a key with spaces"],
          "msg": "Extra inputs are not permitted"}], "pt")
    said = i18n.validation_message(rows, "pt")
    assert i18n.UNRECOGNISED_FIELD not in said, (
        f"the placeholder stayed English inside a Portuguese sentence: {said}")
    assert "a key with spaces" not in said



# --- structural: what each client does with it ------------------------------
#
# Per client, never unioned, and with a *different question per client*,
# because the four decode a refusal in four genuinely different ways.
#
# The first version of this section asked one question of all four — does the
# source mention `message` — and passed on all four while every one of them was
# still broken: `message` is a field on a model, a parameter name on an
# exception class, and a word in the comments directly above the bug.
#
# The second anchored on the throw and asked whether the surrounding lines read
# `message`. That caught the three shells and still passed on a broken console,
# because this console's fallback chain has always read `body.message` as an
# *alternative to* `detail` — so the words were present in a window where the
# sentence was being dropped on the floor.
#
#     asked     does the decode mention the sentence
#     mattered  does the decode consult the sentence first
#
# So the console is checked on the two things that actually carry it: that it
# extracts the sentence at all, and that the extracted sentence is the first
# operand of the fallback. Either one removed and a 422 renders as a list.

CONSOLE = REPO / "app/src/api.ts"

_READS_DETAIL = re.compile(r'"detail"')
_READS_SENTENCE = re.compile(r'"message"')

#: Lines before and after the throw that count as its decode. Wide enough for
#: the C# `try`/`catch` block, narrow enough that an unrelated key elsewhere in
#: the file cannot drift into range.
_BEFORE, _AFTER = 14, 3


def _windows(path: Path, throws: str) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    return ["\n".join(lines[max(0, i - _BEFORE):i + 1 + _AFTER])
            for i, line in enumerate(lines) if re.search(throws, line)]


CONSOLE_THROW = r'throw new Error\(typeof d === "string"'


def test_the_console_extracts_the_sentence_at_every_refusal_site():
    """A site that computes its message from `detail` alone renders the 422
    row list through `JSON.stringify` — which is what a person read before
    this round."""
    # The *extraction*, not a mention of it. The fallback chain a few lines
    # down has always read `body.message` as an alternative to `detail`, so a
    # window with the extraction deleted still contains those words — which is
    # how the first version of this check passed on broken code.
    extracts = re.compile(r'typeof\s+body\.message\s*===\s*"string"')
    blind = [w for w in _windows(CONSOLE, CONSOLE_THROW)
             if not extracts.search(w)]
    assert not blind, (
        f"{len(blind)} console refusal site(s) never read the sentence beside "
        "the rows:\n\n" + "\n\n---\n\n".join(blind[:2]))


def test_the_console_prefers_the_sentence_over_the_structure():
    """Order matters and is easy to get backwards.

    `detail` is truthy when it is a list, so a chain that consults it first
    never reaches the sentence at all.
    """
    sites = _windows(CONSOLE, CONSOLE_THROW)
    assert sites, "no console refusal site found — the pattern stopped matching"
    for window in sites:
        assert re.search(r"said \?\?", window), (
            "the console composes a sentence and then does not put it first "
            "in the fallback, so a 422 list still wins:\n" + window)


def test_the_console_sites_were_actually_found():
    """A guard on the guard: a rewritten throw makes the pattern match
    nothing, and a check over no windows passes."""
    sites = _windows(CONSOLE, CONSOLE_THROW)
    assert sites, "no console refusal site found"
    assert any("detail" in w for w in sites), (
        "no console refusal site reads `detail` — the extraction is pointed "
        "at the wrong lines")


SHELLS = {
    "ios": (REPO / "native/ios/Sources/ApiClient.swift",
             r"throw ApiError\.http\("),
    "android": (next((p for p in (REPO / "native/android").rglob("ApiClient.kt")), None),
             r"throw ApiException\("),
    "windows": (REPO / "native/windows/ApiClient.cs",
             r"throw new HttpRequestException\("),
}


@pytest.mark.parametrize("shell", sorted(SHELLS))
def test_every_shell_refusal_decode_reads_the_sentence(shell):
    """A decode that reads `"detail"` and never `"message"` shows the reader a
    serialised list or a bare status code.

    Structural, and that is the honest limit: this reads the source, it does
    not run the shell — there is no Swift, Kotlin or C# runner in this
    repository. What it rules out is the state all three were actually in.
    """
    path, throws = SHELLS[shell]
    assert path is not None and path.exists(), f"no client source for {shell}"
    blind = [w for w in _windows(path, throws)
             if _READS_DETAIL.search(w) and not _READS_SENTENCE.search(w)]
    assert not blind, (
        f"{shell} has {len(blind)} refusal site(s) that read `detail` and "
        "never look for the sentence beside it:\n\n"
        + "\n\n---\n\n".join(blind[:2]))


@pytest.mark.parametrize("shell", sorted(SHELLS))
def test_the_shell_windows_were_actually_found(shell):
    """A guard on the guard. A renamed exception type makes the pattern match
    nothing, and a check over no windows passes."""
    path, throws = SHELLS[shell]
    found = _windows(path, throws)
    assert found, (
        f"no refusal-throwing site found in {shell} — the pattern "
        f"{throws!r} has stopped matching")
    assert any(_READS_DETAIL.search(w) for w in found), (
        f"none of {shell}'s {len(found)} refusal site(s) reads `detail`, "
        "which means the extraction is pointed at the wrong lines")


def test_the_client_list_is_the_whole_set():
    """A fifth client added to this product and not to the tables above would
    be audited by nothing, and this file would keep passing."""
    assert CONSOLE.exists()
    shells = {p.name for p in (REPO / "native").iterdir() if p.is_dir()}
    assert shells == set(SHELLS), (
        f"native/ holds {sorted(shells)}; SHELLS above covers {sorted(SHELLS)}")


def test_no_label_is_built_from_anything_but_a_constant():
    """What makes widening the rule above safe.

    `test_the_sentence_says_no_more_than_the_rows` now accepts pieces that came
    from `_FIELD_LABELS`. That is only sound while every value in it is a
    literal — a table that interpolated anything could put a submitted value
    into the sentence through the one door the leak check was just told to
    trust.

        asked     is the sentence composed only from the rows
        mattered  is every source of it incapable of carrying the body
    """
    import ast as _ast
    src = pathlib.Path(i18n.__file__).read_text(encoding="utf-8")
    table = next(
        (n for n in _ast.walk(_ast.parse(src))
         if isinstance(n, _ast.AnnAssign)
         and getattr(n.target, "id", "") == "_FIELD_LABELS"), None)
    assert table is not None, "the label table is no longer a module constant"
    bad = [_ast.dump(v)[:60] for v in _ast.walk(table.value)
           if isinstance(v, (_ast.JoinedStr, _ast.Call, _ast.Name,
                             _ast.Attribute, _ast.BinOp))]
    assert not bad, (
        "the label table is not all literals, so a value could reach the "
        "sentence through it:\n    " + "\n    ".join(bad))
