"""Every path JIM's clients call must resolve to a route that exists.

This guard exists because of a bug in the sibling. QRME's community wall shipped
its like, comment and share buttons dead: the console asked for `/post/{id}/…`
where only `/posts/{id}/…` is mapped, the backend tests passed because they used
the reachable form, and the console compiled because a template literal is only
a string. Nobody was comparing the two halves.

JIM has the same shape of exposure and had none of the checking. The console
builds its paths in template literals; the three native shells build theirs in
Swift, Kotlin and C#, where `native.yml` proves they *compile* and cannot say
whether they *resolve*. A mistyped path is a button that does nothing, and the
only way to find it was to press it.

Extraction and matching live in :mod:`jim.tests.clientpaths`, byte-identical
with qrme's and pdi's copies.
"""

from __future__ import annotations

from jim.api import app

from . import clientpaths
from .clientpaths import (CONSOLE, NATIVE, VERBS, accepts, calls,
                          methods_for, normalise, paths)

from . import ratchets

# Low enough to allow a shell to shed a screen, high enough that a pattern which
# has stopped matching altogether cannot pass as coverage.
_MIN_CONSOLE_PATHS = 20
_MIN_NATIVE_PATHS = 30


def test_every_console_call_reaches_a_route():
    """Method and path together, for every request the console makes.

    Checking the path alone accepts a client sending POST where only GET is
    mounted. That is a 405, and from the user's side it is the same dead button
    as a 404 — so the assertion is a FULL router match, not a partial one.

    Scoping to the enclosing call is what makes that possible, and it also keeps
    path-shaped literals that are not requests out of the result: `"/app"` is
    tested against `window.location.pathname` to work out where the console is
    being served, not sent to anything.
    """
    missing = clientpaths.refused(app, CONSOLE)
    assert not missing, (
        "the console makes these requests and no route accepts them:\n  "
        + "\n  ".join(missing)
        + "\n(a 404 or 405 the user meets as a button that does nothing)"
    )


def test_every_native_call_reaches_a_route():
    """Method and path together, on all three shells.

    Each language says the verb its own way — Swift labels it
    (`method: "PUT"`), Kotlin passes it positionally, C# encodes it in the
    helper's name (`Post(...)`) or an `HttpMethod` constant — so the check reads
    it rather than assuming GET.

    All three shells reported together.

    A path added to two shells and mistyped in the third is the likely shape of
    this failure, so the message should name the platform rather than making the
    reader run the suite three times to find out which one drifted.
    """
    missing: list[str] = []
    for lang in NATIVE:
        for line in clientpaths.refused(app, lang):
            missing.append(f"[{lang.name}] {line}")
    assert not missing, (
        "the native shells make these requests and no route accepts them:\n  "
        + "\n  ".join(missing)
    )


def test_every_surface_is_actually_being_scanned():
    """A guard on the guard.

    An extraction pattern that silently matches nothing turns this file into a
    test that always passes — the worst kind, because the coverage it claims
    reads exactly like the coverage it has.
    """
    counted = {CONSOLE.name: len(paths(CONSOLE))}
    counted.update({lang.name: len(paths(lang)) for lang in NATIVE})
    floors = {CONSOLE.name: _MIN_CONSOLE_PATHS}
    floors.update({lang.name: _MIN_NATIVE_PATHS for lang in NATIVE})
    thin = {k: v for k, v in counted.items() if v < floors[k]}
    assert not thin, (
        f"suspiciously few paths extracted: {thin} — the literal or "
        f"interpolation pattern for that language has probably stopped "
        f"matching. All counts: {counted}"
    )


def test_an_interpolated_query_does_not_truncate_the_path():
    """The extractor's own blind spot, pinned.

    An earlier version of this check cut a literal at its first interpolation
    whenever a query followed. That is harmless for `?days=${d}` written after a
    constant path and wrong for `/meds/${uid}/adherence?days=${d}`, where it
    leaves `/meds` — a prefix that resolves for the wrong reason and takes the
    real tail with it. JIM's medication adherence board is exactly that shape,
    so the fixture is the live path rather than a toy.
    """
    assert normalise("/meds/${uid}/adherence?days=${d}", CONSOLE) == (
        "/meds/x/adherence"
    )
    assert "/meds/x/adherence" in paths(CONSOLE), (
        "the adherence path is still not reaching the guard"
    )
    # A query written after a constant path still ends where it always did.
    assert normalise("/checkins?limit=${n}", CONSOLE) == "/checkins"


def test_the_check_is_really_method_aware():
    """Pinned against the live app, so it cannot quietly relax to path-only.

    An earlier version of this guard accepted a partial router match — path
    right, method ignored. That passes a client sending the wrong verb, which
    answers 405 and looks to the user exactly like the 404 the guard exists to
    prevent.

    Each surface's verb reader is checked for life separately, because they are
    separate code: Swift labels the method, Kotlin passes it positionally, C#
    encodes it in the helper's name. If one stops matching, every call from that
    surface silently becomes a GET — and since most routes do serve a GET, the
    suite would stay green while checking almost nothing.
    """
    for lang in (CONSOLE,) + NATIVE:
        made = calls(lang)
        assert made, f"{lang.name}: no calls extracted at all"
        verbs = {method for method, _ in made}
        assert verbs <= set(VERBS), f"{lang.name}: unexpected verbs {verbs}"
        assert len(verbs) >= ratchets.floor("route.verbs_min"), (
            f"{lang.name} reports only {verbs} across {len(made)} calls — its "
            "verb reader has probably stopped matching, which would turn every "
            "call into an unchecked GET"
        )

    # A real verb difference on a real route: the health check is read-only.
    assert accepts(app, "GET", "/health")
    assert not accepts(app, "POST", "/health")
    assert methods_for(app, "/health") == ["GET"]
