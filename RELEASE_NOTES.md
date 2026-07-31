# JIM-mini v0.22.0 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.22.0` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**JIM-mini v0.22.0 — the console backlog reaches zero.**

The desktop console could not reach **109** of JIM's routes. Every one was
present on the phone shells, which is why the guard reported a healthy number
for as long as it did: it was answering *some client can reach this*, and a
phone could.

| | at the start of this release | now |
|---|---|---|
| Console-doorless routes | 109 | **0** |
| Routes no client anywhere calls | 69 | **0** |
| `api.ts` bindings nothing calls | 4 | **0** |

All three record files are now **empty rather than short**, and the tests that
read them assert emptiness.

## Six new screens

Screens 95–100, one per family the routes fell into:

- **What you're working on** — goals, habits, a monthly budget. None of it is a
  list for its own sake: a goal is read by the Coach and the daily suggestion,
  and a budget is how the Guardian learns the shape of financial stress.
- **Who you watch** — a child's account and its limits. Pausing holds everyday
  guidance only; monitoring, crisis escalation and the emergency path never
  pause, and the server says so in its own words every time you use a control.
- **What's held about you** — custody, the access log, consented sources, the
  plan's storage posture, and the erase-everything door.
- **Who else is looking** — specialists, referrals, the household relay, and
  the escalation ladder with its floors and its one ceiling.
- **What reaches out** — a bound robot and its first-aid rating, a placed care
  code, accounts on platforms JIM does not run, and excursions.
- **Bearing** — what you set, what you told it, and what it made of that.

Each with a walkthrough lesson and a help direction.

## Starting without an email address

`POST /enroll` has always taken a name, a birthdate and a consent. Every screen
in front of it demanded an email address and a password, so the only way to
reach it was a phone.

An email address is a thing a person may not have, may not control, or may
share with somebody they are trying not to be watched by. A guardian product
that makes one mandatory to begin has quietly decided who gets a guardian.
This deployment's backend never decided that; the console did, by omission.

The trade is stated rather than buried: no address means no recovery, and the
device holds the only key.

## What driving the routes found

Nothing in the backend was broken this round. What a running server disagreed
with the route table about:

- **`raiseEmergency` sent no credential**, on the reasonable-sounding premise
  that an emergency is when a person is least able to produce one. The
  server's reason is better: an uncredentialed `POST /emergency/{id}` lets
  anybody reach `emergency_services` against anybody's account. The
  uncredentialed door for a bystander already existed and is a different one —
  a scanned care code, capped at `notify_contact`. The escalation policy states
  that ceiling in a field the client already reads.
- **`GET /access-log` answers an object, not a list.** Its other three fields
  say whether anything is being recorded at all. On a vault-less deployment an
  empty `entries` means *no log exists*, not *nobody looked* — and a privacy
  screen showing a person the wrong one of those two, silently, is the worst
  available way for that page to fail.
- **Two routes were bound without required query parameters**, so both were a
  422 every time.
- **The care-code scan page is HTML and two `qr.svg` routes are SVG**; through
  the JSON helper all three came back `null`.
- **The social beacon and its code need the owner's token**, unlike the
  placed-code pair they resemble.

## Three more things the console never offered

Looking at a clinical capture (the image is on its own route, and a person's
own body photographs were listed with no way to see them), handing channel 2
over with its reason and whether anybody else was in the room, and reading the
vigil **without** sweeping it — a sweep can trip the vigil and send somebody to
a person's door, which makes it a write, and a write should not be the only way
to look at a thing.

## Two guards that could only pass while the problem existed

One asserted the union backlog was *strictly* smaller than the console's; the
other asserted the audit's snapshot file was non-empty. Both have been
rewritten to check what they were for rather than what they happened to
measure.

**Suite: 802 passing, 1 skipped.**

---

Cut in step with [QRME](https://github.com/davidsbianchi1984/qrme) and
[PDI](https://github.com/davidsbianchi1984/pdi), both also at v0.22.0. All
three reached zero on the same audit in this release.
