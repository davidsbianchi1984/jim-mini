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


@pytest.fixture(autouse=True)
def rooms(monkeypatch):
    """Where the rooms go for a test: a directory the run can reach. pytest's
    own tmp_path sits under a 0700 directory, and a server that is root runs
    the box as ``nobody`` — the way a real base under the system temp
    directory is reachable, this one is made so."""
    import tempfile, shutil as _sh
    base = Path(tempfile.mkdtemp(prefix="jim-rooms-"))
    base.chmod(0o711)
    monkeypatch.setenv("JIM_WORKROOMS", str(base))
    yield base
    _sh.rmtree(base, ignore_errors=True)


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

def test_a_draft_that_is_not_a_diff_is_unapplied_and_no_tree_is_copied(tmp_path, monkeypatch, rooms):
    src = _tree(tmp_path / "src")
    got = workroom.try_draft("please make the button bigger", "jim/adder.py", source=src)
    assert got["status"] == "unapplied"
    assert got["detail"] == "the draft is not a unified diff, so the box cannot try it"
    assert not any(rooms.iterdir())


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
def test_a_right_draft_runs_green_inside_the_walls(tmp_path, monkeypatch, rooms):
    src = _tree(tmp_path / "src")
    got = workroom.try_draft(FIX, "jim/adder.py", source=src)
    assert got["status"] == "green", got["output"]
    assert got["tests"] == ["jim/tests/test_adder.py"] and got["passed"] == 1
    assert got["changed"] == ["jim/adder.py"]
    # The source tree itself was never written to.
    assert (src / "jim" / "adder.py").read_text() == "def add(a, b):\n    return a - b\n"
    # And the room was cleared.
    assert not any(rooms.iterdir())


@needs_box
def test_the_network_is_cut_and_every_life_on_the_disk_is_hidden(tmp_path, monkeypatch, rooms):
    src = _tree(tmp_path / "src")
    got = workroom.try_draft(WALLS, "jim/walls.py", source=src)
    assert got["status"] == "green", got["output"]
    assert got["passed"] == 3


@needs_box
def test_a_red_run_goes_back_to_the_assistant_and_the_path_is_kept(tmp_path, monkeypatch, rooms):
    src = _tree(tmp_path / "src")
    asked = []

    def again(patch, output):
        asked.append((patch, output))
        return FIX

    got = workroom.iterate(WRONG, "jim/adder.py", again, source=src)
    assert got["status"] == "green" and got["patch"] == FIX.strip()
    assert [r["status"] for r in got["rounds"]] == ["red", "green"]
    assert got["model"] == ""                       # a bare string names nobody
    assert len(asked) == 1 and "test_three_and_two" in asked[0][1]
    assert got["rounds"][0]["patch"] == WRONG and got["rounds"][1]["patch"] == FIX.strip()
    shown = workroom.summary(got)
    assert shown["status"] == "green" and shown["rounds"] == 2
    assert "patch" not in shown


@needs_box
def test_the_assistant_gets_at_most_max_rounds(tmp_path, monkeypatch, rooms):
    src = _tree(tmp_path / "src")
    calls = []
    got = workroom.iterate(WRONG, "jim/adder.py",
                           lambda p, o: (calls.append(1), WRONG.replace("a * b", f"a * b * {len(calls)}"))[1],
                           source=src)
    assert got["status"] == "red"
    assert len(got["rounds"]) == workroom.MAX_ROUNDS
    assert len(calls) == workroom.MAX_ROUNDS - 1


@needs_box
def test_an_assistant_that_fails_is_a_result_not_a_crash(tmp_path, monkeypatch, rooms):
    src = _tree(tmp_path / "src")

    def again(patch, output):
        raise RuntimeError("the model is away")

    got = workroom.iterate(WRONG, "jim/adder.py", again, source=src)
    assert got["status"] == "red" and len(got["rounds"]) == 1
    assert got["rounds"][0]["assistant_failed"].startswith("RuntimeError")


def test_the_limits_are_finite_and_the_hidden_places_are_the_lives(tmp_path, monkeypatch):
    assert workroom.LIMITS["wall_seconds"] > workroom.LIMITS["cpu_seconds"]
    assert workroom.LIMITS["processes"] < 100
    assert workroom.LIMITS["kept_bytes"] <= workroom.LIMITS["output_bytes"]
    assert workroom.LIMITS["file_bytes"] >= workroom.LIMITS["output_bytes"]
    assert set(workroom.HIDDEN) >= {"/home", "/root"}
    assert {".git", "node_modules", "*.db", "*.db-wal", ".env"} <= workroom.SKIP
    # The lives are hidden wherever this host keeps them, not only at the
    # fixed places: the database's directory, the checkout, the console.
    monkeypatch.setenv("JIM_DB", str(tmp_path / "vault" / "jim.db"))
    monkeypatch.setenv("JIM_CONSOLE_DIR", str(tmp_path / "console"))
    places = workroom.hidden()
    assert str((tmp_path / "vault").resolve()) in places
    assert str((tmp_path / "console").resolve()) in places
    assert str(workroom.REPO.resolve()) in places
    # The pid namespace and the reaper are on the command line.
    assert "-rmnp" in workroom._UNSHARE_ARGS
    assert any(a.startswith("--kill-child") for a in workroom._UNSHARE_ARGS)


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
    assert got["status"] == "refused"
    assert got["detail"] == "the assistant's box is not available on this host"


def test_a_base_inside_a_hidden_place_makes_the_box_unavailable(monkeypatch):
    monkeypatch.setattr(workroom, "_AVAILABLE", None)
    monkeypatch.setenv("JIM_WORKROOMS", "/home/nobody/rooms")
    assert workroom.available() == (False, "the assistant's box is not available on this host")
    monkeypatch.setattr(workroom, "_AVAILABLE", None)


# --- what the review found -------------------------------------------------------

def test_the_database_and_the_secrets_are_never_copied_into_the_room(tmp_path, monkeypatch, rooms):
    src = _tree(tmp_path / "src")
    for name in ("jim.db", "jim.db-wal", "jim.db-shm", ".env", ".env.local", "notes.sqlite3"):
        (src / name).write_text("private")
    (src / "vault.db").write_text("private")
    monkeypatch.setenv("JIM_DB", str(src / "vault.db"))
    room, changed = workroom.build(FIX, src)
    try:
        tree = room / "tree"
        assert (tree / "jim" / "adder.py").exists()
        for name in ("jim.db", "jim.db-wal", "jim.db-shm", ".env", ".env.local",
                     "notes.sqlite3", "vault.db"):
            assert not (tree / name).exists(), name
    finally:
        workroom.discard(room)


def test_a_draft_that_does_not_apply_leaves_no_room_behind(tmp_path, monkeypatch, rooms):
    src = _tree(tmp_path / "src")
    with pytest.raises(ValueError):
        workroom.build(FIX.replace("return a - b", "return a / b"), src)
    assert not any(rooms.iterdir())
    # A header naming a directory, or a binary file, is a constant sentence
    # and not a crash.
    (src / "jim" / "icon.png").write_bytes(b"\x89PNG\xff\xfe")
    for header in ("+++ b/jim", "+++ b/jim/icon.png"):
        got = workroom.try_draft(FIX.replace("+++ b/jim/adder.py", header), source=src)
        assert got["status"] == "unapplied", header
        assert got["detail"] == "the draft does not fit the file it changes, so the box cannot try it"
    assert not any(rooms.iterdir())


GIT_STYLE = textwrap.dedent("""\
    The adder subtracted, and the walls were not counted.

    ```diff
    diff --git a/jim/adder.py b/jim/adder.py
    index 1111111..2222222 100644
    --- a/jim/adder.py
    +++ b/jim/adder.py
    @@ -1,2 +1,2 @@
     def add(a, b):
    -    return a - b
    +    return a + b
    diff --git a/jim/walls.py b/jim/walls.py
    index 3333333..4444444 100644
    --- a/jim/walls.py
    +++ b/jim/walls.py
    @@ -1 +1 @@
    -WALLS = 4
    +WALLS = 4  # counted
    ```
    """)


def test_a_git_style_diff_over_two_files_with_a_fence_applies_whole(tmp_path):
    src = _tree(tmp_path / "src")
    assert workroom.apply_patch(src, GIT_STYLE) == ["jim/adder.py", "jim/walls.py"]
    assert "return a + b" in (src / "jim" / "adder.py").read_text()
    assert (src / "jim" / "walls.py").read_text() == "WALLS = 4  # counted\n"


def test_a_removed_line_that_starts_with_two_dashes_is_not_a_header(tmp_path):
    src = _tree(tmp_path / "src")
    (src / "jim" / "schema.sql").write_text("CREATE TABLE a (x);\n-- the audit table\nCREATE TABLE b (y);\n")
    patch = textwrap.dedent("""\
        --- a/jim/schema.sql
        +++ b/jim/schema.sql
        @@ -1,3 +1,3 @@
         CREATE TABLE a (x);
        --- the audit table
        +-- the record
         CREATE TABLE b (y);
        """)
    assert workroom.apply_patch(src, patch) == ["jim/schema.sql"]
    assert (src / "jim" / "schema.sql").read_text() == "CREATE TABLE a (x);\n-- the record\nCREATE TABLE b (y);\n"


def test_a_deletion_deletes_and_a_zero_context_insertion_lands_after_the_line(tmp_path):
    src = _tree(tmp_path / "src")
    gone = "--- a/jim/walls.py\n+++ /dev/null\n@@ -1 +0,0 @@\n-WALLS = 4\n"
    assert workroom.apply_patch(src, gone) == ["jim/walls.py"]
    assert not (src / "jim" / "walls.py").exists()
    (src / "f.txt").write_text("l1\nl2\nl3\nl4\n")
    assert workroom.apply_patch(src, "--- a/f.txt\n+++ b/f.txt\n@@ -2,0 +3 @@\n+X\n") == ["f.txt"]
    assert (src / "f.txt").read_text() == "l1\nl2\nX\nl3\nl4\n"
    # A new file.
    born = "--- /dev/null\n+++ b/jim/new.py\n@@ -0,0 +1,2 @@\n+a = 1\n+b = 2\n"
    assert workroom.apply_patch(src, born) == ["jim/new.py"]
    assert (src / "jim" / "new.py").read_text() == "a = 1\nb = 2\n"


def test_a_plus_line_in_the_prose_is_not_a_file_header(tmp_path):
    src = _tree(tmp_path / "src")
    assert workroom.apply_patch(src, "+++ more\n" + FIX) == ["jim/adder.py"]
    assert not (src / "more").exists()
    assert workroom.touched_files("+++ more\n" + FIX) == ["jim/adder.py"]


@needs_box
def test_nothing_the_run_starts_outlives_it(tmp_path, monkeypatch, rooms):
    """A detached grandchild dies with the run: the pid namespace's pid 1
    is killed at the wall clock, and everything under it goes too."""
    import subprocess
    src = _tree(tmp_path / "src")
    (src / "jim" / "tests" / "test_walls.py").write_text(textwrap.dedent("""\
        import subprocess, time
        from jim.walls import WALLS

        def test_leaves_a_daemon_behind():
            subprocess.Popen(["setsid", "sh", "-c", "exec sleep 654321"], start_new_session=True)
            time.sleep(30)
        """))
    monkeypatch.setitem(workroom.LIMITS, "wall_seconds", 4)
    got = workroom.try_draft(WALLS, "jim/walls.py", source=src)
    assert got["status"] == "timeout"
    assert got["detail"] == "the tests ran longer than the box allows"
    left = subprocess.run(["pgrep", "-f", "sleep 654321"], capture_output=True, text=True)
    assert left.stdout.strip() == "", "a process outlived the box"


@needs_box
def test_the_output_a_person_reads_is_the_tail_and_the_server_never_holds_it_all(tmp_path, monkeypatch, rooms):
    src = _tree(tmp_path / "src")
    (src / "jim" / "tests" / "test_walls.py").write_text(textwrap.dedent("""\
        import sys
        from jim.walls import WALLS

        def test_talks_too_much():
            for _ in range(3000):
                sys.stdout.write("x" * 1000 + "\\n")
            sys.stdout.write("THE-LAST-WORD\\n")
            assert False
        """))
    got = workroom.try_draft(WALLS, "jim/walls.py", source=src)
    assert got["status"] == "red"
    assert len(got["output"].encode()) <= workroom.LIMITS["kept_bytes"]
    assert "THE-LAST-WORD" in got["output"]


@needs_box
def test_tests_that_collect_nothing_are_said_so_and_the_assistant_is_not_asked(tmp_path, monkeypatch, rooms):
    src = _tree(tmp_path / "src")
    (src / "jim" / "tests" / "test_walls.py").write_text("from jim.walls import WALLS\n")
    asked = []
    got = workroom.iterate(WALLS, "jim/walls.py", lambda p, o: asked.append(1) or FIX, source=src)
    assert got["status"] == "red" and len(got["rounds"]) == 1
    assert got["rounds"][0]["detail"] == "the named tests collected nothing, so nothing was tried"
    assert asked == []


@needs_box
def test_a_revision_that_is_not_a_diff_never_replaces_the_draft_on_file(tmp_path, monkeypatch, rooms):
    src = _tree(tmp_path / "src")
    got = workroom.iterate(WRONG, "jim/adder.py",
                           lambda p, o: ("Sorry, I cannot produce a diff.", "stub"), source=src)
    assert got["status"] == "unapplied" and len(got["rounds"]) == 2
    assert got["patch"] == WRONG                    # the last draft that applied
    assert got["rounds"][1]["patch"] == "Sorry, I cannot produce a diff."
    assert got["rounds"][1]["model"] == "stub"


def test_a_degraded_answer_is_no_revision(monkeypatch):
    monkeypatch.setattr(appedits.llm, "generate_for_user",
                        lambda *a, **k: {"text": "stub words", "provider": "stub", "degraded": True})
    assert appedits._again("u1", "auto")(WRONG, "boom") == ("", "stub")


# --- the door, the owner, and oversight ----------------------------------------

def _file(client, uid, patch):
    r = client.post(f"/appedits/{uid}", json={
        "title": "Two and two", "description": "the adder subtracts",
        "target": "jim/adder.py", "patch": patch})
    assert r.status_code == 201, r.text
    return r.json()["id"]


@needs_box
def test_the_door_tries_the_owners_draft_and_oversight_reads_the_fact(client, tmp_path, monkeypatch, rooms):
    monkeypatch.delenv("JIM_SELF_HOSTED", raising=False)
    monkeypatch.setattr(workroom, "REPO", _tree(tmp_path / "src"))
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
def test_a_red_draft_is_revised_by_the_assistant_through_the_door(client, tmp_path, monkeypatch, rooms):
    monkeypatch.setattr(workroom, "REPO", _tree(tmp_path / "src"))
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


@needs_box
def test_a_decided_edit_is_frozen_but_a_self_hosted_owner_may_still_try_theirs(client, tmp_path, monkeypatch, rooms):
    monkeypatch.setattr(workroom, "REPO", _tree(tmp_path / "src"))
    monkeypatch.delenv("JIM_SELF_HOSTED", raising=False)
    uid = enroll(client)
    eid = _file(client, uid, FIX)
    monkeypatch.setenv("JIM_ADMIN_TOKEN", "rev-secret")
    hdr = {"Authorization": "Bearer rev-secret"}
    assert client.post(f"/appedits/oversight/{eid}/decide", headers=hdr,
                       json={"action": "approve"}).status_code == 200
    r = client.post(f"/appedits/{uid}/{eid}/box", json={})
    assert r.status_code == 422
    assert r.json()["detail"] == "this app edit is already decided"
    assert client.get(f"/appedits/{uid}").json()["edits"][0]["patch"] == FIX
    # On their own server the owner is the oversight: approved on arrival,
    # and still theirs to try.
    monkeypatch.setenv("JIM_SELF_HOSTED", "1")
    own = _file(client, uid, FIX)
    assert client.get(f"/appedits/{uid}").json()["edits"][0]["state"] == "approved"
    r = client.post(f"/appedits/{uid}/{own}/box", json={})
    assert r.status_code == 200 and r.json()["box"]["status"] == "green"


def test_one_edit_is_in_the_box_once_and_the_box_holds_two(client, monkeypatch):
    monkeypatch.setattr(workroom, "_AVAILABLE", (True, ""))
    uid = enroll(client)
    eid = _file(client, uid, FIX)
    monkeypatch.setattr(appedits, "_IN_FLIGHT", {eid})
    r = client.post(f"/appedits/{uid}/{eid}/box", json={})
    assert r.status_code == 409 and r.json()["detail"] == "that edit is already in the box"
    monkeypatch.setattr(appedits, "_IN_FLIGHT", set())
    import threading
    monkeypatch.setattr(appedits, "_SLOTS", threading.BoundedSemaphore(1))
    appedits._SLOTS.acquire()
    r = client.post(f"/appedits/{uid}/{eid}/box", json={})
    assert r.status_code == 422
    assert r.json()["detail"] == "the assistant's box is busy, so try again in a moment"
    appedits._SLOTS.release()
    assert appedits.BOX_SLOTS == 2


@needs_box
def test_a_decision_taken_while_the_box_ran_wins(client, tmp_path, monkeypatch, rooms):
    monkeypatch.setattr(workroom, "REPO", _tree(tmp_path / "src"))
    monkeypatch.delenv("JIM_SELF_HOSTED", raising=False)
    uid = enroll(client)
    eid = _file(client, uid, FIX)
    real = workroom.iterate

    def decide_meanwhile(*a, **k):
        appedits.decide(eid, "reject", by="oversight", note="no")
        return real(*a, **k)
    monkeypatch.setattr(workroom, "iterate", decide_meanwhile)
    r = client.post(f"/appedits/{uid}/{eid}/box", json={})
    assert r.status_code == 422
    assert r.json()["detail"] == "this app edit was decided while the box was running"
    row = client.get(f"/appedits/{uid}").json()["edits"][0]
    assert row["state"] == "rejected" and row["box"] is None and row["patch"] == FIX


def test_the_boxs_sentence_reaches_the_reader_in_their_language(client, monkeypatch):
    monkeypatch.setattr(workroom, "_AVAILABLE", (True, ""))
    uid = enroll(client)
    from jim import i18n
    i18n.set_language(uid, "es")
    eid = _file(client, uid, "make the button bigger")
    r = client.post(f"/appedits/{uid}/{eid}/box", json={})
    assert r.status_code == 200
    spanish = i18n.tr_refusal("the draft is not a unified diff, so the box cannot try it", "es")
    assert spanish != "the draft is not a unified diff, so the box cannot try it"
    assert r.json()["box"]["detail"] == spanish
    assert client.get(f"/appedits/{uid}").json()["edits"][0]["box"]["detail"] == spanish
    # Oversight reads it in the reviewer's language, negotiated from the header.
    monkeypatch.setenv("JIM_ADMIN_TOKEN", "rev-secret")
    q = client.get("/appedits/oversight/queue",
                   headers={"Authorization": "Bearer rev-secret", "Accept-Language": "fr"}).json()
    row = next(x for x in q["awaiting"] if x["id"] == eid)
    assert row["box"]["detail"] == i18n.tr_refusal("the draft is not a unified diff, so the box cannot try it", "fr")


@needs_box
def test_the_revised_draft_names_who_revised_it(client, tmp_path, monkeypatch, rooms):
    monkeypatch.setattr(workroom, "REPO", _tree(tmp_path / "src"))
    monkeypatch.setattr(appedits, "_again", lambda uid, choice: (lambda p, o: (FIX, "mistral")))
    uid = enroll(client)
    eid = _file(client, uid, WRONG)
    r = client.post(f"/appedits/{uid}/{eid}/box", json={})
    assert r.status_code == 200 and r.json()["patch"] == FIX.strip()
    assert r.json()["model"] == "mistral"


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
