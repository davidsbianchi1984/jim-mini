"""One contract, three copies — the header a stranger's browser sends.

## Why this file is byte-identical in three repositories

QRME, JIM-mini and PDI each grew a `negotiate()` in a different round, for a
different surface, written from scratch each time: the objector's screen, the
beacon page a passer-by kneels over, the sticker on a sealed carrier. Same
input, same job, three implementations — and the person they serve is
frequently the *same person*, holding one phone, meeting whichever of the
three products the situation put in front of them.

Three copies of one contract drift. Ours already had:

    ar;q=0        qrme en   jim ar   pdi en
    de;q=abc      qrme en   jim de   pdi en

`q=0` means **not acceptable** — RFC 9110 says so plainly — so a browser
sending `ar;q=0` is refusing Arabic. JIM answered in it, on the page somebody
reads while deciding what to do for a person on the floor. It appended every
recognised tag to the ranking regardless of quality, so a header that refused
the only language it named got that language back.

Neither product was checking. Each had its own table of header cases and each
one passed, because each was asking whether *its* implementation did what
*its* author expected. That is this audit's recurring shape across a
repository boundary:

    asked     does this product read the header correctly
    mattered  do the three read it the same way

## What is checked

The table below is the contract. It is not a description of what these
functions happen to do — several rows failed when it was first written. Any
row that disagrees with any product is a defect in that product, and the fix
is to make the product match, not to soften the row.

Copy this file verbatim when adding a fourth product. It imports its own
package by name and nothing else, so the only edit is the import.
"""

from __future__ import annotations

import pytest

from jim import i18n

#: (Accept-Language, the language a reader should get)
#:
#: Written as prose because each row is a decision, not an observation.
CONTRACT = [
    # Nothing to go on falls back rather than guessing.
    (None, "en"),
    ("", "en"),
    ("   ", "en"),
    (",,", "en"),
    ("*", "en"),
    ("xx,yy", "en"),

    # The ordinary case, and the region dropped: a reader in Buenos Aires and
    # a reader in Madrid both read Spanish.
    ("es-ES,es;q=0.9,en;q=0.8", "es"),
    ("es-419", "es"),
    ("en-GB,en;q=0.5", "en"),
    ("zh-Hans", "zh"),

    # Case is not meaningful in a language tag.
    ("JA-JP", "ja"),

    # A tag nobody carries is skipped, not fallen back on.
    ("tlh,ja", "ja"),

    # Quality decides, and the header's own order breaks a tie — listing one
    # tag before another at the same q is what a client means by preferring
    # it.
    ("fr;q=0.4,de;q=0.9", "de"),
    ("fr,es", "fr"),
    ("hi;q=1.0,en;q=1.0", "hi"),
    ("es;q=0.5,fr;q=0.5,de;q=0.5", "es"),

    # `q=0` means **not acceptable**. A browser sending this is refusing the
    # tag, and answering in it is answering in a language the reader has
    # explicitly said they do not want.
    ("ar;q=0", "en"),
    ("ar;q=0,fr", "fr"),

    # A malformed quality is not a preference. Treating it as zero refuses
    # the tag rather than promoting it above properly-formed ones.
    ("de;q=abc", "en"),
    ("de;q=abc,es;q=0.2", "es"),
]


@pytest.mark.parametrize("header,expected", CONTRACT)
def test_the_header_is_read_the_way_the_other_products_read_it(header,
                                                               expected):
    assert i18n.negotiate(header) == expected, (
        f"this product reads {header!r} as "
        f"{i18n.negotiate(header)!r} where the contract says {expected!r}. "
        "The same person meets all three of these products with the same "
        "phone; a header cannot mean different things to each.")


#: The ten, written down rather than read from the product.
#:
#: The first version of this checked `i18n.SUPPORTED` against itself — it
#: iterated the product's own list and asked whether each entry negotiated to
#: itself, which is true of any list whatsoever. Adding a language to one
#: product and not the others passed; so would removing one, because removing
#: it also removed the check. A contract that reads its expectations out of
#: the thing it is checking is not a contract, and that is this audit's shape
#: turned on a test rather than on a product.
LANGUAGES = ("en", "es", "fr", "de", "pt", "it", "ja", "zh", "hi", "ar")


def test_the_product_carries_exactly_the_languages_the_others_do():
    """The same person meets all three. A language one product speaks and
    another does not is a reader who changes language by walking from a
    sticker to a beacon."""
    assert tuple(i18n.SUPPORTED) == LANGUAGES, (
        f"this product carries {tuple(i18n.SUPPORTED)}, and the contract the "
        f"other two hold is {LANGUAGES}")


def test_every_language_in_the_contract_is_reachable_from_a_browser():
    """In the table and unreachable is the same as absent, to a reader."""
    for code in LANGUAGES:
        assert i18n.negotiate(code) == code, (
            f"{code!r} is in the contract and does not negotiate to itself")


def test_english_is_the_fallback_and_is_supported():
    assert i18n.DEFAULT == "en"
    assert "en" in i18n.SUPPORTED
