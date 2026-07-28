"""Showing the Guardian, and a clinician, the thing you cannot describe.

A rash, a wound that is not closing, swelling, a bruise spreading, the colour
of something. These are the parts of a condition that text loses: *"it's a bit
red"* is the same sentence for a heat rash and for cellulitis. This lets
somebody photograph it, attach it to a condition, and have it reach a real
clinician through the referral flow that already exists.

**This is the most sensitive payload either product will ever hold.** A
photograph of somebody's body, taken at home, of the thing they are frightened
about. Every rule below follows from that and none of them is decoration.

**The pixels never touch JIM's own database.** They go to the PDI vault,
sealed, and this table keeps only the metadata — kind, site, when, provenance,
and the vault key. There is no fallback: if no vault is configured, capture is
**refused** rather than degrading to a local file. Degrading gracefully is the
right instinct almost everywhere and the wrong one here, because the graceful
version is an unencrypted photograph of somebody's skin sitting in a SQLite
file on a laptop. Colocation is free (`pdi/hosting.py`) precisely so that
requiring a vault costs nobody anything.

**A synthetic agent never sees the image.** It may know that a capture exists,
where on the body, and when — enough to say *"there is a photograph attached
and somebody should look at it"* — and it never receives the bytes. This is
`pdi/gate.py`'s ceiling arriving in the place it matters most: *the agent's
ceiling is whatever a wrong answer cannot undo.* A model that looks at a
mole and says "that looks fine" has made a diagnosis, with no license, no
examination and no accountability, to somebody who was frightened enough to
photograph it. There is no configuration that turns this on, and
:func:`for_agent` is the only shape an agent can receive.

**Location is stripped, not promised to be absent.** A photograph carries EXIF,
and EXIF carries GPS. A rash photographed at home geotags the person's house to
whoever later reads the record. :func:`strip_metadata` removes it from the
bytes before they are sealed, and reports what it removed.

**Intimate sites are a real clinical need and a separate decision.** A rash
does not respect modesty, and a product that refused to let somebody photograph
one would push them to a worse tool. So they are allowed, with an explicit
extra confirmation, never routed to an agent, and never folded into an
automatically assembled summary — a clinician opens them deliberately or not at
all.

**And never for a child.** :data:`INTIMATE` sites on an account belonging to a
minor are refused outright, with no override, no guardian consent path and no
setting. A guardian product that could be talked into storing that image is one
whose other guarantees do not matter.
"""

from __future__ import annotations

import base64
import hashlib
import json
from datetime import date, datetime, timezone

from . import db, storage, tiers

# What can be captured. Video and audio are here because some things are only
# visible in motion — a tremor, a gait, a wheeze — and a still frame loses
# exactly the thing being asked about.
KINDS: dict[str, str] = {
    "photo": "a still image",
    "video": "a short clip, for something only visible in motion",
    "audio": "a sound — a cough, a wheeze, a breathing pattern",
}

# Where on the body. A closed list, because "site" typed freehand is a field
# nobody can route on and every clinician has to read twice.
SITES: dict[str, str] = {
    "scalp": "scalp or hairline",
    "face": "face",
    "eye": "eye or eyelid",
    "mouth": "mouth, lips or tongue",
    "ear": "ear",
    "neck": "neck or throat",
    "chest": "chest",
    "back": "back",
    "abdomen": "abdomen",
    "arm": "upper arm or shoulder",
    "forearm": "forearm or elbow",
    "hand": "hand, wrist or fingers",
    "hip": "hip",
    "leg": "thigh or knee",
    "lower_leg": "lower leg or ankle",
    "foot": "foot or toes",
    "groin": "groin",
    "genital": "genital area",
    "breast": "breast",
    "buttock": "buttock",
    "whole_body": "a general view",
}

# Sites that carry a separate decision. Not refused — a rash does not respect
# modesty, and a product that would not let somebody photograph one pushes them
# to a worse tool — but confirmed explicitly, kept out of agent hands entirely,
# and kept out of any automatically assembled summary.
INTIMATE: frozenset[str] = frozenset({"genital", "breast", "buttock", "groin"})

# Where it came from. An imported photograph may be months old or of somebody
# else entirely, and a clinician reading it needs to know which they are
# looking at. Recorded rather than inferred, because the file's own timestamp
# is whatever the device felt like writing.
PROVENANCE: dict[str, str] = {
    "captured": "taken now, in the app",
    "imported": "chosen from the device's library — may be older, and the app "
                "cannot verify who is in it",
}

# The one thing an agent may be told, and the shape it arrives in. Nothing here
# is an image. See `for_agent`.
AGENT_FIELDS: tuple[str, ...] = ("id", "kind", "site", "site_label",
                                 "captured_at", "provenance", "note",
                                 "intimate", "seen_by_clinician")

MAX_BYTES = 25 * 1024 * 1024        # a phone photo or a short clip
VAULT_SCOPE = "medical/capture"


class CaptureError(ValueError):
    """A capture that cannot be taken. Text meant for a person."""


class VaultRequired(CaptureError):
    """No vault is configured, and this payload does not go anywhere else."""


# -- metadata stripping --------------------------------------------------------

def strip_metadata(raw: bytes) -> tuple[bytes, list[str]]:
    """Remove EXIF and friends from an image, and say what was removed.

    Real, not a promise. A JPEG is a sequence of marker segments; the ones
    carrying camera metadata are APP1 (`Exif`/XMP), APP2 (ICC/FlashPix), APP13
    (Photoshop IRB, which carries IPTC) and the COM comment. GPS coordinates
    live in the Exif IFD inside APP1, so dropping the segment drops the
    location.

    This matters more than it looks. A rash photographed at home geotags the
    person's house, and that coordinate then travels to a clinician, into a
    referral package, and into a vault record that outlives the rash. Nobody
    involved ever intended to disclose an address.

    Formats other than JPEG are passed through and reported as such rather than
    silently claimed to be clean — a PNG's `tEXt` chunks and a HEIC's metadata
    boxes need their own handling, and saying "stripped" about a format this
    function does not parse would be the exact kind of false assurance the
    module note is against.
    """
    removed: list[str] = []
    if not raw.startswith(b"\xff\xd8"):          # not a JPEG
        return raw, ["not-a-jpeg: metadata left as-is, nothing claimed"]

    names = {0xE1: "exif/xmp", 0xE2: "icc", 0xED: "photoshop-iptc",
             0xFE: "comment"}
    out = bytearray(b"\xff\xd8")
    i = 2
    n = len(raw)
    while i < n - 1:
        if raw[i] != 0xFF:
            out.extend(raw[i:])                  # not a marker: entropy data
            break
        marker = raw[i + 1]
        if marker == 0xD9:                       # end of image
            out.extend(raw[i:i + 2])
            i += 2
            continue
        if marker == 0xDA:                       # start of scan — pixels follow
            out.extend(raw[i:])
            break
        if i + 4 > n:
            out.extend(raw[i:])
            break
        length = int.from_bytes(raw[i + 2:i + 4], "big")
        segment = raw[i:i + 2 + length]
        if marker in names:
            removed.append(names[marker])
        else:
            out.extend(segment)
        i += 2 + length
    return bytes(out), removed or ["none found"]


# -- taking one ----------------------------------------------------------------

def _age_of(user: dict) -> int | None:
    if not user.get("birthdate"):
        return None
    born = date.fromisoformat(str(user["birthdate"])[:10])
    today = datetime.now(timezone.utc).date()
    return today.year - born.year - ((today.month, today.day)
                                     < (born.month, born.day))


def take(user: dict, kind: str, site: str, content_b64: str,
         provenance: str = "captured", note: str | None = None,
         condition: str | None = None, intimate_consent: bool = False,
         pdi=None) -> dict:
    """Seal one capture and record that it exists.

    `user` is the row rather than an id, because the age check below has to be
    made from the account's own birthdate and a caller passing an id could pass
    somebody else's.
    """
    user_id = user["id"]
    if kind not in KINDS:
        raise CaptureError(
            f"unknown kind {kind!r}; one of {', '.join(KINDS)}")
    if site not in SITES:
        raise CaptureError(
            f"unknown site {site!r}; one of {', '.join(SITES)}")
    if provenance not in PROVENANCE:
        raise CaptureError(
            f"unknown provenance {provenance!r}; one of "
            f"{', '.join(PROVENANCE)}")

    age = _age_of(user)
    if site in INTIMATE:
        # The hard line. No override, no guardian consent path, no setting.
        # A guardian product that could be talked into storing this image is
        # one whose other guarantees do not matter.
        if age is not None and age < 18:
            raise CaptureError(
                "this app will not store an image of that area for an account "
                "belonging to a minor, under any circumstance. Please contact "
                "a clinician or a paediatric service directly — they can "
                "examine in person, which is the right way to handle this.")
        if not intimate_consent:
            raise CaptureError(
                f"{SITES[site]} needs an explicit confirmation before it is "
                "stored. It will be kept out of anything automatic — no "
                "synthetic agent ever receives it, and it is never folded "
                "into an assembled summary; a clinician opens it deliberately "
                "or not at all.")

    try:
        raw = base64.b64decode(content_b64, validate=True)
    except Exception:
        raise CaptureError("the capture could not be read — it is not "
                           "base64") from None
    if not raw:
        raise CaptureError("the capture is empty")
    if len(raw) > MAX_BYTES:
        raise CaptureError(
            f"that is {len(raw) // (1024 * 1024)}MB; the limit is "
            f"{MAX_BYTES // (1024 * 1024)}MB")

    cleaned, removed = strip_metadata(raw)

    # No vault, no capture. See the module note: the graceful fallback is an
    # unencrypted photograph of somebody's skin on a laptop.
    if pdi is None:
        raise VaultRequired(
            "a photograph of your body is only stored in the encrypted vault, "
            "and this deployment has none configured. Nothing was saved. "
            "Colocation is free — see the hosting options — and everything "
            "else in the app works without it.")

    # And no open store either. The free plan keeps the record in the clear
    # (see `jim/storage.py`); a photograph of somebody's body is the one
    # payload here that does not get to sit there.
    #
    # Checked **after** the vault, deliberately. In a deployment with no PDI
    # at all, telling somebody on the free plan to pay $20 for the vault would
    # be selling what this deployment cannot deliver — Basic would seal it in
    # a vault that does not exist. The absence of a vault is the deeper cause
    # and gets said first.
    #
    # The governing plan is the guardian's when this is a child's account: a
    # parent on Basic bought the vault precisely so their child's record would
    # be in it, and resolving to the child's own (absent) membership would
    # refuse them.
    storage.require(tiers.governing_plan(user_id), "body_image")

    capture_id = db.new_id("cap")
    key = f"jim/{user_id}/{VAULT_SCOPE}/{capture_id}"
    pdi.put(key, base64.b64encode(cleaned).decode())

    conn = db.connect()
    conn.execute(
        "INSERT INTO captures (id, user_id, kind, site, provenance, note,"
        " condition, intimate, vault_key, digest, bytes, stripped,"
        " captured_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (capture_id, user_id, kind, site, provenance, note, condition,
         int(site in INTIMATE), key,
         hashlib.sha256(cleaned).hexdigest(), len(cleaned),
         json.dumps(removed), db.utcnow()))
    conn.commit()
    return read(capture_id)


def read(capture_id: str) -> dict:
    """The record of a capture. **Never the image** — see `content_for_care`."""
    row = db.connect().execute(
        "SELECT * FROM captures WHERE id=?", (capture_id,)).fetchone()
    if row is None:
        raise CaptureError("no such capture")
    d = dict(row)
    d["intimate"] = bool(d["intimate"])
    d["site_label"] = SITES.get(d["site"], d["site"])
    d["stripped"] = json.loads(d["stripped"])
    d["provenance_note"] = PROVENANCE.get(d["provenance"], "")
    d["seen_by_clinician"] = bool(d.get("released_at"))
    return d


def for_user(user_id: str, condition: str | None = None) -> list[dict]:
    sql = "SELECT id FROM captures WHERE user_id=? AND deleted_at IS NULL"
    args: list = [user_id]
    if condition:
        sql += " AND condition=?"
        args.append(condition)
    rows = db.connect().execute(sql + " ORDER BY captured_at DESC",
                                args).fetchall()
    return [read(r["id"]) for r in rows]


def for_agent(user_id: str, condition: str | None = None) -> list[dict]:
    """What a synthetic profile may be told: that a capture exists, and where.

    **Never the image, and there is no argument that changes it.** A model
    that looks at a mole and says *"that looks fine"* has made a diagnosis —
    with no license, no examination and no accountability — to somebody who was
    frightened enough to photograph it. `pdi/gate.py`'s ceiling is the rule:
    *whatever a wrong answer cannot undo.* A missed melanoma cannot be undone
    by the next sentence.

    What the agent gets is enough to be useful in the only way it should be:
    *there is a photograph of your forearm from Tuesday attached to this — a
    clinician should look at it.* That is a routing decision, which is the
    thing an agent may make.

    Intimate sites are omitted entirely rather than summarised, because
    "there is a photograph of their groin" is itself the disclosure.
    """
    out = []
    for cap in for_user(user_id, condition):
        if cap["intimate"]:
            continue
        out.append({k: cap.get(k) for k in AGENT_FIELDS})
    return out


def content_for_care(capture_id: str, pdi=None) -> str:
    """The sealed bytes, for release to a human clinician.

    The only function that returns an image, and it needs the vault — the
    record here holds a key, not a picture. Callers are the referral path and
    the user's own download.
    """
    cap = read(capture_id)
    if pdi is None:
        raise VaultRequired("the image lives in the vault and no vault is "
                            "configured on this deployment")
    content = pdi.get(cap["vault_key"])
    if content is None:
        raise CaptureError("the vault has no record under that key")
    return content


def attach_to_referral(capture_ids: list[str], user_id: str) -> dict:
    """Mark which captures a referral is releasing, and say what is excluded.

    Intimate captures are **not** auto-included. They can be released, but only
    by being named one at a time, which is what `explicit` reports back — a
    summary that swept them in because they happened to match the condition
    would be the product making that decision on somebody's behalf.
    """
    chosen, excluded = [], []
    for cid in capture_ids:
        cap = read(cid)
        if cap["user_id"] != user_id:
            raise CaptureError("that capture belongs to somebody else")
        (excluded if cap["intimate"] else chosen).append(cap)
    return {
        "release": [c["id"] for c in chosen],
        "explicit": [c["id"] for c in excluded],
        "note": ("intimate-site captures are never included automatically — "
                 "release each one deliberately or leave it out"
                 if excluded else None),
    }


def mark_released(capture_id: str) -> dict:
    conn = db.connect()
    conn.execute("UPDATE captures SET released_at=? WHERE id=?",
                 (db.utcnow(), capture_id))
    conn.commit()
    return read(capture_id)


def delete(capture_id: str, user_id: str, pdi=None) -> dict:
    """Remove it. The vault record goes too.

    A tombstone rather than a row delete, so a clinician who was shown
    something can still see that it was withdrawn rather than finding a
    dangling reference — but the bytes are gone from the vault, which is the
    part that matters.
    """
    cap = read(capture_id)
    if cap["user_id"] != user_id:
        raise CaptureError("that capture belongs to somebody else")
    if pdi is not None:
        try:
            pdi.delete(cap["vault_key"])
        except Exception:
            pass          # the tombstone still stands; the vault has its own
    conn = db.connect()
    conn.execute("UPDATE captures SET deleted_at=?, vault_key='' WHERE id=?",
                 (db.utcnow(), capture_id))
    conn.commit()
    return read(capture_id)


def vocabulary() -> dict:
    """Everything a client needs to draw the capture flow, published."""
    return {
        "kinds": KINDS,
        "sites": SITES,
        "intimate": sorted(INTIMATE),
        "provenance": PROVENANCE,
        "max_bytes": MAX_BYTES,
        "vault_required": True,
        "agent_sees": list(AGENT_FIELDS),
        "agent_never_sees": "the image itself, on any plan or setting",
        "minors": "images of intimate areas are refused for accounts "
                  "belonging to under-18s, with no override",
    }
