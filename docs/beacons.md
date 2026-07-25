# Care beacons — leaving a Guardian somewhere

*Design. Nothing in this document is built yet — it is the decision record that
the implementation round will follow.*

QRME has **desk beacons**: a printed QR stuck to a shop door, resolving to a
live person who is simply not behind it this minute, with a bell a stranger can
ring to fetch them
([qrme/docs/desks.md](https://github.com/davidsbianchi1984/qrme/blob/main/docs/desks.md#leaving-the-desk-behind--beacons)).
The gesture ports to the Guardian. The thing it points at does not.

A desk is a *place a person works*. JIM-mini has no desks, and inventing one
would be cargo-culting the feature rather than porting it. What JIM-mini has is
**a person somebody is watching over**, and the physical anchors that person
already leaves lying around: a wristband, a fridge door, a car window, a bike
helmet, the frame of a walker, a bedside card.

So the port is a **care beacon** — a printed code on the objects around a
watched person, which a stranger can scan to raise the people who are watching.

    POST   /users/{id}/beacons     place one
    GET    /c/{beacon_id}          where the printed QR points
    POST   /c/{beacon_id}/alarm    the bell
    DELETE /beacons/{beacon_id}    peel it off

## It is not a second Medical ID

`GET /medical-id/{token}` already exists and is already a printed code a
stranger scans. Any beacon design that ignores that is a duplicate, so the line
between them is the first thing to draw:

| | Medical ID | care beacon |
|---|---|---|
| answers | *who is this and what is wrong with them* | *is anyone watching, and how do I raise them* |
| is a | disclosure | summons |
| travels | with the person — lock screen, wallet | with the **place or object**, and stays there |
| read by | a responder already on scene | anyone who walks past |
| the act | reading | **ringing** |

The Medical ID is read-only and deliberately ungated: a paramedic kneeling over
someone unconscious should hit zero friction. A beacon is the opposite end —
found by a neighbour, a delivery driver, a stranger at a bus stop, who has no
idea whether anything is wrong at all.

They stay separate objects for four practical reasons as well as the conceptual
one: a beacon carries a **label** (several codes, several doors — same reason
QRME requires one), it can be **peeled off individually** without killing the
card on the person's wrist, it counts **scans** where a Medical ID deliberately
does not advertise one, and a fridge magnet keeps working while its owner is
out with their phone.

## The bell comes first, and the card is what it buys

QRME's desk beacon shows the card freely and offers the bell underneath. A
tradesperson's name and trade is a shop sign; publishing it is the point.

Health is not a shop sign, so the order inverts. **Two stages:**

**Stage one — before any action, no auth, nothing clinical.**

- the person's **first name only**, so the finder can speak to them
- *"Someone is watching over this person through a Guardian."*
- *"If this is an emergency, call your local emergency number first."*
- the alarm button

That is the whole page. A passer-by who scans a fridge magnet learns that the
household uses JIM-mini and nothing else — no age, no conditions, no contact
name, no address.

**Stage two — after the alarm is raised**, the page shows the Medical ID:
condition-level facts, the emergency contact, what to do while help comes.

Raising the alarm is the act that turns a passer-by into a responder. It
notifies the contacts, it is logged, it is attributable to a moment in time —
and *that* is what justifies handing over clinical facts. Before it, the
scanner is a stranger with a phone.

The friction objection answers itself: a real responder wants to alert the
family anyway, so the extra tap is a tap they were going to make; and the
zero-friction path already exists on the person's own body, which is exactly
what the Medical ID QR is for. The beacon can afford a gate **because** the
ungated card ships alongside it.

## The bell rings the ladder, not the owner

QRME's bell rings the desk's owner. Here the owner may be the reason you are
scanning, so an alarm goes into the **existing escalation ladder**
([escalation.py](../jim/escalation.py)) rather than a parallel notifier:

    0  log
    1  self_guidance
    2  check_in
    3  notify_contact       ← a beacon alarm lands here
    4  emergency_services

A beacon alarm enters at `notify_contact` — the emergency contact, plus the
parent for a minor's beacon — and **`notify_contact` is also its ceiling.**

That ceiling is new. Every existing rule in that module is a *floor*: crisis
language never lands below `emergency_services`, a `critical` detection never
below `notify_contact`, whatever the sensitivity dial says. This is the first
rule pointing the other way, and it needs to exist because a stranger's tap
must never dial emergency services on someone else's behalf. A false dispatch
is a real ambulance not going somewhere else, sent by someone with no account
and no accountability. The page tells them to call directly instead — which is
both safer and faster than anything the button could do.

An alarm is an **event**, so it appears in the owner's own event stream and in
a parent's oversight view under the existing `alerts_only` / `full` rules.

## Rate limiting, and why dropping is the wrong failure

QRME caps an anonymous ring per desk at 30 seconds, because a printed code is
reachable by anyone walking past and that is the entire threat model. Same
model here, different stakes: a spammed alarm does not merely annoy, it
**trains a family to ignore the one that matters**.

So the cooldown coalesces rather than drops. Within the window, a second
alarm attaches its message to the **open** alarm instead of raising a new one
or being silently discarded. Two people finding the same person should not
race, and the second one must never be thrown away — that is the case the
feature exists for.

The owner sees who rang and clears each one as they answer it, their token
only, exactly as `GET /desks/{id}/rings` works in QRME.

## What a beacon refuses to say

This is where the port stops being a port. QRME's desk beacon exists **to**
publish presence — is the tradesperson at the desk. A care beacon must publish
the opposite, and each refusal below is load-bearing:

- **Never the person's health status.** Not "elevated heart rate four minutes
  ago", not "checked in this morning", not a colour-coded dot. *Is this person
  OK right now* is precisely the question a stalker is asking. The beacon
  reports **watch status** — a Guardian is watching, or this code is no longer
  active — and never subject status.
- **Never location.** QRME withholds location on rated desks; JIM withholds it
  always. A beacon is *at* a location by definition, so confirming the person
  is there, to anyone who scans, is the whole risk in one field.
- **Never raw biometrics or journal notes**, at either stage. The Medical ID is
  already condition-level only and stage two shows that and no more.
- **Never the scanner's location or device.** A scan is a glance, not evidence.
  The plumber scans the fridge; that means nothing about anyone's health, so it
  feeds the owner's scan count and nothing else. Escalation is driven by the
  **alarm**, which is an act.

## Children

QRME's rated desks meet a stranger with an age wall. The analogue here is a
code on a child's backpack, which is its own threat model and gets stricter
rules, not a wall:

- **A child cannot place their own.** Parent-issued only, through the existing
  `family` link, and it dies when oversight does at 18.
- **The alarm goes to the parent**, ahead of any contact on the child's record.
- **Stage two never opens.** A minor's beacon shows first name and the alarm,
  and no clinical facts at any stage, to anyone. A responder needing a child's
  medical history has the child's Medical ID and a parent on the phone within
  seconds of the alarm; a stranger holding a backpack does not get a medical
  history because they tapped a button.

## The badge

QRME's desk beacon carries **"Live person — not AI"** — green, top-right,
worded as a positive claim, because absence of the AI mark would not be a
disclosure on its own.

Same reasoning, different claim. A care beacon's stage one carries:

> **Scanning this did not call for help.**

A stranger cannot infer from a page's silence that nobody was alerted, and the
worst possible failure of this feature is somebody walking away from a person
on the ground believing the QR handled it. Stated positively, before the tap.

After the tap, it changes to a second claim, not a reassurance:

> **The alarm is raised. This is not an emergency service.**

## Shape of the build

New tables, never new columns — `_SCHEMA` is applied with
`CREATE TABLE IF NOT EXISTS` and there is no migration machinery, so a column
added to an existing table only ever reaches a fresh database:

    care_beacons     id, user_id, label, location, scans, active, created_at
    beacon_alarms    id, beacon_id, user_id, message, state, created_at, cleared_at

Two details carried over from QRME's implementation because both were learned
the hard way:

- The scan page is **one self-contained document** — a camera app's in-app
  browser, on cellular, from cold, is not the place to discover a missing
  stylesheet.
- The alarm posts to a **relative** URL. An absolute one baked from
  `JIM_PUBLIC_URL` breaks every LAN scan, which is most of them during testing.

The QR renders through `segno` like the Medical ID's, and in the same medical
red (`#b3261e`) — a printed code on a person's things should look like the
other printed code on a person's things.

## What this does not give you

- **No presence.** There is no "they're fine" signal to read, by design, and no
  amount of asking will add one.
- **No emergency dispatch.** The ceiling is `notify_contact`; the page says so.
- **No identity for the scanner.** Anyone can raise an alarm on any active
  beacon, which is the point, and the reason for the coalescing cooldown rather
  than a stronger gate.
- **No proof the beacon is on the person it names.** A sticker outlives what is
  behind it — a code peeled off a walker and stuck somewhere else still
  resolves until its owner deactivates it.
