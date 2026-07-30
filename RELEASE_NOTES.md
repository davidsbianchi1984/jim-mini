# JIM-mini v0.19.0 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.19.0` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**JIM-mini v0.19.0** — the app can tell you what broke, without telling you
anything about your health.

Every failed request in the console is now recorded and, where a build has
somewhere to send, reported. What gets kept is the *operation* and the
status code, never the message and never the path as it was actually
called. In a health product that distinction is the whole feature:
`GET /users/{id}/captures/{id}/image → 404` identifies a bug, where the
unredacted version of that path names a photograph of somebody's body and
whose it is. Only the first is written down, and the redaction happens
before the row is stored.

JIM's backend puts user input straight into its error messages — *no
device called 'Pixel Buds' on this account*, *unknown site 'knee'; one of
scalp, face, eye, mouth…*. A place on your body. A device in your home.
Good messages for the person reading them, and exactly the wrong thing to
keep. So the message is shown to you, who own it, and is **never written
to the log**.

**Nothing goes before you have been asked.** Sending is opt-out, which
only means something if the opting-out can happen before the first report
rather than being discovered afterwards in a panel nobody opened. A
first-run notice holds everything until it is answered — and it shows the
actual payload rather than describing it, from the same function that
sends it, so it cannot go stale while still reading honestly. The switch
on the Privacy card is that same answer, changeable whenever.

Counts are sent as **deltas**: each row remembers how much of itself has
been reported, so reopening the app twenty times does not turn one broken
screen into twenty. A failed send moves nothing, and the next launch
retries.

**The receiving gateway refuses rather than redacts.** It accepts exactly
five top-level keys and five per problem and rejects anything else — an
unknown field, a `platform` string long enough to hide a sentence, a `day`
carrying a time of day, a path with an unredacted id still in it. It could
redact that path itself; doing so would let a build whose redaction had
broken keep working while nobody learned that every report from those
users had been arriving with a user id in it.

What survives is less than what arrives. Reports are not stored as
reports — they fold into counters keyed by product, version, platform,
operation and status. Locale is validated and then dropped, and nothing
records that a particular install sent anything, or when beyond the day.

**Off by default, by absence rather than by flag.** The collector address
is compiled in at build time and unset, so an installer built without one
has nowhere to send and no code path that could acquire one. There is no
address for a later mistake to switch on.

**Fixed** — four bugs found by running the thing rather than reasoning
about it. The gateway had no CORS at all, so every browser preflight would
have been refused and every report would have failed silently. Its
validators were anchored with `$`, which in Python also matches before a
trailing newline, so `Win32\n` passed a check whose error message promised
newlines were not allowed. A counter file that was valid JSON of the wrong
shape was adopted wholesale and took the read endpoint down with it. And
the test guarding the payload shape ran only in the repository that ships
the gateway — not here, where a leak would cost the most.
