# JIM-mini v0.6.1 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.6.1` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**JIM-mini v0.6.1** — the round where the coach stopped performing distress
it never detected. One of three interoperating products, all three cut
together at this version.

### The bug, as reported

A career question — *"I want this app I built to be successful"* — was
answered with *"I'm here with you [stub guidance for distress]… let's take
one slow breath together."* Every time. Word for word.

### What was actually wrong

Three things, stacked:

1. When no online model answers, JIM falls back to a deterministic
   built-in helper (so a health app never goes dark). That helper's script
   was written for the *medical guidance* path and **defaulted to
   "distress"** when chat gave it no condition — crisis phrasing in what
   was just a conversation.
2. Any model failure — a missing key, a network error, an overloaded
   provider — **degraded silently**. The only record was a server-side log
   line, and the reply's provenance named the model you *picked*, not the
   one that answered. Canned text under Claude's name.
3. Settings said nothing in the worst case: *Automatic* quietly resolving
   to the built-in helper, under a screen full of provider logos.

### What 0.6.1 does about it

- In chat, the built-in helper now **explains itself honestly**: it says it
  is the offline fallback, that your message is saved, and exactly where to
  add a key — instead of playing a counselor.
- Every coach reply **names who actually wrote it**. A real model answer
  shows "Answered by anthropic"; a degrade shows an amber warning naming
  the fallback and the reason ("anthropic did not answer: …", "no API key
  on this machine — add one in Settings → Model").
- **Settings → Which model answers** now says plainly when replies will
  come from the built-in helper, and what to do about it.

### Verification

609 tests green, including that the reply's `generated_by` is the provider
that produced the words rather than the one that was picked, that a
mid-request failure is disclosed with its reason, that chat stub text
contains no crisis language, and that choosing the offline helper on
purpose is not reported as a degrade.

### Install

Download the installer for your OS from the assets below and double-click.

**Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
