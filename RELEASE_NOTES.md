# JIM-mini v0.24.0 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.24.0` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

Three rounds, one question: **when a passer-by does reach the page built for
them, can they read what it says?**

The beacon page has negotiated `Accept-Language` since the round that
localized it. Everything around the edges of it had not.

## Five strings the named checks could not have found

The existing test named four Spanish strings and checked they appeared on the
beacon page. They did. Meanwhile five strings a passer-by reads had never
gone through `tr` at all, so no language reached them and no amount of adding
translations would have:

- **Both `<title>`s** — what the tab shows, what a shared link previews as,
  and what a screen reader announces first. English, under a translated
  document.
- **The greeting.** `You've found {name}.` was translated only in its
  *anonymous* branch. With a first name on the beacon the code built an
  f-string, so the largest sentence on the page was English for every finder
  holding a beacon that names somebody.
- **Both foot paragraphs** — the sentence telling a finder what pressing the
  button will and will not do. Neither branch wrapped, and testing one branch
  is how the other could have stayed English indefinitely.

Four checks now derive the list from the page rather than from what somebody
thought to name.

## The page was translated; the answer to the button was not

`POST /c/{id}/alarm` never read the header, and the page renders two of its
fields onto itself after the fetch:

> The alarm is raised. This is not an emergency service.

> The people watching over this person have been alerted. If this is an
> emergency, call your local emergency number — this page cannot.

Those are the two sentences on the whole surface that most need to be
understood, and they arrive while somebody is kneeling over a person deciding
what to do next. A Spanish finder read a Spanish page, pressed a Spanish
button, and was answered in English — including the sentence saying this page
cannot call anyone and they have to.

`note` and `badge` by name rather than a walk over the response. The Medical
ID rides in the same object, and a person's conditions, their emergency
contact's name and their resting heart rate are facts rather than copy.
Translating a clinical value is how a responder gets misled, which is worse
than an English one they can still read — there is a test holding that line.

The minor's variant is a third sentence and is covered. The 404 the *button*
answers for a peeled-off code is translated too: the page for that code
already was, and somebody who presses the button is the person who most wants
a sentence they can read.

## One header, three products

QRME, JIM-mini and PDI each grew a `negotiate()` in a different round.
Compared side by side for the first time, JIM disagreed with both on two rows.

`q=0` means **not acceptable** — RFC 9110 is explicit — so a browser sending
`ar;q=0` is refusing Arabic. This appended every recognised tag to its
ranking regardless of quality, so a header that refused the only language it
named got that language back, on the page somebody reads while deciding what
to do for a person on the floor.

Fixed here; QRME and PDI were already right. A conformance table now lives
byte-identically in all three repositories.

## Also

- A tripwire on the promise-and-door guard. Everything it does assumes a
  screen's words are in the screen's file, and QRME's copy of that check broke
  on exactly that assumption when a lookup table arrived. This console has no
  table yet and its server grew `jim/i18n.py` in the same round, so the check
  now fails the day one lands and says what to do.

**864 tests passing.**
