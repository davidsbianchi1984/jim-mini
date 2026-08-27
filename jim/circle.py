"""Your circle: the people you let in, and the surfaces that are yours.

The Guardian watches over one person; this file is about the people
around them — on the person's own terms, three surfaces sharing one idea:

**Feature switches.** A small named set, per user, default on. The point
is not the toggle — it is that everything downstream *refuses by naming
the switch*, so "why can't they message me" always has an answer, and
the answer is theirs.

**Messages.** JIM has no friendship graph, so the consent record is
built here and kept deliberately thin: an invitation is one direction,
two directions make contacts, and either side deleting theirs closes the
door for both — consent that only one person can end is not consent.
Words travel between contacts only, one thread per pair, and words
already exchanged survive the circle ending: they belong to both people.
Nothing leaves this deployment; there is no relay to a cloud.

**The homepage sandbox.** An editable page like the old MySpace — a
headline, an about, a theme, links, top friends — stored as one
validated document. A sandbox in the strict sense: colors must be hex,
links must be http(s), everything else is plain text, and top friends
must be actual contacts. There is structurally nowhere to put a script,
which is what lets the page be shown at all. Unlike QRME's, the page is
never public: only a signed-in neighbour on this deployment may look,
and only while the homepage switch is on.
"""

from __future__ import annotations

import json
import re

from . import db, i18n

#: The switches that exist. Adding one is a decision made here, where the
#: defaults live, rather than a string that quietly becomes load-bearing.
FEATURES = {
    "messaging": True,     # contacts can message this user
    "homepage": True,      # the homepage is visible to neighbours
}

_HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
_MAX_LINKS = 8
_MAX_TOP_FRIENDS = 8


class CircleError(ValueError):
    pass


def _display_name(user_id: str) -> str | None:
    row = db.connect().execute(
        "SELECT display_name FROM users WHERE id=?", (user_id,)).fetchone()
    return row["display_name"] if row else None


def _exists(user_id: str) -> bool:
    return _display_name(user_id) is not None


# -- feature switches ---------------------------------------------------------

def features_of(user_id: str) -> dict:
    out = dict(FEATURES)
    for row in db.connect().execute(
            "SELECT feature, enabled FROM user_features WHERE user_id=?",
            (user_id,)).fetchall():
        if row["feature"] in out:
            out[row["feature"]] = bool(row["enabled"])
    return out


def set_feature(user_id: str, feature: str, enabled: bool) -> dict:
    if feature not in FEATURES:
        raise CircleError(i18n.fill(i18n.UNKNOWN_FEATURE_SWITCHES,
                                    got=repr(feature),
                                    choices=", ".join(sorted(FEATURES))))
    conn = db.connect()
    conn.execute(
        "INSERT INTO user_features (user_id, feature, enabled, updated_at)"
        " VALUES (?,?,?,?) ON CONFLICT (user_id, feature) DO UPDATE SET"
        " enabled=excluded.enabled, updated_at=excluded.updated_at",
        (user_id, feature, 1 if enabled else 0, db.utcnow()))
    conn.commit()
    return features_of(user_id)


def enabled(user_id: str, feature: str) -> bool:
    return features_of(user_id).get(feature, False)


# -- the circle itself --------------------------------------------------------

def _mutual(a: str, b: str) -> bool:
    """Contacts, deliberately mutual: either side removing their direction
    closes the door for both."""
    conn = db.connect()
    one = conn.execute(
        "SELECT 1 FROM circle_invites WHERE user_id=? AND other_id=?",
        (a, b)).fetchone()
    other = conn.execute(
        "SELECT 1 FROM circle_invites WHERE user_id=? AND other_id=?",
        (b, a)).fetchone()
    return one is not None and other is not None


def invite(user_id: str, other_id: str) -> dict:
    """One direction. The same call accepts: inviting somebody who already
    invited you is the second direction, and now you are contacts."""
    if other_id == user_id:
        raise CircleError("you are already in your own circle")
    if not _exists(other_id):
        raise CircleError("nobody by that id lives on this deployment")
    conn = db.connect()
    conn.execute(
        "INSERT OR IGNORE INTO circle_invites (user_id, other_id,"
        " created_at) VALUES (?,?,?)", (user_id, other_id, db.utcnow()))
    conn.commit()
    return {"other_id": other_id,
            "other_name": _display_name(other_id),
            "state": "contacts" if _mutual(user_id, other_id) else "invited"}


def leave(user_id: str, other_id: str) -> dict:
    """Delete your direction. Their invitation is theirs to keep or drop —
    what ends immediately is the mutuality, and with it the messaging."""
    conn = db.connect()
    conn.execute(
        "DELETE FROM circle_invites WHERE user_id=? AND other_id=?",
        (user_id, other_id))
    conn.commit()
    return {"other_id": other_id, "state": "left"}


def circle_of(user_id: str) -> dict:
    """Contacts (mutual), who is waiting on you, and who you are waiting
    on — names included, so a list is a list without n lookups."""
    conn = db.connect()
    mine = {r["other_id"] for r in conn.execute(
        "SELECT other_id FROM circle_invites WHERE user_id=?",
        (user_id,)).fetchall()}
    theirs = {r["user_id"] for r in conn.execute(
        "SELECT user_id FROM circle_invites WHERE other_id=?",
        (user_id,)).fetchall()}

    def _named(ids):
        return [{"user_id": uid, "display_name": _display_name(uid)}
                for uid in sorted(ids)]

    return {"contacts": _named(mine & theirs),
            "invited_me": _named(theirs - mine),
            "awaiting": _named(mine - theirs)}


# -- messages -----------------------------------------------------------------

def _pair(a: str, b: str) -> tuple[str, str]:
    return (a, b) if a < b else (b, a)


def send_message(sender_id: str, recipient_id: str, body: str) -> dict:
    if sender_id == recipient_id:
        raise CircleError("that would be a note to yourself; the journal "
                          "is better at those")
    if not (body or "").strip():
        raise CircleError("a message needs words")
    if not _mutual(sender_id, recipient_id):
        raise CircleError("messages travel inside your circle; invite "
                          "them first, and they must invite you back")
    if not enabled(recipient_id, "messaging"):
        raise CircleError("that person has messaging turned off")
    if not enabled(sender_id, "messaging"):
        raise CircleError("your messaging is turned off; turn the switch "
                          "back on to send")
    low, high = _pair(sender_id, recipient_id)
    conn = db.connect()
    message_id = db.new_id("msg")
    conn.execute(
        "INSERT INTO circle_messages (id, low_id, high_id, sender_id,"
        " body, sent_at) VALUES (?,?,?,?,?,?)",
        (message_id, low, high, sender_id, body.strip(), db.utcnow()))
    conn.commit()
    return dict(conn.execute("SELECT * FROM circle_messages WHERE id=?",
                             (message_id,)).fetchone())


def thread(user_id: str, other_id: str) -> list[dict]:
    """One conversation, read by either side — readable even after the
    circle ends, because words already exchanged belong to both people.
    Only *new* words need the circle back."""
    low, high = _pair(user_id, other_id)
    return [dict(r) for r in db.connect().execute(
        "SELECT * FROM circle_messages WHERE low_id=? AND high_id=?"
        " ORDER BY sent_at", (low, high)).fetchall()]


def threads(user_id: str) -> list[dict]:
    rows = db.connect().execute(
        "SELECT low_id, high_id, MAX(sent_at) AS last_at, COUNT(*) AS n"
        " FROM circle_messages WHERE low_id=? OR high_id=?"
        " GROUP BY low_id, high_id ORDER BY last_at DESC",
        (user_id, user_id)).fetchall()
    out = []
    for r in rows:
        other = r["high_id"] if r["low_id"] == user_id else r["low_id"]
        out.append({"other_id": other, "other_name": _display_name(other),
                    "messages_count": r["n"], "last_at": r["last_at"]})
    return out


# -- the homepage sandbox -----------------------------------------------------

_DEFAULT_DOC = {
    "headline": "",
    "about": "",
    "theme": {"bg": "#10251c", "accent": "#2fbf8f"},
    "links": [],
    "top_friends": [],
}


def _validate_doc(user_id: str, doc: dict) -> dict:
    """The sandbox's walls. Everything that comes back is safe to show a
    neighbour; anything that is not text, a hex color, an http(s) link or
    an actual contact's id is refused with the wall's own sentence."""
    out = dict(_DEFAULT_DOC)
    out["headline"] = str(doc.get("headline") or "")[:120]
    out["about"] = str(doc.get("about") or "")[:2000]

    theme = doc.get("theme") or {}
    for slot in ("bg", "accent"):
        value = theme.get(slot) or _DEFAULT_DOC["theme"][slot]
        if not _HEX.match(str(value)):
            raise CircleError("a theme color is a hex code like #10251c")
    out["theme"] = {"bg": theme.get("bg") or _DEFAULT_DOC["theme"]["bg"],
                    "accent": theme.get("accent")
                    or _DEFAULT_DOC["theme"]["accent"]}

    links = doc.get("links") or []
    if len(links) > _MAX_LINKS:
        raise CircleError(i18n.fill(i18n.MAX_LINKS, max=_MAX_LINKS))
    clean_links = []
    for link in links:
        url = str((link or {}).get("url") or "")
        label = str((link or {}).get("label") or "")[:80]
        if not url.startswith(("http://", "https://")):
            raise CircleError("links start with http:// or https://")
        clean_links.append({"label": label or url, "url": url[:500]})
    out["links"] = clean_links

    tops = list(doc.get("top_friends") or [])[: _MAX_TOP_FRIENDS + 1]
    if len(tops) > _MAX_TOP_FRIENDS:
        raise CircleError(i18n.fill(i18n.TOP_FRIENDS_MAX,
                                    max=_MAX_TOP_FRIENDS))
    for friend_id in tops:
        if not _mutual(user_id, str(friend_id)):
            raise CircleError("top friends are chosen from your actual "
                              "contacts")
    out["top_friends"] = [str(f) for f in tops]
    return out


def set_homepage(user_id: str, doc: dict) -> dict:
    clean = _validate_doc(user_id, doc)
    conn = db.connect()
    conn.execute(
        "INSERT INTO user_homepages (user_id, doc, updated_at)"
        " VALUES (?,?,?) ON CONFLICT (user_id) DO UPDATE SET"
        " doc=excluded.doc, updated_at=excluded.updated_at",
        (user_id, json.dumps(clean), db.utcnow()))
    conn.commit()
    return homepage(user_id, viewer_is_owner=True)


def homepage(user_id: str, viewer_is_owner: bool = False) -> dict:
    """The page, for a signed-in neighbour. The owner always sees their
    own sandbox — it is theirs to edit; only *showing* it is what the
    switch governs."""
    if not viewer_is_owner and not enabled(user_id, "homepage"):
        raise CircleError("this homepage is not shared")
    conn = db.connect()
    row = conn.execute("SELECT * FROM user_homepages WHERE user_id=?",
                       (user_id,)).fetchone()
    doc = json.loads(row["doc"]) if row else dict(_DEFAULT_DOC)
    tops = []
    for friend_id in doc.get("top_friends", []):
        name = _display_name(friend_id)
        if name is not None:
            tops.append({"user_id": friend_id, "display_name": name})
    return {"user_id": user_id, "display_name": _display_name(user_id),
            "headline": doc["headline"], "about": doc["about"],
            "theme": doc["theme"], "links": doc["links"],
            "top_friends": tops, "editable": viewer_is_owner}


# -- the view -----------------------------------------------------------------

def view(user_id: str, lang: str) -> dict:
    """Everything the Circle surface renders — labels included, in the
    reader's language, because no client of this route has a translation
    table of its own."""
    return {
        "features": features_of(user_id),
        "circle": circle_of(user_id),
        "threads": threads(user_id),
        "homepage": homepage(user_id, viewer_is_owner=True),
        "labels": i18n.circle_labels(lang),
        "note": i18n.circle_text("kept_here", lang),
    }
