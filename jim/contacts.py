"""Who this person knows, and how a call comes to have a name on it.

The field ask, in its own words: *the person they may be talking to may
already be in their friends list, and an agent monitoring you making a phone
call outbound will know who you're calling the moment you're calling, so all
of that can be set up as it's happening.* And the other half of it: *they
don't have their friends list — but if the other person had that user stored
as well, the agent will know who they're talking to and reach out to that
individual agent behind the scenes.*

    asked     who is on the other end of this call
    mattered  did we learn it from something this person already had

## It arrives by a grant, not by typing

Nobody retypes their address book into a second app. The book comes from the
device, synced under the ``contacts`` source, the way a wearable's readings
and a calendar already arrive — *allowing the agent access to Contacts, and
messages, and phone*. :data:`SOURCE` is the consent, :func:`sync` is the only
way rows get in, and :func:`allowed` is the only door to reading them.

That grant is not this product's alone. The same access belongs to synthetic
profiles in QRME, and plenty of people hold one of the two products and not
the other — so the shape is declared in both rather than owned by whichever
one happened to need it first.

## This is the grant that is mostly about other people

Every other source is about the person granting it: their pulse, their
calendar, their spending. **An address book is almost entirely somebody
else** — a few hundred people who never chose this product, cannot see that
it holds their number, and were not asked.

That is `touches_others` at its maximum, and it is the same argument
:mod:`jim.monitors` makes about a camera bolted to a hall. So the grant is
off until somebody turns it on, it says in the person's own words what it
takes, and withdrawing it does not merely stop the syncing —
:func:`withdrawn` drops the book. A copy left behind after somebody said stop
is the whole objection, made real.

## The far side's number is still not stored

:mod:`jim.oncall` reads the far side's number for one thing — which language
to speak the notice in — and drops it. That stays exactly true. Recognition
does not write: :func:`whose` asks a question of the book and returns a row
or nothing, and a call from a number nobody granted leaves precisely as
little behind as it did before this module existed. Nothing a call carries
is ever written here.

## Why the numbers are not hashed

They are stored as digits. A phone number is a ten-digit space and a laptop
walks all of it in minutes, so hashing this column would buy nothing and
would say it had bought something, which is worse than storing it plainly.
What actually protects the book is that it never leaves the deployment and
that it belongs to the person whose book it is.

The stored form is the last nine digits, which is what makes ``+1 555-0142``
and ``(555) 0142`` the same person across the ways anybody writes a number
down. Two numbers in different countries can share a nine-digit tail; the
consequence is a wrong **name** on a call, and never a wrong link, because
opening a liaison needs the contact to carry an account *and* be a mutual
contact *and* hold the permit. A name is worth getting right, so
:func:`whose` is exact within that book and nothing here guesses further.

## Most of the book has no guardian in it

``jim_user_id`` is set only where a contact also holds an account here, and
it is NULL for nearly every row. That is not a gap to be filled in later — it
is the ordinary case, and the one this table exists to serve properly. A
mother who will never install anything is still somebody a call can be filed
under, and :mod:`jim.schedule` is where what the call left behind goes.
"""

from __future__ import annotations

import re

from . import db, i18n, life

#: The consent this whole module lives behind. One of `models.Source`, granted
#: and withdrawn where every other source is, so a person reads *what the
#: agent may see* in one list rather than hunting for the address book in a
#: screen of its own.
SOURCE = "contacts"

#: How much of a number is kept. Enough to be specific across the ways people
#: write numbers down, and short enough that a country code or a trunk zero
#: does not stop a match.
TAIL = 9


class NoSuchContact(ValueError):
    """No contact by that id, for this person."""




def digits(number: str) -> str:
    """A number reduced to what recognising it needs.

    Punctuation, spaces and the leading ``+`` all go; the last :data:`TAIL`
    digits stay. Everything that reaches this table or asks a question of it
    comes through here, so the shape somebody typed never decides whether
    their mother is recognised.
    """
    only = re.sub(r"\D", "", number or "")
    return only[-TAIL:]


class NotGranted(RuntimeError):
    """Refused: this person has not let anything see their contacts."""


#: Refused because the grant is off. Names what it would reach rather than the
#: source's identifier — `contacts` is a word in a config file, and *the
#: people in your phone* is the thing somebody is deciding about.
NOT_GRANTED = ("nothing here can see the people in your phone: turn on "
               "contacts in what the agent may see. It is off until you do, "
               "because most of what is in there is somebody else")


def allowed(user_id: str) -> None:
    """The chokepoint. Refuse unless this person granted the source.

    One function, so the book cannot be read by a path that forgot to ask —
    the argument :func:`jim.oncall.may_listen` makes for a call and
    :func:`jim.monitors.may_sense` makes for a camera.
    """
    for row in life.sources(user_id):
        if row["source"] == SOURCE and row["consented"]:
            return
    raise NotGranted(NOT_GRANTED)


def sync(user_id: str, entries: list[dict]) -> dict:
    """Replace the book with what the device has.

    The only way rows get in. A replace rather than a merge, because the
    device's book is the truth and a merge would quietly keep people the
    person deleted from their phone months ago — which is the copy-left-
    behind problem in slow motion.

    Each entry is ``{"name": ..., "number": ..., "jim_user_id": ...}``. Ones
    that carry too little number to recognise anybody are skipped rather than
    refused: a real address book has half-rows in it, and rejecting the whole
    sync over one of them would leave the person with no book at all.
    """
    allowed(user_id)
    seen: dict[str, dict] = {}
    skipped = 0
    for entry in entries:
        name = (entry.get("name") or "").strip()
        tail = digits(entry.get("number") or "")
        if not name or len(tail) < 7:
            skipped += 1
            continue
        # Last one wins, and the dict is what makes a device's duplicate rows
        # one person here rather than a conflict.
        seen[tail] = {"name": name, "jim_user_id": entry.get("jim_user_id")}
    conn = db.connect()
    conn.execute("DELETE FROM contacts WHERE user_id=?", (user_id,))
    now = db.utcnow()
    conn.executemany(
        "INSERT INTO contacts (id, user_id, name, digits, jim_user_id,"
        " added_at) VALUES (?,?,?,?,?,?)",
        [(db.new_id("con"), user_id, row["name"], tail, row["jim_user_id"],
          now) for tail, row in seen.items()])
    conn.commit()
    return {"held": len(seen), "skipped": skipped}


def withdrawn(user_id: str) -> dict:
    """The grant came off. Drop the book.

    Not "stop syncing" — drop it. A copy kept after somebody said stop is the
    entire objection to holding other people's contact details in the first
    place, and it is the one part of this that has to be true rather than
    intended. Called from wherever the source is set, so a person turning the
    switch off does not also have to find a second control.
    """
    conn = db.connect()
    conn.execute("DELETE FROM contacts WHERE user_id=?", (user_id,))
    conn.commit()
    return {"held": 0}


def _seen(row) -> dict:
    """A contact as anybody reads it: a name, and whether they have a
    guardian. The digits do not come back out.

    A book that hands its numbers back on every read is a book that ends up
    in a log, in a screenshot and in a support ticket. Nothing in this
    product needs to display them — the phone already has them — so nothing
    here returns them.
    """
    return {"id": row["id"], "name": row["name"],
            "has_guardian": row["jim_user_id"] is not None,
            "added_at": row["added_at"]}


def one(user_id: str, contact_id: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM contacts WHERE id=? AND user_id=?",
        (contact_id, user_id)).fetchone()
    if row is None:
        raise NoSuchContact("no such contact")
    return _seen(row)


def book(user_id: str) -> list[dict]:
    """Everybody in the synced book, by name."""
    allowed(user_id)
    rows = db.connect().execute(
        "SELECT * FROM contacts WHERE user_id=? ORDER BY name COLLATE NOCASE",
        (user_id,)).fetchall()
    return [_seen(r) for r in rows]


def whose(user_id: str, number: str | None) -> dict | None:
    """Which of this person's own contacts a number belongs to, if any.

    The recognition door, and the only one. It takes a number and returns a
    row of this person's book or nothing at all — it never writes, so a
    number that matches nobody leaves exactly as little behind as it did
    before this module existed.
    """
    if not number:
        return None
    try:
        allowed(user_id)
    except NotGranted:
        # A phone call is not the place to raise about a grant. Without it
        # the call simply has no name on it, which is what it had before.
        return None
    tail = digits(number)
    if len(tail) < 7:
        return None
    row = db.connect().execute(
        "SELECT * FROM contacts WHERE user_id=? AND digits=?",
        (user_id, tail)).fetchone()
    return dict(row) if row else None


def guardian_of(user_id: str, number: str | None) -> str | None:
    """The account behind a number, where this person's book names one.

    What :mod:`jim.oncall` asks at dial time before trying to open a link.
    Two conditions, both from records already held: the number is in **this**
    person's book, and the row they wrote says who it is here.
    """
    row = whose(user_id, number)
    return row["jim_user_id"] if row else None
