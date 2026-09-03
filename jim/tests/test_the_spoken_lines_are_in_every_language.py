"""The spoken lines are in every language.

The sidecar composes no prose of its own: the six sentences it may speak
without asking JIM — the re-prompt, the opt-out, the no-choice, the silence
prompt, the closing, and the trouble line — come from JIM's table, in the
call's language, riding every line envelope.
"""

from __future__ import annotations

import pytest

from jim import i18n, telephony

KEYS = {"repeat", "declined", "no_choice", "silence", "closing", "trouble",
        "unknown_caller"}


def test_the_six_lines_exist_in_all_ten_languages():
    assert set(i18n._SPOKEN_LINES) == KEYS
    for key, rows in i18n._SPOKEN_LINES.items():
        assert set(rows) == set(i18n.SUPPORTED), key
        for lang, text in rows.items():
            assert text.strip(), (key, lang)
            if lang != "en":
                assert text != rows["en"], (key, lang)


def test_the_re_prompt_names_both_keys_everywhere():
    for lang, text in i18n._SPOKEN_LINES["repeat"].items():
        assert "1" in text and "2" in text, lang


@pytest.mark.parametrize("lang", sorted(i18n.SUPPORTED))
def test_phrases_come_in_the_calls_language(lang):
    got = telephony.phrases(lang)
    assert set(got) == KEYS
    assert got["closing"] == i18n._SPOKEN_LINES["closing"][lang]


def test_an_unknown_language_falls_back_to_english():
    assert telephony.phrases("xx") == telephony.phrases("en")


def test_the_line_envelope_carries_the_sidecars_branches():
    line = telephony.line("gather_digit", "hello", "fr", again="encore", close="au revoir")
    assert line == {"say": "hello", "then": "gather_digit", "language": "fr",
                    "again": "encore", "close": "au revoir",
                    "trouble": telephony.phrases("fr")["trouble"]}
    assert telephony.line("hangup", "bye")["again"] is None
    with pytest.raises(LookupError, match="not one of the four then words"):
        telephony.line("dance", "no")


def test_the_then_words_are_the_whole_vocabulary():
    assert telephony.THEN == ("gather_digit", "speak_first", "gather_speech", "hangup")
