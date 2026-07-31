"""Localization keyed on a setting only account-holders have.

## The finding

Every localization path in this product takes a ``user_id``.
``i18n.get_language(user_id)``, ``i18n.effective_language(user_id)``,
``i18n.translate(user_id, ...)``. That is right for everything a user reads,
and it silently excludes the one reader who has no user id: the stranger who
scanned a care beacon.

`landing.py` had known who that reader is since it was written —

    It opens inside a camera app's in-app browser, on cellular, from a cold
    start, possibly by somebody kneeling next to a person on the floor. The
    reader is a stranger with no account.

— and served them English, everywhere in the world, including the sentence
telling them to call an ambulance and the instruction not to move the person.

`Accept-Language` is on every one of those requests. Before this round,
``grep -r accept.language`` returned nothing in any of the three products.

This is the audit's recurring shape one turn further on. The last two rounds
found routes whose *door* was keyed on having an account. This is the same
mistake in the layer above: the door was built, and then the **language** of
the door was keyed on having an account too.

## Why the finder's language and not the watched person's

The subject's language is known — they have a user record. It is the wrong
one. The text is for whoever is holding the phone, and the whole premise of a
care beacon is that those are different people. A Spanish speaker's beacon
scanned by a French passer-by should read French: the person who needs to
understand it is the one being asked to act.

## Why hand-translated

`i18n.py` set this rule before this round and it is quoted here because it is
the reason these strings are in a table rather than through a model:

    Deterministic safety content is hand-translated here for every supported
    language, string-keyed against the English source so an edit to the
    English invalidates the translation loudly (fallback to English) instead
    of silently drifting. Safety text is never machine-mangled.

The beacon page is the most safety-critical text in the product and had none
of it. `test_the_menu_matches_the_kitchen.py` already fails any language that
advertises translated safety content and lacks a string, so adding these to
`_STRINGS` made the round all-or-nothing across nine languages. That is the
correct constraint and it is left in place.
"""

from __future__ import annotations

import pytest

from jim import i18n, landing


@pytest.mark.parametrize("header,expected", [
    ("es-ES,es;q=0.9,en;q=0.8", "es"),
    ("fr-CA", "fr"),                       # region dropped
    ("en;q=0.2,ja;q=0.9", "ja"),           # quality honoured over order
    ("xx,yy", "en"),                       # nothing recognised
    ("", "en"),
    (None, "en"),
])
def test_the_header_picks_the_language(header, expected):
    assert i18n.negotiate(header) == expected


def test_the_finders_language_reaches_the_page():
    card = {"beacon": "bcn_1", "first_name": None, "note": "", "badge": "",
            "site": None}
    page = landing.care_page(card, "es")
    assert "número de emergencias" in page, (
        "the beacon page is still English for a Spanish-speaking finder")
    assert 'lang="es"' in page, (
        "the document does not declare its language — which is what a screen "
        "reader picks a voice from, and this page may well be read aloud")


def test_arabic_gets_a_direction():
    card = {"beacon": "bcn_1", "first_name": None, "note": "", "badge": "",
            "site": None}
    page = landing.care_page(card, "ar")
    assert 'dir="rtl"' in page, (
        "Arabic is one of the ten supported languages and the page does not "
        "say which way it reads")


def test_the_script_strings_are_translated_too():
    """The half that is easy to miss.

    Most of what this page says is written by its own script *after* the
    alarm — the Medical ID labels, the guidance box, the offline fallback.
    Translating only the server-rendered half would give a finder a Spanish
    page that turns English at the moment it starts giving instructions.
    """
    card = {"beacon": "bcn_1", "first_name": None, "note": "", "badge": "",
            "site": None}
    page = landing.care_page(card, "es")
    for expected in ("IDENTIFICACIÓN MÉDICA",       # medid
                     "Contacto de emergencia",      # contact
                     "¿Qué hago mientras espera?",  # whatdo
                     "No les mueva"):               # the offline answer
        assert expected in page, (
            f"the script's strings are still English: {expected!r} missing")


def test_the_answer_itself_arrives_in_the_finders_language():
    """The payload, not just the frame.

    A page that is Spanish until the moment it starts giving instructions is
    barely better than one that was never translated — the English arrives at
    exactly the point somebody is being asked to act on it. The standing
    answer is hand-translated; the specialist path gets `i18n.directive`
    appended to the question, which is how every other model-generated text
    in this product is localized.
    """
    from jim import relay

    out = relay.guidance("alm_x", "not waking up", language="fr")
    assert out["answer"] != relay.STANDING, (
        "the standing guidance is still English for a French finder")
    assert "urgence" in out["answer"]
    assert relay.guidance("alm_x", "q", language="en")["answer"] == (
        relay.STANDING), "English must still be the source text, untouched"


def test_the_dead_sticker_page_is_localized_as_well():
    """A peeled-off code is still somebody standing over a person, and the
    only useful sentence on that page is the one telling them to call."""
    page = landing.gone("fr")
    assert "Ce code ne correspond" in page
    assert 'lang="fr"' in page


def test_an_unknown_string_falls_back_rather_than_guessing():
    """The property that makes editing the English safe.

    `tr` returns the source text when a translation is missing. That is a
    visible, honest failure — English in a Spanish page — rather than a
    stale translation that says something the English no longer says.
    """
    assert i18n.tr("a string nobody has translated", "es") == (
        "a string nobody has translated")


def test_the_page_asks_for_a_language_it_was_given():
    """A guard on the guard.

    Every test above passes a language in directly. If the route stopped
    reading `Accept-Language`, they would all still pass and every real
    scanner would be back to English.

    **The docstring is stripped before searching**, and that is not
    hypothetical tidiness: the first version of this test searched the whole
    function, and the injection that replaced the negotiation with
    `language = "en"` passed — because `beacon_page`'s own docstring contains
    the words "Accept-Language" and "negotiated". That is the seventh time in
    this audit a check has been satisfied by prose describing the thing
    rather than the thing, and the first time it happened inside the test
    written to catch it.
    """
    import inspect
    import re

    from jim import api

    source = inspect.getsource(api)
    beacon = source[source.index("def beacon_page"):]
    beacon = beacon[:beacon.index("\n    @app.")]
    code = re.sub(r'""".*?"""', "", beacon, flags=re.S)      # no docstring
    code = re.sub(r"#[^\n]*", "", code)                      # no comments

    assert "accept-language" in code.lower(), (
        "the beacon route no longer reads Accept-Language, so every scanner "
        "gets the default no matter what their phone asked for")
    assert "negotiate" in code, (
        "the route is not negotiating the language through i18n.negotiate")
