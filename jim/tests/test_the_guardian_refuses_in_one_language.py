"""Safety text is never machine-mangled. It was never translated either.

## The finding

`jim/i18n.py` opens with "Per-user language: everything the Guardian drafts or
delivers, localized", and its second bullet is emphatic about the part that
matters:

    **Deterministic safety content** (the CPR/AED playbooks, pace cues, waiver
    terms) is *hand-translated here* for every supported language ... Safety
    text is never machine-mangled.

The playbooks are translated. The pace cues are. The waiver terms are. The
sentences the Guardian says when it says **no** were English — all sixty-four
of them, including every refusal the medication cabinet, the vigil, the crash
watch and the watch bridge can produce.

    asked     is the safety content the Guardian drafts translated
    mattered  is the safety content it refuses with

Somebody setting up a fall alarm for their mother, in Portuguese, on a
Portuguese phone, was told in English what was wrong with it.

## Why one handler would not have been enough

QRME has a single `HTTPException` handler and that covers its whole surface.
The same round in this repository would have been wrong: `create_app` has
**eight more** exception handlers, one per health domain — storage, watch,
crash watch, calm, fitness, nutrition, vigil, medication — each building its
own `JSONResponse`. Porting the single handler across would have localized the
framework's refusals and left every domain's own untouched, and in this
product those are exactly the wrong eight to miss.

    asked     are the refusals localized
    mattered  are all of them

`test_every_handler_returns_through_the_one_place` below is the structural
half. It is the check that would have caught this, and the one that catches
the ninth domain somebody adds.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

from jim import i18n

#: The health-domain error classes. Their messages are refusals a person
#: reads, and are counted alongside `HTTPException` details for that reason —
#: the class a sentence is raised through says nothing about who reads it.
DOMAIN_ERRORS = ("StorageError", "WatchError", "CrashWatchError", "CalmError",
                 "FitnessError", "NutritionError", "VigilError", "MedError")


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()
PKG = REPO / "jim"
SNAPSHOT = Path(__file__).resolve().parent / "refusals_untranslated.txt"


def _details(root: Path) -> tuple[set[str], int]:
    """Every literal refusal sentence in the package, and how many are built
    by interpolation instead.

    From Python's own parser. A regex over the source is how the language
    audit in this suite's sibling repository missed real text three separate
    times, and refusals are worse than most: they wrap across source lines by
    construction, because they are long sentences inside an indented `raise`.
    """
    literals: set[str] = set()
    interpolated = 0
    for path in sorted(root.rglob("*.py")):
        if "tests" in path.parts:
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if not isinstance(node, ast.Call):
                continue
            name = getattr(node.func, "id", "") or getattr(node.func, "attr", "")
            if name == "HTTPException":
                detail = node.args[1] if len(node.args) >= 2 else None
                for kw in node.keywords:
                    if kw.arg == "detail":
                        detail = kw.value
                candidates = [detail]
            elif name in DOMAIN_ERRORS:
                candidates = list(node.args) + [k.value for k in node.keywords]
            else:
                continue
            for arg in candidates:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    literals.add(arg.value)
                elif isinstance(arg, ast.JoinedStr):
                    interpolated += 1
    return literals, interpolated


def _translated() -> set[str]:
    """Both tables. A sentence already hand-translated as safety content is
    not owed a second entry — see `tr_refusal`, and the argument there about
    two tables free to drift."""
    return set(i18n._REFUSALS) | set(i18n._STRINGS)


def _recorded() -> set[str]:
    return {line.rstrip("\n") for line in
            SNAPSHOT.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")}


def test_every_refusal_is_translated_or_written_down():
    """Both directions. A refusal that is neither is a sentence somebody will
    read in a language they did not choose, that nobody decided about."""
    literals, _ = _details(PKG)
    undecided = sorted(literals - _translated() - _recorded())
    stale = sorted(_recorded() - literals)
    problems = []
    if undecided:
        problems.append(
            f"{len(undecided)} refusal(s) that are neither translated nor "
            "recorded:\n    " + "\n    ".join(s[:90] for s in undecided[:30])
            + "\n  Add it to i18n._REFUSALS, or to "
              f"{SNAPSHOT.name} — but adding there is ratcheted.")
    if stale:
        problems.append(
            f"{len(stale)} recorded refusal(s) are no longer raised anywhere "
            f"— strike them from {SNAPSHOT.name}:\n    "
            + "\n    ".join(s[:90] for s in stale[:30]))
    assert not problems, "\n\n".join(problems)


def test_the_backlog_only_shrinks():
    ceiling = int(re.search(r"# ceiling: (\d+)",
                            SNAPSHOT.read_text(encoding="utf-8")).group(1))
    assert len(_recorded()) <= ceiling, (
        f"{len(_recorded())} untranslated refusals, above the {ceiling} this "
        "guard started at")


def test_every_handler_returns_through_the_one_place():
    """The structural half, and the only part of this file that is a fix.

    Every `@app.exception_handler` in `jim/api.py` must return through
    `i18n.refuse`. Eight of the nine were built one per health domain with
    their own `JSONResponse`, which is how a language round could localize
    everything a person reads *except* the medication cabinet and the vigil,
    and pass.

    Checked structurally rather than by driving each one: a driven check would
    cover the eight that exist today and say nothing about the ninth.
    """
    tree = ast.parse((PKG / "api.py").read_text(encoding="utf-8"))
    handlers: list[tuple[str, bool]] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        decorated = any(
            isinstance(d, ast.Call)
            and getattr(d.func, "attr", "") == "exception_handler"
            for d in node.decorator_list)
        if not decorated:
            continue
        routed = any(
            isinstance(n, ast.Call)
            and getattr(n.func, "attr", "") == "refuse"
            and getattr(n.func.value, "id", "") == "i18n"
            for n in ast.walk(node))
        handlers.append((node.name, routed))

    assert len(handlers) >= 9, (
        f"only {len(handlers)} exception handlers found in api.py — the "
        "pattern has stopped matching, so this check would pass on nothing")
    astray = sorted(name for name, routed in handlers if not routed)
    assert not astray, (
        f"{astray} build their own response instead of returning through "
        "i18n.refuse. Every sentence they carry is a refusal somebody reads, "
        "and it will be in English no matter what language they chose.")


def test_the_extractor_can_still_see(tmp_path):
    """A guard on the guard, against a fixture whose answer is known.

    Everything above trusts an AST walk. If it stops recognising a call shape,
    `_details` returns a small set, the backlog looks solved, and the record
    fills with strings nobody raises — which the staleness half would report
    as *progress*.
    """
    (tmp_path / "shapes.py").write_text(
        'from fastapi import HTTPException\n'
        'def a(): raise HTTPException(404, "positional")\n'
        'def b(): raise HTTPException(403, detail="by keyword")\n'
        'def c(): raise HTTPException(422, "wrapped across "\n'
        '                                  "two source lines")\n'
        'def d(x): raise HTTPException(400, f"built from {x}")\n'
        'def e(): raise MedError("a domain refusal")\n'
        'def f(): raise watch.WatchError(404, "a dotted domain refusal")\n',
        encoding="utf-8")
    literals, interpolated = _details(tmp_path)
    assert literals == {"positional", "by keyword",
                        "wrapped across two source lines", "a domain refusal",
                        "a dotted domain refusal"}, (
        f"the extractor no longer reads the shapes it documents:\n{literals}")
    assert interpolated == 1


def test_every_translated_refusal_has_every_language():
    """No partial rows. A row missing four languages serves English to four
    readers while the table says the sentence is handled."""
    langs = [c for c in i18n.SUPPORTED if c != i18n.DEFAULT]
    gaps = {k: [c for c in langs if c not in v]
            for k, v in i18n._REFUSALS.items()}
    gaps = {k: v for k, v in gaps.items() if v}
    assert not gaps, (
        "these refusals are missing languages:\n    "
        + "\n    ".join(f"{k[:60]}: {', '.join(v)}"
                        for k, v in sorted(gaps.items())))
    assert len(i18n._REFUSALS) >= 21


def test_the_health_domains_are_the_ones_that_got_translated():
    """The choice this round made, asserted rather than described.

    Twenty-two sentences were translated and forty-two were not, and which
    forty-two is the whole decision. If a later round translates alphabetically
    or by frequency, the cabinet and the vigil can slide back down the list
    while the count improves.
    """
    for sentence in (
            "no such medication",
            "an as-needed medication has no slots",
            "a vigil needs a steward's name and a way to reach them",
            "the crash watch needs a trusted person's name and a way to "
            "reach them",
            "the upload was empty"):
        assert sentence in i18n._REFUSALS, (
            f"{sentence!r} is a health-domain refusal and is no longer "
            "translated. These are the sentences somebody reads while a "
            "safety feature is failing them.")


# --- driven, not read ------------------------------------------------------

def _a_user(client, language: str, mode: str = "pre"):
    made = client.post("/enroll", json={
        "display_name": "Refused", "birthdate": "1950-03-01",
        "terms_consent": True, "resting_heart_rate": 62})
    assert made.status_code == 201, made.text
    body = made.json()
    head = {"authorization": f"Bearer {body['user_token']}"}
    set_language = client.put(f"/language/{body['id']}",
                              json={"language": language, "mode": mode},
                              headers=head)
    assert set_language.status_code == 200, set_language.text
    return body["id"], head


def test_a_domain_refusal_reaches_its_reader_in_their_language(client):
    """The defect, driven through the medication cabinet.

    `MedError` never passed through the `HTTPException` handler, which is the
    whole reason this needed nine changes and not one. The browser header says
    `en-US` throughout, because that is what a console user's browser actually
    sends whatever they chose in the app.
    """
    user_id, head = _a_user(client, "es")
    refused = client.post(
        f"/meds/{user_id}",
        json={"name": "", "dose": "", "schedule": {"times": ["08:00"]}},
        headers={**head, "accept-language": "en-US,en;q=0.9"})
    assert refused.status_code >= 400, refused.text
    detail = refused.json().get("detail")
    assert detail not in (None, ""), refused.text
    assert detail == i18n.tr_refusal(
        "a medication has a name and a dose — your words are fine "
        "('the little white one, 10 mg')", "es"), (
        f"the medication cabinet refused in {detail!r}. The user set Spanish; "
        "the browser said en-US, which is why the header cannot decide this.")


def test_on_demand_mode_is_not_a_statement_about_what_the_user_reads(client):
    """`effective_language` returns English whenever the mode is `on_demand`.

    That mode means "keep the original medical wording, I will translate what
    I choose" — a decision about *drafted* text. Reading it here would serve
    English refusals to a user who had set Spanish, and would have passed
    every test written with a default-mode user.
    """
    user_id, head = _a_user(client, "es", mode="on_demand")
    assert i18n.effective_language(user_id) == "en"
    assert i18n.get_language(user_id) == "es"

    refused = client.post(
        f"/meds/{user_id}",
        json={"name": "", "dose": "", "schedule": {"times": ["08:00"]}},
        headers={**head, "accept-language": "en-US,en;q=0.9"})
    assert refused.status_code >= 400, refused.text
    assert refused.json()["detail"] == i18n.tr_refusal(
        "a medication has a name and a dose — your words are fine "
        "('the little white one, 10 mg')", "es"), (
        "a user in on_demand mode was refused in English. That mode is about "
        "how drafted text arrives; it says nothing about what they read when "
        "something is refused.")


def test_a_stranger_gets_their_own_language_and_not_the_watched_persons(client):
    """The wrong fix, checked directly.

    Resolving from a user id in the path would answer a passer-by on a care
    beacon in the language of the person on the ground. `negotiate` already
    documents that the beacon page belongs to whoever is holding the phone;
    refusals on the way to it are no different.
    """
    user_id, _ = _a_user(client, "ja")
    refused = client.get(f"/meds/{user_id}",
                         headers={"accept-language": "fr-FR,fr;q=0.9"})
    assert refused.status_code == 401, refused.text
    assert refused.json()["detail"] == (
        i18n._REFUSALS["authentication required"]["fr"]), (
        "a stranger asking about a Japanese-speaking user got the wrong "
        "language. The path names whose data it is, never who is reading.")


def test_the_storage_refusal_keeps_its_vocabulary(client):
    """`_storage_refusal` sends `reason`, `have`, `needs` and `period` beside
    its sentence, and the console branches on them. What a person reads is
    translated; what a client compares is not."""
    out = i18n.localize_detail(
        {"detail": "authentication required", "reason": "storage_posture",
         "needs": "basic", "period": "month"}, "de")
    assert out["detail"] == i18n._REFUSALS["authentication required"]["de"]
    assert out["reason"] == "storage_posture" and out["needs"] == "basic"


def test_an_unknown_sentence_falls_through_as_english():
    """The 42 in the record, and anything added tomorrow. English is a visible
    gap; a guessed translation is a confident error, and a refusal is where
    being confidently wrong costs somebody the most."""
    assert i18n.tr_refusal("a sentence nobody has translated", "es") == (
        "a sentence nobody has translated")


def test_resolving_a_language_never_raises():
    """This runs inside every exception handler. If it can throw, a refusal
    becomes a 500 — telling somebody the server broke when it was really
    telling them no."""
    class _Odd:
        headers = {"authorization": "Bearer nope"}

    class _Worse:
        @property
        def headers(self):
            raise RuntimeError("no headers here")

    assert i18n.refusal_language(_Odd()) == "en"
    assert i18n.refusal_language(_Worse()) == "en"
