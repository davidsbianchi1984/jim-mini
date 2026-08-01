"""A 422 returned what the caller sent, on a product that records nothing.

## The finding

The round before this one put every refusal the product *writes* into the
reader's language, through nine handlers that all return by one door. It missed
every refusal the product *returns*.

    asked     is every refusal this product writes translated
    mattered  is every refusal this product returns

`RequestValidationError` is neither an `HTTPException` nor one of the eight
domain errors. FastAPI raises it before
routing finishes and renders it with its own handler, so a 422 — the refusal a
person meets most often, because it is what a mistyped form produces — went
out in English past a handler written to catch everything.

## The larger half

Pydantic's error rows carry an `input` key holding the value that failed, and
for a missing field that value is the **entire submitted body**. The 422
handed it straight back — a journal entry, for instance:

    {"type": "missing", "loc": ["body", "text"], "msg": "Field required",
     "input": {"entry": "chest pain since Tuesday, have not told my daughter",
               "mood": 3}}

Every other part of this ecosystem's error design refuses to carry content.
`app/src/errors.ts` and the three `Problems` shells record a method, a
redacted path and a status, and have no parameter a message could arrive
through — the signature is the safeguard. `cloudgw` refuses a report whole if
it finds prose in it rather than sanitising it. The one place content left the
process was the framework's default renderer, because nobody had looked at it
as ours.

    asked     does this product record anything private
    mattered  does this product return anything private

## What this is, and what it is not

Not disclosure between people. A 422 goes back to whoever sent the request, so
what came back was the sender's own body — nobody read anybody else's data
because of this, and no stored record was exposed. In PDI it could not even
happen unauthenticated: the tenant dependency refuses before the body is
validated.

What it is: content leaving the process on an error path, in a product whose
whole error design exists so that it does not. A response body travels through
whatever sits between the app and the person — a reverse proxy's access log, a
corporate TLS-inspecting middlebox, a HAR export attached to a support ticket,
a browser extension. Every one of those is a place `errors.ts` was written to
keep content out of, and the framework's default renderer put it back.

Severity aside, the reason to fix it is the same reason the intake refuses a
report that holds prose rather than sanitising it: the posture is that content
does not travel, and a posture with one documented exception is a preference.

## How this is checked

Not by asserting the absence of the `input` key — a check on the name of the
leak rather than on the leak. `test_nothing_a_caller_sent_comes_back` posts a
canary string to **every route in the table that takes a body**, from
`all_routes`, and fails if the canary appears anywhere in the response at all.
A future key under a different name is caught by the same test, without anyone
editing it.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from .clientpaths import all_routes
from jim import i18n

#: A string no route could produce, that reads like something a person would
#: be sorry to see returned. Both halves matter: distinctive enough that a
#: substring search means what it says, and recognisable in a failure message
#: as the thing that should not have come back.
CANARY = "chest-pain-since-tuesday-do-not-echo-this"


def test_the_handler_is_registered(client):
    """The premise. A validation error must not reach FastAPI's own renderer.

    Checked by driving one rather than by reading `create_app`, because a
    handler registered for the wrong exception class would read correctly and
    do nothing.
    """
    refused = client.post("/enroll", json={"display_name": "x"})
    assert refused.status_code == 422, refused.text
    rows = refused.json()["detail"]
    assert isinstance(rows, list) and rows
    assert set(rows[0]) == {"type", "loc", "msg"}, (
        f"a validation row carries {sorted(rows[0])}. FastAPI's own renderer "
        "is answering, or the allowlist has grown a key.")


def _body_routes(app):
    """Every route that reads a request body, with a path that can be filled.

    Path parameters are given a syntactically plausible id. The request is
    expected to fail — that is the point — and it must fail in *validation*,
    which happens before the handler would have looked the id up.
    """
    out = []
    for route in all_routes(app):
        methods = {m for m in (route.methods or ()) if m in
                   ("POST", "PUT", "PATCH")}
        if not methods:
            continue
        path = re.sub(r"\{[^}]+\}", "usr_000000000000", route.path)
        if "{" in path:
            continue
        for method in sorted(methods):
            out.append((method, path))
    return out


def _sweep(client):
    """Post the canary at every body-taking route. Returns what came back.

    One pass, so the two checks below cannot disagree about what was driven.
    """
    leaked, reached = [], 0
    for method, path in _body_routes(client.app):
        response = client.request(
            method, path,
            json={"this-field-does-not-exist": CANARY, "nor_this": [CANARY]},
            headers={"authorization": "Bearer not-a-real-token"})
        if response.status_code == 422:
            reached += 1
        if CANARY in response.text:
            leaked.append(f"{method} {path} → {response.status_code}")
    return leaked, reached


def test_the_sweep_reaches_the_thing_it_is_sweeping(client):
    """A guard on the guard, and the one that matters most here.

    A sweep of two hundred routes that all answer 404 before validation runs
    is a spotless report about nothing — the exact shape this audit is named
    for. So the count of routes that actually reached validation is asserted,
    not just the count of routes attempted.

    The gap between the two is expected and benign: a route with no body model
    ignores an unexpected body and answers from its handler, which for a
    made-up path id is a 404.
    """
    found = _body_routes(client.app)
    assert len(found) > 80, (
        f"only {len(found)} body-taking routes found — `all_routes` or the "
        "method filter has stopped matching")
    _, reached = _sweep(client)
    assert reached > 50, (
        f"only {reached} of {len(found)} routes reached validation. The sweep "
        "below would be reporting a clean product it never asked.")


def test_nothing_a_caller_sent_comes_back(client):
    """The sweep, over every body-taking route this product serves.

    Deliberately not a check for the `input` key. That would test the name of
    the leak rather than the leak, and would pass on the same content arriving
    under `ctx`, or under whatever pydantic adds next. This posts the canary
    and searches the whole response body for it.
    """
    leaked, _ = _sweep(client)
    assert not leaked, (
        f"{len(leaked)} route(s) returned what the caller sent:\n    "
        + "\n    ".join(leaked[:25])
        + "\n  Nothing else in this product's error path carries content — "
          "errors.ts records a redacted path and a status, cloudgw refuses a "
          "report that holds prose. This is the one door it left by.")


def test_the_canary_would_have_been_found_before_the_fix():
    """A guard on the guard, against the defect itself.

    The sweep proves the responses are clean; it cannot prove it would have
    noticed. This runs the sanitiser's input through the shape pydantic
    actually produces, and asserts the raw form does contain the canary while
    the sanitised one does not — so the search above is looking at a place the
    value really used to be.
    """
    raw = [{"type": "missing", "loc": ("body", "text"), "msg": "Field required",
            "input": {"entry": CANARY, "mood": 3},
            "url": "https://errors.pydantic.dev/2/v/missing"}]
    assert CANARY in json.dumps(raw), "the fixture no longer carries the leak"
    cleaned = i18n.validation_detail(raw, "en")
    assert CANARY not in json.dumps(cleaned)
    assert cleaned == [{"type": "missing", "loc": ["body", "text"],
                        "msg": "Field required"}]


def test_a_validators_own_words_are_not_repeated():
    """`value_error` carries whatever a validator raised.

    No model here has one that quotes its input today. The rule exists for the
    day somebody writes `raise ValueError(f"unknown site {site!r}")`, which is
    this same leak wearing a different key — and the only moment it would
    otherwise be noticed is after it shipped.
    """
    cleaned = i18n.validation_detail(
        [{"type": "value_error", "loc": ("body", "site"),
          "msg": f"Value error, unknown site {CANARY!r}",
          "ctx": {"error": ValueError(CANARY)}}], "en")
    assert CANARY not in json.dumps(cleaned, default=str)
    assert cleaned[0]["msg"] == i18n.UNSPECIFIED_VALUE_ERROR
    assert cleaned[0]["loc"] == ["body", "site"], (
        "the field name is still named — `loc` is how a console highlights "
        "the input that was wrong, and it is this product's own vocabulary")


def test_a_callers_own_key_name_is_not_echoed():
    """On `extra_forbidden`, the last element of `loc` is a name the caller
    invented, not a field this product declares. A key can be content."""
    cleaned = i18n.validation_detail(
        [{"type": "extra_forbidden", "loc": ("body", CANARY),
          "msg": "Extra inputs are not permitted", "input": 1}], "en")
    assert CANARY not in json.dumps(cleaned)
    assert cleaned[0]["loc"] == ["body", i18n.UNRECOGNISED_FIELD]


def test_the_message_is_in_the_readers_language(client):
    """The half this round shares with the one before it.

    Same resolution — the credential names the reader — so this is checked
    through the browser header, which is what a caller with no token carries.
    """
    refused = client.post("/enroll", json={"display_name": "x"},
                          headers={"accept-language": "es-ES,es;q=0.9"})
    assert refused.status_code == 422
    messages = {row["msg"] for row in refused.json()["detail"]}
    assert messages == {i18n._VALIDATION["Field required"]["es"]}, (
        f"a 422 came back saying {messages}. It is the refusal a person meets "
        "most often, and it was the last one still in English.")


def test_every_validation_message_has_every_language():
    """No partial rows."""
    langs = [c for c in i18n.SUPPORTED if c != i18n.DEFAULT]
    gaps = {k: [c for c in langs if c not in v]
            for k, v in i18n._VALIDATION.items()}
    gaps = {k: v for k, v in gaps.items() if v}
    assert not gaps, (
        "these validation messages are missing languages:\n    "
        + "\n    ".join(f"{k}: {', '.join(v)}" for k, v in sorted(gaps.items())))
    assert len(i18n._VALIDATION) >= 10


def test_an_unrecognised_pydantic_message_falls_through_as_english():
    """Pydantic's catalogue is larger than the part of it this product's forms
    can produce, and it grows with pydantic. English is a visible gap; a
    guessed translation is a confident error.

    Safe to pass through *because* of what these sentences are: they
    interpolate limits — "String should have at most 64 characters" — never
    the value that failed. The two error types whose text does come from our
    own code are replaced above rather than passed through.
    """
    for message in ("String should have at most 64 characters",
                    "Input should be greater than 0"):
        assert i18n.tr_refusal(message, "ja") == message
