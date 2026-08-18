"""One book, one withdrawal, and the vault question asked in one place.

The contacts round shipped the book and left the custody decision for later:
every row went into the local `contacts` table whatever the account was paying
for. `jim/storage.py` had already settled how this product answers that
question, and it answers it about the **plan** rather than about whether the
deployment happens to have a vault configured — a free account on a PDI-backed
deployment does not get its journal, or its check-in notes, or now its address
book sealed into a vault it is not paying for and cannot hold a key to.

    asked     where does the book live
    mattered  is there ever more than one of it

## What these hold

**Writes are plan-gated; reads and deletions are not.** That asymmetry is
`vault_for`'s own, and the address book is the payload that makes the cost of
getting it wrong plainest. Somebody on Basic for a year has a sealed book. If
they move to Free and withdraw the grant, a withdrawal that only cleared the
side their *current* plan points at would leave a few hundred other people's
names and numbers in a vault, after the one person who could have said stop
did. That is the copy-kept-after-stop objection wearing a billing change as a
disguise.

**Never both.** A plan change between two syncs is the ordinary way to end up
with two books that disagree about who somebody knows, so `sync` clears both
custodies before writing to either.

**A sealed book with no vault raises.** *You know nobody* and *I could not
open your book* are different sentences and only one of them is true; the
second one is the one that has to reach the caller, because the first is the
answer that quietly puts the wrong name — or no name — on a phone call.
"""

from __future__ import annotations

import json

import pytest

from jim import contacts, db, life, storage
from jim.tests.conftest import enroll

MOM = "+1 555 010 2233"


class Vault:
    """A PDI stand-in that keeps what it is given and says what it was asked.

    Records the calls as well as the contents: half of what these tests check
    is *that the vault was reached at all* on a path where forgetting to reach
    it is the defect.
    """

    def __init__(self):
        self.records: dict[str, str] = {}
        self.deleted: list[str] = []

    def put(self, key, value):
        self.records[key] = value

    def get(self, key):
        return self.records.get(key)

    def delete(self, key):
        self.deleted.append(key)
        return self.records.pop(key, None) is not None


def granted(client):
    user_id = enroll(client)
    life.set_source(user_id, contacts.SOURCE, True)
    return user_id


def local_rows(user_id):
    return db.connect().execute(
        "SELECT * FROM contacts WHERE user_id=?", (user_id,)).fetchall()


def sealed_row(user_id):
    return db.connect().execute(
        "SELECT * FROM contact_books WHERE user_id=?", (user_id,)).fetchone()


# --- the plan decides, and only the plan ------------------------------------

def test_a_private_plan_seals_the_book(client):
    vault = Vault()
    user_id = granted(client)
    out = contacts.sync(user_id, [{"name": "Mom", "number": MOM}],
                        vault, "basic")
    assert out["sealed"] is True
    assert sealed_row(user_id) is not None
    assert list(vault.records) == [f"jim/{user_id}/contacts/book"]
    names = [r["name"] for r in json.loads(next(iter(vault.records.values())))]
    assert names == ["Mom"]


def test_an_open_plan_keeps_it_local_on_a_deployment_that_has_a_vault(client):
    """The defect `vault_for` exists to prevent, on this payload.

    A vault is configured. The account is free. Free is platform custody, and
    sealing here would put somebody's address book behind a key they do not
    hold and are not paying for.
    """
    vault = Vault()
    user_id = granted(client)
    out = contacts.sync(user_id, [{"name": "Mom", "number": MOM}],
                        vault, "free")
    assert out["sealed"] is False
    assert vault.records == {}
    assert sealed_row(user_id) is None
    assert [r["name"] for r in local_rows(user_id)] == ["Mom"]


def test_no_vault_on_the_deployment_keeps_it_local_whatever_the_plan(client):
    user_id = granted(client)
    out = contacts.sync(user_id, [{"name": "Mom", "number": MOM}], None,
                        "basic")
    assert out["sealed"] is False
    assert [r["name"] for r in local_rows(user_id)] == ["Mom"]


# --- one book, never two ----------------------------------------------------

def test_moving_to_an_open_plan_leaves_one_book(client):
    vault = Vault()
    user_id = granted(client)
    contacts.sync(user_id, [{"name": "Mom", "number": MOM}], vault, "basic")
    contacts.sync(user_id, [{"name": "Mom", "number": MOM}], vault, "free")

    assert sealed_row(user_id) is None
    assert len(local_rows(user_id)) == 1
    assert vault.records == {}, (
        "the sealed book survived a move to a plan that does not seal")


def test_moving_to_a_private_plan_leaves_one_book(client):
    vault = Vault()
    user_id = granted(client)
    contacts.sync(user_id, [{"name": "Mom", "number": MOM}], vault, "free")
    contacts.sync(user_id, [{"name": "Mom", "number": MOM}], vault, "basic")

    assert sealed_row(user_id) is not None
    assert local_rows(user_id) == [], (
        "the local book survived a move to a plan that seals")


def test_the_book_reads_the_same_from_either_custody(client):
    vault = Vault()
    entries = [{"name": "Mom", "number": MOM},
               {"name": "Ada", "number": "+1 555 010 9001"}]

    open_user = granted(client)
    contacts.sync(open_user, entries, vault, "free")
    sealed_user = granted(client)
    contacts.sync(sealed_user, entries, vault, "basic")

    one = contacts.book(open_user, vault)
    two = contacts.book(sealed_user, vault)
    assert [r["name"] for r in one] == [r["name"] for r in two] == ["Ada", "Mom"]
    assert set(one[0]) == set(two[0])
    assert "digits" not in one[0] and "digits" not in two[0]


# --- withdrawal reaches what is actually there ------------------------------

def test_withdrawing_drops_a_sealed_book(client):
    vault = Vault()
    user_id = granted(client)
    contacts.sync(user_id, [{"name": "Mom", "number": MOM}], vault, "basic")
    key = f"jim/{user_id}/contacts/book"

    life.set_source(user_id, contacts.SOURCE, False, vault)

    assert sealed_row(user_id) is None
    assert key in vault.deleted, "the vault was never asked to drop the book"
    assert vault.records == {}


def test_withdrawing_on_an_open_plan_still_drops_the_sealed_book(client):
    """The one this asymmetry is for.

    Sealed on Basic, withdrawn on Free. A withdrawal that asked the plan where
    to look would look in the local table, find nothing, and report success
    over a vault still holding a few hundred other people's numbers.
    """
    vault = Vault()
    user_id = granted(client)
    contacts.sync(user_id, [{"name": "Mom", "number": MOM}], vault, "basic")

    # The plan changes. Nothing re-syncs — they simply withdraw.
    life.set_source(user_id, contacts.SOURCE, False, vault)

    assert vault.records == {}, (
        "a book sealed on a paid plan outlived the withdrawal because the "
        "withdrawal asked the current plan where to look")


def test_the_deletion_path_does_not_ask_the_plan():
    """Read from the source, because this is a rule about a call that is easy
    to make correctly and easy to make wrong in one edit."""
    import inspect
    body = inspect.getsource(contacts._clear)
    assert "vault_for" not in body, (
        "_clear plan-gates the deletion, so a book sealed under an earlier "
        "plan is unreachable to the thing whose job is to remove it")


# --- a sealed book with no vault is not an empty one ------------------------

def test_a_sealed_book_with_no_vault_raises_rather_than_answering_nobody(client):
    vault = Vault()
    user_id = granted(client)
    contacts.sync(user_id, [{"name": "Mom", "number": MOM}], vault, "basic")

    with pytest.raises(contacts.VaultUnreachable):
        contacts.book(user_id)
    with pytest.raises(contacts.VaultUnreachable):
        contacts.whose(user_id, MOM)


def test_a_row_that_says_sealed_over_an_empty_vault_raises(client):
    """Not the same as a book with nobody in it.

    An empty book is a row saying `held = 0`. A row pointing at a record the
    vault does not have is a vault that lost something, and answering *you
    know nobody* would be this product reporting somebody's data loss as a
    fact about their life.
    """
    vault = Vault()
    user_id = granted(client)
    contacts.sync(user_id, [{"name": "Mom", "number": MOM}], vault, "basic")
    vault.records.clear()

    with pytest.raises(contacts.VaultUnreachable):
        contacts.book(user_id, vault)


def test_an_empty_sealed_book_is_readable_and_says_nobody(client):
    vault = Vault()
    user_id = granted(client)
    contacts.sync(user_id, [], vault, "basic")
    assert contacts.book(user_id, vault) == []
    assert contacts.held(user_id) == 0


# --- recognition works from the vault ---------------------------------------

def test_a_call_is_named_from_a_sealed_book(client):
    vault = Vault()
    user_id = granted(client)
    contacts.sync(user_id, [{"name": "Mom", "number": MOM}], vault, "basic")

    known = contacts.whose(user_id, MOM, vault)
    assert known and known["name"] == "Mom"
    assert contacts.whose(user_id, "+1 555 010 7777", vault) is None


def test_a_guardian_is_found_from_a_sealed_book(client):
    vault = Vault()
    a, b = granted(client), enroll(client)
    contacts.sync(a, [{"name": "Sam", "number": MOM, "jim_user_id": b}],
                  vault, "basic")
    assert contacts.guardian_of(a, MOM, vault) == b


def test_the_count_needs_no_unsealing(client):
    """A screen saying *312 people* is not a reason to open three hundred
    names, and a count is not one of the things this is protecting."""
    vault = Vault()
    user_id = granted(client)
    contacts.sync(user_id, [{"name": "Mom", "number": MOM},
                            {"name": "Ada", "number": "+1 555 010 9001"}],
                  vault, "basic")
    vault.records.clear()          # the vault is unreachable
    assert contacts.held(user_id) == 2


# --- the question is asked in one place -------------------------------------

def test_the_plan_question_is_storages_and_is_asked_once():
    import inspect
    body = inspect.getsource(contacts.sync)
    assert body.count("vault_for") == 1
    assert "is_private" not in inspect.getsource(contacts), (
        "contacts.py decides the posture itself rather than asking storage, "
        "so the two can disagree about what a plan means")
    # And it is the same function every other seal point asks.
    assert storage.vault_for(  # noqa: S101 — the shape, not a behaviour
        "free", object()) is None
