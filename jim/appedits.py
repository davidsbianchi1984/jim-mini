"""App edits — a person's proposed change to the app itself, held at apply.

The owner's ask: users (and, when this seam is lifted into QRME, synthetic
profiles) can edit the app — with an assistant that writes code, right in the
widget screen — and have their edits ride the next version. Two lanes:

* **Their own server** (``JIM_SELF_HOSTED=1``): free rein. An edit is approved
  on arrival; nobody stands between the person and their own machine.
* **The hosted cloud** (the default): an edit is **held** for company oversight
  to approve or reject, and only an approved one is queued.

## Held at apply, in both lanes

This seam never writes to the running code and never deploys. An approved edit
is *queued to ride the next publish-merge* — the merge itself stays a reviewed
human step, the same way the 911 dialer holds its send and the mailbox holds
every message for a person. :func:`posture` says so out loud (``apply_wired``
is False). Free rein on a self-hosted server means no approval gate, not an
unattended write to a live server from inside the app.

## The assistant writes, the menu chooses the model

:func:`draft` has a language model compose the change from the person's
instruction — the coding assistant. Which model is the person's choice from
their region's loadout (:mod:`jim.loadouts`): the platform's Anthropic key by
default during beta, or a key they bring. The draft lands as a proposal like any
other and goes through the same lane.
"""

from __future__ import annotations

import json
import os
import threading

from . import audit, corpus, db, i18n, llm, loadouts

LANES = ("self_hosted", "cloud")
STATES = ("proposed", "approved", "rejected")
_TRUTHY = {"1", "true", "yes", "on"}

#: How many drafts may be in the box at once, and which are. A box run
#: pins a worker thread for minutes; two at a time keeps every other door
#: — the safety paths above all — answering.
BOX_SLOTS = 2
_SLOTS = threading.BoundedSemaphore(BOX_SLOTS)
_IN_FLIGHT: set[str] = set()
_FLIGHT_LOCK = threading.Lock()


def lane() -> str:
    return ("self_hosted"
            if os.environ.get("JIM_SELF_HOSTED", "").strip().lower() in _TRUTHY
            else "cloud")


def posture() -> dict:
    from . import workroom
    which = lane()
    return {
        "lane": which,
        # Whether a drafted edit can be tried in the assistant's box on this
        # host (jim/workroom.py): all four walls or nothing.
        "box_available": workroom.available()[0],
        "free_rein": which == "self_hosted",
        "held_for_approval": which == "cloud",
        # The honest seam: nothing here applies a change to running code or
        # deploys. An approved edit is queued for the next publish-merge, and
        # that merge is a reviewed human step.
        "apply_wired": False,
        "note": ("on your own server your edits are approved as they arrive; "
                 "on the hosted cloud they are held for company oversight to "
                 "approve. Either way an approved edit is queued to ride the "
                 "next publish-merge — this never writes to the running app or "
                 "deploys on its own."),
    }


def _public(r: dict, language: str = i18n.DEFAULT) -> dict:
    from . import workroom
    return {"id": r["id"], "title": r["title"], "description": r["description"],
            "target": r["target"], "patch": r["patch"], "model": r["model"],
            "lane": r["lane"], "state": r["state"], "note": r["note"],
            "decided_at": r["decided_at"], "created_at": r["created_at"],
            # What the assistant's box made of it, or null when never tried;
            # its sentence, if any, in the reader's language.
            "box": workroom.summary(workroom.loads(r.get("box")), language)}


def _row(edit_id: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM app_edits WHERE id=?", (edit_id,)).fetchone()
    if row is None:
        raise ValueError("no such app edit")
    return dict(row)


def propose(user_id: str, *, title: str, description: str, target: str = "",
            patch: str = "", model: str = "") -> dict:
    """File a proposed edit into the lane this deployment runs."""
    title = (title or "").strip()
    description = (description or "").strip()
    if not title:
        raise ValueError("an app edit needs a title")
    if not description:
        raise ValueError("an app edit needs a description of the change")
    which = lane()
    state = "approved" if which == "self_hosted" else "proposed"
    now = db.utcnow()
    eid = db.new_id("aed")
    conn = db.connect()
    conn.execute(
        "INSERT INTO app_edits (id, user_id, title, description, target, patch,"
        " model, lane, state, note, decided_by, decided_at, created_at,"
        " updated_at) VALUES (?,?,?,?,?,?,?,?,?, '', ?, ?, ?, ?)",
        (eid, user_id, title, description, (target or "").strip(),
         patch or "", (model or "").strip(), which, state,
         "self-hosted" if state == "approved" else None,
         now if state == "approved" else None, now, now))
    conn.commit()
    audit.record("appedit.proposed", user_id=user_id, ref=title[:80])
    if state == "approved":
        audit.record("appedit.approved", user_id=user_id,
                     ref=f"{title[:60]} (self-hosted, free rein)")
    return _public(_row(eid))


def _system(target: str) -> str:
    where = f" The change is to: {target}." if target else ""
    return ("You are a careful software engineer making a change to the "
            "JIM-mini app on the person's behalf." + where + " Write the "
            "change as a git-style unified diff (--- a/path, +++ b/path, @@ "
            "hunks) against the repository's files, so it can be tried in a "
            "box before a person reads it; explain the change in two "
            "sentences above the diff. Keep it minimal, and never touch "
            "safety, consent, or billing paths — those need a human. Plain "
            "text only.")


def _again(user_id: str, model_choice: str):
    """The assistant asked once more, with what the tests said. Answers
    ``(patch, who)`` so the round records its author; a degraded answer —
    the stub standing in for a provider that did not answer — is no
    revision at all, so the draft on file is never replaced by stub text."""
    def revise(patch: str, output: str) -> tuple[str, str]:
        system = ("You are a careful software engineer. Your earlier diff was "
                  "tried in a box and its tests failed. Answer with a revised "
                  "git-style unified diff against the ORIGINAL files — the "
                  "whole change again, not a diff of your diff — and nothing "
                  "else after the two-sentence explanation.")
        prompt = (f"Your diff:\n\n{patch}\n\nWhat the tests said:\n\n"
                  f"{output[-4000:]}")
        if model_choice == "auto":
            gen = llm.generate_for_user(user_id, system, prompt,
                                        source="appedit")
            if gen.get("degraded"):
                return "", gen["provider"]
            return gen["text"], gen["provider"]
        provider = llm.get_provider(choice=model_choice)
        text = provider.generate(system, prompt)
        used = getattr(provider, "answered_by", None) or model_choice
        corpus.capture(user_id, system, prompt, text, used, source="appedit")
        return text, used
    return revise


def box(user_id: str, edit_id: str, *, model: str = "",
        language: str = i18n.DEFAULT) -> dict:
    """Try a drafted edit in the assistant's box (jim/workroom.py): the
    diff applied to a copy of the tree, the tests it names run inside four
    walls, the assistant asked again on a red run up to MAX_ROUNDS tries in
    all, and every round filed beside the diff for oversight. The box
    decides nothing: an approved edit still rides the next publish-merge.

    Only an edit still awaiting a decision is tried — or, on a self-hosted
    server, the owner's own approved one, since there the owner is the
    oversight — so a diff oversight approved is never rewritten under it.
    One edit is in the box once at a time, and ``BOX_SLOTS`` at most."""
    from . import workroom
    try:
        row = _row(edit_id)
    except ValueError:
        row = None
    # Somebody else's edit reads as no edit: the box is the owner's to ask.
    if row is None or row["user_id"] != user_id:
        raise ValueError("no such edit")
    if row["state"] == "rejected" or (
            row["state"] == "approved" and row["lane"] != "self_hosted"):
        raise ValueError("this app edit is already decided")
    ok, why = workroom.available()
    if not ok:
        audit.record("appedit.box_refused", user_id=user_id, ref=edit_id)
        raise ValueError(why)
    choice = (model or "").strip() or "auto"
    if not loadouts.allowed(user_id, choice):
        raise ValueError("that model is not on the menu for your region")
    with _FLIGHT_LOCK:
        if edit_id in _IN_FLIGHT:
            raise ValueError("that edit is already in the box")
        if not _SLOTS.acquire(blocking=False):
            raise ValueError("the assistant's box is busy, so try again in a moment")
        _IN_FLIGHT.add(edit_id)
    try:
        got = workroom.iterate(row["patch"], row["target"],
                               _again(user_id, choice))
        conn = db.connect()
        # Optimistic: the row must still be the one read above. A decision
        # taken while the box ran wins, and the run is filed as refused.
        n = conn.execute(
            "UPDATE app_edits SET box=?, patch=?, model=?, updated_at=?"
            " WHERE id=? AND state=? AND patch=?",
            (json.dumps(got), got["patch"],
             got.get("model") or row["model"], db.utcnow(),
             edit_id, row["state"], row["patch"])).rowcount
        conn.commit()
    finally:
        with _FLIGHT_LOCK:
            _IN_FLIGHT.discard(edit_id)
            _SLOTS.release()
    if n == 0:
        audit.record("appedit.box_refused", user_id=user_id, ref=edit_id)
        raise ValueError("this app edit was decided while the box was running")
    if got["status"] in ("unapplied", "refused"):
        audit.record("appedit.box_refused", user_id=user_id, ref=edit_id)
    else:
        audit.record("appedit.boxed", user_id=user_id,
                     ref=f"{edit_id}:{got['status']}")
    return _public(_row(edit_id), language)


def draft(user_id: str, *, target: str = "", instruction: str,
          model: str = "") -> dict:
    """The coding assistant: have a model write the change from the person's
    instruction, then file it as a proposal in the deployment's lane. The
    model is the person's pick from their region's loadout."""
    instruction = (instruction or "").strip()
    if not instruction:
        raise ValueError("the assistant needs an instruction to draft from")
    choice = (model or "").strip() or "auto"
    if not loadouts.allowed(user_id, choice):
        raise ValueError("that model is not on the menu for your region")
    system = _system((target or "").strip())
    if choice == "auto":
        gen = llm.generate_for_user(user_id, system, instruction,
                                    source="appedit")
        text, used = gen["text"], gen["provider"]
    else:
        provider = llm.get_provider(choice=choice)
        text = provider.generate(system, instruction)
        used = getattr(provider, "answered_by", None) or choice
        corpus.capture(user_id, system, instruction, text, used,
                       source="appedit")
    audit.record("appedit.drafted", user_id=user_id, ref=used)
    title = instruction.splitlines()[0][:80]
    return propose(user_id, title=title, description=instruction,
                   target=target, patch=text, model=used)


def mine(user_id: str, limit: int = 50,
         language: str = i18n.DEFAULT) -> list[dict]:
    rows = db.connect().execute(
        "SELECT * FROM app_edits WHERE user_id=? ORDER BY created_at DESC"
        " LIMIT ?", (user_id, int(limit))).fetchall()
    return [_public(dict(r), language) for r in rows]


def queue(language: str = i18n.DEFAULT) -> dict:
    """Oversight's view: what awaits a decision, and what is approved and
    queued to ride the next publish-merge."""
    conn = db.connect()
    awaiting = [_public(dict(r), language) for r in conn.execute(
        "SELECT * FROM app_edits WHERE state='proposed' ORDER BY created_at"
    ).fetchall()]
    queued = [_public(dict(r), language) for r in conn.execute(
        "SELECT * FROM app_edits WHERE state='approved' ORDER BY decided_at"
    ).fetchall()]
    return {"awaiting": awaiting, "queued": queued, "posture": posture()}


def decide(edit_id: str, action: str, *, by: str, note: str = "",
           language: str = i18n.DEFAULT) -> dict:
    """Company oversight's word on a held edit."""
    row = _row(edit_id)
    if row["state"] != "proposed":
        raise ValueError("this app edit is not awaiting a decision")
    if action not in ("approve", "reject"):
        raise ValueError("a decision on an app edit is approve or reject")
    state = "approved" if action == "approve" else "rejected"
    now = db.utcnow()
    conn = db.connect()
    conn.execute(
        "UPDATE app_edits SET state=?, note=?, decided_by=?, decided_at=?,"
        " updated_at=? WHERE id=?",
        (state, (note or "").strip(), by, now, now, edit_id))
    conn.commit()
    # Two literals, not an f-string: the audit catalogue's guard reads the
    # call sites for the names it promises, and a name built at runtime is a
    # name it cannot see.
    audit.record("appedit.approved" if state == "approved" else "appedit.rejected",
                 user_id=row["user_id"], ref=row["title"][:80])
    return _public(_row(edit_id), language)
