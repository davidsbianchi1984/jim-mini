"""Everything the Guardian could change was a menu, and the menus were the bug.

Field report, verbatim: *these menus and settings are awful user unfriendly if
you don't know what you're doing … I want users to be able to verbally
communicate with JIM what they would like to have on or off and JIM to be able
to make edits and changes to their accounts.*

Twenty-six tools, and three of them touched a setting: how it talks, what
language, which model. Where it speaks through, what it may read, and which
parts of the product are switched on were screens and only screens — reachable
by somebody who already knew where they were, which is the population that did
not need them.

    asked     can the Guardian act
    mattered  can it act on the thing the person is actually stuck on

The second half of the report is the shape, and it is not "give the agent more
reach". It is *kinda like I gave you permission and connections to my ElevenLabs
account … after they opened the connectors and approved permissions per app* —
a grant, in a list, revocable, read before it is given. So:

  * the three new tools are real doors, driven here end to end;
  * the two that widen what the Guardian sees or switch parts of the product on
    and off are refused until their group is granted;
  * the group already covered by opening a session is *not* re-asked for,
    because a release that adds a permission screen in front of something
    somebody already approved has made the product more annoying, not safer;
  * and every one of them can be taken back, which is where the interesting
    bugs were.
"""

from __future__ import annotations

import pytest

from jim import engaged, permits

from .conftest import enroll


class _Scripted:
    """A model that says what the test needs said, in order.

    `answered_by` is load-bearing: an engaged turn refuses to act on a stub
    answer, so a scripted model that did not claim to be an online one would
    be refused before it could say anything.
    """

    answered_by = "claude"
    failure = None

    def __init__(self, lines):
        self.lines = list(lines)

    def generate(self, system, user):
        return self.lines.pop(0) if self.lines else "Done."


@pytest.fixture()
def engaged_user(client):
    uid = enroll(client)
    client.post(f"/engaged/{uid}", json={"area": "personal_growth"})
    return uid


def _script(monkeypatch, *lines):
    """One instance, closed over — the loop asks for a provider on every step,
    and a fresh script each time would replay line one until the ceiling."""
    from jim import llm
    provider = _Scripted(lines)
    monkeypatch.setattr(llm, "get_provider",
                        lambda cloud=None, choice=None: provider)


# --------------------------------------------------------------------------- #
# The sentence that used to be a screen
# --------------------------------------------------------------------------- #

def test_it_can_be_told_which_device_to_speak_through(client, engaged_user,
                                                      monkeypatch):
    """The picker somebody photographed, said out loud instead.

    `how_it_speaks` is granted by opening the session — the surface belongs to
    the same group as the bearing and the language, which a person approved
    when they read what the session may touch. Nothing extra is switched on
    here, deliberately: this is the case that must keep working untouched.
    """
    uid = engaged_user
    assert client.get(f"/presence/{uid}/surfaces").json()["chosen"] \
        == "phone_screen"

    _script(monkeypatch,
            'CALL set_surface {"speaks_on": "earbuds"}',
            "Earbuds it is.")
    turn = client.post(f"/engaged/{uid}/turn",
                       json={"message": "talk to me through my earbuds"})
    assert turn.status_code == 200, turn.text
    assert client.get(f"/presence/{uid}/surfaces").json()["chosen"] == "earbuds"


def test_the_surface_it_overwrote_comes_back(client, engaged_user,
                                             monkeypatch):
    """The undo, driven — and the reason the spec grew a rename.

    `GET /presence/{id}/surfaces` answers with `chosen`; `PUT
    /presence/{id}/surface` takes `speaks_on`. They differ on purpose: QRME and
    PDI already use "surface" for a *display* surface, and the shared-vocabulary
    guard across the three products is right that one field name should not mean
    two things.

        asked     is the prior value stored
        mattered  is it stored under the name the door will accept

    Replaying `{"chosen": "phone_screen"}` at a door expecting `speaks_on` is a
    422 — found not in review but by somebody trying to take something back,
    which is the worst moment for an undo to be wrong.
    """
    uid = engaged_user
    _script(monkeypatch,
            'CALL set_surface {"speaks_on": "speaker"}', "Done.")
    client.post(f"/engaged/{uid}/turn", json={"message": "use the speaker"})
    assert client.get(f"/presence/{uid}/surfaces").json()["chosen"] == "speaker"

    act = [a for a in client.get(f"/engaged/{uid}/acts").json()
           if a["tool"] == "set_surface"][0]
    assert act["reversible"] is True, (
        "the surface change recorded no way back — the read and the write "
        "name the setting differently and the inverse was stored under the "
        "read's name")
    assert client.post(f"/engaged/{uid}/acts/{act['id']}/undo").status_code \
        == 200
    assert client.get(f"/presence/{uid}/surfaces").json()["chosen"] \
        == "phone_screen"


# --------------------------------------------------------------------------- #
# The two that have to be asked for
# --------------------------------------------------------------------------- #

def test_a_switch_it_was_never_given_is_refused_and_says_where(
        client, engaged_user, monkeypatch):
    """The defect this module exists to avoid.

    `set_feature` switches parts of the product on and off. Nobody consented
    to that by opening a session, because it did not exist when they did.
    """
    uid = engaged_user
    before = client.get(f"/circle/{uid}").json()["features"]
    feature = sorted(before)[0]

    _script(monkeypatch,
            'CALL set_feature {"feature": "%s", "enabled": false}' % feature,
            "I cannot do that one yet.")
    turn = client.post(f"/engaged/{uid}/turn",
                       json={"message": f"turn {feature} off"})
    assert turn.status_code == 200, turn.text
    assert client.get(f"/circle/{uid}").json()["features"] == before, (
        "the feature changed without the group being granted")

    refused = [d for d in turn.json()["did"]
               if d.get("refused") == "engaged.not_permitted"]
    assert refused, (
        "the turn did not record the refusal, so the transcript reads as "
        f"though nothing was attempted: {turn.json()}")
    assert refused[0]["tool"] == "set_feature", (
        "the refusal does not name the tool that was reached for, so a "
        "person reading the trail cannot tell what they need to switch on")


def test_granting_the_group_is_all_it_needed(client, engaged_user,
                                             monkeypatch):
    """And the other half — a grant is a switch, not a ceremony."""
    uid = engaged_user
    before = client.get(f"/circle/{uid}").json()["features"]
    feature = sorted(before)[0]

    on = client.put(f"/engaged/{uid}/permits/what_is_switched_on",
                    json={"granted": True})
    assert on.status_code == 200, on.text
    assert on.json()["granted"] is True
    assert on.json()["decided_at"], (
        "the grant recorded no date — 'I never agreed to that' has to be "
        "answerable with something")

    _script(monkeypatch,
            'CALL set_feature {"feature": "%s", "enabled": false}' % feature,
            "Switched off.")
    client.post(f"/engaged/{uid}/turn", json={"message": f"turn {feature} off"})
    assert client.get(f"/circle/{uid}").json()["features"][feature] is False


def test_a_feature_it_switched_comes_back(client, engaged_user, monkeypatch):
    """The `in` undo, driven: a map rather than a list of rows.

    `GET /circle/{id}` answers with `{"features": {name: bool}, …}`. The
    row-selector written for `/bands` hunts for the first *list* in the answer
    and would have picked the message threads, so this needed its own way of
    finding the prior value — and without it the act would have been recorded
    as one that cannot be taken back.
    """
    uid = engaged_user
    client.put(f"/engaged/{uid}/permits/what_is_switched_on",
               json={"granted": True})
    feature = sorted(client.get(f"/circle/{uid}").json()["features"])[0]
    before = client.get(f"/circle/{uid}").json()["features"][feature]

    _script(monkeypatch,
            'CALL set_feature {"feature": "%s", "enabled": %s}'
            % (feature, "false" if before else "true"), "Done.")
    client.post(f"/engaged/{uid}/turn", json={"message": "flip it"})
    act = [a for a in client.get(f"/engaged/{uid}/acts").json()
           if a["tool"] == "set_feature"][0]
    assert act["reversible"] is True
    assert client.post(f"/engaged/{uid}/acts/{act['id']}/undo").status_code \
        == 200
    assert client.get(f"/circle/{uid}").json()["features"][feature] is before


def test_a_source_it_switched_comes_back(client, engaged_user, monkeypatch):
    """`select`, keyed off the body rather than the path.

    `PUT /sources/{id}` names the source in the body and has no second path
    slot. The selector only searched `path_args`, found nothing, and returned
    no inverse — so the act was recorded as irreversible while being perfectly
    reversible, which is the failure that costs somebody their trust rather
    than their data.
    """
    uid = engaged_user
    client.put(f"/engaged/{uid}/permits/what_it_may_read", json={"granted": True})
    client.put(f"/sources/{uid}", json={"source": "calendar", "consented": True})

    _script(monkeypatch,
            'CALL set_source {"source": "calendar", "consented": false}',
            "Stopped reading it.")
    client.post(f"/engaged/{uid}/turn",
                json={"message": "stop reading my calendar"})
    now = {s["source"]: s["consented"]
           for s in client.get(f"/sources/{uid}").json()}
    assert now["calendar"] is False

    act = [a for a in client.get(f"/engaged/{uid}/acts").json()
           if a["tool"] == "set_source"][0]
    assert act["reversible"] is True, (
        "the source change recorded no way back — the selector looked in the "
        "path for a value the body was carrying")
    assert client.post(f"/engaged/{uid}/acts/{act['id']}/undo").status_code \
        == 200
    back = {s["source"]: s["consented"]
            for s in client.get(f"/sources/{uid}").json()}
    assert back["calendar"] is True


# --------------------------------------------------------------------------- #
# The list, and the two directions of the switch
# --------------------------------------------------------------------------- #

def test_the_list_says_what_each_group_covers_before_it_is_granted(
        client, engaged_user):
    """Informed consent is a sentence somebody can read, not a group name.

    `what_it_may_read` tells nobody anything. The row has to say *switch a
    source of yours on or off … changing what the Guardian is allowed to see*
    before the toggle beside it means anything.
    """
    uid = engaged_user
    body = client.get(f"/engaged/{uid}/permits").json()
    areas = {a["area"]: a for a in body["groups"]}
    assert set(areas) == set(permits.AREAS)
    for area in areas.values():
        # Measured against the name rather than against a number: the claim
        # is that the sentence says more than the group's own identifier
        # does, which is exactly what makes it informed consent rather than a
        # second copy of the label.
        assert len(area["says"].split()) > len(area["area"].split("_")), (
            f"{area['area']} explains itself in {area['says']!r}, which says "
            "no more than its own name does")
        assert area["tools"], f"{area['area']} covers nothing"


def test_the_groups_that_need_asking_start_refused(client, engaged_user):
    """And the ones that do not, do not.

    Both halves in one test on purpose: the interesting property is not that
    some are off, it is that the split falls where the consent already fell.
    """
    uid = engaged_user
    areas = {a["area"]: a
             for a in client.get(f"/engaged/{uid}/permits").json()["groups"]}
    for name, area in areas.items():
        expected = permits.AREAS[name]["standing"] == "opened"
        assert area["granted"] is expected, (
            f"{name} starts {'on' if area['granted'] else 'off'} and its "
            f"standing is {permits.AREAS[name]['standing']!r}")


def test_a_group_can_be_switched_off_again(client, engaged_user, monkeypatch):
    """The direction nobody builds, and the one that makes the rest a grant
    rather than a one-way door.

    Switching off an `opened` group has to work too — somebody who wants their
    journal left alone should not have to close the session to say so.
    """
    uid = engaged_user
    off = client.put(f"/engaged/{uid}/permits/your_records",
                     json={"granted": False})
    assert off.status_code == 200 and off.json()["granted"] is False

    _script(monkeypatch, 'CALL write_journal {"text": "no"}', "I cannot.")
    client.post(f"/engaged/{uid}/turn", json={"message": "write that down"})
    assert client.get(f"/journal/{uid}").json() == [], (
        "a group switched off still let its tool through")

    client.put(f"/engaged/{uid}/permits/your_records", json={"granted": True})
    _script(monkeypatch, 'CALL write_journal {"text": "yes"}', "Written.")
    client.post(f"/engaged/{uid}/turn", json={"message": "now write it"})
    assert len(client.get(f"/journal/{uid}").json()) == 1


def test_an_area_that_does_not_exist_is_refused_by_name(client, engaged_user):
    """A typo in a path should not silently create a permission."""
    uid = engaged_user
    bad = client.put(f"/engaged/{uid}/permits/everything",
                     json={"granted": True})
    assert bad.status_code == 422


# --------------------------------------------------------------------------- #
# The records that keep the two lists from drifting
# --------------------------------------------------------------------------- #

def test_every_acting_tool_belongs_to_a_group():
    """The one that will fail the next time somebody adds a tool.

    An acting tool with no area is not ungoverned in an interesting way — it
    is a switch that never appears in the list a person reads, which is how
    reach grows without anybody having agreed to it.
    """
    orphans = [t["name"] for t in engaged.TOOLS
               if t["acts"] and permits.area_of(t["name"]) is None]
    assert not orphans, (
        f"{len(orphans)} acting tool(s) are in no group, so they appear in no "
        "list and are covered by no yes:\n    " + "\n    ".join(orphans))


def test_no_group_names_a_tool_that_does_not_exist():
    """The other direction: a group promising reach the product does not have
    is a list that overstates what somebody is agreeing to."""
    names = set(engaged.tool_names())
    ghosts = sorted({t for spec in permits.AREAS.values()
                     for t in spec["tools"] if t not in names})
    assert not ghosts, (
        f"{len(ghosts)} tool(s) are listed in a permit group and do not "
        "exist:\n    " + "\n    ".join(ghosts))


def test_reads_are_governed_by_nothing_here():
    """Deliberate, and worth pinning.

    A read changes nothing and is already bound to this person's own records
    by the token. Putting the twelve of them behind switches would produce a
    list nobody finishes reading, which is how a consent screen becomes a
    thing people click past.
    """
    for tool in engaged.TOOLS:
        if not tool["acts"]:
            assert permits.area_of(tool["name"]) is None, (
                f"{tool['name']} only reads and is behind a switch")
