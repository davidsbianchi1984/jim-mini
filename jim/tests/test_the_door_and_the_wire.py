"""The last hundred and nine doors, and what building them found.

This closes JIM's console backlog. It stood at 109 — routes reachable from
the phone shells and from no part of the desktop app — and it is now zero, as
is the unused-binding record and the union backlog next to it. All three
files are empty rather than merely short, and the tests below assert
emptiness rather than a number.

## What building the doors found

Nothing in the backend was broken. That is worth saying plainly, because the
previous eight rounds each turned up a real defect and it would be easy to
manufacture a ninth. What this round found instead was **six places where the
route table and the wire disagree**, every one of them caught by calling the
route against a running server rather than reading its signature:

1. `GET /access-log/{uid}` returns an object, not an array. Its `entries`
   field is one of four, and the other three are the answer to *is anything
   even being recorded* — which, on a deployment with no vault, is **no**. A
   binding typed as a list would have mapped over an object, rendered
   nothing, and shown a person an empty access log when the truth was that no
   log exists. Those two facts are opposites.

2. `GET /custody/{uid}/provenance` requires a `key` query parameter.

3. `GET /users/{uid}/referral/clinicians` requires `condition`.

4. `GET /c/{bid}` serves **HTML** and `…/qr.svg` serves **SVG**. Bound through
   the JSON helper, which falls back to `null` on a body it cannot parse,
   both came back as `null` silently. A content type is part of a route's
   shape and appears in no signature.

5. `GET /social/connection/{cid}/beacon` and its `qr.svg` want the owner's
   token, where the placed-code pair at `/c/{bid}` deliberately does not.
   That asymmetry is correct — a care code on a front door is *for* strangers
   and somebody's Mastodon address is not — and it is invisible from outside.

6. `POST /emergency/{uid}` **takes a credential**. The first version of that
   binding did not pass one, on the reasonable-sounding premise that an
   emergency is the moment a person is least able to produce a token. The
   server's answer is better than the premise: an uncredentialed emergency
   route lets anybody raise `emergency_services` against anybody's account.
   The uncredentialed door for a bystander already exists and is a different
   one — `POST /c/{bid}/alarm`, off a scanned code, capped at
   `notify_contact`. A stranger wakes the household; only the account holder
   reaches an ambulance.

Number six is the one worth keeping. The argument against the mistake was
already written down in this repository, in the escalation policy's own
`ceilings` field, which the server returns on every call and which says:

    anonymous_beacon_alarm: notify_contact (maximum) — a stranger who
    scanned a care beacon can raise the people watching, never an ambulance

The design was right, was documented, and was documented *in a place the
client already reads*. The binding contradicted it anyway, because it was
written from a plausible story about emergencies instead of from the
product. That is the same shape as every other defect this audit has
produced: a plausible story passing where a call would have failed.

## Two guards that could only pass while the problem existed

Closing the backlog broke two tests, and both were wrong in the same way.

`test_the_union_is_still_wider_than_the_console` asserted the union backlog
was **strictly** smaller than the console's — reasoning that if they ever
agreed, the likelier cause was a dead native extractor than a console that
had caught up. Sound while catching up was hypothetical. Both are zero now,
which is the outcome the audit was for.

`test_the_audit_is_actually_looking_at_something` asserted the snapshot file
was non-empty, to prove the audit had something to look at. It could
therefore only pass while the backlog did. The liveness question is real and
now lives where the meaning is: the console must still be producing call
sites.

A check that can only be satisfied by the problem still existing is not a
check. Both have been rewritten rather than deleted.
"""

from __future__ import annotations

import re
from pathlib import Path


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()
API = REPO / "app" / "src" / "api.ts"
SCREENS = REPO / "app" / "src" / "screens"
HERE = Path(__file__).resolve().parent


def _api() -> str:
    return API.read_text(encoding="utf-8")


def _screen(name: str) -> str:
    """A screen's source, plus the English behind every key it looks up.

    Reading the raw file was right until the console gained a language table.
    The moment a sentence moves from the JSX into `l10n.ts`, a check searching
    the file finds nothing and reports the door gone — while the door is there
    and now works in ten languages. QRME's audit hit this exact shape when its
    accountless screen was localized:

        asked     does this file contain this English sentence
        mattered  does this screen say this to the person reading it

    So the keys are resolved. What comes back is what the screen *shows*, in
    English, whatever file the words live in.
    """
    source = (SCREENS / name).read_text(encoding="utf-8")
    table = SCREENS.parent / "l10n.ts"
    if not table.exists():
        return source
    text = table.read_text(encoding="utf-8")
    english = {}
    for key, row in re.findall(r'^  "([\w.]+)":\s*\{(.*?)^  \},', text,
                               re.S | re.M):
        hit = re.search(r'\ben:\s*"((?:[^"\\]|\\.)*)"', row)
        if hit:
            english[key] = hit.group(1)
    looked_up = re.findall(r'\b(?:t|tr)\(\s*"([\w.]+)"', source)
    return "\n".join([source] + [english[k] for k in looked_up if k in english])


# --- the three records reach zero -------------------------------------------

def test_the_console_backlog_record_is_empty():
    """Not short — empty. Every route in the app is reachable from the
    desktop console on its own, without borrowing a phone."""
    rec = (HERE / "console_doorless.txt").read_text().strip()
    assert rec == "", f"still recorded as doorless from the console:\n{rec}"


def test_the_union_backlog_record_is_empty():
    rec = (HERE / "doorless_routes.txt").read_text().strip()
    assert rec == "", f"still recorded as doorless everywhere:\n{rec}"


def test_the_unused_binding_record_is_empty():
    """And every binding written in `api.ts` has a screen that calls it, so
    the two halves of the audit agree at zero rather than only one of them."""
    rec = (HERE / "unused_bindings.txt").read_text().strip()
    assert rec == "", f"still called by nothing:\n{rec}"


# --- the six the wire corrected ---------------------------------------------

def test_the_access_log_is_not_typed_as_a_list():
    """The one that would have shown an empty privacy log for the wrong
    reason. `AccessLog` carries the three fields around `entries`."""
    src = _api()
    assert "req<AccessLog>(`/access-log/" in src, (
        "the access log is bound as something other than AccessLog — if that "
        "is a list type again, the screen will map over an object and render "
        "nothing")
    decl = re.search(r"export type AccessLog = \{(.*?)\};", src, re.S)
    assert decl, "AccessLog is not declared"
    for field in ("vaulted", "access_record_kept", "entries", "note"):
        assert field in decl.group(1), f"AccessLog has lost `{field}`"


def test_the_screen_says_why_the_log_is_empty():
    """An empty list and no list at all are opposite facts. The screen is
    required to tell them apart, because a user reading it is asking who has
    seen their record."""
    flat = " ".join(_screen("Held.tsx").split())
    assert "not because nobody has looked" in flat


def test_provenance_carries_the_key_it_asks_about():
    assert "custodyProvenance: (uid: string, key: string" in _api()
    assert "provenance?key=" in _api()


def test_clinicians_are_asked_for_per_condition():
    assert "referralClinicians: (uid: string, condition: string" in _api()
    assert "?condition=" in _api()


def test_the_markup_routes_do_not_go_through_the_json_helper():
    """`req` falls back to `null` on a body it cannot parse — right for a
    crashed server, wrong for a route whose job is to return a page."""
    src = _api()
    assert "async function reqText(" in src
    for binding in ("placedCode:", "placedCodeQr:", "socialQr:"):
        line = next(l for l in src.splitlines() if l.strip().startswith(binding))
        nxt = src.splitlines()[src.splitlines().index(line) + 1]
        assert "reqText(" in line or "reqText(" in nxt, (
            f"{binding} is bound through the JSON helper again, so it will "
            "come back as null")


def test_the_social_beacon_carries_a_credential():
    """Unlike the placed code, which deliberately does not."""
    src = _api()
    assert "socialBeaconCard: (cid: string, token: string)" in src
    assert "socialQr: (cid: string, token: string)" in src
    # And the front-door code stays open, because that is the whole point
    # of a care code somebody else can scan.
    assert "placedCode: (bid: string) =>" in src
    assert "raiseFromCode: (bid: string, body: Body) =>" in src


def test_the_emergency_route_carries_a_credential():
    """The correction that matters. An uncredentialed `POST /emergency/{uid}`
    would let anybody reach `emergency_services` against anybody's account."""
    src = _api()
    assert re.search(r"raiseEmergency: \(uid: string, body: \{[^}]*\},\s*"
                     r"token: string\)", src, re.S), (
        "raiseEmergency does not take a token — the server requires one, and "
        "the reason is that the alternative is an abuse vector that ends in "
        "a dispatched ambulance")
    assert "req<Row>(`/emergency/${uid}`, { method: \"POST\", body, token })" in src


def test_the_screen_names_the_two_doors_apart():
    """A product with two emergency paths, one credentialed and one not,
    should say which is which where a person can read it."""
    flat = " ".join(_screen("Attending.tsx").split())
    assert "Only you can send an ambulance to yourself" in flat
    assert "bystander" in flat


# --- the screens actually call what they claim ------------------------------

def test_each_new_screen_calls_its_family():
    """The unused-binding guard checks this from the binding's side. This
    checks it from the screen's, so a screen gutted in a refactor fails here
    rather than silently emptying the other file."""
    expected = {
        "Aims.tsx": ("api.goals(", "api.addGoal(", "api.updateGoal(",
                     "api.habits(", "api.addHabit(", "api.logHabit(",
                     "api.budgets(", "api.setBudget(", "api.clearBudget(",
                     "api.logActivity("),
        "Wards.tsx": ("api.children(", "api.child(", "api.addChild(",
                      "api.removeChild(", "api.setChildControls(",
                      "api.guardianWatch("),
        # The three waiver bindings were on the Wards row until a field report
        # said the card did not belong there: *get this out of there, it
        # shouldn't belong in who you watch.* The waiver is signed by the
        # account holder about their own body, so it moved to Safety, under
        # the automatic path it modifies. Kept as its own row rather than
        # folded into a longer one, because this guard is the thing that would
        # catch the card being moved again and the bindings being left behind.
        "Safety.tsx": ("api.waivers(", "api.signWaiver(",
                       "api.withdrawWaiver("),
        "Held.tsx": ("api.accessLog(", "api.membership(", "api.setMembership(",
                     "api.cancelMembership(", "api.plans(", "api.sources(",
                     "api.setSources(", "api.custody(",
                     "api.custodyProvenance(", "api.eraseEverything(",
                     "api.cloudStatus(", "api.connectorsCatalog(",
                     "api.providerFor("),
        "Attending.tsx": ("api.specialists(", "api.seedSpecialists(",
                          "api.seedTandemSpecialists(",
                          "api.referralClinicians(", "api.referralRequests(",
                          "api.prepareReferral(", "api.markReferralReleased(",
                          "api.specialistTasks(", "api.specialistTask(",
                          "api.handToSpecialist(",
                          "api.advanceSpecialistTask(",
                          "api.escalationPolicy(", "api.relayChannel(",
                          "api.relayRoster(", "api.relayRota(",
                          "api.startSession(", "api.endSession(",
                          "api.alarmGuidance(", "api.raiseEmergency(",
                          "api.medicalId(", "api.makeMedicalIdQr(",
                          "api.revokeMedicalIdQr("),
        "Reach.tsx": ("api.roboticsCatalog(", "api.robots(", "api.bindRobot(",
                      "api.commandRobot(", "api.unbindRobot(",
                      "api.placedCode(", "api.placedCodeCard(",
                      "api.placedCodeQr(", "api.raiseFromCode(",
                      "api.pickUpCode(", "api.socialAccounts(",
                      "api.connectSocialAccount(", "api.socialBeaconCard(",
                      "api.socialQr(", "api.collectFromSocial(",
                      "api.publishToSocial(",
                      "api.disconnectSocialAccount(", "api.excursions(",
                      "api.startExcursion(", "api.excursionEntry(",
                      "api.learnFromExcursion(", "api.communityVisits(",
                      "api.watchDrip("),
        # `api.setSensitivity(` moved to Baseline.tsx in the limits
        # round-up — the dial scales the drift bands that screen shows.
        "Baseline.tsx": ("api.setSensitivity(",),
        "Bearing.tsx": ("api.languages(", "api.userLanguage(",
                        "api.setUserLanguage(", "api.translate(",
                        "api.setPersonality(",
                        "api.clearVoice(", "api.recordCondition(",
                        "api.giveContext(", "api.askCompanion(",
                        "api.updateMed(", "api.insights(", "api.report(",
                        "api.events(", "api.followup(", "api.calmHistory(",
                        "api.coachHistory(", "api.tutorial(",
                        "api.tutorialStep(", "api.tutorialForScreen(",
                        "api.tutorialProgress(", "api.startTutorial(",
                        "api.finishTutorialStep(", "api.helpTopics(",
                        "api.dock(", "api.dockFaces(", "api.dockFace(",
                        "api.dockWhere(", "api.setDock(",
                        "api.improvements(", "api.suggestImprovement(",
                        "api.sendFeedback("),
    }
    missing = []
    for name, bindings in expected.items():
        src = _screen(name)
        missing += [f"{name}: {b}" for b in bindings if b not in src]
    assert not missing, "screens no longer call:\n    " + "\n    ".join(missing)


def test_the_four_orphans_found_screens():
    """`api.enroll`, `api.getVigil`, `api.handOverMic` and `api.captureImage`
    were the whole of the unused-binding record and predate this round. Each
    had a real capability behind it that the console simply did not offer.

    `api.getVigil` found Settings first, and moved home in the limits
    round-up: the vigil's quiet-days threshold is a line the Guardian
    draws around a person, and those live on the baseline screen now.
    """
    assert "api.enroll(" in _screen("Onboarding.tsx")
    assert "api.getVigil(" in _screen("Baseline.tsx")
    assert "api.handOverMic(" in _screen("Channel.tsx")
    assert "api.captureImage(" in _screen("Channel.tsx")


def test_starting_without_an_email_is_offered_and_its_cost_is_stated():
    """`POST /enroll` has always let somebody in with a name, a birthdate and
    a consent. Every screen in front of it demanded an email and a password,
    so the only way to reach it was a phone or a curl command — which quietly
    decided that a person without an email address does not get a guardian.

    The trade is real and has to be said rather than buried: no address means
    no recovery.
    """
    flat = " ".join(_screen("Onboarding.tsx").split())
    assert "Start without an email address" in flat
    assert "no way to recover an account made this way" in flat


def test_the_closed_sets_are_unions_rather_than_strings():
    """The server names the members of both in its 422 body. A wrong literal
    is a build error; a wrong string is a user's error message."""
    src = _api()
    for member in ("mental_health", "health_fitness", "personal_growth"):
        assert f'"{member}"' in src, f"GoalArea has lost {member}"
    for member in ("financial_stress", "physical_distress", "physical_injury"):
        assert f'"{member}"' in src, f"ConditionName has lost {member}"
