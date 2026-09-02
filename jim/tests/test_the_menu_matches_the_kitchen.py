"""Every option the backend offers, the backend must accept.

A catalog endpoint is a menu. The console and the three shells render it
directly — a language picker, a provider list, a robot catalog — so whatever it
lists is what a user can choose. If the endpoint that *consumes* the choice
refuses one of those values, the user picks it from a dropdown and meets an
error for doing exactly what they were offered.

This is the shape of the bug that left a sibling's community wall with dead
buttons: the request routes perfectly, and the refusal happens inside the
handler, after dispatch. The route guard in this directory says plainly that it
cannot see that far. This one can, because it stops reading source and sends the
request.

For JIM the stakes are not cosmetic. A language listed but refused is a person
who set their own language and got English back, and the safety content — the
CPR and AED playbooks — is exactly what they would have been reading.

What it does not cover: a choice the client invents rather than reads from a
catalog, and a refusal that depends on state this fixture does not set up.
`/specialists/catalog` is left out on purpose — it needs a configured QRME
endpoint and answers 409 without one, which is a tandem test rather than a
vocabulary one.
"""

from __future__ import annotations

import pytest

from .conftest import enroll


def _accepted(response) -> bool:
    """A 2xx, or a refusal clearly about something other than the value.

    409 is the one status that is not evidence of a bad vocabulary: it means the
    server understood the value and objected to the state — already bound,
    already connected.
    """
    return response.status_code < 400 or response.status_code == 409


def _check(label, offered, send):
    assert offered, f"{label}: the catalog offered nothing, so nothing was checked"
    refused = []
    for value in offered:
        response = send(value)
        if not _accepted(response):
            refused.append(f"{value!r} -> {response.status_code} "
                           f"{response.text[:120]}")
    assert not refused, (
        f"{label}: the backend offers these and then refuses them:\n  "
        + "\n  ".join(refused)
        + "\n(a value the user picked from a list the server itself supplied)"
    )


@pytest.mark.parametrize("mode", ["pre", "on_demand"])
def test_every_offered_language_can_be_set(client, mode):
    """Both delivery modes, because the pair is validated together.

    A language accepted in one mode and refused in the other would be invisible
    to a test that only tried the default.
    """
    uid = enroll(client)
    offered = [row["code"] for row in client.get("/languages").json()["languages"]]
    _check(
        f"language ({mode})", offered,
        lambda code: client.put(f"/language/{uid}",
                                json={"language": code, "mode": mode}),
    )


def test_every_language_claiming_translated_safety_content_has_it(client):
    """The menu makes a promise per language, and it has to be kept.

    `safety_content_translated` is not decoration — it tells the user whether
    the CPR and AED playbooks and the waiver terms arrive in their language or
    fall back to English. A language advertising `true` and then serving English
    is worse than a dead button: it is a person reading resuscitation steps in a
    language they did not ask for, at the moment they can least afford it.

    The trap here is structural rather than present. `HAND_TRANSLATED` is
    derived — every supported language except the default is flagged `true`
    automatically — while the strings themselves live in a hand-written table.
    Adding a tenth language to `SUPPORTED` therefore promises translated safety
    content in the same commit that gives it none, and nothing would have said
    so. Today the table is complete; this keeps it that way.
    """
    offered = client.get("/languages").json()["languages"]
    claimed = [row["code"] for row in offered
               if row.get("safety_content_translated")]
    assert claimed, "no language claims translated safety content"

    from jim import i18n

    gaps: list[str] = []
    for code in claimed:
        if code == i18n.DEFAULT:
            continue  # the default *is* the source text
        missing = [text for text, per_language in i18n._STRINGS.items()
                   if not per_language.get(code)]
        if missing:
            gaps.append(f"{code}: {len(missing)} of {len(i18n._STRINGS)} "
                        f"strings, e.g. {missing[0][:60]!r}")
    assert not gaps, (
        "these languages advertise translated safety content and do not have "
        "all of it:\n  " + "\n  ".join(gaps)
    )


def test_every_provider_on_the_menu_can_be_chosen(client):
    """Including the ones with no key configured.

    Choosing an unconfigured provider is allowed on purpose — the account
    records the preference and the runtime falls back with a warning, so the
    user can set the choice before pasting the key.
    """
    uid = enroll(client)
    # The account's own menu, not the whole catalogue: what a person is
    # offered is their region's loadout (jim/loadouts.py), and a provider off
    # it is refused on purpose — that refusal is the loadout working.
    providers = client.get(f"/models/{uid}").json()["providers"]
    _check(
        "provider", [(p["name"], p["model"]) for p in providers],
        lambda pair: client.put(f"/model/{uid}",
                                json={"provider": pair[0], "model": pair[1]}),
    )


def test_every_robot_in_the_catalog_can_be_bound(client):
    uid = enroll(client)
    catalog = client.get("/robotics/catalog").json()["robots"]
    _check(
        "robot", [r["model"] for r in catalog],
        lambda model: client.post(f"/robots/{uid}", json={"model": model}),
    )


def test_every_connector_in_the_catalog_can_be_connected(client):
    """Provider and app together, which is how the catalog is keyed."""
    uid = enroll(client)
    catalog = client.get("/connectors/catalog").json()["app_providers"]
    pairs = [(p["provider"], app["app"])
             for p in catalog for app in (p.get("apps") or [])]
    _check(
        "connector", pairs,
        lambda pair: client.post(f"/apps/{uid}",
                                 json={"provider": pair[0], "app": pair[1]}),
    )
