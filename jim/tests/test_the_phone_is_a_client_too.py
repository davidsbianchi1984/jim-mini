"""And so is each phone. The same question the console guard asks, one
surface over — and it has been going unasked for exactly as long.

`test_the_console_is_a_client_too.py` was written because the union guard
answered *some client can reach this*, which was true, in place of *this
client can reach this*, which was not. It fixed that for the console. The
console backlog is now zero.

It fixed it for **one** client. There are four.

                      at the start of this round    now
    union doorless                         0          0
    console                                0          0
    ios                                  145        140
    android                              154        147
    windows                              146        141

Three quarters of JIM's routes were unreachable from the phone, and until this
file nothing anywhere said so. The movement is the alarm block below, plus one
route on Android that was never missing at all — see `clientpaths`, where the
Kotlin extractor could not see the direct-connection form a JSON **array**
response has to use, so `GET /baseline/{user_id}` had a working door in that
shell and was counted doorless for the whole audit. The console guard's own docstring contains the
sentence that should have led here, and did not:

    a phone-only capability is a legitimate design choice, and it is: a
    camera roll has no business on a desktop

That is true, and its converse is louder: a **desktop-only** capability is
also a design choice, and it needs making rather than defaulting into. The
number above is not a list of things to build. It is a list of things nobody
has decided about.

## Why this is the more serious direction

The console gap was an owner who could not post a licence offer from a desk.
Inconvenient, and a desk is not the only place they could do it.

The phone gap is different in kind, because for a guardian product the phone
is the **crisis surface**. It is the thing a person has on them. What this
guard found on its first run:

  * `GET  /users/{id}/alarms`                   — cannot see an open alarm
  * `POST /users/{id}/alarms/{aid}/accept`      — cannot say "I have this"
  * `POST /users/{id}/alarms/{aid}/clear`       — cannot stand one down
  * `POST /users/{id}/alarms/{aid}/escalate`    — cannot push it up
  * `POST /alarms/{aid}/guidance`               — cannot ask what to do

Zero occurrences of the word *alarm* in the iOS, Android or Windows shell.

`relay.accept(user_id, alarm_id, responder)` takes a **responder** — the
neighbour, the on-call carer, the person the household relay pages. Accepting
is the act that stops the ladder climbing to emergency services. So the
person who was paged, holding the device they were paged on, had no way to
answer, and the only path left was the one that ends in an ambulance.

The phone could already *raise* an emergency, and command a bound robot to
perform CPR. It could not answer the alarm about it.

The vigil — the alarm that fires when a person's signals stop entirely — and
the care beacon a stranger scans on a door are absent from the phones for the
same reason: nobody was counting.

## What this file is not

It is not a demand that every route reach every client. It is the ratchet
that makes the split deliberate: deferring a route means writing a line in
the snapshot, which takes an edit and shows in a diff. The difference between
a decision and an oversight is whether anybody made it.
"""

from __future__ import annotations

from pathlib import Path

from jim.api import app

from . import clientpaths

HERE = Path(__file__).resolve().parent

#: One snapshot per shell. Separate files rather than one, because the shells
#: diverge for real reasons — Windows has no camera roll, iOS has HealthKit —
#: and a single list would hide which of them a line belongs to.
SNAPSHOTS = {
    "ios": HERE / "ios_doorless.txt",
    "android": HERE / "android_doorless.txt",
    "windows": HERE / "windows_doorless.txt",
}

#: Where each stood when this guard was written, so the direction of travel is
#: a fact in the file rather than a claim in a commit message.
STARTED_AT = {"ios": 145, "android": 154, "windows": 146}


def _surface(name: str):
    for lang in clientpaths.NATIVE:
        if lang.name == name:
            return lang
    raise AssertionError(f"no native surface named {name!r}")


def _recorded(name: str) -> list[str]:
    return [line.strip() for line in
            SNAPSHOTS[name].read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")]


def _actual(name: str) -> list[str]:
    return clientpaths.doorless(app, surfaces=(_surface(name),))


def test_each_shell_backlog_matches_its_record():
    """Both directions, per shell.

    A route that has gained a door on a phone is as much a change to report
    as one that has lost it — a file only checked for growth becomes a list
    of things that were true once.
    """
    problems = []
    for name in SNAPSHOTS:
        actual, recorded = set(_actual(name)), set(_recorded(name))
        appeared, resolved = sorted(actual - recorded), sorted(recorded - actual)
        if appeared:
            problems.append(
                f"{name}: {len(appeared)} route(s) the shell cannot reach:\n    "
                + "\n    ".join(appeared)
                + "\n  (build the door, or record it here with the reason)")
        if resolved:
            problems.append(
                f"{name}: {len(resolved)} route(s) now have a door — strike "
                f"them from {SNAPSHOTS[name].name}:\n    "
                + "\n    ".join(resolved))
    assert not problems, "\n\n".join(problems)


def test_each_backlog_only_shrinks():
    """A ratchet per shell. None of these is zero and none has to be — what
    they must not do is grow."""
    for name, started in STARTED_AT.items():
        assert len(_recorded(name)) <= started, (
            f"the {name} backlog is {len(_recorded(name))}, above the "
            f"{started} it started at — routes are being added faster than "
            "doors")


def test_the_union_is_never_worse_than_any_single_shell():
    """Arithmetic, not policy: every shell is one of the union's own
    surfaces, so the union cannot be missing something a shell reaches."""
    union = set(clientpaths.doorless(app))
    for name in SNAPSHOTS:
        assert union <= set(_actual(name)), (
            f"a route is doorless everywhere but reachable from {name}, "
            "which means the two are computed over different route tables")


# --- the crisis surface -----------------------------------------------------

#: Routes a phone must reach because the phone is the device a person has on
#: them when it matters. Unlike the snapshots above, this list is **not**
#: deferrable: a line here cannot be answered by recording it somewhere.
CRISIS_PATHS = (
    "GET /users/{user_id}/alarms",
    "POST /users/{user_id}/alarms/{alarm_id}/accept",
    "POST /users/{user_id}/alarms/{alarm_id}/clear",
    "POST /users/{user_id}/alarms/{alarm_id}/escalate",
    "POST /alarms/{alarm_id}/guidance",
)


def test_every_shell_can_answer_an_alarm():
    """The one thing no shell may defer.

    Accepting an alarm is how a paged responder says *I have this*, and it is
    what stops the escalation ladder climbing to emergency services. A person
    paged on their phone, holding that phone, must be able to answer on it.

    This is not a snapshot and there is no line to add. If a shell cannot
    reach these, the shell is wrong.
    """
    missing = []
    for name in SNAPSHOTS:
        cannot = set(_actual(name))
        missing += [f"{name}: {p}" for p in CRISIS_PATHS if p in cannot]
    assert not missing, (
        "a shell cannot answer an alarm:\n    " + "\n    ".join(missing)
        + "\n  Accepting is what stops the ladder reaching emergency "
          "services; the phone is the device the responder was paged on.")


def test_the_crisis_paths_are_real_routes():
    """A guard on the guard. If one of these is renamed in the backend, this
    file would silently stop checking anything — the list would simply never
    match, and every shell would 'pass'."""
    routed = {f"{m} {r.path}"
              for r in clientpaths.all_routes(app)
              for m in (r.methods or set()) - {"HEAD", "OPTIONS"}}
    unknown = [p for p in CRISIS_PATHS if p not in routed]
    assert not unknown, (
        "these are not routes in the app any more, so the check above is "
        f"vacuous:\n    " + "\n    ".join(unknown))
