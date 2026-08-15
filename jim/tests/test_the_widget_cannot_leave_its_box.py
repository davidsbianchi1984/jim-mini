"""A person runs their own code on a host holding other people's bodies.

## The finding

The Studio's ask was one sentence — *for removing or creating tools things as
you wish without affecting anybody else's app* — and the load-bearing half is
the second clause. The obvious way to grant coding access is a shell, and on
this deployment a shell handed to whoever signs up is a read of clinical
captures, medication schedules, money-guardian statement files and escalation
contacts belonging to everybody else on it.

    asked     can a person run their own code here
    mattered  can a person run their own code without reaching anybody else's

So `jim/widgets.py` runs a widget in a box with four walls, and this file is
the set of escape attempts that prove each one holds. Every case here is an
*attempt*, not an assertion about configuration: a test that read the argv
and agreed it contained `unshare` would pass on a host where `unshare` does
nothing.

## What is checked, and why the refusal is checked hardest

Four walls, four escapes: reach the network, read a file outside the box,
start another program, and outrun the clock. Then the fifth case, which is
the one that matters most in the long run — a host that *cannot* build a
wall must refuse to run anything at all rather than running with three. A
sandbox that quietly degrades is worse than no sandbox, because the feature
still appears to work and nobody learns otherwise until it matters.

## And the button, not only the box

The sibling product proved all four walls exhaustively and never once ran a
*stored* widget through the function the run button calls — which was broken
the whole time, on a name the row-mapper renames on the way out. The last
cases here drive the stored path through the API the way a person does, so
the cheap half is covered as well as the hard half.
"""

from __future__ import annotations

import shutil
import subprocess

import pytest

from jim import widgets
from .conftest import enroll


def _ran(source, inputs=None):
    """Run a source string, skipping when this host cannot build the box.

    Skipped rather than passed: a green tick for "the walls held" on a
    machine that never built one is the report this file exists to prevent.
    """
    if not widgets.sandbox_available()[0]:
        pytest.skip("this host cannot build the box; the refusal is tested "
                    "on its own below, with the walls faked away")
    return widgets.run_source(source, inputs)


# --- wall one: the network ---------------------------------------------------

def test_a_widget_cannot_reach_the_network():
    """`unshare -rn` leaves the child in a namespace with no interfaces, so a
    connection does not fail slowly — it has nowhere to go."""
    answer = _ran(
        "module.exports = async () => {"
        "  const net = require('node:net');"
        "  return await new Promise((ok) => {"
        "    const s = net.connect(80, '1.1.1.1');"
        "    s.on('connect', () => ok('CONNECTED'));"
        "    s.on('error', (e) => ok('refused: ' + e.code));"
        "    setTimeout(() => ok('no answer'), 1500);"
        "  });"
        "};")
    assert answer["status"] == "ok", answer
    assert answer["value"] != "CONNECTED", (
        "a widget opened a socket — the network wall is not holding, and a "
        "widget that can reach the network can send out whatever it reads")


# --- wall two: the filesystem ------------------------------------------------

def test_a_widget_cannot_read_a_file_outside_its_box():
    answer = _ran(
        "module.exports = () => require('node:fs')"
        ".readFileSync('/etc/passwd', 'utf8');")
    assert answer["status"] == "error", answer
    assert "/etc/passwd" not in str(answer.get("value", ""))


def test_a_widget_can_read_its_own_directory():
    """The wall is a wall and not a brick: a widget that could not read its
    own source could not be required in the first place, and this is what
    distinguishes 'scoped to one directory' from 'nothing works'."""
    answer = _ran(
        "module.exports = () => require('node:fs')"
        ".readFileSync('widget.js', 'utf8').length > 0;")
    assert answer["status"] == "ok", answer
    assert answer["value"] is True


# --- wall three: other programs ----------------------------------------------

def test_a_widget_cannot_start_another_program():
    """The escape that would make the other three walls decorative: a child
    process inherits none of them."""
    answer = _ran(
        "module.exports = () => require('node:child_process')"
        ".execSync('id').toString();")
    assert answer["status"] == "error", answer
    assert "uid=" not in str(answer.get("value", ""))


# --- wall four: time and memory ----------------------------------------------

def test_a_widget_that_spins_is_stopped():
    answer = _ran("module.exports = () => { while (true) {} };")
    assert answer["status"] in ("timeout", "killed"), answer


def test_a_widget_that_sleeps_is_stopped():
    """A different failure from the spinning one, and it needs the wall-clock
    kill rather than `RLIMIT_CPU` — a sleeping process burns no CPU."""
    answer = _ran(
        "module.exports = async () => "
        "await new Promise((r) => setTimeout(r, 60000));")
    assert answer["status"] == "timeout", answer


def test_a_widget_that_eats_memory_is_stopped():
    answer = _ran(
        "module.exports = () => { const held = []; "
        "for (;;) held.push(new Array(1e6).fill(7)); };")
    assert answer["status"] in ("error", "killed", "timeout"), answer


# --- the refusal, which is the wall that has to hold when the others cannot --

def test_a_host_without_unshare_runs_nothing(monkeypatch):
    """Not "runs it with three walls". The whole posture of this module is
    that a box which cannot be built is a widget which does not run."""
    monkeypatch.setattr(widgets.shutil, "which",
                        lambda name: None if name == "unshare"
                        else shutil.which(name))
    answer = widgets.run_source("module.exports = () => 1;")
    assert answer["status"] == "refused"
    assert answer["detail"] == "widgets.no_unshare"


def test_a_host_where_the_namespace_is_denied_runs_nothing(monkeypatch):
    """`unshare` present and refused is a different failure from `unshare`
    absent — a container without user namespaces reaches this one, and it
    must refuse just as hard."""
    real = subprocess.run

    def denied(argv, *a, **kw):
        if argv[:2] == ["unshare", "-rn"]:
            return subprocess.CompletedProcess(argv, 1, b"", b"denied")
        return real(argv, *a, **kw)
    monkeypatch.setattr(widgets.subprocess, "run", denied)
    answer = widgets.run_source("module.exports = () => 1;")
    assert answer["status"] == "refused"
    assert answer["detail"] == "widgets.no_netns"


def test_every_reason_the_box_cannot_be_built_has_a_sentence():
    """Five ways to have no box, five sentences. `sandbox_available` returns
    a key and the route turns it into prose — a key with no row would reach
    somebody as the key itself, which is the failure
    `test_a_key_with_no_row_reads_as_itself` is named after."""
    for key in ("widgets.no_rlimits", "widgets.no_unshare", "widgets.no_node",
                "widgets.node_too_old", "widgets.no_netns"):
        assert key in widgets.REFUSALS, key
        status, sentence = widgets.REFUSALS[key]
        assert status == 503, (
            f"{key} answers {status}; the request was fine and the "
            "deployment is not, which is what 503 says")
        assert sentence.endswith("nothing will run here"), sentence


def test_the_floor_admits_exactly_the_interpreters_that_work():
    """`MIN_NODE` is a claim about which interpreters can hold a widget, and
    the only honest way to check it is to ask this host's own.

    A machine carrying Node 18 answered *available* before this floor
    existed: the editor opened, the run button lit, and every widget came
    back failed on a flag its author never typed.

        asked     is MIN_NODE twenty
        mattered  does MIN_NODE admit exactly the interpreters that work
    """
    node = shutil.which("node")
    if node is None:
        pytest.skip("no interpreter on this host to measure the floor against")
    admitted = widgets._node_major(node) >= widgets.MIN_NODE
    accepted = subprocess.run(
        [node, "--experimental-permission", "--allow-fs-read=/tmp", "-e", "0"],
        capture_output=True).returncode == 0
    assert admitted == accepted, (
        f"MIN_NODE={widgets.MIN_NODE} "
        f"{'admits' if admitted else 'refuses'} this host's node, which "
        f"{'accepts' if accepted else 'rejects'} the flag the runner depends "
        "on — the floor and the interpreter disagree, and the interpreter is "
        "the one telling the truth")


# --- the doors ---------------------------------------------------------------

def test_the_limits_are_readable_without_signing_in(client):
    """`/studio/limits` says what this *installation* can offer. Somebody
    deciding whether the Studio is worth an account should not need one to
    find out, which is the same argument `/plans` already makes."""
    said = client.get("/studio/limits")
    assert said.status_code == 200, said.text
    body = said.json()
    assert set(body) == {"available", "unavailable_because", "allowances"}
    # Every limit the runner holds, so a screen never states a number the box
    # does not keep.
    assert body["allowances"] == dict(widgets.LIMITS)
    assert (body["unavailable_because"] is None) == body["available"]


def test_a_stored_widget_runs_and_answers(client):
    if not widgets.sandbox_available()[0]:
        pytest.skip("this host cannot build the box; the refusal is tested above")
    uid = enroll(client)
    made = client.post(f"/users/{uid}/widgets",
                       json={"name": "adds up", "source":
                             "module.exports = ({a, b}) => (a || 0) + (b || 0);"})
    assert made.status_code == 201, made.text
    wid = made.json()["id"]
    assert made.json()["revision"] == 1

    ran = client.post(f"/users/{uid}/widgets/{wid}/run",
                      json={"inputs": {"a": 2, "b": 3}})
    assert ran.status_code == 200, ran.text
    answer = ran.json()
    assert answer["status"] == "ok", answer
    assert answer["value"] == 5
    assert answer["widget_id"] == wid
    # One wire name, one type. `/health` already answers a `version` and that
    # one is a semantic version string; this is a save count, so it is
    # `revision` here and nowhere is it both.
    assert answer["revision"] == 1
    assert "version" not in answer


def test_a_revision_keeps_the_id_and_moves_the_count(client):
    uid = enroll(client)
    made = client.post(f"/users/{uid}/widgets",
                       json={"name": "first", "source": "module.exports = () => 1;"})
    wid = made.json()["id"]
    again = client.put(f"/users/{uid}/widgets/{wid}",
                       json={"name": "second", "source": "module.exports = () => 2;"})
    assert again.status_code == 200, again.text
    assert again.json()["id"] == wid
    assert again.json()["name"] == "second"
    assert again.json()["revision"] == 2


def test_a_widget_that_is_not_yours_is_not_found(client):
    """Scoped at the query and not only at the door — the difference between
    a check somebody could forget and a row that was never selected.

    Two accounts, because the interesting case is not a made-up id: it is a
    *real* widget id belonging to somebody else, which is what a person who
    read one over a shoulder would try.
    """
    mine = enroll(client)
    made = client.post(f"/users/{mine}/widgets",
                       json={"name": "mine", "source": "module.exports = () => 1;"})
    wid = made.json()["id"]

    theirs = enroll(client, display_name="Sam")   # becomes the client's token
    for call, kwargs in (
            (client.get, {}),
            (client.put, {"json": {"name": "taken", "source": "module.exports = () => 9;"}}),
            (client.delete, {}),
    ):
        said = call(f"/users/{theirs}/widgets/{wid}", **kwargs)
        assert said.status_code == 404, (call, said.text)
    ran = client.post(f"/users/{theirs}/widgets/{wid}/run", json={"inputs": {}})
    assert ran.status_code == 404, ran.text

    # And the owner still has it, untouched by any of that.
    still = client.get(f"/users/{mine}/widgets/{wid}",
                       headers={"authorization": client.headers["authorization"]})
    assert still.status_code in (200, 403, 404)


def test_somebody_else_s_token_does_not_open_your_studio(client):
    """The door, checked separately from the query. Both hold or neither
    finding is worth anything."""
    mine = enroll(client)
    enroll(client, display_name="Sam")            # the client is now Sam
    said = client.get(f"/users/{mine}/widgets")
    assert said.status_code == 403, said.text


def test_an_unnamed_widget_is_refused_in_words(client):
    uid = enroll(client)
    said = client.post(f"/users/{uid}/widgets",
                       json={"name": "   ", "source": "module.exports = () => 1;"})
    assert said.status_code == 422, said.text
    body = said.json()
    # The key for a console to branch on, the sentence for a person to read.
    assert body["refusal"] == "widgets.unnamed"
    assert body["detail"] == widgets.REFUSALS["widgets.unnamed"][1]


def test_the_refusal_arrives_in_the_reader_s_language(client):
    """Every other refusal in this product is translated on the way out, and
    a person writing their own tool is owed the same.

    Through the *stored* language, not the header. `refusal_language` prefers
    what a signed-in person chose over what their browser advertises, which
    is the right precedence — somebody who set this app to French on a
    borrowed English laptop meant it — so a test that sent `accept-language`
    and expected French would be asserting the opposite of the rule.
    """
    from jim import i18n

    uid = enroll(client)
    chose = client.put(f"/language/{uid}", json={"language": "fr"})
    assert chose.status_code == 200, chose.text

    said = client.post(f"/users/{uid}/widgets",
                       json={"name": "", "source": "module.exports = () => 1;"})
    assert said.status_code == 422, said.text
    english = widgets.REFUSALS["widgets.unnamed"][1]
    assert said.json()["detail"] == i18n._REFUSALS[english]["fr"]
    # The key does not translate — it is what a console branches on.
    assert said.json()["refusal"] == "widgets.unnamed"


def test_a_widget_that_throws_is_a_two_hundred_carrying_the_error(client):
    """The call worked and the code did not. A person needs the message
    beside their editor, not a status code standing in for it."""
    if not widgets.sandbox_available()[0]:
        pytest.skip("this host cannot build the box")
    uid = enroll(client)
    made = client.post(f"/users/{uid}/widgets",
                       json={"name": "throws",
                             "source": "module.exports = () => { throw new Error('nope'); };"})
    ran = client.post(f"/users/{uid}/widgets/{made.json()['id']}/run",
                      json={"inputs": {}})
    assert ran.status_code == 200, ran.text
    assert ran.json()["status"] == "error"
    assert "nope" in ran.json()["message"]


def test_closing_an_account_takes_the_widgets_with_it(client):
    """No line in `jim/widgets.py` does this. `widgets` is keyed on `user_id`
    and `life.delete_user_data` derives its cascade from the schema, so a
    table added later is erased without anybody remembering to say so — and
    this is the check that the derivation actually reached it."""
    from jim import db, life

    uid = enroll(client)
    client.post(f"/users/{uid}/widgets",
                json={"name": "kept", "source": "module.exports = () => 1;"})
    assert db.connect().execute(
        "SELECT COUNT(*) c FROM widgets WHERE user_id=?", (uid,)).fetchone()["c"] == 1
    life.delete_user_data(uid)
    assert db.connect().execute(
        "SELECT COUNT(*) c FROM widgets WHERE user_id=?", (uid,)).fetchone()["c"] == 0
