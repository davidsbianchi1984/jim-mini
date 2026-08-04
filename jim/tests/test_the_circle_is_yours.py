"""Messaging, switches, and a homepage — for the person, not the profile.

## The finding

QRME's people got messages, switches and a MySpace-style page this round,
and the person behind a JIM had none of them: no way to reach the other
user on the same deployment, nothing to turn off, no page of their own.
The Guardian knew everything about them and offered them no surface that
was simply *theirs*.

    asked     can the Guardian's user reach the people around them
    mattered  on whose terms

## What this file drives

`jim/circle.py`, whose four parts share one idea — the person decides:

1. **the circle** — JIM has no friendship graph, so the consent record
   is built here: an invitation is one direction, two directions make
   contacts, and either side deleting theirs ends it for both;
2. **switches** — a named set, default on, refusing by naming the switch;
3. **messages** — contacts only, one thread per pair, old words
   surviving the circle ending while new ones need it back, and nothing
   ever leaving the deployment;
4. **the homepage sandbox** — identical walls to QRME's (hex colors,
   http(s) links, plain text, actual contacts), but never public: a
   signed-in neighbour is the widest audience it has.
"""

from __future__ import annotations

from jim import db


def _person(client, name):
    r = client.post("/enroll", json={"display_name": name,
                                     "birthdate": "1984-06-01",
                                     "terms_consent": True})
    assert r.status_code == 201, r.text
    u = r.json()
    return u["id"], {"authorization": f"Bearer {u['user_token']}"}


def _join(client, a, ha, b, hb):
    assert client.post(f"/circle/{a}/contacts", json={"other_id": b},
                       headers=ha).status_code == 201
    r = client.post(f"/circle/{b}/contacts", json={"other_id": a},
                    headers=hb)
    assert r.status_code == 201 and r.json()["state"] == "contacts"


# --- the circle itself -------------------------------------------------------

def test_an_invitation_is_one_direction_and_two_make_contacts(client):
    a, ha = _person(client, "Ana")
    b, hb = _person(client, "Ben")
    r = client.post(f"/circle/{a}/contacts", json={"other_id": b},
                    headers=ha)
    assert r.status_code == 201 and r.json()["state"] == "invited"
    # Ben sees the waiting invitation by name.
    view = client.get(f"/circle/{b}", headers=hb).json()
    assert [p["display_name"] for p in view["circle"]["invited_me"]] == ["Ana"]
    # Accepting is just the second direction.
    r = client.post(f"/circle/{b}/contacts", json={"other_id": a},
                    headers=hb)
    assert r.json()["state"] == "contacts"
    view = client.get(f"/circle/{a}", headers=ha).json()
    assert [p["user_id"] for p in view["circle"]["contacts"]] == [b]


def test_the_circle_refuses_ghosts_and_yourself(client):
    a, ha = _person(client, "Ana")
    r = client.post(f"/circle/{a}/contacts", json={"other_id": "u-nobody"},
                    headers=ha)
    assert r.status_code == 422 and "deployment" in r.json()["detail"]
    r = client.post(f"/circle/{a}/contacts", json={"other_id": a},
                    headers=ha)
    assert r.status_code == 422 and "own circle" in r.json()["detail"]


def test_the_circle_is_behind_the_users_own_door(client):
    a, _ = _person(client, "Ana")
    _, hb = _person(client, "Ben")
    assert client.get(f"/circle/{a}",
                      headers=hb).status_code in (401, 403)
    assert client.put(f"/circle/{a}/features",
                      json={"feature": "messaging", "enabled": False},
                      headers=hb).status_code in (401, 403)


# --- the switches ------------------------------------------------------------

def test_the_switches_default_on_and_refuse_by_name(client):
    a, ha = _person(client, "Ana")
    view = client.get(f"/circle/{a}", headers=ha).json()
    assert view["features"] == {"messaging": True, "homepage": True}
    out = client.put(f"/circle/{a}/features",
                     json={"feature": "messaging", "enabled": False},
                     headers=ha).json()
    assert out["messaging"] is False and out["homepage"] is True
    r = client.put(f"/circle/{a}/features",
                   json={"feature": "telepathy", "enabled": True},
                   headers=ha)
    assert r.status_code == 422
    assert "messaging" in r.json()["detail"] and \
           "homepage" in r.json()["detail"]


# --- the messages ------------------------------------------------------------

def test_messages_travel_inside_the_circle_and_only_inside(client):
    a, ha = _person(client, "Ana")
    b, hb = _person(client, "Ben")
    r = client.post(f"/circle/{a}/messages", json={"to": b, "body": "hi"},
                    headers=ha)
    assert r.status_code == 422 and "circle" in r.json()["detail"]
    # One direction is an invitation, not consent.
    client.post(f"/circle/{a}/contacts", json={"other_id": b}, headers=ha)
    r = client.post(f"/circle/{a}/messages", json={"to": b, "body": "hi"},
                    headers=ha)
    assert r.status_code == 422
    client.post(f"/circle/{b}/contacts", json={"other_id": a}, headers=hb)
    r = client.post(f"/circle/{a}/messages",
                    json={"to": b, "body": "hi Ben"}, headers=ha)
    assert r.status_code == 201, r.text
    # Both sides read the same thread; the list names the other person.
    mine = client.get(f"/circle/{a}/messages", params={"with_id": b},
                      headers=ha).json()["messages"]
    theirs = client.get(f"/circle/{b}/messages", params={"with_id": a},
                        headers=hb).json()["messages"]
    assert [m["body"] for m in mine] == ["hi Ben"] and mine == theirs
    threads = client.get(f"/circle/{b}/messages", headers=hb).json()["threads"]
    assert [t["other_name"] for t in threads] == ["Ana"]


def test_the_recipients_switch_refuses_by_name(client):
    a, ha = _person(client, "Ana")
    b, hb = _person(client, "Ben")
    _join(client, a, ha, b, hb)
    client.put(f"/circle/{b}/features",
               json={"feature": "messaging", "enabled": False}, headers=hb)
    r = client.post(f"/circle/{a}/messages", json={"to": b, "body": "hi"},
                    headers=ha)
    assert r.status_code == 422 and "turned off" in r.json()["detail"]


def test_old_words_survive_the_circle_ending_and_new_ones_need_it_back(client):
    a, ha = _person(client, "Ana")
    b, hb = _person(client, "Ben")
    _join(client, a, ha, b, hb)
    client.post(f"/circle/{a}/messages", json={"to": b, "body": "before"},
                headers=ha)
    assert client.delete(f"/circle/{a}/contacts/{b}",
                         headers=ha).status_code == 200
    old = client.get(f"/circle/{b}/messages", params={"with_id": a},
                     headers=hb).json()["messages"]
    assert [m["body"] for m in old] == ["before"]
    r = client.post(f"/circle/{b}/messages", json={"to": a, "body": "hey"},
                    headers=hb)
    assert r.status_code == 422 and "circle" in r.json()["detail"]


def test_a_message_needs_words_and_a_message_never_leaves_home(client):
    a, ha = _person(client, "Ana")
    b, hb = _person(client, "Ben")
    _join(client, a, ha, b, hb)
    r = client.post(f"/circle/{a}/messages", json={"to": b, "body": "  "},
                    headers=ha)
    assert r.status_code == 422 and "words" in r.json()["detail"]
    # The structural half of "never leaves": the module that carries
    # messages imports no client that could carry them out — not the
    # tandem, not the cloud, not the mailer.
    import ast
    import jim.circle as mod
    tree = ast.parse(open(mod.__file__, encoding="utf-8").read())
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported |= {a.name for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            imported |= {a.name for a in node.names}
    outward = {"qrme_client", "cloud", "mailer", "requests", "httpx",
               "pdi_client", "relay", "notify"}
    assert not (imported & outward), (
        f"jim/circle.py imports {sorted(imported & outward)} — messages "
        "are supposed to live and die on this deployment")


# --- the homepage sandbox ----------------------------------------------------

def _edit(client, uid, head, **doc):
    return client.put(f"/circle/{uid}/homepage", json=doc, headers=head)


def test_the_homepage_shows_to_a_neighbour_but_never_to_the_street(client):
    a, ha = _person(client, "Ana")
    b, hb = _person(client, "Ben")
    _join(client, a, ha, b, hb)
    r = _edit(client, a, ha, headline="Ana's corner",
              about="Tea and long walks.",
              theme={"bg": "#101020", "accent": "#2fbf8f"},
              links=[{"label": "my garden", "url": "https://example.com"}],
              top_friends=[b])
    assert r.status_code == 200, r.text
    # A signed-in neighbour sees it, as themselves…
    page = client.get(f"/circle/{b}/homepage/{a}", headers=hb).json()
    assert page["headline"] == "Ana's corner"
    assert [t["display_name"] for t in page["top_friends"]] == ["Ben"]
    assert page["editable"] is False
    # …and the street does not: no credential, no page.
    assert client.get(f"/circle/{b}/homepage/{a}").status_code in (401, 403)


def test_the_walls_hold_and_a_rejected_edit_changes_nothing(client):
    a, ha = _person(client, "Ana")
    r = _edit(client, a, ha, theme={"bg": "javascript:alert(1)"})
    assert r.status_code == 422 and "hex" in r.json()["detail"]
    r = _edit(client, a, ha, links=[{"url": "javascript:alert(1)"}])
    assert r.status_code == 422 and "http" in r.json()["detail"]
    b, _ = _person(client, "Ben")
    r = _edit(client, a, ha, top_friends=[b])
    assert r.status_code == 422 and "actual contacts" in r.json()["detail"]
    # The wall is a wall, not a filter: the page keeps its last good state.
    _edit(client, a, ha, headline="good")
    _edit(client, a, ha, headline="evil",
          links=[{"url": "javascript:alert(1)"}])
    page = client.get(f"/circle/{a}/homepage/{a}", headers=ha).json()
    assert page["headline"] == "good" and page["editable"] is True


def test_the_homepage_switch_hides_it_from_everyone_but_the_owner(client):
    a, ha = _person(client, "Ana")
    b, hb = _person(client, "Ben")
    _join(client, a, ha, b, hb)
    _edit(client, a, ha, headline="mine")
    client.put(f"/circle/{a}/features",
               json={"feature": "homepage", "enabled": False}, headers=ha)
    assert client.get(f"/circle/{b}/homepage/{a}",
                      headers=hb).status_code == 404
    own = client.get(f"/circle/{a}/homepage/{a}", headers=ha).json()
    assert own["headline"] == "mine" and own["editable"] is True


def test_nothing_a_neighbour_sees_can_carry_a_script(client):
    """The structural claim, same as QRME's: every field a neighbour sees
    is text, a hex color, or an http(s) URL — nowhere to put a script."""
    a, ha = _person(client, "Ana")
    b, hb = _person(client, "Ben")
    _join(client, a, ha, b, hb)
    _edit(client, a, ha, headline="<script>alert(1)</script>",
          about="<img onerror=x src=y>")
    page = client.get(f"/circle/{b}/homepage/{a}", headers=hb).json()
    assert page["theme"]["bg"].startswith("#")
    for link in page["links"]:
        assert link["url"].startswith(("http://", "https://"))
    assert isinstance(page["headline"], str)
    assert isinstance(page["about"], str)


# --- the view ----------------------------------------------------------------

def test_the_view_carries_labels_in_the_readers_language(client):
    a, ha = _person(client, "Ana")
    client.put(f"/language/{a}", json={"language": "pt"}, headers=ha)
    view = client.get(f"/circle/{a}", headers=ha).json()
    assert view["labels"]["title"] == "O seu círculo"
    assert "instalação" in view["note"]
