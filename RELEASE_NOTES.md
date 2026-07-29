# JIM-mini v0.5.0 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.5.0` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**JIM-mini v0.5.0** — the round where JIM notices, speaks, and lets you
choose who is thinking. One of three interoperating products, all three
cut together at this version.

### A threshold around your baseline, not around a textbook

A baseline is only useful if something happens when you leave it. JIM now
keeps a **personal drift band** for every metric it tracks — heart rate,
resting heart rate, HRV, blood oxygen, respiratory rate, body temperature
— expressed as a distance from *your* learned baseline rather than a
population range.

Each band has a low edge and a high edge, and each edge can be watched or
ignored: HRV and blood oxygen only watch the low side by default, because
a high number there is good news. **Settings → Baseline** shows every band
with a slider, the current baseline, and how many samples it rests on. A
band whose baseline is still provisional says *learning* and stays quiet —
JIM will not raise a threshold against a number it has barely seen.

When a reading crosses a watched edge, the check-in is a question, not a
verdict: what crossed, which direction, by how much, and *"How have you
been feeling?"* One sensitivity dial — cautious, balanced, assertive —
widens or narrows every band at once.

### Talking to JIM out loud

The coach screen has a **microphone** and a **read-aloud** button. Speak a
question, JIM transcribes it, answers it, and speaks the answer back. Type
it instead and it stays quiet — the reply is spoken only when the question
was.

Voice is a provider layer like everything else: **ElevenLabs** (male
voices first — Daniel is the default, with Adam, Josh, Arnold and George)
or **OpenAI** (onyx, echo). Choose the service and the voice in
**Settings → Voice**, or configure nothing and the app falls back to the
browser's own speech, preferring a male voice where the system offers one.
The key is stored on the machine it was typed on and is never returned by
the API.

### Pick your model, by its own logo

The model picker is no longer a dropdown of strings. **Settings → Model**
shows a tile per provider — Claude, ChatGPT, Grok, Perplexity, Gemini —
each with its own glyph, drawn here rather than copied, so you can see at
a glance which one is answering and switch with one click. *Auto* stays
available for "whichever is configured."

### Verification

585 tests green, including that a provisional baseline raises nothing,
that assertive narrows the band while cautious widens it, that an ignored
edge is never reported, that the voice key never comes back out of the
API, and that an unconfigured voice service degrades to browser speech
instead of failing the request.

### Install

Download the installer for your OS from the assets below and double-click.

**Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
