"""The coding assistant gets a box — write, run, iterate, then oversight.

The owner's ask, pinned: the assistant that writes a change to the app has an
environment of its own to try the change in — not the widget box, which runs
a person's JavaScript, but a room where the repository with the draft applied
runs its own tests, with the network cut, every other life on the disk hidden,
processes counted, time and memory finite. A red run is handed back to the
assistant for another try; every round is filed beside the diff; oversight
reads a fact and not a guess. The box decides nothing — an approved edit still
rides the next publish-merge, and nothing here touches running code.

The tests here run a real box on a small synthetic tree, so a host without
user namespaces skips the runs and keeps the refusal.
"""

from __future__ import annotations

import os
import textwrap
from pathlib import Path

import pytest

from jim import appedits, db, workroom
from jim.tests.conftest import enroll

BOX_HERE = workroom.available()[0]
needs_box = pytest.mark.skipif(not BOX_HERE, reason="no user namespaces on this host")


def _actions(uid):
    return [r["action"] for r in db.connect().execute(
        "SELECT action FROM audit WHERE user_id=? ORDER BY seq", (uid,)).fetchall()]


def _tree(root: Path) -> Path:
    """A repository in miniature: a module with a bug, and the tests that
    would catch it, laid out the way this one is."""
    (root / "jim" / "tests").mkdir(parents=True)
    (root / "jim" / "__init__.py").write_text("")
    (root / "jim" / "tests" / "__init__.py").write_text("")
    (root / "jim" / "adder.py").write_text("def add(a, b):\n    return a - b\n")
    (root / "jim" / "tests" / "test_adder.py").write_text(textwrap.dedent("""\
        from jim.adder import add

        def test_three_and_two():
            assert add(3, 2) == 5
        """))
    (root / "jim" / "walls.py").write_text("WALLS = 4\n")
    (root / "jim" / "tests" / "test_walls.py").write_text(textwrap.dedent("""\
        import os, socket
        from jim.walls import WALLS

        def test_the_network_is_cut():
            try:
                socket.create_connection(("1.1.1.1", 443), timeout=2)
            except OSError:
                return
            raise AssertionError("the box reached the network")

        def test_every_life_on_the_disk_is_hidden():
            for place in ("/home", "/root", "/srv", "/data"):
                if os.path.isdir(place):
                    assert os.listdir(place) == [], place

        def test_the_walls_are_counted():
            assert WALLS == 4
        """))
    return root


FIX = textwrap.dedent("""\
    Three and two make five. The adder subtracted.

    --- a/jim/adder.py
    +++ b/jim/adder.py
    @@ -1,2 +1,2 @@
     def add(a, b):
    -    return a - b
    +    return a + b
    """)

WRONG = FIX.replace("return a + b", "return a * b")

WALLS = textwrap.dedent("""\
    --- a/jim/walls.py
    +++ b/jim/walls.py
    @@ -1 +1 @@
    -WALLS = 4
    +WALLS = 4  # counted
    """)


# --- the draft as a diff ------------------------------------------------------

def test_a_draft_that_is_not_a_diff_is_unapplied_and_no_tree_is_copied(tmp_path, monkeypatch):
    src = _tree(tmp_path / "src")
    monkeypatch.setenv("JIM_WORKROOMS", str(tmp_path / "rooms"))
    got = workroom.try_draft("please make the button bigger", "jim/adder.py", source=src)
    assert got["status"] == "unapplied"
    assert got["detail"] == "the draft is not a unified diff, so the box cannot try it"
    assert not (tmp_path / "rooms").exists() or not any((tmp_path / "rooms").iterdir())


def test_a_draft_reaching_outside_the_tree_is_refused(tmp_path):
    src = _tree(tmp_path / "src")
    escape = FIX.replace("+++ b/jim/adder.py", "+++ b/../../etc/passwd")
    got = workroom.try_draft(escape, source=src)
    assert got["status"] == "unapplied"
    assert "reaches outside the tree" in got["detail"]
    assert workroom.touched_files(FIX) == ["jim/adder.py"]


def test_a_hunk_that_does_not_fit_is_said_so(tmp_path):
    src = _tree(tmp_path / "src")
    got = workroom.try_draft(FIX.replace("return a - b", "return a / b"), source=src)
    assert got["status"] == "unapplied"
    assert "does not fit the file it changes" in got["detail"]


def test_the_tests_tried_are_the_ones_the_draft_names(tmp_path):
    src = _tree(tmp_path / "src")
    assert workroom.tests_for(src, ["jim/adder.py"]) == ["jim/tests/test_adder.py"]
    assert workroom.tests_for(src, [], "jim/walls.py") == ["jim/tests/test_walls.py"]
    assert workroom.tests_for(src, ["jim/tests/test_walls.py"]) == ["jim/tests/test_walls.py"]
    assert workroom.tests_for(src, ["README.md"]) == []


# --- the box runs ----------------------------------------------------------------

@needs_box
def test_a_right_draft_runs_green_inside_the_walls(tmp_path, monkeypatch):
    src = _tree(tmp_path / "src")
    monkeypatch.setenv("JIM_WORKROOMS", str(tmp_path / "rooms"))
    got = workroom.try_draft(FIX, "jim/adder.py", source=src)
    assert got["status"] == "green", got["output"]
    assert got["tests"] == ["jim/tests/test_adder.py"] and got["passed"] == 1
    assert got["changed"] == ["jim/adder.py"]
    # The source tree itself was never written to.
    assert (src / "jim" / "adder.py").read_text() == "def add(a, b):\n    return a - b\n"
    # And the room was cleared.
    assert not any((tmp_path / "rooms").iterdir())


@needs_box
def test_the_network_is_cut_and_every_life_on_the_disk_is_hidden(tmp_path, monkeypatch):
    src = _tree(tmp_path / "src")
    monkeypatch.setenv("JIM_WORKROOMS", str(tmp_path / "rooms"))
    got = workroom.try_draft(WALLS, "jim/walls.py", source=src)
    assert got["status"] == "green", got["output"]
    assert got["passed"] == 3


@needs_box
def test_a_red_run_goes_back_to_the_assistant_and_the_path_is_kept(tmp_path, monkeypatch):
    src = _tree(tmp_path / "src")
    monkeypatch.setenv("JIM_WORKROOMS", str(tmp_path / "rooms"))
    asked = []

    def again(patch, output):
        asked.append((patch, output))
        return FIX

    got = workroom.iterate(WRONG, "jim/adder.py", again, source=src)
    assert got["status"] == "green" and got["patch"] == FIX.strip()
    assert [r["status"] for r in got["rounds"]] == ["red", "green"]
    assert len(asked) == 1 and "test_three_and_two" in asked[0][1]
    assert got["rounds"][0]["patch"] == WRONG and got["rounds"][1]["patch"] == FIX.strip()
    shown = workroom.summary(got)
    assert shown["status"] == "green" and shown["rounds"] == 2
    assert "patch" not in shown


@needs_box
def test_the_assistant_gets_at_most_max_rounds(tmp_path, monkeypatch):
    src = _tree(tmp_path / "src")
    monkeypatch.setenv("JIM_WORKROOMS", str(tmp_path / "rooms"))
    calls = []
    got = workroom.iterate(WRONG, "jim/adder.py",
                           lambda p, o: (calls.append(1), WRONG.replace("a * b", f"a * b * {len(calls)}"))[1],
                           source=src)
    assert got["status"] == "red"
    assert len(got["rounds"]) == workroom.MAX_ROUNDS
    assert len(calls) == workroom.MAX_ROUNDS - 1


@needs_box
def test_an_assistant_that_fails_is_a_result_not_a_crash(tmp_path, monkeypatch):
    src = _tree(tmp_path / "src")
    monkeypatch.setenv("JIM_WORKROOMS", str(tmp_path / "rooms"))

    def again(patch, output):
        raise RuntimeError("the model is away")

    got = workroom.iterate(WRONG, "jim/adder.py", again, source=src)
    assert got["status"] == "red" and len(got["rounds"]) == 1
    assert got["rounds"][0]["assistant_failed"].startswith("RuntimeError")


def test_the_limits_are_finite_and_the_hidden_places_are_the_lives():
    assert workroom.LIMITS["wall_seconds"] > workroom.LIMITS["cpu_seconds"]
    assert workroom.LIMITS["processes"] < 100
    assert workroom.LIMITS["kept_bytes"] <= workroom.LIMITS["output_bytes"]
    assert set(workroom.HIDDEN) >= {"/home", "/root"}
    assert ".git" in workroom.SKIP and "node_modules" in workroom.SKIP


# --- the refusal that matters ---------------------------------------------------

def test_without_four_walls_the_box_runs_nothing(tmp_path, monkeypatch):
    src = _tree(tmp_path / "src")
    monkeypatch.setattr(workroom, "_AVAILABLE",
                        (False, "the assistant's box is not available on this host"))
    got = workroom.try_draft(FIX, "jim/adder.py", source=src)
    assert got["status"] == "refused"
    assert got["detail"] == "the assistant's box is not available on this host"
    assert appedits.posture()["box_available"] is False


def test_a_room_inside_a_hidden_place_is_refused(tmp_path, monkeypatch):
    src = _tree(tmp_path / "src")
    monkeypatch.setattr(workroom, "_AVAILABLE", (True, ""))
    monkeypatch.setenv("JIM_WORKROOMS", "/home/nobody/rooms")
    monkeypatch.setattr(workroom, "build",
                        lambda patch, source=None: (Path("/home/nobody/rooms/room-x"), ["jim/adder.py"]))
    monkeypatch.setattr(workroom, "discard", lambda room: None)
    got = workroom.try_draft(FIX, "jim/adder.py", source=src)
    assert got["status"] == "refused" and "JIM_WORKROOMS" in got["detail"]


# --- the door, the owner, and oversight ----------------------------------------

def _file(client, uid, patch):
    r = client.post(f"/appedits/{uid}", json={
        "title": "Two and two", "description": "the adder subtracts",
        "target": "jim/adder.py", "patch": patch})
    assert r.status_code == 201, r.text
    return r.json()["id"]


@needs_box
def test_the_door_tries_the_owners_draft_and_oversight_reads_the_fact(client, tmp_path, monkeypatch):
    monkeypatch.delenv("JIM_SELF_HOSTED", raising=False)
    monkeypatch.setattr(workroom, "REPO", _tree(tmp_path / "src"))
    monkeypatch.setenv("JIM_WORKROOMS", str(tmp_path / "rooms"))
    uid = enroll(client)
    assert client.get(f"/appedits/{uid}").json()["posture"]["box_available"] is True
    eid = _file(client, uid, FIX)
    mine = client.get(f"/appedits/{uid}").json()["edits"][0]
    assert mine["box"] is None
    r = client.post(f"/appedits/{uid}/{eid}/box", json={})
    assert r.status_code == 200, r.text
    box = r.json()["box"]
    assert box["status"] == "green" and box["rounds"] == 1 and box["passed"] == 1
    assert r.json()["state"] == "proposed"        # tried, not decided
    assert "appedit.boxed" in _actions(uid)
    monkeypatch.setenv("JIM_ADMIN_TOKEN", "rev-secret")
    q = client.get("/appedits/oversight/queue",
                   headers={"Authorization": "Bearer rev-secret"}).json()
    row = next(x for x in q["awaiting"] if x["id"] == eid)
    assert row["box"]["status"] == "green" and row["box"]["tests"] == ["jim/tests/test_adder.py"]
    assert q["posture"]["apply_wired"] is False


@needs_box
def test_a_red_draft_is_revised_by_the_assistant_through_the_door(client, tmp_path, monkeypatch):
    monkeypatch.setattr(workroom, "REPO", _tree(tmp_path / "src"))
    monkeypatch.setenv("JIM_WORKROOMS", str(tmp_path / "rooms"))
    monkeypatch.setattr(appedits, "_again", lambda uid, choice: (lambda p, o: FIX))
    uid = enroll(client)
    eid = _file(client, uid, WRONG)
    r = client.post(f"/appedits/{uid}/{eid}/box", json={})
    assert r.status_code == 200, r.text
    assert r.json()["box"]["status"] == "green" and r.json()["box"]["rounds"] == 2
    assert r.json()["patch"] == FIX.strip()         # the draft on file is the revised one


def test_the_door_is_the_owners_and_a_non_diff_is_unapplied(client, monkeypatch):
    monkeypatch.setattr(workroom, "_AVAILABLE", (True, ""))
    uid = enroll(client)
    eid = _file(client, uid, "make the button bigger")
    r = client.post(f"/appedits/{uid}/{eid}/box", json={})
    assert r.status_code == 200
    assert r.json()["box"]["status"] == "unapplied"
    assert "appedit.box_refused" in _actions(uid)
    # Somebody else's edit reads as no edit.
    other_token = client.headers["authorization"]
    uid2 = enroll(client)
    r = client.post(f"/appedits/{uid2}/{eid}/box", json={})
    assert r.status_code == 404
    assert client.post(f"/appedits/{uid2}/aed_nothing/box", json={}).status_code == 404
    del other_token


def test_without_a_box_the_door_refuses_in_a_sentence(client, monkeypatch):
    monkeypatch.setattr(workroom, "_AVAILABLE",
                        (False, "the assistant's box is not available on this host"))
    uid = enroll(client)
    assert client.get(f"/appedits/{uid}").json()["posture"]["box_available"] is False
    eid = _file(client, uid, FIX)
    r = client.post(f"/appedits/{uid}/{eid}/box", json={})
    assert r.status_code == 422
    assert r.json()["detail"] == "the assistant's box is not available on this host"
    assert "appedit.box_refused" in _actions(uid)


def test_a_model_off_the_menu_is_refused_at_the_box_too(client, monkeypatch):
    monkeypatch.setattr(workroom, "_AVAILABLE", (True, ""))
    uid = enroll(client)
    eid = _file(client, uid, FIX)
    r = client.post(f"/appedits/{uid}/{eid}/box", json={"model": "zhipu"})
    assert r.status_code == 422


def test_the_box_never_applies_and_never_deploys():
    """Pinned in source: the workroom module names no deploy, no git push,
    no write to the repository it copies from."""
    src = Path(workroom.__file__).read_text(encoding="utf-8")
    for word in ("git push", "docker", "systemctl", "REPO / ", "REPO.write"):
        assert word not in src, word
    assert "copytree(src, tree" in src            # a copy, never the tree itself
    assert appedits.posture()["apply_wired"] is False
