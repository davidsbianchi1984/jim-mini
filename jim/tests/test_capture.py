"""Showing the Guardian a rash — and the four rules that make that safe.

This is the most sensitive payload either product holds: a photograph of
somebody's body, taken at home, of the thing they are frightened about. The
first four sections are the rules, and each is asserted rather than intended:

1. a synthetic agent never receives the image
2. an intimate-site image is never stored for a minor
3. the pixels never reach JIM's own database
4. EXIF — and the GPS inside it — is removed from the bytes, not promised absent
"""

import base64
import inspect
import re

import pytest

from jim import capture
from jim.tests.conftest import enroll


# A minimal JPEG carrying an APP1 (Exif) segment with a recognisable payload,
# so the stripping test checks bytes rather than a flag.
def _jpeg_with_exif(secret: bytes = b"GPSLatitude53.8008N") -> bytes:
    app1 = b"Exif\x00\x00" + secret
    seg = b"\xff\xe1" + (len(app1) + 2).to_bytes(2, "big") + app1
    # SOF0 segment kept, so we can prove non-metadata survives.
    sof = b"\xff\xc0" + (11).to_bytes(2, "big") + b"\x08\x00\x10\x00\x10\x01\x01\x11\x00"
    return b"\xff\xd8" + seg + sof + b"\xff\xda\x00\x08pixels\xff\xd9"


def _person(client, birthdate: str = "1990-01-01", plan: str = "basic") -> dict:
    """A real enrolled account, as a row dict for `capture.take`.

    Fabricated ids used to be fine here. They are not any more: `take`
    resolves the *governing plan* from the memberships table, an id nobody
    enrolled comes back a visitor, and a visitor's posture is the open cloud —
    which is exactly where a photograph of a body may not go. See
    `jim/storage.py` and `test_storage_posture.py`.
    """
    body = {"birthdate": birthdate, "plan": plan}
    if birthdate >= "2008":
        body["guardian_consent"] = True
    uid = enroll(client, **body)
    return {"id": uid, "birthdate": birthdate}


def _b64(raw: bytes) -> str:
    return base64.b64encode(raw).decode()


class FakeVault:
    """Stands in for PDI. Records what was sealed so tests can read it back."""

    def __init__(self):
        self.store: dict[str, str] = {}

    def put(self, key, value):
        self.store[key] = value

    def get(self, key):
        return self.store.get(key)

    def delete(self, key):
        return self.store.pop(key, None) is not None


# -- 1. a synthetic agent never receives the image -----------------------------

def test_an_agent_is_told_a_photo_exists_and_never_gets_it(client):
    """A model that looks at a mole and says "that looks fine" has made a
    diagnosis — no license, no examination, no accountability — to somebody
    frightened enough to photograph it. `gate.py`'s ceiling: whatever a wrong
    answer cannot undo. A missed melanoma is not undone by the next sentence.
    """
    v = FakeVault()
    u = enroll(client)
    user = {"id": u, "birthdate": "1990-01-01"}
    capture.take(user, "photo", "forearm", _b64(_jpeg_with_exif()),
                 note="spreading since Tuesday", pdi=v)

    seen = capture.for_agent(u)
    assert len(seen) == 1
    row = seen[0]
    assert row["site"] == "forearm" and row["note"] == "spreading since Tuesday"
    # Enough to route on, and nothing else.
    assert set(row) == set(capture.AGENT_FIELDS)
    for leaky in ("content", "image", "vault_key", "digest", "bytes"):
        assert leaky not in row, leaky


def test_no_code_path_hands_an_agent_the_bytes(client):
    """Asserted against the function rather than its output, because the
    output is one refactor away from carrying a field somebody added.

    Read from the AST, not the source text. The first version was a substring
    sweep and it failed on this function's own docstring, which cites
    `pdi/gate.py` for the rule it is enforcing — the same trap PDI's console
    guide fell into. A guard that punishes explaining the invariant is one
    somebody deletes.
    """
    import ast
    import textwrap

    tree = ast.parse(textwrap.dedent(inspect.getsource(capture.for_agent)))
    called = {n.func.id for n in ast.walk(tree)
              if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert "content_for_care" not in called
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    for forbidden in ("content_for_care", "pdi", "base64", "b64decode",
                      "b64encode"):
        assert forbidden not in names, f"for_agent reaches {forbidden!r}"
    # `.get`/`.put` on a vault specifically — `cap.get(k)` is dict access and
    # naming it forbidden would be a guard that fights the code rather than
    # the risk.
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            assert not (node.value.id == "pdi"), (
                f"for_agent calls pdi.{node.attr}")
    # And the literal key it would need is never mentioned in code either.
    literals = {n.value for n in ast.walk(tree)
                if isinstance(n, ast.Constant) and isinstance(n.value, str)}
    assert "vault_key" not in literals


def test_an_intimate_capture_is_omitted_from_the_agent_view_entirely(client):
    """Not summarised. "There is a photograph of their groin" is itself the
    disclosure."""
    v = FakeVault()
    u = enroll(client)
    user = {"id": u, "birthdate": "1990-01-01"}
    capture.take(user, "photo", "forearm", _b64(_jpeg_with_exif()), pdi=v)
    capture.take(user, "photo", "groin", _b64(_jpeg_with_exif()),
                 intimate_consent=True, pdi=v)

    assert len(capture.for_user(u)) == 2
    seen = capture.for_agent(u)
    assert len(seen) == 1
    assert all(r["site"] != "groin" for r in seen)
    assert "groin" not in str(seen)


# -- 2. never for a child ------------------------------------------------------

def test_an_intimate_site_is_refused_for_a_minor_with_no_override(client):
    """The hard line. No override, no guardian consent path, no setting. A
    guardian product that could be talked into storing that image is one whose
    other guarantees do not matter."""
    v = FakeVault()
    child = _person(client, "2015-01-01")
    for site in sorted(capture.INTIMATE):
        with pytest.raises(capture.CaptureError) as exc:
            capture.take(child, "photo", site, _b64(_jpeg_with_exif()),
                         intimate_consent=True, pdi=v)
        assert "minor" in str(exc.value), site
    assert v.store == {}, "something was sealed despite the refusal"


def test_the_refusal_points_somewhere_useful(client):
    """A flat "no" to a frightened parent is a product failing twice."""
    v = FakeVault()
    child = _person(client, "2015-01-01")
    with pytest.raises(capture.CaptureError) as exc:
        capture.take(child, "photo", "genital", _b64(_jpeg_with_exif()),
                     intimate_consent=True, pdi=v)
    assert "clinician" in str(exc.value)


def test_a_non_intimate_site_is_fine_for_a_child(client):
    """A child's rash on the forearm is an ordinary thing to photograph, and
    refusing it would push a parent to a worse tool."""
    v = FakeVault()
    child = _person(client, "2015-01-01")
    out = capture.take(child, "photo", "forearm", _b64(_jpeg_with_exif()),
                       pdi=v)
    assert out["site"] == "forearm" and len(v.store) == 1


def test_an_adult_still_confirms_an_intimate_site(client):
    v = FakeVault()
    adult = _person(client, "1990-01-01")
    with pytest.raises(capture.CaptureError) as exc:
        capture.take(adult, "photo", "breast", _b64(_jpeg_with_exif()), pdi=v)
    assert "confirmation" in str(exc.value)
    assert v.store == {}
    ok = capture.take(adult, "photo", "breast", _b64(_jpeg_with_exif()),
                      intimate_consent=True, pdi=v)
    assert ok["intimate"] is True


# -- 3. the pixels never reach JIM's own database ------------------------------

def test_the_schema_has_nowhere_to_put_an_image(client):
    """A `content` column here is one somebody eventually writes to, and the
    thing they would be writing is an unencrypted photograph of skin."""
    from jim import db

    cols = {r[1] for r in db.connect().execute(
        "PRAGMA table_info(captures)").fetchall()}
    for forbidden in ("content", "image", "data", "blob", "bytes_b64"):
        assert forbidden not in cols, f"captures has a {forbidden!r} column"
    assert "vault_key" in cols and "digest" in cols


def test_no_vault_means_no_capture_rather_than_a_local_file(client):
    """Degrading gracefully is right almost everywhere and wrong here: the
    graceful version is an unencrypted photograph on a laptop."""
    adult = _person(client, "1990-01-01")
    with pytest.raises(capture.VaultRequired) as exc:
        capture.take(adult, "photo", "forearm", _b64(_jpeg_with_exif()),
                     pdi=None)
    assert "vault" in str(exc.value)
    from jim import db

    n = db.connect().execute("SELECT COUNT(*) AS n FROM captures").fetchone()["n"]
    assert n == 0, "a row was written with no vault behind it"


def test_the_refusal_names_the_free_option(client):
    """Requiring a vault costs nobody anything, because colocation is free —
    and a refusal that did not say so would read as an upsell."""
    adult = _person(client, "1990-01-01")
    with pytest.raises(capture.VaultRequired) as exc:
        capture.take(adult, "photo", "forearm", _b64(_jpeg_with_exif()),
                     pdi=None)
    assert "free" in str(exc.value)


def test_the_image_comes_back_only_through_the_vault(client):
    v = FakeVault()
    adult = _person(client, "1990-01-01")
    cap = capture.take(adult, "photo", "back", _b64(_jpeg_with_exif()), pdi=v)
    assert capture.content_for_care(cap["id"], v)
    with pytest.raises(capture.VaultRequired):
        capture.content_for_care(cap["id"], None)


def test_the_module_writes_nothing_but_its_own_table(client):
    src = inspect.getsource(capture)
    written = set(re.findall(r"(?:INSERT INTO|DELETE FROM)\s+(\w+)", src))
    written |= set(re.findall(r"(?<!DO )\bUPDATE\s+(\w+)\s+SET", src))
    assert written <= {"captures"}, f"capture writes elsewhere: {written}"


# -- 4. EXIF is removed from the bytes -----------------------------------------

def test_gps_is_gone_from_the_sealed_bytes(client):
    """Not a flag, not a promise — the coordinate is checked for in what was
    actually stored. A rash photographed at home geotags the person's house,
    and that coordinate outlives the rash."""
    v = FakeVault()
    adult = _person(client, "1990-01-01")
    raw = _jpeg_with_exif(b"GPSLatitude53.8008N")
    assert b"GPSLatitude" in raw                     # it is really in there

    cap = capture.take(adult, "photo", "leg", _b64(raw), pdi=v)
    sealed = base64.b64decode(v.store[cap["vault_key"]])
    assert b"GPSLatitude" not in sealed
    assert b"Exif" not in sealed
    assert b"pixels" in sealed, "the image itself was destroyed too"


def test_what_was_stripped_is_recorded(client):
    v = FakeVault()
    adult = _person(client, "1990-01-01")
    cap = capture.take(adult, "photo", "leg", _b64(_jpeg_with_exif()), pdi=v)
    assert "exif/xmp" in cap["stripped"]


def test_a_format_it_cannot_parse_is_reported_rather_than_claimed_clean(client):
    """Saying "stripped" about a format this function does not parse would be
    the exact false assurance the module is written against."""
    png = b"\x89PNG\r\n\x1a\n" + b"tEXtComment\x00hello"
    out, removed = capture.strip_metadata(png)
    assert out == png
    assert "not-a-jpeg" in removed[0]
    assert not any("exif" in r for r in removed)


def test_stripping_leaves_a_jpeg_still_a_jpeg(client):
    out, _ = capture.strip_metadata(_jpeg_with_exif())
    assert out.startswith(b"\xff\xd8") and out.endswith(b"\xff\xd9")


# -- what it is for ------------------------------------------------------------

def test_provenance_says_whether_the_app_can_vouch_for_it(client):
    """An imported photograph may be months old or of somebody else. The
    file's own timestamp is whatever the device felt like writing."""
    v = FakeVault()
    adult = _person(client, "1990-01-01")
    imported = capture.take(adult, "photo", "hand", _b64(_jpeg_with_exif()),
                            provenance="imported", pdi=v)
    assert "cannot verify" in imported["provenance_note"]


def test_video_and_audio_are_capturable(client):
    """Some things are only visible in motion — a tremor, a gait, a wheeze —
    and a still frame loses exactly the thing being asked about."""
    v = FakeVault()
    adult = _person(client, "1990-01-01")
    for kind in ("video", "audio"):
        out = capture.take(adult, kind, "whole_body", _b64(b"\x00clip"), pdi=v)
        assert out["kind"] == kind


def test_an_unknown_kind_or_site_is_refused(client):
    v = FakeVault()
    adult = _person(client, "1990-01-01")
    for kwargs in ({"kind": "hologram", "site": "hand"},
                   {"kind": "photo", "site": "aura"}):
        with pytest.raises(capture.CaptureError):
            capture.take(adult, kwargs["kind"], kwargs["site"],
                         _b64(_jpeg_with_exif()), pdi=v)


def test_junk_and_oversize_are_refused(client):
    v = FakeVault()
    adult = _person(client, "1990-01-01")
    with pytest.raises(capture.CaptureError):
        capture.take(adult, "photo", "hand", "not base64!!", pdi=v)
    with pytest.raises(capture.CaptureError):
        capture.take(adult, "photo", "hand", "", pdi=v)
    big = _b64(b"\x00" * (capture.MAX_BYTES + 1))
    with pytest.raises(capture.CaptureError) as exc:
        capture.take(adult, "photo", "hand", big, pdi=v)
    assert "limit" in str(exc.value)


# -- releasing to a clinician --------------------------------------------------

def test_intimate_captures_are_never_swept_into_a_referral(client):
    """A summary that included them because they matched the condition would
    be the product making that decision on somebody's behalf."""
    v = FakeVault()
    u = enroll(client)
    user = {"id": u, "birthdate": "1990-01-01"}
    ordinary = capture.take(user, "photo", "back", _b64(_jpeg_with_exif()),
                            pdi=v)
    private = capture.take(user, "photo", "breast", _b64(_jpeg_with_exif()),
                           intimate_consent=True, pdi=v)

    out = capture.attach_to_referral([ordinary["id"], private["id"]], u)
    assert out["release"] == [ordinary["id"]]
    assert out["explicit"] == [private["id"]]
    assert "deliberately" in out["note"]


def test_you_cannot_attach_somebody_elses_capture(client):
    v = FakeVault()
    mine = capture.take(_person(client, "1990-01-01"),
                        "photo", "hand", _b64(_jpeg_with_exif()), pdi=v)
    with pytest.raises(capture.CaptureError):
        capture.attach_to_referral([mine["id"]], "usr_b")


def test_deleting_destroys_the_vault_record_and_leaves_a_tombstone(client):
    """A clinician who was shown something should see it was withdrawn rather
    than find a dangling reference — but the bytes go."""
    v = FakeVault()
    u = enroll(client)
    cap = capture.take({"id": u, "birthdate": "1990-01-01"}, "photo",
                       "hand", _b64(_jpeg_with_exif()), pdi=v)
    assert v.store

    out = capture.delete(cap["id"], u, v)
    assert out["deleted_at"] is not None
    assert v.store == {}, "the image survived the delete"
    assert capture.read(cap["id"])["id"] == cap["id"]     # tombstone stands
    assert cap["id"] not in [c["id"] for c in capture.for_user(u)]


def test_you_cannot_delete_somebody_elses(client):
    v = FakeVault()
    cap = capture.take(_person(client, "1990-01-01"),
                       "photo", "hand", _b64(_jpeg_with_exif()), pdi=v)
    with pytest.raises(capture.CaptureError):
        capture.delete(cap["id"], "usr_y", v)


# -- over the wire -------------------------------------------------------------

def test_the_vocabulary_is_public_and_states_the_limits(client):
    out = client.get("/captures/vocabulary").json()
    assert out["vault_required"] is True
    assert "image itself" in out["agent_never_sees"]
    assert "no override" in out["minors"]
    assert set(out["intimate"]) == set(capture.INTIMATE)


def test_taking_one_over_http_without_a_vault_is_a_503(client):
    """The request was fine and the deployment is not — 503, not 422."""
    u = enroll(client)
    r = client.post(f"/users/{u}/captures",
                    json={"kind": "photo", "site": "forearm",
                          "content": _b64(_jpeg_with_exif())})
    assert r.status_code == 503, r.text
    assert "vault" in r.json()["detail"]


def test_another_user_cannot_read_your_captures(client):
    from jim.tests.conftest import as_user

    v = FakeVault()
    mine = enroll(client)
    my_token = client.headers["authorization"].split()[1]
    cap = capture.take({"id": mine, "birthdate": "1990-01-01"}, "photo",
                       "back", _b64(_jpeg_with_exif()), pdi=v)
    other = enroll(client, display_name="Rae")
    del other
    # Still holding Rae's token.
    assert client.get(f"/users/{mine}/captures").status_code == 403
    assert client.get(
        f"/users/{mine}/captures/{cap['id']}/image").status_code == 403

    as_user(client, my_token)
    assert client.get(f"/users/{mine}/captures").status_code == 200
