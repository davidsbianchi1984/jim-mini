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

import json
import re

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


# --- the exhaustive half ----------------------------------------------------
#
# Everything above this line names a string and checks it appears. That is a
# spot check, and it passed for as long as five strings on these pages were
# never translated at all: the `<title>` of both pages, both foot paragraphs,
# and the named greeting — which was run through `tr` only in its *anonymous*
# branch, so a finder holding a beacon that carries a first name got the
# largest sentence on the page in English.
#
# A named check can only find what somebody thought to name. These two ask
# the question the other way round, and derive the list from the page.

CARD = {"beacon": "bcn_1", "first_name": "Dana", "note": "wears a hearing aid",
        "badge": "UNDER CARE", "site": "Building 4"}

OTHERS = tuple(code for code in i18n.SUPPORTED if code != "en")


def _pages(language):
    """Both branches of the care page, and the dead sticker.

    The workplace/home foot is a real fork and each side is a different
    sentence — testing one branch is how one of them stayed English.
    """
    home = {k: v for k, v in CARD.items() if k != "site"}
    anon = {k: v for k, v in home.items() if k != "first_name"}
    return {
        "care, workplace": landing.care_page(CARD, language),
        "care, home": landing.care_page(home, language),
        "care, no name": landing.care_page(anon, language),
        "dead sticker": landing.gone(language),
    }


def _readable(page):
    """The page as a person meets it: no markup, no script, no entities."""
    import html as _html

    body = re.sub(r"<script>.*?</script>", " ", page, flags=re.S)
    body = re.sub(r"<style>.*?</style>", " ", body, flags=re.S)
    return _html.unescape(re.sub(r"<[^>]+>", " ", body))


def _blobs(page):
    """The `var S={...}` object the alarm script reads its words from."""
    return [json.loads(m) for m in
            re.findall(r"var S\s*=\s*(\{.*?\});", page, flags=re.S)]


def _as_pattern(known):
    """A table key as a regex, with `{name}` standing for whatever was put
    there. `"You've found {name}."` must match `You've found Dana.`"""
    return re.compile("".join(
        ".+?" if part.startswith("{") and part.endswith("}")
        else re.escape(part)
        for part in re.split(r"(\{\w+\})", known)))


def test_every_word_on_these_pages_is_in_the_table():
    """The check that found five untranslated strings the named ones missed.

    Renders in English, removes the card's own data and every sentence the
    table knows, and asks what is left. Anything still there is English that
    no reader outside the anglosphere will ever stop seeing, and that no
    amount of adding translations fixes, because nothing looks it up.
    """
    leftover = []
    for name, page in _pages("en").items():
        text = _readable(page)
        for value in CARD.values():
            if value:
                text = text.replace(str(value), " ")
        # Longest first: a short key that is a substring of a long one would
        # otherwise punch a hole in the middle of the long one and leave two
        # fragments behind, which reads as a defect and is not.
        for known in sorted(i18n._STRINGS, key=len, reverse=True):
            text = _as_pattern(known).sub(" ", text)
        for fragment in re.split(r"\s{2,}|\n", text):
            fragment = fragment.strip()
            if re.search(r"[A-Za-z]{3}", fragment):
                leftover.append(f"{name}: {fragment[:70]!r}")
    assert not leftover, (
        "these strings are on a page a stranger reads and are not in the "
        "translation table at all, so no language reaches them:\n    "
        + "\n    ".join(leftover))


def test_the_scripts_words_are_all_in_the_table_too():
    """The half that only exists after the button is pressed.

    A page that is Spanish until somebody acts on it, then turns English at
    the moment it starts giving instructions about a person on the floor, is
    the worst version of this defect rather than a lesser one.
    """
    missing = []
    for name, page in _pages("en").items():
        for blob in _blobs(page):
            missing += [f"{name}: {key}={value[:44]!r}"
                        for key, value in blob.items()
                        if isinstance(value, str) and value not in i18n._STRINGS]
    assert not missing, (
        "the alarm script writes these words and the table does not have "
        "them:\n    " + "\n    ".join(missing))


def test_no_english_survives_a_translation():
    """Derived rather than named: every sentence that shows up on the English
    page must be gone from the translated one, in all nine languages.

    **Templates are included, and that is the whole point.** The first draft
    of this skipped any key containing a `{hole}` — and so passed the exact
    defect this round exists for. `You've found {name}.` was in the table and
    the code built the sentence with an f-string instead of looking it up, so
    a Spanish finder saw "You've found Dana." at the top of the page. Both of
    the other checks called it covered, because the table did have the
    sentence. Only asking *what does the translated page actually say* finds
    it. That is the audit's own shape, one more time, inside a test written
    against it.
    """
    english = {name: _readable(page) for name, page in _pages("en").items()}
    english_script = {value for page in _pages("en").values()
                      for blob in _blobs(page) for value in blob.values()
                      if isinstance(value, str)}
    left = []
    for language in OTHERS:
        for name, page in _pages(language).items():
            readable = _readable(page)
            for known in i18n._STRINGS:
                # A translation identical to its English is a coincidence for
                # short words — German "Name" is the English one — not a
                # missed lookup, so only flag rows that actually differ.
                if i18n.tr(known, language) == known:
                    continue
                pattern = _as_pattern(known)
                if not pattern.search(english[name]):
                    continue
                if pattern.search(readable):
                    left.append(f"{language} / {name}: {known[:52]!r}")
            for blob in _blobs(page):
                for key, value in blob.items():
                    if (isinstance(value, str) and value in english_script
                            and i18n.tr(value, language) != value):
                        left.append(f"{language} / {name}: script {key}")
    assert not left, (
        "these pages still say English to somebody whose phone asked for "
        "another language:\n    " + "\n    ".join(left)
        + "\n  A sentence being in the table is not the same as the code "
          "looking it up.")


def test_every_template_keeps_its_hole_in_every_language():
    """`You've found {name}.` is filled by name substitution. A translation
    that loses `{name}` loses the person's name out of the sentence at the
    top of the page, in that language only."""
    broken = []
    for source, row in i18n._STRINGS.items():
        holes = set(re.findall(r"\{(\w+)\}", source))
        if not holes:
            continue
        for language, text in row.items():
            got = set(re.findall(r"\{(\w+)\}", text))
            if got != holes:
                broken.append(f"{source[:40]!r}/{language}: {sorted(got)} "
                              f"!= {sorted(holes)}")
    assert not broken, (
        "these translations do not carry the same named values as their "
        "English:\n    " + "\n    ".join(broken))


# --- what the alarm answers -------------------------------------------------
#
# The page is the first half. The second is the response to the button, and
# the checks above cannot see it: `note` and `badge` are rendered onto the
# page *by the script*, from JSON, after the fetch. Both were English however
# the page around them had been negotiated.
#
# They are the two sentences on the whole surface that most need to be
# understood — "the alarm is raised, this is not an emergency service" and
# "call your local emergency number yourself, this page cannot" — and they
# arrive at the moment somebody is kneeling over a person deciding what to do
# next.


def _alarm(client, bid, language=None):
    head = {"Accept-Language": language} if language else {}
    return client.post(f"/c/{bid}/alarm", json={"message": None}, headers=head)


def test_the_alarms_answer_arrives_in_the_finders_language(client):
    """Driven through the route, because the function taking a `language` is
    not the same as anything passing one — the mistake this audit has made
    most often."""
    from .conftest import enroll

    uid = enroll(client)
    made = client.post(f"/users/{uid}/beacons", json={"label": "fridge"})
    assert made.status_code == 201, made.text
    bid = made.json()["id"]

    english = _alarm(client, bid)
    assert english.status_code == 201, english.text
    plain = english.json()

    for language in ("es", "ja", "ar"):
        said = _alarm(client, bid, language).json()
        for key in ("note", "badge"):
            assert said[key] == i18n.tr(plain[key], language), (
                f"the alarm's {key} is still English for a {language} "
                f"finder: {said[key][:60]!r}")
            assert said[key] != plain[key], (
                f"{key} came back unchanged — the table has no {language} row "
                "for it, so the sentence a responder acts on is English")


def test_a_dead_sticker_refuses_in_the_finders_language(client):
    """The POST, not the page. Somebody at a peeled-off code who presses the
    button gets this, and it was English under a translated document."""
    refused = _alarm(client, "bcn_neverexisted", "fr")
    assert refused.status_code == 404
    assert refused.json()["detail"] == i18n.tr(
        "this code does not resolve to anything", "fr")


def test_the_medical_id_is_never_translated(client):
    """The line this round does not cross.

    A person's conditions, their emergency contact's name and their resting
    heart rate are facts. Running them through a translation table would be
    inventing, and on a Medical ID an invented fact is how a responder is
    misled — which is worse than an English one they can still read.
    """
    from .conftest import enroll

    uid = enroll(client, emergency_name="Alex Ruiz",
                 emergency_phone="+15555550123", contact_consent=True,
                 conditions=["Type 1 diabetes"])
    made = client.post(f"/users/{uid}/beacons", json={"label": "fridge"})
    assert made.status_code == 201, made.text
    bid = made.json()["id"]

    said = _alarm(client, bid, "es").json()
    medical = said.get("medical_id") or {}
    flat = json.dumps(medical, ensure_ascii=False)
    if "Type 1 diabetes" in json.dumps(_alarm(client, bid).json(),
                                       ensure_ascii=False):
        assert "Type 1 diabetes" in flat, (
            "a clinical condition was translated — that is inventing a fact "
            "on the one card a responder acts from")
        assert "Alex Ruiz" in flat, "the contact's name was altered"
