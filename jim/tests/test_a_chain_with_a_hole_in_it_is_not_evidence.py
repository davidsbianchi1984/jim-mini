"""The audit chain: catalogued, wired, verifiable, and readable by its subject.

    asked     is there a record of what this Guardian did
    mattered  can somebody tell whether that record was edited afterwards

`jim/audit.py` is a port of PDI's chain. A hash-chained log has one failure
mode that matters and it is not a crash: it is a log that looks like evidence
and is not. Four ways that happens, one guard each.

1. **A catalogue nobody writes to.** `ACTIONS` is a list of promises. An
   action named there and recorded nowhere is a reader concluding "this never
   happened" from a table that was never going to say it did. A count is not a
   shelf.
2. **A write nobody catalogued.** The inverse: `record()` accepts an unknown
   action on purpose — dropping the trace would be worse — but it must not
   *ship* that way, because `category()` reports it as `other` and the reading
   door hands the person a row with no description beside it.
3. **A chain that does not actually chain.** Verified by breaking it, not by
   reading the code: edit a row and the verifier must name the sequence
   number.
4. **A chain the subject cannot read.** It is excluded from the export bundle
   and it survives an erase; both are only honest because
   `GET /audit/{user_id}` exists and is scoped to its subject.
"""

from __future__ import annotations

import pathlib
import re

import pytest

from jim import audit, life
from jim.tests.conftest import enroll, user_header

SRC = pathlib.Path(__file__).resolve().parent.parent

#: Source files that talk *about* the catalogue rather than writing to it.
NOT_A_CALL_SITE = {"audit.py"}

#: Actions catalogued for an act that has no call site yet, each with the
#: reason it is named early. Empty is the goal; a row here is a debt with a
#: sentence attached, not a blanket exemption.
NOT_YET_WIRED: dict[str, str] = {}


def _actions_in(call: str) -> list[str]:
    """Every string literal in one `audit.record(...)` call.

    Not just the first: several call sites pick the action with a
    conditional — `"grant.open" if on else "grant.close"` — because a grant
    and its withdrawal are one act with two directions and splitting them
    into two call sites is how the two drift apart. A scan that read only the
    first literal would report the closing half as unwired forever.
    """
    return [m for m in re.findall(r"""["']([a-z_]+\.[a-z_]+)["']""", call)]


def _recorded_actions() -> dict[str, list[str]]:
    """action -> the files that record it, read out of the source."""
    found: dict[str, list[str]] = {}
    for path in sorted(SRC.glob("*.py")):
        if path.name in NOT_A_CALL_SITE:
            continue
        text = path.read_text(encoding="utf-8")
        for start in (m.end() for m in re.finditer(r"audit\.record\(", text)):
            depth, i = 1, start
            while i < len(text) and depth:
                depth += {"(": 1, ")": -1}.get(text[i], 0)
                i += 1
            for action in _actions_in(text[start:i - 1]):
                found.setdefault(action, []).append(path.name)
    return found


def test_every_catalogued_action_is_recorded_somewhere():
    recorded = _recorded_actions()
    missing = sorted(a for a in audit.ACTIONS
                     if a not in recorded and a not in NOT_YET_WIRED)
    assert not missing, (
        "catalogued in jim/audit.py and recorded nowhere: "
        + ", ".join(missing)
        + " — a reader takes an empty audit log as 'this did not happen', so "
          "either wire the call site or move the action to NOT_YET_WIRED "
          "with the reason it is named early.")


def test_every_recorded_action_is_catalogued():
    recorded = _recorded_actions()
    unknown = {a: f for a, f in sorted(recorded.items())
               if a not in audit.ACTIONS}
    assert not unknown, (
        "recorded but not in jim.audit.ACTIONS: "
        + ", ".join(f"{a} ({', '.join(f)})" for a, f in unknown.items())
        + " — record() accepts these rather than losing the trace, but they "
          "read as category 'other' with no description on the audit door. "
          "Give each one a category and a sentence.")


def test_the_catalogue_says_what_each_action_is():
    """A description is what turns a row into something a person can read."""
    thin = sorted(a for a, (cat, desc) in audit.ACTIONS.items()
                  if not cat or len(desc.split()) < 4)
    assert not thin, (
        "catalogued with no usable description: " + ", ".join(thin))


def test_the_chain_records_what_a_person_did_and_verifies(client):
    user_id = enroll(client)
    assert audit.verify()["intact"] is True

    before = len(audit.entries(user_id))
    r = client.put(f"/engaged/{user_id}/permits/what_it_may_read",
                   json={"granted": True})
    assert r.status_code == 200, r.text
    after = audit.entries(user_id)
    assert len(after) == before + 1
    assert after[-1]["action"] == "grant.open"
    assert after[-1]["category"] == "access"
    assert audit.verify()["intact"] is True


def test_an_edited_row_breaks_the_chain_and_the_verifier_says_where(client):
    from jim import db

    user_id = enroll(client)
    audit.record("watch.arm", user_id=user_id, ref="one")
    audit.record("watch.disarm", user_id=user_id, ref="two")
    assert audit.verify()["intact"] is True

    # Reach past the module and rewrite history the way somebody with the
    # database file would. Nothing in the API can do this — that is the point.
    conn = db.connect()
    seq = conn.execute(
        "SELECT seq FROM audit ORDER BY seq DESC LIMIT 1").fetchone()["seq"]
    conn.execute("UPDATE audit SET ref='three' WHERE seq=?", (seq,))
    conn.commit()

    broken = audit.verify()
    assert broken["intact"] is False
    assert broken["broken_at_seq"] == seq


def test_a_deleted_row_breaks_the_chain_too(client):
    from jim import db

    user_id = enroll(client)
    audit.record("watch.arm", user_id=user_id)
    audit.record("watch.trip", user_id=user_id)
    audit.record("alarm.clear", user_id=user_id)
    conn = db.connect()
    rows = conn.execute("SELECT seq FROM audit ORDER BY seq").fetchall()
    victim = rows[-2]["seq"]
    conn.execute("DELETE FROM audit WHERE seq=?", (victim,))
    conn.commit()

    assert audit.verify()["intact"] is False


def test_the_subject_can_read_their_own_rows_and_the_chain_state(client):
    user_id = enroll(client)
    r = client.get(f"/audit/{user_id}")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["count"] == len(body["trail"])
    assert body["integrity"]["intact"] is True
    # The catalogue travels with the rows: an empty list has to be readable as
    # "nothing happened" rather than "nothing is watched".
    catalogued = {a["action"] for a in body["catalogue"]}
    assert catalogued == set(audit.ACTIONS)
    assert any(e["action"] == "account.enroll" for e in body["trail"])
    # None of the three obvious names, because each already carries another
    # type in this API and `test_one_name_one_type_on_the_wire.py` is what
    # said so. A rename back would pass every test in this file and fail there.
    assert not {"entries", "chain", "actions", "acts"} & set(body)


def test_the_audit_door_is_the_subjects_alone(client):
    """Both directions, because a one-way check passes on a broken gate."""
    first = enroll(client)
    first_token = client.headers["authorization"].split()[-1]
    second = enroll(client)          # becomes the client's default caller
    assert client.get(f"/audit/{first}").status_code == 403
    r = client.get(f"/audit/{second}", headers=user_header(first_token))
    assert r.status_code == 403
    assert client.get("/audit/usr_nobody").status_code == 404


def test_an_erase_keeps_the_chain_and_the_door_still_opens(client):
    user_id = enroll(client)
    client.put(f"/engaged/{user_id}/permits/what_it_may_read",
               json={"granted": True})
    kept = len(audit.entries(user_id))
    assert kept

    life.delete_user_data(user_id)

    rows = audit.entries(user_id)
    assert len(rows) == kept + 1
    assert rows[-1]["action"] == "account.erase"
    assert audit.verify()["intact"] is True
    assert "audit" in life.ERASE_KEEPS


def test_the_export_bundle_leaves_the_chain_to_its_own_door(client):
    user_id = enroll(client)
    bundle = life.export_user_data(user_id)
    assert "audit" not in bundle["tables"], (
        "the audit chain is a person's record *about* them, not a table of "
        "theirs — it is read at GET /audit/{user_id} so the two ends stay "
        "symmetrical with the erase, which keeps it")


def test_category_is_derived_not_stored(client):
    """The stored fields are fixed so the catalogue can grow forever.

    If `category` were written into the row, every enrichment of `ACTIONS`
    would either break existing hashes or leave old rows describing
    themselves with a word the catalogue no longer uses. So the column must
    not exist, and the value must arrive on the way out.
    """
    from jim import db

    user_id = enroll(client)
    audit.record("watch.arm", user_id=user_id)
    columns = {r["name"] for r in
               db.connect().execute("PRAGMA table_info(audit)").fetchall()}
    assert "category" not in columns
    assert columns == {"seq", "user_id", "action", "ref", "at",
                       "prev_hash", "hash"}
    assert audit.entries(user_id)[-1]["category"] == "safety"


@pytest.mark.parametrize("action", sorted(audit.ACTIONS))
def test_every_action_resolves_to_a_real_category(action):
    assert audit.category(action) == audit.ACTIONS[action][0]
    assert audit.category(action) in {"safety", "money", "access", "life"}
