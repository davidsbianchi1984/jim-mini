# JIM-mini v0.1.9 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.1.9` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**JIM-mini v0.1.9** — the release where the workplace relay learns who is
actually on shift, and where "notified" stops meaning "written down". One of
three interoperating products (with
[qrme](https://github.com/davidsbianchi1984/qrme) and
[pdi](https://github.com/davidsbianchi1984/pdi)), all three cut together at this
version.

### Highlights

- **A rota, because a flat list pages the day person at 2am.**
  `JIM_SITE_ROSTER` was a list of names worked top to bottom, every time, and
  `relay.py`'s own comment defended that as a deliberate limit — *a rota with
  shift patterns is a scheduling product*. Honest, but wrong about the size of
  the gap. The relay exists for **night shift**: lone workers, plant rooms,
  single-staffed sites. Getting *who is on right now* wrong at 3am is not a
  degraded feature, it is the feature failing in the hour it was built for.

- **`JIM_SITE_ROTA` is deliberately small.** Named people, the days they work,
  the hours, and `JIM_SITE_TZ`. No leave, no swaps, no fairness, no recurrence
  grammar. Three things it does get right, because each is a way of paging the
  wrong person:

  - **Shifts cross midnight.** `18:00–06:00` is the shift this is all about,
    and `start <= now <= end` is false for every minute of it. A wrapping shift
    is two intervals and belongs to the day it *started*: at 02:00 on Saturday
    it is Friday's night worker on the floor, not the weekend rota.
  - **A site is somewhere.** Without a timezone a rota written in local time is
    evaluated in UTC, shifting every boundary by the offset — and by a
    *different* offset in summer, so it would look correct for half the year.
    An unrecognised zone is named in `GET /relay/roster`'s `warning` rather than
    silently treated as UTC.
  - **A rota has gaps.** Nobody rostered at 4am on a bank holiday is a real
    state. The relay works the whole rota — better to wake the wrong person than
    nobody — and reports `on_shift: false` on the escalation *and in the page
    itself*, so whoever it wakes knows they were a guess.

  `GET /relay/rota` answers *who would you page right now?* in the afternoon,
  rather than leaving it to be discovered at 3am. `JIM_SITE_ROSTER` still works
  and still means plain names, always on — a test asserts the old configuration
  is unchanged.

- **And `escalate` now sends something.** "Notified" meant a row in `events`
  saying somebody had been notified, while nothing had left the building — so
  the loop the relay is built around, *keep going until a human accepts*, could
  never close on its first step. JIM posts a signed envelope to
  `JIM_NOTIFY_URL` and stops; the SMS gateway or pager behind it is the
  deployment's, and the envelope matches PDI's shape so one receiver can take
  both. An unreachable responder sets `reached_somebody: false` **and**
  `escalate_again_now`, because *waiting on a human* and *waiting on a human who
  was never told* need different next moves, and only the first should wait.

- **Incident scope survives the trip out of the building.** A webhook is the
  easiest place in the system to turn an incident into a health record — *"just
  add the name so they know who to look for"* is a reasonable-sounding sentence
  that would undo the whole promise. So the envelope is built by copying named
  fields *out* of `relay.incident`, never by stripping fields from a user
  record, and not even the finder's words go out. A test reads the whole
  envelope as one string and looks for the name, birthdate, contact number,
  resting rate and the finder's message in it.

- **The ceiling did not move.** A notification channel is not a siren. A test
  runs the rota to exhaustion to prove `notify_contact` still caps it, and that
  the relay still refuses to call emergency services on anyone's behalf.

- **The tandem doc was describing a past release.** This copy listed the suite
  gateway's erase, export, consent and metering as `[planned]` when
  `suite/gateway.py` had shipped them — a reader here was told cross-app
  deletion did not exist. [docs/tandem.md](docs/tandem.md) is now identical
  byte-for-byte in all three repos, with new sections for the arrow that runs
  out of PDI into QRME, the beacon family across all three products, and the
  notification channel — the one thing the suite genuinely cannot supply for
  itself. `docs/diagrams/tandem-flow.svg` is generated rather than hand-drawn.

### Verification

293 tests green (20 new this release). 87 routes. Version strings moved in
exactly five places: `pyproject.toml`, the FastAPI app, `app/package.json`, and
the two root entries in its lockfile (dependency versions untouched).

### Install

Download the installer for your OS below (`.dmg` / `.exe` / `.AppImage`), or run
`python -m jim` from source and pick your device — see the [README](README.md). Installers are signed
only if signing secrets are configured; otherwise they are unsigned (see
[docs/releasing.md](docs/releasing.md)).

**Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
