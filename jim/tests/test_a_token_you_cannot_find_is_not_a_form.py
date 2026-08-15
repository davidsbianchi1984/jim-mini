"""Linking your own QRME profile by signing in, not by pasting two secrets.

    asked     how do I get a token
    mattered  there was no answer, and `Your own profile` asked anyway

`POST /self-profile/{user_id}` wants a `prf_…` id and an owner token. Both are
real and neither is findable: QRME mints an owner token once, in its create
response, and hands it to whichever client did the creating. Somebody who made
the profile on their phone and opened the Guardian on a laptop could not fill
that form in at all — and the field report said so in those words.

`POST /self-profile/{user_id}/sign-in` takes the credential a person has.

Five ways this could be wrong, one guard each:

1. **It stores the password, or the account token.** The password rides one
   call. The account token is *broader* than the owner token it mints — it
   reaches every profile on the account and the billing — so it must not
   survive the function that used it.
2. **It links something that is not the person.** Only `kind == "self"` may be
   briefed, and filtering before the choice is offered is what stops a person
   picking something that would then be refused.
3. **It goes around `link`.** The kind check, the unreachable-QRME refusal and
   the consent reset all live there. A second path into `self_links` is how
   those three drift apart.
4. **It leaks which profile ids exist.** A `profile_id` on another account must
   answer as one that does not exist.
5. **It flattens QRME's refusals.** A wrong password and a deployment with no
   QRME configured are different problems, and a person can act on one.

The fake below answers the shapes QRME's own suite verifies in
`tests/test_where_do_i_find_my_owner_token.py` — `profile_id` keyed rows from
`identity.roster`, and a mint that is additive rather than a rotation.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from jim import db, synthetic_self
from jim.api import create_app
from jim.qrme_client import QRMEClient
from jim.tests.conftest import _Resp, enroll


class FakeQRMEAccount:
    """QRME's account doors, at the HTTP-client boundary.

    Records every request so a test can assert on what actually crossed —
    in particular that the password crossed exactly once and the account
    token never came back to JIM's caller.
    """

    PASSWORD = "hunter2-hunter2"

    def __init__(self, profiles=None):
        self.profiles = profiles if profiles is not None else [
            {"profile_id": "prf_dana", "kind": "self", "shown_as": "Dana",
             "display_name": "Dana"},
            {"profile_id": "prf_work", "kind": "fictional",
             "shown_as": "Dana at work", "display_name": "Dana at work"},
        ]
        self.posts: list[tuple] = []
        self.gets: list[tuple] = []
        self.minted = 0

    def post(self, path, json=None, headers=None):
        self.posts.append((path, dict(json or {}), dict(headers or {})))
        if path == "/signin":
            if (json or {}).get("password") != self.PASSWORD:
                return _Resp(403, {"detail": "that is not right"})
            return _Resp(200, {"account_id": "acc_dana",
                               "email": (json or {}).get("email"),
                               "account_token": "acct-token-secret"})
        if path.endswith("/owner-token"):
            if (headers or {}).get("authorization") != "Bearer acct-token-secret":
                return _Resp(403, {"detail": "not authorized"})
            self.minted += 1
            pid = path.split("/profiles/")[1].split("/")[0]
            return _Resp(201, {"profile_id": pid,
                               "owner_token": f"owner-{pid}-{self.minted}",
                               "shown_once": True})
        return _Resp(404, {})

    def get(self, path, headers=None):
        self.gets.append((path, dict(headers or {})))
        if path == "/accounts/acc_dana/profiles":
            if (headers or {}).get("authorization") != "Bearer acct-token-secret":
                return _Resp(403, {"detail": "not authorized"})
            return _Resp(200, {"owner_id": "acc_dana",
                               "profiles": self.profiles,
                               "count": len(self.profiles)})
        if path.startswith("/profiles/"):
            # `link` reads the kind back from QRME before it will store
            # anything, and that guard stays in force through this route.
            pid = path.rsplit("/", 1)[-1]
            for p in self.profiles:
                if p["profile_id"] == pid:
                    return _Resp(200, {"id": pid, "kind": p["kind"],
                                       "display_name": p["display_name"]})
            return _Resp(404, {})
        return _Resp(404, {})


@pytest.fixture()
def qrme():
    return FakeQRMEAccount()


@pytest.fixture()
def client(tmp_path, monkeypatch, qrme):
    monkeypatch.setenv("JIM_DB", str(tmp_path / "test.db"))
    monkeypatch.setenv("JIM_LLM", "stub")
    db.reset()
    with TestClient(create_app(qrme_client=QRMEClient(client=qrme))) as c:
        yield c
    db.reset()


def _sign_in(client, user_id, **extra):
    return client.post(f"/self-profile/{user_id}/sign-in",
                       json={"email": "dana@example.test",
                             "password": FakeQRMEAccount.PASSWORD, **extra})


def test_an_email_and_a_password_are_enough(client, qrme):
    user_id = enroll(client)
    r = _sign_in(client, user_id)
    assert r.status_code == 201, r.text
    assert r.json()["linked"] is True

    # The `self` profile, not the fictional one standing beside it.
    status = client.get(f"/self-profile/{user_id}").json()
    assert status["profile_id"] == "prf_dana"
    assert qrme.minted == 1


def test_neither_the_password_nor_the_account_token_is_kept(client, qrme):
    """The account token is the broader credential and must not outlive the
    call that used it: it reaches every profile on the account and the
    billing, where the owner token reaches one profile."""
    user_id = enroll(client)
    r = _sign_in(client, user_id)
    assert r.status_code == 201, r.text

    body = r.text
    assert FakeQRMEAccount.PASSWORD not in body
    assert "acct-token-secret" not in body

    # And nothing of either landed in the database.
    rows = db.connect().execute("SELECT * FROM self_links").fetchall()
    assert len(rows) == 1
    stored = " ".join(str(v) for v in dict(rows[0]).values())
    assert FakeQRMEAccount.PASSWORD not in stored
    assert "acct-token-secret" not in stored
    # What *is* stored is the owner token — the same field the paste-it form
    # was asking the person to go and find.
    assert stored.count("owner-prf_dana") == 1


def test_the_password_crosses_once_and_only_to_signin(client, qrme):
    user_id = enroll(client)
    _sign_in(client, user_id)
    carried = [p for p in qrme.posts
               if FakeQRMEAccount.PASSWORD in str(p[1])]
    assert len(carried) == 1
    assert carried[0][0] == "/signin"


def test_a_wrong_password_says_so_rather_than_something_else(client):
    user_id = enroll(client)
    r = client.post(f"/self-profile/{user_id}/sign-in",
                    json={"email": "dana@example.test", "password": "nope"})
    assert r.status_code == 403, r.text
    assert "email and password" in r.text


def test_two_of_the_person_ask_which_and_store_nothing_yet(client, qrme):
    qrme.profiles = [
        {"profile_id": "prf_dana", "kind": "self", "shown_as": "Dana",
         "display_name": "Dana"},
        {"profile_id": "prf_quiet", "kind": "self", "shown_as": "Someone",
         "display_name": "Dana (quiet)"},
    ]
    user_id = enroll(client)

    first = _sign_in(client, user_id)
    assert first.status_code == 201, first.text
    body = first.json()
    assert body["linked"] is False
    assert {c["profile_id"] for c in body["choose"]} == {"prf_dana",
                                                        "prf_quiet"}
    assert qrme.minted == 0
    assert db.connect().execute(
        "SELECT COUNT(*) AS n FROM self_links").fetchone()["n"] == 0

    # The second call carries the same password plus the choice — which the
    # console can send without asking the person to type anything again.
    second = _sign_in(client, user_id, profile_id="prf_quiet")
    assert second.status_code == 201, second.text
    assert second.json()["linked"] is True
    assert client.get(f"/self-profile/{user_id}").json()[
        "profile_id"] == "prf_quiet"


def test_a_profile_on_another_account_is_refused(client, qrme):
    user_id = enroll(client)
    r = _sign_in(client, user_id, profile_id="prf_somebody_else")
    assert r.status_code == 404, r.text
    assert qrme.minted == 0


def test_an_account_with_no_self_profile_says_what_to_do(client, qrme):
    """Not a 500 and not an empty success — the person has to be told the
    thing they can act on, which is that QRME has to make one first."""
    qrme.profiles = [{"profile_id": "prf_work", "kind": "fictional",
                      "shown_as": "Dana at work",
                      "display_name": "Dana at work"}]
    user_id = enroll(client)
    r = _sign_in(client, user_id)
    assert r.status_code == 409, r.text
    assert "kind 'self'" in r.text


def test_a_deployment_with_no_qrme_says_that_rather_than_failing(tmp_path,
                                                                 monkeypatch):
    monkeypatch.setenv("JIM_DB", str(tmp_path / "noqrme.db"))
    monkeypatch.setenv("JIM_LLM", "stub")
    db.reset()
    with TestClient(create_app()) as c:
        user_id = enroll(c)
        r = c.post(f"/self-profile/{user_id}/sign-in",
                   json={"email": "dana@example.test", "password": "x"})
        assert r.status_code == 502, r.text
        assert "QRME endpoint" in r.text
    db.reset()


def test_it_goes_through_link_so_the_kind_check_still_runs(client, qrme,
                                                           monkeypatch):
    """The refusal that keeps a fictional profile from being briefed lives in
    `link`. If this route ever wrote `self_links` itself, that check would be
    the first thing to go missing — so prove `link` is on the path."""
    seen = {}
    real = synthetic_self.link

    def spy(user_id, profile_id, owner_token, qrme_client):
        seen["called"] = (profile_id, owner_token)
        return real(user_id, profile_id, owner_token, qrme_client)

    monkeypatch.setattr(synthetic_self, "link", spy)
    user_id = enroll(client)
    assert _sign_in(client, user_id).status_code == 201
    assert seen["called"][0] == "prf_dana"
    assert seen["called"][1].startswith("owner-prf_dana")


def test_the_paste_it_route_still_works(client, qrme):
    """The other door is not removed. Somebody who does hold an id and a token
    — from the create response, or from QRME's own console — has no reason to
    type a password here."""
    user_id = enroll(client)
    r = client.post(f"/self-profile/{user_id}",
                    json={"profile_id": "prf_dana",
                          "owner_token": "owner-from-somewhere-else"})
    assert r.status_code == 201, r.text
    assert r.json()["linked"] is True
