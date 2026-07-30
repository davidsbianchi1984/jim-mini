# JIM-mini v0.19.1 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.19.1` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**JIM-mini v0.19.1** — a feature can no longer ship with nothing drawn.

The gallery tests all check screens against the README: a reference with no
file, a file with no reference, a gap in the numbering. Every one of them
starts from the screens. **None asked the opposite question — does this surface
have a screen at all?** So a feature could ship undrawn, untaught and
unreachable from the in-app helper, and the suite stayed green.

That had happened three times, most recently to 0.19.0's own error-reporting
card and its first-run notice, which went out undrawn while the release notes
described them at length. It is the same shape of flaw found twice before here:
a guard that only walks the relation in the direction where the answers already
exist.

`ui_screens.txt` is the missing direction. Every console surface carries a
screen number, `undrawn`, or `unaudited`, so a surface nobody has classified
fails in the round that introduces it. The mapping is declared rather than
guessed — matching component names to screen titles resolved only a fraction of
them, because titles are written for the person using the app and component
names for the person editing it.

Both backlogs are ratcheted against a ceiling each repository declares for
itself, and a ceiling left high after the backlog falls fails too: a ratchet
that stops ratcheting re-opens the ground it gained. Five failures were injected
to prove it bites, including the one that matters — silencing the check by
writing `undrawn` fails the ratchet.

**And the two surfaces it caught are drawn.** Screens **93 What Went Wrong** and **94 Before Anything Is Sent** join the gallery, each
with a lesson and with phrasings that reach it in the words somebody actually
types when something has broken: "it failed", "something broke", "stop
sending", "opt out". The card draws an operation and a status and nothing else,
because that is all the log holds.

**No application behaviour changes in this release** — screens, gallery,
lessons, helper phrasings, and the guard that will keep them honest.
