# Care beacons — leaving a Guardian somewhere

*Shipped: `jim/beacons.py`, `jim/relay.py`, and the `ceiling` added to
`jim/escalation.py`. Covered by `jim/tests/test_beacons.py`. What is **not**
built is called out at the end.*

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

    POST   /users/{id}/beacons              place one
    GET    /users/{id}/beacons              the owner's codes and scan counts
    DELETE /beacons/{id}                    peel it off
    GET    /users/{id}/alarms               who rang, their token only
    POST   /users/{id}/alarms/{id}/clear    answer one

    GET    /c/{id}                          the page a phone opens
    GET    /c/{id}/card                     the same card as JSON
    GET    /c/{id}/qr.svg                   the printable code
    POST   /c/{id}/alarm                    the bell

    GET    /relay/roster                    who a site escalates through
    GET    /users/{id}/incidents            open site alarms, incident scope
    POST   /users/{id}/alarms/{id}/escalate next name on the roster
    POST   /users/{id}/alarms/{id}/accept   a named human takes it
    POST   /alarms/{id}/guidance            what to tell whoever is waiting

The three `/c/…` routes take no token: a stranger holding a phone at a sticker
is exactly the caller they exist for.

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

`notify_contact` is also a **send**, not just a tier. A personal beacon's
alarm pages a real channel when one exists — a minor's goes to the guardian
inbox that verified their consent, an adult's to the trusted channel they
armed their crash watch with — and the attempt lands in the same
`relay_pages` ledger the workplace relay and the crash watch write, under the
alarm's own id, so "What went out" shows a page that could not be sent as a
`queued` row rather than a silence. The finder's sentence is derived from
that outcome, never asserted: *a message has been sent* only when one was,
and otherwise *no message went out from this page* — because a stranger who
walks away from a person on the ground believing a QR code summoned help is
the worst failure this feature can have. Which of the three ways a message
can fail to go out — an unmailable contact, a delivery failure, or nobody
configured at all — is the owner's information, readable in their ledger; a
beacon never tells a stranger how watched a person is. A **site** beacon's
alarm sends nothing here: a worker's personal emergency contact is the wrong
recipient for a workplace incident, and the roster relay below is that
deployment's answer.

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

## At work: the agent that answers when nobody does

The Guardian is a personal product, and for a desk-bound office worker a care
beacon adds little over walking to reception. The case where it earns its keep
is narrow and specific, and it is a real category with a real name: **lone and
remote workers.** Night shift, field engineers, plant rooms, single-staffed
sites, anyone whose failure mode is *nobody was there*.

That case exposes a gap in the design above. `notify_contact` assumes **a
contact who answers.** In a personal deployment that is a family member, and
usually true. In a workplace at 2am on a remote site it may be nobody at all —
and a worker's personal emergency contact is the wrong recipient for a
workplace incident regardless.

So a corporate deployment adds a **relay of last resort**: an agent that takes
the alarm when the roster does not. Three things it does, none of them
clinical:

- **Works the roster in order** rather than firing one notification into the
  void — on-call, then supervisor, then the site's escalation list.
- **Confirms a human actually accepted**, and keeps escalating until one does.
  This is the loop a fire-and-forget notification leaves open, and it is the
  whole reason to have an agent rather than a second phone number.
- **Answers the finder while they wait.** Someone standing over a colleague
  needs to be told what to do in the next ninety seconds. JIM already delegates
  guidance to QRME specialist profiles for exactly this, and AI first aid
  already ships; the agent is a new caller to it, not a new model.

### Incident scope, never person scope

The constraint that makes this acceptable rather than a surveillance product.

A corporate deployment must not become a way for an employer to hold health
data about employees. JIM's data promise is per-user and does not bend because
the licence was bought by a company. So the workplace agent sees **an alarm was
raised at this beacon and this is what is needed** — not the worker's
conditions, baseline, history, or check-ins.

This is the same decision as PDI's *blind by default* and for the same reason:
the party who paid for the deployment is not thereby entitled to what is inside
it.

The **ceiling does not move either.** A workplace agent still cannot reach
`emergency_services`; it escalates *people*, not sirens. An employer's agent
dispatching an ambulance for an employee is precisely the version of this that
should not exist.

### Where it closes a loop with the other two products

A workplace incident is a recordkeeping obligation, and PDI already carries
**OSHA** in its compliance programs with retention attached. So the alarm seals
an incident record into the tenant's vault under OSHA retention, on the
hash-chained log, without anybody filling in a form at the time.

That is the concrete answer to *is there a use case here* — lone-worker safety
is an established category, and the suite already owns the two pieces around
it. It is a narrower case than PDI's facility agent, and worth building second.

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

Two new tables, never a new column — `_SCHEMA` is applied with
`CREATE TABLE IF NOT EXISTS` and there is no migration machinery, so a column
added to an existing table only ever reaches a fresh database:

    care_beacons   id, user_id, label, placement, kind, scans, active,
                   created_at
    beacon_alarms  id, beacon_id, user_id, messages, state, tier, accepted_by,
                   created_at, cleared_at

`messages` is a list rather than a string because the cooldown coalesces:
every finder's words are kept in order on the one open alarm. `kind` is
`personal` or `site`, and it is the only thing separating a fridge door from a
plant room — the relay reads it rather than a second table.

`label` and `placement` are the owner's own filing notes and are **never** in
the card a stranger sees; the tests assert that by searching the whole
serialized card for them.

The QR renders through `segno` like the Medical ID's, and in the same medical
red (`#b3261e`) — a printed code on a person's things should look like the
other printed code on a person's things.

## What a phone actually opens

`GET /c/{id}` serves **HTML**, because a QR is pointed at by a person holding a
phone — it used to answer JSON and show a neighbour a wall of braces. The JSON
moved to `/c/{id}/card`.

**Stage one is the whole page.** A first name, one sentence, and a button. The
instruction to dial sits *above* the button in the document, because the one
mistake that matters here is somebody waiting for a page instead of calling —
and it is the loudest thing on the screen.

**The Medical ID is not on the page at all before the alarm.** It arrives in
the alarm's own response and is rendered in place, so there is nothing in the
served HTML to reveal early even by mistake. A test asserts the values —
name, resting rate, conditions, contact number — are absent from stage one.

For a minor the server returns `medical_id: None`, and the page renders only
what it is handed, so stage two simply never appears. No second check to
forget.

One self-contained document, inline everything, no fetch it has to wait on:
somebody may be reading this kneeling next to a person on the floor. The alarm
posts to a **relative** URL. The rise animates `transform` only and honours
`prefers-reduced-motion`, so a browser that drops the animation still shows the
page rather than a blank card.

## What this does not give you

- **No presence.** There is no "they're fine" signal to read, by design, and no
  amount of asking will add one.
- **No emergency dispatch.** The ceiling is `notify_contact`; the page says so.
  That holds for the workplace agent too — it escalates people, not sirens.
- **No clinician.** The workplace relay reaches humans and repeats guidance
  that already exists. It does not triage, assess, or decide how bad something
  is, and a site that staffs it instead of a first-aider has misread it.
- **No identity for the scanner.** Anyone can raise an alarm on any active
  beacon, which is the point, and the reason for the coalescing cooldown rather
  than a stronger gate.
- **No proof the beacon is on the person it names.** A sticker outlives what is
  behind it — a code peeled off a walker and stuck somewhere else still
  resolves until its owner deactivates it.
- **No transport of its own.** JIM posts a signed envelope to
  `JIM_NOTIFY_URL` and stops (`jim/notify.py`). Whatever is behind that URL —
  SMS gateway, pager, chat webhook, a script that rings a desk phone — is the
  deployment's, and JIM ships no vendor and holds no account. With no URL set,
  a page is `queued` and the escalation *says nobody was reached*, which is the
  same behaviour as before except no longer silent.
- **No scheduling product.** `jim/rota.py` knows named people, the days they
  work, the hours, and the site's timezone. It does not know leave, swaps,
  fairness, or recurrence. What it does get right is the part that was actually
  hurting: shifts crossing midnight, attributed to the day they started.

## Who is on, and reaching them

`JIM_SITE_ROSTER` was a list of names worked top to bottom, every time, and
this document used to defend that as a deliberate limit. It was the wrong
limit. The relay exists for **night shift**, and a flat list pages the day
person at 2am — the feature failing in the hour it was built for.

    JIM_SITE_TZ=Europe/Lisbon
    JIM_SITE_ROTA='[{"name":"Dana Okafor","role":"on-call",
                     "days":"mon-fri","from":"18:00","to":"06:00"},
                    {"name":"Ash Bell","role":"supervisor",
                     "days":"sat,sun","from":"08:00","to":"20:00"}]'

Three things it is careful about, because each is a way of paging the wrong
person:

**Shifts cross midnight.** `18:00–06:00` is the shift this is all about, and
`start <= now <= end` is false for every minute of it. A wrapping shift is two
intervals and belongs to the day it *started* — at 02:00 on Saturday it is
Friday's night worker who is on the floor, not the weekend rota.

**A site is somewhere.** Without `JIM_SITE_TZ` a rota written in local time is
evaluated in UTC, shifting every boundary by the offset — and by a *different*
offset in summer, so it would look correct for half the year. An unrecognised
zone is named in `GET /relay/roster`'s `warning` rather than silently treated
as UTC.

**A rota has gaps.** Nobody is rostered at 4am on a bank holiday. The relay
then works the whole rota — better to wake the wrong person than nobody — and
reports `on_shift: false` on the escalation *and in the page itself*, so
whoever it wakes knows they were a guess.

`GET /relay/rota` answers "who would you page right now?" in the afternoon,
rather than leaving it to be discovered at 3am. `JIM_SITE_ROSTER` still works
and still means plain names, always on.

**A typo cannot take the escalation path down.** An unreadable `JIM_SITE_ROTA`
— bad JSON, a missing name, `"funday"` for `"sunday"` — is *not* raised at the
moment somebody needs help. The rota is ignored, the relay falls back to
`JIM_SITE_ROSTER`'s flat names (and to `DEFAULT_ROSTER` if that is unset), and
somebody is still woken. This matters because there is no start-up validation
step to catch it earlier: the first read happens when an alarm is already open.

Degrading is not hiding. The error is reported as `warning` on
`GET /relay/roster`, as `rota_error` on every escalation result, and
`GET /relay/rota` still refuses outright with a 422 — a surface an operator
uses to *check* their rota should be strict, because degrading there would hide
the exact thing they came to find.

An escalation now reports `reached_somebody`, and when it is false it also sets
`escalate_again_now` — because *waiting on a human* and *waiting on a human who
was never told* need different next moves, and only the first should wait.
