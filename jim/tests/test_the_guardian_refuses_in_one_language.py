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


#: Every shape an `HTTPException` detail is written in, and what this suite
#: does about each. A shape that is in none of these is the defect the
#: classifier exists to report — see `_classify`.
#:
#:   literal      a plain string. Checked against the translation table.
#:   named        a module-level constant holding a plain string. Resolved,
#:                then checked exactly like a literal.
#:   template     an f-string, a `.format()`, or a concatenation. The English
#:                skeleton is recovered and checked against its own record —
#:                it cannot be a table key as written, which is the finding.
#:   translated   already goes through `i18n` at the raise: `i18n.fill(...)`
#:                or a lookup into one of the translation tables. Nothing owed.
#:   passthrough  carries a sentence raised somewhere else — `exc.detail`, a
#:                local rebound from an earlier raise. Owed at that raise.
#:   domain       `str(exc)` on a domain exception. The sentence lives at the
#:                `raise SomeError("…")` in a module, not here. **Not yet
#:                followed** — see `refusal_templates.txt` for the count and
#:                why it is its own round.
SHAPES = ("literal", "named", "template", "translated", "passthrough", "domain")

#: What must be translated or written down. The other three shapes are
#: accounted for elsewhere, and saying which is the point of the split.
OWED = ("literal", "named", "template")


def _module_strings(tree: ast.Module) -> dict[str, str]:
    """Module-level `NAME = "a sentence"`, so a refusal raised as a constant
    can be read. Two of them were invisible for as long as this guard has
    existed: QRME's `common.RESTRICTED_WHILE_CONTESTED` was one."""
    out: dict[str, str] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if isinstance(target, ast.Name) and isinstance(node.value, ast.Constant) \
                and isinstance(node.value.value, str):
            out[target.id] = node.value.value
    return out


def _module_tables(tree: ast.Module) -> dict[str, list[str]]:
    """Module-level `NAME = {...}` whose values are plain strings.

    A refusal picked out of one of these — `_MISSING[posture].format(label=…)`
    in `jim's routers` — is every one of its values, because which sentence
    a reader meets depends on a key chosen at runtime. Recovering only the
    subscript would find nothing; recovering the table finds all of them.
    """
    out: dict[str, list[str]] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name) or not isinstance(node.value, ast.Dict):
            continue
        values = [v.value for v in node.value.values
                  if isinstance(v, ast.Constant) and isinstance(v.value, str)]
        if values and len(values) == len(node.value.values):
            out[target.id] = values
    return out


def _skeleton(node: ast.AST) -> str | None:
    """The English of a sentence built by interpolation, with `{}` where each
    filled-in piece goes.

    This is what makes an f-string refusal visible. It is deliberately not a
    translation key: `i18n.fill` uses *named* placeholders, and an f-string
    does not carry names a reader could rely on. The skeleton says what a
    person will actually read, which is the thing the record is about.
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        return "".join(
            v.value if isinstance(v, ast.Constant) and isinstance(v.value, str)
            else "{}" for v in node.values)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left, right = _skeleton(node.left), _skeleton(node.right)
        return None if left is None or right is None else left + right
    return None


def _is_i18n(node: ast.AST) -> bool:
    """Whether this detail already went through the translation layer.

    `i18n.fill(i18n.MUST_BE_ONE_OF, field=…)` and
    `i18n.STUDIO_REFUSALS[str(exc)]` are the two shapes in use. Both are
    refusals-as-keys, which is the pattern the rest of this suite asks for,
    so they are owed nothing here — but they must be *recognised* rather
    than unseen, or the guard cannot tell them from an English f-string.
    """
    for sub in ast.walk(node):
        if isinstance(sub, ast.Attribute) \
                and getattr(sub.value, "id", "") == "i18n":
            return True
    return False


def _classify(detail: ast.AST | None, consts: dict[str, str],
              tables: dict[str, list[str]]) -> tuple[str, list[str]]:
    """One detail node, into exactly one of :data:`SHAPES`.

    The old extractor read `ast.Constant` and counted `ast.JoinedStr`. Every
    other shape fell through in silence — 145 refusals, including two module
    constants and thirty-eight f-strings that reach a reader in English
    whatever language they chose.

        asked     is this refusal a string literal
        mattered  what does this refusal put in front of a person
    """
    def table_of(node: ast.AST) -> list[str] | None:
        """The sentences behind `SOME_TABLE[whatever]`."""
        if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name):
            return tables.get(node.value.id)
        return None

    if detail is None:
        return "passthrough", []
    if _is_i18n(detail):
        return "translated", []
    if isinstance(detail, ast.Constant) and isinstance(detail.value, str):
        return "literal", [detail.value]
    if isinstance(detail, ast.Name):
        if detail.id in consts:
            return "named", [consts[detail.id]]
        return "passthrough", []            # a local, rebound from a raise
    if isinstance(detail, ast.Attribute):
        return "passthrough", []            # exc.detail, exc.message
    if isinstance(detail, (ast.JoinedStr, ast.BinOp)):
        skeleton = _skeleton(detail)
        return ("template", [skeleton]) if skeleton else ("passthrough", [])
    if isinstance(detail, ast.Call):
        fn = detail.func
        # `str(exc)` — the sentence is at the `raise` in a domain module.
        if getattr(fn, "id", "") == "str":
            return "domain", []
        # `SOMETHING.format(...)` — the receiver carries the English, whether
        # that is a literal or a row of a table picked at runtime.
        if getattr(fn, "attr", "") == "format":
            receiver = getattr(fn, "value", None)
            skeleton = _skeleton(receiver)
            if skeleton:
                return "template", [skeleton]
            rows = table_of(receiver)
            if rows:
                return "template", rows
            return "domain", []
        return "domain", []
    if isinstance(detail, ast.Dict):
        # The plan gate. `localize_detail` translates `message` and leaves the
        # API's own vocabulary alone — `test_a_dict_detail_…` covers it.
        for key, value in zip(detail.keys, detail.values):
            if getattr(key, "value", None) == "message":
                text = _skeleton(value)
                if text:
                    return "literal", [text]
        return "translated", []
    if isinstance(detail, ast.Subscript):
        rows = table_of(detail)
        if rows:
            return "named", rows
        return "domain", []
    return "unknown", []


def _refusals(root: Path) -> dict[str, list[tuple[str, str | None]]]:
    """Every `HTTPException` detail in the package, by shape.

    Values are `(where, text)` so a failure can name the file and line rather
    than only the sentence — a template appears verbatim at several call
    sites and the sentence alone does not say which one is new.
    """
    found: dict[str, list[tuple[str, str | None]]] = {s: [] for s in SHAPES}
    found["unknown"] = []
    for path in sorted(root.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        consts, tables = _module_strings(tree), _module_tables(tree)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            fn = node.func
            name = getattr(fn, "id", "") or getattr(fn, "attr", "")
            if name != "HTTPException":
                continue
            detail = node.args[1] if len(node.args) >= 2 else None
            for kw in node.keywords:
                if kw.arg == "detail":
                    detail = kw.value
            shape, texts = _classify(detail, consts, tables)
            where = f"{path.relative_to(root.parent)}:{node.lineno}"
            if texts:
                found[shape].extend((where, t) for t in texts)
            else:
                found[shape].append((where, None))
    return found


def _stringified_errors(root: Path) -> set[str]:
    """Domain exception classes whose message becomes a refusal.

    Derived rather than listed. A handler that does
    `except displays.DisplayError as exc: raise HTTPException(409, str(exc))`
    is turning that class's message into the sentence a person reads, and the
    next module to invent one is covered without anybody remembering to add
    it here.
    """
    out: set[str] = set()
    for path in sorted(root.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for handler in [n for n in ast.walk(tree)
                        if isinstance(n, ast.ExceptHandler)]:
            stringifies = any(
                isinstance(call, ast.Call)
                and (getattr(call.func, "id", "")
                     or getattr(call.func, "attr", "")) == "HTTPException"
                and any(isinstance(arg, ast.Call)
                        and getattr(arg.func, "id", "") == "str"
                        for arg in list(call.args)
                        + [kw.value for kw in call.keywords])
                for call in ast.walk(handler))
            if not stringifies or handler.type is None:
                continue
            caught = (handler.type.elts if isinstance(handler.type, ast.Tuple)
                      else [handler.type])
            for node in caught:
                name = getattr(node, "attr", "") or getattr(node, "id", "")
                if name:
                    out.add(name)
    return out


def _domain_sentences(root: Path) -> tuple[set[str], set[str]]:
    """The English behind `str(exc)`, as (literals, templates).

    `raise DisplayError("a display needs a name")` is the sentence; the route
    that catches it only forwards. The refusal guard walked `HTTPException`
    call sites and stopped there, so a hundred and five forwarding sites hid
    two hundred and sixty-nine sentences nobody was ever asked about.

        asked     what does this route pass to HTTPException
        mattered  where does the sentence it passes come from

    They land in the same two records as any other refusal, because
    `tr_refusal` treats them identically at answer time: it looks the
    sentence up and falls through to English when it is not there.
    """
    classes = _stringified_errors(root)
    literals: set[str] = set()
    templates: set[str] = set()
    for path in sorted(root.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        consts, tables = _module_strings(tree), _module_tables(tree)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Raise) or not isinstance(node.exc, ast.Call):
                continue
            name = (getattr(node.exc.func, "id", "")
                    or getattr(node.exc.func, "attr", ""))
            if name not in classes or not node.exc.args:
                continue
            arg = node.exc.args[0]
            if isinstance(arg, ast.Name) and arg.id in consts:
                literals.add(consts[arg.id])
                continue
            if isinstance(arg, ast.Subscript) \
                    and getattr(arg.value, "id", "") in tables:
                templates.update(tables[arg.value.id])
                continue
            text = _skeleton(arg)
            if text is None:
                continue
            (templates if isinstance(arg, (ast.JoinedStr, ast.BinOp))
             else literals).add(text)
    return literals, templates


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


def _tabled() -> set[str]:
    """Refusal sentences that live in a table rather than at the raise site.

    `jim/engaged.py` raises `EngagedError("engaged.not_engaged")` — a *key* —
    and the handler looks the sentence up in `engaged.REFUSALS` before
    `i18n.refuse` sends it. The AST walk above sees the key, which is not a
    sentence and must never be translated, so sixteen real sentences would
    have gone out in English while this file reported a comfortable zero.

        asked     is every refusal *raised with a sentence* translated
        mattered  is every refusal *a person reads* translated

    A separate source rather than a branch inside `_details`, because
    `_details` is measured by its own guard against a synthetic module and
    must find exactly the shapes it documents there — and rather than putting
    `EngagedError` in `DOMAIN_ERRORS`, which would have demanded translations
    for the keys.

    **Every** keyed table, not the first one that needed this. `jim/widgets.py`
    arrived with a `REFUSALS` of the same shape, and a function that named
    `engaged` alone would have reported the same comfortable zero over
    thirteen more English sentences — the defect this docstring already
    describes, repeating because the fix was written for one module instead
    of for the pattern.

        asked     is engaged.REFUSALS translated
        mattered  is every table of this shape translated
    """
    from jim import engaged, widgets
    return {sentence
            for table in (engaged.REFUSALS, widgets.REFUSALS)
            for _status, sentence in table.values()}


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
    # The sentences behind `str(exc)` too. They reach `tr_refusal` exactly as
    # a directly-raised literal does, and fall through to English the same way.
    literals |= _domain_sentences(PKG)[0]
    literals |= _tabled()
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


TEMPLATES = Path(__file__).resolve().parent / "refusal_templates.txt"


def _recorded_templates() -> set[str]:
    return {line.rstrip("\n") for line in
            TEMPLATES.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")}


def _refusal_floor() -> int:
    """The registered floor, so the number lives in `ratchets.py` where
    something audits it against what it measures every run."""
    from .ratchets import RATCHETS
    return next(r.floor for r in RATCHETS if r.name == "refusals.literal")


def test_no_refusal_shape_goes_unclassified():
    """The finding this round is about, as a standing check.

    The extractor read `ast.Constant` and counted `ast.JoinedStr`. Everything
    else — a module constant, a row of a table picked at runtime, a
    `.format()`, a concatenation — fell through in silence, and a refusal
    added in one of those shapes was a sentence nobody would ever be asked
    about.

        asked     is this refusal a string literal
        mattered  what does this refusal put in front of a person

    Every detail now lands in one of :data:`SHAPES`. A shape that lands in
    none of them fails here rather than being skipped, because a shape nobody
    classified is a shape nobody decided about.
    """
    found = _refusals(PKG)
    assert not found["unknown"], (
        f"{len(found['unknown'])} refusal detail(s) in a shape this guard "
        "does not classify:\n    "
        + "\n    ".join(where for where, _ in found["unknown"][:20])
        + "\n  Give the shape a row in SHAPES and a branch in _classify — "
          "or the sentences it carries are invisible.")
    # And the classifier must still be finding the bulk of them: a refactor
    # that broke `_refusals` would report zero unknown on zero refusals.
    assert len(found["literal"]) >= _refusal_floor(), (
        f"only {len(found['literal'])} literal refusals found — the walk has "
        "stopped matching, so every check built on it is passing on nothing")


def test_every_interpolated_refusal_is_recorded():
    """The templates, both directions.

    These cannot be keys in `_REFUSALS` as written — `i18n.fill` is the
    mechanism for a refusal with a value in it, and twenty-two call sites use
    it correctly. The ones here were written as f-strings instead, which
    means English whatever language the reader chose. Recorded rather than
    translated in the round that found them; `refusal_templates.txt` says why.
    """
    found = _refusals(PKG)
    measured = {text for _, text in found["template"] if text}
    measured |= _domain_sentences(PKG)[1]
    recorded = _recorded_templates()
    problems = []
    new = sorted(measured - recorded)
    if new:
        problems.append(
            f"{len(new)} interpolated refusal(s) not in {TEMPLATES.name}:\n    "
            + "\n    ".join(s[:90] for s in new[:20])
            + "\n  Convert it to i18n.fill with a translated constant, or "
              "record it — but recording is ratcheted.")
    gone = sorted(recorded - measured)
    if gone:
        problems.append(
            f"{len(gone)} recorded template(s) are no longer raised — strike "
            f"them from {TEMPLATES.name}:\n    "
            + "\n    ".join(s[:90] for s in gone[:20]))
    assert not problems, "\n\n".join(problems)


def test_the_template_backlog_only_shrinks():
    ceiling = int(re.search(r"# ceiling: (\d+)",
                            TEMPLATES.read_text(encoding="utf-8")).group(1))
    assert len(_recorded_templates()) <= ceiling, (
        f"{len(_recorded_templates())} interpolated refusals, above the "
        f"{ceiling} this record started at")


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


def test_every_failure_answers_in_the_readers_language():
    """The path the handler guard above could not see.

    `@app.exception_handler(Exception)` cannot be the catch-all here:
    Starlette hands it to `ServerErrorMiddleware`, outside the CORS layer, so
    the 500 goes back without the header and the console reads it as
    unreachable. The catch-all is therefore a middleware — and being a
    middleware, it was not a handler, so nothing above was asking it
    anything. Its sentence sat inline in English for three releases.

        asked     does every exception handler answer in the reader's language
        mattered  does every failure answer in the reader's language

    The one answer every route in this product can give is the one a person
    meets when the product is already failing them, and it was the only one
    that came back in a language they might not read.
    """
    tree = ast.parse((PKG / "api.py").read_text(encoding="utf-8"))
    caught = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not any(isinstance(d, ast.Call)
                   and getattr(d.func, "attr", "") == "middleware"
                   for d in node.decorator_list):
            continue
        # The catch-all specifically, not any middleware that happens to
        # handle an error: the JSON-localizing middleware catches
        # `(ValueError, TypeError)` around one `json.loads` and is not
        # answering a failed route. A bare `except:` counts, because that is
        # a catch-all written the other way.
        if not any(isinstance(n, ast.ExceptHandler)
                   and (n.type is None
                        or getattr(n.type, "id", "") == "Exception")
                   for n in ast.walk(node)):
            continue
        asked = any(
            isinstance(n, ast.Call)
            and getattr(n.func, "attr", "") in ("refusal_language", "refuse")
            and getattr(getattr(n.func, "value", None), "id", "") == "i18n"
            for n in ast.walk(node))
        caught.append((node.name, asked))

    assert caught, (
        "no middleware in api.py catches an exception — either the catch-all "
        "is gone, in which case a failing route answers with nothing the "
        "console can read, or this guard has stopped matching")
    astray = sorted(name for name, asked in caught if not asked)
    assert not astray, (
        f"{astray} answer a failed route without asking what language the "
        "reader is in. A person who is already being failed reads the "
        "apology in English.")


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


def test_no_refusal_is_translated_into_english():
    """The check the one above cannot make.

    `test_every_translated_refusal_has_every_language` asks whether each row
    has all nine keys. A row whose nine values are the English sentence pasted
    nine times satisfies it exactly, and the table would then claim the refusal
    is handled while every reader gets English — the failure this whole file
    exists to catch, wearing the shape of the fix.

        asked     does every refusal have every language
        mattered  does every language say something other than the English

    Byte equality is the whole test. It cannot tell a good translation from a
    bad one and does not try; it can tell a translation from no translation,
    which is the difference that was going unchecked while 142 rows were added
    to this table by hand in one release.
    """
    untouched = [(k, c) for k, v in i18n._REFUSALS.items()
                 for c, t in v.items() if t == k]
    assert not untouched, (
        f"{len(untouched)} language value(s) are the English sentence "
        "verbatim, so the table claims a refusal is translated and serves "
        "English:\n    "
        + "\n    ".join(f"[{c}] {k[:70]}" for k, c in untouched[:20]))


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
